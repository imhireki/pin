from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver

from typing import List, Dict, Union

class Browser:
    """ Setup driver and perform actions on it """
    def __init__(self, headless=False, user_data='.selenium'):
        self.driver = {'headless': headless,
                       'user_data': user_data}

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, options:Dict[str, Union[str, bool]]):
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument(f'user-data-dir={options["user_data"]}')
        driver_options.headless = options['headless']
        self._driver = webdriver.Chrome(options=driver_options)

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
