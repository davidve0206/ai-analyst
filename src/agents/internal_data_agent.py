from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from .utils.render_template import render_prompt
from .client import get_gemini_client, GeminiModels
from .tools.db import InternalDatabase

from src.configuration.consts import DATABASE_CATALOG


async def create_internal_data_agent(
    internal_db: InternalDatabase,
) -> RoundRobinGroupChat:
    """
    Create an instance of the InternalDataAgent with the necessary configurations.
    This agent can access internal data and answer questions based on it.
    """
    agent_name = "InternalDataAgent"
    model_client = get_gemini_client(GeminiModels.GEMINI_2_0_FLASH)
    system_prompt = render_prompt(
        "internal_data_agent_system_prompt.md.j2",
        {
            "table_list": internal_db.table_names,
            "database_catalog": DATABASE_CATALOG,
        },
    )

    internal_data_agent = AssistantAgent(
        name=agent_name,
        description="An agent that can access internal data and answer questions based on it.",
        system_message=system_prompt,
        tools=[internal_db.describe_schema, internal_db.execute_query],
        model_client=model_client,
    )

    # Termination condition that stops the task if the agent responds with a text message.
    termination_condition = TextMessageTermination(agent_name)

    # Create a team with the looped assistant agent and the termination condition.
    return RoundRobinGroupChat(
        [internal_data_agent],
        termination_condition=termination_condition,
    )
