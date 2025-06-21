from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments

from .utils.prompt_utils import render_prompt_from_jinja
from .models import GeminiModels, get_default_execution_settings, get_gemini_service
from .tools.db import InternalDatabase

from src.configuration.consts import DATABASE_CATALOG


def create_internal_data_agent(
    internal_db: InternalDatabase,
) -> ChatCompletionAgent:
    """
    Create an instance of the InternalDataAgent with the necessary configurations.
    This agent can access internal data and answer questions based on it.
    """
    agent_name = "InternalDataAgent"
    system_prompt = render_prompt_from_jinja(
        "internal_data_agent_system_prompt.md.j2",
        {
            "table_list": internal_db.table_names,
            "database_catalog": DATABASE_CATALOG,
        },
    )

    return ChatCompletionAgent(
        name=agent_name,
        instructions=system_prompt,
        arguments=KernelArguments(get_default_execution_settings()),
        plugins=[internal_db],
        service=get_gemini_service(
            model=GeminiModels.GEMINI_2_5_FLASH,
        ),
    )
