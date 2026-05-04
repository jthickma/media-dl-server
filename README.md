# claude-media-dl

Self-hosted Docker web service. Paste URL → yt-dlp / gallery-dl downloads → preview & browse in browser.

## Features

- Auto-detects tool per URL (override available)
- Live progress via WebSocket
- Built-in viewer: video (Range-streamed), audio, image, PDF, text
- File browser with delete
- Edit `yt-dlp.conf` / `gallery-dl.conf` from UI (saved to mounted volume)
- Upload `cookies.txt`, select per-job
- Single-user, no auth

## Run

```sh
docker compose up -d --build
```

Open http://localhost:8080

Volumes:
- `./downloads` — output media
- `./config` — `yt-dlp.conf`, `gallery-dl.conf` (auto-created)
- `./cookies` — uploaded cookies files

## Dev

Backend:
```sh
cd backend
pip install -r requirements.txt
DOWNLOAD_DIR=../downloads CONFIG_DIR=../config COOKIES_DIR=../cookies \
  uvicorn app.main:app --reload --port 8080
```

Frontend:
```sh
cd frontend
npm install
npm run dev   # http://localhost:5173 → proxies /api & /media to :8080
```

## Security

No auth. **Do not expose to the internet.** `--exec` is allowed in yt-dlp configs (RCE-equivalent for whoever can edit config). Run on trusted LAN or behind reverse proxy with auth (Caddy + basic auth, Authelia, etc).
