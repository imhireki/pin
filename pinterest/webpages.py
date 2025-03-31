import time
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4._typing import _QueryResults
from bs4 import BeautifulSoup, Tag
from requests import Session

from pinterest.pin import Pin, PinData
from browser import IBrowser
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
        self.browser.wait.until(
            EC.frame_to_be_available_and_switch_to_it(settings.ELEMENTS["GOOGLE_LOGIN"])
        )

        close_button = self.browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"])
        )
        close_button.click()

        self.browser.switch_to_default_content()

    def authenticate_session(self, retries: int, retry_delay: int) -> None:
        for _ in range(retries):
            auth_cookie = self.browser.get_cookie("_auth")

            if auth_cookie and auth_cookie["value"] == "1":
                for cookie in self.browser.get_cookies():
                    self.session.cookies.set(cookie["name"], cookie["value"])
                return
            time.sleep(retry_delay)

        raise Exception("Failed to authenticate Session")

    def perform_login(self) -> None:
        email_field = self.browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["EMAIL_FIELD"])
        )

        email_field.send_keys(settings.CREDENTIALS["EMAIL"])

        password_field = self.browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["PASSWORD_FIELD"])
        )

        password_field.send_keys(settings.CREDENTIALS["PASSWORD"], Keys.ENTER)

        self.authenticate_session(10, 1)

    def _find_a_tags(self) -> list:
        pins_element = self.browser.wait.until(
            EC.visibility_of_element_located(settings.ELEMENTS["PINS"])
        )
        pins_html = pins_element.get_attribute("outerHTML")

        if not pins_html:
            return []

        return BeautifulSoup(pins_html, "html.parser").find_all("a")

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

    def find_pin_ids(self) -> set[str]:
        urls = set()
        for tag in self._find_a_tags():
            try:
                urls.add(self._extract_pin_id(tag))
            except (TypeError, ValueError):
                continue
        return urls

    def fetch_pin_data(self, pin_id: str) -> dict:
        pin_data = PinData(pin_id, self.session)
        pin = Pin(pin_data)

        if not pin.is_valid():
            return {}
        return pin.fetch_data()
