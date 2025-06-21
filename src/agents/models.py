from enum import Enum
from semantic_kernel.connectors.ai.google.google_ai import (
    GoogleAIChatCompletion,
    GoogleAIChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)

from src.configuration.settings import app_settings


class GeminiModels(Enum):
    GEMINI_1_5_PRO = "gemini-1.5-pro" # NOTE: not available in the free tier
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro" # NOTE: not available in the free tier
    GEMINI_2_5_FLASH = "gemini-2.5-flash"


def get_gemini_service(model: GeminiModels, service_id: str | None = None):
    return GoogleAIChatCompletion(
        gemini_model_id=model.value,
        api_key=app_settings.gemini_api_key.get_secret_value(),
        service_id=service_id,
    )


def get_default_execution_settings() -> GoogleAIChatPromptExecutionSettings:
    execution_settings = GoogleAIChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    return execution_settings
