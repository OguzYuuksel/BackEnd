from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen, Request
from urllib.parse import urlsplit, urlunsplit, quote
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import simplejson as json
import os
import sys

filename_migrosData                 = "data_Migros.json"
filename_migrosCategories           = "categories_Migros.json"
market_link_migros                  = "https://www.migros.com.tr"

filename_a101Data                   = "data_A101.json"
filename_a101Categories             = "categoryLinks_A101.json"
market_link_a101                    = "https://www.a101.com.tr"

filename_carrefoursaData            = "data_Carrefoursa.json"
filename_carrefoursaCategories      = "categoryLinks_Carrefoursa.json"
market_link_carrefoursa             = "https://www.carrefoursa.com"

filename_istegelsinData             = "data_Istegelsin.json"
filename_istegelsinCategories       = "categoryLinks_Istegelsin.json"
market_link_istegelsin              = "https://www.istegelsin.com"

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
    # scrolls down until end of a page
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

def write_file(filename, objects):    
    with open(filename, 'w', encoding='utf8') as json_file:
        for obj in objects:
            # convert dictionary object of python into JSON string data format
            #json_string = json.dumps(obj.__dict__, indent=4)
            # write json data into file
            print(toJSON(obj))
            json.dump(toJSON(obj), json_file)
    
        #print("Written %d bytes to %s" % (json_file.size(), json_file.fname()))

def toJSON(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

class Markets(Enum):
    MIGROS, A101, CARREFOURSA, ISTEGELSIN = range(4)

class Category(object):
    #__slots__ = ['link', 'name']
    
    def __init__(self, link, name):
        self.link = link
        self.name = name
    
    def __str__(self):
        return f'Category name is {self.name} and link is {self.link}'

    def __repr__(self):
        return f'Category(name={self.name}, link={self.link})'

class Product(object):
    #__slots__ = ['product_name', 'category_name', 'sale_price', 'list_price', 'product_link', 'image_link']
    
    def __init__(self, product_name, brand, category_name, sale_price, list_price, in_stock, product_link, image_link):
        self.product_name = product_name
        self.brand = brand
        self.category_name = category_name
        self.sale_price = sale_price
        self.list_price = list_price
        self.in_stock = in_stock
        self.product_link = product_link
        self.image_link = image_link

    def __str__(self):
        return f'Name: {self.product_name}, Brand: {self.brand}, category: {self.category_name}, SalePrice: {self.sale_price}, ListPrice: {self.list_price}, InStock: {self.in_stock}, Link: {self.product_link}, ImgLink: {self.image_link}'

class CategoryLinks():

    def __init__(self, market, link):
        self.__market = market
        self.__market_link = link
        self.category_data = []
        
    def get_links(self):
        start_time = time.time()
               
        request = Request(self.__market_link,None,headers)
        webpage = urlopen(request)
        # parses html into a soup data structure to traverse html as if it were a json data type.
        webpage_soup = soup(webpage.read(), "html.parser")
        webpage.close()

        if self.__market is Markets.MIGROS:
            self.__getMigrosCategoryLinks(webpage_soup, self.__market_link)
        elif self.__market is Markets.CARREFOURSA:
            self.__getCarrefoursaCategoryLinks(webpage_soup, self.__market_link)
        elif self.__market is Markets.A101:
            self.__getA101CategoryLinks(webpage_soup, self.__market_link)
        elif self.__market is Markets.ISTEGELSIN:
            self.__getIstegelsinCategoryLinks(webpage_soup, self.__market_link)
        else:
            print("No scrape function for market: ", self.__market.name)

        end_time = time.time() - start_time

        print("Scraping category links of %s is completed. Category Count: %d, ElapsedTime_sec: %f" %(self.__market.name, len(self.category_data), end_time))
        return self.category_data

    def __getMigrosCategoryLinks(self, webpage_soup, market_link):
        # finds each category from the store page
        categories_html = webpage_soup.find("ul", {"class": "header-menu-bar-list"}).findAll("li", {"class": "category-list-item category-title"})

        for category_html in categories_html:
            category_link = market_link + category_html.find('a',href=True)['href']
            category_name = category_html.text.strip()
            # add category obj to list for later use
            self.category_data.append(Category(link=category_link,name=category_name))

    def __getIstegelsinCategoryLinks(self, webpage_soup, market_link):
        # finds each category from the store page
        categories_html = webpage_soup.findAll("a", {"class": "v3-home-category-list-item"})

        for category_html in categories_html:
            category_link = market_link + category_html['href']
            # add category obj to list for later use
            self.category_data.append(Category(link=category_link,name="category_name"))

    def __getA101CategoryLinks(self, webpage_soup, market_link):
    
        # finds each category from the store page
        main_categories_html = webpage_soup.findAll("div", {"class": "submenu-dropdown"})
        for main_category_html in main_categories_html:
            try:
                sub_categories_html = main_category_html.find("div", {"class": "col-sm-10 submenu-items"}).findAll("ul", {"class": "list"})
                for sub_category_html in sub_categories_html:
                    categories_html = sub_category_html.findAll('a',href=True)
                    for index, category_html in enumerate(categories_html):
                        if(len(categories_html) != 1 and index == 0):
                            continue
                        else:
                            category_link = market_link + category_html['href']
                            # add category obj to list for later use
                            self.category_data.append(Category(link=category_link,name="category_name"))
            except:
                pass
   
    def __getCarrefoursaCategoryLinks(self, webpage_soup, market_link):
        # finds each main category from the store page
        main_categories_html = webpage_soup.findAll("ul", {"class": "dropdown-menu sub-menu s-menu-2"})

        for index, main_category_html in enumerate(main_categories_html):

            if index == len(main_category_html) - 1: # pass unwanted category
                continue
            else:
                category_html = main_category_html.find("li", {"class": ""})
                
                category_link = market_link + category_html.find('a',href=True)['href']
                category_name = category_html.span.span.text.strip()
                # add category obj to list for later use
                self.category_data.append(Category(link=category_link,name=category_name))

                while True:
                    category_html = category_html.find_next_sibling("li")
                    if category_html is None:
                        break
                    else:
                        category_link = market_link + category_html.find('a',href=True)['href']
                        category_name = category_html.span.span.text.strip()
                        # add category obj to list for later use
                        self.category_data.append(Category(link=category_link,name=category_name))

class DataScraper():

    def __init__(self, market, categories):
        self.__market = market
        self.__categories = categories
        self.product_data = []

    def scrape_data(self):

        start_time = time.time()

        if self.__market is Markets.MIGROS:
            self.__scrape_migros(self.__categories)
        elif self.__market is Markets.CARREFOURSA:
            self.__scrape_carrefoursa(self.__categories)
        elif self.__market is Markets.A101:
            self.__scrape_a101(self.__categories)
        elif self.__market is Markets.ISTEGELSIN:
            self.__scrape_istegelsin(self.__categories)
        else:
            print("Wrong market type!!!")

        end_time = (time.time() - start_time) / 60

        print("Scraping of %s data is completed. Product count: %d, ElapsedTime_mins: %f" %(self.__market.name, len(self.product_data), end_time))

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

    def __scrape_migros(self, categories): 
    
        for category in categories:
            page_count = 2
            starting_number = 1
            page_index = starting_number
            
            while page_index < page_count + starting_number:
                start = time.time()
                # opens the connection and downloads html page from url
                page_url = category.link + "?sayfa=" + str(page_index) 
                request = Request(page_url,None,headers)
                webpage = urlopen(request)

                # parses html into a soup data structure to traverse html
                # as if it were a json data type.
                webpage_soup = soup(webpage.read(), "html.parser")
                webpage.close()
                # find number of pages in the link at the beginning of iteration
                if(page_index == starting_number):
                    try:
                        page_count_raw = webpage_soup.findAll("li", {"class": "pag-next"})[0].find_previous_sibling('li').text.strip()
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
                # loops over each product and grabs attributes about each product
                for container in containers:

                    product_name = container.h5.a.text #product_name = container.find("a", {"class": "product-link"})['data-monitor-name']
                    brand = container.find("a", {"class": "product-link"})['data-monitor-brand']
                    category_name = category.name
                    sale_price = container.find("div", {"class": "price-tag"}).find("span", {"class": "value"}).text.strip()
                    try:
                        list_price = container.find("div", {"class": "campaign-tag"}).find("span", {"class": "value"}).text.strip()
                    except:
                        list_price = sale_price
                    product_link = container.h5.find('a',href=True)['href']
                    image_link = container.find("img", {"class": "product-card-image lozad"})['src']
                    
                    self.product_data.append(Product(product_name, brand, category_name, sale_price, list_price, False, product_link, image_link))

                page_index += 1

                end = time.time() - start
                print(page_url , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

    def __scrape_carrefoursa(self, categories): 
    
        for category in categories:
            page_count = 2
            starting_number = 1
            page_index = starting_number
            
            while page_index < page_count + starting_number:
                start = time.time()
                # opens the connection and downloads html page from url
                page_url = category.link + "?page=" + str(page_index) 
                request = Request(page_url,None,headers)
                webpage = urlopen(request)

                # parses html into a soup data structure to traverse html as if it were a json data type.
                webpage_soup = soup(webpage.read(), "html.parser")
                webpage.close()
                # find number of pages in the link at the beginning of iteration
                if(page_index == starting_number):
                    try:
                        page_count_raw = webpage_soup.find("ul", {"class": "pagination"}).findAll('a',href=True)[-2].text.strip()
                        # get number from strip
                        for char in page_count_raw.split():
                            if char.isdigit():
                                page_count = int(char)
                                break
                    except:
                        page_count = 1

                # finds each product from the store page
                containers = webpage_soup.findAll("li", {"class": "col-xs-6 col-sm-3 col-md-2 col-lg2"})
                product_count = len(containers)
                # loops over each product and grabs attributes about each product
                for container in containers:

                    if container.find("button", {"btn btn-default btn-block js-add-to-cart outOfStock"}):
                        in_stock = False
                    else:
                        in_stock = True

                    product_name = container.find("span", {"class": "item-name"}).text.strip()
                    #brand = container.find("a", {"class": "product-link"})['data-monitor-brand']
                    try:
                        unit = container.find("span", {"class": "productUnit"}).text.strip()
                    except:
                        unit = "adet"
                        print("Unit Problemzzz: ", product_name)
                    category_name = category.name
                    sale_price = container.find("span", {"class": "item-price"}).text.strip()
                    try:
                        list_price = container.find("span", {"class": "priceLineThrough"}).text.strip()
                    except:
                        list_price = sale_price
                    product_link = container.find("div", {"class": "product_click"}).find('a',href=True)['href']
                    image_link = container.find("span", {"class": "thumb"}).img['data-src']
                    
                    self.product_data.append(Product(product_name, "noInfo", category_name, sale_price, list_price, in_stock, product_link, image_link))

                page_index += 1

                end = time.time() - start
                print(page_url , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

    def __scrape_a101(self, categories):

        for category in categories:
            page_count = 2
            starting_number = 1
            page_index = starting_number
            
            while page_index < page_count + starting_number:
                start = time.time()
                # opens the connection and downloads html page from url
                page_url = category.link + "?page=" + str(page_index) 
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
                    
                    self.product_data.append(Product(product_name, "noInfo", "noInfo", sale_price, list_price, False, product_link, image_link))

                page_index += 1

                end = time.time() - start
                print(page_url , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

    def __scrape_istegelsin(self, categories):

        for category in categories:
            start = time.time()

            webpage_soup = self.__get_html_istegelsin(category.link)

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
                    
                self.product_data.append(Product(product_name, "noInfo", "noInfo", sale_price, list_price, False, product_link, image_link))

            end = time.time() - start
            print(category.link , "\tNumOfProduct: " , product_count , "\tElapsedTime_sec: " , end)

if __name__ == "__main__":

    if sys.argv[1] == "MIGROS":
        market = Markets.MIGROS
        market_link = market_link_migros
        filename_Data         = filename_migrosData
        filename_Categories   = filename_migrosCategories
    elif sys.argv[1] == "A101":
        market = Markets.A101
        market_link = market_link_a101
        filename_Data         = filename_a101Data
        filename_Categories   = filename_a101Categories
    elif sys.argv[1] == "ISTEGELSIN":
        market = Markets.ISTEGELSIN
        market_link = market_link_istegelsin
        filename_Data         = filename_istegelsinData
        filename_Categories   = filename_istegelsinCategories
    elif sys.argv[1] == "CARREFOURSA":
        market = Markets.CARREFOURSA
        market_link = market_link_carrefoursa
        filename_Data         = filename_carrefoursaData
        filename_Categories   = filename_carrefoursaCategories
    else:
        print("Unknown market: ", sys.argv[1])
        sys.exit()

    categories = CategoryLinks(market, market_link)
    categories.get_links()
    write_file(filename_Categories, categories.category_data)

    scraper = DataScraper(market, categories.category_data)
    scraper.scrape_data()
    write_file(filename_Data, scraper.product_data)