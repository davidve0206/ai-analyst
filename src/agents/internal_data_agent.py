from src.agents.code_agent_with_review import CodeAgentState, PreConfiguredCodeAgent
from src.agents.models import AppChatModels
from src.agents.utils.output_utils import get_request_temp_dir
from src.agents.utils.prompt_utils import MessageTypes, render_prompt_template
from src.configuration.constants import INTERNAL_DATA
from src.configuration.kpis import SalesReportRequest
from src.configuration.settings import app_settings

def get_internal_data_agent(
    models: AppChatModels, request: SalesReportRequest
) -> PreConfiguredCodeAgent:
    """
    Very basic agent that can interact with a code interpreter.

    Args:
        models (AppChatModels): The models to use for the agent.

    Returns:
        PreConfiguredCodeAgent: The configured agent for internal data retrieval.
    """
    temp_path = get_request_temp_dir(request)
    system_message = render_prompt_template(
        "internal_data_agent_system_prompt.md",
        context={
            "date": app_settings.analysis_date,
            "input_location": str(INTERNAL_DATA.path),
            "data_description": INTERNAL_DATA.description,
            "temp_path": str(temp_path),
        },
        type=MessageTypes.SYSTEM,
    )

    agent = PreConfiguredCodeAgent(
        models=models,
        preset_state=CodeAgentState(
            system_prompt=system_message,
        ),  # Default values for errors and iterations
        name="Internal Data Agent",
    )

    return agent
