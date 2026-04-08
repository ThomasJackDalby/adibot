import asyncio
import os
import logging
import dotenv
import rich.logging

FORMAT = "%(message)s"
handler = rich.logging.RichHandler(rich_tracebacks=True)
# handler.addFilter(logging.Filter(name='adibot'))
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt="[%X]", handlers=[handler])

logger = logging.getLogger("adibot")
logger.info("Starting ADIBOT")

if os.path.exists(".env"): logger.info("Loading env variables from .env file.")
dotenv.load_dotenv()

import bot
import app

async def main():
     async with asyncio.TaskGroup() as task_group:
        task_group.create_task(bot.main())
        task_group.create_task(app.main())

if __name__ == "__main__":
    asyncio.run(main())