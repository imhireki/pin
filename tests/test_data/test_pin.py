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


class TestPin:
    def test_pin_data(self, mocker):
        pin_data_mock = mocker.patch('data.pin.PinData', return_value=mocker.Mock())

        pin_object = pin.Pin('_')
        pin_data = pin_object.get_pin_data()

        assert pin_data_mock.call_args.args == ('_',)
        assert pin_data is pin_data_mock()
        assert pin_object._pin_data is pin_data_mock()

    def test_fetch_data(self, mocker):
        data = {"x": 1, "y": 2}
        mocker.patch('data.pin.PinData')

        pin_object = pin.Pin('_')
        pin_object._pin_data = mocker.Mock(fetch_data=lambda: data)

        fetched_data = pin_object.fetch_data()

        assert fetched_data == data
        assert pin_object._fetched_data == data

    @pytest.mark.parametrize('fetched_data,validity', [
        [{"images": ['img.jpg']}, True],
        [{"images": []}, False]
    ])
    def test_is_valid(self, mocker, fetched_data, validity):
        mocker.patch('data.pin.PinData')

        pin_object = pin.Pin('_')
        mocker.patch.object(pin_object, 'fetch_data')
        pin_object._fetched_data = fetched_data

        assert pin_object.is_valid() is validity
        assert pin_object.fetch_data.called

@pytest.mark.e2e
def test_pin_single_image_source():
    pin_single_image_data = {
        'url': 'https://www.pinterest.com/pin/581105158183245043/',
        'title': 'Shanks', 'description': ' ', 'hashtags': [], 'dominant_color': '#fdfdfd',
        'images': ['https://i.pinimg.com/736x/68/92/17/689217658bbff324dfba0621ce9449fa.jpg']
    }
    pin_single_image_url = 'https://www.pinterest.com/pin/581105158183245043/'

    pin_data = pin.PinData(pin_single_image_url)

    assert pin_data.fetch_data() == pin_single_image_data

@pytest.mark.e2e
def test_pin_multiple_images_source():
    pin_multiple_images_data = {
        'url': 'https://www.pinterest.com/pin/10485011624488809/',
        'title': 'Luffy & Zoro Matching Icon', 'description': 'One Piece', 'hashtags': [],
        'dominant_color': '#6e6e90',
        'images': ['https://i.pinimg.com/736x/ed/02/90/ed029092be09633a085854675461cbd1.jpg',
                   'https://i.pinimg.com/736x/e3/0f/4b/e30f4b0e9cf0d1d84bdd0fb382238cb9.jpg']
    }
    pin_multiple_images_url = 'https://www.pinterest.com/pin/10485011624488809/'

    pin_data = pin.PinData(pin_multiple_images_url)

    assert pin_data.fetch_data() == pin_multiple_images_data
