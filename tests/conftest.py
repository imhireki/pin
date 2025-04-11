import pytest

from pinterest.webpages import Login
from browser import Firefox


@pytest.fixture(scope="session")
def pinterest_session():
    with Firefox(headless=False) as web_driver:
        login = Login(web_driver)
        login.go_to_page()
        login.close_google_login()
        login.authenticate()

        session = login.session
    return session
