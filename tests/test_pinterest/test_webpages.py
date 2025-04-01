import pytest

from pinterest.webpages import Pinterest, Login, SearchFeed
import settings


EC = "selenium.webdriver.support.expected_conditions"


class TestLogin:
    def test_url(self, mocker):
        login = Login(mocker.Mock())

        assert login.url == "https://www.pinterest.com/login/"

    def test_go_to_page(self, mocker):
        browser = mocker.Mock()

        login = Login(browser)
        login.go_to_page()

        browser.get.assert_called_with(login.url)

    def test_close_google_login(self, mocker):
        frame_to_be_available = mocker.patch(
            EC + ".frame_to_be_available_and_switch_to_it"
        )
        element_to_be_clickable = mocker.patch(EC + ".element_to_be_clickable")
        browser = mocker.Mock()

        login = Login(browser)
        login.close_google_login()

        assert browser.wait.until.call_count == 2
        frame_to_be_available.assert_called_with(settings.ELEMENTS["GOOGLE_LOGIN"])
        element_to_be_clickable.assert_called_with(
            settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"]
        )
        browser.wait.until().click.assert_called()
        browser.switch_to_default_content.assert_called()

    @pytest.mark.parametrize(
        "cookies",
        [
            [],
            [{"name": "_auth", "value": "0"}],
            [{"name": "_auth", "value": "1"}],
        ],
    )
    def test_authenticate_session(self, mocker, cookies):
        sleep = mocker.patch("time.sleep")
        auth_cookie = cookies[0] if cookies else {}

        browser = mocker.Mock()
        browser.get_cookie.return_value = None if not cookies else auth_cookie
        browser.get_cookies.return_value = cookies

        login = Login(browser)
        login.session = mocker.Mock()

        if auth_cookie and auth_cookie["value"] == "1":
            login.authenticate_session(1, 0)
            login.session.cookies.set.assert_called()
            sleep.assert_not_called()
        else:
            try:
                login.authenticate_session(1, 0)
            except Exception:
                login.session.cookies.set.assert_not_called()
                sleep.assert_called()

    def test_authenticate(self, mocker):
        element_to_be_clickable = mocker.patch(EC + ".element_to_be_clickable")

        browser = mocker.Mock()
        login = Login(browser)
        auth_session = mocker.patch.object(login, "authenticate_session")
        login.authenticate()

        assert browser.wait.until.call_count == 2

        element_to_be_clickable.assert_any_call(settings.ELEMENTS["EMAIL_FIELD"])
        browser.wait.until().send_keys.assert_any_call(settings.CREDENTIALS["EMAIL"])

        element_to_be_clickable.assert_any_call(settings.ELEMENTS["PASSWORD_FIELD"])
        browser.wait.until().send_keys.assert_any_call(
            settings.CREDENTIALS["PASSWORD"], "\ue007"
        )

        auth_session.assert_called_with(10, 1)


class TestPinterest:
    @pytest.mark.parametrize(
        "query, search_url",
        [
            ("query", f'{settings.URLS["SEARCH_PIN"]}query'),
            ("my query", f'{settings.URLS["SEARCH_PIN"]}my+query'),
        ],
    )
    def test_make_search_url(self, mocker, query, search_url):
        pinterest = Pinterest(mocker.Mock())
        url = pinterest.make_search_url(query)

        assert url == search_url

    def test_close_google_login(self, mocker):
        frame_to_be_available = mocker.patch(
            EC + ".frame_to_be_available_and_switch_to_it"
        )
        element_to_be_clickable = mocker.patch(EC + ".element_to_be_clickable")

        browser = mocker.Mock()
        pinterest = Pinterest(browser)
        pinterest.close_google_login()

        assert browser.wait.until.call_count == 2
        frame_to_be_available.assert_called_with(settings.ELEMENTS["GOOGLE_LOGIN"])
        element_to_be_clickable.assert_called_with(
            settings.ELEMENTS["GOOGLE_LOGIN_CLOSE_BUTTON"]
        )
        browser.wait.until().click.assert_called()
        browser.switch_to_default_content.assert_called()

    @pytest.mark.parametrize(
        "cookies",
        [
            [],
            [{"name": "_auth", "value": "0"}],
            [{"name": "_auth", "value": "1"}],
        ],
    )
    def test_authenticate_session(self, mocker, cookies):
        sleep = mocker.patch("time.sleep")
        auth_cookie = cookies[0] if cookies else {}

        browser = mocker.Mock()
        browser.get_cookie.return_value = None if not cookies else auth_cookie
        browser.get_cookies.return_value = cookies

        pinterest = Pinterest(browser)
        pinterest.session = mocker.Mock()

        if auth_cookie and auth_cookie["value"] == "1":
            pinterest.authenticate_session(1, 0)
            pinterest.session.cookies.set.assert_called()
            sleep.assert_not_called()

    def test_perform_login(self, mocker):
        element_to_be_clickable = mocker.patch(EC + ".element_to_be_clickable")

        browser = mocker.Mock()
        pinterest = Pinterest(browser)
        auth_session = mocker.patch.object(pinterest, "authenticate_session")
        pinterest.perform_login()

        assert browser.wait.until.call_count == 2

        element_to_be_clickable.assert_any_call(settings.ELEMENTS["EMAIL_FIELD"])
        browser.wait.until().send_keys.assert_any_call(settings.CREDENTIALS["EMAIL"])

        element_to_be_clickable.assert_any_call(settings.ELEMENTS["PASSWORD_FIELD"])
        browser.wait.until().send_keys.assert_any_call(
            settings.CREDENTIALS["PASSWORD"], "\ue007"
        )

        auth_session.assert_called_with(10, 1)

    @pytest.mark.parametrize(
        "html,ids",
        [
            ["", set()],
            ["<html></html>", set()],
            [
                "<html><a href='/pin/123/'>link1</a><a href='/hmmm/'>link2</a></html>",
                {"123"},
            ],
        ],
    )
    def test_find_pin_ids(self, mocker, html, ids):
        visibility_of_element_located = mocker.patch(
            EC + ".visibility_of_element_located"
        )
        browser = mocker.Mock()
        browser.wait.until.return_value.get_attribute.return_value = html

        pinterest = Pinterest(browser)
        pids = pinterest.find_pin_ids()

        visibility_of_element_located.assert_called_with(settings.ELEMENTS["PINS"])
        assert pids == ids

    @pytest.mark.parametrize(
        "validity, data", [(True, {"title": "title"}), (False, {})]
    )
    def test_fetch_pin_data(self, mocker, validity, data):
        pin = mocker.patch("pinterest.webpages.Pin").return_value
        pin.is_valid.return_value = validity
        pin.fetch_data.return_value = data
        mocker.patch("pinterest.webpages.PinData")

        pinterest = Pinterest(mocker.Mock())
        result = pinterest.fetch_pin_data("123")

        assert result == data
