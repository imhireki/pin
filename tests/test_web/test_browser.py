import pytest

from web import browser


def test_browser_scroll_to_page_bottom(mocker):
    time_sleep_mock = mocker.patch("time.sleep")
    scroll_times = 2
    scroll_timeout = 3
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.scroll_to_page_bottom(times=scroll_times, timeout=scroll_timeout)

    assert (
        chromium._driver.execute_script.call_args.args[0]
        == "window.scrollTo(0, document.body.scrollHeight);"
    )
    assert chromium._driver.execute_script.call_count == scroll_times
    assert time_sleep_mock.call_args.args[0] == scroll_timeout


def test_browser_get(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.get("url")

    assert chromium._driver.get.call_args.args[0] == "url"


def test_browser_refresh(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.refresh()

    assert chromium._driver.refresh.called


def test_browser_quit(mocker):
    chromium = browser.Chromium()
    chromium._driver = mocker.Mock()

    chromium.quit()

    assert chromium._driver.quit.called


class TestChromium:
    def test_driver(self, mocker):
        driver = mocker.patch("web.browser.ChromeDriver")
        options = mocker.patch("web.browser.ChromeOptions")

        chromium = browser.Chromium()
        chromium.setup_driver()
        chromium.quit()

        assert chromium.driver == driver.return_value
        assert driver.call_args.kwargs["options"] == options.return_value
        assert driver.return_value.quit.called

    @pytest.mark.parametrize("raw_options", [{"headless": True}, {"headless": False}])
    def test_setup_driver(self, mocker, raw_options):
        driver = mocker.patch("web.browser.ChromeDriver").return_value
        options = mocker.patch("web.browser.ChromeOptions").return_value

        chromium = browser.Chromium(**raw_options)
        chromium.setup_driver()

        assert chromium.driver is driver

        if raw_options["headless"]:
            options.add_argument.assert_any_call("--headless=new")

        options.add_experimental_option.assert_called_with("detach", True)

        options.add_argument.assert_any_call(
            "--user-data-dir=" + chromium._driver_data_directory
        )


class TestFirefox:
    def test_driver(self, mocker):
        driver = mocker.patch("web.browser.FirefoxDriver")
        options = mocker.patch("web.browser.FirefoxOptions")

        firefox = browser.Firefox()
        firefox.setup_driver()
        firefox.quit()

        assert firefox.driver == driver.return_value
        assert driver.call_args.kwargs["options"] == options.return_value
        assert driver.return_value.quit.called

    @pytest.mark.parametrize("raw_options", [{"headless": True}, {"headless": False}])
    def test_setup_driver(self, mocker, raw_options):
        options = mocker.patch("web.browser.FirefoxOptions").return_value
        driver = mocker.patch("web.browser.FirefoxDriver").return_value

        firefox = browser.Firefox(**raw_options)
        firefox.setup_driver()

        assert firefox.driver is driver

        if raw_options["headless"]:
            options.add_argument.assert_any_call("-headless")
        assert options.profile == firefox._driver_data_directory
