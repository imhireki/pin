from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver

from typing import List, Dict, Union
from time import sleep
import os


class Browser:
    """Setup the driver and perform actions on it.

    Attributes:
        defaults Dict[str, Union[str, bool]]: The default options to configure
            the webdriver.
    """

    defaults = {
        'browser': 'Firefox',
        'headless': False,
        'binary': None
    }

    def __init__(self, **kwargs):
        """Update the driver's default options with the kwargs."""

        self.defaults.update(kwargs) if kwargs else self.defaults
        self.driver = self.defaults

    @property
    def driver(self):
        """The browser's driver.

        Args:
            opt: The Options to configure the browser and the driver.
        """

        return self._driver

    @driver.setter
    def driver(self, opt:Dict[str, Union[str, bool]]):
        if opt['browser'] == 'Firefox':
            self._driver = self.firefox(opt)
        elif opt['browser'] == 'Chrome':
            self._driver = self.chrome(opt)

    def _options(self, options, opt):
        """Add the base options: binary and headless."""

        if opt['binary']:
            options.binary_location = opt['binary']
        options.headless = opt['headless']
        return options

    def firefox(self, opt):
        """Setup the Firefox webdriver."""

        opt['data'] = '.firefox'
        if not os.path.exists(opt['data']):
            os.mkdir(opt['data'])

        profile = webdriver.FirefoxProfile(opt['data'])
        return webdriver.Firefox(profile, options=self._options(
            webdriver.FirefoxOptions(), opt))

    def chrome(self, opt):
        """Setup the Chrome webdriver."""

        opt['data'] = '.chrome'
        options = self._options(webdriver.ChromeOptions(), opt)
        options.add_argument('user-data-dir={}'.format(opt['data']))
        return webdriver.Chrome(options=options)

    def scroll(self, times:int=1):
        """Scroll to the bottom of the page, iterating over the amount of times.

        Args:
            times: The amount of times the driver is gonna scroll to the bottom
                of the page.
        """

        for time in range(times):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            sleep(3)
