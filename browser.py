import time

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import (
    Firefox as FirefoxDriver,
    Chrome as ChromeDriver,
    FirefoxOptions,
    ChromeOptions,
)


def Firefox(headless=True) -> FirefoxDriver:
    options = FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    return FirefoxDriver(options)


def Chrome(headless=True) -> ChromeDriver:
    options = ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # Keeps the driver from closing by itself (like firefox)
    options.add_experimental_option("detach", True)
    return ChromeDriver(options)


def scroll_down(web_driver: WebDriver, loading_delay=3) -> None:
    web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(loading_delay)
