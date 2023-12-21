import pytest

from web import www
import settings


class TestPinterest:
    @pytest.mark.parametrize('query, search_url', [
        ('query', f'{settings.URLS["SEARCH_PIN"]}query'),
        ('my query', f'{settings.URLS["SEARCH_PIN"]}my+query'),
    ])
    def test_make_search_url(self, mocker, query, search_url):
        pinterest = www.Pinterest(mocker.Mock())
        url = pinterest.make_search_url(query)

        assert url == search_url

    def test_perform_login(self, mocker):
        web_element_manager_mock = mocker.patch(
            'web.www.WebElementManager').return_value

        pinterest = www.Pinterest(mocker.Mock())
        pinterest.perform_login()

        assert (web_element_manager_mock.mock_calls[0].args[0]
                == settings.ELEMENTS['EMAIL_INPUT']['element'])
        assert (web_element_manager_mock.mock_calls[1].args[0]
                == settings.CREDENTIALS['EMAIL'])
        assert (web_element_manager_mock.mock_calls[2].args[0]
                == settings.ELEMENTS['PASSWORD_INPUT']['element'])
        assert (web_element_manager_mock.mock_calls[3].args[0]
                == settings.CREDENTIALS['PASSWORD'])

    def test_find_pins_urls(self, mocker):
        pins_a_tag = [{"href": "/pin/123/"}]

        web_element_manager_mock = mocker.patch(
            'web.www.WebElementManager').return_value
        web_element_manager_mock.make_html_soup\
            .return_value.find_all=lambda _: pins_a_tag

        pinterest = www.Pinterest(mocker.Mock())
        pins_urls = pinterest.find_pins_urls()

        assert pins_urls == [settings.URLS["HOME"] + pins_a_tag[0]["href"]]

    @pytest.mark.parametrize('validity, data', [
        (True, {"title": "title"}),
        (False, {})
    ])
    def test_fetch_pin_data(self, mocker, validity, data):
        pin_mock = mocker.patch('web.www.Pin')
        pin_mock.return_value = mocker.Mock(is_valid=lambda: validity,
                                            fetch_data=lambda: data)

        pinterest = www.Pinterest(mocker.Mock())
        fetched_pin_data = pinterest.fetch_pin_data(
            'https://pinterest.com/pin/123/')

        assert fetched_pin_data == data
