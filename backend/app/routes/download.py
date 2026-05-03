import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..jobs import store
from ..workers.detect import detect_tool
from ..workers.runner import run_ytdlp, run_gallerydl

router = APIRouter()


class DownloadIn(BaseModel):
    url: str
    tool: Optional[str] = None  # "yt-dlp" | "gallery-dl" | None=auto
    cookies: Optional[str] = None  # filename in COOKIES_DIR


@router.post("/api/download")
async def download(body: DownloadIn):
    url = body.url.strip()
    if not url:
        raise HTTPException(400, "empty url")
    tool = body.tool or detect_tool(url)
    job = store.create(url, tool)
    coro = run_ytdlp(job, body.cookies) if tool == "yt-dlp" else run_gallerydl(job, body.cookies)
    asyncio.create_task(coro)
    return {"id": job.id, "tool": tool}


@router.get("/api/jobs")
async def list_jobs():
    return store.list()


@router.get("/api/jobs/{jid}")
async def get_job(jid: str):
    j = store.get(jid)
    if not j:
        raise HTTPException(404, "no such job")
    snap = j.snapshot()
    snap["log"] = j.log[-500:]
    return snap
