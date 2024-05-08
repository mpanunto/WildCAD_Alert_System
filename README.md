# WildCAD Alert System
Email alerts for new smoke checks and wildfires, pulled from WildCAD


1) Customize your "WildCAD_Alert_Templates.aprx" layouts to your liking.
   -For Utah, I created a layout for each dispatch center to have unique inset maps.
   -For easiest setup, do not change the layout title text, or the "WildCAD Fire Location" layer name. These are hardcoded references for the script.
3) Setup your WildCAD_Alert_Emails.xlsx so that they correspond to your dispatch centers of interest.
4) Setup dummy gmail account.

5) Update script



In order for my Python environment to have access to my dummy gmail account (logging into the account and sending emails), I had to create an App Password. An app password is a password that is generated so that a third-party app can connect to your Gmail account. You then use it instead of your Google account password when using that app.

To create an app password for your dummy account: go here: https://myaccount.google.com/apppasswords

![screenshot_GmailSetup_1.png](https://raw.githubusercontent.com/mpanunto/WildCAD_Alert_System/main/Docs/screenshot_GmailSetup_1.png)



