import pytest

from pinterest.webpages import Login, SearchFeed
from pinterest.pin import Pin, PinData
from browser import Firefox


@pytest.mark.web
def test_scraping():
    with Firefox(headless=False) as web_driver:
        login = Login(web_driver)
        login.go_to_page()
        login.close_google_login()
        login.authenticate()

        session = login.session

        search_feed = SearchFeed(web_driver, "Frieren icon")
        search_feed.go_to_page()
        search_feed.load_more()

        pin_ids = search_feed.find_pin_ids()

        assert isinstance(pin_ids, set) and len(pin_ids) > 5

        for pid in pin_ids:

            pin_data = PinData(pid, session)
            pin = Pin(pin_data)

            data = pin.fetch_data()

            if not pin.is_valid():
                continue
            assert data and data["id"]
