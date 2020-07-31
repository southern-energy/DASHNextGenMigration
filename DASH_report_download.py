from selenium import webdriver  # https://selenium-python.readthedocs.io/
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import time

# set the download directory if you want the file to go somewhere other than Downloads:
#download_directory = 'C:\\Users\\jonathan.scott\\My ShareSync\\RandD\\'
#profile.set_preference('browser.download.dir', download_directory)

# https://stackoverflow.com/questions/25251583/downloading-file-to-specified-location-with-selenium-and-python
# https://stackoverflow.com/questions/45645648/python-disable-download-popup-when-using-firefox-with-selenium
profile = webdriver.FirefoxProfile()

profile.set_preference("browser.download.manager.showWhenStarting", False)

# specify file types that we want to download without being asked whether we want to open or save
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 
                       'text/xml,text/csv,application/xls,'
                       'application/vnd.ms-excel')  
profile.update_preferences()


url = 'http://privdemo.myeldash.com'
un = 'tryit'
pw = 'nrgDem0s!'

browser = webdriver.Firefox(firefox_profile=profile)
browser.maximize_window()

# use Selenium package to open a browser window, create html soup, then close the window
browser.get(url)
time.sleep(5)

# user name
inputElement = browser.find_element_by_id('ContentPlaceHolder1_Username')
inputElement.send_keys(un)

# password
inputElement = browser.find_element_by_id('ContentPlaceHolder1_Password')
inputElement.send_keys(pw)

# Login
inputElement = browser.find_element_by_id('ContentPlaceHolder1_btnLogin')
inputElement.click()
time.sleep(5)

# Reports
inputElement = browser.find_element_by_id('navReports')
inputElement.click()
time.sleep(5)

# Ad Hoc Reports
inputElement = browser.find_element_by_xpath('/html/body/form/div[4]/div[3]/div[4]/div/div[1]/ul/li[2]/a')
inputElement.click()
time.sleep(5)

# GP - HERO Export
inputElement = browser.find_element_by_xpath('/html/body/form/div[4]/div[3]/div[6]/div[5]/div/div[2]/table/tbody/tr[5]/td[2]/a')
inputElement.click()
time.sleep(5)

# export to Excel
inputElement = browser.find_element_by_id('ContentPlaceHolder1_lnkExport')
inputElement.click()

browser.quit()