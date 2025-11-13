import os
import requests
from io import BytesIO
from PIL import Image
from youtubesearchpython import VideosSearch


def extract_id(link: str) -> str:
    """Extract video ID from link or return raw."""
    link = str(link).strip()

    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]

    if "youtu.be/" in link:
        return link.split("youtu.be/")[-1].split("?")[0]

    return link


def get_best_thumbnail(video_id: str) -> str:
    """Try all YouTube thumbnail resolutions until one works."""
    urls = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/hq720.jpg",
        f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/default.jpg",
    ]

    for url in urls:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            return url

    raise Exception("No working thumbnail found.")


def download_thumb(video: str) -> str:
    video = str(video).strip()

    # If it's not a YouTube link or ID → treat as search query
    if (
        "youtu" not in video
        and len(video) != 11
        and not video.isnumeric()
    ):
        results = VideosSearch(video, limit=1).result().get("result", [])
        if not results:
            raise Exception("No search results found.")
        video_id = results[0]["id"]
    else:
        video_id = extract_id(video)

    url = get_best_thumbnail(video_id)
    response = requests.get(url, stream=True)
    img = Image.open(BytesIO(response.content)).convert("RGB")

    os.makedirs("cache", exist_ok=True)
    path = f"cache/thumb-{video_id}.jpg"
    img.save(path, "JPEG")

    return path


class thumb:
    @staticmethod
    def generate(video: str, *args, **kwargs) -> str:
        """Bot-compatible wrapper"""
        try:
            return download_thumb(video)
        except Exception as e:
            print("Thumbnail Error:", e)
            return None
