from abc import ABC, abstractmethod
import json

from bs4 import BeautifulSoup
from requests import Session

import settings


class MaxLength:
    TITLE = 255
    DESCRIPTION = 255
    DOMINANT_COLOR = 7
    HASHTAG = 255


class IPin(ABC):
    @abstractmethod
    def fetch_data(self) -> dict:
        pass


class PinData(IPin):
    def __init__(self, pin_id: str, session: Session) -> None:
        self._id = pin_id
        self._session = session
        self._url = self._make_url(pin_id)

    def fetch_data(self) -> dict:
        data = {"custom": {}, "scraped": {}}

        data["scraped"].update(self._fetch_data_root())

        data["custom"]["images"] = self._get_images(data["scraped"])
        data["custom"]["url"] = self._url
        data["custom"]["id"] = self._id
        return data

    @staticmethod
    def _make_url(pin_id: str) -> str:
        return settings.URLS["HOME"] + "/pin/" + pin_id

    def _fetch_data_root(self) -> dict:
        pin_html = self._session.get(self._url).text
        pin_soup = BeautifulSoup(pin_html, "html.parser")

        script_tag_soup = pin_soup.find(
            "script", {"id": "__PWS_INITIAL_PROPS__", "type": "application/json"}
        )

        if not script_tag_soup:
            return {}

        script_tag_dict = json.loads(script_tag_soup.text)

        try:
            return script_tag_dict["initialReduxState"]["pins"][self._id]
        except KeyError:
            return {}

    @staticmethod
    def _get_images(data_root: dict) -> list[str]:
        try:
            if data_root.get("carousel_data") is None:
                return [data_root["images"]["orig"]["url"]]
            carousel = data_root["carousel_data"]["carousel_slots"]
            images = [slot["images"]["736x"]["url"] for slot in carousel]
            return images
        except KeyError:
            return []


class Pin(IPin):
    def __init__(self, pin_data: PinData) -> None:
        self._pin_data = pin_data
        self._raw = {"custom": {}, "scraped": {}}
        self._processed = {}

    def fetch_data(self) -> dict:
        if not self._processed:
            self._raw = self._pin_data.fetch_data()

            self._processed = {
                "id": self.id,
                "url": self.url,
                "title": self.title,
                "description": self.description,
                "dominant_color": self.dominant_color,
                "hashtags": self.hashtags,
                "images": self.images,
            }

        return self._processed

    def is_valid(self) -> bool:
        """Ensure there's images along with any text to identify them."""
        self.fetch_data()

        if not self.images:
            return False

        if not self.title and not self.description and not self.hashtags:
            return False

        return True

    @property
    def id(self) -> str:
        return self._raw["custom"].get("id", "")

    @property
    def url(self) -> str:
        return self._raw["custom"].get("url", "")

    @property
    def images(self) -> list[str]:
        return self._raw["custom"].get("images", [])

    @property
    def title(self) -> str:
        title = self._raw["scraped"].get("title") or ""
        alt_title = self._raw["scraped"].get("closeup_unified_title") or ""
        return title.strip()[: MaxLength.TITLE] or alt_title.strip()[: MaxLength.TITLE]

    @property
    def description(self) -> str:
        description = self._raw["scraped"].get("description") or ""
        alt_description = self._raw["scraped"].get("closeup_unified_description") or ""
        return (
            description.strip()[: MaxLength.DESCRIPTION]
            or alt_description.strip()[: MaxLength.DESCRIPTION]
        )

    @property
    def hashtags(self) -> list[str]:
        return [
            hashtag[: MaxLength.HASHTAG]
            for hashtag in self._raw["scraped"].get("hashtags", []) or []
        ]

    @property
    def dominant_color(self) -> str:
        dominant_color = self._raw["scraped"].get("dominant_color", "")
        return dominant_color[: MaxLength.DOMINANT_COLOR]
