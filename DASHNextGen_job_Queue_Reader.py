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
import gspread

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
browser = webdriver.Chrome(chrome_options=options, executable_path=ChromeDriverManager().install())
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

def read_energystar_and_non_energy_star_queue_tabs():

    """
    This section uses gspread and the Google API to access the Non-E* Process Sheet and the Energy Star Process Sheet 
    """
    # We had to create a Google API Credentials Key, which we access.
    gc = gspread.service_account(filename="google_api_credentials.json")
    
    # The Key is https://docs.google.com/spreadsheets/d/<THIS PART OF THE ADDRESS>/edit#gid=
    sh = gc.open_by_key('1necFt4Dobp7E_hlUzcIHSlVneB5zB3DzwQZcZmDH0uE')
    worksheet = sh.worksheet('Queue Copy for Print Tool')

    Non_Energy_Star_Data = worksheet.col_values(1)[1:]

    # print(Non_Energy_Star_Data)

    Energy_Star_Sheet = gc.open_by_key('1vIPJSB35NqJMVbjHq9X5NjmWll60C2wqTncNpK7ic7Y')

    queue_for_print_tool_sheet = Energy_Star_Sheet.worksheet('Queue Copy for Print Tool')

    Energy_Star_DASH_IDs = queue_for_print_tool_sheet.col_values(1)[1:]

    # print(Energy_Star_DASH_IDs)

    combined_list = Non_Energy_Star_Data + Energy_Star_DASH_IDs

    print(f"We grabbed " + str(len(Non_Energy_Star_Data)) + " Non Energy Star IDs.")
    print(f"We grabbed " + str(len(Energy_Star_DASH_IDs)) + " Non Energy Star IDs.")
    print(f"We have " + str(len(combined_list)) + " total DASH IDs.")
    global DASH_ID_List
    DASH_ID_List = combined_list

def read_table(url, DASH_List):
    browser.get(url)

    dataframe = pd.DataFrame()


    for index, DASH_ID in enumerate(DASH_ID_List):
        print(f"We are on DASH ID " + str(DASH_ID) + " number " + str(int(index)+1) + " of " + str(len(DASH_ID_List)))
        print(f"Grabbing page for DASH " + str(DASH_ID))
        try:
            WebDriverWait(browser,1).until(EC.element_to_be_clickable((By.ID,"ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04")))
        finally:
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").click()
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(Keys.CONTROL, "a")
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(Keys.BACKSPACE)
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ctl01_ctl08_ctl04").send_keys(str(DASH_ID))
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_rfReport_ApplyButton").click()
            try:
                WebDriverWait(browser,1).until(EC.visibility_of_element_located((By.ID,'ctl00_ContentPlaceHolder1_rgReport_ctl00__0')))
            finally:
                table_list = browser.find_elements_by_class_name('rgClipCells')
                table_we_want = table_list[1].get_attribute('outerHTML')
                dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
        

    dataframe = dataframe[[0,12,3,5,6,7,2,8,9,10,4,11,13,14,18,15,16,17]]

    #TODO: Fix this ordering and rearrangin' of stuff

    # dataframe.rename(columns={0:"RatingID",12:"Checkbox3Value",3:"ServiceDate",5:"TestingComplete",6:"DataEntryComplete",7:"Reschedule", 2:"ServiceName",8:"Reinspection",9:"RescheduledDate",10:"Price",4:"Employee",11:"PONumber",13:"EmployeeTime5",14:"EmployeeTime6",18:"LastUpdated",16:"DateEntered",15:"EmployeeTime7",1:"ServiceID",17:"EnteredBy"})

    # ["RatingID","JobNumber","Address","City","State","Zip","Builder","Subdivision","GasUtility","ElectricUtility","Lot","Division","HERSIndex","BldgFile","DateEntered"]

    dataframe[17] = dataframe[17].str[-8:]
    dataframe[18] = pd.to_datetime(dataframe[18], utc=False)

    # dataframe.to_csv("Export_After_Reorganization.csv", encoding="utf-8", index=False)

    dataframe = dataframe.replace({r',': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r';': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r'\r': ' '}, regex=True)# remove all returns
    dataframe = dataframe.replace({r'\n': ' '}, regex=True)# remove all newlines

    # Remove the previous "DASH_Job_Export_Queue_Reader.csv" file.
    if os.path.exists("DASH_Job_Export_Queue_Reader.csv"):
        os.remove("DASH_Job_Export_Queue_Reader.csv")
    else:
        print("We do not have to remove the file.")

    dataframe.to_csv("DASH_Job_Export_Queue_Reader.csv", index=False)

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

    path= os.getcwd()+"\\DASH_Job_Export_Queue_Reader.csv"
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
    print("DASHNextGen_job_individual.py is Starting")
    read_energystar_and_non_energy_star_queue_tabs()
    login_into_dash("./DASHLoginInfo.json")
    read_table("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1322", DASH_ID_List)
    csv_to_database("./DASHLoginInfo.json")
    logout_session()
    print("DASHNextGen_job_individual.py is Done")

main()
import beeper_module
browser.quit()