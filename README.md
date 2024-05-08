# WildCAD Alert System
Email alerts for new smoke checks and wildfires, pulled from WildCAD

</br>
</br>

1. Customize your "WildCAD_Alert_Templates.aprx" layouts to your liking.
   - For Utah, I created a layout for each dispatch center in order to have unique inset maps. For ease of setup, I would recommend the same approach.
   - Change the names of the layouts and maps so they correspond to your dispatch centers of interest. Use the standard 5 character dispatch abbreviations.
   - Due to hardcoded references in the script, DO NOT change the following elements of the templates:
      - Layout title/subtitle text
      - "WildCAD Fire Location" layer name
      - "Layers Map Frame" map frame name
      - "Layers" map name       

</br>
</br>

2. Setup the "FieldOfficeBoundaries" feature class.   
   - Ensure it has full data coverage of your dispatch centers of interest.
   - Follow the same schema as the provided dataset
      - ADMU_NAME (field office)
      - PARENT_NAME (district)
      - ADMIN_ST (state)
   

</br>
</br>

3. Setup your "WildCAD_Alert_Emails.xlsx"
   - Rename the column names so they correspond to your dispatch centers of interest. Use the standard 5 character dispatch abbreviations.
   - DO NOT remove the "_SmokeCheck_SmallFire" and "_LargeFire" text in the column names.

</br>
</br>

4. Setup dummy gmail account.
   - In order for my Python environment to have access to my dummy gmail account (logging into the account and sending emails), I had to create an App Password. An app password is a password that is generated so that a third-party app can connect to your Gmail account. You then use it instead of your Google account password when using that app.
   - To create an app password for your dummy account: go here: https://myaccount.google.com/apppasswords

![screenshot_GmailSetup_1.png](https://raw.githubusercontent.com/mpanunto/WildCAD_Alert_System/main/Docs/screenshot_GmailSetup_1.png)

</br>
</br>

5. Modify Python script inputs at top of script
   - Change file paths
   - Change list of dispatch centers, use the standard 5 character abbreviations
   - Specify dummy email address and password
   - Specify recipient of error alert emails
   - Specify output coordinate system






