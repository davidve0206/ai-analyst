from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import default_models as models_client
from src.agents.quant_agent import QuantitativeAgentResponse, get_quantitative_agent
from src.agents.report_editor_graph import (
    ReportEditorGraphState,
    create_report_editor_graph,
)
from src.agents.research_graph import ResearchGraphState, create_research_graph
from src.agents.utils.prompt_utils import (
    MessageTypes,
    create_human_message_from_parts,
    create_multimodal_prompt,
    extract_graph_response_content,
    get_sales_history_location,
    render_prompt_template,
)
from src.configuration.constants import DATA_PROVIDED
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR, DATA_DIR, app_settings


class SalesReportGraphState(BaseModel):
    request: SalesReportRequest
    sales_history: str = ""
    sales_history_code: str = ""
    sales_analysis: str = ""
    sales_operational_data: str = ""
    sales_operational_data_code: str = ""
    is_special_case: bool = False
    special_case_reason: str = ""
    sales_in_depth_analysis: str = ""
    report: str = ""


class GraphNodeNames(Enum):
    RETRIEVE_SALES_HISTORY = "retrieve_sales_history"
    PROCESS_SALES_DATA = "process_sales_data"
    RETRIEVE_OPERATIONAL_DATA = "retrieve_operational_data"
    REVIEW_SPECIAL_CASE = "review_special_case"
    PROCESS_SPECIAL_CASE = "process_special_case"
    GENERATE_REPORT = "generate_report"


async def retrieve_sales_history(state: SalesReportGraphState):
    """
    First LLM call, retrieve the sales history for the last 3 years
    from the database.
    """
    default_logger.info(
        f"Retrieving sales history for {state.request.grouping} - {state.request.grouping_value}."
    )
    output_location = get_sales_history_location(state.request.grouping_value)
    task_prompt = render_prompt_template(
        template_name="retrieve_sales_step_prompt.md",
        context={
            "date": app_settings.analysis_date,
            "periodicity": state.request.period,
            "grouping": state.request.grouping,
            "grouping_value": state.request.grouping_value,
            "input_location": str(DATA_DIR / DATA_PROVIDED.name),
            "data_description": DATA_PROVIDED.description,
            "output_location": str(output_location),
        },
        type=MessageTypes.HUMAN,
    )

    quant_agent = get_quantitative_agent(models_client)
    response = await quant_agent.ainvoke({"messages": [task_prompt]})
    quant_agent_response: QuantitativeAgentResponse = extract_graph_response_content(
        response
    )
    return {
        "sales_history": quant_agent_response.content,
        "sales_history_code": quant_agent_response.code,
    }


async def process_sales_data(state: SalesReportGraphState):
    """
    Process the sales data retrieved from the database.
    """
    default_logger.info(
        f"Processing sales data for {state.request.grouping} - {state.request.grouping_value}."
    )
    input_location = get_sales_history_location(state.request.grouping_value)
    task_prompt = render_prompt_template(
        template_name="analyse_sales_step_prompt.md",
        context={
            "grouping": state.request.grouping,
            "grouping_value": state.request.grouping_value,
            "input_location": str(input_location),
        },
        type=MessageTypes.HUMAN,
    )

    quant_agent = get_quantitative_agent(models_client)
    response = await quant_agent.ainvoke({"messages": [task_prompt]})
    quant_agent_response: QuantitativeAgentResponse = extract_graph_response_content(
        response
    )
    return {"sales_analysis": quant_agent_response.content}


async def retrieve_operational_data(state: SalesReportGraphState):
    """Retrieve operational data for the sales history."""
    default_logger.info(
        f"Retrieving operational data for {state.request.grouping} - {state.request.grouping_value}."
    )
    task_message = render_prompt_template(
        template_name="retrieve_operational_data_step_prompt.md",
        context={
            "date": app_settings.analysis_date,
            "periodicity": state.request.period,
            "grouping": state.request.grouping,
            "grouping_value": state.request.grouping_value,
            "input_location": str(DATA_DIR / DATA_PROVIDED.name),
            "data_description": DATA_PROVIDED.description,
            "previous_output_location": str(DATA_DIR / DATA_PROVIDED.name),
        },
        type=MessageTypes.HUMAN,
    )
    prompt = create_multimodal_prompt(
        text_parts=f"The code you used to retrieve the sales history is:\n{state.sales_history_code}",
        file_list=[get_sales_history_location(state.request.grouping_value)],
        human_message=task_message,
    )

    # NOTE: this requires a lot of recursion to get the operational data.
    #       We set a recursion limit to avoid hitting the default limit.
    #       Alternatively, we could use a more structured approach to retrieve the data.
    quant_agent = get_quantitative_agent(models_client)
    response = await quant_agent.ainvoke(prompt, {"recursion_limit": 50})
    quant_agent_response: QuantitativeAgentResponse = extract_graph_response_content(
        response
    )
    return {
        "sales_operational_data": quant_agent_response.content,
        "sales_operational_data_code": quant_agent_response.code,
    }


async def review_special_cases(
    state: SalesReportGraphState,
):
    """
    Check whether there are any special cases to review in the sales data.
    """
    task_prompt = render_prompt_template(
        "review_special_case_step_prompt.md",
        context={
            "sales_analysis": state.sales_analysis,
        },
        type=MessageTypes.HUMAN,
    )

    # Response format is a simple yes/no
    class ReviewResponse(BaseModel):
        is_special_case: bool = Field(
            description="Whether there is a special case to review; answer with True or False."
        )
        special_case_reason: str = Field(
            description="Reason for the special case, providing context or explanation."
        )

    structured_response_model = models_client.default_model.with_structured_output(
        ReviewResponse
    )
    response: ReviewResponse = await structured_response_model.ainvoke([task_prompt])
    return {
        "is_special_case": response.is_special_case,
        "special_case_reason": response.special_case_reason,
    }


def special_case_gate(
    state: SalesReportGraphState,
) -> Literal["generate_report", "process_special_case"]:
    """
    Gate to determine whether to process a special case or generate the report.
    """
    if state.is_special_case:
        return GraphNodeNames.PROCESS_SPECIAL_CASE.value
    else:
        return GraphNodeNames.GENERATE_REPORT.value


async def process_special_case(state: SalesReportGraphState):
    """
    If there is a special case, we will process it in depth.
    """
    # Get the graph that processes the special case
    researcher_workflow = await create_research_graph()

    task_prompt = render_prompt_template(
        "research_task_prompt.md",
        context={
            "date": app_settings.analysis_date,
            "grouping": state.request.grouping,
            "grouping_value": state.request.grouping_value,
            "special_case_reason": state.special_case_reason,
            "input_location": str(DATA_DIR / DATA_PROVIDED.name),
            "data_description": DATA_PROVIDED.description,
            "sales_history": state.sales_history,
            "sales_analysis": state.sales_analysis,
            "sales_operational_data": state.sales_operational_data,
        },
        type=MessageTypes.HUMAN,
    )
    quant_agent_message = create_human_message_from_parts(
        text_parts=[
            "The following code was used to retrieve the sales history:\n",
            state.sales_history_code,
        ],
        file_list=[get_sales_history_location(state.request.grouping_value)],
    )

    result = await researcher_workflow.ainvoke(
        ResearchGraphState(
            task_id=state.request.task_id,
            task=task_prompt.content,
            quant_agent_context=[quant_agent_message],
        ),
        {"recursion_limit": 10000},
    )

    return {"sales_in_depth_analysis": result["task_output"]}


async def generate_report(state: SalesReportGraphState):
    """
    Generate the sales report based on the sales history,
    using the report_editor_graph.
    """
    # Get the graph that edits the report
    editor_workflow = await create_report_editor_graph()

    # We assume that all files are mentioned in the outputs
    # so no need to explicitly include files.
    text_parts = [
        state.sales_history,
        state.sales_analysis,
        state.sales_operational_data,
        state.sales_in_depth_analysis,
    ]

    result = await editor_workflow.ainvoke(
        ReportEditorGraphState(
            messages=[
                create_human_message_from_parts(
                    text_parts=text_parts,
                )
            ],
        )
    )
    return {"report": result["report"]}


async def create_report_graph(
    store_diagram: bool = False,
) -> CompiledStateGraph[
    SalesReportGraphState, SalesReportGraphState, SalesReportGraphState
]:
    """
    Create the state graph for the sales report generation.

    To be invokes with a request of type SalesReportRequest.
    """

    workflow = StateGraph(SalesReportGraphState)

    # Add all noted nodes to the graph
    workflow.add_node(
        GraphNodeNames.RETRIEVE_SALES_HISTORY.value,
        retrieve_sales_history,
    )
    workflow.add_node(
        GraphNodeNames.PROCESS_SALES_DATA.value,
        process_sales_data,
    )
    workflow.add_node(
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
        retrieve_operational_data,
    )
    workflow.add_node(
        GraphNodeNames.REVIEW_SPECIAL_CASE.value,
        review_special_cases,
    )
    workflow.add_node(
        GraphNodeNames.PROCESS_SPECIAL_CASE.value,
        process_special_case,
    )
    workflow.add_node(
        GraphNodeNames.GENERATE_REPORT.value,
        generate_report,
    )

    # Add edges to connect the nodes
    workflow.add_edge(START, GraphNodeNames.RETRIEVE_SALES_HISTORY.value)
    workflow.add_edge(
        GraphNodeNames.RETRIEVE_SALES_HISTORY.value,
        GraphNodeNames.PROCESS_SALES_DATA.value,
    )
    workflow.add_edge(
        GraphNodeNames.PROCESS_SALES_DATA.value,
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
    )
    workflow.add_edge(
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
        GraphNodeNames.REVIEW_SPECIAL_CASE.value,
    )
    workflow.add_conditional_edges(
        GraphNodeNames.REVIEW_SPECIAL_CASE.value, special_case_gate
    )
    workflow.add_edge(
        GraphNodeNames.PROCESS_SPECIAL_CASE.value,
        GraphNodeNames.GENERATE_REPORT.value,
    )
    workflow.add_edge(GraphNodeNames.GENERATE_REPORT.value, END)

    chain = workflow.compile()

    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the sales report graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "sales_report_graph.png")
        )

    return chain
