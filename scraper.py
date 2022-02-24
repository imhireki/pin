#!/usr/bin/env python3
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Dict, Union

from data.store.storage import Storage
from data.pin import PinData
from web.driver import Browser
from web.html import WebSite

import re
import os
from time import sleep


class Client:
    """ Wrapper to perform actions on the WebSite, using Browser and its driver """

    def __init__(self, queries:List[str], storage:Storage, scrolls:int=0):
        self.browser = Browser()
        self.driver = self.browser.driver
        self.scrolls = scrolls
        self.site = WebSite(self.browser.driver)
        self.storage = storage
        self.query_urls = queries

    @property
    def query_urls(self):
        return self._query_urls

    @query_urls.setter
    def query_urls(self, queries:List[str]):
        urls = []
        for query in queries:
            words = query.split(' ')  # type: List[str]
            url = self.site.ENDPOINT_SEARCH

            # ?q=word+word...
            for c, word in enumerate(words):
                if c != 0:
                    url += f'+{word}'  # ?q=word+word...
                else:
                    url += word  # ?q=word
            urls.append(url)
        self._query_urls = urls

    def login(self, timeout:float=10.0):
        """ Perform login using enviroment keys """

        # Go to the login form
        try:
            login_button = self.site.web_element(
                element=self.site.ELEMENT_LOGIN_BUTTON,
                condition=EC.element_to_be_clickable,
                timeout=5.0,
            ).click()
        except TimeoutException:  # User already logged in
            return

        # Get the fields elements
        email_input = self.site.web_element(self.site.ELEMENT_EMAIL_INPUT)
        password_input = self.site.web_element(self.site.ELEMENT_PASSWORD_INPUT)

        # Send the enviroment keys's credentials for its fields
        email_input.send_keys(os.getenv('PINTEREST_EMAIL'))
        password_input.send_keys(os.getenv('PINTEREST_PASSWORD'), Keys.ENTER)

        sleep(timeout)

    def _pins(self) -> List[str]:
        """ Return pins from the current driver's page """

        # links(<a>) in ELEMENT_PINS
        links_soup = self.site.html_soup(self.site.ELEMENT_PINS).find_all('a')

        found_pins = list(set([
            '{}{}'.format(self.site.ENDPOINT_HOME, link.get('href'))
            for link in links_soup
            if re.search('^/pin/[0-9]+/$', link.get('href'))  # /pin/id/
        ]))

        # inserted_pins = self.storage.select().keys()
        inserted_pins = self.storage.query_urls(found_pins)

        return [pin for pin in found_pins if pin not in inserted_pins]

    def pins(self) -> Dict[str, list]:
        """ Go to each search url, perform login, scroll, and return its pins """

        pins = {}  # type: Dict[str, list]

        # Loop thru the queries
        for url in self.query_urls:
            self.driver.get(url)

            if url == self.query_urls[0]:  # Login on the first url
                self.login()

            self.browser.scroll(self.scrolls)

            # self.used_pins = ... NOTE: requires db data
            pins[url] = self._pins()

        return pins

    def pin(self, pins:Dict[str, list]):
        """ Loop thru the pins, getting its data """

        for query_url in pins.keys():  #  url which the pins where found at
            for pin in pins.get(query_url):
                self.driver.get(pin)

                pin_data = PinData(self.site).data

                # pin_data = {pin: pin_data}
                # self.storage.insert(pin_data)

                self.storage.insert_pin({
                    'url': pin,
                    'title': pin_data['title'],
                    'subtitle': pin_data['subtitle'],
                    'images': pin_data['images']
                })

