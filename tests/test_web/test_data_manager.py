from web import data_manager


def test_web_data_manager_make_html_soup(mocker):
    beautiful_soup_mock = mocker.patch("web.data_manager.BeautifulSoup")
    html = "<html></html>"

    web_element_manager = data_manager.WebElementManager(mocker.Mock())
    html_soup = web_element_manager.make_html_soup(html)

    assert beautiful_soup_mock.call_args.args == (html, "html.parser")
    assert html_soup is beautiful_soup_mock.return_value


class TestWebElementManager:
    def test_get(self, mocker):
        mocker.patch("web.data_manager.WebDriverWait")
        locator_mock, ec_mock = mocker.Mock, mocker.Mock()
        element = "ele.ment"
        web_element_manager = data_manager.WebElementManager(mocker.Mock())
        web_driver_wait_mock = web_element_manager._web_driver_wait

        web_element = web_element_manager.get(element, locator_mock, ec_mock)

        assert web_element is web_driver_wait_mock.until.return_value
        assert web_driver_wait_mock.until.call_args.args[0] == ec_mock.return_value
        assert ec_mock.call_args.args[0] == (locator_mock, element)

    def test_get_html(self, mocker):
        web_element_mock = mocker.Mock()
        web_element_manager = data_manager.WebElementManager(mocker.Mock())

        html_element = web_element_manager.get_html(web_element_mock)

        assert web_element_mock.get_attribute.call_args.args[0] == "outerHTML"
        assert html_element is web_element_mock.get_attribute.return_value


class TestGetRequestManager:
    def test_get(self, mocker):
        url = "http://127.0.0.1/"
        session_mock = mocker.patch(
            "requests.Session",
        )()
        web_driver_mock = mocker.Mock(get_cookies=lambda: [{"name": "a", "value": "b"}])

        get_request_manager = data_manager.GetRequestManager(web_driver_mock)
        response = get_request_manager.get(url)

        assert session_mock.cookies.set.call_args.args == ("a", "b")
        assert response is session_mock.get.return_value
        assert session_mock.get.call_args.args[0] == url

    def test_get_html(self, mocker):
        web_driver_mock = mocker.Mock(get_cookies=lambda: [{"name": "a", "value": "b"}])
        response_mock = mocker.Mock()

        get_request_manager = data_manager.GetRequestManager(web_driver_mock)
        response_html = get_request_manager.get_html(response_mock)

        assert response_html is response_mock.text
