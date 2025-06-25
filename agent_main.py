import asyncio

from semantic_kernel.agents.runtime import InProcessRuntime

from src.agents.research_team import invoke_research_team_task
from src.agents.tools.db import InternalDatabase
from src.configuration.company import KPI_LIST
from src.configuration.logger import default_logger


async def main():
    default_logger.info("Starting agent main process...")

    # Get a Runtime instance
    runtime = InProcessRuntime()
    runtime.start()

    # Initialize the internal database
    internal_db = await InternalDatabase.create()

    results = {}
    async with asyncio.TaskGroup() as tg:
        for kpi in KPI_LIST:
            tg.create_task(
                invoke_research_team_task(
                    kpi=kpi,
                    internal_db=internal_db,
                    runtime=runtime,
                    results_dict=results,
                )
            )

    await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())
