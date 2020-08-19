POWERSHELL VERSION

Before you begin, you must open up an instance of Windows Powershell. You can type it into the search bar or you can use the Keyboard Shortcut "Windows Key + R" then type "powershell" and hit Enter.

To Copy and Paste into Windows Powershell you can use your usual "Ctrl + C" and "Ctrl + V" commands.

The code segments you'll be copying are inside the sections marked with tildes "~~~~".

=====================================================

STEP 1:

This will open up the Excel sheet you need to put your DASH IDs in.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
start 'G:\Shared drives\BES - Builder Services Team\Non-Energy Star Certification Scripts\nonEnergyStarClickBot\nonEnergyStarClickBot\NonEnergyStarDashClickerSheet.xlsx'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once you have saved the DASH ID's you want to queue inside the sheet. You can run the script 'clickBot.py'

=====================================================

STEP 2:

Run the clickBot.py script. If you run into issues with not having any modules, use "pip install " (be sure to include the module it says you don't have to install the module).

STEP 2.1:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Set-Location 'G:\Shared drives\BES - Builder Services Team\Non-Energy Star Certification Scripts\nonEnergyStarClickBot\nonEnergyStarClickBot\' ; python .clickBot.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STEP 2.2:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python .\clickBot.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

--------------------------------

=====================================================

STEP 3:

Once you have put the DASH ID's into the "Queued" tab of the "Non-E* Process Sheet" run the scripts below. You can copy and paste the whole line into Windows Powershell.

-------START of STEP 3 ASIDE----------------

NOTE: The scripts below will individually beep when they are done running. You're going to hear a series of three beeps. For an example of what you're going to hear:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python 'G:\My Drive\PythonDev\Dash\Beeper_Sample.py'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-------END of STEP 3 ASIDE------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set-Location 'G:\My Drive\PythonDev\Ekotrope\Live' ; python 'G:\My Drive\PythonDev\Ekotrope\Live\EkoDataPull_2.5 - BeeperEdition.py' ; Set-Location 'G:\My Drive\PythonDev\Dash\' ; python 'G:\My Drive\PythonDev\Dash\Dash_Sync_Master_Big - BeeperEdition.py'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=====================================================

STEP 4:

After you have heard your series of beeps saying that everything is complete, you need to open the Print Tool Excel File 'BES Cert Print_Eko_1.12'. You are going to have to troubleshoot using the Excel sheet from here.

-------START of STEP 4 ASIDE----------------

Issue: "Nothing is in Column 2"

Solution: You're going to have to double check that "Queued" tab of the "Non-E* Process Sheet" from earlier.

Issue: "Already Printed"

Solution: I usually go to the DASH ID, download the certificate that is already in there and move it into the "Other Files" section in DASH and delete the existing one. The easier way is to manually Copy and Paste the DASH ID into the Column 3 AFTER you have done this.

Issue: "Not Registered"

Solution: You're going to have to go to register the DASH ID with Ekotrope. Ask Jamie/Debi/Sara Caliendo.

-------END of STEP 4 ASIDE------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
start 'G:\My Drive\SEM Print Tool\BES Cert Print_Eko_1.12.xlsm'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=====================================================

STEP 5:

After clicking the Update and Print Certificates and it is done "Publishing" the Certificates. We are going to run "CopyDASHFileUploaderIntoNewestDirectory.ps1", it is a Windows Powershell script that will copy the script that uploads DASH ID's into DASH, runs that Python Script, then once it is done running, it will upload the certificates to the S Drive.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Set-Location 'G:\My Drive\SEM Print Tool' ; .\CopyDASHFileUploaderIntoNewestDirectory.ps1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IF ABOVE DOESN'T WORK! USE THIS BELOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Set-ExecutionPolicy -Scope CurrentUser ; Set-Location 'G:\My Drive\SEM Print Tool' ; .\CopyDASHFileUploaderIntoNewestDirectory.ps1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=====================================================
