from selenium import webdriver
from threading import Thread
import re
import csv
import time

class MyThread(Thread):
    def __init__(self, threadID, name, ProductIndex, StoreLinkColumn, ReadDBName, WriteDBName, BrowserEmulator):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ProductIndex = ProductIndex
        self.StoreLinkColumn = StoreLinkColumn
        self.ReadDBName = ReadDBName
        self.WriteDBName = WriteDBName
        self.BrowserEmulator = BrowserEmulator

    def run(self):
        print("Starting " + self.name)
        getData(self.ProductIndex, self.StoreLinkColumn, self.ReadDBName, self.WriteDBName, self.BrowserEmulator)
        print("Exiting " + self.name)

def getData(ProductIndex, StoreLinkColumn, ReadDBName, WriteDBName, BrowserEmulator):  
    Link = ReadDBName[ProductIndex][StoreLinkColumn] # column = 2for migros row= ürün sırası # direk linki yazdır
    BrowserEmulator.get(Link)
    
    if StoreLinkColumn == MigrosLinkReadDB:
        GetPrice = BrowserEmulator.find_element_by_id("store-product-primary-price").text
        StoreProductName = BrowserEmulator.find_element_by_css_selector("h1[class*='seo title']").text
    elif StoreLinkColumn == CarrefoursaLinkReadDB:
        GetPrice = BrowserEmulator.find_element_by_xpath("//span[@class = 'item-price'][@itemprop = 'price']").text
        StoreProductName = BrowserEmulator.find_element_by_css_selector("li[class*='active']").text

    CommasRemovedFromPriceText = GetPrice.replace(',', '.')
    PriceDigits = re.findall(r"[-+]?\d*\.?\d+|\d+", CommasRemovedFromPriceText)
    CombinePriceDigits = ''.join(PriceDigits)
    WriteDBName[ProductIndex][3*StoreLinkColumn-4] = StoreProductName #Product name on store
    WriteDBName[ProductIndex][3*StoreLinkColumn-3] = CombinePriceDigits #price
    WriteDBName[ProductIndex][3*StoreLinkColumn-2] = Link #link 4. column

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
numOfMarkets = 2
numOfThreads = 4
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

browserEmulators = []
for Row in range(0, numOfThreads):
    browserEmulators.append(webdriver.Chrome(options=options))

#Thread yaratarak veri cekme
start_time = time.time()

for productIndex in range(0,TotalRow):
    OutputFile[productIndex][0] = InputFile[productIndex][0] #ProductID  0. column
    OutputFile[productIndex][1] = InputFile[productIndex][1] #ProductName 1. column
    for marketIndex in range(2,numOfMarkets+2):
        if InputFile[productIndex][marketIndex] != '0':
            # numOfThreads'den az sayida aktif thread varsa yenisi yaratilir.
            # Thread'e beslenecek olan browser ise thread ile iliskili browser olmalidir. Thread1-Browser1 Thread2-Browser2 gibi.
            # Cunku browser sayisi kadar thread olmalidir.

            # thread = MyThread(cnt,"Thread-" + str(cnt), productIndex, marketIndex, InputFile, OutputFile)
            # thread.start()
            alper = 1
    
end_time= time.time() - start_time
   
print(OutputFile)

print(end_time)
#Print = pd.DataFrame(OutputFile)
#Print.columns = ["Index","Product Name","Migros Product Name","URL"]
#Print.to_csv("Enflasyon.csv")