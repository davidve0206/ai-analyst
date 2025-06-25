from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments, kernel_function

from src.agents.database_agent import create_database_agent

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

from src.configuration.consts import COMPANY_DESCRIPTION
from src.configuration.logger import default_logger


class DBAgentPlugin:
    _agent: ChatCompletionAgent

    def __init__(self, internal_db: InternalDatabase, model_type: ModelTypes):
        self._agent = create_database_agent(
            internal_db=internal_db, model_type=model_type
        )

    @kernel_function(
        name="database_agent_tool",
        description="A tool to interact with the database agent.",
    )
    async def database_agent_tool(self, query: str) -> str:
        """
        Get a response from the database agent a tool.

        Args:
          query (str): The natural language query to send to the agent.
        """
        response = await self._agent.get_response(messages=query)
        if response is None:
            raise ValueError("No response received from the agent.")
        return response.content.content


def create_internal_data_agent(
    internal_db: InternalDatabase,
    model_type: ModelTypes = ModelTypes.AZURE_OPENAI,
    db_agent_model_type: ModelTypes = ModelTypes.AZURE_OPENAI,
) -> ChatCompletionAgent:
    """
    Create an instance of the InternalDataAgent with the DatabaseAgent
    as tool.
    """
    agent_name = "InternalDataAgent"
    system_prompt = render_prompt_from_jinja(
        "internal_data_agent_system_prompt.md.j2",
        {
            "company_description": COMPANY_DESCRIPTION,
        },
    )

    default_logger.debug(
        f"Creating InternalDataAgent with model type: {model_type.value}"
    )
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

    db_agent_tool = DBAgentPlugin(
        internal_db=internal_db, model_type=db_agent_model_type
    )

    return ChatCompletionAgent(
        name=agent_name,
        description="High level agent that can process natural language questions using the company's internal database",
        instructions=system_prompt,
        arguments=KernelArguments(execution_settings=execution_settings),
        function_choice_behavior=default_function_choice_behavior,
        plugins=[db_agent_tool],
        service=model_service,
    )
