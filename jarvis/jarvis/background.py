from __future__ import annotations

from collections import deque


class JobQueue:
    def __init__(self) -> None:
        self.jobs: deque[str] = deque()

    def add(self, job: str) -> None:
        self.jobs.append(job)

    def run_next(self) -> str:
        if not self.jobs:
            return "No background jobs."
        job = self.jobs.popleft()
        return f"Completed background job: {job}"

