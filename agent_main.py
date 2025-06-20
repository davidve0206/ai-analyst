import asyncio

from src.agents.internal_data_agent import create_internal_data_agent
from src.configuration.logger import logger


async def main():

    logger.info("Starting agent main process...")
    agent = await create_internal_data_agent()
    result = await agent.run(
        task="How much revenue did we make every year thats available in the database?"
    )
    print(result.messages)


if __name__ == "__main__":
    asyncio.run(main())
