import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Importing Webdriver_Manager to prevent the need for maintenance.
# https://github.com/SergeyPirogov/webdriver_manager

"""
This was the original method I was using when developing this script, please run this if you are curious of what is happening under the hood of Selenium or you need to troubleshoot any issues.
"""
# print("Real Browser Launching")
# browser = webdriver.Chrome(ChromeDriverManager().install())
# print("Real Browser has Launched")

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""
print("Headless Browser Running")
options = Options()
options.add_argument("--headless") # Runs Chrome in headless mode.
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized') # 
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
print("Headless Browser has Launched")

def login_into_dash(json_target_file):
    """
    Takes the login information from JSON file and passes data to login form.

    Parameter json_target_file needs to be equal to the file's location.

    Contents of the file must be organized as follows [Note: don't forget the curly braces]:
    
    {
    "username": "please-put-your-username-here",
    "password": "please-put-your-password-here"
    }


    """
    browser.get("http://sem.myirate.com/")
    with open(json_target_file) as login_data:
        data = json.load(login_data)
    username = data['username']
    password = data['password']
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Username").send_keys(username)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$Password").send_keys(password)
    browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()

#TODO: Add way to connect to Non-Energy Star Sheet and Rob's Energy Star Sheet

def read_table(url):

    browser.get(url)

    dataframe = pd.DataFrame()

    filter_date_start =  date.today() + datetime.timedelta(days=2)
    print(filter_date_start)

    filter_date_end =  date.today() + datetime.timedelta(days=-180)
    print(filter_date_end)

    try:
        WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput")))
    finally:
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").click()
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").send_keys(Keys.CONTROL, "a")
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").send_keys(Keys.BACKSPACE)
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04_dateInput").send_keys(str(filter_date_end))
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").click()
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").send_keys(Keys.CONTROL, "a")
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").send_keys(Keys.BACKSPACE)
        browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl05_dateInput").send_keys(str(filter_date_start))
        try:
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()
            print("We did not have to wait to click the apply button")
        except:
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ApplyButton"))).click()
            print("We had to wait to click the apply button.")
        try:
            WebDriverWait(browser,1).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
        finally:
            print("We have applied the date filter, we are now grabbing data.")

        # Here we define the number of pages we have to scrape through.
        
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

        while int(len(dataframe.index)) < items:
            try:
                WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
            finally:
                table_list = browser.find_elements_by_class_name('rgClipCells')
                table_we_want = table_list[1].get_attribute('outerHTML')
                dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
                print(len(dataframe))
            try:
                WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.CLASS_NAME,"rgPageNext"))).click()
            except:
                WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.CLASS_NAME,"rgPageNext"))).click()
        else:
            print("We are done scraping on to the next query.")
              
                
        

    dataframe = dataframe[[0,12,3,5,6,7,2,8,9,10,4,11,14,15,19,16,17,18,13,1]]


    #TODO: Fix this ordering and rearrangin' of stuff

    # dataframe.rename(columns={0:"RatingID",12:"Checkbox3Value",3:"ServiceDate",5:"TestingComplete",6:"DataEntryComplete",7:"Reschedule", 2:"ServiceName",8:"Reinspection",9:"RescheduledDate",10:"Price",4:"Employee",11:"PONumber",13:"EmployeeTime5",14:"EmployeeTime6",18:"LastUpdated",16:"DateEntered",15:"EmployeeTime7",1:"ServiceID",17:"EnteredBy"})

    # ["RatingID","JobNumber","Address","City","State","Zip","Builder","Subdivision","GasUtility","ElectricUtility","Lot","Division","HERSIndex","BldgFile","DateEntered"]

    dataframe[18] = dataframe[18].str[-8:]
    dataframe[4] = pd.to_numeric(dataframe[4], downcast='integer',errors='ignore')
    dataframe[19] = pd.to_datetime(dataframe[19], utc=False)

    # dataframe.to_csv("Export_After_Reorganization.csv", encoding="utf-8", index=False)

    dataframe = dataframe.replace({r',': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r';': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r'\r': ' '}, regex=True)# remove all returns
    dataframe = dataframe.replace({r'\n': ' '}, regex=True)# remove all newlines

    # Remove the previous "DASH_Job_Export_Queue_Reader_Date_v2.csv" file.
    if os.path.exists("DASH_Job_Export_Queue_Reader_Date_v2.csv"):
        os.remove("DASH_Job_Export_Queue_Reader_Date_v2.csv")
    else:
        print("We do not have to remove the file.")

    print(dataframe)
    print(len(dataframe.index)) 

    dataframe.to_csv("DASH_Job_Export_Queue_Reader_Date_v2.csv", index=False)

def defloat():
    with open('DASH_Job_Export_Queue_Reader_Date_v2.csv', newline='') as f, open('DASH_Job_Export_Queue_Reader_Date_defloated_v2.csv', "w", newline='') as outFile:
        reader = csv.reader(f)
        writer = csv.writer(outFile)
        for row in reader:
            if row[10].endswith(".0") == True: # This statement converts the floats in the csv to regular values.
                row[10] = row[10][:-2]
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18]])
            elif row[10] == "":
                row[10] = ''
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18]])
            else:
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18]])
                continue

def csv_to_database(json_target_file):
    with open(json_target_file) as login_data:
        data = json.load(login_data)

    mydb = MySQLdb.connect(
        host=data["host"],
        port=int(data["port"]),
        user=data["user"],
        passwd=data["passwd"],
        db=data["db"],
        charset=data["charset"],
        local_infile=data["local_infile"])

    cursor = mydb.cursor()
    
    # Point to the file that we want to grab.

    path= os.getcwd()+"\\DASH_Job_Export_Queue_Reader_Date_defloated_v2.csv"
    print (path+"\\")
    path = path.replace('\\', '/')
    
    cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `job` FIELDS TERMINATED BY \',\' ignore 1 lines;')
    
    # #close the connection to the database.
    mydb.commit()
    cursor.close()

def logout_session():
    browser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    browser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()
    except:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()

def main():
    """
    Please use these to control the previously defined functions.
    """
    print("DASHNextGen_job_date_BIG_v2.py is Starting")
    # read_energystar_and_non_energy_star_queue_tabs()
    login_into_dash("./DASHLoginInfo.json")
    read_table("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1353")
    defloat()
    csv_to_database("./DASHLoginInfo.json")
    logout_session()
    print("DASHNextGen_job_date_BIG_v2.py is Done")

main()
browser.quit()
