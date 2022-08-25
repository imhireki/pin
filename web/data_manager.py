from abc import ABC, abstractmethod
import requests

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from web import browser


class IWebDataManager(ABC):
    @abstractmethod
    def get(self): pass

    @abstractmethod
    def get_html(self) -> str: pass

    def make_html_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')


class WebElementManager(IWebDataManager):
    def __init__(self, web_driver: browser.WebDriver) -> None:
        self._web_driver_wait: WebDriverWait = WebDriverWait(web_driver, 10)

    def get(self, element: str, locator: By = By.CSS_SELECTOR,
            condition: EC = EC.presence_of_element_located) -> WebElement:
        return self._web_driver_wait.until(condition(locator, element))

    def get_html(self, web_element: WebElement) -> str:
        return web_element.get_attribute('outerHTML')


