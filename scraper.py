from utils import utils 


if __name__ == '__main__':

    url = 'https://br.pinterest.com/search/pins/?q=roronoa%20zoro%20icons'\
          '&rs=typed&term_meta[]=roronoa%7Ctyped&term_meta[]=zoro%7Ctyped'\
          '&term_meta[]=icons%7Ctyped'

    driver = utils.setup_driver()
    driver.get(url)

    try:
        scrolls = 3 
        pin_urls = []
        used_pin_urls = []

        while scrolls > 0:
            # Getter
            _pin_urls = utils.get_searched_links(driver)

            # Setter
            pin_urls = [
                pin
                for pin in _pin_urls
                if pin not in used_pin_urls
                ] 
                        
            # Loop thru the urls to get data
            for pin_url in pin_urls:

                # get data
                json_data = utils.current_json_data()

                # if url already in data, go to next url
                if json_data.get(pin_url):
                    continue

                driver.get(pin_url)

                # Get the datas 
                titles_soup = utils.get_title_subtitle_section(driver)
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

                # append data to json
                json_data[pin_url] = url_data 
                utils.write_to_json(json_data)
                # // End loop For(get data at list of urls)

            for pin in pin_urls:
                used_pin_urls.append(pin)
                
            utils.scroller(driver=driver)
            scrolls -= 1
            # // End loop while (scrolls)
            
    except Exception as e:
        print(e)

    driver.quit()

