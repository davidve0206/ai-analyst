import asyncio
import pickle
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from langchain_core.tools import tool

from sqlalchemy import ForeignKeyConstraint, MetaData, NullPool, Table, event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.configuration.auth import (
    get_db_connection_string,
    provide_azure_sql_token,
)
from src.configuration.logger import default_logger
from src.configuration.settings import CACHE_DIR

# NOTE: The code for now only supports Azure SQL Database.
# Ensure you have the ODBC Driver 18 for SQL Server installed.
# We should evaluate adding support for other databases in the future.

"""
Credits:

My implementation is inspired by https://github.com/Finndersen/dbdex.

"""
DB_CONNECTION_RETRIES = 3
DB_RETRY_DELAY = 10  # seconds


class InternalDatabaseToolkit:
    """A toolkit to interact with a SQL database using SQLAlchemy."""

    _engine: AsyncEngine
    _metadata: MetaData
    _cache_file: Path = CACHE_DIR / "db_metadata_cache.pkl"

    def __init__(self, _engine, metadata):
        self._engine = _engine
        self._metadata = metadata

    @classmethod
    async def create(cls, force_refresh: bool = False):
        """Create an instance of InternalDatabase with an async _engine and metadata."""
        default_logger.info("Creating InternalDatabase instance...")
        connection_string = get_db_connection_string()
        _engine = create_async_engine(connection_string, poolclass=NullPool)
        event.listen(_engine.sync_engine, "do_connect", provide_azure_sql_token)

        # Try to load metadata from cache first
        metadata = None
        if not force_refresh and cls._cache_file.exists():
            try:
                with open(cls._cache_file, "rb") as f:
                    metadata = pickle.load(f)
                default_logger.info("Loaded metadata from cache")
            except Exception as e:
                default_logger.warning(f"Failed to load metadata cache: {e}")

        # If no cached metadata, reflect from database
        if metadata is None:
            metadata = await cls._reflect_database_schema(_engine)
            # Cache the metadata
            try:
                with open(cls._cache_file, "wb") as f:
                    pickle.dump(metadata, f)
                default_logger.info("Cached metadata to disk")
            except Exception as e:
                default_logger.warning(f"Failed to cache metadata: {e}")

        return cls(_engine=_engine, metadata=metadata)

    @classmethod
    async def _reflect_database_schema(cls, _engine: AsyncEngine) -> MetaData:
        """Reflect the database schema."""
        metadata = MetaData()
        for retry_number in range(1, DB_CONNECTION_RETRIES + 1):
            try:
                async with _engine.begin() as conn:
                    schemas = await conn.execute(
                        text("""
                            SELECT DISTINCT TABLE_SCHEMA
                            FROM INFORMATION_SCHEMA.TABLES
                            WHERE TABLE_TYPE = 'BASE TABLE';
                        """)
                    )
                    for (schema,) in schemas:
                        default_logger.info(f"Reflecting {schema} schema...")
                        await conn.run_sync(metadata.reflect, schema=schema)
                    break
            except OperationalError as e:
                if retry_number == DB_CONNECTION_RETRIES:
                    default_logger.error(
                        f"Failed to connect to the database after {DB_CONNECTION_RETRIES} retries: {e}"
                    )
                    raise e
                default_logger.warning(
                    f"Failed to reflect database schema, retrying ({retry_number}/{DB_CONNECTION_RETRIES}): {e}"
                )
                await asyncio.sleep(DB_RETRY_DELAY)
        return metadata

    @property
    def dialect(self) -> str:
        return self._engine.dialect.name

    @property
    def table_names(self) -> list[str]:
        return list(self._metadata.tables.keys())

    def get_tools(self) -> list:
        """Get the tools in the toolkit."""
        return [
            self._create_describe_schema_tool(),
            self._create_execute_query_tool(),
        ]

    def _get_tables(self) -> list[Table]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        return list(self._metadata.tables.values())

    def _create_describe_schema_tool(self):
        """Create a describe_schema tool bound to this database instance."""

        @tool
        def describe_schema_impl(table_names: str | None = None) -> str:
            """Get the schema for tables in a comma-separated list;
            if no list is provided, describes all tables.

            Args:
                table_names (str | None): Comma-separated list of tables to describe.
            Returns:
                A string representation of the schema for the specified tables.
            """
            try:
                if table_names:
                    table_names = [name.strip() for name in table_names.split(",")]
                    tables = [self._metadata.tables[table] for table in table_names]
                else:
                    tables = self._get_tables()
                output = "\n\n".join(format_table_schema(table) for table in tables)
                return output
            except KeyError as e:
                default_logger.debug(f"Table not found: {str(e)}")
                return f"Error: Table not found - {str(e)}"
            except Exception as e:
                default_logger.debug(f"An unexpected error occurred: {str(e)}")
                return f"An unexpected error occurred: {str(e)}"

        return describe_schema_impl

    def _create_execute_query_tool(self):
        """Create an execute_query tool bound to this database instance."""

        @tool
        async def execute_query_impl(query: str) -> list[dict[str, Any]] | str:
            """Execute a SQL query against the database; only SELECT queries are allowed.

            Args:
                query (str): The SQL query to execute. Only SELECT queries are allowed.
            Returns:
                A list of dictionaries representing the rows returned by the query,
                or an error message if the query is not a valid SELECT query or fails.
            """
            if not query.strip().lower().startswith("select"):
                return "Error: Only SELECT queries are allowed."

            try:
                async with self._engine.connect() as connection:
                    result = await connection.execute(text(query))
                    rows = result.mappings().all()
                    return make_json_serializable(rows)
            except Exception as e:
                default_logger.debug(f"Query execution failed: {str(e)}")
                return f"Query execution failed: {str(e)}"

        return execute_query_impl


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

    schema_lines = [f"TABLE [{table.schema}].[{table.name}] ("]

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
