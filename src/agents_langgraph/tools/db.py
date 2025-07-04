import asyncio
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import Engine, create_engine
from sqlalchemy import NullPool, event, text
from sqlalchemy.exc import OperationalError

from src.agents_langgraph.logging_config import default_logger
from src.agents_langgraph.models import AppChatModels
from src.configuration.auth import get_db_connection_string, provide_azure_sql_token

DB_CONNECTION_RETRIES = 3
DB_RETRY_DELAY = 10  # seconds


class InternalDatabaseToolkit(SQLDatabaseToolkit):
    """A class to interact with a SQL database using SQLAlchemy."""

    def __init__(self, engine: Engine, models: AppChatModels):
        super().__init__(db=SQLDatabase(engine=engine), llm=models.default_model)

    @classmethod
    async def create(cls, models: AppChatModels) -> "SQLDatabaseToolkit":
        """Create an instance of InternalDatabase with an async engine and metadata."""
        default_logger.info("Creating InternalDatabase instance...")
        connection_string = get_db_connection_string()
        engine = create_engine(connection_string, poolclass=NullPool)
        event.listen(engine, "do_connect", provide_azure_sql_token)

        # Ensure the database connection is established
        retry_number = 0
        for retry_number in range(1, DB_CONNECTION_RETRIES + 1):
            try:
                with engine.begin() as conn:
                    # Perform a simple query to ensure the connection is valid
                    conn.execute(text("SELECT 1"))
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

        return cls(engine=engine, models=models)
