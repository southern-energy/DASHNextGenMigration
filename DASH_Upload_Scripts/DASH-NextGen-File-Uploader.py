import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import shutil
import os
import json
import pandas as pd
import time
import winsound

# Importing Webdriver_Manager to prevent the need for maintenance.
# https://github.com/SergeyPirogov/webdriver_manager

# Since DASH NextGen Uses AJAX for Every Action
# https://stackoverflow.com/questions/24053671/webdriver-wait-for-ajax-request-in-python

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

def directory_creator():
    path= os.getcwd()
    newpath = path+'\\'+ 'Successfully_Uploaded'
    newpath2 = path+'\\'+ 'already_uploaded'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    if not os.path.exists(newpath2):
        os.makedirs(newpath2)

def navigate_to_downloads_and_upload_file():

    path= os.getcwd()
    newpath = path+'\\'+ 'Successfully_Uploaded'
    newpath2 = path+'\\'+ 'already_uploaded'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    if not os.path.exists(newpath2):
        os.makedirs(newpath2)

    file_list = os.listdir(".")
    absolute_path_list = []
    file_name_list = []
    absolute_path_iterator = 0

    for files in file_list:
        if files.endswith(".pdf"):
            absolute_path_list.append(os.path.abspath(files))
            file_name_list.append(files)
    # print(absolute_path_list)
    # print(file_name_list)
    
    
    for filename in file_name_list:
        ratingID = filename.split("_",1)[0]
        print(f"Current Rating ID Being Printed is: " + str(ratingID))
        browser.get(f"http://sem.myirate.com/Jobs/NewConst_Edit_File.aspx?id=1&j=" + str(ratingID))
    
        # browser.get("http://sem.myirate.com/Jobs/NewConst_Edit_File.aspx?id=33&j=486")
        files_table = browser.find_element_by_id("ctl00_ContentPlaceHolder1_rgUploadedFiles_ctl00").get_attribute("outerHTML")
        df = pd.read_html(files_table)
        df[0].drop(index=0)
        file_label_list = df[0].Description.tolist()
        if (any(item.startswith('HERS Certificate') for item in file_label_list)) == True:
            print(True)
            print("You already have a HERS Certificate Uploaded")
            # We should consider adding function that removes existing script so we can re-upload anyways.
            shutil.move(path + '\\' + filename, 'already_uploaded' + "\\" + filename)
            absolute_path_iterator += 1
        else:
            print(False)
            print("Uploading Certificate")
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_FileType1_Input").click
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_FileType1_Input").send_keys(Keys.CONTROL, "a")
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_FileType1_Input").send_keys(Keys.BACKSPACE)
            browser.find_element_by_id("ctl00_ContentPlaceHolder1_FileType1_Input").send_keys("HERS Certificate - Ekotrope",Keys.ENTER)
            print(str(absolute_path_list[absolute_path_iterator]))
            browser.find_element_by_css_selector("#File1file0").send_keys(str(absolute_path_list[absolute_path_iterator]))
            print("Sleeping for 2 seconds")
            time.sleep(2)
            browser.find_element_by_name("ctl00$ContentPlaceHolder1$btnSaveFiles").click()
            time.sleep(2) # We have saved the file!

            """
            Now we have to click the button to make sure that the builder has access to the uploaded certificate 🙃.
            """
            browser.find_element_by_name("ctl00$ContentPlaceHolder1$rgUploadedFiles$ctl00$ctl05$EditButton").click()

            # Now we wait until the box with the check boxes is selectable.

            try:
                WebDriverWait(browser,2).until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_rgUploadedFiles_ctl00_ctl05_ctl02")))
            finally:
                if browser.find_element_by_id("ctl00_ContentPlaceHolder1_rgUploadedFiles_ctl00_ctl05_ctl02").is_selected() == False:
                    browser.find_element_by_id("ctl00_ContentPlaceHolder1_rgUploadedFiles_ctl00_ctl05_ctl02").click()
                    print(f"Builder Checkbox for DASH" + str(ratingID))
                else:
                    print("Something is broken, or the box is already checked.")
            browser.find_element_by_name("ctl00$ContentPlaceHolder1$rgUploadedFiles$ctl00$ctl05$UpdateButton").click()

            print(f"We have uploaded and saved DASH: " + str(ratingID))

            shutil.move(path + '\\' + filename, newpath + "\\" + filename)
            absolute_path_iterator += 1

def beep_when_done():
    #Attributes
    duration_short = 100  # milliseconds
    duration_long = 300  # milliseconds
    freq = 400  # Hz
    freq2 = 200 

    winsound.Beep(freq, duration_short)
    winsound.Beep(freq2, duration_long)
    winsound.Beep(freq, duration_short)

def main():
    login_into_dash("./DASHLoginInfo.json")
    navigate_to_downloads_and_upload_file()
    beep_when_done()

main()
browser.quit()