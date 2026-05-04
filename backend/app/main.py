from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import download, files, cookies, ws

app = FastAPI(title="claude-media-dl")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(download.router)
app.include_router(ws.router)
app.include_router(files.router)
app.include_router(cookies.router)


STATIC_DIR = Path(__file__).parent.parent / "static"


@app.get("/healthz")
async def healthz():
    return {"ok": True}


if STATIC_DIR.exists():
    app.mount("/_app", StaticFiles(directory=str(STATIC_DIR / "_app")), name="svelte_app")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
