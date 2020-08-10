

$latest_folder = Get-ChildItem -Path "G:\My Drive\SEM Print Tool\" | Sort-Object CreationTime -Descending | Select-Object -First 1
$copy_DASH_File_Uploader = Copy-Item -Path "G:\My Drive\SEM Print Tool\DASH File Uploader - for Powershell.py" -Destination $latest_folder
$copy_certificate_folder_to_here = "\\redbull\public\SEM\Building Science Team\Energy Star Certification Material\HERC\2020\Q3"
# $current_date_yyyy_mm_dd = Get-Date -Format "yyyy-mm-dd"


$copy_DASH_File_Uploader

Write-Output "We have copied DASH File Uploader - for Powershell.py into the most most recent folder: $latest_folder"
Set-Location $latest_folder
Write-Output "We are inside $latest_folder"
Write-Output "We are going to begin running DASH File Uploader - for Powershell.py"
python '.\DASH File Uploader - for Powershell.py'
Write-Output "We should be done uploading into DASH now."

Write-Output "We will now copy all the contents of $latest_folder to $copy_certificate_folder_to_here"

Copy-Item "." -Destination $copy_certificate_folder_to_here -Recurse

Write-Output "We have copied everything to the S Drive!"