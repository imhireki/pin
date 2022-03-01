#!/usr/bin/env python3
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from data.store import storage
from web.driver import Browser
from data.pin import PinData
from web.html import WebSite

from typing import List, Dict, Union
from time import sleep
import re
import os


class Client:
    """Client to manage the website, browser, data and a storage.

    Search each query to get the pins URL, drive the browser through each pin
    storing the pin's data.

    Args:
        query (List[str]): A query to get the pins URLs from.
        storage (Union[JsonFile, Postgres, MySQL]): The way to query and insert
            the pins.
        scrolls (int): The amount of times the driver will perform a scroll on
            each query URL. Default to 0.
        browser (Dict[str, Union[str, bool]): The options for the driver:
            headless, browser and binary. Default to {}.

    Attributes:
        browser (Browser): A browser to be controlled by the driver.
        site (WebSite): The link to elements related to the pinterest.
        driver (WebDriver): The driver of the browser.
        scrolls (int): The amount of times the driver will perform a scroll on
            each query URL.
        storage (Union[JsonFile, Postgres, MySQL]): The way to query and insert
            the pins.
    """

    def __init__(self, query, storage, scrolls=0, browser={}):
        self.browser = Browser(**browser)
        self.site = WebSite(self.browser.driver)
        self.driver = self.browser.driver
        self.scrolls = scrolls
        self.storage = storage
        self.query_urls = query

    @property
    def pin_data(self) -> Dict[str, Union[str, list]]:
        """The data of the current driver's pin URL"""

        return PinData(self.site).data

    @property
    def query_urls(self) -> list:
        """A List with all URLs to get the pins's data from.

        Get the list's items using the `query`.

        Args:
            query: A query to get the pins URLs from.
        """

        return self._query_urls

    @query_urls.setter
    def query_urls(self, query:List[str]):
        urls = []
        for q in query:
            url = self.site.ENDPOINT_SEARCH

            for c, word in enumerate(q.split(' ')):
                if c != 0:
                    url += f'+{word}'  # ?q=word+word...
                else:
                    url += word  # ?q=word.

            urls.append(url)
        self._query_urls = urls

    def login(self):
        """Perform login.

        Use `PINTEREST_EMAIL` and `PINTEREST_PASSWORD` environment keys
        to proceed with an authenticated session.
        """

        # Click to drive to the login form.
        try:
            login_button = self.site.web_element(
                element=self.site.ELEMENT_LOGIN_BUTTON,
                condition=EC.element_to_be_clickable,
                timeout=7.0,
            ).click()
        except TimeoutException:  # Return when the user is already logged in.
            return

        # Get the elements of the fields.
        email_input = self.site.web_element(self.site.ELEMENT_EMAIL_INPUT)
        password_input = self.site.web_element(self.site.ELEMENT_PASSWORD_INPUT)

        # Send the environment keys's for its fields.
        email_input.send_keys(os.getenv('PINTEREST_EMAIL'))
        password_input.send_keys(os.getenv('PINTEREST_PASSWORD'), Keys.ENTER)

        # Free the Firefox driver from the login form (redirect problem).
        if isinstance(self.driver, FirefoxDriver):
            sleep(2)
            self.driver.refresh()

        sleep(3)

    def _pins(self) -> List[str]:
        """Get the pins for the current driver's URL.

        Returns:
            List[str]: The found valid pins.
        """

        # Get the <a> HTML's tags.
        links_soup = self.site.html_soup(self.site.ELEMENT_PINS).find_all('a')

        # Search <a> tags's href for regex matches.
        found_pins = list(set([
            '{}{}'.format(self.site.ENDPOINT_HOME, link.get('href'))
            for link in links_soup
            if re.search('^/pin/[0-9]+/$', link.get('href'))
        ]))

        inserted_pins = self.storage.query_urls(found_pins)  # Repeated pins.
        return [pin for pin in found_pins if pin not in inserted_pins]

    def pins(self) -> Dict[str, list]:
        """Drive the browser through each `self.query_urls` getting its data.

        Returns:
            Dict[str, list]: The query's URL as key and its pins as values.
        """

        pins = {}  # type: Dict[str, list].
        for url in self.query_urls:

            self.driver.get(url)  # Drive the browser to a query URL

            # Perform login in the first URL.
            if url == self.query_urls[0]:
                self.login()

            self.browser.scroll(self.scrolls)  # Scroll `self.scrolls` times

            pins[url] = self._pins()
        return pins

    def pin(self, pins:Dict[str, list]):
        """Drive the browser through each pin, storing the pin's data.

        Args:
            pins: The query's URL as key and its pins as values.
        """

        for query_url in pins.keys():
            for pin in pins.get(query_url):

                self.driver.get(pin)

                pin_data = self.pin_data

                if pin_data:
                    self.storage.insert_pin(dict(url=pin, **pin_data))
