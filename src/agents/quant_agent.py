from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import AppChatModels
from src.agents.tools.python_interpreter import repl_tool
from src.agents.utils import render_system_prompt_template
from src.configuration.constants import COMPANY_DESCRIPTION
from src.configuration.settings import TEMP_DIR

RECURSION_LIMIT = 10


def get_quantitative_agent(models: AppChatModels) -> CompiledStateGraph:
    """
    Very basic agent that can interact with a code interpreter.

    Args:
        models (AppChatModels): The models to use for the agent.

    Returns:
        CompiledStateGraph: The compiled state graph for the agent.
    """
    system_prompt = render_system_prompt_template(
        "quantitative_analyst_agent_system_prompt.md",
        context={
            "temp_path": str(TEMP_DIR),
            "company_description": COMPANY_DESCRIPTION,
        },
    )

    return create_react_agent(
        model=models.gpt_o4_mini, tools=[repl_tool], prompt=system_prompt
    )
