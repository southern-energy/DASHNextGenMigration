import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
import requests
import json
import re
import pandas as pd
from datetime import datetime
import time

# Imports from Will's Previous Work
from robobrowser import RoboBrowser #for navigating and form submission
import datetime
from datetime import timedelta, date
import time
import csv
import pandas as pd
import MySQLdb
import os
# End of Import Section



browser = webdriver.Chrome("./chromedriver.exe")

# print("Headless Browser Running")
# options = Options()
# options.add_argument("--headless") # Runs Chrome in headless mode.
# options.add_argument('--no-sandbox') # Bypass OS security model
# options.add_argument('--disable-gpu')  # applicable to windows os only
# options.add_argument('start-maximized') # 
# options.add_argument('disable-infobars')
# options.add_argument("--disable-extensions")
# browser = webdriver.Chrome(chrome_options=options, executable_path=r'./chromedriver.exe')
# print("Headless Browser has Launched")

def login_into_dash(json_target_file):
    """
    Takes the login information from JSON file and passes data to login form.
    """
    browser.get("http://privdemo.myeldash.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Username").send_keys(username)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Password").send_keys(password)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()

def download_excel():
    browser.get("http://privdemo.myeldash.com/Reports/AdHoc_View.aspx?id=1")
    browser.find_element_by_id("ContentPlaceHolder1_lnkExport").click()

def read_table():
    browser.get("http://privdemo.myeldash.com/Reports/AdHoc_View.aspx?id=4")

    #  Start of Grabbing Iterator Information

    items_and_pages_element = browser.find_element_by_class_name("rgInfoPart").text
    digits_list = []
    pattern = r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    if re.search(pattern, items_and_pages_element) is not None:
        for catch in re.finditer(pattern, items_and_pages_element):
            # print(catch[0])
            digits_list.append(catch[0])
    else:
        print("Something is broken.")

    # print(digits_list)

    items = int(digits_list[0])
    pages = int(digits_list[1])
    print("Number of items: " + str(items))
    print("Number of pages: " + str(pages))

    # End of Grabbing Iterator Information

    # This block controls table scraping.

    table_list = browser.find_elements_by_class_name('rgClipCells')

    # We have to grab table headings from the report.
    table_headers = table_list[0]
    print(table_headers)


    table_we_want = table_list[1].get_attribute('outerHTML')
    dataframe = pd.DataFrame()
    dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
    print(len(dataframe.index))
    # print(dataframe)
    # print(len(dataframe.index))

    while int(len(dataframe.index)) <= items:
        browser.find_element_by_name("ctl00$ContentPlaceHolder1$rgReport$ctl00$ctl03$ctl01$ctl11").click()
        dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
        print(len(dataframe.index))
    else:
        print("We are done scraping.")
        print(dataframe)
        print(len(dataframe.index))
    return dataframe

def database_plug(dataframe):
    mydb = MySQLdb.connect(
        host='104.154.197.202',
        port=3306,
        user='will_etheridge',
        passwd='M!ll_<3s_fr0g$',
        db='sem_dash',
        charset='utf8',
        local_infile = 1)

    cursor = mydb.cursor()
    dataframe.to_csv('TEMPO.csv', encoding='utf-8',index=False)
    
    
    path= os.getcwd()+"\\TEMPO.csv"
    print (path+"\\")
    path = path.replace('\\', '/')
    
    cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `job` FIELDS TERMINATED BY \',\' ignore 1 lines;')
    
    # #close the connection to the database.
    mydb.commit()
    cursor.close()

login_into_dash("./DASHLoginInfo.json")
# read_table()
# database_plug()