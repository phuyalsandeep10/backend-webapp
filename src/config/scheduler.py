import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.tasks.sla_task import check_sla_breach

logger = logging.getLogger("my_scheduler")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # print to stdout
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

scheduler = AsyncIOScheduler()


async def start_scheduler():
    scheduler.add_job((check_sla_breach), IntervalTrigger(seconds=10))
    scheduler.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(start_scheduler())
