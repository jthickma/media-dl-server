import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..jobs import store

router = APIRouter()


@router.websocket("/api/jobs/{jid}/ws")
async def job_ws(ws: WebSocket, jid: str):
    await ws.accept()
    job = store.get(jid)
    if not job:
        await ws.send_json({"type": "error", "message": "no such job"})
        await ws.close()
        return

    q: asyncio.Queue = asyncio.Queue(maxsize=1000)
    job.subscribers.append(q)
    try:
        await ws.send_json({"type": "status", "data": job.snapshot()})
        for line in job.log[-200:]:
            await ws.send_json({"type": "log", "line": line})
        while True:
            try:
                msg = await asyncio.wait_for(q.get(), timeout=30.0)
                await ws.send_json(msg)
                if msg.get("type") == "status" and msg["data"]["status"] in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                await ws.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    finally:
        if q in job.subscribers:
            job.subscribers.remove(q)
