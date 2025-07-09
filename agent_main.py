from langsmith import traceable
from langgraph.graph.state import CompiledStateGraph

from src.agents.graph import create_research_graph
from src.agents.models import default_models
from src.configuration.kpis import SalesReportRequest


@traceable
async def main():
    """
    Main function to run the database agent.
    This is a simple example of how to use the database agent.
    """

    research_graph: CompiledStateGraph = await create_research_graph(
        models_client=default_models
    )

    test_request = SalesReportRequest(
        grouping="country",
        grouping_value="Spain",
        period="monthly",
    )

    test_result = await research_graph.ainvoke({"request": test_request})

    print("Test Result:", test_result["report"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
