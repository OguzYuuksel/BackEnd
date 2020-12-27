from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen, Request
import time

tot_product_number = 0

def scrapeLinkDatas(url):

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
            
            # prints the dataset to console
            # print("Marka: " + brand + "\tUrun_Ismi: " + product_name + "\tFiyat: " + price_tag + "\tcategory: " + category + "\n")

            # writes the dataset to file
        page_index += 1
        end = time.time() - start
        print(page_url + "\tNumOfProduct: " + str(product_number) + "\tElapsedTime_sec: " + str(end))
    tot_product_number += category_product_number
    print("Number of Products Per Category: " + str(category_product_number) )

# URl to web scrap from.
# in this example we web scrap graphics cards from Newegg.com
category_links = [  "https://www.migros.com.tr/meyve-c-65?sayfa=",
                    "https://www.migros.com.tr/meyve-c-66?sayfa=",
                    "https://www.migros.com.tr/yetistirme-kiti-c-118b1?sayfa=",
                    "https://www.migros.com.tr/kirmizi-et-c-68?sayfa=",
                    "https://www.migros.com.tr/beyaz-et-c-69?sayfa=",                   
                    "https://www.migros.com.tr/balik-deniz-urunleri-c-6a?sayfa=",
                    "https://www.migros.com.tr/et-sarkuteri-c-6b?sayfa=",
                    "https://www.migros.com.tr/sut-c-6c?sayfa=",
                    "https://www.migros.com.tr/peynir-c-6d?sayfa=",
                    "https://www.migros.com.tr/yogurt-c-6e?sayfa=",
                    "https://www.migros.com.tr/tereyagi-c-413?sayfa=",
                    "https://www.migros.com.tr/margarin-c-414?sayfa=",
                    "https://www.migros.com.tr/yumurta-c-70?sayfa=",
                    "https://www.migros.com.tr/zeytin-c-71?sayfa=",
                    "https://www.migros.com.tr/dondurma-c-41b?sayfa=",
                    "https://www.migros.com.tr/sutlu-tatli-krema-c-72?sayfa=",
                    "https://www.migros.com.tr/kahvaltiliklar-c-73?sayfa=",
                    "https://www.migros.com.tr/yilbasi-sepeti-c-11328?sayfa=",
                    "https://www.migros.com.tr/makarna-c-425?sayfa=",
                    "https://www.migros.com.tr/bakliyat-c-428?sayfa=",
                    "https://www.migros.com.tr/sivi-yag-c-76?sayfa=",
                    "https://www.migros.com.tr/tuz-baharat-harc-c-77?sayfa=",
                    "https://www.migros.com.tr/corba-ve-bulyonlar-c-75?sayfa=",
                    "https://www.migros.com.tr/atistirmalik-c-113fb?sayfa=",
                    "https://www.migros.com.tr/meze-hazir-yemek-c-7d?sayfa=",
                    "https://www.migros.com.tr/konserve-c-452?sayfa=",
                    "https://www.migros.com.tr/sos-c-113fc?sayfa=",
                    "https://www.migros.com.tr/un-c-45f?sayfa=",
                    "https://www.migros.com.tr/seker-c-ac?sayfa=",
                    "https://www.migros.com.tr/dondurulmus-gida-c-7c?sayfa=",
                    "https://www.migros.com.tr/unlu-mamul-tatli-c-7e?sayfa=",
                    "https://www.migros.com.tr/saglikli-yasam-urunleri-c-7f?sayfa=",
                    "https://www.migros.com.tr/gazli-icecek-c-80?sayfa=",
                    "https://www.migros.com.tr/gazsiz-icecek-c-81?sayfa=",
                    "https://www.migros.com.tr/cay-c-475?sayfa=",
                    "https://www.migros.com.tr/kahve-c-476?sayfa=",
                    "https://www.migros.com.tr/su-c-84?sayfa=",
                    "https://www.migros.com.tr/maden-suyu-c-85?sayfa=",
                    "https://www.migros.com.tr/camasir-yikama-c-86?sayfa=",
                    "https://www.migros.com.tr/bulasik-yikama-c-87?sayfa=",
                    "https://www.migros.com.tr/genel-temizlik-c-88?sayfa=",
                    "https://www.migros.com.tr/temizlik-malzemeleri-c-89?sayfa=",
                    "https://www.migros.com.tr/banyo-gerecleri-c-8b?sayfa=",
                    "https://www.migros.com.tr/camasir-gerecleri-c-8a?sayfa=",
                    "https://www.migros.com.tr/cop-poseti-c-11359?sayfa=",
                    "https://www.migros.com.tr/kagit-urunleri-c-8d?sayfa=",
                    "https://www.migros.com.tr/hijyenik-ped-c-96?sayfa=",
                    "https://www.migros.com.tr/agiz-bakim-urunleri-c-8e?sayfa=",
                    "https://www.migros.com.tr/sac-bakim-c-8f?sayfa=",
                    "https://www.migros.com.tr/dus-banyo-sabun-c-92?sayfa=",
                    "https://www.migros.com.tr/tiras-malzemeleri-c-90?sayfa=",
                    "https://www.migros.com.tr/agda-epilasyon-c-91?sayfa=",
                    "https://www.migros.com.tr/cilt-bakimi-c-93?sayfa=",
                    "https://www.migros.com.tr/kolonya-c-4cf?sayfa=",
                    "https://www.migros.com.tr/parfum-deodorant-c-97?sayfa=",
                    "https://www.migros.com.tr/makyaj-c-95?sayfa=",
                    "https://www.migros.com.tr/saglik-urunleri-c-98?sayfa=",
                    "https://www.migros.com.tr/bebek-tekstil-c-4e1?sayfa=",
                    "https://www.migros.com.tr/anne-urunleri-c-9a?sayfa=",
                    "https://www.migros.com.tr/oyuncak-c-9e?sayfa=",
                    "https://www.migros.com.tr/mutfak-esyalari-c-9f?sayfa=",
                    "https://www.migros.com.tr/dekorasyon-c-a4?sayfa=",
                    "https://www.migros.com.tr/bahce-malzemeleri-c-a2?sayfa=",
                    "https://www.migros.com.tr/spor-outdoor-c-11403?sayfa=",
                    "https://www.migros.com.tr/kirtasiye-c-11420?sayfa=",
                    "https://www.migros.com.tr/kitap-dergi-c-a5?sayfa=",
                    "https://www.migros.com.tr/ev-tekstili-c-50b?sayfa=",
                    "https://www.migros.com.tr/giyim-c-508?sayfa=",
                    "https://www.migros.com.tr/petshop-c-a0?sayfa=",
                    "https://www.migros.com.tr/pil-c-2ad2?sayfa=",
                    "https://www.migros.com.tr/ampul-c-2ac8?sayfa=",
                    "https://www.migros.com.tr/hirdavat-c-500?sayfa=",
                    "https://www.migros.com.tr/oto-aksesuar-c-4ff?sayfa=",
                    "https://www.migros.com.tr/altin-c-1118a?sayfa=",
                    "https://www.migros.com.tr/firsatlar-dunyasi-c-113d6?sayfa=",
                    "https://www.migros.com.tr/bebek-bezi-c-ab?sayfa=",
                    "https://www.migros.com.tr/bebek-bakim-c-4d8?sayfa=",
                    "https://www.migros.com.tr/bebek-beslenme-c-4e4?sayfa=",
                    "https://www.migros.com.tr/bebek-banyo-c-4d7?sayfa=",
                    "https://www.migros.com.tr/bebek-deterjani-ve-yumusaticisi-c-297b?sayfa="]

# urlRequest setting in order to avoid webpage errors
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent,}

# opens file, and writes headers
out_filename = "graphics_cards.csv"
f = open(out_filename, "w")
f.write("product_name,brand,category,price_tag,campaign_tag,product_link \n")
start_time= time.time()

for link in category_links:
    scrapeLinkDatas(link)

end_time= time.time()
print("Total Number of Products: " + str(tot_product_number))
print("Elapsed time in Min: " + str( (end_time - start_time) / 60) )
f.close()  # Close the file