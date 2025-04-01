import pytest

from browser import Firefox
from pinterest.webpages import Login


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

    login = Login(browser)
    login.go_to_page()
    login.authenticate()

    session = login.session
    browser.quit()
    return session
