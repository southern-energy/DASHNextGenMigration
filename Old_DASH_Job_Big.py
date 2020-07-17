'''
Created on Nov 2, 2016

@author: will
'''
from robobrowser import RoboBrowser #for navigating and form submission
import datetime
from datetime import timedelta, date
import time
import csv
import pandas as pd
import MySQLdb
import os

start_time = time.time()

browser = RoboBrowser(parser="lxml") 
browser.open('http://sem.myirate.com/login.asp')
login_form = browser.get_form(action='login.asp')

#login to Dash
login_form['txtSiteID'].value = "SEM"
login_form['txtUser'].value = "Will"
login_form['txtPasswd'].value = "babywill7"
browser.submit_form(login_form)

#go to my Job Report Page
browser.open('http://sem.myirate.com/reports/adHocReportingview.asp?id=1220')

now = date.today()
now = now - timedelta(days=0)  #   most recent date, normally today so: "days = 0", 
                                #    unless you want to just grab info from 
                                #    just the distant and not today, in which case you could make this "days = 365" 
                                #    and the start variable below "days = 365" to get all jobs between 1 and 2 years ago-- or whatever range you want!
start = now - timedelta(days=730) #go back X days and get jobs
print(start)
 
#10 day increments should keep us from hitting max of 500 rows per query
N = 5
#define list of jobs
values = []
#date loop
while start < now:        
    startPeriod = start.strftime('%m/%d/%Y')
    print(startPeriod)
    if start + timedelta(days=N) < now:
        #loop for N days until we get to today
        start += timedelta(days=N)
        midEnd = start - timedelta(days=1)
        #pass n - 1 to dash form so we don't overlap date filters
        endPeriod = midEnd.strftime('%m/%d/%Y')
    else:
        #make sure we end loop on today
        start = now
        endPeriod = start.strftime('%m/%d/%Y')
    print(endPeriod)
    #pass date filters to asp form with robobrowser
    report_form = browser.get_form(action='adHocReportingView.asp')
    report_form['LimitValue0'].value = 1
    report_form['LimitValue1'].value = startPeriod
    report_form['LimitValue1a'].value = endPeriod        
    browser.submit_form(report_form)    
    #print(browser.parsed) 
    #data is stored in HTML table elements, find all the tables
    table = browser.find_all('table')
    #the 4th table (index 3) has the data we want, get all of the tr elements out of it
    rows = table[3].find_all('tr')    
    #define column headers from 1st row of table
    headers = [header.text for header in rows[0].find_all('td')]    
    #build 
    for i in range(1,len(rows)-1):
        values.append( [value.text for value in rows[i].find_all('td')])    
    time.sleep(1)  #take 5 seconds off between calls to Dash Server
    print(headers)
keys = ['RatingID', 'JobNumber', 'Address', 'City', 'State', 'Zip', 'Builder', 'Subdivision', 'GasUtility', 'ElectricUtility', 'Lot', 'Division', 'HERSIndex', 'BldgFile', 'DateEntered', 'EkotropeStatus', 'EkotropeProjectName', 'EkotropeProjectLink']    
df = pd.DataFrame(values, columns = keys)
 
df['DateEntered'] =  pd.to_datetime(df['DateEntered'])
df['EkotropeProjectLink'] =  df['EkotropeProjectLink'].str[-8:]
# print(df['dateentered'])
# with open("DashJOB.csv", "w", newline='', encoding='utf8') as f:
#     writer = csv.writer(f)
#     writer.writerows(values)        
# print('all done')
#send to MySQL database
df = df.replace({',': '.'}, regex=True) # remove all commas
df = df.replace({';': '.'}, regex=True) # remove all commas
df = df.replace({r'\r': ' '}, regex=True)# remove all returns
df = df.replace({r'\n': ' '}, regex=True)# remove all newlines
 
mydb = MySQLdb.connect(
    host='104.154.197.202',
    port=3306,
    user='will_etheridge',
    passwd='M!ll_<3s_fr0g$',
    db='sem_dash',
    charset='utf8',
    local_infile = 1)
cursor = mydb.cursor()
df.to_csv('TEMPO.csv', encoding='utf-8',index=False)
 
 
path= os.getcwd()+"\\TEMPO.csv"
print (path+"\\")
path = path.replace('\\', '/')
 
cursor.execute('LOAD DATA LOCAL INFILE \"'+ path +'\" REPLACE INTO TABLE `job` FIELDS TERMINATED BY \',\' ignore 1 lines;')
 
# #close the connection to the database.
mydb.commit()
cursor.close()
      
print("--- %s ran in --- %s seconds ---" % (str(os.path.basename(__file__)),(time.time() - start_time)))
