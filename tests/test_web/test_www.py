import pytest

from web import www
import settings


class TestPinterest:
    @pytest.mark.parametrize('query,search_url', [
        ('query', f'{settings.URLS["SEARCH_PIN"]}query'),
        ('my query', f'{settings.URLS["SEARCH_PIN"]}my+query'),
    ])
    def test_make_search_url(self, mocker, query, search_url):
        pinterest = www.Pinterest(mocker.Mock())
        url = pinterest.make_search_url(query)

        assert url == search_url

    def test_perform_login(self, mocker):
        web_element_manager_mock = mocker.Mock()

        pinterest = www.Pinterest(web_element_manager_mock)
        pinterest.perform_login()

        assert (web_element_manager_mock.mock_calls[0].args
                == (settings.ELEMENTS['EMAIL_INPUT']['element'],))
        assert (web_element_manager_mock.mock_calls[1].args
                == (settings.CREDENTIALS['EMAIL'],))

        assert ((settings.ELEMENTS['PASSWORD_INPUT']['element'],)
                == web_element_manager_mock.mock_calls[2].args)
        assert (settings.CREDENTIALS['PASSWORD']
                in web_element_manager_mock.mock_calls[3].args)

    def test_find_pins_urls(self, mocker):
        pins_a_tag = [{"href": "/pin/123/"}]

        web_element_manager_mock = mocker.Mock()
        make_html_soup_mock = web_element_manager_mock.make_html_soup
        make_html_soup_mock.return_value.find_all = lambda _: pins_a_tag

        pinterest = www.Pinterest(web_element_manager_mock)
        pins_urls = pinterest.find_pins_urls()

        assert pins_urls == [settings.URLS["HOME"] + pins_a_tag[0]["href"]]

    @pytest.mark.parametrize('validity,data', [
        (True, {"title": "title"}), (False, {})
    ])
    def test_fetch_pin_data(self, mocker, validity, data):
        pin_url = 'https://pinterest.com/pin/123/'

        pin_mock = mocker.patch('web.www.Pin')
        pin_mock.return_value = mocker.Mock(is_valid=lambda: validity,
                                            fetch_data=lambda: data)

        pinterest = www.Pinterest(mocker.Mock())
        pin_data = pinterest.fetch_pin_data(pin_url)

        assert pin_data == data

