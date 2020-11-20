from selenium import webdriver
from threading import Thread
from multiprocessing import Process
import re
import csv
import time

def migros(StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
    BrowserEmulator = webdriver.Chrome(options=options)
    for Row in range(0,TotalRow):
        WriteDBName[Row][0] = ReadDBName[Row][0] #ProductID  0. column
        WriteDBName[Row][1] = ReadDBName[Row][1] #ProductName 1. column
        if ReadDBName[Row][MigrosLinkReadDB] != '0':
            Link = ReadDBName[Row][StoreLinkColumn] # column = 2for migros row= ürün sırası # direk linki yazdır
            BrowserEmulator.get(Link)
            GetPrice = BrowserEmulator.find_element_by_id("store-product-primary-price").text
            CommasRemovedFromPriceText = GetPrice.replace(',', '.')
            PriceDigits = re.findall(r"[-+]?\d*\.?\d+|\d+", CommasRemovedFromPriceText)
            CombinePriceDigits = ''.join(PriceDigits)
            StoreProductName = BrowserEmulator.find_element_by_css_selector("h1[class*='seo title']").text
            WriteDBName[Row][3*StoreLinkColumn-4] = StoreProductName #Product name on store
            WriteDBName[Row][3*StoreLinkColumn-3] = CombinePriceDigits #price
            WriteDBName[Row][3*StoreLinkColumn-2] = Link #link 4. column
    BrowserEmulator.quit()

def carrefoursa(StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
    BrowserEmulator = webdriver.Chrome(options=options)
    for Row in range(0, TotalRow):
        WriteDBName[Row][0] = ReadDBName[Row][0]  # ProductID  0. column
        WriteDBName[Row][1] = ReadDBName[Row][1]  # ProductName 1. column
        if ReadDBName[Row][CarrefoursaLinkReadDB] != '0':
            Link = ReadDBName[Row][StoreLinkColumn]  # column = 3for carrefoursa row= ürün sırası # direk linki yazdır
            BrowserEmulator.get(Link)
            GetPrice = BrowserEmulator.find_element_by_xpath("//span[@class = 'item-price'][@itemprop = 'price']").text
            CommasRemovedFromPriceText = GetPrice.replace(',', '.')
            PriceDigits = re.findall(r"[-+]?\d*\.?\d+|\d+", CommasRemovedFromPriceText)
            CombinePriceDigits = ''.join(PriceDigits)
            StoreProductName = BrowserEmulator.find_element_by_css_selector("li[class*='active']").text
            WriteDBName[Row][3*StoreLinkColumn-4] = StoreProductName  # Product name on store
            WriteDBName[Row][3*StoreLinkColumn-3] = CombinePriceDigits  # price
            WriteDBName[Row][3*StoreLinkColumn-2] = Link  # link 4. column
    BrowserEmulator.quit()

# URL/Product Database Upload
with open('links.csv', newline='', encoding='utf-8') as csvfile:
    InputFile = list(csv.reader(csvfile))
##########

# Define Store's Links Location in ReadDB
NumOfMarkets = 2
NumOfThreads = 4
##########

##########Create array from Uploaded Database
TotalColumn = 7 # WriteDB ne kadarda bir tekrarlıyor 0-4 / 1-5 adet (0 1 base (2-3-4), (5-6-7) store)
TotalRow = int(len(InputFile))
OutputFile = [[0] * (TotalColumn+1) for Row in range(TotalRow)] #Output CSV'mizi oluşturacak array
##########

##########Chrome için görüntü yüklenmesini engelliyor, sayfa daha hızlı yüklensin diye
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("incognito")
options.add_argument("disable-extensions")
options.add_argument("disable-popup-blocking")
options.add_argument('--ignore-certificate-errors')
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

#Thread yaratarak veri cekme
start_time = time.time()

thread1 = Process(target=migros(MigrosLinkReadDB, InputFile, OutputFile, TotalRow))
thread2 = Process(target=carrefoursa(CarrefoursaLinkReadDB, InputFile, OutputFile, TotalRow))

thread1.start()
thread2.start()
thread1.join()
thread2.join()
    
end_time= time.time() - start_time
   
print(OutputFile)

print(end_time)
#Print = pd.DataFrame(OutputFile)
#Print.columns = ["Index","Product Name","Migros Product Name","URL"]
#Print.to_csv("Enflasyon.csv")