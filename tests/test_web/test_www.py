import pytest

from web import www
import settings


class TestPinterest:
    @pytest.mark.parametrize(
        "query, search_url",
        [
            ("query", f'{settings.URLS["SEARCH_PIN"]}query'),
            ("my query", f'{settings.URLS["SEARCH_PIN"]}my+query'),
        ],
    )
    def test_make_search_url(self, mocker, query, search_url):
        pinterest = www.Pinterest(mocker.Mock())
        url = pinterest.make_search_url(query)

        assert url == search_url

    def test_close_google_login(self, mocker):
        web_element_manager = mocker.patch("web.www.WebElementManager").return_value
        driver = mocker.Mock()

        pinterest = www.Pinterest(driver)
        pinterest.close_google_login()

        web_element_manager.get.assert_any_call(
            settings.ELEMENTS["GOOGLE_LOGIN"]["element"]
        )
        driver.switch_to.frame.assert_called()
        web_element_manager.get.assert_any_call(
            settings.ELEMENTS["GOOGLE_LOGIN"]["element"]
        )
        web_element_manager.get.return_value.click.assert_called()
        driver.switch_to.default_content.assert_called()

    def test_perform_login(self, mocker):
        web_element_manager_mock = mocker.patch(
            "web.www.WebElementManager"
        ).return_value

        pinterest = www.Pinterest(mocker.Mock())
        pinterest.perform_login()

        assert (
            web_element_manager_mock.mock_calls[0].args[0]
            == settings.ELEMENTS["EMAIL_INPUT"]["element"]
        )
        assert (
            web_element_manager_mock.mock_calls[1].args[0]
            == settings.CREDENTIALS["EMAIL"]
        )
        assert (
            web_element_manager_mock.mock_calls[2].args[0]
            == settings.ELEMENTS["PASSWORD_INPUT"]["element"]
        )
        assert (
            web_element_manager_mock.mock_calls[3].args[0]
            == settings.CREDENTIALS["PASSWORD"]
        )

    @pytest.mark.parametrize("html,ids", [
        ["", []],
        ["<html></html>", []],
        [
            "<html> <a href='/pin/123/'>link1</a> <a href='/invalid/'>link2</a> </html>",
            ["123"]
         ],
    ])
    def test_find_pin_ids(self, mocker, html, ids):
        web_element_manager = mocker.patch("web.www.WebElementManager").return_value
        web_element_manager.get_html.return_value = html

        pinterest = www.Pinterest(mocker.Mock())
        pins_urls = pinterest.find_pin_ids()

        assert pins_urls == ids

    @pytest.mark.parametrize(
        "validity, data", [(True, {"title": "title"}), (False, {})]
    )
    def test_fetch_pin_data(self, mocker, validity, data):
        pin_mock = mocker.patch("web.www.Pin")
        pin_mock.return_value = mocker.Mock(
            is_valid=lambda: validity, fetch_data=lambda: data
        )

        pinterest = www.Pinterest(mocker.Mock())
        fetched_pin_data = pinterest.fetch_pin_data("https://pinterest.com/pin/123/")

        assert fetched_pin_data == data
