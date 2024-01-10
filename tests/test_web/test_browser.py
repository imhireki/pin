import pytest

from web import browser


def test_browser_scroll_to_page_bottom(mocker):
    time_sleep_mock = mocker.patch('time.sleep')
    scroll_times = 2
    scroll_timeout = 3
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.scroll_to_page_bottom(times=scroll_times, timeout=scroll_timeout)

    assert (chromium._driver.execute_script.call_args.args[0]
            == 'window.scrollTo(0, document.body.scrollHeight);')
    assert chromium._driver.execute_script.call_count == scroll_times
    assert time_sleep_mock.call_args.args[0] == scroll_timeout

def test_browser_get(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.get('url')

    assert chromium._driver.get.call_args.args[0] == 'url'

def test_browser_refresh(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.refresh()

    assert chromium._driver.refresh.called

def test_browser_close(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.close()

    assert chromium._driver.close.called


class TestChromium:
    def test_driver(self, mocker):
        driver_mock = mocker.patch('web.browser.webdriver.Chrome')
        options_mock = mocker.patch('web.browser.webdriver.ChromeOptions')

        chromium = browser.Chromium()
        chromium.setup_driver()
        chromium.close()

        assert chromium.driver == driver_mock.return_value
        assert (driver_mock.call_args.kwargs['options']
                == options_mock.return_value)
        assert driver_mock.return_value.close.called


    @pytest.mark.parametrize('options', [
        {"headless": True, "binary": "./chromium"},
        {"headless": False}
    ])
    def test_setup_driver(self, mocker, options):
        driver_mock = mocker.patch('selenium.webdriver.Chrome')
        mocker.patch('selenium.webdriver.ChromeOptions')

        chromium = browser.Chromium(**options)
        chromium.setup_driver()

        driver_options_mock = driver_mock.call_args.kwargs['options']
        assert driver_options_mock.headless is options['headless']
        if 'binary' in options:
            assert driver_options_mock.binary_location == options['binary']
        assert (driver_options_mock.add_argument.call_args.args[0]
                == f'user-data-dir={chromium._driver_data_directory}')
        assert chromium.driver is driver_mock.return_value


class TestFirefox:
    def test_driver(self, mocker):
        driver_mock = mocker.patch('web.browser.webdriver.Firefox')
        options_mock = mocker.patch('web.browser.webdriver.FirefoxOptions')

        firefox = browser.Firefox()
        firefox.setup_driver()
        firefox.close()

        assert firefox.driver == driver_mock.return_value
        assert (driver_mock.call_args.kwargs['options']
                == options_mock.return_value)
        assert driver_mock.return_value.close.called


    @pytest.mark.parametrize('options', [
        {"headless": True, "binary": "./firefox"},
        {"headless": False}
    ])
    def test_setup_driver(self, mocker, options):
        mocker.patch('web.browser.webdriver.FirefoxOptions')
        driver_mock = mocker.patch('selenium.webdriver.Firefox')

        firefox = browser.Firefox(**options)
        firefox.setup_driver()

        driver_options_mock = driver_mock.call_args.kwargs['options']
        assert driver_options_mock.headless is options['headless']
        if  'binary' in options:
            assert driver_options_mock.binary_location == options['binary']
        assert (driver_options_mock.set_preference.call_args.args
                == ('profile', firefox._driver_data_directory))
        assert firefox.driver is driver_mock.return_value
