import asyncio
import re
import shlex
from pathlib import Path
from typing import Optional

from ..config import DOWNLOAD_DIR, YTDLP_CONF, COOKIES_DIR
from ..jobs import Job

PROGRESS_RE = re.compile(
    r"\[download\]\s+(?P<pct>[\d.]+)%\s+of\s+~?\s*(?P<size>\S+)(?:\s+at\s+(?P<speed>\S+))?(?:\s+ETA\s+(?P<eta>\S+))?"
)
DEST_RE = re.compile(r"\[download\] Destination: (.+)$")
MERGE_RE = re.compile(r"\[Merger\] Merging formats into \"(.+)\"")
GDL_FILE_RE = re.compile(r"^# (.+)$|^(/downloads/.+)$")


async def run_ytdlp(job: Job, cookies: Optional[str] = None):
    args = ["yt-dlp", "--newline", "--no-colors"]
    if YTDLP_CONF.exists():
        args += ["--config-location", str(YTDLP_CONF)]
    if cookies:
        cpath = COOKIES_DIR / cookies
        if cpath.exists():
            args += ["--cookies", str(cpath)]
    out_tmpl = str(DOWNLOAD_DIR / "%(uploader,extractor)s/%(title).100B [%(id)s].%(ext)s")
    args += ["-o", out_tmpl, "--print", "after_move:filepath", job.url]
    await _run(job, args, parse=_parse_ytdlp)


async def run_gallerydl(job: Job, cookies: Optional[str] = None):
    # gallery-dl autoloads $HOME/.config/gallery-dl/config.json (mounted from
    # the host) and falls back to /etc/gallery-dl.conf shipped in the image.
    args = ["gallery-dl", "-d", str(DOWNLOAD_DIR)]
    if cookies:
        cpath = COOKIES_DIR / cookies
        if cpath.exists():
            args += ["--cookies", str(cpath)]
    args += [job.url]
    await _run(job, args, parse=_parse_gallerydl)


async def _run(job: Job, args: list[str], parse):
    job.status = "running"
    job.message = "starting"
    await job.publish({"type": "status", "data": job.snapshot()})
    job.log.append("$ " + " ".join(shlex.quote(a) for a in args))

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(DOWNLOAD_DIR),
        )
    except FileNotFoundError as e:
        job.status = "error"
        job.error = str(e)
        await job.publish({"type": "status", "data": job.snapshot()})
        return

    assert proc.stdout
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        text = line.decode(errors="replace").rstrip()
        job.log.append(text)
        if len(job.log) > 2000:
            job.log = job.log[-1500:]
        await parse(job, text)
        await job.publish({"type": "log", "line": text})

    rc = await proc.wait()
    if rc == 0:
        job.status = "done"
        job.progress = 100.0
        job.message = "complete"
    else:
        job.status = "error"
        job.error = f"exit {rc}"
    await job.publish({"type": "status", "data": job.snapshot()})


async def _parse_ytdlp(job: Job, line: str):
    m = PROGRESS_RE.search(line)
    if m:
        job.progress = float(m.group("pct"))
        job.speed = m.group("speed") or ""
        job.eta = m.group("eta") or ""
        await job.publish({"type": "progress", "data": job.snapshot()})
        return
    m = DEST_RE.search(line) or MERGE_RE.search(line)
    if m:
        p = m.group(1)
        if p not in job.files:
            job.files.append(p)
        return
    if line and not line.startswith("[") and Path(line).exists():
        if line not in job.files:
            job.files.append(line)


async def _parse_gallerydl(job: Job, line: str):
    p = Path(line)
    if p.is_absolute() and p.exists():
        if line not in job.files:
            job.files.append(line)
        await job.publish({"type": "progress", "data": job.snapshot()})
