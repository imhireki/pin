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
def pinterest_session():
    browser = Firefox(binary="geckodriver", headless=True)
    browser.setup_driver()

    pinterest = Pinterest(browser)
    browser.get(settings.URLS["LOGIN"])
    pinterest.close_google_login()
    pinterest.perform_login()

    session = pinterest.session
    browser.quit()
    return session
