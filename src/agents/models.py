from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI

from src.configuration.settings import app_settings


API_VERSION_MAPPING = {"gpt-4o-mini": "2025-01-01-preview"}


class AppChatModels:
    """
    Class to initialize and manage chat models for the application.

    Holds instances of chat models that can be used throughout the application.
    """

    gemini_2_0_flash: ChatGoogleGenerativeAI
    gemini_2_5_pro: ChatGoogleGenerativeAI
    gpt_o4_mini: AzureChatOpenAI
    default_model: ChatGoogleGenerativeAI | AzureChatOpenAI

    def __init__(self):
        DEFAULT_TEMPERATURE = 0.4  # We want consistent responses, but be careful about loops and repetition
        DEFAULT_TOP_P = 1  # This just makes sure that we override the default value of any of the models

        self.gemini_2_0_flash = init_chat_model(
            "google_genai:gemini-2.0-flash",
            api_key=app_settings.gemini_api_key,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
        )

        self.gemini_2_5_pro = init_chat_model(
            "google_genai:gemini-2.5-pro",
            api_key=app_settings.gemini_api_key,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
        )

        self.gpt_o4_mini = init_chat_model(
            "azure_openai:gpt-4o-mini",
            api_key=app_settings.azure_openai_api_key,
            api_version="2025-01-01-preview",  # Consider making this configurable if needed
            azure_endpoint=app_settings.azure_openai_endpoint,
            azure_deployment="gpt-4o-mini",
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
        )

        # Sets a default model for places where we don't specify a model
        # Recommended to use a cheap but fast model, explicitly set a
        # different model in the agent if needed
        self.default_model = self.gemini_2_0_flash 

default_models = AppChatModels()