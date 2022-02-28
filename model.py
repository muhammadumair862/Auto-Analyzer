import re
from select import select
import sqlite3
import os
import pandas as pd
from sqlalchemy import true
import multiprocessing



def return_id(data):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select id from tasks where (name='{}' and category='{}')".format(data['name'],data['category']))
        result, = r1.fetchone() 
        return result
        con.close()


def initialize_db():
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        # table to store tasks
        con.execute("create table tasks (id integer PRIMARY KEY AUTOINCREMENT,name varchar (255),url varchar (255),category varchar (100),website varchar (50),sub_url varchar (255),margin_fee numeric,ship_fee numeric,ebay_fee numeric)")
        con.commit()

        # table to store default integrations
        con.execute("create table settings (id integer PRIMARY KEY AUTOINCREMENT,margin_fee numeric,ship_fee numeric,ebay_fee numeric,username varchar (255),password varchar (255))")
        con.commit()

        # table to store integrations
        con.execute("create table tasks_status (id integer PRIMARY KEY AUTOINCREMENT,account_id integer,status varchar(255),CONSTRAINT fk_tasks FOREIGN KEY (account_id) REFERENCES tasks(id))")
        con.commit()

        # table to store scrape data
        con.execute("create table tasks_data (id integer PRIMARY KEY AUTOINCREMENT,account_id integer,brand varchar (255),product_image varchar (255),title varchar (255),oldprice numeric,newprice numeric,description varchar (255),stock varchar (255),sku varchar (255),upc numeric)")
        con.commit()
        # con.close()




# %%%%%%%%%%%   Store Tasks data into tables   %%%%%%%%%%%%
def task(data):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        con.execute("insert into tasks (name,url,category,website,sub_url) values(?,?,?,?,?)",(data['name'],data['url'],data['category'],data['website'],data['sub_category']))
        con.commit()
        # con.close()

def store_task(data):
    if os.path.isfile("productanalyzer.sqlite3"):
        task(data)
    else:
        initialize_db()
        task(data)
    return return_id(data)

# store formula data
def task_formula(data):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        con.execute("update tasks set margin_fee='{}',ship_fee='{}',ebay_fee='{}' where (id ='{}')".format(data['margin_fee'],data['ship_fee'],data['ebay_fee'],data['id']))
        con.commit()
        con.execute("insert into tasks_status (account_id,status) values(?,?)",(data['id'],'Running'))
        con.commit()
        # con.close()

# %%%%%%%%%%%%%%%%%%%%%  Show Tasks Data  %%%%%%%%%%%%%%%%%%%%%

def view_status():
    if os.path.isfile("productanalyzer.sqlite3"):
        with sqlite3.connect("productanalyzer.sqlite3") as con:
            r1=con.execute("select * from tasks_status")
            result=r1.fetchall()
            data_list=[]
            
            for i in result:
                try:
                    data=get_specific_record(i[1])
                    data_list.append({'id':data[0][0],'name':data[0][1],'p_link':data[0][2],'status':i[2]})                
                except:
                    pass
            return data_list
    else:
        initialize_db()
        view_status()

# %%%%%%%%%%%%%%  Store & Update Settings in table  %%%%%%%%%%%%%%%

def settings(data):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select *from settings")
        result=r1.fetchall()
        if len(result)==0:
            con.execute("insert into settings (margin_fee,ship_fee,ebay_fee,username,password) values(?,?,?,?,?)",(data['margin_fee'],data['ship_fee'],data['ebay_fee'],data['username'],data['password']))
            con.commit()
        else:
            con.execute("update settings set margin_fee='{}',ship_fee='{}',ebay_fee='{}',username='{}',password='{}' where id='{}'".format(data['margin_fee'],data['ship_fee'],data['ebay_fee'],data['username'],data['password'],1))
            con.commit()
        # con.close()

def store_settings(data):
    if os.path.isfile("productanalyzer.sqlite3"):
        settings(data)
    else:
        initialize_db()
        store_settings(data)

# Display Settings
def get_settings():
    if os.path.isfile("productanalyzer.sqlite3"):
        with sqlite3.connect("productanalyzer.sqlite3") as con:
            r1=con.execute("select *from settings")
            result=r1.fetchall()
            if result:
                data={'margin_fee':result[0][1],'ship_fee':result[0][2],'ebay_fee':result[0][3],'username':result[0][4],'password':result[0][5]}
            else:
                data=[]
            return data
    else:
        initialize_db()
        get_settings()


def get_all_tasks():
    if os.path.isfile("productanalyzer.sqlite3"):
        with sqlite3.connect("productanalyzer.sqlite3") as con:
            r1=con.execute("select *from tasks")
            result=r1.fetchall()
            return result
    else:
        initialize_db()
        get_all_tasks()


# %%%%%%%%  Delete Tasks  %%%%%%%%%%
def delete_task(id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        con.execute("delete from tasks where (id ='{}')".format(id))
        con.commit()
        con.execute("delete from tasks_status where (id='{}')".format(id))

# %%%%%%%%%  Check Task & get Specific Task Data  %%%%%%%%%%%%%% 

def check_task_record(id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select *from tasks where id='{}'".format(id))
        result=r1.fetchall()
        
        if len(result)>0:
            return str(1)
        else:
            return str(0)

def get_specific_record(id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select *from tasks where id='{}'".format(id))
        result=r1.fetchall()
        return result

# Update Tasks
def edit_task(data):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        con.execute("update tasks set name='{}',url='{}',category='{}',website='{}',sub_url='{}',margin_fee='{}',ship_fee='{}',ebay_fee='{}' where (id ='{}')".format(data['name'],data['url'],data['category'],data['website'],data['sub_category'],data['margin_fee'],data['ship_fee'],data['ebay_fee'],data['id']))
        con.commit()
        r1=con.execute("select *from tasks_status where account_id=?",(data['id'],))
        if r1.fetchall():
            pass
        else:
            con.execute("insert into tasks_status (account_id,status) values(?,?)",(data['id'],'Running'))
            con.commit()


# Update Status
def update_status(id,status):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        print(id,status)
        con.execute("update tasks_status set status='{}' where account_id ='{}'".format(status,id))
        con.commit()


# Get settings
def task_with_default_settings(id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select * from settings")
        result=r1.fetchall()
        if len(result)>0:
            try:
                con.execute("update tasks set margin_fee='{}',ship_fee='{}',ebay_fee='{}' where (id ='{}')".format(result[0][1],result[0][2],result[0][3],id))
                con.commit()
                con.execute("insert into tasks_status (account_id,status) values(?,?)",(id,'Running'))
                con.commit()
                return True
            except:
                return False
        else:
            return "No setting"



# %%%%%%%%% Store scrape data to Table %%%%%%%%%%
def store_scrape_data(data,account_id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        con.execute("insert into tasks_data (account_id,brand,product_image,title,oldprice,newprice,description,stock,sku,upc) values(?,?,?,?,?,?,?,?,?,?)",(account_id,data['Brand'],data["Product Image"],data["Title"],data["OldPrice"],data["NewPrice"],data['Description'],data['Stock'],data['Sku'],data["upc"]))
        con.commit()

# Show Data
def get_scrape_record(id):
    with sqlite3.connect("productanalyzer.sqlite3") as con:
        r1=con.execute("select *from tasks_data where account_id='{}'".format(id))
        result=r1.fetchall()
        return result






# with sqlite3.connect("productanalyzer.sqlite3") as con:
#     con.execute("update tasks set margin_fee='{}',ship_fee='{}',ebay_fee='{}' where (id ='{}')".format(10,10,15,3))
#     con.commit()