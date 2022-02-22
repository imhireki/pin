from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


class WebSite:
    """ Deal with elements on the HTML of the website """
    ENDPOINT_SEARCH = 'https://www.pinterest.com/search/pins/?q='
    ENDPOINT_HOME = 'https://br.pinterest.com'

    ELEMENT_LOGIN_BUTTON = 'div.Eqh:nth-child(3) > div:nth-child(1) > button:nth-child(1)'
    ELEMENT_EMAIL_INPUT = '#email'
    ELEMENT_PASSWORD_INPUT = '#password'

    ELEMENT_PINS = 'div.vbI:nth-child(1)'

    ELEMENT_TITLE = 'h1.lH1'
    ELEMENT_SUBTITLE = 'div.FNs:nth-child(2) > span:nth-child(1)'
    ELEMENT_IMAGES = '.OVX > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)'

    def __init__(self, driver):
        self.driver = driver

    def html_soup(self, element:str, **kwargs):
        """ Return an object of BeautifulSoup parsed as HTML """
        return BeautifulSoup(self.html(element, **kwargs), 'html.parser')

    def html(self, element:str, **kwargs):
        """ Return the HTML of the an `element` """
        return self.web_element(element, **kwargs).get_attribute('outerHTML')

    def web_element(self,
             element:str,
             timeout:float=10.0,
             condition:EC=EC.presence_of_element_located,
             locator:By=By.CSS_SELECTOR) -> WebElement:
        """ Return a WebElement (wrapper of WebDriverWait)
        args
        ----
        element -- element to search for
        timeout -- timeout to search for the element (default 10.0)
        condition -- expected condition (default: EC.presence_of_element_located)
        locator -- locator to search the element (deffault: By.CSS_SELECTOR)
        """
        return WebDriverWait(self.driver, timeout).until(
            condition((locator, element))
            )
