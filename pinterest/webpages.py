from abc import ABC, abstractmethod
import time
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4._typing import _QueryResults
from bs4 import BeautifulSoup, Tag
from requests import Session

from browser import IBrowser
import settings


class WebPage(ABC):
    def __init__(self, browser: IBrowser) -> None:
        self._browser = browser

    def go_to_page(self) -> None:
        self._browser.get(self.url)

    @property
    @abstractmethod
    def url(self) -> str:
        pass


class Login(WebPage):
    def __init__(self, browser: IBrowser):
        self.session = Session()
        super().__init__(browser)

    @property
    def url(self) -> str:
        return settings.URLS["LOGIN"]

    def close_google_login(self) -> None:
        self._browser.wait.until(
            EC.frame_to_be_available_and_switch_to_it(settings.ELEMENTS["GOOGLE_LOGIN"])
        )

        close_button = self._browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"])
        )
        close_button.click()

        self._browser.switch_to_default_content()

    def authenticate_session(self, retries: int, retry_delay: int) -> None:
        for _ in range(retries):
            auth_cookie = self._browser.get_cookie("_auth")
            if auth_cookie and auth_cookie["value"] == "1":
                for cookie in self._browser.get_cookies():
                    self.session.cookies.set(cookie["name"], cookie["value"])
                return
            time.sleep(retry_delay)

        raise Exception("Failed to authenticate Session")

    def authenticate(self) -> None:
        email_field = self._browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["EMAIL_FIELD"])
        )

        email_field.send_keys(settings.CREDENTIALS["EMAIL"])

        password_field = self._browser.wait.until(
            EC.element_to_be_clickable(settings.ELEMENTS["PASSWORD_FIELD"])
        )

        password_field.send_keys(settings.CREDENTIALS["PASSWORD"], Keys.ENTER)

        self.authenticate_session(10, 1)


class SearchFeed(WebPage):
    def __init__(self, browser: IBrowser, query: str) -> None:
        self._url = self._make_search_url(query)
        super().__init__(browser)

    @property
    def url(self) -> str:
        return self._url

    @staticmethod
    def _make_search_url(query: str) -> str:
        return settings.URLS["SEARCH_PIN"] + "+".join(query.split())

    def load_more(self) -> None:
        self._browser.scroll_down(2, 3)

    def find_pin_ids(self) -> set[str]:
        urls = set()
        for tag in self._find_a_tags():
            try:
                urls.add(self._extract_pin_id(tag))
            except (TypeError, ValueError):
                continue
        return urls

    def _find_a_tags(self) -> list:
        pins_element = self._browser.wait.until(
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
