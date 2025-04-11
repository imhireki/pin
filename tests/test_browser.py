import browser


def test_browser_scroll_down(mocker):
    sleep = mocker.patch("time.sleep")
    driver = mocker.Mock()

    browser.scroll_down(driver, 3)

    driver.execute_script.assert_any_call(
        "window.scrollTo(0, document.body.scrollHeight);"
    )
    sleep.assert_called_with(3)


def test_firefox(mocker):
    driver = mocker.patch("browser.FirefoxDriver")
    options = mocker.patch("browser.FirefoxOptions").return_value

    result = browser.Firefox(headless=True)

    options.add_argument.assert_called_with("-headless")
    driver.assert_called_with(options)
    assert result == driver.return_value


def test_chrome(mocker):
    driver = mocker.patch("browser.ChromeDriver")
    options = mocker.patch("browser.ChromeOptions").return_value

    result = browser.Chrome(headless=True)

    options.add_argument.assert_called_with("--headless=new")
    options.add_experimental_option.assert_called_with("detach", True)
    driver.assert_called_with(options)
    assert result == driver.return_value
