import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

Job = Callable[[], Awaitable[None]]


class JobQueue:
    def __init__(self, num_workers: int = 2):
        self._queue: asyncio.Queue[Job] = asyncio.Queue()
        self._num_workers = num_workers
        self._workers: list[asyncio.Task] = []

    async def start(self):
        self._workers = [asyncio.create_task(self._worker_loop()) for _ in range(self._num_workers)]

    async def stop(self):
        for worker in self._workers:
            worker.cancel()

    async def enqueue(self, job: Job):
        await self._queue.put(job)

    async def _worker_loop(self):
        while True:
            job = await self._queue.get()
            try:
                await job()
            except Exception:
                # a job blowing up shouldn't kill the whole worker
                logger.exception("job failed")


job_queue = JobQueue()
