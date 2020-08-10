'''
from StackExchange
http://stackoverflow.com/questions/8316818/login-to-website-using-python
Thanks Acorn!
@author: will
'''
import requests, zipfile
from io import StringIO
import datetime
from datetime import timedelta, date
import time
from bs4 import BeautifulSoup
import shutil
import os

SITEID = 'sem'
EMAIL = 'gregory'
PASSWORD = 'Scheduling!'
URL = 'http://sem.myirate.com/login.asp'

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:  
    # This is the form data that the page sends when logging in
    login_data = {
        'txtSiteID': SITEID,
        'txtUser': EMAIL,
        'txtPasswd': PASSWORD,
        'Submit': 'Submit',    }
   
    p = s.post(URL, data=login_data) #Authenticate
    DL_URL = ('http://sem.myirate.com/jobs/uploadFile11.asp')#dash file upload form

path= os.getcwd()
newpath = path+'\\'+ 'Successfully_Uploaded'
newpath2 = path+'\\'+ 'already_uploaded'
if not os.path.exists(newpath):
    os.makedirs(newpath)
if not os.path.exists(newpath2):
    os.makedirs(newpath2)

for filename in os.listdir('.'):
    if filename.endswith(".pdf") and 'Cert' in filename :
       # get rating id from first section of file name
        ratingid = filename.split('_', 1)[0]
        print(ratingid) 
        bowl = s.get("http://sem.myirate.com/jobs/builderphotos.asp?id=%s" % ratingid)#navigate to job page to get certifcate file id
        soup = BeautifulSoup(bowl.content, "lxml")
        existingCert = soup.find_all("table")[10].find_all("tr")[5].find_all('td')[1].get_text()    
        if 'pdf' not in str(existingCert):
            print('passed')            
            payload = {'jobID': ratingid}
            with open(path + '\%s' % filename,'rb') as myfile:
                files = {'File2': myfile}       
                req = s.post(DL_URL, files=files, data=payload)
            time.sleep(5)  #take time off between calls to server
            bowl = s.get("http://sem.myirate.com/jobs/builderphotos.asp?id=%s" % ratingid)#navigate to job page to get certifcate file id
            soup = BeautifulSoup(bowl.content, "lxml")
            inputs = soup.find_all("input", {"name":"fileID"})   
            fileid = inputs[0]['value']#second input with name "fileID" is the input we want to change to share with the builder
            print(fileid)
            fileurl = "http://sem.myirate.com/jobs/builderphotos.asp"
            payload = {"btnSubmit":"Save",
            "updateQueue":"yes",
            "jobID":ratingid,
            "tableID":0,
            "fileID":fileid,
            "Builder":'1'}
            req = s.post(fileurl, data=payload)  
            shutil.move(path + '\\' + filename, newpath + "\\" + filename)
        else:
            print('failed')
            shutil.move(path + '\\' + filename, 'already_uploaded' + "\\" + filename)                
print('all done')

# Adding a Beep for when the program finishes.
import winsound
import time
def beep_when_done():
    #Attributes
    duration_short = 100  # milliseconds
    duration_long = 300  # milliseconds
    freq = 400  # Hz
    freq2 = 200 

    winsound.Beep(freq, duration_short)
    winsound.Beep(freq2, duration_long)
    winsound.Beep(freq, duration_short)

beep_when_done()

# Closes Python Environment so we can get back to Powershell

quit()
