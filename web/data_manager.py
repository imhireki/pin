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

