import selenium
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.common.service 
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import winsound
import json
import gspread

# Research Deeper Executing JS in Python https://seleniumwithjavapython.wordpress.com/selenium-with-python/intermediate-topics/playing-with-javascript-and-javascript-executor/hidden-elements-in-javascript/

start_time = time.time()

# print("Browser Launching")
# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
# options.add_argument("--disable-extensions")
# browser = webdriver.Chrome(executable_path=ChromeDriverManager().install())
# print("Browser has Launched")

# Attempt to Run Chrome Headless (Without Window Popping Up)
print("Browser Launching Headless")
options = Options()
options.add_argument("--headless") # Runs Chrome in headless mode.
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized') # 
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
print("Browser has Launched Headlessly")

def read_excel_sheet():
    df = pd.read_excel("./NonEnergyStarDashClickerSheet.xlsx", sheet_name=0,header=0,usecols=0)
    print(df)
    df['DASHID'].astype(str)
    global Local_Excel_DASH_ID_List
    Local_Excel_DASH_ID_List = df['DASHID'].tolist()
    print(Local_Excel_DASH_ID_List)

    global DASH_ID_List
    DASH_ID_List = Local_Excel_DASH_ID_List


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

    print(f"We grabbed " + str(len(Non_Energy_Star_Data)) + " Non Energy Star IDs.")

    # print(Non_Energy_Star_Data)
    # Energy_Star_Sheet = gc.open_by_key('1vIPJSB35NqJMVbjHq9X5NjmWll60C2wqTncNpK7ic7Y')
    # queue_for_print_tool_sheet = Energy_Star_Sheet.worksheet('Queue Copy for Print Tool')
    # Energy_Star_DASH_IDs = queue_for_print_tool_sheet.col_values(1)[1:]
    # print(f"We grabbed " + str(len(Energy_Star_DASH_IDs)) + " Non Energy Star IDs.")
    # # print(Energy_Star_DASH_IDs)
    # combined_list = Non_Energy_Star_Data + Energy_Star_DASH_IDs
    # print(f"We have " + str(len(combined_list)) + " total DASH IDs.")
    
    
    global DASH_ID_List
    DASH_ID_List = Non_Energy_Star_Data



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

def read_excel_file_return_list(DASH_ID_List):
    # df = pd.read_excel('./NonEnergyStarDashClickerSheet.xlsx', header=0, usecols=0, index_col=None, converters={'DASHID':str})
    # DASH_ID_List = df['DASHID'].tolist()
    # DASH_ID_List = ["69990"]

    print(DASH_ID_List)
    print(f"We have " + str(len(DASH_ID_List)) + " DASH ID's to Iterate Through")
    for DASHID in DASH_ID_List:
        print(f"We are on DASHID " + str(DASHID))
        browser.get(f"http://sem.myirate.com/Jobs/NewConst_Edit_Service.aspx?id=3019&j="+str(DASHID))
        # Open the menu under "Add a Service"
        time.sleep(2)
        browser.find_elements_by_class_name("inspButton")[1].click()
        # We wait for the menu to open.
        try:
            "We are trying to find the element."
            WebDriverWait(browser,5).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0")))
        finally:
            if browser.find_element_by_id("ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0").is_selected() == False:
                time.sleep(1)

                # print(browser.find_element_by_id("ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0").get_attribute("outerHTML"))

                # browser.find_element_by_id("ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0").click()

                print("Now executing Javascript!")
                browser.execute_script("arguments[0].style.display = 'block';arguments[0].style.visibility = 'visible';",browser.find_element_by_xpath("//*[@id='ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0']"))
                print("Now we will try clicking it!")
                try:
                    browser.find_element_by_xpath("//*[@id='ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0']").click()
                    print("Didn't have to wait to click.")
                except:
                    button = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='ContentPlaceHolder1_rptServices_CustomCheckboxes_0_2_0']")))
                    button.click()
                    print("Had to wait to click.")
                print(f"Ready to Print Checkbox for DASH " + str(DASHID) + " is clicked!")
                parent_div_save_button = browser.find_elements_by_class_name("buttonFloat")[0]
                save_button_child = parent_div_save_button.find_element_by_name("ctl00$ContentPlaceHolder1$rptServices$ctl00$btnSave")
                if save_button_child.get_attribute("value") == "Save Service":
                    save_button_child.click()
                    print(f"We saved our input for DASH: " + str(DASHID))
            else:
                print("Something is broken, or the box is already checked.")
        # We now have to click the "Import Button"
        time.sleep(2)
        browser.get(f"http://sem.myirate.com/Jobs/NewConst_Edit_CloseOut.aspx?id=1016&j="+str(DASHID))
        print("We are on the Close Out Page")
        try:
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.ID,"button2"))).click()
            print("We opened Close Job Box on the first try.")
            WebDriverWait(browser,5).until(EC.element_to_be_clickable((By.NAME,"ctl00$ContentPlaceHolder1$btnSaveEkotrope"))).click()
            print("We clicked the Import Data button on the first try.")
        except:
            WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.ID,"button2"))).click()
            print("We opened Close Job Box on the second try.")
            WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.NAME,"ctl00$ContentPlaceHolder1$btnSaveEkotrope"))).click()
            print("We clicked the Import Data button on the second try.")
    print("We are done.")

def logout_session():
    browser.get("http://sem.myirate.com/Dashboard_Company.aspx")
    browser.find_element_by_xpath('//*[@id="navProfile"]').click()
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()
    except:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT,"Log Out"))).click()

def beep_when_done():
    #Attributes
    duration_short = 100  # milliseconds
    duration_long = 300  # milliseconds
    freq = 400  # Hz

    winsound.Beep(freq, duration_short)
    winsound.Beep(freq, duration_long)
    winsound.Beep(freq, duration_short)

def main():
    read_energystar_and_non_energy_star_queue_tabs()
    # read_excel_sheet()
    login_into_dash("./DASHLoginInfo.json")
    read_excel_file_return_list(DASH_ID_List)
    logout_session()
main()
browser.quit()

beep_when_done()
print("Script has completed all tasks in %s seconds." % (time.time() - start_time))