import time

from web.data_manager import WebElementManager
from data.storage.file import CSVStorage, JsonStorage
from web.browser import Chromium, Firefox
from web.www import Pinterest
import settings


if __name__ == '__main__':
    storage = CSVStorage('csv.csv')

    browser = Chromium()
    browser.setup_driver()

    pinterest = Pinterest(WebElementManager(browser.driver))

    # browser.get(settings.URLS['LOGIN'])
    # pinterest.perform_login()
    # time.sleep(3)

    for query in ['Luffy Icon']:
        search_url = pinterest.make_search_url(query)

        browser.get(search_url)
        browser.scroll_to_page_bottom()

        pins_urls = pinterest.find_pins_urls()
        pins_data = [pinterest.fetch_pin_data(pin_url) for pin_url in pins_urls]

        for data in pins_data:
            if storage.query_pin(data['url']):
                continue
            storage.insert_pin(data)

    browser.close()
