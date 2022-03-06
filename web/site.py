from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


class Element:
    """The elements to locate and URLs in the Pinterest."""

    ELEMENT_LOGIN_BUTTON = 'div.Eqh:nth-child(3) > div:nth-child(1) > button:nth-child(1)'
    ELEMENT_EMAIL_INPUT = '#email'
    ELEMENT_PASSWORD_INPUT = '#password'

    ELEMENT_PINS = 'div.vbI:nth-child(1)'

    ELEMENT_TITLE = 'h1.lH1'
    ELEMENT_SUBTITLE = 'div.FNs:nth-child(2) > span:nth-child(1)'
    ELEMENT_IMAGES = '.OVX > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)'


class Site(Element):
    """Provide ways to get elements using WebDriverWait."""

    URL_SEARCH = 'https://www.pinterest.com/search/pins/?q='
    URL_HOME = 'https://pinterest.com'

    def __init__(self, driver):
        self.web_driver_wait = driver

    @property
    def web_driver_wait(self) -> WebDriverWait:
        """An instance of WebDriverWait."""
        return self._web_driver_wait

    @web_driver_wait.setter
    def web_driver_wait(self, driver):
        self._web_driver_wait = WebDriverWait(driver, 10)

    def web_element(self, element:str, locator: By = By.CSS_SELECTOR,
                    condition: EC = EC.presence_of_element_located):
        """Wrap a WebDriverWait's until method.

        Args:
            element: The element to search for.
            locator: The locator to search for the element.
            condition: The condition to track the element.

        Returns:
            WebElement: return a WebElement instance matching the args.
        """

        return self.web_driver_wait.until(condition((locator, element)))

    def html(self, element:str, *args, **kwargs) -> str:
        """Get the HTML of the `element`."""

        return self.web_element(element, *args, **kwargs
                                ).get_attribute('outerHTML')

    def html_soup(self, element:str, *args, **kwargs) -> BeautifulSoup:
        """Get an BeautifulSoup's object from the `element`, parsed as HTML."""

        return BeautifulSoup(self.html(element, *args, **kwargs), 'html.parser')
