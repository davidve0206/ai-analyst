import pytest_asyncio

from src.configuration.db_service import SalesReportsDB


@pytest_asyncio.fixture(scope="function")
async def test_db() -> SalesReportsDB:
    """
    Fixture to create an instance of InternalDatabase for testing.
    Requiring a single instance across the test session to avoid
    multiple connections to the database.
    """
    TEST_DATABASE_URL = "sqlite:///:memory:"
    return SalesReportsDB(db_url=TEST_DATABASE_URL)
