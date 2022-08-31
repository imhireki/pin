from selenium.webdriver.common.by import By
import os


URLS = {
    "SEARCH_PIN": "https://www.pinterest.com/search/pins/?q=",
    "LOGIN": "https://www.pinterest.com/login/",
    "HOME": "https://www.pinterest.com",
}

ELEMENTS = {
    "PINS": {
        "element": 'div.vbI:nth-child(1)',
        "locator": By.CSS_SELECTOR
    },
    "EMAIL_INPUT": {
        "element": "#email",
        "locator": By.CSS_SELECTOR,
    },
    "PASSWORD_INPUT": {
        "element": "#password",
        "locator": By.CSS_SELECTOR
    },
}

CREDENTIALS = {
    "EMAIL": os.getenv('PINTEREST_EMAIL'),
    "PASSWORD": os.getenv('PINTEREST_PASSWORD')
}

DATABASE = {
    "database": os.getenv('PIN_DATABASE'),
    "user": os.getenv('PIN_USER'),
    "password": os.getenv('PIN_PASSWORD'),
}
