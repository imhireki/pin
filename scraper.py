import time

from data.storage.file import JsonStorage
from web.browser import Firefox
from web.www import Pinterest
import settings


storage = JsonStorage('data.json')

browser = Firefox(binary="geckodriver", headless=False)
browser.setup_driver()

pinterest = Pinterest(browser.driver)

try:
    browser.get(settings.URLS['LOGIN'])
    pinterest.perform_login()
    time.sleep(3)

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
except KeyboardInterrupt:
    pass
except Exception:
    pass
finally:
    browser.close()
