from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas
import time
import json
import re


def setup_driver():
    driver_options = webdriver.FirefoxOptions()
    driver_options.headless = True

    return webdriver.Firefox(
        options=driver_options
        )

def scroller(driver, scrolls): 
    while scrolls > 1:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
            )
        time.sleep(10)
        scrolls -= 1

def write_to_json(data):
    w_file = open('data.json', 'w')
    json.dump(data, w_file, indent=4)
    w_file.close() 

def current_json_data():  
    r_file = open('data.json', 'r')
    json_data = json.load(r_file)
    r_file.close()
    return json_data

def perform_login(driver):
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.Eqh:nth-child(3) > div:nth-child(1) > button:nth-child(1)')
            )
        ).click()

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#email')
            )
        )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#password')
            )
        ) 
    
    email_input.send_keys('f9c10a89b0@emailnax.com')
    password_input.send_keys('teste123', Keys.ENTER)
    time.sleep(10) 

def get_searched_links(driver):
    try:
        collection = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.vbI:nth-child(1)')
                )
            ).get_attribute('outerHTML')
    except Exception:
        raise Exception('Problem getting the links')

    # soup
    collection_soup = BeautifulSoup(collection, 'html.parser')
    link_tags = collection_soup.find_all('a')

    PINTEREST_URL = 'https://br.pinterest.com'
    pin_urls = []

    # append urls to pin_urls
    for link in link_tags:
        pin_href = link.get('href')

        if not 'pin' in pin_href:
            continue

        url = f'{PINTEREST_URL}{pin_href}' 
        pin_urls.append(url)

    return pin_urls

def get_title_section(driver): 
    try:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1.lH1')
                )
            ).get_attribute('outerHTML')
    except Exception:
        return None

def get_title(section):
    if not section:
        return ''
    return BeautifulSoup(section, 'html.parser').h1.string

def get_subtitle_section(driver): 
    try:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.FNs:nth-child(2) > span:nth-child(1)')
                )
            ).get_attribute('outerHTML')
    except Exception:
        return None

def get_subtitle(section):
    if not section:
        return ''
    soup = BeautifulSoup(section, 'html.parser')
    try:
        return soup.span.string
    except Exception as e:
        return ''

def get_image_section(driver):
    try:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.OVX > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)')
                )
            ).get_attribute('outerHTML')

    except Exception:
        return None

def get_image(section):
    if not section:
        return []
    
    img = BeautifulSoup(section, 'html.parser').find('img')

    if img:
        src = img.get('src')
        return [src]

    # DEAL WITH STYLE IMAGES
    soup = BeautifulSoup(section, 'html.parser')
    
    urls = []
    for div in soup.find_all('div'):
        style = div.get('style', '')
        _url = re.search("http.*[)]", style)

        if not _url:
            continue
         
        url = style[_url.start():_url.end()-2] 
        urls.append(url)
    
    return urls

def validate_data(data):
    """ errors if not img and not title """
    # def data
    title = data.get('title', '')
    subtitle = data.get('subtitle', '') 
    image = data.get('image', [])
    errors = {}

    # Check / patch data - TODO: Update it to regex
    if title == 'requests are open!':  # pinterest placeholder
        title = ''
     
    if subtitle == ' ' or subtitle == None:
        subtitle = ''
     
    if not image:
        errors['image'] = 'lack in image'

    # Try patch the title
    if not title:
        if subtitle:
            title = subtitle
        else:
            errors['title'] = 'lack in title'
             
    # Join the new data
    cleaned_data = {
        'title': title,
        'subtitle': subtitle,
        'image': image
        }
    
    return cleaned_data, errors   
 
