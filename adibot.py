import asyncio
import logging
import rich.logging

FORMAT = "%(message)s"
handler = rich.logging.RichHandler(rich_tracebacks=True)
handler.addFilter(logging.Filter(name='adibot'))
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt="[%X]", handlers=[handler])

logger = logging.getLogger("adibot")
logger.info("Starting ADIBOT")

import bot
import app

async def main():
     async with asyncio.TaskGroup() as task_group:
        task_group.create_task(bot.main())
        task_group.create_task(app.main())

if __name__ == "__main__":
    asyncio.run(main())