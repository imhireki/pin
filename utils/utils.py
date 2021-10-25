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


def setup_driver():
    driver_options = webdriver.FirefoxOptions()
    driver_options.headless = True

    return webdriver.Firefox(
        options=driver_options
        )

def scroller(scrolls=2): 
    scroll = 0
    while scroll < scrolls:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
            )
        time.sleep(5)
        scroll += 1

def write_to_json(data):
    w_file = open('data.json', 'w')
    json.dump(data, w_file, indent=4)
    w_file.close() 

def current_json_data():  
    r_file = open('data.json', 'r')
    json_data = json.load(r_file)
    r_file.close()
    return json_data

def get_searched_links(driver):
    collection = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.Collection')
            )
        ).get_attribute('outerHTML')
    collection_soup = BeautifulSoup(collection, 'html.parser')
    
    # RETURN THE URLS
    link_tags = collection_soup.find_all('a')

    PINTEREST_URL = 'https://br.pinterest.com'
    pin_urls = []

    for link in link_tags:
        pin_href = link.get('href')
        url = f'{PINTEREST_URL}{pin_href}' 
        pin_urls.append(url)
   
    # PIN_URLS = [PIN_URLS[0], PIN_URLS[1]]
    return pin_urls

def get_title_subtitle_section(driver): 
    data_section = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.rDA:nth-child(1)')
            )
        ).get_attribute('outerHTML')
    return BeautifulSoup(data_section, 'html.parser')

def get_title(soup):
    title = soup.h1.string
    return [title if title != 'requests are open!' else ''][0] 

def get_subtitle(soup):
    subtitle = soup.h2.string 
    return [subtitle if subtitle != ' ' else ''][0]

def get_tags_section(driver): 
    tags_section = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div[2]/div/div/'\
                       'div/div[2]/div/div/div/div/div[2]/div/div/div/div[7]')
            )
        ).get_attribute('outerHTML')
    return BeautifulSoup(tags_section, 'html.parser')

def get_tags(soup):
    a_tags = soup.find_all('a')
    tags = []
    for tag in a_tags:
        tag_soup = BeautifulSoup(str(tag), 'html.parser')
        tags.append(tag_soup.a.string) 
    return tags     

def get_image_section(driver):
    img_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,'.PcK > div:nth-child(1) > img:nth-child(1)')
            )
        ).get_attribute('outerHTML')
    return BeautifulSoup(img_element, 'html.parser')

def get_image(soup):
    return soup.img.get('src')

