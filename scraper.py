from utils import utils

if __name__ == '__main__':
    url = 'https://br.pinterest.com/search/pins/?q=roronoa%20zoro%20icons&rs=typed&term_meta[]=roronoa%7Ctyped&term_meta[]=zoro%7Ctyped&term_meta[]=icons%7Ctyped'
    
    url = 'https://br.pinterest.com/search/pins/?q=anime%20icon&rs=typed&term_meta[]=anime%7Ctyped&term_meta[]=icon%7Ctyped'

    driver = utils.setup_driver()
    driver.get(url)
    utils.perform_login(driver)

    try:
        scrolls = 1 
        pin_urls = []
        sum_scrolls = 1 
        json_data = utils.current_json_data() 
        used_pin_urls = list(json_data.keys())

        while scrolls < 5:
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
        print(e)

    driver.quit()

