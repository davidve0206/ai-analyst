from enum import Enum
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.db_agent import get_database_agent
from src.agents.models import AppChatModels
from src.agents.quant_agent import get_quantitative_agent
from src.agents.tools.db import InternalDatabaseToolkit
from src.agents.utils import (
    PrompTypes,
    extract_graph_response_content,
    render_prompt_template,
)
from src.configuration.constants import DATA_PROVIDED
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger
from src.configuration.settings import DATA_DIR, TEMP_DIR, app_settings


class ResearchGraphState(BaseModel):
    request: SalesReportRequest
    sales_history: str = ""
    sales_analysis: str = ""
    report: str = ""


class GraphNodeNames(Enum):
    GET_SALES_HISTORY = "get_sales_history"
    PROCESS_SALES_DATA = "process_sales_data"
    GENERATE_REPORT = "generate_report"
    SEND_EMAIL = "send_email"


async def create_research_graph(
    models_client: AppChatModels,
) -> CompiledStateGraph[ResearchGraphState, ResearchGraphState, ResearchGraphState]:
    """
    Create the state graph for the sales report generation.

    To be invokes with a request of type SalesReportRequest.
    """

    # Agents to be used in the graph
    quant_agent = get_quantitative_agent(models_client)

    async def get_sales_history(state: ResearchGraphState):
        """
        First LLM call, retrieve the sales history for the last 3 years
        from the database.
        """
        default_logger.info(
            f"Retrieving sales history for {state.request.grouping} - {state.request.grouping_value}."
        )
        output_location = TEMP_DIR / f"{state.request.grouping_value}_sales_history.csv"
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

        response = await quant_agent.ainvoke({"messages": [("user", task_prompt)]})
        response_content = extract_graph_response_content(response)
        return {"sales_history": response_content}

    async def process_sales_data(state: ResearchGraphState) -> ResearchGraphState:
        """
        Process the sales data retrieved from the database.
        This is a placeholder for the actual processing logic.
        """
        input_location = TEMP_DIR / f"{state.request.grouping_value}_sales_history.csv"
        task_prompt = render_prompt_template(
            template_name="analyse_sales_step_prompt.md",
            context={
                "grouping": state.request.grouping,
                "grouping_value": state.request.grouping_value,
                "input_location": str(input_location),
            },
            type=PrompTypes.HUMAN,
        )

        response = await quant_agent.ainvoke({"messages": [("user", task_prompt)]})
        response_content = extract_graph_response_content(response)
        return {"sales_analysis": response_content}

    async def generate_report(state: ResearchGraphState) -> str:
        """
        Generate the sales report based on the sales history.
        This is a placeholder for the actual report generation logic.
        """
        # Here you would implement the logic to generate a report
        # For now, we just return the sales history as a string
        return {"report": state.sales_analysis}

    graph = StateGraph(ResearchGraphState)

    # Add all noted nodes to the graph
    graph.add_node(
        GraphNodeNames.GET_SALES_HISTORY.value,
        get_sales_history,
    )
    graph.add_node(
        GraphNodeNames.PROCESS_SALES_DATA.value,
        process_sales_data,
    )
    graph.add_node(
        GraphNodeNames.GENERATE_REPORT.value,
        generate_report,
    )

    # Add edges to connect the nodes
    graph.add_edge(START, GraphNodeNames.GET_SALES_HISTORY.value)
    graph.add_edge(
        GraphNodeNames.GET_SALES_HISTORY.value, GraphNodeNames.PROCESS_SALES_DATA.value
    )
    graph.add_edge(
        GraphNodeNames.PROCESS_SALES_DATA.value, GraphNodeNames.GENERATE_REPORT.value
    )
    graph.add_edge(GraphNodeNames.GENERATE_REPORT.value, END)

    chain = graph.compile()

    return chain
