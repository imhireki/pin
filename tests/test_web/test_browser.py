import pytest

from web import browser


class TestChromium:
    @pytest.mark.web_driver
    def test_driver(self):
        chromium = browser.Chromium(headless=False)
        chromium.setup_driver()
        chromium.close()

    @pytest.mark.parametrize('options', [
        {"headless": True, "binary": "./chromium"}, {"headless": False}
    ])
    def test_setup_driver(self, mocker, options):
        mocker.patch('selenium.webdriver.ChromeOptions')
        driver_mock = mocker.patch('selenium.webdriver.Chrome')

        chromium = browser.Chromium(**options)
        chromium.setup_driver()

        driver_options_mock = driver_mock.call_args.kwargs['options']

        assert driver_options_mock.headless is options['headless']
        if 'binary' in options:
            assert driver_options_mock.binary_location == options['binary']
        assert driver_options_mock.add_argument.call_args.args == (
            f'user-data-dir={chromium._driver_data_directory}',
        )
        assert chromium.driver is driver_mock()

    def test_scroll_to_page_bottom(self, mocker):
        chromium = browser.Chromium()
        chromium._driver = mocker.Mock()

        time_sleep_mock = mocker.patch('time.sleep')

        chromium.scroll_to_page_bottom(times=2, timeout=3)

        assert chromium._driver.execute_script.call_count == 2
        assert chromium._driver.execute_script.call_args.args == (
            'window.scrollTo(0, document.body.scrollHeight);',
        )
        assert time_sleep_mock.call_args.args == (3,)

    def test_get(self, mocker):
        chromium = browser.Chromium()
        chromium._driver = mocker.Mock()

        chromium.get('url')
        assert chromium._driver.get.call_args.args == ('url',)

    def test_refresh(self, mocker):
        chromium = browser.Chromium()
        chromium._driver = mocker.Mock()

        chromium.refresh()
        assert chromium._driver.refresh.called

    def test_close(self, mocker):
        chromium = browser.Chromium()
        chromium._driver = mocker.Mock()

        chromium.close()
        assert chromium._driver.close.called


class TestFirefox:
    @pytest.mark.web_driver
    def test_driver(self):
        firefox = browser.Firefox(headless=False)
        firefox.setup_driver()
        firefox.close()

    @pytest.mark.parametrize('options', [
        {"headless": True, "binary": "./firefox"}, {"headless": False}
    ])
    def test_setup_driver(self, mocker, options):
        mocker.patch('selenium.webdriver.FirefoxOptions')
        driver_mock = mocker.patch('selenium.webdriver.Firefox')

        firefox = browser.Firefox(**options)
        firefox.setup_driver()

        driver_options_mock = driver_mock.call_args.kwargs['options']
        if  'binary' in options:
            assert driver_options_mock.binary_location == options['binary']
        assert driver_options_mock.headless is options['headless']
        assert driver_options_mock.set_preference.call_args.args == (
            'profile_directory', firefox._driver_data_directory
        )
        assert firefox.driver is driver_mock()
