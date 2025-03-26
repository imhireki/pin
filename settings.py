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
    "GOOGLE_LOGIN": (
        By.CSS_SELECTOR,
        "#credential_picker_container > iframe:nth-child(1)",
    ),
    "GOOGLE_LOGIN_CLOSE_BUTTON": (By.ID, "close"),
    "PINS": (By.CSS_SELECTOR, "div.vbI:nth-child(1)"),
    "EMAIL_FIELD": (By.CSS_SELECTOR, "#email"),
    "PASSWORD_FIELD": (By.CSS_SELECTOR, "#password"),
}

CREDENTIALS = {
    "EMAIL": os.getenv("PINTEREST_EMAIL", ""),
    "PASSWORD": os.getenv("PINTEREST_PASSWORD", ""),
}

DATABASE = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
