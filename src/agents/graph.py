from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.models import default_models as models_client
from src.agents.quant_agent import get_quantitative_agent
from src.agents.utils.prompt_utils import (
    PrompTypes,
    create_multimodal_prompt,
    extract_graph_response_content,
    get_all_temp_files,
    get_sales_history_location,
    render_prompt_template,
)
from src.configuration.constants import DATA_PROVIDED
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR, DATA_DIR, app_settings


class SalesResearchGraphState(BaseModel):
    request: SalesReportRequest
    sales_history: str = ""
    sales_analysis: str = ""
    sales_operational_data: str = ""
    is_special_case: bool = False
    sales_in_depth_analysis: str = ""
    report: str = ""


class GraphNodeNames(Enum):
    RETRIEVE_SALES_HISTORY = "retrieve_sales_history"
    PROCESS_SALES_DATA = "process_sales_data"
    RETRIEVE_OPERATIONAL_DATA = "retrieve_operational_data"
    REVIEW_SPECIAL_CASE = "review_special_case"
    PROCESS_SPECIAL_CASE = "process_special_case"
    GENERATE_REPORT = "generate_report"


# Agents to be used in the graph
quant_agent = get_quantitative_agent(models_client)


async def retrieve_sales_history(state: SalesResearchGraphState):
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
        type=PrompTypes.HUMAN,
    )

    response = await quant_agent.ainvoke({"messages": [task_prompt]})
    response_content = extract_graph_response_content(response)
    return {"sales_history": response_content}


async def process_sales_data(state: SalesResearchGraphState):
    """
    Process the sales data retrieved from the database.
    """
    input_location = get_sales_history_location(state.request.grouping_value)
    task_prompt = render_prompt_template(
        template_name="analyse_sales_step_prompt.md",
        context={
            "grouping": state.request.grouping,
            "grouping_value": state.request.grouping_value,
            "input_location": str(input_location),
        },
        type=PrompTypes.HUMAN,
    )

    response = await quant_agent.ainvoke({"messages": [task_prompt]})
    response_content = extract_graph_response_content(response)
    return {"sales_analysis": response_content}


async def retrieve_operational_data(state: SalesResearchGraphState):
    """Retrieve operational data for the sales history."""
    pass


async def review_special_cases(
    state: SalesResearchGraphState,
):
    """
    Check whether there are any special cases to review in the sales data.
    """
    task_prompt = render_prompt_template(
        "review_special_case_step_prompt.md",
        context={
            "sales_analysis": state.sales_analysis,
        },
        type=PrompTypes.HUMAN,
    )

    # Response format is a simple yes/no
    class ReviewResponse(BaseModel):
        is_special_case: bool = Field(
            description="Whether there is a special case to review; answer with True or False."
        )

    structured_response_model = models_client.default_model.with_structured_output(
        ReviewResponse
    )
    response: ReviewResponse = await structured_response_model.ainvoke(
        [task_prompt]
    )
    return {
        "is_special_case": response.is_special_case,
    }


def special_case_gate(
    state: SalesResearchGraphState,
) -> Literal["generate_report", "process_special_case"]:
    """
    Gate to determine whether to process a special case or generate the report.
    """
    if state.is_special_case:
        return GraphNodeNames.PROCESS_SPECIAL_CASE.value
    else:
        return GraphNodeNames.GENERATE_REPORT.value


async def process_special_case(state: SalesResearchGraphState):
    """
    If there is a special case, we will process it in depth.
    This is a placeholder for the actual processing logic.
    """
    return {"sales_in_depth_analysis": state.sales_analysis}


async def generate_report(state: SalesResearchGraphState):
    """
    Generate the sales report based on the sales history.
    This is a placeholder for the actual report generation logic.
    """
    # TODO: We might want to add a step to review the report and make changes
    #       before sending it to the user.

    # Get the system prompt for the editor agent
    system_message = render_prompt_template(
        template_name="editor_agent_system_prompt.md",
        context={},
        type=PrompTypes.SYSTEM,
    )

    # Finally, we create the message and send to the LLM
    prompt = create_multimodal_prompt(
        text_parts=state.sales_analysis,
        file_list=get_all_temp_files(),
        system_message=system_message,
    )

    result = await models_client.gpt_o4_mini.ainvoke(prompt)
    return {"report": result.content}


async def create_research_graph(
    store_diagram: bool = False,
) -> CompiledStateGraph[
    SalesResearchGraphState, SalesResearchGraphState, SalesResearchGraphState
]:
    """
    Create the state graph for the sales report generation.

    To be invokes with a request of type SalesReportRequest.
    """

    graph = StateGraph(SalesResearchGraphState)

    # Add all noted nodes to the graph
    graph.add_node(
        GraphNodeNames.RETRIEVE_SALES_HISTORY.value,
        retrieve_sales_history,
    )
    graph.add_node(
        GraphNodeNames.PROCESS_SALES_DATA.value,
        process_sales_data,
    )
    graph.add_node(
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
        retrieve_operational_data,
    )
    graph.add_node(
        GraphNodeNames.REVIEW_SPECIAL_CASE.value,
        review_special_cases,
    )
    graph.add_node(
        GraphNodeNames.PROCESS_SPECIAL_CASE.value,
        process_special_case,
    )
    graph.add_node(
        GraphNodeNames.GENERATE_REPORT.value,
        generate_report,
    )

    # Add edges to connect the nodes
    graph.add_edge(START, GraphNodeNames.RETRIEVE_SALES_HISTORY.value)
    graph.add_edge(
        GraphNodeNames.RETRIEVE_SALES_HISTORY.value,
        GraphNodeNames.PROCESS_SALES_DATA.value,
    )
    graph.add_edge(
        GraphNodeNames.PROCESS_SALES_DATA.value,
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
    )
    graph.add_edge(
        GraphNodeNames.RETRIEVE_OPERATIONAL_DATA.value,
        GraphNodeNames.REVIEW_SPECIAL_CASE.value,
    )
    graph.add_conditional_edges(
        GraphNodeNames.REVIEW_SPECIAL_CASE.value, special_case_gate
    )
    graph.add_edge(
        GraphNodeNames.PROCESS_SPECIAL_CASE.value,
        GraphNodeNames.GENERATE_REPORT.value,
    )
    graph.add_edge(GraphNodeNames.GENERATE_REPORT.value, END)

    chain = graph.compile()

    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the sales research graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "sales_research_graph.png")
        )

    return chain
