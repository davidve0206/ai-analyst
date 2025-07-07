from enum import Enum
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents_langgraph.db_agent import get_database_agent
from src.agents_langgraph.models import AppChatModels
from src.agents_langgraph.tools.db import InternalDatabaseToolkit
from src.agents_langgraph.utils import extract_graph_response_content
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger


class ResearchGraphState(BaseModel):
    request: SalesReportRequest
    sales_history: str = ""
    report: str = ""


class GraphNodeNames(Enum):
    GET_SALES_HISTORY = "get_sales_history"
    PROCESS_SALES_DATA = "process_sales_data"
    GENERATE_REPORT = "generate_report"
    SEND_EMAIL = "send_email"


async def create_research_graph(
    internal_db_toolkit: InternalDatabaseToolkit,
    models_client: AppChatModels,
) -> CompiledStateGraph[ResearchGraphState, ResearchGraphState, ResearchGraphState]:
    """
    Create the state graph for the sales report generation.

    To be invokes with a request of type SalesReportRequest.
    """
    db_agent = get_database_agent(internal_db_toolkit, models_client)

    async def get_sales_history(state: ResearchGraphState):
        """
        First LLM call, retrieve the sales history for the last 3 years
        from the database.
        """
        default_logger.info(
            f"Retrieving sales history for {state.request.grouping} - {state.request.grouping_value}."
        )

        query = f"Retrieve the last three years of {state.request.period} total sales data, excluding taxes, available in the database for the following {state.request.grouping}: {state.request.grouping_value}. Include the month and year in the response, formatted as YYYY-MM."
        response = await db_agent.ainvoke({"messages": [("user", query)]})
        response_content = extract_graph_response_content(response)
        return {"sales_history": response_content}

    async def process_sales_data(state: ResearchGraphState) -> ResearchGraphState:
        """
        Process the sales data retrieved from the database.
        This is a placeholder for the actual processing logic.
        """
        # Here you would implement the logic to process the sales data
        # For now, we just return the state as is

        return {"sales_history": state.sales_history}

    async def generate_report(state: ResearchGraphState) -> str:
        """
        Generate the sales report based on the sales history.
        This is a placeholder for the actual report generation logic.
        """
        # Here you would implement the logic to generate a report
        # For now, we just return the sales history as a string
        return {"report": state.sales_history}

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
