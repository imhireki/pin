from abc import ABC, abstractmethod
from typing import Any
import time
import os

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver import (
    Firefox as FirefoxDriver,
    Chrome as ChromeDriver,
    FirefoxOptions,
    ChromeOptions,
)


class IBrowser[Opts: ArgOptions](ABC):
    _default_options: dict[str, Any] = {"headless": True, "wait_timeout": 10}
    _driver: WebDriver
    _wait: WebDriverWait
    _options: dict[str, Any]

    def setup_driver(self) -> None:
        options = {**self._default_options}
        options.update(**self._options)

        driver_options = self._set_driver_options(options)
        wait_options = self._set_wait_options(options)

        self._driver = self._set_driver(driver_options)
        self._wait = WebDriverWait(self._driver, **wait_options)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    @abstractmethod
    def _set_driver_options(self, options: dict[str, Any]) -> Opts:
        pass

    @staticmethod
    def _set_wait_options(options: dict) -> dict:
        return {"timeout": options["wait_timeout"]}

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

        # Keeps the driver from closing by itself (like firefox)
        driver_options.add_experimental_option("detach", True)

        driver_options.add_argument(f"--user-data-dir={self._driver_data_directory}")
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

        driver_options.profile = self._driver_data_directory
        return driver_options

    def _set_driver(self, driver_options: FirefoxOptions) -> FirefoxDriver:
        return FirefoxDriver(options=driver_options)
