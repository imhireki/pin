from abc import ABC, abstractmethod
from typing import Any, Union
import time
import os

from selenium import webdriver


WebDriver = Union[webdriver.Chrome, webdriver.Firefox]
WebDriverOptions = Union[webdriver.ChromeOptions, webdriver.FirefoxOptions]
WebDriverProfile = Union[webdriver.FirefoxProfile]


class IBrowser(ABC):
    _default_options = {"binary": None, "headless": True}
    _driver: WebDriver

    def setup_driver(self) -> None:
        setup_driver_options = dict(**self._default_options)
        setup_driver_options.update(**self._options)

        driver_options = self._set_driver_options(setup_driver_options)
        self._driver = self._set_driver(driver_options)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @abstractmethod
    def _set_driver_options(self) -> WebDriverOptions: pass

    @abstractmethod
    def _set_driver(self) -> WebDriver: pass

    def scroll_to_page_bottom(self, times=1, timeout=3):
        for _ in range(times):
            self._driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            time.sleep(timeout)

    def get(self, url: str) -> None:
        self._driver.get(url)

    def refresh(self) -> None:
        self._driver.refresh()

    def close(self) -> None:
        self._driver.close()

