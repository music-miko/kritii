import os
import requests
from io import BytesIO
from PIL import Image
from youtubesearchpython import VideosSearch


def _extract_video_id(link: str) -> str:
    """Extract YouTube video ID safely from any string."""
    link = str(link).strip()

    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]
    if "youtu.be/" in link:
        return link.split("youtu.be/")[-1].split("?")[0]

    return link  # fallback raw ID


def _download_thumbnail(video: str) -> str:
    """Download raw YouTube thumbnail only (no branding)."""

    video = str(video).strip()     # 🔥 FIX: ensure string always

    # If it's not a YouTube link → treat as search query
    if "youtube.com" not in video and "youtu.be" not in video and len(video) != 11:
        data = VideosSearch(video, limit=1).result().get("result", [])
        if not data:
            raise Exception("No search results found.")
        video_id = data[0]["id"]
    else:
        video_id = _extract_video_id(video)

    # Try maxres thumbnail
    url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    r = requests.get(url, stream=True)

    # Fallback → HQ thumbnail
    if r.status_code != 200:
        url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        r = requests.get(url, stream=True)

    img = Image.open(BytesIO(r.content)).convert("RGB")

    os.makedirs("cache", exist_ok=True)
    path = f"cache/thumb-{video_id}.jpg"
    img.save(path, "JPEG")

    return path


class thumb:
    @staticmethod
    def generate(video: str, *args, **kwargs) -> str:
        """Bot-compatible wrapper: thumb.generate(video_id)"""
        try:
            return _download_thumbnail(video)
        except Exception as e:
            print("Thumbnail Error:", e)
            return None
