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
)

from src.configuration.logger import default_logger


def create_editor_agent(
    model_type: ModelTypes = ModelTypes.AZURE_OPENAI,
) -> ChatCompletionAgent:
    """
    Create an instance of the EditorAgent with the DatabaseAgent
    as tool.
    """
    agent_name = "EditorAgent"
    system_prompt = render_prompt_from_jinja("editor_agent_system_prompt.md.j2")

    default_logger.debug(f"Creating EditorAgent with model type: {model_type.value}")
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

    return ChatCompletionAgent(
        name=agent_name,
        description="An agent that edits business reports to ensure they are well-structured, clear, and concise.",
        instructions=system_prompt,
        arguments=KernelArguments(execution_settings=execution_settings),
        service=model_service,
    )
