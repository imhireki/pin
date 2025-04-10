import pytest

from pinterest.webpages import Login, SearchFeed
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


class TestSearchFeed:
    def test_url(self, mocker):
        search_feed = SearchFeed(mocker.Mock(), "sleep token")
        assert search_feed.url == "https://www.pinterest.com/search/pins/?q=sleep+token"

    def test_go_to_page(self, mocker):
        browser = mocker.Mock()

        search_feed = SearchFeed(browser, "sleep token")
        search_feed.go_to_page()

        browser.get.assert_called_with(search_feed.url)

    def test_load_more(self, mocker):
        browser = mocker.Mock()

        search_feed = SearchFeed(browser, "sleep token")
        search_feed.load_more()

        browser.scroll_down.assert_called()

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

        search_feed = SearchFeed(browser, "query")
        pids = search_feed.find_pin_ids()

        visibility_of_element_located.assert_called_with(settings.ELEMENTS["PINS"])
        assert pids == ids
