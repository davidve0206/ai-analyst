import asyncio

from src.agent.internal_data.db import InternalDatabase
from src.configuration.logger import logger


async def main():
    logger.info("Starting agent main process...")
    db = await InternalDatabase.create()
    print(f"Connected to database: {db.dialect} with tables: {db.table_names}")
    print(db.describe_schema())


if __name__ == "__main__":
    asyncio.run(main())
