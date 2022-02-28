import model
import test
import upload_draft

import requests as req
import bs4
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import os
from webdriver_manager.chrome import ChromeDriverManager



"""# **Store File**"""

def store(data,name):
    row1=['#INFO','Version=0.0.2','Template= eBay-draft-listings-template_AU','','','','','','','','']
    row2=['#INFO Action and Category ID are required fields. 1) Set Action to Draft 2) Please find the category ID for your listings here: https://pages.ebay.com/sellerinformation/news/categorychanges.html','','','','','','','','','','']
    row3=["#INFO After you've successfully uploaded your draft from the Seller Hub Reports tab, complete your drafts to active listings here: https://www.ebay.com.au/sh/lst/drafts",'','','','','','','','','','']
    row4=['Action(SiteID=Australia|Country=AU|Currency=AUD|Version=1193|CC=UTF-8)','Custom label (SKU)','Category ID','Title','UPC','Price','Quantity','Item photo URL','Condition ID','Description','Format']
    data=['Draft',data['Sku'],47140,data['Title'],data['upc'],data['NewPrice'],1,data['Product Image'],'NEW',data['Description'],'FixedPrice']
    # csv header
    # fieldnames = ['Brand',"Title","StartPrice",'Description','Stock','Sku',"upc"]
    
    with open(str(name), 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # writer.writeheader()
        writer.writerows([row1,row2,row3,row4,data])        # writer.writerows(data)


def csv_map_scrape(data,name):
    with open(name,mode='r') as f:
        reader=csv.reader(f)
        for r,i in enumerate(reader):
            if r==4:
                sku=i[1];price=i[5]
        if str(price)==str(data['NewPrice']):
            return False
        else:
            return True


def scrape_data_update(data,name):
    if os.path.isfile(name):
        if csv_map_scrape(data,name):
            store(data,name)
            upload_draft.upload_draft(name)
    else:
        if not os.path.isdir("output_files"):
            os.mkdir('output_files')
        store(data,name)
        upload_draft.upload_draft(name)







def run_scraper():
    while True:
        data=model.view_status()
        tasks_list=model.get_all_tasks()
        
        if data: 
            for t,status in zip(tasks_list,data):
                if status['status']=='Running':
                    id=t[0]
                    url=t[2]
                    margin=t[6]
                    ship=t[7]
                    ebay_fee=t[8]
                    catalog_url=t[5]
                    print(url,catalog_url,margin,ship,ebay_fee)
                    # try:
                    if 'www.healthpost.co' in url:
                        health_obj=test.HEALTHPOST(url,margin,ship,ebay_fee)
                        data=health_obj.run_healthpost()
                        # model.store_scrape_data(data,id)
                        print(data)
                        scrape_data_update(data,'output_files/'+data['Sku']+'healthpost.csv')

                    elif 'iherb.com' in url:
                        iherb_obj=test.IHERB(url,margin,ship,ebay_fee)
                        data=iherb_obj.run_iherb()
                        # model.store_scrape_data(data,id)
                        print(data)
                        scrape_data_update(data,'output_files/'+data['Sku']+'iherb.csv')
                    else:
                        field_obj=test.FIELDFOLIO(url,catalog_url,margin,ship,ebay_fee)
                        data=field_obj.run_fieldfolio()
                        # model.store_scrape_data(data,id)
                        print(data)
                    
                        scrape_data_update(data,'output_files/'+data['Sku']+'fieldfolio.csv')
                    # except:
                        # print("Invailed Values.")
        else:  
            print("Sleep")
        time.sleep(10)


if __name__ == "__main__":
    run_scraper()