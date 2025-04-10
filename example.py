from pinterest.webpages import Login, SearchFeed
from storage.file import CSVStorage, JsonStorage
from storage.database import PostgreSQLStorage, MySQLStorage
from storage.utils import connect_to_postgres, connect_to_mysql
from browser import Firefox
import settings
import utils


QUERY = "Frieren Icon"

db_connection = connect_to_postgres(**settings.DATABASE)
storage = PostgreSQLStorage(db_connection)

browser = Firefox(headless=True)
browser.setup_driver()

try:
    login = Login(browser)
    login.go_to_page()
    login.authenticate()
    session = login.session

    search_feed = SearchFeed(browser, QUERY)
    search_feed.go_to_page()
    search_feed.load_more()
    pin_ids = search_feed.find_pin_ids()

    for pid in pin_ids:
        utils.store_valid_pin(storage, session, pid)
finally:
    browser.quit()
    db_connection.close()
