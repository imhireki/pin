from utils import utils 


if __name__ == '__main__':

    url = 'https://br.pinterest.com/search/pins/?q=roronoa%20zoro%20icons'\
          '&rs=typed&term_meta[]=roronoa%7Ctyped&term_meta[]=zoro%7Ctyped'\
          '&term_meta[]=icons%7Ctyped'

    driver = utils.setup_driver()
    driver.get(url)

    try:
        pin_urls = utils.get_searched_links(driver)

        # Loop thru the urls to get data
        for url in pin_urls: 
            json_data = utils.current_json_data()

            # if url already in data, go to next url
            if json_data.get(url):
                continue

            driver.get(url)

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
            json_data[url] = url_data 
            utils.write_to_json(json_data)

    except Exception as e:
        print(e)
    
    driver.quit()

