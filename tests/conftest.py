import pytest

from pinterest.webpages import Login
from browser import Firefox


@pytest.fixture(scope="session")
def pinterest_session():
    browser = Firefox(binary="geckodriver", headless=True)
    browser.setup_driver()

    login = Login(browser)
    login.go_to_page()
    login.authenticate()

    session = login.session
    browser.quit()
    return session
