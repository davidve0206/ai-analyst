from langsmith import traceable
from src.agents_langgraph.graph import create_research_graph
from src.agents_langgraph.models import default_models
from src.agents_langgraph.tools.db import InternalDatabaseToolkit
from src.agents_langgraph.utils import extract_graph_response_content
from src.configuration.kpis import SalesReportRequest


@traceable
async def main():
    """
    Main function to run the database agent.
    This is a simple example of how to use the database agent.
    """
    internal_db_toolkit = await InternalDatabaseToolkit.create()

    research_graph = await create_research_graph(
        internal_db_toolkit=internal_db_toolkit, models_client=default_models
    )

    test_request = SalesReportRequest(
        grouping="state",
        grouping_value="California",
        period="monthly",
    )

    test_result = await research_graph.ainvoke({"request": test_request})

    print("Test Result:", test_result["report"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
