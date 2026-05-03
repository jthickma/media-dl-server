import re
from fastapi import APIRouter, HTTPException, UploadFile, File

from ..config import COOKIES_DIR

router = APIRouter()

SAFE = re.compile(r"^[A-Za-z0-9._-]+$")


@router.get("/api/cookies")
async def list_cookies():
    return [p.name for p in sorted(COOKIES_DIR.iterdir()) if p.is_file()]


@router.post("/api/cookies")
async def upload_cookie(file: UploadFile = File(...)):
    name = file.filename or "cookies.txt"
    if not SAFE.match(name):
        raise HTTPException(400, "bad filename")
    data = await file.read()
    (COOKIES_DIR / name).write_bytes(data)
    return {"ok": True, "name": name, "bytes": len(data)}


@router.delete("/api/cookies/{name}")
async def delete_cookie(name: str):
    if not SAFE.match(name):
        raise HTTPException(400, "bad filename")
    p = COOKIES_DIR / name
    if not p.exists():
        raise HTTPException(404, "not found")
    p.unlink()
    return {"ok": True}
