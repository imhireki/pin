#!/usr/bin/env python3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Union

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from time import sleep
from os import getenv
import json
import os
import re


class Browser:
    """ Setup driver and perform actions on it """
    def __init__(self):
        self.driver = self._driver()

    @staticmethod
    def _driver() -> ChromiumDriver:
        """ Return a configured ChromiumDriver """
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('user-data-dir=.selenium')
        driver_options.headless = False
        return webdriver.Chrome(options=driver_options)


    def scroll(self, times:int=1, timeout:float=10.0):
        """ Scroll to the bottom of the site iterating over `times`

        Args:
            times: how much the driver is gonna scroll to the bottom
                of the page.
            timeout: time between the each scroll
        """
        for time in range(times):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            sleep(timeout)


class WebSite:
    """ Deal with elements on the HTML of the website """
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


class PinData:
    """ Deal with the data inside a pin """

    def __init__(self, site):
        self.site = site
        self.data = self._data()

    def _data(self) -> Dict[str, Union[str, list]]:
        return {'title': self.title(),
                'subtitle': self.subtitle(),
                'images': self.images()}

    def ignore_error(default=''):
        """ It avoids any exception, setting a default value if it happens """
        def _decorator(func):
            def wrapper_data(self):
                try:
                    return func(self)
                except Exception:
                    return default
            return wrapper_data
        return _decorator

    @ignore_error()
    def title(self) -> str:
        """ Return pin's title """
        return self.site.html_soup(self.site.ELEMENT_TITLE).h1.string

    @ignore_error()
    def subtitle(self) -> str:
        """ Return pin's subtitle"""
        return self.site.html_soup(self.site.ELEMENT_SUBTITLE).span.string

    @ignore_error([])
    def images(self) -> Union[List[str], list]:
        """ Return pin's images """
        img_soup = self.site.html_soup(self.site.ELEMENT_IMAGES)

        if img_soup.find('img'):
            return [img_soup.find('img').get('src')]  # src img

        urls = []  # style with multiples imgs
        for div in img_soup.find_all('div'):
            url = re.search(
                "(http.?://i.pinimg.com/[0-9]{3}x/../../../[a-z0-9]+\.(?:png|jpg|jpeg))",
                div.get('style', '')
            )
            if not url:
                continue

            urls.append(url.group())
        return urls

    def is_valid(self):
        """ Return whether the data is valid """
        pass

    def patch_data(self):
        """ Return the patched data or None """
        pass


class JsonFile:
    """ Deal with the storage using a Json file """

    def __init__(self, filename:str):
        self.filename = filename

    def insert(self, data:Dict[str, Union[str, list]]):
        """ Append the data to `self.filename` """

        json_data = self.select()
        json_data.update(data)

        json_file = open(self.filename, 'w')
        json.dump(obj=json_data, fp=json_file, indent=4)
        json_file.close()

    def select(self) -> Dict[str, Union[str, list]]:
        """ Return all the data from the `self.filename` file """

        if not os.path.exists(self.filename):
            return {}  # the file is created just on insert()

        json_file = open(self.filename, 'r')
        json_data = json.load(json_file)
        json_file.close()
        return json_data


class SQL(ABC):
    @abstractmehod
    def __init__(self, connection:Dict[str, str]):
        pass

    def insert(self, data:Dict[str, list]):
        """Insert the data inside db's tables

        Args:
            data: dictionary with url:str, title:str, subtitle:str, images:list
        """

        # inserting url title e subtitle
        self.cursor.execute(
            """
            INSERT INTO
                pins (url, title, subtitle)
            VALUES
                (%s, %s, %s)
            ;
            """,
            (data['url'], data['title'], data['subtitle'])
        )
        self.connection.commit()  # maybe just one commit

        # query the id from the last insertion
        self.cursor.execute(
            """
            SELECT
                pin.id
            FROM
                pins as pin
            WHERE
                pin.url = %s
            ;
            """,
            [data['url']]
        )
        rows = self.cursor.fetchall()
        pin_id = [col[0] for col in rows][0]

        for image in data['images']:
            # insert the image  FIXME: pins_id to pin_id or pin
            self.cursor.execute(
                """
                INSERT INTO
                    images (pins_id, url)
                VALUES
                    (%s, %s)
                ;
                """,
                (pin_id, image)
            )
            self.connection.commit()  # maybe just one commit

    def select(self, urls:List[str]):
        """Select urls matching `urls` sent in the list.

        Args:
            urls: list of urls used for check the url field in the db.
        Returns:
            list: List[str] if any matches, List[] otherwise.
        """
        self.cursor.execute(
            """
            SELECT
                pin.url
            FROM
                pins as pin
            WHERE
                pin.url in ({})
            ;
            """.format(('%s, ' * len(urls))[:-2]),  # %s for each url
            urls
        )
        rows = self.cursor.fetchall()
        return [col[0] for col in rows]


class Postgres(SQL):
    def __init__(self, connection:Dict[str, str]):
        self.connection = psycopg.connect(**connection)
        self.cursor = self.connection.cursor()


class Storage:
    @staticmethod
    def postgres(connection):
        return Postgres(connection)

    @staticmethod
    def json(filename):
        return JsonFile(filename)


class Client:
    """ Wrapper to perform actions on the WebSite, using Browser and its driver """

    def __init__(self, queries:List[str], storage:Storage, scrolls:int=0):
        self.browser = Browser()
        self.driver = self.browser.driver
        self.scrolls = scrolls
        self.site = WebSite(self.browser.driver)
        self.storage = storage
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
        email_input.send_keys(getenv('PINTEREST_EMAIL'))
        password_input.send_keys(getenv('PINTEREST_PASSWORD'), Keys.ENTER)

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

        inserted_pins = self.storage.select().keys()
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

                pin_data = {pin: PinData(self.site).data}
                self.storage.insert(pin_data)


if __name__ == '__main__':
    json_storage = Storage.json('myjsonfile.json')

    client = Client(
        queries=['anime matching icons'],
        storage=json_storage
    )
    try:
        pins = client.pins()
        if pins:
            client.pin(pins)

    except Exception as e:
        raise e
    except KeyboardInterrupt:
        pass
    finally:
        client.driver.quit()
