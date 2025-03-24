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

    assert fetched_data == expected_fetched_data


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


class TestPin:
    def test_get_pin_data(self, mocker):
        pin_data_mock = mocker.patch("data.pin.PinData")
        web_driver_mock = mocker.Mock()
        pin_url = "url"

        pin_object = pin.Pin(web_driver_mock, pin_url)
        pin_data_object = pin_object.get_pin_data()

        assert pin_data_mock.call_args.args == (web_driver_mock, pin_url)
        assert pin_data_object is pin_data_mock.return_value
        assert pin_object._pin_data is pin_data_mock.return_value

    def test_fetch_data(self, mocker):
        expected_data = {"x": 1, "y": 2}
        mocker.patch(
            "data.pin.PinData",
            return_value=mocker.Mock(fetch_data=lambda: expected_data),
        )

        pin_object = pin.Pin(mocker.Mock(), "url")
        fetched_data = pin_object.fetch_data()

        assert fetched_data == expected_data
        assert pin_object._fetched_data == expected_data

    @pytest.mark.parametrize(
        "fetched_data, validity",
        [({"images": ["img.jpg"]}, True), ({"images": []}, False)],
    )
    def test_is_valid(self, mocker, fetched_data, validity):
        pin_object = pin.Pin(mocker.Mock(), "url")
        pin_object._fetched_data = fetched_data
        mocker.patch.object(pin_object, "fetch_data", return_value=fetched_data)

        pin_is_valid = pin_object.is_valid()

        assert pin_is_valid is validity
