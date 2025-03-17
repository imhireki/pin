import json
import time

import pytest

from web.browser import Firefox
from web.www import Pinterest
import settings


base_pin_data = {
    "title": "title",
    "description": "description",
    "dominant_color": "#ffffff",
    "hashtags": ["hashtag"],
}


@pytest.fixture
def pin_data():
    return {
        "url": "https://www.pinterest.com/pin/123/",
        "images": ["img.jpg"],
        **base_pin_data,
    }


@pytest.fixture
def raw_pin_data():
    return {
        **base_pin_data,
        "carousel_data": {},
        "images": {"736x": {"url": "img.jpg"}},
    }


@pytest.fixture(scope="session")
def cookies():
    browser = Firefox(binary="geckodriver", headless=True)
    browser.setup_driver()

    browser.get(settings.URLS["LOGIN"])
    Pinterest(browser.driver).perform_login()
    time.sleep(3)

    cookies = browser.driver.get_cookies()
    browser.quit()
    return cookies


@pytest.fixture
def make_pin_html():
    def _make_pin_html(raw_pin_data):
        pin_id = "123"
        script_data = {"initialReduxState": {"pins": {pin_id: raw_pin_data}}}

        html_script_data_json_string = json.dumps(script_data)

        html_script = f"""
            <script id='__PWS_INITIAL_PROPS__' type='application/json'>
                {html_script_data_json_string}
            </script>
        """
        return html_script

    return _make_pin_html
