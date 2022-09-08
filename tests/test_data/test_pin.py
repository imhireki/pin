import pytest

from data import pin


@pytest.mark.parametrize('carousel_data, images', [
    ({"carousel_data": {}}, ["img.jpg"]),
    (
        {"carousel_data": {"carousel_slots": [
            {"images": {"736x": {"url": "img.jpg"}}}
        ]}},
        ["img.jpg"]
    )
])
def test_pin_data(mocker, raw_pin_data, make_pin_html, carousel_data, images):
    raw_pin_data.update(**carousel_data)
    mocker.patch('requests.get',
                 return_value=mocker.Mock(text=make_pin_html(raw_pin_data)))
    pin_url = 'https://pinterest.com/pin/123/'
    expected_fetched_data = {
        "url": pin_url,
        "title": raw_pin_data["title"],
        "description": raw_pin_data["description"],
        "dominant_color": raw_pin_data["dominant_color"],
        "hashtags": raw_pin_data["hashtags"],
        "images": images,
    }

    pin_data = pin.PinData(pin_url)
    fetched_data = pin_data.fetch_data()

    assert fetched_data == expected_fetched_data

@pytest.mark.e2e
def test_pin_single_image_source():
    pin_url = 'https://www.pinterest.com/pin/581105158183245043/'
    expected_pin_data = {
        'url': pin_url,
        'title': 'Shanks',
        'description': ' ',
        'dominant_color': '#fdfdfd',
        'hashtags': [],
        'images': [
            'https://i.pinimg.com/736x/68/92/17/'\
            '689217658bbff324dfba0621ce9449fa.jpg'
        ]
    }

    pin_data = pin.PinData(pin_url)
    fetched_data = pin_data.fetch_data()

    assert fetched_data == expected_pin_data

@pytest.mark.e2e
def test_pin_multiple_images_source():
    pin_url = 'https://www.pinterest.com/pin/10485011624488809/'
    expected_pin_data = {
        'url': pin_url,
        'title': 'Luffy & Zoro Matching Icon',
        'description': 'One Piece',
        'dominant_color': '#6e6e90',
        'hashtags': [],
        'images': [
            'https://i.pinimg.com/736x/ed/02/90/'\
            'ed029092be09633a085854675461cbd1.jpg',

            'https://i.pinimg.com/736x/e3/0f/4b/'\
            'e30f4b0e9cf0d1d84bdd0fb382238cb9.jpg'
        ]
    }

    pin_data = pin.PinData(pin_url)
    fetched_data = pin_data.fetch_data()

    assert fetched_data == expected_pin_data


class TestPin:
    def test_get_pin_data(self, mocker):
        pin_data_mock = mocker.patch('data.pin.PinData')
        pin_url = 'url'

        pin_object = pin.Pin(pin_url)
        pin_data_object = pin_object.get_pin_data()

        assert pin_data_mock.call_args.args == (pin_url,)
        assert pin_data_object is pin_data_mock.return_value
        assert pin_object._pin_data is pin_data_mock.return_value

    def test_fetch_data(self, mocker):
        expected_data = {"x": 1, "y": 2}
        mocker.patch(
            'data.pin.PinData',
            return_value=mocker.Mock(fetch_data=lambda: expected_data))

        pin_object = pin.Pin('url')
        fetched_data = pin_object.fetch_data()

        assert fetched_data == expected_data
        assert pin_object._fetched_data == expected_data

    @pytest.mark.parametrize('fetched_data, validity', [
        ({"images": ['img.jpg']}, True),
        ({"images": []}, False)
    ])
    def test_is_valid(self, mocker, fetched_data, validity):
        pin_object = pin.Pin('url')
        pin_object._fetched_data = fetched_data
        mocker.patch.object(pin_object, 'fetch_data', return_value=fetched_data)

        pin_is_valid = pin_object.is_valid()

        assert pin_is_valid is validity
