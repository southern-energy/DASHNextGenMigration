from selenium import webdriver  # https://selenium-python.readthedocs.io/
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import pandas as pd
import MySQLdb
import ctypes

profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)

"""
SET PREFERRED DIRECTORY TO CURRENT ROOT DIRECTORY OF THIS SCRIPT!
"""

preferred_directory = os.getcwd() # 'G:\\My Drive\\PythonDev\\DASHNextGenMigration\\'
print(f"Report will land in: " + str(os.getcwd()))

profile.set_preference('browser.download.dir', preferred_directory)
profile.set_preference('browser.download.manager.showWhenStarting', False)
# specify file types that we want to download without being asked whether we want to open or save
profile.set_preference('browser.helperApps.neverAsk.saveToDisk','text/xml,text/csv,application/xls,''application/vnd.ms-excel')  
profile.update_preferences()


"""
The window will show up with this one.
"""
# browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),firefox_profile=profile)

"""
The Headless browsing option greatly reduces the amount of time it takes for the scraper to run.
"""

print("Headless Browser Running")
options = Options()
options.add_argument("--headless") # Runs Firefox in headless mode.
browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),firefox_profile=profile, options=options)

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

def navigate_to_reports_and_click_excel():
    browser.get("http://sem.myirate.com/Reports/AdHoc_View.aspx?id=1306")

    if os.path.exists("report.xls"):
        print("Removing Previous Report")
        os.remove("report.xls")
        print("Previous Report Removed")
    else:
        print("No report.xls file was present.")
    print("Sleeping for 5 seconds.")
    time.sleep(5)
    print("Done Sleeping")
    browser.find_element_by_id('ContentPlaceHolder1_lnkExport').click()

def grab_downloaded_report():
    print("Sleeping for 5 seconds.")
    time.sleep(5)
    print("Done Sleeping")
    df = pd.read_html("report.xls", header=0)[0]
    # print(df)

    df = df[['ServiceID','JobID','ServiceName','ServiceDate','Employee1', 'PONumber', 'Price','TestingComplete','DataEntryComplete','Reschedule','Reinspection','RescheduledDate','DateEntered','EnteredBy', 'LastUpdated','LastUpdatedBy','Checkbox3Value','Employee1Time5','Employee1Time6','Employee1Time7']]

    df.rename(columns={"JobID":"RatingID", "Employee1": "Employee", 'Employee1Time5':"EmployeeTime5",'Employee1Time6':"EmployeeTime6",'Employee1Time7':"EmployeeTime7", "Checkbox3Value":"readyToPrint"})

    df['LastUpdated'].astype('datetime64[ns]')
    df['DateEntered'].astype('datetime64[ns]')
    pd.to_datetime(df['ServiceDate'], utc=False)
    pd.to_datetime(df['RescheduledDate'], utc=False)

    mask = df.applymap(type) != bool
    d = {True: 'TRUE', False: 'FALSE'}

    df = df.where(mask, df.replace(d))

    df = df.replace({r',': '.'}, regex=True) # remove all commas
    df = df.replace({r';': '.'}, regex=True) # remove all commas
    df = df.replace({r'\r': ' '}, regex=True)# remove all returns
    df = df.replace({r'\n': ' '}, regex=True)# remove all

    # We want to grab the first 600 records, because the dataframe is 10000 recorsd long.

    df = df[:601]

    # Remove the previous "DASH_Service_Report_Export.csv" file.
    if os.path.exists("DASH_Service_Report_Export.csv"):
        os.remove("DASH_Service_Report_Export.csv")
    else:
        print("We do not have to remove the file.")

    df.to_csv("DASH_Service_Report_Export.csv", index=False)

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

    path= os.getcwd()+"\\DASH_Service_Report_Export.csv"
    print (path+"\\")
    path = path.replace('\\', '/')
    
    cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `service` FIELDS TERMINATED BY \',\' ignore 1 lines;')
    
    # #close the connection to the database.
    mydb.commit()
    cursor.close()

def file_cleanup():
    # Remove the previous "DASH_Service_Report_Export.csv" file.
    if os.path.exists("report.xls"):
        os.remove("report.xls")
    else:
        print("We do not have to remove the file.")

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
    print("DASHNextGen_Service_Report.py is Starting")
    login_into_dash("./DASHLoginInfo.json")
    navigate_to_reports_and_click_excel()
    browser.quit()
    time.sleep(5)
    grab_downloaded_report()
    file_cleanup()
    csv_to_database("./DASHLoginInfo.json")
    logout_session()


main()

browser.quit()

print("DASHNextGen_Service_Report.py is Done")