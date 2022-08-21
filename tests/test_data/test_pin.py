import requests
import pytest

from data import pin


class TestPinData:
    pin_url = 'https://pinterest.com/pin/123/'

    @pytest.fixture(autouse=True)
    def patch_pin_request(self, requests_mock, pin_html):
        requests_mock.get(self.pin_url, text=pin_html)

    def test_fetch_raw_pin_data(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._fetch_raw_pin_data() == raw_pin_data
        assert pin_data._raw_pin_data == raw_pin_data

    @pytest.mark.parametrize('carousel_data,images', [
        [{"carousel_data": {}}, ["img.jpg"]],
        [{"carousel_data": {"carousel_slots": [{"images": {"736x": {"url": "img.jpg"}}}]}},
         ["img.jpg"]]
    ])
    def test_fetch_data(self, raw_pin_data, carousel_data, images):
        raw_pin_data.update(**carousel_data)
        pin_data = pin.PinData(self.pin_url)

        fetched_data = {
            "url": self.pin_url,
            "title": raw_pin_data["title"],
            "description": raw_pin_data["description"],
            "dominant_color": raw_pin_data["dominant_color"],
            "hashtags": raw_pin_data["hashtags"],
            "images": images,
        }

        assert pin_data.fetch_data() == fetched_data

    def test_get_title(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_title() == raw_pin_data['title']

    def test_get_description(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_description() == raw_pin_data['description']

    def test_get_description(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_description() == raw_pin_data['description']

    def test_get_dominant_color(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_dominant_color() == raw_pin_data['dominant_color']

    def test_get_hashtags(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_hashtags() == raw_pin_data['hashtags']

    def test_get_images(self, raw_pin_data):
        pin_data = pin.PinData(self.pin_url)
        assert pin_data._get_images() == [raw_pin_data['images']['736x']['url']]
