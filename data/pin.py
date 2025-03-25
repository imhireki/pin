from abc import ABC, abstractmethod
import json

from web.data_manager import GetRequestManager, make_html_soup
import settings


class IPin(ABC):
    @abstractmethod
    def fetch_data(self) -> dict:
        pass


class PinData(IPin):
    def __init__(self, pin_id: str, get_request_manager: GetRequestManager) -> None:
        self.get_request_manager: GetRequestManager = get_request_manager
        self._id = pin_id
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
        pin_page_response = self.get_request_manager.get(self._url)
        pin_page_html = self.get_request_manager.get_html(pin_page_response)

        pin_page_soup = make_html_soup(pin_page_html)

        script_tag_soup = pin_page_soup.find(
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
        title = self._raw["scraped"].get("title", "")
        alt_title = self._raw["scraped"].get("closeup_unified_title", "")
        return title.strip() or alt_title.strip()

    @property
    def description(self) -> str:
        description = self._raw["scraped"].get("description", "")
        alt_description = self._raw["scraped"].get("closeup_unified_description", "")
        return description.strip() or alt_description.strip()

    @property
    def hashtags(self) -> list[str]:
        return self._raw["scraped"].get("hashtags", [])

    @property
    def dominant_color(self) -> str:
        return self._raw["scraped"].get("dominant_color", "")
