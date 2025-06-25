import pytest_asyncio

from src.configuration.db import create_config_db_sessionmaker


@pytest_asyncio.fixture(scope="function")
async def test_session_maker():
    """
    Fixture to create an instance of InternalDatabase for testing.
    Requiring a single instance across the test session to avoid
    multiple connections to the database.
    """
    TEST_DATABASE_URL = "sqlite:///:memory:"
    return create_config_db_sessionmaker(url=TEST_DATABASE_URL)
