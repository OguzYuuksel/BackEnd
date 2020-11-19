from selenium import webdriver
from threading import Thread
import re
import csv
import time


class Migros(Thread):
    def __init__(self, threadID, name, StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.StoreLinkColumn = StoreLinkColumn
        self.ReadDBName = ReadDBName
        self.WriteDBName = WriteDBName
        self.TotalRow = TotalRow

    def run(self):
        print("Starting " + self.name)
        migros(self.StoreLinkColumn, self.ReadDBName, self.WriteDBName, self.TotalRow)
        print("Exiting " + self.name)


def migros(StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
    BrowserEmulator = webdriver.Chrome(chrome_options=options)
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

class Carrefoursa(Thread):
    def __init__(self, threadID, name, StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.StoreLinkColumn = StoreLinkColumn
        self.ReadDBName = ReadDBName
        self.WriteDBName = WriteDBName
        self.TotalRow = TotalRow

    def run(self):
        print ("Starting " + self.name)
        carrefoursa(self.StoreLinkColumn, self.ReadDBName, self.WriteDBName, self.TotalRow)
        print ("Exiting " + self.name)

def carrefoursa(StoreLinkColumn, ReadDBName, WriteDBName, TotalRow):
    BrowserEmulator = webdriver.Chrome(chrome_options=options)
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
MigrosLinkReadDB = 2 #2 for migros
CarrefoursaLinkReadDB = 3 #2 for migros
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
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
##########

start_time = time.time()



thread1 = Migros(1,"Thread-Mig", MigrosLinkReadDB, InputFile, OutputFile, TotalRow)
thread2 = Carrefoursa(2,"Thread-Car", CarrefoursaLinkReadDB, InputFile, OutputFile, TotalRow)

thread1.start()
thread2.start()
thread1.join()
thread2.join()

#if InputFile[GetLinkRow][MigrosLinkReadDB] != '0':
    
#if InputFile[GetLinkRow][CarrefoursaLinkReadDB] != '0':        
end_time= time.time() - start_time
   
print(OutputFile)

print(end_time)
#Print = pd.DataFrame(OutputFile)
#Print.columns = ["Index","Product Name","Migros Product Name","URL"]
#Print.to_csv("Enflasyon.csv")
