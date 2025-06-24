from enum import Enum
from semantic_kernel.connectors.ai.google.google_ai import (
    GoogleAIChatCompletion,
    GoogleAIChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

from src.configuration.settings import app_settings


class ModelTypes(Enum):
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"


class GeminiModels(Enum):
    GEMINI_1_5_PRO = "gemini-1.5-pro"  # NOTE: not available in the free tier
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"  # NOTE: not available in the free tier
    GEMINI_2_5_FLASH = "gemini-2.5-flash"


class AzureOpenAIModels(Enum):
    GPT_4o_MINI = "gpt-4o-mini"


# Mapping of Azure OpenAI models to their API versions.
# This is fragile when using a preview model and could be set as configurable in the future.
API_VERSION_MAPPING = {AzureOpenAIModels.GPT_4o_MINI: "2025-01-01-preview"}


# Default function choice behavior; with additional attempts than default
default_function_choice_behavior = FunctionChoiceBehavior(
    enable_kernel_functions=True, maximum_auto_invoke_attempts=15, type_="auto"
)


def get_gemini_service(model: GeminiModels, service_id: str | None = None):
    return GoogleAIChatCompletion(
        gemini_model_id=model.value,
        api_key=app_settings.gemini_api_key.get_secret_value(),
        service_id=service_id,
    )


def get_gemini_default_execution_settings() -> GoogleAIChatPromptExecutionSettings:
    execution_settings = GoogleAIChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = (
        default_function_choice_behavior.Auto()
    )
    return execution_settings


def get_azure_openai_service(
    model: AzureOpenAIModels, service_id: str | None = None
) -> AzureChatCompletion:
    """
    Get an instance of the Google AI Gemini service with the specified model.
    """

    return AzureChatCompletion(
        deployment_name=model.value,
        api_key=app_settings.azure_openai_api_key.get_secret_value(),
        endpoint=app_settings.azure_openai_endpoint,
        api_version=API_VERSION_MAPPING[model],
        service_id=service_id,
    )


def get_azure_openai_default_execution_settings() -> OpenAIChatPromptExecutionSettings:
    execution_settings = OpenAIChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = (
        default_function_choice_behavior.Auto()
    )
    return execution_settings
