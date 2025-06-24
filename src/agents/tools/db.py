from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKeyConstraint, MetaData, NullPool, Table, event, text
from sqlalchemy.ext.asyncio import create_async_engine
from semantic_kernel.functions import kernel_function

from src.configuration.auth import (
    get_azure_sql_connection_string,
    provide_azure_sql_token,
)
from src.configuration.logger import default_logger

# NOTE: The code for now only supports Azure SQL Database.
# Ensure you have the ODBC Driver 18 for SQL Server installed.
# We should evaluate adding support for other databases in the future.

"""
Credits:

My implementation is inspired by https://github.com/Finndersen/dbdex.

"""


class InternalDatabase:
    """A class to interact with a SQL database using SQLAlchemy."""

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata

    @classmethod
    async def create(cls):
        """Create an instance of InternalDatabase with an async engine and metadata."""
        default_logger.info("Creating InternalDatabase instance...")
        connection_string = get_azure_sql_connection_string()
        engine = create_async_engine(connection_string, poolclass=NullPool)
        event.listen(engine.sync_engine, "do_connect", provide_azure_sql_token)

        # Reflect the database schema
        # This will load all tables and their metadata from the database.
        # TODO: Implement retry logic for cold databases.
        metadata = MetaData()
        async with engine.begin() as conn:
            schemas = await conn.execute(
                text("""
                    SELECT DISTINCT TABLE_SCHEMA
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE';
                """)
            )
            for (schema,) in schemas:
                await conn.run_sync(metadata.reflect, schema=schema)

        return cls(engine=engine, metadata=metadata)

    @property
    def dialect(self) -> str:
        return self.engine.dialect.name

    @property
    def table_names(self) -> list[str]:
        return list(self.metadata.tables.keys())

    def get_tables(self) -> list[Table]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        return list(self.metadata.tables.values())

    @kernel_function
    def describe_schema(self, table_names: str | None = None) -> str:
        """Get a string representation of the structure of tables in
        the database

        Args:
            table_names (srt | None): Name of the table to describe.
                If several tables are provided, separate them by commas.
                If None, describes all tables in the database.
        """
        try:
            if table_names:
                table_names = [name.strip() for name in table_names.split(",")]
                tables = [self.metadata.tables[table] for table in table_names]
            else:
                tables = self.get_tables()
            return "\n\n".join(format_table_schema(table) for table in tables)

        except KeyError as e:
            default_logger.debug(f"Table not found: {str(e)}")
            return f"Error: Table not found - {str(e)}"
        except Exception as e:
            default_logger.debug(f"An unexpected error occurred: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"

    @kernel_function
    async def execute_query(self, query: str) -> list[dict[str, Any]] | str:
        """Execute a SQL query; only allows SELECT queries."""
        if not query.strip().lower().startswith("select"):
            return "Error: Only SELECT queries are allowed."

        default_logger.debug(f"Executing query: {query}")
        try:
            async with self.engine.connect() as connection:
                result = await connection.execute(text(query))
                rows = result.mappings().all()
                return make_json_serializable(rows)
        except Exception as e:
            return f"Query execution failed: {str(e)}"


def make_json_serializable(dict_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def convert_value(val):
        if isinstance(val, Decimal):
            return float(val)
        elif isinstance(val, (datetime, date)):
            return val.isoformat()
        elif isinstance(val, bytes):
            return val.decode("utf-8", errors="replace")
        elif isinstance(val, (set, frozenset)):
            return list(val)
        else:
            return val

    return [{k: convert_value(v) for k, v in row.items()} for row in dict_rows]


def format_table_schema(table: Table) -> str:
    """
    Formats a SQLAlchemy Table object into a schema string representation like:
    TABLE table_name (
        COLUMNS
            [column_name] column_type [PRIMARY KEY] [NOT NULL] [DEFAULT value]
        CONSTRAINTS
            FOREIGN KEY (column_name) REFERENCES target_table (target_column)
    )

    TODO: Add support for indexes if needed.
    """

    schema_lines = [f"TABLE {table.schema}.{table.name} ("]

    # Format column definitions
    schema_lines.append("    COLUMNS")
    for column in table.columns:
        column_definition = f"        [{column.name}] {column.type}"
        if column.primary_key:
            column_definition += " PRIMARY KEY"
        if not column.nullable:
            column_definition += " NOT NULL"
        if column.default:
            column_definition += f" DEFAULT {column.default.arg}"
        if column.unique:
            column_definition += " UNIQUE"
        schema_lines.append(column_definition + ",")

    # Format constraints
    schema_lines.append("    CONSTRAINTS")

    # Format foreign keys
    for fk_constraint in table.constraints:
        if isinstance(fk_constraint, ForeignKeyConstraint):
            for fk in fk_constraint.elements:
                schema_lines.append(
                    f"        FOREIGN KEY ({fk.parent.name}) REFERENCES {fk.column.table.name} ({fk.column.name}),"
                )

    schema_lines.append(")")
    return "\n".join(schema_lines)
