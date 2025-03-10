from abc import ABC, abstractmethod

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests

from web import browser


class IWebDataManager(ABC):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def get_html(self) -> str:
        pass

    def make_html_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")


class WebElementManager(IWebDataManager):
    def __init__(self, web_driver: browser.WebDriver) -> None:
        self._web_driver_wait: WebDriverWait = WebDriverWait(web_driver, 10)

    def get(
        self,
        element: str,
        locator: str = By.CSS_SELECTOR,
        condition=EC.presence_of_element_located,
    ) -> WebElement:
        return self._web_driver_wait.until(condition((locator, element)))

    def get_html(self, web_element: WebElement) -> str | None:
        return web_element.get_attribute("outerHTML")


class GetRequestManager(IWebDataManager):
    def __init__(self, web_driver: browser.WebDriver) -> None:
        self.web_driver = web_driver

    def _get_updated_session(self) -> requests.Session:
        browser_cookies = self.web_driver.get_cookies()
        session = requests.Session()
        for cookie in browser_cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        return session

    def get(self, url: str) -> requests.Response:
        updated_session = self._get_updated_session()
        return updated_session.get(url)

    def get_html(self, response: requests.Response) -> str:
        return response.text
