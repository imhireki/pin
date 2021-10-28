from utils import utils 


#  \ - - - |\ BASIC STRUCTURE /| - - - - /
#   TODO: for pinterest search urls
#       while scrolls
#           for pin url in search urls
#               get data url 


if __name__ == '__main__':
    url = 'https://br.pinterest.com/search/pins/?q=anime%20icon%20profile%20pictur&rs=typed&term_meta[]=anime%7Ctyped&term_meta[]=icon%7Ctyped&term_meta[]=profile%7Ctyped&term_meta[]=pictur%7Ctyped'

    driver = utils.setup_driver()
    
    try:
        scrolls = 5 
        pin_urls = []
        sum_scrolls = 1 
        json_data = utils.current_json_data() 
        used_pin_urls = list(json_data.keys())

        while scrolls > 0:
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
                titles_soup = utils.get_titles_section(driver)
                title = utils.get_title(titles_soup)
                subtitle = utils.get_subtitle(titles_soup)
                
                tags_soup = utils.get_tags_section(driver)
                tags = utils.get_tags(tags_soup)

                image_soup = utils.get_image_section(driver)
                image = utils.get_image(image_soup)

                url_data = {
                    'title': title,
                    'subtitle': subtitle,
                    'tags': tags,
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

