import json
import urllib.parse

import requests
from pytube import YouTube


class Hell_YTS:
    def __init__(self, search_terms: str, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = self._search()

    def _search(self):
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"

        session = requests.Session()
        response = session.get(url)
        response.raise_for_status()

        html = response.text

        start = html.find("ytInitialData") + len("ytInitialData") + 3
        end = html.find("};", start) + 1
        json_str = html[start:end]
        data = json.loads(json_str)

        videos = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])[0]
            .get("itemSectionRenderer", {})
            .get("contents", [])
        )

        results = []
        for video in videos:
            if "videoRenderer" in video:
                video_data = video["videoRenderer"]
                res = {}
                res["title"] = (
                    video_data.get("title", {})
                    .get("runs", [{}])[0]
                    .get("text", None)
                )
                res["id"] = video_data.get("videoId", None)
                res["url"] = (
                    "https://www.youtube.com/watch?v="
                    + video_data.get("videoId", None)
                )
                res["thumbnail"] = (
                    video_data.get("thumbnail", {})
                    .get("thumbnails", [{}])[-1]
                    .get("url", None)
                )
                res["description"] = (
                    video_data.get("descriptionSnippet", {})
                    .get("runs", [{}])[0]
                    .get("text", None)
                )
                res["channel"] = (
                    video_data.get("longBylineText", {})
                    .get("runs", [[{}]])[0]
                    .get("text", None)
                )
                res["duration"] = video_data.get("lengthText", {}).get(
                    "simpleText", 0
                )
                res["views"] = video_data.get("viewCountText", {}).get(
                    "simpleText", 0
                )

                # ---- FIXED PUBLISH TIME HANDLING ----
                yt_obj = YouTube(
                    "https://www.youtube.com/watch?v="
                    + video_data.get("videoId", "")
                )
                publish_date = getattr(yt_obj, "publish_date", None)
                if publish_date:
                    res["publish_time"] = publish_date.strftime(
                        "%d{} of %B, %Y"
                    ).format(
                        "th"
                        if 4 <= publish_date.day <= 20
                        or 24 <= publish_date.day <= 30
                        else ["st", "nd", "rd"][
                            (publish_date.day - 1) % 10 % 3
                        ]
                    )
                else:
                    # fallback to raw text from search results or "Unknown"
                    res["publish_time"] = video_data.get(
                        "publishedTimeText", {}
                    ).get("simpleText", "Unknown")

                res["url_suffix"] = (
                    video_data.get("navigationEndpoint", {})
                    .get("commandMetadata", {})
                    .get("webCommandMetadata", {})
                    .get("url", None)
                )
                results.append(res)

                if self.max_results and len(results) >= self.max_results:
                    break
        return results

    def to_dict(self, clear_cache=True):
        result = self.videos
        if clear_cache:
            self.videos = ""
        return result

    def to_json(self, clear_cache=True):
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = ""
        return result
