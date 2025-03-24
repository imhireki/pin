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

        data["custom"]["images"] = self._get_images(data["scraped"])
        data["custom"]["url"] = self._url
        data["custom"]["id"] = self._id

        data["scraped"].update(self._fetch_data_root())

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
            if not "carousel_data" in data_root:
                return [data_root["images"]["736x"]["url"]]

            carousel = data_root["carousel_data"]["carousel_slots"]
            images = [slot["images"]["736x"]["url"] for slot in carousel]
            return images
        except KeyError:
            return []


class Pin(IPin):
    _fetched_data: dict[str, str | list[str]]
    _pin_data: PinData

    def __init__(self, get_request_manager: GetRequestManager, pin_url: str) -> None:
        self.get_request_manager: GetRequestManager = get_request_manager
        self._pin_url: str = pin_url

    def get_pin_data(self) -> PinData:
        if not hasattr(self, "_pin_data"):
            self._pin_data = PinData(self.get_request_manager, self._pin_url)
        return self._pin_data

    def fetch_data(self) -> dict[str, str | list[str]]:
        self.get_pin_data()

        if not hasattr(self, "_fetched_data"):
            self._fetched_data = self._pin_data.fetch_data()
        return self._fetched_data

    def is_valid(self) -> bool:
        self.fetch_data()

        if not self._fetched_data["images"]:
            return False
        return True
