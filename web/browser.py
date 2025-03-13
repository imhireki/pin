from abc import ABC, abstractmethod
from typing import Any
import time
import os

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver import (
    Firefox as FirefoxDriver,
    Chrome as ChromeDriver,
    FirefoxOptions,
    ChromeOptions,
)


class IBrowser[Opts: ArgOptions](ABC):
    _default_options: dict[str, Any] = {"headless": True}
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
    def _set_driver_options(self, options: dict[str, Any]) -> Opts:
        pass

    @abstractmethod
    def _set_driver(self, driver_options: Opts) -> WebDriver:
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

    def quit(self) -> None:
        self._driver.quit()


class Chromium(IBrowser):
    _driver_data_directory: str = "/tmp/pin/driver_data/chrome"

    def __init__(self, **options: Any) -> None:
        self._options: dict[str, Any] = options

    def _set_driver_options(self, options: dict[str, Any]) -> ChromeOptions:
        driver_options = ChromeOptions()

        if options["headless"]:
            driver_options.add_argument("--headless=new")

        driver_options.add_argument(f"user-data-dir={self._driver_data_directory}")
        return driver_options

    def _set_driver(self, driver_options: ChromeOptions) -> ChromeDriver:
        return ChromeDriver(options=driver_options)


class Firefox(IBrowser):
    _driver_data_directory: str = "/tmp/pin/driver_data/firefox"

    def __init__(self, **options: Any) -> None:
        self._options: dict[str, Any] = options

    def _set_driver_options(self, options: dict[str, Any]) -> FirefoxOptions:
        driver_options = FirefoxOptions()

        if options["headless"]:
            driver_options.add_argument("-headless")

        if not os.path.exists(self._driver_data_directory):
            os.makedirs(self._driver_data_directory)
        driver_options.set_preference("profile", self._driver_data_directory)
        return driver_options

    def _set_driver(self, driver_options: FirefoxOptions) -> FirefoxDriver:
        return FirefoxDriver(options=driver_options)
