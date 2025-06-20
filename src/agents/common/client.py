from enum import Enum
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.configuration.settings import app_settings


class GeminiModels(Enum):
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_0_PRO = "gemini-2.0-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"


def get_gemini_client(model: GeminiModels):
    print(app_settings.gemini_api_key)
    return OpenAIChatCompletionClient(
        model=model.value,
        api_key=app_settings.gemini_api_key.get_secret_value(),  # Set your API key here if needed
        max_retries=3,
        timeout=30,
    )
