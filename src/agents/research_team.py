from semantic_kernel.agents import StandardMagenticManager, MagenticOrchestration
from semantic_kernel.agents.runtime import CoreRuntime
from azure.ai.projects.aio import AIProjectClient

from src.agents.quantitative_agent import create_quantitative_agent
from src.agents.editor_agent import create_editor_agent
from src.agents.internal_data_agent import create_internal_data_agent
from src.agents.tools.db import InternalDatabase
from src.agents.utils.prompt_utils import render_prompt_from_jinja
from src.configuration.kpis import KpiRequest, SalesReportRequest
from src.configuration.logger import default_logger
from src.configuration.company import COMPANY_DESCRIPTION
from src.agents.models import AzureOpenAIModels, ModelTypes, get_azure_openai_service
from src.agents.utils.output_utils import (
    handle_intermediate_steps,
    store_response_with_timestamp,
)


async def invoke_research_team_task(
    request: KpiRequest | SalesReportRequest,
    internal_db: InternalDatabase,
    runtime: CoreRuntime,
    azure_ai_client: AIProjectClient,
):
    research_result = await research_team_task(
        request=request,
        internal_db=internal_db,
        runtime=runtime,
        azure_ai_client=azure_ai_client,
    )

    editor_agent = create_editor_agent(
        model_type=ModelTypes.AZURE_OPENAI,
    )

    edited_report = await editor_agent.get_response(messages=research_result)
    edited_report_content = edited_report.content.content

    output_path = store_response_with_timestamp(
        response=edited_report_content, file_name=f"{request.name}"
    )
    default_logger.info(f"Completed research task for KPI: {request.name}")
    return output_path


async def research_team_task(
    request: KpiRequest | SalesReportRequest,
    internal_db: InternalDatabase,
    runtime: CoreRuntime,
    azure_ai_client: AIProjectClient,
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
    default_logger.info(f"Processing request: {request.name}")
    if isinstance(request, KpiRequest):
        task_prompt = render_prompt_from_jinja(
            "research_team_kpi_task_prompt.md.j2",
            {
                "kpi": request,
                "company_description": COMPANY_DESCRIPTION,
            },
        )
    elif isinstance(request, SalesReportRequest):
        task_prompt = render_prompt_from_jinja(
            "research_team_sales_task_prompt.md.j2",
            {
                "request": request,
                "company_description": COMPANY_DESCRIPTION,
            },
        )

    # Create the team for the research task
    db_agent = create_internal_data_agent(
        internal_db=internal_db,
        model_type=ModelTypes.AZURE_OPENAI,
        db_agent_model_type=ModelTypes.AZURE_OPENAI,
    )

    quantitative_agent = await create_quantitative_agent(
        model_type=ModelTypes.AZURE_OPENAI,
        azure_ai_client=azure_ai_client,
    )

    manager = StandardMagenticManager(
        chat_completion_service=get_azure_openai_service(
            model=AzureOpenAIModels.GPT_4o_MINI,
        )
    )

    magentic_orchestration = MagenticOrchestration(
        members=[db_agent, quantitative_agent],
        manager=manager,
        agent_response_callback=handle_intermediate_steps,
    )

    # Invoke the orchestration with the task prompt
    orchestration_result = await magentic_orchestration.invoke(
        task=task_prompt,
        runtime=runtime,
    )
    value = await orchestration_result.get()

    # Delete the coder agent after use
    # This is necessary to clean up resources as the coder agent is created on
    # azure AI foundry.
    await azure_ai_client.agents.delete_agent(quantitative_agent.id)

    return value.content
