from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments

from .utils.prompt_utils import render_prompt_from_jinja
from .models import (
    AzureOpenAIModels,
    GeminiModels,
    ModelTypes,
    get_gemini_service,
    get_gemini_default_execution_settings,
    get_azure_openai_service,
    get_azure_openai_default_execution_settings,
    default_function_choice_behavior,
)
from .tools.db import InternalDatabase

from src.configuration.consts import DATABASE_CATALOG
from src.configuration.logger import default_logger


def create_database_agent(
    internal_db: InternalDatabase,
    model_type: ModelTypes = ModelTypes.AZURE_OPENAI,
) -> ChatCompletionAgent:
    """
    Create an instance of the DatabaseAgent with the necessary configurations.
    This agent can access internal data and answer questions based on it.
    """
    agent_name = "DatabaseAgent"
    system_prompt = render_prompt_from_jinja(
        "database_agent_system_prompt.md.j2",
        {
            "table_list": internal_db.table_names,
            "database_catalog": DATABASE_CATALOG,
            "dialect": internal_db.dialect,
        },
    )

    default_logger.debug(f"Creating DatabaseAgent with model type: {model_type.value}")
    match model_type:
        case ModelTypes.GEMINI:
            model_service = get_gemini_service(
                model=GeminiModels.GEMINI_2_5_FLASH,
            )
            execution_settings = get_gemini_default_execution_settings()
        case ModelTypes.AZURE_OPENAI:
            model_service = get_azure_openai_service(
                model=AzureOpenAIModels.GPT_4o_MINI,
            )
            execution_settings = get_azure_openai_default_execution_settings()
        case _:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    # The database agent needs additional retries for function calls
    default_function_choice_behavior.maximum_auto_invoke_attempts = 10

    return ChatCompletionAgent(
        name=agent_name,
        description="An agent that can access internal data and answer questions based on it.",
        instructions=system_prompt,
        arguments=KernelArguments(execution_settings=execution_settings),
        function_choice_behavior=default_function_choice_behavior,
        plugins=[internal_db],
        service=model_service,
    )
