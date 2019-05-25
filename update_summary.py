import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import *


# OAUTH CREDENTIALS
def oauth():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def main():
    # Get Creds
    creds = oauth()
    spreadsheet_id = total_summary_sheet
    range_name = "Pilot Summary"

    # Call the Sheets API
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API, read data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()

    # create to_write data
    to_write_values = list()
    pilot_list = dict()
    cpn_pilot_list = dict()
    mission_list_ii = list()
    mission_list = list()

    for line in result["values"]:
        if line[0] != "":
            # get mission column in header row
            if line[0] in ["Pilot", "Pilot\n(green sortie = AIC)\ncheck Operation Spreadsheet for a more detailed overview over this mission"]:
                for column in range(len(line)):
                    if line[column].upper().startswith(campaign_abbreviation):
                        mission_list_ii.append(column)
                    elif line[column] != "" and column not in [0, 1, 13]:
                        mission_list.append(column)
                continue

            # create pilot entry
            pilot = line[0]
            pilot_list[pilot] = {
                "Attendance": 0,
                "Sorties": 0,
                "Landings": 0,
                "Deaths": 0,
                "Success": 0.0,
                "A2A - Shots": 0,
                "A2A - Hits": 0,
                "A2A - Kills": 0,
                "A2G - Shots": 0,
                "A2G - Hits": 0,
                "A2G - Kills": 0,
            }
            cpn_pilot_list[pilot] = {
                "Attendance": 0,
                "Sorties": 0,
                "Landings": 0,
                "Deaths": 0,
                "Success": 0.0,
                "A2A - Shots": 0,
                "A2A - Hits": 0,
                "A2A - Kills": 0,
                "A2G - Shots": 0,
                "A2G - Hits": 0,
                "A2G - Kills": 0,
                    }

            cpn_success_rate = 0.0
            cpn_success_mis = 0

            # add values to cpn_total list
            for mis_col in mission_list_ii:
                if line[mis_col] not in ["", "0", 0]:
                    cpn_pilot_list[pilot]["Attendance"] += 1
                    if line[mis_col] != "AIC":
                        cpn_pilot_list[pilot]["Sorties"] += int(line[mis_col])
                cpn_pilot_list[pilot]["Landings"] += int(line[mis_col+1])
                cpn_pilot_list[pilot]["Deaths"] += int(line[mis_col+2])

                if line[mis_col+4] != "-":
                    cpn_success_mis += 1
                    cpn_success_rate += float(line[mis_col+4].replace("%", "")) / 100

                cpn_pilot_list[pilot]["A2A - Shots"] += int(line[mis_col+5])
                cpn_pilot_list[pilot]["A2A - Hits"] += int(line[mis_col+6])
                cpn_pilot_list[pilot]["A2A - Kills"] += int(line[mis_col+7])
                cpn_pilot_list[pilot]["A2G - Shots"] += int(line[mis_col+8])
                cpn_pilot_list[pilot]["A2G - Hits"] += int(line[mis_col+9])
                cpn_pilot_list[pilot]["A2G - Kills"] += int(line[mis_col+10])
            if cpn_pilot_list[pilot]["Sorties"] > 0:
                cpn_pilot_list[pilot]["Survival"] = round(cpn_pilot_list[pilot]["Landings"] / cpn_pilot_list[pilot]["Sorties"], 2)
            else:
                cpn_pilot_list[pilot]["Survival"] = 0
            if cpn_success_mis == 0:
                cpn_pilot_list[pilot]["Success"] = "-"
            else:
                cpn_pilot_list[pilot]["Success"] = cpn_success_rate / cpn_success_mis

            success_rate = 0.0
            success_mis = 0

            # add values to total list
            for mis_col in mission_list:
                if line[mis_col] not in ["", "0", 0]:
                    pilot_list[pilot]["Attendance"] += 1
                    if line[mis_col] != "AIC":
                        pilot_list[pilot]["Sorties"] += int(line[mis_col])
                pilot_list[pilot]["Landings"] += int(line[mis_col+1])
                pilot_list[pilot]["Deaths"] += int(line[mis_col+2])
                if line[mis_col+4] != "-":
                    success_mis += 1
                    success_rate += float(line[mis_col+4].replace("%", "")) / 100
                pilot_list[pilot]["A2A - Shots"] += int(line[mis_col+5])
                pilot_list[pilot]["A2A - Hits"] += int(line[mis_col+6])
                pilot_list[pilot]["A2A - Kills"] += int(line[mis_col+7])
                pilot_list[pilot]["A2G - Shots"] += int(line[mis_col+8])
                pilot_list[pilot]["A2G - Hits"] += int(line[mis_col+9])
                pilot_list[pilot]["A2G - Kills"] += int(line[mis_col+10])

            # add cpn_total list to total list
            pilot_list[pilot]["Attendance"] += cpn_pilot_list[pilot]["Attendance"]
            pilot_list[pilot]["Sorties"] += cpn_pilot_list[pilot]["Sorties"]
            pilot_list[pilot]["Landings"] += cpn_pilot_list[pilot]["Landings"]
            pilot_list[pilot]["Deaths"] += cpn_pilot_list[pilot]["Deaths"]
            pilot_list[pilot]["A2A - Shots"] += cpn_pilot_list[pilot]["A2A - Shots"]
            pilot_list[pilot]["A2A - Hits"] += cpn_pilot_list[pilot]["A2A - Hits"]
            pilot_list[pilot]["A2A - Kills"] += cpn_pilot_list[pilot]["A2A - Kills"]
            pilot_list[pilot]["A2G - Shots"] += cpn_pilot_list[pilot]["A2G - Shots"]
            pilot_list[pilot]["A2G - Hits"] += cpn_pilot_list[pilot]["A2G - Hits"]
            pilot_list[pilot]["A2G - Kills"] += cpn_pilot_list[pilot]["A2G - Kills"]

            if pilot_list[pilot]["Sorties"] > 0:
                pilot_list[pilot]["Survival"] = round(pilot_list[pilot]["Landings"] / pilot_list[pilot]["Sorties"], 2)
            else:
                pilot_list[pilot]["Survival"] = 0

            if (cpn_success_mis + success_mis) == 0:
                pilot_list[pilot]["Success"] = "-"
            else:
                pilot_list[pilot]["Success"] = (cpn_success_rate + success_rate) / (cpn_success_mis + success_mis)

    # replace 0 with -
    for loop_pilot, value in cpn_pilot_list.items():
        if value["Attendance"] == 0:
            cpn_pilot_list[loop_pilot]["Attendance"] = "-"
        if value["Sorties"] == 0:
            cpn_pilot_list[loop_pilot]["Sorties"] = "-"
            cpn_pilot_list[loop_pilot]["Landings"] = "-"
            cpn_pilot_list[loop_pilot]["Deaths"] = "-"
            cpn_pilot_list[loop_pilot]["Survival"] = "-"
            cpn_pilot_list[loop_pilot]["A2A - Shots"] = "-"
            cpn_pilot_list[loop_pilot]["A2A - Hits"] = "-"
            cpn_pilot_list[loop_pilot]["A2A - Kills"] = "-"
            cpn_pilot_list[loop_pilot]["A2G - Shots"] = "-"
            cpn_pilot_list[loop_pilot]["A2G - Hits"] = "-"
            cpn_pilot_list[loop_pilot]["A2G - Kills"] = "-"

    for loop_pilot, value in pilot_list.items():
        if value["Attendance"] == 0:
            pilot_list[loop_pilot]["Attendance"] = "-"
        if value["Sorties"] == 0:
            pilot_list[loop_pilot]["Sorties"] = "-"
            pilot_list[loop_pilot]["Landings"] = "-"
            pilot_list[loop_pilot]["Deaths"] = "-"
            pilot_list[loop_pilot]["Survival"] = "-"
            pilot_list[loop_pilot]["A2A - Shots"] = "-"
            pilot_list[loop_pilot]["A2A - Hits"] = "-"
            pilot_list[loop_pilot]["A2A - Kills"] = "-"
            pilot_list[loop_pilot]["A2G - Shots"] = "-"
            pilot_list[loop_pilot]["A2G - Hits"] = "-"
            pilot_list[loop_pilot]["A2G - Kills"] = "-"

    # create final value-list to write to spreadsheet
    for loop_pilot, value in pilot_list.items():
        to_write_values.append([
            loop_pilot,
            value["Attendance"],
            value["Sorties"],
            value["Landings"],
            value["Deaths"],
            value["Survival"],
            value["Success"],
            value["A2A - Shots"],
            value["A2A - Hits"],
            value["A2A - Kills"],
            value["A2G - Shots"],
            value["A2G - Hits"],
            value["A2G - Kills"],
            cpn_pilot_list[loop_pilot]["Attendance"],
            cpn_pilot_list[loop_pilot]["Sorties"],
            cpn_pilot_list[loop_pilot]["Landings"],
            cpn_pilot_list[loop_pilot]["Deaths"],
            cpn_pilot_list[loop_pilot]["Survival"],
            cpn_pilot_list[loop_pilot]["Success"],
            cpn_pilot_list[loop_pilot]["A2A - Shots"],
            cpn_pilot_list[loop_pilot]["A2A - Hits"],
            cpn_pilot_list[loop_pilot]["A2A - Kills"],
            cpn_pilot_list[loop_pilot]["A2G - Shots"],
            cpn_pilot_list[loop_pilot]["A2G - Hits"],
            cpn_pilot_list[loop_pilot]["A2G - Kills"],
        ])

    pil_sum_range = "Pilot Summary!A4:Y"
    body = {'values': to_write_values}

    # Call the Sheets API, clear Range, write Data
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=pil_sum_range).execute()

    result2 = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=pil_sum_range,
        valueInputOption='RAW', body=body).execute()
    print('%s: %s cells updated.' % (pil_sum_range, result2.get('updatedCells')))

    print("finish")


# RUN MAIN
if __name__ == '__main__':
    main()
