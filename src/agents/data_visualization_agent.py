from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import AppChatModels
from src.agents.tools.python_interpreter import create_python_repl_tool
from src.agents.utils.prompt_utils import PrompTypes, render_prompt_template
from src.configuration.settings import TEMP_DIR


def get_data_visualization_agent(models: AppChatModels) -> CompiledStateGraph:
    """
    Very basic agent that can interact with a code interpreter.

    Args:
        models (AppChatModels): The models to use for the agent.

    Returns:
        CompiledStateGraph: The compiled state graph for the agent.
    """
    system_message = render_prompt_template(
        "data_visualization_agent_system_prompt.md",
        context={
            "temp_path": str(TEMP_DIR),
        },
        type=PrompTypes.SYSTEM,
    )

    return create_react_agent(
        model=models.gpt_o4_mini,
        tools=[create_python_repl_tool()],
        prompt=system_message,
    )
