from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver

from typing import List, Dict, Union
from time import sleep
import os


class Browser:
    """ Setup driver and perform actions on it """

    defaults = {
        'browser': 'Firefox',
        'headless': False,
        'binary': None
    }

    def __init__(self, **kwargs):
        self.defaults.update(kwargs) if kwargs else self.defaults
        self.driver = self.defaults

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, opt:Dict[str, Union[str, bool]]):
        if opt['browser'] == 'Firefox':
            self._driver = self.firefox(opt)
        elif opt['browser'] == 'Chrome':
            self._driver = self.chrome(opt)

    def _options(self, options, opt):
        if opt['binary']:
            options.binary_location = opt['binary']
        options.headless = opt['headless']
        return options

    def firefox(self, opt):
        opt['data'] = '.firefox'
        if not os.path.exists(opt['data']):
            os.mkdir(opt['data'])

        profile = webdriver.FirefoxProfile(opt['data'])
        return webdriver.Firefox(profile, options=self._options(
            webdriver.FirefoxOptions(), opt))

    def chrome(self, opt):
        opt['data'] = '.chrome'
        options = self._options(webdriver.ChromeOptions(), opt)
        options.add_argument('user-data-dir={}'.format(opt['data']))
        return webdriver.Chrome(options=options)

    def scroll(self, times:int=1):
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
            sleep(3)
