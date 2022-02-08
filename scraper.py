#!/usr/bin/env python3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

# Typing Hint
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List

from time import sleep
from os import getenv


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
    ENDPOINT_SEARCH = 'https://www.pinterest.com/search/pins/?q='

    ELEMENT_LOGIN_BUTTON = 'div.Eqh:nth-child(3) > div:nth-child(1) > button:nth-child(1)'
    ELEMENT_EMAIL_INPUT = '#email'
    ELEMENT_PASSWORD_INPUT = '#password'

    """ Get elements on the HTML of the website """
    def __init__(self, driver):
        self.driver = driver

    def get_element(self,
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

