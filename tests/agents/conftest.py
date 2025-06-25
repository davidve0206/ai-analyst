import pytest_asyncio

from src.agents.tools.db import InternalDatabase


@pytest_asyncio.fixture(scope="session")
async def internal_database():
    """
    Fixture to create an instance of InternalDatabase for testing.
    Requiring a single instance across the test session to avoid
    multiple connections to the database.
    """

    return await InternalDatabase.create()
