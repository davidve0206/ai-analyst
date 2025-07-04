import pytest

from src.agents_langgraph.models import default_models, AppChatModels


@pytest.fixture(scope="session")
def models_client() -> AppChatModels:
    return default_models
