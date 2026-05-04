# --- frontend build ---
FROM node:20-bookworm-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- runtime ---
FROM python:3.12-bookworm
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg ca-certificates curl tini \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir --upgrade yt-dlp gallery-dl

COPY backend/ /app/
COPY --from=web /web/build /app/static

VOLUME ["/downloads", "/config", "/cookies"]

ENV DOWNLOAD_DIR=/downloads \
    CONFIG_DIR=/config \
    COOKIES_DIR=/cookies \
    PORT=8080 \
    PYTHONUNBUFFERED=1 \
    HOME=/root

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -fsS "http://localhost:${PORT:-8080}/healthz" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
