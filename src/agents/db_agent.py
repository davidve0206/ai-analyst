"""
This agent is currently deprecated as the data ended being provided as a csv file.
It is kept here for reference and future use.
"""

from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import AppChatModels
from src.agents.tools.db import InternalDatabaseToolkit
from src.agents.utils.prompt_utils import PrompTypes, render_prompt_template
from src.configuration.constants import DATABASE_CATALOG

RECURSION_LIMIT = 10


def get_database_agent(
    db_toolkit: InternalDatabaseToolkit, models: AppChatModels
) -> CompiledStateGraph:
    """
    Very basic agent that can interact with a SQL database.

    This should not be the final implementation, but rather a starting point.

    Args:

        db_toolkit (InternalDatabaseToolkit): The database toolkit to use.
        models (AppChatModels): The models to use for the agent.

    Returns:
        CompiledStateGraph: The compiled state graph for the agent.
    """
    system_message = render_prompt_template(
        "db_agent_system_prompt.md",
        context={
            "dialect": db_toolkit.dialect,
            "tables": db_toolkit.table_names,
            "catalog": DATABASE_CATALOG,
        },
        type=PrompTypes.SYSTEM,
    )

    return create_react_agent(
        model=models.gpt_o4_mini, tools=db_toolkit.get_tools(), prompt=system_message
    )

    """ limited_agent = agent.with_config(
        recursion_limit=RECURSION_LIMIT,
    )

    return limited_agent """
