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
# # print("Real Browser Launching")
# browser = webdriver.Chrome(ChromeDriverManager().install())
# # print("Real Browser has Launched")

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

def read_table(url):
    browser.get(url)

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
    # table_headers_table = table_list[0]
    # print(table_headers_table)

    # table_headers_table_table_row_element = browser.find_element_by_xpath("/html/body/form/div[4]/div[3]/div[6]/div[6]/div[1]/div/table/thead/tr[1]").get_attribute('outerHTML')


    table_we_want = table_list[1].get_attribute('outerHTML')

    """Please remember to change the columns for each report"""

    # dataframe = pd.DataFrame(columns=["Job ID","Project Name","Client Name","Street Address","Lot","City","State","Zip","Subdivision Name","Gas Utility","Electric Utility","Division Name","Job Number","HERS","Bldg File","Ekotrope Status","Ekotrope Project Name","Ekotrope Project Link","Date Entered"])

    dataframe = pd.DataFrame()

    dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
    print(len(dataframe.index))
    # print(dataframe)
    # print(len(dataframe.index))

    # while int(len(dataframe.index)) < items:
    #     browser.find_element_by_css_selector("button.t-button.rgActionButton.rgPageNext").click()
    #     time.sleep(10)
    #     table_list = browser.find_elements_by_class_name('rgClipCells')
    #     table_we_want = table_list[1].get_attribute('outerHTML')
    #     # print(table_we_want)
    #     dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
    #     print(len(dataframe.index))
    #     time.sleep(2)
    # else:
    #     print("We are done scraping.")
    #     print(dataframe)
    #     print(len(dataframe.index))

    page_counter = 0
    page_limiter = 100

    while page_counter < page_limiter:
        browser.find_element_by_css_selector("button.t-button.rgActionButton.rgPageNext").click()
        table_list = browser.find_elements_by_class_name('rgClipCells')
        table_we_want = table_list[1].get_attribute('outerHTML')

        # We need to apply the regext statements from earlier to each loop as well.

        table_we_want = re.sub(r'<span.{164} disabled="disabled"><\/span>', 'False', table_we_want)
        table_we_want = re.sub(r'<span.{182} disabled="disabled"><\/span>', 'True', table_we_want)

        # print(table_we_want)
        dataframe = dataframe.append(pd.read_html(table_we_want),ignore_index=True)
        print(len(dataframe.index))
        time.sleep(2)
        page_counter += 1
    else:
        print("We are done scraping.")
        print(dataframe)
        print(len(dataframe.index))


    """
    Here we must reorder the columns so our data can be compatible with older DASH Information
    
    The changes we are making:
        - Remove Project Name Column
        - Rearranging the columns to align with the database schema.
    """
    # keys = ['RatingID', 'JobNumber', 'Address', 'City', 'State', 'Zip', 'Builder', 'Subdivision', 'GasUtility', 'ElectricUtility', 'Lot', 'Division', 'HERSIndex', 'BldgFile', 'DateEntered', 'EkotropeStatus', 'EkotropeProjectName', 'EkotropeProjectLink']
    #TODO: Label these columns.
    dataframe = dataframe[[0,12,3,5,6,7,2,8,9,10,4,11,13,14,18,15,16,17]]
   
    # dataframe = dataframe.rename(columns={1:"ServiceID",0:"RatingID",2:"ServiceName",3:"ServiceDate",4:"Employee",11:"PONumber",10:"Price",5:"TestingComplete",6:"DataEntryComplete",7:"Reschedule",8:"Reinspection",9:"RescheduledDate",16:"DateEntered",17:"EnteredBy",18:"LastUpdated",19:"LastUpdatedBy",12:"Checkbox3Value",13:"EmployeeTime5",14:"EmployeeTime6",15:"EmployeeTime7"})

    dataframe[17] = dataframe[17].str[-8:]
    dataframe[4] = pd.to_numeric(dataframe[4], downcast='integer',errors='ignore')
    dataframe[18] = pd.to_datetime(dataframe[18], utc=False)

    dataframe = dataframe.replace({r',': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r';': '.'}, regex=True) # remove all commas
    dataframe = dataframe.replace({r'\r': ' '}, regex=True)# remove all returns
    dataframe = dataframe.replace({r'\n': ' '}, regex=True)# remove all newlines

    # Remove the previous "DASH_Job_Export.csv" file.
    if os.path.exists("DASH_Job_Export.csv"):
        os.remove("DASH_Job_Export.csv")
    else:
        print("We do not have to remove the file.")

    dataframe.to_csv("DASH_Job_Export.csv", index=False)

def defloat():
    with open('DASH_Job_Export.csv', newline='') as f, open('DASH_Job_Export_defloated.csv', "w", newline='') as outFile:
        reader = csv.reader(f)
        writer = csv.writer(outFile)
        for row in reader:
            if row[10].endswith(".0") == True: # This statement converts the floats in the csv to regular values.
                row[10] = row[10][:-2]
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]])
            elif row[10] == "":
                row[10] = ''
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]])
            else:
                writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]])
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

    path= os.getcwd()+"\\DASH_Job_Export_defloated.csv"
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
    print("DASHNextGen_job_delimited.py is Starting")
    login_into_dash("./DASHLoginInfo.json")
    read_table("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1307")
    defloat()
    csv_to_database("./DASHLoginInfo.json")
    logout_session()
    print("DASHNextGen_job_delimited.py is Done")

main()
browser.quit()
