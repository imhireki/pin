from storage.connection import connect_to_postgres, connect_to_mysql
from storage.database import PostgreSQLStorage, MySQLStorage
from storage.file import CSVStorage, JsonStorage
from pinterest.webpages import Login, SearchFeed
from browser import Firefox
import settings
import utils


QUERY = "Frieren Icon"

with (
    Firefox(headless=True) as web_driver,
    connect_to_postgres(**settings.DATABASE) as db_connection,
):
    storage = PostgreSQLStorage(db_connection)

    login = Login(web_driver)
    login.go_to_page()
    login.close_google_login()
    login.authenticate()
    session = login.session

    search_feed = SearchFeed(web_driver, QUERY)
    search_feed.go_to_page()
    search_feed.load_more()
    pin_ids = search_feed.find_pin_ids()

    for pid in pin_ids:
        utils.store_valid_pin(storage, session, pid)
