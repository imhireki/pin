from typing import Union
import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from web.data_manager import WebElementManager
from data.pin import Pin
import settings


class Pinterest:
    def __init__(self, web_element_manager: WebElementManager) -> None:
        self._web_element_manager: WebElementManager = web_element_manager

    def make_search_url(self, query: str) -> str:
        search_url = settings.URLS['SEARCH_PIN']

        for index, word in enumerate(query.split(' ')):
            if index != 0:
                search_url += f'+{word}'
            else:
                search_url += word
        return search_url

    def perform_login(self) -> None:
        try:
            email_input = self._web_element_manager.get(
                settings.ELEMENTS['EMAIL_INPUT']['element']
                ).send_keys(settings.CREDENTIALS['EMAIL'])

            password_input = self._web_element_manager.get(
                settings.ELEMENTS['PASSWORD_INPUT']['element']
                ).send_keys(settings.CREDENTIALS['PASSWORD'], Keys.ENTER)
        except TimeoutException:
            return

    def find_pins_urls(self) -> list[str]:
        pins_element = self._web_element_manager.get(
            settings.ELEMENTS['PINS']['element'])
        pins_html = self._web_element_manager.get_html(pins_element)
        links_soup = self._web_element_manager.make_html_soup(
            pins_html).find_all('a')

        return list({
            '{}{}'.format(settings.URLS['HOME'], link.get('href'))
            for link in links_soup
            if re.search('^/pin/[0-9]+/$', link.get('href'))
        })

    def fetch_pin_data(self, pin_url: str) -> dict[str, Union[str, list]]:
        pin = Pin(pin_url)

        if not pin.is_valid():
            return {}
        return pin.fetch_data()
