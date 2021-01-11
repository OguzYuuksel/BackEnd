from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen, Request
from urllib.parse import urlsplit, urlunsplit, quote
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import os
import sys

filename_migrosRawData = "rawData_Migros.csv"
filename_migrosCategoryLinks = "categoryLinks_Migros.csv"
filename_a101RawData = "rawData_A101.csv"
filename_a101CategoryLinks = "categoryLinks_A101.csv"
filename_carrefoursaRawData = "rawData_Carrefoursa.csv"
filename_carrefoursaCategoryLinks = "categoryLinks_Carrefoursa.csv"

# urlRequest setting in order to avoid webpage errors
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent':user_agent,}

options = webdriver.ChromeOptions()
#options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("incognito")
options.add_argument("disable-extensions")
options.add_argument("disable-popup-blocking")
options.add_argument('--ignore-certificate-errors')

def fix_link(url):
    url = urlsplit(url)
    url = list(url)
    url[2] = quote(url[2])
    url = urlunsplit(url)
    return url

def scroll_page(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

class Markets(Enum):
    MIGROS, A101, CARREFOURSA, ISTEGELSIN = range(4)

class CategoryLinks():

    def __init__(self, market):
        self.market = market
        self.__market_link = None
        self.category_links = []
        
    def get_links(self):
        start_time = time.time()

        if self.market is Markets.MIGROS:
            self.__market_link = "https://www.migros.com.tr"
        elif self.market is Markets.A101:
            self.__market_link = "https://www.a101.com.tr"
        elif self.market is Markets.CARREFOURSA:
            self.__market_link = "https://www.carrefoursa.com"
        elif self.market is Markets.ISTEGELSIN:
            self.__market_link = "https://www.istegelsin.com"

        request = Request(self.__market_link,None,headers)
        webpage = urlopen(request)
        # parses html into a soup data structure to traverse html as if it were a json data type.
        webpage_soup = soup(webpage.read(), "html.parser")
        webpage.close()

        if self.market is Markets.MIGROS:
            self.__getMigrosCategoryLinks(webpage_soup, self.__market_link)
        elif self.market is Markets.A101:
            self.__getA101CategoryLinks(webpage_soup, self.__market_link)
        elif self.market is Markets.ISTEGELSIN:
            self.__getIstegelsinCategoryLinks(webpage_soup, self.__market_link)
        elif self.market is Markets.CARREFOURSA:
            self.__getCarrefoursaCategoryLinks(webpage_soup, self.__market_link)
        else:
            print("No scrape function for market: ", self.market.name)

        end_time = time.time() - start_time

        print("Scraping category links of %s is completed. Category Count: %d, ElapsedTime_sec: %f" %(self.market.name, len(self.category_links), end_time))
        return self.category_links

    def __getMigrosCategoryLinks(self, webpage_soup, market_link):

        # finds each category from the store page
        categories = webpage_soup.find("ul", {"class": "header-menu-bar-list"}).findAll("li", {"class": "category-list-item category-title"})

        for category in categories:
            self.category_links.append(market_link + category.find('a',href=True)['href'])
            print(self.category_links[-1])

    def __getIstegelsinCategoryLinks(self, webpage_soup, market_link):

        # finds each category from the store page
        categories = webpage_soup.findAll("a", {"class": "v3-home-category-list-item"})

        for category in categories:
            self.category_links.append(market_link + category['href'])
            print(self.category_links[-1])

    def __getA101CategoryLinks(self, webpage_soup, market_link):
    
        # finds each category from the store page
        main_categories = webpage_soup.findAll("div", {"class": "submenu-dropdown"})
        for main_category in main_categories:
            try:
                sub_categories = main_category.find("div", {"class": "col-sm-10 submenu-items"}).findAll("ul", {"class": "list"})
                for sub_category in sub_categories:
                    categories = sub_category.findAll('a',href=True)
                    for index, category in enumerate(categories):
                        if(len(categories) != 1 and index == 0):
                            continue
                        else:
                            self.category_links.append(market_link + category['href'])
                            print(self.category_links[-1])
            except:
                pass
   
    def __getCarrefoursaCategoryLinks(self, webpage_soup, market_link):
        # finds each main category from the store page
        main_categories = webpage_soup.findAll("ul", {"class": "dropdown-menu sub-menu s-menu-2"})

        for index, main_category in enumerate(main_categories):

            if index == len(main_categories) - 1: # pass unwanted category
                continue
            else:
                category = main_category.find("li", {"class": ""})
                self.category_links.append(market_link + category.find('a',href=True)['href'])
                print(self.category_links[-1])
                print(category.span.span.text.strip())
                while True:
                    category = category.find_next_sibling("li")
                    if category is None:
                        break
                    else:
                        self.category_links.append(market_link + category.find('a',href=True)['href'])
                        print(self.category_links[-1])
                        print(category.span.span.text.strip())

class DataScraper():

    def __init__(self, market, category_links):
        self.market = market
        self.category_links = category_links
        self.total_product_count = 0

    def scrape_data(self):
        
        #csv_file = CSVWriter(filename_migrosRawData) # opens file

        start_time = time.time()

        if self.market is Markets.MIGROS:
            self.__scrape_migros(self.category_links)
        elif self.market is Markets.A101:
            self.__scrape_a101(self.category_links)
        elif self.market is Markets.ISTEGELSIN:
            self.__scrape_istegelsin(self.category_links)
        else:
            print("Wrong market type!!!")

        end_time = (time.time() - start_time) / 60

        #csv_file.close()  # Close the file
        #print("Written %d bytes to %s" % (csv_file.size(), csv_file.fname()))

        print("Scraping of %s data is completed. Product count: %d, ElapsedTime_mins: %f" %(self.market.name, self.total_product_count, end_time))

    def __get_html_istegelsin(self, category_link):

        driver = webdriver.Chrome(options=options)           
        # implicitly_wait tells the driver to wait before throwing an exception
        driver.implicitly_wait(30)
        # converts an IRI(non-ascii) to a plain ASCII URI:
        category_link = fix_link(category_link)
        # driver.get(url) opens the page
        driver.get(category_link)
        # clicks "Tum Urunler" button
        driver.find_elements_by_xpath("//label[@for='all']")[0].click()
        time.sleep(15)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(5)
        # This starts the scrolling by passing the driver and a timeout
        scroll_page(driver, 5)

        # parses html into a soup data structure to traverse html as if it were a json data type.
        webpage_soup = soup(driver.page_source, "html.parser")
        driver.quit()

        return webpage_soup

    def __scrape_migros(self, category_links): 
    
        for category_link in category_links:
            page_count = 2
            starting_number = 1
            page_index = starting_number
            
            while page_index < page_count + starting_number:
                start = time.time()
                # opens the connection and downloads html page from url
                page_url = category_link + "?sayfa=" + str(page_index) 
                request = Request(page_url,None,headers)
                webpage = urlopen(request)

                # parses html into a soup data structure to traverse html
                # as if it were a json data type.
                webpage_soup = soup(webpage.read(), "html.parser")
                webpage.close()
                # find number of pages in the link at the beginning of iteration
                if(page_index == starting_number):
                    try:
                        page_count_raw = webpage_soup.findAll("li", {"class": "pag-next"})[0].find_previous_sibling('li').text
                        # get number from strip
                        for char in page_count_raw.split():
                            if char.isdigit():
                                page_count = int(char)
                                break
                    except:
                        page_count = 1

                # finds each product from the store page
                containers = webpage_soup.findAll("div", {"class": "list"})
                product_count = len(containers)
                # loops over each product and grabs attributes about
                # each product
                for container in containers:

                    product_name1 = container.h5.a.text
                    product_name = container.find("a", {"class": "product-link"})['data-monitor-name']
                    brand = container.find("a", {"class": "product-link"})['data-monitor-brand']
                    category = container.find("a", {"class": "product-link"})['data-monitor-category']
                    sale_price = container.find("div", {"class": "price-tag"}).find("span", {"class": "value"}).text.strip()
                    try:
                        list_price = container.find("div", {"class": "campaign-tag"}).find("span", {"class": "value"}).text.strip()
                    except:
                        list_price = sale_price
                    product_link = container.h5.find('a',href=True)['href']
                    image_link = container.find("img", {"class": "product-card-image lozad"})['src']
                    # writes the dataset to file          
                    #csv_file.write((product_name1, product_name, brand, list_price, sale_price, category, product_link, image_link))

                page_index += 1
                self.total_product_count += product_count

                end = time.time() - start
                print(page_url , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

    def __scrape_a101(self, category_links):

        for category_link in category_links:
            page_count = 2
            starting_number = 1
            page_index = starting_number
            
            while page_index < page_count + starting_number:
                start = time.time()
                # opens the connection and downloads html page from url
                page_url = category_link + "?page=" + str(page_index) 
                request = Request(page_url,None,headers)
                webpage = urlopen(request)

                # parses html into a soup data structure to traverse html as if it were a json data type.
                webpage_soup = soup(webpage.read(), "html.parser")
                webpage.close()
                # find number of pages in the link at the beginning of iteration
                if(page_index == starting_number):
                    try:
                        page_count = int(webpage_soup.findAll("li", {"class": "page-item"})[-2].find("a", {"class": "page-link js-pagination"}).text.strip())
                    except:
                        page_count = 1

                # finds each product from the store page
                containers = webpage_soup.findAll("div", {"class": "col-md-4 col-sm-6 col-xs-6 set-product-item"})
                product_count = len(containers)
                # loops over each product and grabs attributes about each product
                for container in containers:
                
                    product_name = container.find("a", {"class": "name-price"})['title']
                    sale_price = container.find("span", {"class": "current"}).text.strip()
                    try:
                        list_price = container.find("span", {"class": "old"}).text.strip()
                    except:
                        list_price = sale_price
                    product_link = container.find('a',href=True)['href']
                    image_link = container.find("div", {"class": "product-image"}).img['src'] # ayrica 'src' denenebilir

                    # writes the dataset to file          
                    #csv_file.write((product_name1, product_name, brand, price_tag, campaign_tag, category, product_link, image_link))

                page_index += 1
                self.total_product_count += product_count

                end = time.time() - start
                print(page_url , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

    def __scrape_istegelsin(self, category_links):

        for category_link in category_links:
            start = time.time()

            webpage_soup = self.__get_html_istegelsin(category_link)

            # finds each product from the store page
            containers = webpage_soup.findAll("div", {"class": "v3-global-product-item"})
            product_count = len(containers)
            # loops over each product and grabs attributes about each product
            for container in containers:
            
                product_name = container.find("span", {"class": "product-name"}).text
                sale_price = container.find("span", {"class": "discountless-price"}).text.strip()
                try:
                    list_price = container.find("span", {"class": "discounted-price"}).text.strip()
                except:
                    list_price = sale_price
                product_link = container.find('a',href=True)['href']
                image_link = container.find("img", {"class": "ineligible"})['src'] # ayrica 'src' denenebilir

                #print(product_name, sale_price, list_price, product_link, image_link)
                # writes the dataset to file          
                #csv_file.write((product_name1, product_name, brand, price_tag, campaign_tag, category, product_link, image_link))

            self.total_product_count += product_count

            end = time.time() - start
            print(category_link , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

if __name__ == "__main__":

    if sys.argv[1] == "MIGROS":
        market = Markets.MIGROS
    elif sys.argv[1] == "A101":
        market = Markets.A101
    elif sys.argv[1] == "ISTEGELSIN":
        market = Markets.ISTEGELSIN
    elif sys.argv[1] == "CARREFOURSA":
        market = Markets.CARREFOURSA
    else:
        print("Unknown market: ", sys.argv[1])
        sys.exit()

    category = CategoryLinks(market)
    category.get_links()

    scraper = DataScraper(market, category.category_links)
    scraper.scrape_data()