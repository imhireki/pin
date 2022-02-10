#!/usr/bin/env python3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Union

from bs4 import BeautifulSoup
from time import sleep
from os import getenv
import re


class Browser:
    """ Setup driver and perform actions on it """
    def __init__(self):
        self.driver = self._driver()

    @staticmethod
    def _driver() -> ChromiumDriver:
        """ Return a configured ChromiumDriver"""
        driver_options = webdriver.ChromeOptions()
        driver_options.headless = False
        return webdriver.Chrome(options=driver_options)


    def scroll(self, times:int=1, timeout:float=10.0):
        """ Scroll to the bottom of the site iterating over `times`
        args
        ----
        times -- number of times driver is gonna scroll (default 1)
        timeout -- timeout between scrolls (default 10.0)
        """
        for time in range(times):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            sleep(timeout)


class WebSite:
    """ Handle elements on the HTML of the website """
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


class Client:
    """ Wrapper to perform actions on the WebSite, using Browser and its driver """

    def __init__(self, queries:List[str], scrolls:int):
        self.browser = Browser()
        self.driver = self.browser.driver
        self.site = WebSite(self.browser.driver)
        self.query_urls = self._query_urls(queries)

    def _query_urls(self, queries:List[str]) -> List[str]:
        """ Return a list of urls using the content inside `queries` """
        query_urls = []
        for query in queries:
            words = query.split(' ')  # type: List[str]
            url = self.site.ENDPOINT_SEARCH

            # ?q=word+word...
            for c, word in enumerate(words):
                if c != 0:
                    url += f'+{word}'  # ?q=word+word...
                else:
                    url += word  # ?q=word
            query_urls.append(url)

        return query_urls

    def login(self, timeout:float=10.0):
        """ Perform login using enviroment keys """

        # Go to the login form
        login_button = self.site.web_element(
            element=self.site.ELEMENT_LOGIN_BUTTON,
            condition=EC.element_to_be_clickable,
            ).click()

        # Get the fields elements
        email_input = self.site.web_element(self.site.ELEMENT_EMAIL_INPUT)
        password_input = self.site.web_element(self.site.ELEMENT_PASSWORD_INPUT)

        # Send the enviroment keys's credentials for its fields
        email_input.send_keys(getenv('PINTEREST_EMAIL'))
        password_input.send_keys(getenv('PINTEREST_PASSWORD'), Keys.ENTER)

        sleep(timeout)

    def lookup_urls(self):
        """ Go to each search url, perform login and scroll over them """

        for url in self.search_urls:
            self.driver.get(url)

            if url == self.search_urls[0]:
                self.login()

            self.browser.scroll(2)


if __name__ == '__main__':
    client = None

    try:
        client = Client(
            queries=['Kusanagi Motoko', 'anime icons'],
            scrolls=1
        )
        client.lookup_urls()

    except Exception as e:
        raise e
    except KeyboardInterrupt:
        pass
    finally:
        client.driver.quit()
