import pytest

from semantic_kernel.contents.chat_history import ChatHistory
from src.agents.models import (
    get_gemini_service,
    GeminiModels,
)
from src.configuration.settings import app_settings


@pytest.mark.asyncio
async def test_client_connects():
    # Ensure the API key is set for testing
    assert app_settings.gemini_api_key is not None, (
        "Gemini API key must be set for testing."
    )

    service = get_gemini_service(
        GeminiModels.GEMINI_1_5_FLASH, service_id="test_service"
    )
    execution_settings = service.get_prompt_execution_settings_class()()
    chat_history = ChatHistory()
    chat_history.add_user_message(
        "Hello, how are you?",
    )

    # Test the connection by making a simple request
    response = await service.get_chat_message_content(
        chat_history=chat_history,
        service_id="test_service",
        settings=execution_settings,
    )

    # Check if the response is valid
    assert response is not None
