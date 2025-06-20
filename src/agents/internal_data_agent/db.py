from sqlalchemy import ForeignKeyConstraint, MetaData, NullPool, Table, event, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import ArgumentError, ProgrammingError


from src.configuration.auth import (
    get_azure_sql_connection_string,
    provide_azure_sql_token,
)

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
        connection_string = get_azure_sql_connection_string()
        engine = create_async_engine(connection_string, poolclass=NullPool)
        event.listen(engine.sync_engine, "do_connect", provide_azure_sql_token)

        # Reflect the database schema
        # This will load all tables and their metadata from the database.
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

    def describe_schema(self, table_names: list[str] | None = None) -> str:
        """Get a sring representation of the structure of tables in the database (all by default)"""
        if table_names:
            try:
                tables = [self.metadata.tables[table] for table in table_names]
            except KeyError as e:
                raise ProgrammingError(f"Invalid table name: {e}") from e
        else:
            tables = self.get_tables()
        return "\n\n".join(format_table_schema(table) for table in tables)

    async def execute(self, query, *args, **kwargs):
        """Execute a SQL query; only allows SELECT queries."""
        if not query.strip().lower().startswith("select"):
            raise ArgumentError("Only SELECT queries are allowed.")

        async with self.engine.connect() as connection:
            result = await connection.execute(query, *args, **kwargs)
            return result.fetchall()


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
