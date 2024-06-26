# WildCAD Alert System
This system generates email alerts for new smoke checks and wildfires, pulled directly from WildCAD. [Here is a briefing video for this product](https://www.youtube.com/watch?v=IzJMHeuVztE). Below are the steps to follow for getting things working.

</br>
</br>

1. [Download this repository](https://github.com/mpanunto/WildCAD_Alert_System/archive/refs/heads/main.zip) and extract the files.

</br>
</br>

2. Customize your "WildCAD_Alert_Templates.aprx" layouts to your liking.
   - For Utah, I created a layout for each dispatch center in order to have unique inset maps. For ease of setup, I would recommend the same approach.
   - Change the names of the layouts and maps so they correspond to your dispatch centers of interest. Only change the standard 5 character dispatch abbreviations.
   - Due to hardcoded references in the script, DO NOT change the following elements of the templates:
      - Layout title/subtitle text
      - "WildCAD Fire Location" layer name
      - "Layers Map Frame" map frame name
      - "Layers" map name       

</br>
</br>

3. Setup the "FieldOfficeBoundaries" GDB feature class.
   - Unzip "FieldOfficeBoundaries.gdb.zip"   
   - Ensure feature class has full data coverage of your dispatch centers of interest.
   - Follow the same schema as the provided dataset
      - ADMU_NAME (field office)
      - PARENT_NAME (district)
      - ADMIN_ST (state)
   
   
</br>
</br>

4. Setup your "WildCAD_Alert_Emails.xlsx" spreadsheet.
   - Rename the column names so they correspond to your dispatch centers of interest. Only change the standard 5 character dispatch abbreviations.
   

</br>
</br>

5. Setup dummy email account.
   - This account will be sending the automated email alerts. I use a Gmail account.
   - An "App Password" is needed for Python to access a Gmail account to automate email sending. An App Password is a password that is generated so that a third-party app can connect to a Gmail account. This password can then be used instead of the Google account password when using that app.
   - To create an App Password for a Gmail account, first you will need to setup 2-Step Verification with the account. Once that is completed, go here: https://myaccount.google.com/apppasswords

![screenshot_GmailSetup_1.png](https://raw.githubusercontent.com/mpanunto/WildCAD_Alert_System/main/docs/screenshot_GmailSetup_1.png)


</br>
</br>

6. Modify Python script inputs at top of script
   - Change file paths
   - Change list of dispatch centers, use the standard 5 character abbreviations
   - Specify dummy email address and password (the App Password generated in step 4)
   - Specify recipient of error alert emails
   - Specify output coordinate system

</br>
</br>

7. Run script
   - I have the script running on a dedicated machine using Windows Task Scheduler, set to run every minute.






