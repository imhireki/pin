import time
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4._typing import _QueryResults
from bs4 import BeautifulSoup, Tag
from requests import Session

from data.pin import Pin, PinData
from web.browser import IBrowser
import settings


class Pinterest:
    def __init__(self, browser: IBrowser) -> None:
        self.browser = browser
        self.session = Session()

    @staticmethod
    def make_search_url(query: str) -> str:
        search_url = settings.URLS["SEARCH_PIN"]

        for index, word in enumerate(query.split(" ")):
            search_url += word if index == 0 else "+" + word
        return search_url

    def close_google_login(self) -> None:
        iframe = self._web_element_manager.get(
            settings.ELEMENTS["GOOGLE_LOGIN"]["element"]
        )
        self._driver.switch_to.frame(iframe)

        close_button = self._web_element_manager.get(
            settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"]["element"],
            settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"]["locator"],
        )
        close_button.click()

        self._driver.switch_to.default_content()

    def perform_login(self) -> None:
        try:
            email_input = self._web_element_manager.get(
                settings.ELEMENTS["EMAIL_INPUT"]["element"]
            ).send_keys(settings.CREDENTIALS["EMAIL"])

            password_input = self._web_element_manager.get(
                settings.ELEMENTS["PASSWORD_INPUT"]["element"]
            ).send_keys(settings.CREDENTIALS["PASSWORD"], Keys.ENTER)
        except TimeoutException:
            return

    def _find_a_tags(self) -> list:
        pins_element = self._web_element_manager.get(**settings.ELEMENTS["PINS"])
        pins_html = self._web_element_manager.get_html(pins_element)

        if not pins_html:
            return []

        return make_html_soup(pins_html).find_all("a")

    @staticmethod
    def _extract_pin_id(tag: _QueryResults) -> str:
        if not isinstance(tag, Tag):
            raise TypeError(
                f"Expected an instance of Tag, but got {tag} {type(tag).__name__}"
            )

        href = tag.get("href")

        pin_id_match = re.search(r"/pin/(\d+)/$", str(href))

        if not pin_id_match:
            raise ValueError(
                "Invalid href: Expected a string matching '/pin/[0-9]+/$', "
                f"but got {href} ({type(href).__name__})"
            )

        return pin_id_match.group(1)

    def find_pin_ids(self) -> list[str]:
        urls = []
        for tag in self._find_a_tags():
            try:
                urls.append(self._extract_pin_id(tag))
            except (TypeError, ValueError):
                continue
        return urls

    def fetch_pin_data(self, pin_url: str) -> dict[str, Any]:
        pin = Pin(self._get_request_manager, pin_url)

        if not pin.is_valid():
            return {}
        return pin.fetch_data()
