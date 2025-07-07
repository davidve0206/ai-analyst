from langsmith import traceable
from src.agents_langgraph.models import default_models
from src.agents_langgraph.db_agent import get_database_agent
from src.agents_langgraph.tools.db import InternalDatabaseToolkit


@traceable
async def main():
    """
    Main function to run the database agent.
    This is a simple example of how to use the database agent.
    """
    internal_db_toolkit = await InternalDatabaseToolkit.create()
    db_agent = get_database_agent(internal_db_toolkit, default_models)
    query = "What is the date of the most recent 'Invoice Date Key' in the Fact.Sale table? Respond in the format YYYY-MM-DD."

    async for event in db_agent.astream(
        {"messages": [("user", query)]}, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
