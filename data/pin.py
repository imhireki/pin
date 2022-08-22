from abc import ABC, abstractmethod
from typing import Union, Any

from bs4 import BeautifulSoup
import requests
import json


class IPin(ABC):
    def fetch_data(self) -> dict[str, Union[str, list]]: pass


class PinData(IPin):
    def __init__(self, pin_url: str) -> None:
        self._pin_url: str = pin_url
        self._raw_pin_data: dict[str, Any] = self._fetch_raw_pin_data()

    def fetch_data(self) -> dict[str, Union[str, list]]:
        return {
            "url": self._pin_url,
            "title": self._get_title(),
            "description": self._get_description(),
            "hashtags": self._get_hashtags(),
            "dominant_color": self._get_dominant_color(),
            "images": self._get_images(),
        }

    def _fetch_raw_pin_data(self) -> dict[str, Any]:
        response = requests.get(self._pin_url)

        pin_page_soup = BeautifulSoup(response.text, 'html.parser')
        script_tag_soup = pin_page_soup.find('script', id='__PWS_DATA__', type='application/json')

        script_tag_dict = json.loads(script_tag_soup.text)

        pin_resource = script_tag_dict['props']['initialReduxState']['resources']['PinResource']
        return pin_resource[list(pin_resource.keys())[0]]['data']

    def _get_title(self) -> str:
        return self._raw_pin_data['title']

    def _get_description(self) -> str:
        return self._raw_pin_data['description']

    def _get_hashtags(self) -> list[str]:
        return self._raw_pin_data['hashtags']

    def _get_dominant_color(self) -> str:
        return self._raw_pin_data['dominant_color']

    def _get_images(self) -> list[str]:
        if not self._raw_pin_data['carousel_data']:
            return [self._raw_pin_data['images']['736x']['url']]

        images_carousel = self._raw_pin_data['carousel_data']['carousel_slots']
        return [carousel_data['images']['736x']['url'] for carousel_data in images_carousel]


class Pin(IPin):
    _fetched_data: str
    _pin_data: PinData

    def __init__(self, pin_url: str) -> None:
        self._pin_url: str = pin_url

    def get_pin_data(self) -> PinData:
        if not hasattr(self, '_pin_data'):
            self._pin_data = PinData(self._pin_url)
        return self._pin_data

    def fetch_data(self) -> dict[str, Union[str, list]]:
        self.get_pin_data()

        if not hasattr(self, '_fetched_data'):
            self._fetched_data = self._pin_data.fetch_data()
        return self._fetched_data

    def is_valid(self) -> bool:
        self.fetch_data()

        if not self._fetched_data['images']:
            return False
        return True
