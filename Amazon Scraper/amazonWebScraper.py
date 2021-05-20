import csv
from bs4 import BeautifulSoup
from selenium import webdriver


def get_url(search_term):
    """Generate a url from search_term"""
    template = 'https://www.amazon.com/s?k={}{}&ref=nb_sb_noss_1'
    search_term = search_term.replace(' ', '+')
    # Add term query to url
    url = template.format(search_term, '{}')
    # Add page query placeholder
    url = url.format('&page={}')
    return url


def extract_record(_item):
    """Extract and return data from a single record"""
    # description and url
    atag = _item.h2.a
    description = atag.text.strip()
    url = 'https://www.amazon.com' + atag.get('href')
    try:
        # Price
        price_parent = _item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError:
        return
    try:
        # Rank and rating
        rating = _item.i.text
        review_count = _item.find('span', {'class': 'a-size-base'}).text
    except AttributeError:
        rating = ''
        review_count = ''
    # Image src url
    image_src = _item.find('img', {'class': 's-image'})['src']

    result = (description, price, rating, review_count, url, image_src)
    return result


def main(search_term):
    """Run main program routine"""
    # Create an instance of the web driver
    driver = webdriver.Chrome()
    records = []
    url = get_url(search_term)

    for page in range(1, 50):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)
        max_pages = soup.find_all('li', {'class': 'a-disabled', 'aria-disabled': 'true'})
        max_page = 0
        for p in max_pages:
            try:
                max_page = int(p.text)
            except ValueError:
                continue
        to_break = False
        next_page = (int(str(page)) + 1)
        if max_page < next_page:
            to_break = True
        if to_break:
            break
    driver.close()
    # Save data to a CSV file
    file_name = 'AmazoneScraper - {}.csv'.format(search_term)
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Description', 'Price', 'Rating', 'ReviewCount', 'Url', 'ImageUrl'])
        writer.writerows(records)


term = 'Friends'
main(term)
