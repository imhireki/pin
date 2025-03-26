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


def test_browser_shortcuts(mocker):
    firefox = browser.Firefox()
    driver = mocker.Mock()
    firefox._driver = driver

    cookie = firefox.get_cookie("cookie")
    cookies = firefox.get_cookies()
    firefox.switch_to_default_content()
    firefox.get("url")
    firefox.quit()

    assert cookie == driver.get_cookie.return_value
    assert cookies == driver.get_cookies.return_value
    driver.switch_to.default_content.assert_called()
    driver.get.assert_called_with("url")
    driver.quit.assert_called()


@pytest.mark.parametrize("options", [{"wait_timeout": 12}, {"wait_timeout": 10}])
def test_browser_set_wait_options(mocker, options):
    mocker.patch("web.browser.ChromeDriver")
    chromium = browser.Chromium()

    assert chromium._set_wait_options(options) == {"timeout": options["wait_timeout"]}


@pytest.mark.parametrize("options", [{}, {"headless": False}])
def test_browser_setup_driver(mocker, options):
    wait = mocker.patch("web.browser.WebDriverWait")

    chromium = browser.Chromium(**options)
    set_driver = mocker.patch.object(chromium, "_set_driver")
    set_driver_options = mocker.patch.object(chromium, "_set_driver_options")
    set_wait_options = mocker.patch.object(chromium, "_set_wait_options")

    chromium.setup_driver()

    processed_opts = {"headless": True, "wait_timeout": 10}
    processed_opts.update(options)
    set_driver_options.assert_called_with(processed_opts)
    set_wait_options.assert_called_with(processed_opts)

    set_driver.assert_called_with(set_driver_options.return_value)
    wait.assert_called_with(set_driver.return_value, **set_wait_options.return_value)

    assert chromium._driver and chromium._wait


class TestChromium:
    @pytest.mark.parametrize("headless", [True, False])
    def test_set_driver_options(self, mocker, headless):
        mocker.patch("web.browser.ChromeDriver")
        options = mocker.patch("web.browser.ChromeOptions").return_value

        chromium = browser.Chromium()

        assert options == chromium._set_driver_options(dict(headless=headless))
        if headless:
            options.add_argument.assert_any_call("--headless=new")
        options.add_experimental_option.assert_called_with("detach", True)
        options.add_argument.assert_any_call(
            "--user-data-dir=" + chromium._driver_data_directory
        )

    def test_set_driver(self, mocker):
        driver = mocker.patch("web.browser.ChromeDriver")
        options = mocker.Mock()

        chromium = browser.Chromium()
        chromium_driver = chromium._set_driver(options)

        driver.assert_called_with(options=options)
        assert chromium_driver is driver.return_value


class TestFirefox:
    @pytest.mark.parametrize("headless", [True, False])
    def test_set_driver_options(self, mocker, headless):
        mocker.patch("web.browser.FirefoxDriver")
        options = mocker.patch("web.browser.FirefoxOptions").return_value

        firefox = browser.Firefox(headless=headless)
        driver_options = firefox._set_driver_options(dict(headless=headless))
        assert driver_options == options
        if headless:
            options.add_argument.assert_any_call("-headless")
        assert options.profile == firefox._driver_data_directory

    def test_set_driver(self, mocker):
        driver = mocker.patch("web.browser.FirefoxDriver")
        options = mocker.Mock()

        firefox = browser.Firefox()
        firefox_driver = firefox._set_driver(options)

        driver.assert_called_with(options=options)
        assert firefox_driver is driver.return_value
