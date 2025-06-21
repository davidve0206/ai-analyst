import asyncio

from src.agents.internal_data_agent import create_internal_data_agent
from src.agents.tools.db import InternalDatabase
from src.agents.utils.output_utils import invoke_agent_displaying_intermediate_steps
from src.configuration.logger import default_logger


async def main():
    default_logger.info("Starting agent main process...")

    # Initialize the internal database
    internal_db = await InternalDatabase.create()

    agent = create_internal_data_agent(internal_db=internal_db)
    await invoke_agent_displaying_intermediate_steps(
        agent=agent,
        messages="How much revenue did we make every year that is available in the database?",
    )


if __name__ == "__main__":
    asyncio.run(main())
