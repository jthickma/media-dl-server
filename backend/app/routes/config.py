from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import YTDLP_CONF, GALLERYDL_CONF

router = APIRouter()

CONF_MAP = {
    "yt-dlp": YTDLP_CONF,
    "gallery-dl": GALLERYDL_CONF,
}


class ConfIn(BaseModel):
    content: str


@router.get("/api/config/{name}")
async def get_conf(name: str):
    if name not in CONF_MAP:
        raise HTTPException(404, "unknown config")
    p = CONF_MAP[name]
    return {"name": name, "path": str(p), "content": p.read_text() if p.exists() else ""}


@router.put("/api/config/{name}")
async def set_conf(name: str, body: ConfIn):
    if name not in CONF_MAP:
        raise HTTPException(404, "unknown config")
    CONF_MAP[name].write_text(body.content)
    return {"ok": True, "bytes": len(body.content)}
