from abc import ABC, abstractmethod
from typing import Any, Union
import time
import os

from selenium import webdriver


WebDriver = Union[webdriver.Chrome, webdriver.Firefox]
WebDriverOptions = Union[webdriver.ChromeOptions, webdriver.FirefoxOptions]


class IBrowser(ABC):
    _default_options: dict[str, Any] = {"binary": None, "headless": True}
    _driver: WebDriver
    _options: dict[str, Any]

    def setup_driver(self) -> None:
        setup_driver_options = {**self._default_options}
        setup_driver_options.update(**self._options)

        driver_options = self._set_driver_options(setup_driver_options)
        self._driver = self._set_driver(driver_options)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @abstractmethod
    def _set_driver_options(self, options: dict[str, Any]) -> WebDriverOptions:
        pass

    @abstractmethod
    def _set_driver(self, driver_options: WebDriverOptions) -> WebDriver:
        pass

    def scroll_to_page_bottom(self, times=1, timeout=3) -> None:
        for _ in range(times):
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(timeout)

    def get(self, url: str) -> None:
        self._driver.get(url)

    def refresh(self) -> None:
        self._driver.refresh()

    def close(self) -> None:
        self._driver.close()


class Chromium(IBrowser):
    _driver_data_directory: str = "/tmp/pin/driver_data/chrome"

    def __init__(self, **options: Any) -> None:
        self._options: dict[str, Any] = options

    def _set_driver_options(self, options: dict[str, Any]) -> webdriver.ChromeOptions:
        driver_options = webdriver.ChromeOptions()
        driver_options.headless = options["headless"]

        if "binary" in options:
            driver_options.binary_location = options["binary"]

        driver_options.add_argument(f"user-data-dir={self._driver_data_directory}")
        return driver_options

    def _set_driver(self, driver_options: webdriver.ChromeOptions) -> webdriver.Chrome:
        return webdriver.Chrome(options=driver_options)


class Firefox(IBrowser):
    _driver_data_directory: str = "/tmp/pin/driver_data/firefox"

    def __init__(self, **options: Any) -> None:
        self._options: dict[str, Any] = options

    def _set_driver_options(self, options: dict[str, Any]) -> webdriver.FirefoxOptions:
        driver_options = webdriver.FirefoxOptions()
        driver_options.headless = options["headless"]

        if "binary" in options:
            driver_options.binary_location = options["binary"]

        if not os.path.exists(self._driver_data_directory):
            os.makedirs(self._driver_data_directory)
        driver_options.set_preference("profile", self._driver_data_directory)
        return driver_options

    def _set_driver(
        self, driver_options: webdriver.FirefoxOptions
    ) -> webdriver.Firefox:
        return webdriver.Firefox(options=driver_options)
