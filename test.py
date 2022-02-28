import model
import csv
import os

import requests as req
import bs4
import json
from selenium import webdriver
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager

import warnings
warnings.filterwarnings("ignore")


# %%%%%%%%%%%%%%% HealthPost Website Scraper %%%%%%%%%%%%%%%%%%%%

# Healthpost website class
class HEALTHPOST:
    # Intialize margin, ship and ebay fee (for repricing)
    def __init__(self,url,margin,ship,ebay) -> None:
        self.url=url
        self.margin_fee=margin
        self.ship_fee=ship
        self.ebay_fee=ebay

    # Function use to scrape product pages for healthpost
    def extract_page(self,url):
        raw_page=req.get(url)
        page=bs4.BeautifulSoup(raw_page.content,'lxml')
        return page

    # Preprocess healtpost data to extract specific data from product page
    def preprocess_healtpost(self,page):
        brand=page.find("h2",attrs={'class':'productView-brand'}).text.strip()
        title=page.find("h1",attrs={'class':'productView-title'}).text.strip()
        price=page.find("div",attrs={'class':'our-price-container price-item'}).find("span",attrs={'class':'price'}).text.split('$')[1].strip()
        product_img=page.find("div",attrs={'class':'productView-img-container'}).a['href']
        # des=page.find("div",attrs={'class':'product-description'}).text.strip()
        des=page.find("div",attrs={'class':'product-description'})
        e_des=page.find("div",attrs={'class':'product-description'}).find('p')

        json_data=''
        for i in page.find_all('script'):
            if 'BCData' in i.text:
                json_data=i
                break

        d1=json.loads(json_data.text.split('=')[1].strip().replace(';',''))
        stock=d1['product_attributes']['instock']
        sku=d1['product_attributes']['sku']
        upc=d1['product_attributes']['upc']
        # ean=d1['product_attributes']['ean']
        if stock==True:
            stock=4
        else:
            stock=0

        dic1={'Brand':brand,"Product Image":product_img,"Title":title,"OldPrice":price,'Description':des,'Stock':stock,'Sku':sku,"upc":upc}
        return dic1
    
    # Reprice function to calculate new price of product using different parameters
    def reprice(self,data,margin,ship,ebay_fee):
        n_price=(float(data['OldPrice'])+((margin/100)*float(data['OldPrice']))+ship+0.33)/(1-(ebay_fee/100))
        data['NewPrice']=round(n_price,2)
        return data
    
    # Function to run healthpost script
    def run_healthpost(self):
        page=self.extract_page(self.url)
        data=self.preprocess_healtpost(page)
        data=self.reprice(data,self.margin_fee,self.ship_fee,self.ebay_fee)
        return data


# %%%%%%%%%%%%%%% Iherb Website Scraper %%%%%%%%%%%%%%%%%%%%

# Iherb website class
class IHERB:
    # Intialize url, margin, ship and ebay fee (for repricing)
    def __init__(self,url,margin,ship,ebay) -> None:
        self.url=url
        self.margin_fee=margin
        self.ship_fee=ship
        self.ebay_fee=ebay

    # Function use to scrape product pages for iherb
    def extract_page(self,url):
        raw_page=req.get(url)
        page=bs4.BeautifulSoup(raw_page.content,'lxml')
        return page

    # Preprocess iherb data to extract specific data from product page
    def preprocess_iherb(self,page):
        title=page.find('div',attrs={'class':'product-summary-title'}).text.strip()
        brand=page.find('div',attrs={'id':'brand'}).find('a').text.strip()
        product_img=page.find("div",attrs={'id':'product-image'}).a['href']
        price=page.find('div',attrs={'id':'price'}).text.split('$')[1].strip()
        des=page.find('section',attrs={'class':'column fluid product-description-specifications'}).text.strip()
        stock=page.find('div',attrs={'id':'stock-status'}).text.strip()
        e_des=page.find('section',attrs={'class':'column fluid product-description-specifications'})
        
        spec=page.find('ul',attrs={'id':'product-specs-list'}).find_all('li')
        sku,upc='',''
        for i in spec:
            if "Product code" in i.text:
                sku=i.find('span').text
            elif "UPC Code" in i.text:
                upc=i.find('span').text

        print("Title : ",title,"\nBrand : ",brand,"\nPrice : ",price,"\nStock : ",stock,"\nSKU : ",sku,"\nUPC : ",upc,"\nDescription : ",des)
        dic1={'Brand':brand,"Product Image":product_img,"Title":title,"OldPrice":price,'Description':des,'Stock':stock,'Sku':sku,"upc":upc}

        return dic1

    # Reprice function to calculate new price of product using different parameters
    def reprice(self,data,margin,ship,ebay_fee):
        n_price=(float(data['OldPrice'])+((margin/100)*float(data['OldPrice']))+ship+0.33)/(1-(ebay_fee/100))
        data['NewPrice']=round(n_price,2)
        return data

    # Function to run iherb script
    def run_iherb(self):
        page=self.extract_page(self.url)
        data=self.preprocess_iherb(page)
        data=self.reprice(data,self.margin_fee,self.ship_fee,self.ebay_fee)
        return data


# %%%%%%%%%%%%%%%%% FieldFolio Website Scraper %%%%%%%%%%%%%%%%%%%

# Fieldfolio website class
class FIELDFOLIO:
    # Intialize chrome driver for scraping
    def __init__(self,sku,cat_url,margin,ship,ebay):
        self.sku=sku
        self.cat_url=cat_url
        self.margin_fee=margin
        self.ship_fee=ship
        self.ebay_fee=ebay
        self.driver = webdriver.Chrome(ChromeDriverManager().install())   #intialize webdriver

    # Login function
    def fieldfolio_login(self,username='gigint2@yahoo.com',password='M1l93W1hPlia'):
        

        self.driver.get('https://fieldfolio.com/login')
        self.driver.find_element_by_name('email').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_xpath('//*[@id="__next"]/div/main/div/div/div[2]/form/button').click()

    # Users catalog links scraping
    def mycatalog_cateogries_links(self):
        cat_links=[]
        if self.driver.current_url=="https://fieldfolio.com/":
            c_p=bs4.BeautifulSoup(self.driver.page_source,"html")
            link_content=c_p.find('div',attrs={'class':'YourCatalogList_listContainer__E7N5k'})
            cat_links=[self.driver.current_url[:-1]+i.a['href'] for i in link_content.find_all('div',attrs={'class':'CatalogListItem_catalogListItem__1QH99'})]
            print(cat_links)
            return cat_links
    
    # search and scrape product function
    def product_scrape(self):
        s=True
        for url in [self.cat_url]:
            count=1
            while True:
                if "categories" in url:
                    self.driver.get(url+'&page='+str(count))
                else:
                    self.driver.get(url+'?page='+str(count))
                time.sleep(3)
                product_code=bs4.BeautifulSoup(self.driver.page_source,'html')
                
                try:
                    if 'No products match search or filters'==product_code.find('h4',attrs={'class':'EmptyState_title__DWRDB'}).text.strip():
                        break
                except:
                    pass
                
                products=product_code.find('script',attrs={'id':'__NEXT_DATA__'}).text.strip()
                data=json.loads(products)
                for i in data['props']['pageProps']['hydrationData']['productStore']['items']:
                    stock=0
                    if self.sku==i['varieties'][0]['sku']:
                        try:
                            print('Stock : ',i['varieties'][0]['stock_on_hand'])
                            stock=i['varieties'][0]['stock_on_hand']
                        except:
                            stock=0

                        brand=''
                        upc=''                        
                        sku=i['varieties'][0]['sku']
                        title=i['name']
                        product_img=i["pictures"][0]['hero_photo_url']
                        des=str(i['extended_description']).replace('\u003cp\u003e','<p>').replace('\u003c/p\u003e','</p>')
                        price=i['prices'][0]
                        dic1={'Brand':brand,"Product Image":product_img,"Title":title,"OldPrice":price,'Description':des,'Stock':stock,'Sku':sku,"upc":upc}
                        s=False
                        return dic1
                        break
                    else:
                        s=True
                count+=1
                if s==False:
                    break
            if s==False:
                break
            else:
                print("Product Not Found in this catalog ",url)

    # Reprice function to calculate new price of product using different parameters
    def reprice(self,data,margin,ship,ebay_fee):
        n_price=(float(data['OldPrice'])+((margin/100)*float(data['OldPrice']))+ship+0.33)/(1-(ebay_fee/100))
        data['NewPrice']=round(n_price,2)
        return data
    
    # Function to run fieldfolio script
    def run_fieldfolio(self):
        self.fieldfolio_login()
        time.sleep(5)
        data=self.product_scrape()
        data=self.reprice(data,self.margin_fee,self.ship_fee,self.ebay_fee)
        self.driver.quit()
        return data

        


    
    


#Testing Code

# health_obj=HEALTHPOST('https://www.healthpost.co.nz/radiance-kids-gummies-immune-rdkgi-p',15,12,21)
# print(health_obj.run_healthpost())
# iher_obj=IHERB('https://au.iherb.com/pr/california-gold-nutrition-vitamin-d3-125-mcg-5-000-iu-90-fish-gelatin-softgels/70316',10,14,12)
# print(iher_obj.run_iherb())
# filedfolio_obj=FIELDFOLIO('1244W','https://fieldfolio.com/little-smiles/catalog',10,15,12)
# print(filedfolio_obj.run_fieldfolio())









    
#     if os.path.isfile('fieldfolio_data.csv'):
#         df.to_csv('fieldfolio_data.csv',index=False)
#     else:
#         df.to_csv('fieldfolio_data.csv',mode='a',header=False,index=False)    # function to store data
# def store(self,sku,name,des,price,img,stock):
#     try:
#         if stock>1:
#             stock=4
#     except:
#         stock=0
#     df=pd.DataFrame({'Sku':sku,
#     'Title':[name],
#     'Description':[des],
#     'PicURL':[img],
#     'Quantity':[stock],
#     'StartPrice':[price]})
    
#     if os.path.isfile('fieldfolio_data.csv'):
#         df.to_csv('fieldfolio_data.csv',index=False)
#     else:
#         df.to_csv('fieldfolio_data.csv',mode='a',header=False,index=False)


# """# **Store File**"""

# def store(data,name):
#     data=[data]
#     # csv header
#     fieldnames = ['Brand',"Title","Product Image","StartPrice",'Description','Stock','Sku',"upc"]

#     with open(name+'.csv', 'w', encoding='UTF8', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(data)









# """# **Store File**"""

# def store(data,name):
#     data=[data]
#     # csv header
#     fieldnames = ['Brand',"Title","Price",'Description','Stock','SKU',"UPC"]

#     with open(name+'.csv', 'w', encoding='UTF8', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(data)

# url=input("Enter URL of Product : ")
# s=scrape()     # class for get page text
# h1=healtpost()  # class to transform data of healtpost website
# ih1=iherb()     # class to transform data of iherb website
# page=s.extract_page(url)

# if 'www.healthpost.co' in url:
#     data=h1.preprocess_healtpost(page)
#     store(data,'healthpost')
# elif 'au.iherb.com' in url:
#     data=ih1.preprocess_iherb(page)
#     store(data,"iherb")





















# def run_scraper():
#     while True:
#         data=model.view_status()
#         tasks_list=model.get_all_tasks()
        
#         if data:
#             for t,status in zip(tasks_list,data):
#                 if status['status']=='Running':
#                     url=t[2]
#                     margin=t[6]
#                     ship=t[7]
#                     ebay_fee=t[8]
#                     catalog_url=t[5]
#                     print(url,catalog_url,margin,ship,ebay_fee)
#                     try:
#                         if 'www.healthpost.co' in url:
#                             s=scrape()     # class for get page text
#                             page=s.extract_page(url)
#                             h1=healtpost()  # class to transform data of healtpost website
#                             data=h1.preprocess_healtpost(page)
#                             data=h1.reprice(data,margin,ship,ebay_fee)
#                             print("New Price : ",data['StartPrice'])
#                             store(data,'healthpost')
#                         else:
#                             f1=FieldFolio()
#                             f1.fieldfolio_login()
#                             time.sleep(5)
#                             # cat_links=f1.mycatalog_cateogries_links()
#                             f1.product_scrape([catalog_url],url,margin,ship,ebay_fee)
#                     except:
#                         print("Invailed Values.")
#         else:
#             print("Sleep")
#         time.sleep(10)


# if __name__ == "__main__":
#     run_scraper()