from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import AppChatModels
from src.agents.tools.python_interpreter import create_python_repl_tool
from src.agents.utils.output_utils import get_request_temp_dir
from src.agents.utils.prompt_utils import MessageTypes, render_prompt_template
from src.configuration.kpis import SalesReportRequest


def get_data_visualization_agent(
    models: AppChatModels, request: SalesReportRequest
) -> CompiledStateGraph:
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
            "temp_path": str(get_request_temp_dir(request)),
        },
        type=MessageTypes.SYSTEM,
    )

    return create_react_agent(
        model=models.default_model,
        tools=[create_python_repl_tool()],
        prompt=system_message,
    )
