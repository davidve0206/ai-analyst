from enum import Enum
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.db_agent import get_database_agent
from src.agents.models import AppChatModels
from src.agents.tools.db import InternalDatabaseToolkit
from src.agents.utils import extract_graph_response_content
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger


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


CALIFORNIA_MONTHLY_SALES_CACHE = "Here is the last three years of monthly total sales data (excluding taxes) for California, formatted as YYYY-MM:\n\n| Month-Year | Total Sales  |\n|------------|--------------|\n| 2025-05    | 200624.20    |\n| 2025-04    | 212986.75    |\n| 2025-03    | 232004.15    |\n| 2025-02    | 197168.70    |\n| 2025-01    | 231620.75    |\n| 2024-12    | 248809.15    |\n| 2024-11    | 169227.50    |\n| 2024-10    | 277312.45    |\n| 2024-09    | 210397.65    |\n| 2024-08    | 174239.60    |\n| 2024-07    | 294432.50    |\n| 2024-06    | 269011.10    |\n| 2024-05    | 186417.50    |\n| 2024-04    | 285375.45    |\n| 2024-03    | 211678.75    |\n| 2024-02    | 220957.65    |\n| 2024-01    | 227591.75    |\n| 2023-12    | 244497.65    |\n| 2023-11    | 184132.40    |\n| 2023-10    | 217520.45    |\n| 2023-09    | 200238.90    |\n| 2023-08    | 169368.60    |\n| 2023-07    | 298161.80    |\n| 2023-06    | 169257.70    |\n| 2023-05    | 262177.15    |\n| 2023-04    | 249891.10    |\n| 2023-03    | 219177.95    |\n| 2023-02    | 194381.50    |\n| 2023-01    | 192188.20    |\n| 2022-12    | 199803.00    |\n| 2022-11    | 220820.90    |\n| 2022-10    | 220462.45    |\n| 2022-09    | 232417.60    |\n| 2022-08    | 135010.70    |\n| 2022-07    | 172959.55    |\n\nThis data reflects the total sales (excluding taxes) for each month over the last three years."


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

        """ query = f"Retrieve the last three years of {state.request.period} total sales data, excluding taxes, available in the database for the following {state.request.grouping}: {state.request.grouping_value}. Include the month and year in the response, formatted as YYYY-MM."
        response = await db_agent.ainvoke({"messages": [("user", query)]})
        response_content = extract_graph_response_content(response)
        return {"sales_history": response_content} """
        return {"sales_history": CALIFORNIA_MONTHLY_SALES_CACHE}

    async def process_sales_data(state: ResearchGraphState) -> ResearchGraphState:
        """
        Process the sales data retrieved from the database.
        This is a placeholder for the actual processing logic.
        """
        query = f"""Perform an in-depth analysis of the sales history data for {state.request.grouping} - {state.request.grouping_value}. Identify trends, patterns, and insights that can be derived from the data. Provide all of your findings in a structured format.
        
        The sales history data is as follows:
        {state.sales_history}"""
        response = await db_agent.ainvoke(query)
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
