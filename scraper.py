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


# SETUP SELENIUM
url = 'https://br.pinterest.com/search/pins/?q=roronoa%20zoro%20icons'\
      '&rs=typed&term_meta[]=roronoa%7Ctyped&term_meta[]=zoro%7Ctyped'\
      '&term_meta[]=icons%7Ctyped'

driver_options = webdriver.FirefoxOptions()
driver_options.headless = True

driver = webdriver.Firefox(
    options=driver_options
    )

driver.get(url)

# scroll down on selenium
def scroller(scrolls=2): 
    scroll = 0
    while scroll < scrolls:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
            )
        time.sleep(5)
        scroll += 1

# append data to my json data
def write_to_json(data):
    w_file = open('data.json', 'w')
    json.dump(json_data, w_file, indent=4)
    w_file.close() 

# return my json data
def current_json_data():  
    r_file = open('data.json', 'r')
    json_data = json.load(r_file)
    r_file.close()
    return json_data

try:
    # GET THE COLLECTION
    collection = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.Collection')
            )
        ).get_attribute('outerHTML')
    
    # Parse the html
    collection_soup = BeautifulSoup(collection, 'html.parser')
    
    # GET THE URLS
    link_tags = collection_soup.find_all('a')
    
    PINTEREST_URL = 'https://br.pinterest.com'
    PIN_URLS = []

    for link in link_tags:
        pin_href = link.get('href')
        url = f'{PINTEREST_URL}{pin_href}' 
        
        PIN_URLS.append(url)
   
    # PIN_URLS = [PIN_URLS[0], PIN_URLS[1]]
    
    # GO TO EACH URL TO GET DATA
    for url in PIN_URLS:

        json_data = current_json_data()

        # if url already in data, go to next url
        if json_data.get(url):
            continue

        driver.get(url)
        URL_DATA = {}
         
        # html section
        data_section = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.rDA:nth-child(1)')
                )
            ).get_attribute('outerHTML')
        
        # parse html
        data_section_soup = BeautifulSoup(data_section, 'html.parser')

        # get title
        title = data_section_soup.h1.string
        URL_DATA['title'] = [
            title if title != 'requests are open!' else ''
            ][0] 

        # get subtitle
        subtitle = data_section_soup.h2.string 
        URL_DATA['subtitle'] = [
            subtitle if subtitle != ' ' else ''
            ][0]

        # get tags
        tags_section = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                    (
                    By.XPATH,
                    '/html/body/div[1]/div/div/div/div[2]/div[2]/div/div/'\
                    'div/div[2]/div/div/div/div/div[2]/div/div/div/div[7]'
                    )
                )
            ).get_attribute('outerHTML')
        
        tags_section_soup = BeautifulSoup(tags_section, 'html.parser')
        a_tags = tags_section_soup.find_all('a')
        
        tags = []
        for tag in a_tags:
            tag_soup = BeautifulSoup(str(tag), 'html.parser')
            tags.append(tag_soup.a.string) 
        
        URL_DATA['tags'] = tags 
        
        # get img
        img_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,'.PcK > div:nth-child(1) > img:nth-child(1)')
                )
            ).get_attribute('outerHTML')
        
        img_element_soup = BeautifulSoup(img_element, 'html.parser')
        URL_DATA['image'] = img_element_soup.img.get('src')
        
        # append data to json
        json_data[url] = URL_DATA
        write_to_json(json_data)

except Exception as e:
    print(e)

driver.quit()

