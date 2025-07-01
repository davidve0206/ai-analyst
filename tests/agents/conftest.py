import pytest_asyncio

from src.agents.tools.db import InternalDatabase
from src.configuration.auth import get_azure_ai_agent_client


@pytest_asyncio.fixture(scope="session")
async def internal_database():
    """
    Fixture to create an instance of InternalDatabase for testing.
    Requiring a single instance across the test session to avoid
    multiple connections to the database.
    """

    return await InternalDatabase.create()


@pytest_asyncio.fixture(scope="session")
async def azure_ai_client():
    """
    Fixture to create an instance of AIProjectClient for testing.
    This client is used to interact with Azure AI services.
    """

    client = get_azure_ai_agent_client()
    yield client
    client.close()
