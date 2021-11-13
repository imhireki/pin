from utils import utils

if __name__ == '__main__':
    urls = [
        'https://br.pinterest.com/search/pins/?q=anime%20pfp&rs=typed&term_meta[]=anime%7Ctyped&term_meta[]=pfp%7Ctyped',
        'https://br.pinterest.com/search/pins/?q=anime%20profile%20picture&rs=typed&term_meta[]=anime%7Ctyped&term_meta[]=profile%7Ctyped&term_meta[]=picture%7Ctyped',
        'https://br.pinterest.com/search/pins/?q=profile%20pic%20anime&rs=typed&term_meta[]=profile%7Ctyped&term_meta[]=pic%7Ctyped&term_meta[]=anime%7Ctyped',
        'https://br.pinterest.com/search/pins/?q=profile%20pic%20anime%20border&rs=typed&term_meta[]=profile%7Ctyped&term_meta[]=pic%7Ctyped&term_meta[]=anime%7Ctyped&term_meta[]=border%7Ctyped'
        ]

    try:

        for url in urls:
            driver = utils.setup_driver()
            driver.get(url)

            if urls[0]:
                utils.perform_login(driver)

            scrolls = 1 
            pin_urls = []
            sum_scrolls = 1 
            json_data = utils.current_json_data() 
            used_pin_urls = list(json_data.keys())

            while scrolls < 2:
                driver.get(url)
                utils.scroller(driver, sum_scrolls)

                # urls pins getter
                _pin_urls = utils.get_searched_links(driver)

                # urls pins setter
                pin_urls = [
                    pin
                    for pin in _pin_urls
                    if pin not in used_pin_urls
                    ] 

                # Loop thru the urls to get data
                for pin_url in pin_urls:
                    used_pin_urls.append(pin_url)
                    driver.get(pin_url)

                    # Get the data
                    title_soup = utils.get_title_section(driver)
                    title = utils.get_title(title_soup)
                    
                    subtitle_soup = utils.get_subtitle_section(driver)
                    subtitle = utils.get_subtitle(subtitle_soup)
                    
                    image_soup = utils.get_image_section(driver)
                    image = utils.get_image(image_soup)

                    url_data = {
                        'title': title,
                        'subtitle': subtitle,
                        'image': image,
                        }
                    
                    # Patch or exclude invalid / not good data
                    cleaned_data, errors = utils.validate_data(url_data)

                    if errors:
                        continue

                    # append data to json
                    json_data[pin_url] = cleaned_data 
                    utils.write_to_json(json_data)
                    
                scrolls -= 1
                sum_scrolls +=  1
            
    except Exception as e:
        raise e
    
    except KeyboardInterrupt:
        pass
    
    finally:
        driver.quit()

