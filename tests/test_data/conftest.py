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
