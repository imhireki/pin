from copy import deepcopy

import pytest

from web.data_manager import GetRequestManager
from data.pin import Pin, PinData
from data import pin


class TestPinData:
    def test_fetch_data(self, mocker):
        pin_data = PinData("123", mocker.Mock())

        fetch_data_root = mocker.patch.object(
            pin_data, "_fetch_data_root", lambda: {"data": "root"}
        )
        get_images = mocker.patch.object(pin_data, "_get_images")
        url = mocker.patch.object(pin_data, "_url")

        data = pin_data.fetch_data()

        custom = {
            "images": get_images.return_value,
            "url": url,
            "id": "123",
        }
        assert data == dict(custom=custom, scraped=fetch_data_root())

    def test_make_url(self, mocker):
        pin_data = PinData("123", mocker.Mock())
        assert pin_data._make_url("123") == "https://www.pinterest.com/pin/123"

    @pytest.mark.parametrize(
        "html,result",
        [
            ("<script id='json not found' type='text/javascript'></script>", {}),
            (
                """
            <script id='__PWS_INITIAL_PROPS__' type='application/json'>{}</script>
            """,
                {},
            ),
            (
                """
            <script id='__PWS_INITIAL_PROPS__' type='application/json'>
                {"initialReduxState": {"pins": {"123": {"valid": "data"} }}}
            </script>
            """,
                {"valid": "data"},
            ),
        ],
    )
    def test_fetch_data_root(self, mocker, html, result):
        get_request_manager = mocker.patch("data.pin.GetRequestManager")
        get_request_manager.get_html = lambda _: html

        pin_data = PinData("123", get_request_manager)
        data_root = pin_data._fetch_data_root()

        assert data_root == result

    @pytest.mark.parametrize(
        "root,result",
        [
            ({}, []),
            ({"carousel_data": {}, "images": {}}, []),
            (
                {
                    "carousel_data": {
                        "carousel_slots": [
                            {"images": {"736x": {"url": "carousel1.jpg"}}},
                            {"images": {"736x": {"url": "carousel2.jpg"}}},
                        ]
                    }
                },
                ["carousel1.jpg", "carousel2.jpg"],
            ),
            ({"images": {"736x": {"url": "img.jpg"}}}, ["img.jpg"]),
        ],
    )
    def test_get_images(self, mocker, root, result):
        pin_data = PinData("", mocker.Mock())
        assert pin_data._get_images(root) == result


class TestPin:
    def test_fetch_data(self, mocker):
        extra = {"a": "1", "b": 2}
        clean_raw_data = {
            "custom": {"id": "1", "url": "url", "images": ["img"]},
            "scraped": {
                "title": "title",
                "description": "desc",
                "hashtags": ["#a"],
                "dominant_color": ["#ffffff"],
            },
        }
        raw_data = deepcopy(clean_raw_data)
        raw_data["scraped"].update(extra)

        pin_data = mocker.Mock()
        pin_data.fetch_data = mocker.Mock(return_value=raw_data)

        pin = Pin(pin_data)
        processed = pin.fetch_data()

        pin_data.fetch_data.assert_called()
        assert pin._raw == raw_data
        assert processed == dict(**clean_raw_data["custom"], **clean_raw_data["scraped"])
        assert pin._processed == processed

    @pytest.mark.parametrize("data,is_valid", [
        ({"images": []}, False),
        ({"images": ["img1"]}, False),
        ({"images": ["img1"], "title": "title"}, True),
        ({"images": ["img1"], "description": "desc"}, True),
        ({"images": ["img1"], "hashtags": ["#hash"]}, True),
    ])
    def test_is_valid(self, mocker, data, is_valid):
        pin = Pin(mocker.Mock())
        pin._processed = {"x": "y"}

        images = data.pop("images")
        pin._raw = {"custom": {"images": images}, "scraped": data}

        assert pin.is_valid() == is_valid


@pytest.mark.web
def test_pin_single_image_source(mocker, cookies):
    pin_url = "https://www.pinterest.com/pin/581105158183245043/"
    expected_pin_data = {
        "url": pin_url,
        "title": "Shanks",
        "description": " ",
        "dominant_color": "#fdfdfd",
        "hashtags": [],
        "images": [
            "https://i.pinimg.com/736x/68/92/17/" "689217658bbff324dfba0621ce9449fa.jpg"
        ],
    }
    driver = mocker.Mock(get_cookies=lambda: cookies)

    get_request_manager = GetRequestManager(driver)
    pin_data = pin.PinData(get_request_manager, pin_url)
    fetched_data = pin_data.fetch_data()

    assert fetched_data == expected_pin_data


@pytest.mark.web
def test_pin_multiple_images_source(mocker, cookies):
    pin_url = "https://www.pinterest.com/pin/10485011624488809/"
    expected_pin_data = {
        "url": pin_url,
        "title": "Luffy & Zoro Matching Icon",
        "description": "One Piece",
        "dominant_color": "#6e6e90",
        "hashtags": [],
        "images": [
            "https://i.pinimg.com/736x/ed/02/90/"
            "ed029092be09633a085854675461cbd1.jpg",
            "https://i.pinimg.com/736x/e3/0f/4b/"
            "e30f4b0e9cf0d1d84bdd0fb382238cb9.jpg",
        ],
    }

    driver = mocker.Mock(get_cookies=lambda: cookies)

    get_request_manager = GetRequestManager(driver)
    pin_data = pin.PinData(get_request_manager, pin_url)
    fetched_data = pin_data.fetch_data()

    assert fetched_data == expected_pin_data
