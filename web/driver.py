from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver


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
