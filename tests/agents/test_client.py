import pytest
from autogen_core.models import UserMessage

from src.agents.client import get_gemini_client, GeminiModels
from src.configuration.settings import app_settings


@pytest.mark.asyncio
async def test_client_connects():
    # Ensure the API key is set for testing
    assert app_settings.gemini_api_key is not None, (
        "Gemini API key must be set for testing."
    )

    # Create a Gemini client instance
    client = get_gemini_client(GeminiModels.GEMINI_1_5_FLASH)

    # Test the connection by making a simple request
    response = await client.create(
        [UserMessage(content="What is the capital of France?", source="user")]
    )
    print(response)

    # Check if the response is valid
    assert response is not None, "Response should not be None."
