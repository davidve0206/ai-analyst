from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from langchain_core.rate_limiters import InMemoryRateLimiter

from src.configuration.settings import app_settings


class AppChatModels:
    """
    Class to initialize and manage chat models for the application.

    Holds instances of chat models that can be used throughout the application.
    """

    gemini_2_0_flash: ChatGoogleGenerativeAI
    gemini_2_5_pro: ChatGoogleGenerativeAI
    openai_gpt_4o_mini: AzureChatOpenAI
    openai_o4_mini: AzureChatOpenAI
    default_model: AzureChatOpenAI  # Default model has to use an Open model, as the multimodal prompt from LangChain uses the OpenAI standard.

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

        azure_rate_limiter = InMemoryRateLimiter(
            requests_per_second=12,  # Slightly under max RPM (1K/min = ~16.6/sec)
            check_every_n_seconds=0.1,  # Check every 100 ms
            max_bucket_size=10,  # Allow small bursts
        )
        self.openai_gpt_4o_mini = init_chat_model(
            "azure_openai:gpt-4o-mini",
            api_key=app_settings.azure_openai_api_key,
            api_version="2025-01-01-preview",  # Consider making this configurable if needed
            azure_endpoint=app_settings.azure_openai_endpoint,
            azure_deployment="gpt-4o-mini",
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            request_timeout=45,  # Set a reasonable timeout for requests
            rate_limiter=azure_rate_limiter,
        )
        self.openai_o4_mini = init_chat_model(
            "azure_openai:o4-mini",
            api_key=app_settings.azure_openai_api_key,
            api_version="2025-01-01-preview",  # Consider making this configurable if needed
            azure_endpoint=app_settings.azure_openai_endpoint,
            azure_deployment="o4-mini",
            request_timeout=45,  # Set a reasonable timeout for requests
            rate_limiter=azure_rate_limiter,
        )
        # Sets a default model; this allow us to change the model used by the agents without changing the code
        self.default_model = self.openai_o4_mini
        self.default_non_reasoning_model = self.openai_gpt_4o_mini


default_models = AppChatModels()
