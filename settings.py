import os

from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

URLS = {
    "SEARCH_PIN": "https://www.pinterest.com/search/pins/?q=",
    "LOGIN": "https://www.pinterest.com/login/",
    "HOME": "https://www.pinterest.com",
}


ELEMENTS = {
    "GOOGLE_LOGIN": {
        "element": "#credential_picker_container > iframe:nth-child(1)",
        "locator": By.CSS_SELECTOR,
    },
    "GOOGLE_LOGIN_CLOSE_BUTTON": {
        "element": "close",
        "locator": By.ID,
    },
    "PINS": {
        "element": "div.vbI:nth-child(1)",
        "locator": By.CSS_SELECTOR,
    },
    "EMAIL_INPUT": {
        "element": "#email",
        "locator": By.CSS_SELECTOR,
    },
    "PASSWORD_INPUT": {
        "element": "#password",
        "locator": By.CSS_SELECTOR,
    },
}

CREDENTIALS = {
    "EMAIL": os.getenv("PINTEREST_EMAIL"),
    "PASSWORD": os.getenv("PINTEREST_PASSWORD"),
}

DATABASE = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
