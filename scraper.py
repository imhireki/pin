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

