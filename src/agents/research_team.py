from semantic_kernel.agents import StandardMagenticManager, MagenticOrchestration
from semantic_kernel.agents.runtime import CoreRuntime

from src.agents.internal_data_agent import create_internal_data_agent
from src.agents.tools.db import InternalDatabase
from src.agents.utils.prompt_utils import render_prompt_from_jinja
from src.configuration.logger import default_logger
from src.configuration.consts import COMPANY_DESCRIPTION, REPORT_STRUCTURE, KpiRequest
from src.agents.models import AzureOpenAIModels, ModelTypes, get_azure_openai_service
from src.agents.utils.output_utils import (
    handle_intermediate_steps,
    store_response_with_timestamp,
)


async def invoke_research_team_task(
    kpi: KpiRequest,
    internal_db: InternalDatabase,
    runtime: CoreRuntime,
    results_dict: dict[str, str] | None = None,
):
    result = await research_team_task(
        kpi=kpi,
        internal_db=internal_db,
        runtime=runtime,
    )
    store_response_with_timestamp(result, f"{kpi.name}_report.md")
    if results_dict is not None:
        results_dict[kpi.name] = result

    default_logger.info(f"Completed research task for KPI: {kpi.name}")
    print(result)


async def research_team_task(
    kpi: KpiRequest,
    internal_db: InternalDatabase,
    runtime: CoreRuntime,
) -> str | None:
    """
    Research team task to handle KPI requests.

    Args:
        kpi (KpiRequest): The KPI request containing name, description, direction, and period.
        internal_db (InternalDatabase): The internal database instance for data access.
        runtime (CoreRuntime): The core runtime instance for agent management.

    Returns:
        str: The result of the research task.
    """
    # Here you would implement the logic to handle the KPI request
    # For example, querying the internal database and processing the data

    # Placeholder for actual implementation
    default_logger.info(f"Processing KPI request: {kpi.name}")
    task_prompt = render_prompt_from_jinja(
        "research_team_task_prompt.md.j2",
        {
            "kpi": kpi,
            "report_structure": REPORT_STRUCTURE,
            "company_description": COMPANY_DESCRIPTION,
        },
    )

    # Create the team for the research task
    db_agent = create_internal_data_agent(
        internal_db=internal_db,
        model_type=ModelTypes.AZURE_OPENAI,
        db_agent_model_type=ModelTypes.AZURE_OPENAI,
    )

    manager = StandardMagenticManager(
        chat_completion_service=get_azure_openai_service(
            model=AzureOpenAIModels.GPT_4o_MINI,
        )
    )

    magentic_orchestration = MagenticOrchestration(
        members=[db_agent],
        manager=manager,
        agent_response_callback=handle_intermediate_steps,
    )

    # Invoke the orchestration with the task prompt
    orchestration_result = await magentic_orchestration.invoke(
        task=task_prompt,
        runtime=runtime,
    )
    value = await orchestration_result.get()
    return value.content
