import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Literal, Optional

JobStatus = Literal["pending", "running", "done", "error"]


@dataclass
class Job:
    id: str
    url: str
    tool: str
    status: JobStatus = "pending"
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    message: str = ""
    files: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    error: Optional[str] = None
    subscribers: list[asyncio.Queue] = field(default_factory=list)

    def snapshot(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "tool": self.tool,
            "status": self.status,
            "progress": self.progress,
            "speed": self.speed,
            "eta": self.eta,
            "message": self.message,
            "files": self.files,
            "error": self.error,
        }

    async def publish(self, event: dict):
        for q in list(self.subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


class JobStore:
    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def create(self, url: str, tool: str) -> Job:
        jid = uuid.uuid4().hex[:12]
        j = Job(id=jid, url=url, tool=tool)
        self.jobs[jid] = j
        return j

    def get(self, jid: str) -> Optional[Job]:
        return self.jobs.get(jid)

    def list(self) -> list[dict]:
        return [j.snapshot() for j in self.jobs.values()]


store = JobStore()
