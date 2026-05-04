import mimetypes
import os
import zipfile
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse

from ..config import DOWNLOAD_DIR

router = APIRouter()


def _safe(rel: str) -> Path:
    p = (DOWNLOAD_DIR / rel.lstrip("/")).resolve()
    try:
        p.relative_to(DOWNLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(400, "path escape")
    return p


@router.get("/api/files")
async def list_dir(path: str = ""):
    d = _safe(path) if path else DOWNLOAD_DIR
    if not d.exists():
        raise HTTPException(404, "not found")
    if not d.is_dir():
        raise HTTPException(400, "not a directory")
    items = []
    for entry in sorted(d.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
        st = entry.stat()
        rel = str(entry.relative_to(DOWNLOAD_DIR))
        items.append({
            "name": entry.name,
            "path": rel,
            "is_dir": entry.is_dir(),
            "size": st.st_size if entry.is_file() else 0,
            "mtime": st.st_mtime,
            "mime": (mimetypes.guess_type(entry.name)[0] or "application/octet-stream") if entry.is_file() else None,
        })
    parent = ""
    if d != DOWNLOAD_DIR:
        parent = str(d.parent.relative_to(DOWNLOAD_DIR))
        if parent == ".":
            parent = ""
    return {"path": "" if d == DOWNLOAD_DIR else str(d.relative_to(DOWNLOAD_DIR)), "parent": parent, "items": items}


@router.delete("/api/files")
async def delete(path: str):
    p = _safe(path)
    if not p.exists():
        raise HTTPException(404, "not found")
    if p.is_dir():
        import shutil
        shutil.rmtree(p)
    else:
        p.unlink()
    return {"ok": True}


class _CountingWriter:
    """Non-seekable, write+tell-only sink. zipfile detects no seek() and
    switches to data descriptors so we can stream the archive."""

    def __init__(self):
        self._buf = bytearray()
        self._pos = 0

    def write(self, data) -> int:
        self._buf.extend(data)
        self._pos += len(data)
        return len(data)

    def tell(self) -> int:
        return self._pos

    def flush(self) -> None:
        pass

    def drain(self) -> bytes:
        out = bytes(self._buf)
        self._buf.clear()
        return out


@router.get("/api/files/zip")
async def zip_dir(path: str = ""):
    p = _safe(path) if path else DOWNLOAD_DIR
    if not p.exists():
        raise HTTPException(404, "not found")
    if not p.is_dir():
        raise HTTPException(400, "not a directory")

    name = (p.name if p != DOWNLOAD_DIR else "downloads") + ".zip"

    def gen():
        out = _CountingWriter()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
            for sub in sorted(p.rglob("*")):
                if not sub.is_file():
                    continue
                arc = sub.relative_to(p).as_posix()
                zinfo = zipfile.ZipInfo.from_file(sub, arcname=arc)
                zinfo.compress_type = zipfile.ZIP_STORED
                with zf.open(zinfo, "w") as zfp, open(sub, "rb") as fsrc:
                    while True:
                        chunk = fsrc.read(256 * 1024)
                        if not chunk:
                            break
                        zfp.write(chunk)
                        if len(out._buf) >= 256 * 1024:
                            yield out.drain()
                data = out.drain()
                if data:
                    yield data
        data = out.drain()
        if data:
            yield data

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(gen(), media_type="application/zip", headers=headers)


@router.get("/media/{path:path}")
async def serve(path: str, request: Request):
    p = _safe(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "not found")

    file_size = p.stat().st_size
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    range_h = request.headers.get("range")

    if range_h and range_h.startswith("bytes="):
        rng = range_h[6:]
        start_s, _, end_s = rng.partition("-")
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        def iter_file():
            with open(p, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": mime,
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)

    return FileResponse(p, media_type=mime, headers={"Accept-Ranges": "bytes"})
