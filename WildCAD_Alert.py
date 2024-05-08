import arcpy, arcgis, os, sys, datetime, pandas, bs4, html5lib, zipfile, shutil, csv, email, smtplib, json
import email.mime.multipart
import email.mime.text


########################################################################################################
### BEGIN USER INPUT
########################################################################################################

#Read-in the csv log file
wildcad_log_path = r"C:\Workspace\OneDrive\Code\WildCAD_Alert/WildCAD_Alert_Log.csv"
wildcad_log_df = pandas.read_csv(wildcad_log_path, encoding="ISO-8859-1")

#Read-in the email list
wildcad_emails_path = r"C:\Workspace\OneDrive\Code\WildCAD_Alert/WildCAD_Alert_Emails.xlsx"
wildcad_emails_df = pandas.read_excel(wildcad_emails_path)

#Alert map output directory
wildcad_map_dir = r"C:\Workspace\OneDrive\Code\WildCAD_Alert/WildCAD_Alert_Maps"

#Paths to template aprx
template_aprx = r"C:\Workspace\OneDrive\Code\WildCAD_Alert\Templates\ArcGISPro/WildCAD_Alert_Templates.aprx"

#Specify path to Field Office Boundary feature class
#This feature class contains information for State, District, and Field Office
fo_bndry_fc_path = r"C:\Workspace\Layers\Boundaries\FieldOfficeBoundaries.gdb/FieldOfficeBoundaries"

#Specify dispatch centers to process, using 5 character abbreviations
dispatch_list = ["UTCDC", "UTMFC", "UTNUC", "UTRFC", "UTUBC", "AZFDC", "IDEIC", "NVECC"]

#Specify dummy email address, and password
#This is the email that will be sending out the wildfire alert emails
email_sender = 'yourdummyemail@gmail.com'
email_password = 'xxxxxxxxxxxxxx'

#Specify recipient of error alert emails
#If the script encounters and error, it will send an email alert to this recipient.
receiverEmail_errors = "yourworkorpersonalemail@email.com"

#Specify output coordinate system WKID
out_crs = 26912

########################################################################################################
### END USER INPUT
########################################################################################################


try:

    base_URL = "https://snknmqmon6.execute-api.us-west-2.amazonaws.com/centers/DISPATCH/incidents"

    df_dispatch_list = []
    for i in range(0, len(dispatch_list)):
        curr_dispatch = dispatch_list[i]
        dispatch_URL = base_URL.replace("DISPATCH", curr_dispatch)

        df_json = pandas.read_json(dispatch_URL)
        df_json_data = df_json["data"][0]

        #If json returns nan, skip. Else, create dataframe
        if(str(df_json_data) == "nan"):
            continue
        else:
            df_dispatch = pandas.DataFrame(df_json_data)

        if(len(df_dispatch) > 0):
            df_dispatch["Dispatch"] = curr_dispatch
            df_dispatch_list.append(df_dispatch)

    all_df = pandas.concat(df_dispatch_list)

    #Now sort by the new DateTime field
    all_df.sort_values(by="date", ascending=False, inplace=True)

    #Filter out lat/long values (NA's)
    all_df_filter1 = all_df[~pandas.isna(all_df['latitude']) & ~pandas.isna(all_df['longitude'])]
    all_df_filter1.reset_index(inplace=True)

    #Filter out wildfires that have an acreage of NA
    all_df_filter2 = all_df_filter1[ ~( (all_df_filter1["type"] == "Wildfire") & (pandas.isna(all_df_filter1["acres"])) )]

    #Filter out bad lat/long values ((*******'s))
    all_df_filter3 = all_df_filter2[(all_df_filter2['latitude'] != "*******") & (all_df_filter2['longitude'] != "*******")]

    #Convert latitude and longitude fields to float
    all_df_filter3["latitude"] = all_df_filter3["latitude"].astype(float)
    all_df_filter3["longitude"] = all_df_filter3["longitude"].astype(float)

    #Filter out 0 lat/long values (0's)
    all_df_filter4 = all_df_filter3[(all_df_filter3['latitude'] != 0) & (all_df_filter3['longitude'] != 0)]

    #Cleanup fields
    all_df_filter4['date'] = pandas.to_datetime(all_df_filter4['date'])
    all_df_filter4['acres'] = all_df_filter4['acres'].astype(float)
    all_df_filter4["longitude"] = all_df_filter4["longitude"] * -1

    #Create lat/long fields
    lat_ddm_list = []
    lat_ddm_dir_list = []
    lat_ddm_dir_format_list = []
    long_ddm_list = []
    long_ddm_dir_list = []
    long_ddm_dir_format_list = []
    lat_long_dd_list = []
    lat_long_dd_dir_list = []
    lat_long_ddm_list = []
    lat_long_ddm_dir_list = []
    lat_long_ddm_dir_format_list = []
    for i in range(0, len(all_df_filter4)):

        #Create lat variables
        curr_lat_dd = all_df_filter4.iloc[i]["latitude"]
        curr_lat_dd_str = str(curr_lat_dd)
        curr_lat_dd_dir = curr_lat_dd_str + "N"
        curr_lat_deg = curr_lat_dd_str.split(".")[0]
        curr_lat_dm = round(float("0." + curr_lat_dd_str.split(".")[1]) * 60, 3)
        curr_lat_ddm = curr_lat_deg + " " + str(curr_lat_dm)
        curr_lat_ddm_dir = curr_lat_ddm + "N"
        curr_lat_ddm_dir_format = curr_lat_deg + chr(176) + " " + str(curr_lat_dm) + "'N"

        #Create long variables
        curr_long_dd = all_df_filter4.iloc[i]["longitude"]
        curr_long_dd_str = str(curr_long_dd)
        curr_long_dd_dir = curr_long_dd_str.replace("-", "") + "W"
        curr_long_deg = curr_long_dd_str.split(".")[0]
        curr_long_dm = round(float("0." + curr_long_dd_str.split(".")[1]) * 60, 3)
        curr_long_ddm = curr_long_deg + " " + str(curr_long_dm)
        curr_long_ddm_dir = curr_long_ddm.replace("-", "") + "W"
        curr_long_ddm_dir_format = curr_long_deg.replace("-", "") + chr(176) + " " + str(curr_long_dm) + "'W"

        #Create lat/long variables
        curr_lat_long_dd = curr_lat_dd_str + ", " + curr_long_dd_str
        curr_lat_long_dd_dir = curr_lat_dd_dir + ", " + curr_long_dd_dir
        curr_lat_long_ddm = curr_lat_ddm + ", " + curr_long_ddm
        curr_lat_long_ddm_dir = curr_lat_ddm_dir + ", " + curr_long_ddm_dir
        curr_lat_long_ddm_dir_format = curr_lat_ddm_dir_format + ", " + curr_long_ddm_dir_format


        #Build lat lists
        lat_ddm_list.append(curr_lat_ddm)
        lat_ddm_dir_list.append(curr_lat_ddm_dir)
        lat_ddm_dir_format_list.append(curr_lat_ddm_dir_format)

        #Build long lists
        long_ddm_list.append(curr_long_ddm)
        long_ddm_dir_list.append(curr_long_ddm_dir)
        long_ddm_dir_format_list.append(curr_long_ddm_dir_format)

        #Build lat/long lists
        lat_long_dd_list.append(curr_lat_long_dd)
        lat_long_dd_dir_list.append(curr_lat_long_dd_dir)
        lat_long_ddm_list.append(curr_lat_long_ddm)
        lat_long_ddm_dir_list.append(curr_lat_long_ddm_dir)
        lat_long_ddm_dir_format_list.append(curr_lat_long_ddm_dir_format)

    #Create new lat/long dataframe fields
    all_df_filter4["lat_ddm"] = lat_ddm_list
    all_df_filter4["lat_ddm_dir"] = lat_ddm_dir_list
    all_df_filter4["lat_ddm_dir_format"] = lat_ddm_dir_format_list

    all_df_filter4["long_ddm"] = long_ddm_list
    all_df_filter4["long_ddm_dir"] = long_ddm_dir_list
    all_df_filter4["long_ddm_dir_format"] = long_ddm_dir_format_list

    all_df_filter4["lat_long_dd"] = lat_long_dd_list
    all_df_filter4["lat_long_dd_dir"] = lat_long_dd_dir_list
    all_df_filter4["lat_long_ddm"] = lat_long_ddm_list
    all_df_filter4["lat_long_ddm_dir"] = lat_long_ddm_dir_list
    all_df_filter4["lat_long_ddm_dir_format"] = lat_long_ddm_dir_format_list


    ########################################################################################################
    # IDENTIFY NEW SMOKE CHECKS
    ########################################################################################################

    #Filter the log file to only smokechecks
    smokecheck_log_df = wildcad_log_df[wildcad_log_df["Alert"] == "SmokeCheck"]
    smokecheck_log_date_list = list(smokecheck_log_df["Date"])
    smokecheck_log_name_list = list(smokecheck_log_df["Name"])
    smokecheck_log_lat_list = list(smokecheck_log_df["Latitude_DDM"])
    smokecheck_log_long_list = list(smokecheck_log_df["Longitude_DDM"])
    smokecheck_log_latlong_list = [i + ", " + j for i, j in zip(smokecheck_log_lat_list, smokecheck_log_long_list)]

    #Now create a new dataframe from WildCAD scrape, keep only smoke checks
    smokecheck_df = all_df_filter4[all_df_filter4["type"] == "Smoke Check"]

    #Want to reduce alerts, but dispatch updates fire names and lat/longs frequently early on. So, trying to
    #reduce them by determining which entries are truly unique.
    #An incident is considered unique only if their discover date, name, and lat/long cannot be found in the log
    new_smokechecks_list = []
    if( len(smokecheck_df) > 0 ):

        for i in range(0, len(smokecheck_df)):

            curr_datetime = list(smokecheck_df["date"])[i]
            curr_datetime_format = datetime.datetime.strftime(curr_datetime, "%Y/%m/%d %H:%M")
            curr_type = list(smokecheck_df["type"])[i]
            curr_latlong = list(smokecheck_df["lat_long_ddm_dir"])[i]
            curr_name = list(smokecheck_df["name"])[i]

            #Some dispatch centers put "//" in front of the incident name until it's more finalized. Account for that here.
            if(curr_name[0:2] == "//"):
                curr_name = curr_name.replace("//", "")

            #Perform discovery date test
            date_test = "Pass"
            if(curr_datetime_format in smokecheck_log_date_list):
                date_test = "Fail"

            #Perform name test
            name_test = "Pass"
            if(curr_name in smokecheck_log_name_list):
                name_test = "Fail"

            #If the smokecheck fails the name test, check to see if the name is "New"
            #If it is, force the smokecheck to pass the name test
            if(curr_name == "New"):
                name_test = "Pass"

            #If the smokecheck still fails the incident name test, check to see if the conflicting smokechecks are all greater than 1 day old.
            #If they are, force the smokecheck to pass the name test
            if(name_test == "Pass"):
                conflict_dates = smokecheck_log_df[smokecheck_log_df["Name"] == curr_name]["Date"]

                if(len(conflict_dates) > 0):

                    conflict_datetimes = pandas.to_datetime(conflict_dates, format="%Y%m%d %H:%M")
                    conflict_time_diff = curr_datetime - conflict_datetimes
                    timedelta_1_day = pandas.Timedelta(1, unit="days")

                    if(all( conflict_time_diff > timedelta_1_day )):
                        name_test = "Pass"


            #Perform lat/long test
            latlon_test = "Pass"
            if(curr_latlong in smokecheck_log_latlong_list):
                latlon_test = "Fail"

            #Determine if the record failed any of the tests
            if(date_test == "Pass" and name_test == "Pass" and latlon_test == "Pass"):
                new_smokechecks_list.append(i)


    #Create dataframe of new small fires, create empty dataframe if none
    if( len(new_smokechecks_list) > 0 ):
        new_smokechecks_df = smokecheck_df.iloc[new_smokechecks_list]
        new_smokechecks_df["Alert"] = "SmokeCheck"

    else:
        new_smokechecks_df = pandas.DataFrame()



    ########################################################################################################
    # IDENTIFY NEW SMALL WILDFIRES (<10ac)
    ########################################################################################################

    #Filter the log file to only Smoke Checks and Small Wildfires
    smallfire_log_df = wildcad_log_df[wildcad_log_df["Alert"].isin(["SmokeCheck", "SmallFire"])]
    smallfire_log_date_list = list(smallfire_log_df["Date"])
    smallfire_log_name_list = list(smallfire_log_df["Name"])
    smallfire_log_lat_list = list(smallfire_log_df["Latitude_DDM"])
    smallfire_log_long_list = list(smallfire_log_df["Longitude_DDM"])
    smallfire_log_latlong_list = [i + ", " + j for i, j in zip(smallfire_log_lat_list, smallfire_log_long_list)]

    #Now create a new dataframe from WildCAD scrape, keep only Small Wildfires (<10ac)
    smallfire_df = all_df_filter4[all_df_filter4["type"] == "Wildfire"]
    smallfire_df = smallfire_df[smallfire_df["acres"] < 10]
    smallfire_df.reset_index(inplace=True, drop=True)


    #Want to reduce alerts, but dispatch updates fire names and lat/longs frequently early on. So, trying to
    #reduce them by determining which entries are truly unique.
    #An incident is considered unique only if their discover date, name, and lat/long cannot be found in the log
    new_smallfires_list = []
    if( len(smallfire_df) > 0 ):

        for i in range(0, len(smallfire_df)):

            curr_datetime = list(smallfire_df["date"])[i]
            curr_datetime_format = datetime.datetime.strftime(curr_datetime, "%Y/%m/%d %H:%M")
            curr_type = list(smallfire_df["type"])[i]
            curr_latlong = list(smallfire_df["lat_long_ddm_dir"])[i]
            curr_name = list(smallfire_df["name"])[i]

            #Some dispatch centers put "//" in front of the incident name until it's more finalized. Account for that here.
            if(curr_name[0:2] == "//"):
                curr_name = curr_name.replace("//", "")

            #Perform discovery date test
            date_test = "Pass"
            if(curr_datetime_format in smallfire_log_date_list):
                date_test = "Fail"

            #Perform name test
            name_test = "Pass"
            if(curr_name in smallfire_log_name_list):
                name_test = "Fail"

            #Perform lat/long test
            latlon_test = "Pass"
            if(curr_latlong in smallfire_log_latlong_list):
                latlon_test = "Fail"

            #Determine if the record failed all of the tests
            if(date_test == "Pass" and name_test == "Pass" and latlon_test == "Pass"):
                new_smallfires_list.append(i)


    #Create dataframe of new small fires, create empty dataframe if none
    if( len(new_smallfires_list) > 0 ):
        new_smallfires_df = smallfire_df.iloc[new_smallfires_list]
        new_smallfires_df["Alert"] = "SmallFire"

    else:
        new_smallfires_df = pandas.DataFrame()



    ########################################################################################################
    # IDENTIFY NEW LARGE WILDFIRES (>=10ac)
    ########################################################################################################

    #Filter the log file to only Smoke Checks and Small Wildfires
    largefire_log_df = wildcad_log_df[wildcad_log_df["Alert"].isin(["LargeFire"])]
    largefire_log_date_list = list(largefire_log_df["Date"])
    largefire_log_name_list = list(largefire_log_df["Name"])
    largefire_log_lat_list = list(largefire_log_df["Latitude_DDM"])
    largefire_log_long_list = list(largefire_log_df["Longitude_DDM"])
    largefire_log_latlong_list = [i + ", " + j for i, j in zip(largefire_log_lat_list, largefire_log_long_list)]

    #Now create a new dataframe from WildCAD scrape, keep only Large Wildfires (<10ac)
    largefire_df = all_df_filter4[all_df_filter4["type"] == "Wildfire"]
    largefire_df = largefire_df[largefire_df["acres"] >= 10]
    largefire_df.reset_index(inplace=True, drop=True)


    #Want to reduce alerts, but dispatch updates fire names and lat/longs frequently early on. So, trying to
    #reduce them by determining which entries are truly unique.
    #An incident is considered unique only if their discover date, name, and lat/long cannot be found in the log
    new_largefires_list = []
    if( len(largefire_df) > 0 ):

        for i in range(0, len(largefire_df)):

            curr_datetime = list(largefire_df["date"])[i]
            curr_datetime_format = datetime.datetime.strftime(curr_datetime, "%Y/%m/%d %H:%M")
            curr_type = list(largefire_df["type"])[i]
            curr_latlong = list(largefire_df["lat_long_ddm_dir"])[i]
            curr_name = list(largefire_df["name"])[i]

            #Perform discovery date test
            date_test = "Pass"
            if(curr_datetime_format in largefire_log_date_list):
                date_test = "Fail"

            #Perform name test
            name_test = "Pass"
            if(curr_name in largefire_log_name_list):
                name_test = "Fail"

            #Perform lat/long test
            latlon_test = "Pass"
            if(curr_latlong in largefire_log_latlong_list):
                latlon_test = "Fail"

            #Determine if the record failed all of the tests
            if(date_test == "Pass" and name_test == "Pass" and latlon_test == "Pass"):
                new_largefires_list.append(i)


    #Create dataframe of new small fires, create empty dataframe if none
    if( len(new_largefires_list) > 0 ):
        new_largefires_df = largefire_df.iloc[new_largefires_list]
        new_largefires_df["Alert"] = "LargeFire"

    else:
        new_largefires_df = pandas.DataFrame()





    ##################################################################################################################
    #COMBINE THE WILDCAD SMOKE CHECKS, SMALL FIRES, AND LARGE FIRES INTO A SINGLE DATAFRAME
    ##################################################################################################################

    #Merge dataframes, and reset index
    new_fires_combined_df = pandas.concat([new_smokechecks_df, new_smallfires_df, new_largefires_df])
    new_fires_combined_df.reset_index(inplace=True, drop=True)

    ###################################################################################################################
    # PROCESS SMOKE CHECK, SMALL WILDFIRE, AND LARGE WILDFIRE ALERTS
    ###################################################################################################################

    #if the new fire list has 1 or more smokechecks, small fires, or large fires...
    if( len(new_fires_combined_df) > 0 ):


        #Drop un-needed fields from dataframe
        #new_fires_combined_df.drop(['ic', 'uuid', 'fuels', 'fire_num', 'location', 'resources', 'webComment'], axis=1, inplace=True)

        #Read in Field Office Feature Class to spatial dataframe
        fo_bndry_sdf = arcgis.GeoAccessor.from_featureclass(fo_bndry_fc_path)

        #Loop through each fire in the list, and process one at a time
        for i in range(0, len(new_fires_combined_df)):

            curr_fire_df = new_fires_combined_df.iloc[[i]]

            #Define fire date, name, and reported acreage
            curr_fire_datetime = list(curr_fire_df["date"])[0]
            curr_fire_datetime_format = datetime.datetime.strftime(curr_fire_datetime, "%Y/%m/%d %H:%M")

            curr_fire_name = list(curr_fire_df["name"])[0]
            if(curr_fire_name[0:2] == "//"):
                curr_fire_name = curr_fire_name.replace("//", "")
            curr_fire_name_alphanum = ''.join(filter(str.isalpha, curr_fire_name))

            print(".." + curr_fire_name)

            #The "fire_status" field is a dictionary, extract that here
            firestatus_string = curr_fire_df.iloc[0]["fire_status"]
            firestatus_dict = json.loads(firestatus_string)

            #The "fiscal_data" field is a dictionary, extract that here
            fiscaldata_string = curr_fire_df.iloc[0]["fiscal_data"]
            fiscaldata_dict = json.loads(fiscaldata_string)

            curr_fire_incnum = str(fiscaldata_dict["wfdssunit"]) + "-" + str(fiscaldata_dict["inc_num"])
            curr_fire_acres = list(curr_fire_df["acres"])[0]
            curr_fire_type = list(curr_fire_df["type"])[0]
            curr_fire_type_nospaces = curr_fire_type.replace(" ", "")
            curr_fire_lat_dd = list(curr_fire_df["latitude"])[0]
            curr_fire_lat_ddm_dir = list(curr_fire_df["lat_ddm_dir"])[0]
            curr_fire_long_dd = list(curr_fire_df["longitude"])[0]
            curr_fire_long_ddm_dir = list(curr_fire_df["long_ddm_dir"])[0]
            curr_fire_lat_long_dd = list(curr_fire_df["lat_long_dd"])[0]
            curr_fire_lat_long_dd_dir = list(curr_fire_df["lat_long_dd_dir"])[0]
            curr_fire_lat_long_ddm = list(curr_fire_df["lat_long_ddm"])[0]
            curr_fire_lat_long_ddm_dir = list(curr_fire_df["lat_long_ddm_dir"])[0]
            curr_fire_lat_ddm_dir_format = list(curr_fire_df["lat_ddm_dir_format"])[0]
            curr_fire_long_ddm_dir_format = list(curr_fire_df["long_ddm_dir_format"])[0]
            curr_fire_dispatch = list(curr_fire_df["Dispatch"])[0]
            curr_fire_alert = list(curr_fire_df["Alert"])[0]


            #Create spatial dataframe of fire point, but drop problematic fields first
            curr_fire_sdf_nad83 = arcgis.GeoAccessor.from_xy(curr_fire_df, 'longitude', 'latitude', sr=4269)
            curr_fire_sdf_utm12 = curr_fire_sdf_nad83.copy()
            curr_fire_sdf_utm12.spatial.project(out_crs)

            #Determine which State, BLM District, and BLM Field Office the WildCAD point intersects
            fo_select_sdf = fo_bndry_sdf.spatial.select(curr_fire_sdf_utm12)
            if(len(fo_select_sdf) == 1):
                curr_fire_state = list(fo_select_sdf["ADMIN_ST"])[0]
                curr_fire_do = list(fo_select_sdf["PARENT_NAME"])[0]
                curr_fire_fo = list(fo_select_sdf["ADMU_NAME"])[0]
            else:
                curr_fire_state = "NA"
                curr_fire_do = "NA"
                curr_fire_fo = "NA"


            #If the fire's lat/long belongs to IDEIC, NVECC, or AZFDC, but does not fall inside the Utah state boundary, enter fire info into csv log file and skip fire
            if( (curr_fire_dispatch in ["IDEIC", "NVECC", "AZFDC"]) & (curr_fire_state != "Utah") ):

                #Set field office, district, output path, and mxd to NA
                output_dir_path = "NA"
                curr_fire_layout = "NA"

                #Create list of fire information
                fireinfo_list = [curr_fire_datetime_format, curr_fire_name, curr_fire_incnum, curr_fire_type, curr_fire_acres,
                					curr_fire_dispatch, curr_fire_state, curr_fire_do, curr_fire_fo, curr_fire_alert,
                					curr_fire_lat_dd, curr_fire_long_dd,
                					curr_fire_lat_ddm_dir, curr_fire_long_ddm_dir,
                					output_dir_path, curr_fire_layout]

                #Update wildfire log csv with fire information, then overwrite the old version
                wildcad_log_df.loc[len(wildcad_log_df)] = fireinfo_list
                wildcad_log_df.to_csv(wildcad_log_path, index=False)

                #Skip to next incident
                continue


            #Determine which ArcGIS Pro layout to use
            curr_fire_layout = "WildCAD_Alert_Template_" + curr_fire_dispatch

            #Create output directory
            discov_time_parse = datetime.datetime.strptime(curr_fire_datetime_format, "%Y/%m/%d %H:%M")
            discov_time_format = datetime.datetime.strftime(discov_time_parse, "%Y%m%d_%H%M")
            curr_fire_name_alphanum = ''.join(filter(str.isalpha, curr_fire_name))
            output_dir_str = discov_time_format + "_" + curr_fire_dispatch + "_" + curr_fire_name_alphanum
            if(curr_fire_alert == "SmokeCheck"):
                output_dir_path = wildcad_map_dir + "/" + output_dir_str + "_SmokeCheck"
            if(curr_fire_alert == "SmallFire"):
                output_dir_path = wildcad_map_dir + "/" + output_dir_str + "_SmallFire"
            if(curr_fire_alert == "LargeFire"):
                output_dir_path = wildcad_map_dir + "/" + output_dir_str + "_LargeFire"
            os.mkdir(output_dir_path)

            #Create output GDB
            outgdb_name = discov_time_format + "_" + curr_fire_name_alphanum
            outgdb_path = output_dir_path + "/" + outgdb_name + ".gdb"
            arcpy.CreateFileGDB_management(output_dir_path, outgdb_name)
            firepoint_fc_filename = curr_fire_name_alphanum + "_point"
            if(firepoint_fc_filename[0].isnumeric()):
                firepoint_fc_filename = "i_" + firepoint_fc_filename
            firepoint_fc_path = outgdb_path + "/" + firepoint_fc_filename

            #Sanitize spatial dataframe columns manually
            column_list = list(curr_fire_sdf_utm12.columns)
            column_sanitize_list = []
            for j in range(0, len(column_list)):
                curr_col = column_list[j]
                curr_col_sanitize = ''.join(ch for ch in curr_col if ch.isalnum())
                column_sanitize_list.append(curr_col_sanitize)
            curr_fire_sdf_utm12.columns = column_sanitize_list

            #Export WildCAD point to feature class
            curr_fire_sdf_utm12.spatial.to_featureclass(firepoint_fc_path, sanitize_columns=False)


            ########################################################################
            ### CREATE MAP AND KMZ FILE
            ########################################################################

            #Create aprx object
            print("....Creating APRX")
            aprx = arcpy.mp.ArcGISProject(template_aprx)

            #Save a copy
            aprx_new_path = output_dir_path + "/" + curr_fire_name_alphanum + "_" + curr_fire_type_nospaces + ".aprx"
            aprx.saveACopy(aprx_new_path)

            #Create new aprx object
            aprx_new = arcpy.mp.ArcGISProject(aprx_new_path)

            #Create layout object
            alert_layout = aprx_new.listLayouts(curr_fire_layout)[0]

            #Create map object
            layers_map = aprx_new.listMaps("Layers")[0]

            #Create layer object
            firepoint_layer = layers_map.listLayers("WildCAD Fire Location")[0]

            #Get the original datasource for layer object
            firepoint_layer_cp = firepoint_layer.connectionProperties
            firepoint_layer_cp_new = firepoint_layer.connectionProperties

            #Re-source the fire point feature class
            firepoint_layer.visible = True
            firepoint_layer_cp_new['connection_info']['database'] = outgdb_path
            firepoint_layer_cp_new['dataset'] = firepoint_fc_filename
            firepoint_layer.updateConnectionProperties(firepoint_layer_cp, firepoint_layer_cp_new)

            #Create replacement string for map title
            if(curr_fire_type == "Wildfire"):
                title_insert = curr_fire_name + " Fire" + " (" + str(curr_fire_acres) + " Acres)"
            if(curr_fire_type == "Smoke Check"):
                title_insert = curr_fire_name + " Smoke Check"

            #Create replacement string for discovery date subtitle
            discov_date_insert = "Discovered: " +  curr_fire_datetime_format

            #Create replacement string for lat/long subtitle
            latlong_insert = "Lat = " +  curr_fire_lat_ddm_dir_format + "    " + "Long = " + curr_fire_long_ddm_dir_format

            #Update Map text elements using replacement strings
            for j in range(0, len(alert_layout.listElements("TEXT_ELEMENT"))):
                curr_text = alert_layout.listElements("TEXT_ELEMENT")[j].text

                if( "Discovered" in curr_text ):
                    alert_layout.listElements("TEXT_ELEMENT")[j].text = discov_date_insert

                if( "Lat = " in curr_text ):
                    alert_layout.listElements("TEXT_ELEMENT")[j].text = latlong_insert

                if( "Fire Name" in curr_text ):
                    alert_layout.listElements("TEXT_ELEMENT")[j].text = title_insert


            #ZOOM TO "WildCAD Fire Location" LAYER.
            #Create MapFrame object for the "Layers Map Frame"
            for j in range(0, len(alert_layout.listElements("MAPFRAME_ELEMENT"))):
                curr_mapframe_name = alert_layout.listElements("MAPFRAME_ELEMENT")[j].name
                if( curr_mapframe_name == "Layers Map Frame"):
                    alert_layers_mapframe = alert_layout.listElements("MAPFRAME_ELEMENT")[2]

            #Create selection of WildCAD Fire Location and zoom to it
            firepoint_layer = layers_map.listLayers("WildCAD Fire Location")[0]
            arcpy.SelectLayerByAttribute_management(firepoint_layer)
            alert_layers_mapframe.zoomToAllLayers(selection_only=True)
            arcpy.SelectLayerByAttribute_management(firepoint_layer, "CLEAR_SELECTION")

            #SET SCALE to 1:24K
            zoom_scale = 24000
            alert_layers_mapframe.camera.scale = zoom_scale

            #Save the map
            print("....Saving APRX")
            aprx_new.save()
            #aprx_new.saveACopy(aprx_new_path) #Had to use this for ArcGIS Pro v2.9.x, as aprx.save() would throw errors

            #Export Layout to PDF
            print("....Exporting Map to PDF")
            fire_pdf_path = output_dir_path + "/" + curr_fire_name_alphanum + "_" + curr_fire_type_nospaces + ".pdf"
            alert_layout.exportToPDF(fire_pdf_path)

            print("....Creating KMZ of the lat/long location")
            #Create KMZ of the lat/long location
            fire_kmz_path = output_dir_path + "/" + curr_fire_name_alphanum + "_" + curr_fire_type_nospaces + ".kmz"
            arcpy.LayerToKML_conversion(firepoint_layer, fire_kmz_path)


            ####################################################################
            # SEND EMAIL
            ####################################################################

            #Create list of emails recipients
            if(curr_fire_alert in ["SmokeCheck", "SmallFire"]):
                curr_fire_alert_str = "SmokeCheck_SmallFire"
            if(curr_fire_alert in ["LargeFire"]):
                curr_fire_alert_str = "LargeFire"
            curr_fire_alert_list_str = curr_fire_dispatch + "_" + curr_fire_alert_str
            curr_recipients_list = list(wildcad_emails_df[curr_fire_alert_list_str])

            #Remove nan values from recipient list
            curr_recipients_list = [x for x in curr_recipients_list if str(x) != 'nan']

            #Was hitting 100 address recipient limit with NUIFC SmallFire/SmokeCheck
            #To fix, will now split it up each time and send out in chunks.
            chunk_size = 100
            recipients_list_chunks = [curr_recipients_list[x * chunk_size:(x + 1) * chunk_size] for x in range((len(curr_recipients_list) + chunk_size - 1) // chunk_size )]

            #Prepare email for sending
            print("....Sending email")

            #build email subject string
            if(curr_fire_type == "Wildfire"):
            	email_subject = "WILDFIRE ALERT: " + curr_fire_name + " (" + str(curr_fire_acres) + " Acres) - Discovered at " + curr_fire_datetime_format
            if(curr_fire_type == "Smoke Check"):
            	email_subject = "SMOKE CHECK ALERT: " + curr_fire_name + " - Discovered at " + curr_fire_datetime_format

            # Write the content of your email
            email_message = "DD:" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + curr_fire_lat_long_dd + '<br><br>' + \
                            "DD w/ dir:" + "&nbsp;&nbsp;&nbsp;&nbsp;" + curr_fire_lat_long_dd_dir + '<br><br>' + \
                            "DDM:" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + curr_fire_lat_long_ddm + '<br><br>' + \
                            "DDM w/ dir:" + "&nbsp;&nbsp;" + curr_fire_lat_long_ddm_dir + '<br><br>' + \
                            "Google Maps: " + "https://www.google.com/maps/search/?api=1&query=" + str(curr_fire_lat_dd) + "," + str(curr_fire_long_dd)

            #Loop through each chunk of 100 email addresses, and send them out
            for j in range(0, len(recipients_list_chunks)):

                receiverEmail = recipients_list_chunks[j]   # Email receiver(s)

                #Now build email
                msg = email.mime.multipart.MIMEMultipart()
                msg['Subject'] = email_subject
                msg['From'] = email_sender
                msg['To'] = ", ".join(receiverEmail)

                msg.attach(email.mime.text.MIMEText(email_message, 'html'))

                files_list = [fire_pdf_path, fire_kmz_path]

                for a_file in files_list:
                    attachment = open(a_file, 'rb')
                    file_name = os.path.basename(a_file)
                    part = email.mime.base.MIMEBase('application','octet-stream')
                    part.set_payload(attachment.read())
                    part.add_header('Content-Disposition',
                                    'attachment',
                                    filename=file_name)
                    email.encoders.encode_base64(part)
                    msg.attach(part)

                #Login to email
                session = smtplib.SMTP('smtp.gmail.com', 587)  # SMPT Server Name and Port
                session.starttls()
                session.login(email_sender, email_password)

                #Sends email
                session.sendmail(email_sender, receiverEmail, msg.as_string()) #
                session.quit()

            ######################################################################
            # UPDATE LOG FILE
            ######################################################################

            #Create list of fire information
            fireinfo_list = [curr_fire_datetime_format, curr_fire_name, curr_fire_incnum, curr_fire_type, curr_fire_acres,
            					curr_fire_dispatch, curr_fire_state, curr_fire_do, curr_fire_fo, curr_fire_alert,
            					curr_fire_lat_dd, curr_fire_long_dd,
            					curr_fire_lat_ddm_dir, curr_fire_long_ddm_dir,
            					output_dir_path, curr_fire_layout]

            #Update wildfire log csv with fire information
            wildcad_log_df.loc[len(wildcad_log_df)] = fireinfo_list

            #Save updated log file
            wildcad_log_df.to_csv(wildcad_log_path, index=False)



#If enounter error, send it to me in an email
except Exception as e:

    #Don't send an error email if the error is "HTTP Error 503: Service Unavailable".
    #This seems to just be a stutter of some sort during the web scrape, and happens regularly
    error_msg = str(e)
    if("HTTP Error 503: Service Unavailable" not in error_msg):

        #Build email
        msg = email.mime.multipart.MIMEMultipart()
        msg['Subject'] = "WildCAD ALERT ERROR"
        msg['From'] = email_sender
        msg['To'] = receiverEmail_errors

        msg.attach(email.mime.text.MIMEText(error_msg, 'html'))

        #Login to email
        session = smtplib.SMTP('smtp.gmail.com', 587)  # SMPT Server Name and Port
        session.starttls()
        session.login(email_sender, email_password)

        #Sends email
        session.sendmail(email_sender, receiverEmail, msg.as_string())
        session.quit()





