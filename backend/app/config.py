import os
from pathlib import Path

DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/downloads"))
CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "/config"))
COOKIES_DIR = Path(os.getenv("COOKIES_DIR", "/cookies"))

YTDLP_CONF = CONFIG_DIR / "yt-dlp.conf"
GALLERYDL_CONF = CONFIG_DIR / "gallery-dl.conf"

for d in (DOWNLOAD_DIR, CONFIG_DIR, COOKIES_DIR):
    d.mkdir(parents=True, exist_ok=True)

if not YTDLP_CONF.exists():
    YTDLP_CONF.write_text("# yt-dlp config\n# https://github.com/yt-dlp/yt-dlp#configuration\n")
if not GALLERYDL_CONF.exists():
    GALLERYDL_CONF.write_text('{\n  "extractor": {}\n}\n')
