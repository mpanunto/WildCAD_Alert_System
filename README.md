# WildCAD Alert System
Email alerts for new smoke checks and wildfires, pulled from WildCAD

</br>
</br>

1. Customize your "WildCAD_Alert_Templates.aprx" layouts to your liking.
   - For Utah, I created a layout for each dispatch center to have unique inset maps. For ease of setup, I would recommend the same approach.
   - Change the names of the layouts and maps so they correspond to your dispatch centers of interest. Use the standard 5 character dispatch abbreviations.
   - Due to hardcoded references in the script, DO NOT change the following elements of the templates:
      - Layout title/subtitle text
      - "WildCAD Fire Location" layer name
      - "Layers Map Frame" map frame name
      - "Layers" map name       

</br>
</br>

2. Setup the "FieldOfficeBoundaries" feature class.
   - DO NOT change the filename of the GDB or feature class
   - Ensure it has full data coverage of your dispatch centers of interest.
   - Follow the same schema as the provided dataset
      - ADMU_NAME (field office)
      - PARENT_NAME (district)
      - ADMIN_ST (state)
   

</br>
</br>

3. Setup your "WildCAD_Alert_Emails.xlsx"
   - Rename the column names so they correspond to your dispatch centers of interest. Use the standard 5 character dispatch abbreviations.

</br>
</br>

4. Setup dummy gmail account.

</br>
</br>

5. Update Python script
   - Change file paths at top of script
   - Change list of dispatch centers at top of script, use the standard 5 character abbreviations
   - Set output coordinate system at top of script 



In order for my Python environment to have access to my dummy gmail account (logging into the account and sending emails), I had to create an App Password. An app password is a password that is generated so that a third-party app can connect to your Gmail account. You then use it instead of your Google account password when using that app.

To create an app password for your dummy account: go here: https://myaccount.google.com/apppasswords

![screenshot_GmailSetup_1.png](https://raw.githubusercontent.com/mpanunto/WildCAD_Alert_System/main/Docs/screenshot_GmailSetup_1.png)



