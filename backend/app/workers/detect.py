from urllib.parse import urlparse

GALLERY_HOSTS = {
    "instagram.com", "www.instagram.com",
    "pixiv.net", "www.pixiv.net",
    "deviantart.com", "www.deviantart.com",
    "flickr.com", "www.flickr.com",
    "imgur.com", "i.imgur.com",
    "danbooru.donmai.us", "gelbooru.com", "safebooru.org",
    "twitter.com", "x.com", "nitter.net",
    "tumblr.com",
    "reddit.com", "www.reddit.com", "old.reddit.com",
    "artstation.com", "www.artstation.com",
}


def detect_tool(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host in GALLERY_HOSTS:
        return "gallery-dl"
    return "yt-dlp"
