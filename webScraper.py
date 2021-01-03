from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen, Request
import time
import csv
import os

tot_product_number = 0

out_filename = "migros_raw.csv"

# urlRequest setting in order to avoid webpage errors
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent,}

migros_category_links = []

class CSVWriter():

    filename = None
    fp = None
    writer = None

    def __init__(self, filename):
        self.filename = filename
        self.fp = open(self.filename, 'w', encoding='utf8')
        self.writer = csv.writer(self.fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')

    def close(self):
        self.fp.close()

    def write(self, elems):
        self.writer.writerow(elems)

    def size(self):
        return os.path.getsize(self.filename)

    def fname(self):
        return self.filename

def getMigrosCategoryLinks():

    request = Request("https://www.migros.com.tr/",None,headers)
    webpage = urlopen(request)

    # parses html into a soup data structure to traverse html
    # as if it were a json data type.
    webpage_soup = soup(webpage.read(), "html.parser")
    webpage.close()

    # finds each category from the store page
    containers = webpage_soup.find("ul", {"class": "header-menu-bar-list"}).findAll("li", {"class": "category-list-item category-title"})
    print("Number of Migros Categories: ", len(containers) )

    for container in containers:
        category_link = "https://www.migros.com.tr" + container.find('a',href=True)['href'] + "?sayfa="
        migros_category_links.append(category_link)
        print(migros_category_links[-1])

def scrapeLinkData(url): 

    global tot_product_number
    category_product_number = 0
    page_number = 2
    starting_number = 1
    page_index = starting_number
    while page_index < page_number + starting_number:
        start = time.time()
        # opens the connection and downloads html page from url
        page_url = url + str(page_index) 
        request = Request(page_url,None,headers)
        webpage = urlopen(request)

        # parses html into a soup data structure to traverse html
        # as if it were a json data type.
        webpage_soup = soup(webpage.read(), "html.parser")
        webpage.close()
        # find number of pages in the link at the beginning of iteration
        if(page_index == 1):
            try:
                page_number_raw = webpage_soup.findAll("li", {"class": "pag-next"})[0].find_previous_sibling('li').text
                # get number from strip
                for char in page_number_raw.split():
                    if char.isdigit():
                        page_number = int(char)
                        break
            except:
                page_number = 1

        # finds each product from the store page
        containers = webpage_soup.findAll("div", {"class": "list"})
        product_number = len(containers)
        category_product_number += product_number
        # loops over each product and grabs attributes about
        # each product
        for container in containers:
        
            product_name1 = container.h5.a.text
            product_name = container.find("a", {"class": "product-link"})['data-monitor-name']
            brand = container.find("a", {"class": "product-link"})['data-monitor-brand']
            category = container.find("a", {"class": "product-link"})['data-monitor-category']
            price_tag = container.find("div", {"class": "price-tag"}).find("span", {"class": "value"}).text.strip()
            try:
                campaign_tag = container.find("div", {"class": "campaing-tag"}).find("span", {"class": "value"}).text.strip()
            except:
                campaign_tag = price_tag
            product_link = container.h5.find('a',href=True)['href']
            image_link = container.find("img", {"class": "product-card-image lozad"})['src']

            # writes the dataset to file          
            csv_file.write((product_name1, product_name, brand, price_tag, campaign_tag, category, product_link, image_link))

        page_index += 1
        end = time.time() - start
        print(page_url + "\tNumOfProduct: " + str(product_number) + "\tElapsedTime_sec: " + str(end))
    tot_product_number += category_product_number
    print("Number of Products Per Category: " + str(category_product_number) )

# opens file
csv_file = CSVWriter(out_filename)

start_time= time.time()

getMigrosCategoryLinks()

for link in migros_category_links:
    scrapeLinkData(link)

end_time= time.time()

csv_file.close()  # Close the file

print("Total Number of Products: " + str(tot_product_number))
print("Elapsed time in Min: " + str( (end_time - start_time) / 60) )
print("Written %d bytes to %s" % (csv_file.size(), csv_file.fname()))