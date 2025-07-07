import pytest
import pytest_asyncio

from src.agents_langgraph.models import default_models, AppChatModels
from src.agents_langgraph.tools.db import InternalDatabaseToolkit


@pytest.fixture(scope="session")
def models_client() -> AppChatModels:
    return default_models


@pytest_asyncio.fixture(scope="session")
async def internal_db_toolkit():
    return await InternalDatabaseToolkit.create()
