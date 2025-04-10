import pytest

from pinterest.webpages import Login, SearchFeed
from pinterest.pin import Pin, PinData
from browser import Firefox


@pytest.mark.web
def test_scraping():
    browser = Firefox(headless=True)
    browser.setup_driver()

    try:
        login = Login(browser)
        login.go_to_page()
        login.authenticate()

        session = login.session

        search_feed = SearchFeed(browser, "Frieren icon")
        search_feed.go_to_page()
        search_feed.load_more()

        pin_ids = search_feed.find_pin_ids()

        assert isinstance(pin_ids, set) and len(pin_ids) > 5

        for pid in pin_ids:

            pin_data = PinData(pid, session)
            pin = Pin(pin_data)

            data = pin.fetch_data()

            if not pin.is_valid():
                return
            assert data and data["id"]

    except Exception as e:
        print(e)
        assert 0
    finally:
        browser.quit()
