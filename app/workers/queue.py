import asyncio
from collections.abc import Awaitable, Callable

Job = Callable[[], Awaitable[None]]


class JobQueue:
    def __init__(self, num_workers: int = 2):
        self._queue: asyncio.Queue[Job] = asyncio.Queue()
        self._num_workers = num_workers
        self._workers: list[asyncio.Task] = []

    async def start(self):
        self._workers = [
            asyncio.create_task(self._worker_loop()) for _ in range(self._num_workers)
        ]

    async def stop(self):
        for worker in self._workers:
            worker.cancel()

    async def enqueue(self, job: Job):
        await self._queue.put(job)

    async def _worker_loop(self):
        while True:
            job = await self._queue.get()
            await job()


job_queue = JobQueue()
