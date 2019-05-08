import pickle
import os.path
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import *

# OAUTH CREDENTIALS
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


# import Mission.csv-files
tacview_log = []

with open(import_file, "r", encoding="utf8") as file:
    reader = csv.DictReader(file)
    for line in reader:
        tacview_log.append(line)

unit_spawned = list()
unit_tookoff = list()
unit_landed = list()
unit_despawned = list()
unit_fired = list()
unit_hit = list()
unit_destroyed = list()

for line in tacview_log:
    hours = int(float(line["\ufeffMission Time"]) / 60 / 60)
    minutes = int(float(line["\ufeffMission Time"]) / 60 % 60)
    seconds = int(float(line["\ufeffMission Time"]) % 60)
    line["\ufeffMission Time"] = "%s:%s:%s" % (hours, minutes, seconds)
    if line["Primary Object Coalition"] != "":
        line["Primary Object Coalition"] = coalitions[line["Primary Object Coalition"]]
    if line["Secondary Object Coalition"] != "":
        line["Secondary Object Coalition"] = coalitions[line["Secondary Object Coalition"]]
    if line["Relevant Object Coalition"] != "":
        line["Relevant Object Coalition"] = coalitions[line["Relevant Object Coalition"]]
    if line["Event"] == "HasEnteredTheArea":
        unit_spawned.append(line)
    elif line["Event"] == "HasTakenOff":
        unit_tookoff.append(line)
    elif line["Event"] == "HasLanded":
        unit_landed.append(line)
    elif line["Event"] == "HasLeftTheArea":
        unit_despawned.append(line)
    elif line["Event"] == "HasFired":
        unit_fired.append(line)
    elif line["Event"] == "HasBeenHitBy":
        unit_hit.append(line)
    elif line["Event"] == "HasBeenDestroyed":
        unit_destroyed.append(line)


# adjust for RIOs
# unit_spawned
for x in range(len(unit_spawned)):
    if unit_spawned[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_spawned[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_spawned[x]["Primary Object Pilot"] = item["pilot"]
            unit_spawned[x]["Primary Object Rio"] = item["rio"]

# unit_tookoff
for x in range(len(unit_tookoff)):
    if unit_tookoff[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_tookoff[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_tookoff[x]["Primary Object Pilot"] = item["pilot"]
            unit_tookoff[x]["Primary Object Rio"] = item["rio"]

# unit_landed
for x in range(len(unit_landed)):
    if unit_landed[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_landed[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_landed[x]["Primary Object Pilot"] = item["pilot"]
            unit_landed[x]["Primary Object Rio"] = item["rio"]

# unit_despawned
for x in range(len(unit_despawned)):
    if unit_despawned[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_despawned[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_despawned[x]["Primary Object Pilot"] = item["pilot"]
            unit_despawned[x]["Primary Object Rio"] = item["rio"]

# unit_hit
for x in range(len(unit_hit)):
    if unit_hit[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_hit[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_hit[x]["Primary Object Pilot"] = item["pilot"]
            unit_hit[x]["Primary Object Rio"] = item["rio"]

# unit_destroyed
for x in range(len(unit_destroyed)):
    if unit_destroyed[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_destroyed[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_destroyed[x]["Primary Object Pilot"] = item["pilot"]
            unit_destroyed[x]["Primary Object Rio"] = item["rio"]

# unit_fired
for x in range(len(unit_fired)):
    if unit_fired[x]["Primary Object Name"] == "F-14B Tomcat":
        generator = (crew for crew in f14_crew if unit_fired[x]["Primary Object Pilot"] in crew.values())
        for item in generator:
            unit_fired[x]["Primary Object Pilot"] = item["pilot"]
            unit_fired[x]["Primary Object Rio"] = item["rio"]

# weapons fired
total_weapons_fired = {
    "USA": {},
    "Iran": {}
}
for shot in unit_fired:
    weapon_name = shot["Secondary Object Name"]
    weapon_count = shot["Occurrences"]
    weapon_coalition = shot["Primary Object Coalition"]
    if weapon_name in total_weapons_fired[weapon_coalition]:
        total_weapons_fired[weapon_coalition][weapon_name] += int(weapon_count)
    else:
        total_weapons_fired[weapon_coalition][weapon_name] = int(weapon_count)


# unit damaged or destroyed
unit_dnd = {
    "USA": {
        "destroyed": {},
        "damaged": {}
    },
    "Iran": {
        "destroyed": {},
        "damaged": {}
    }
}

unit_scored_hits = list()
unit_scored_kills = list()

for unit in unit_destroyed:
    unit_id = unit["Primary Object ID"]
    unit_coalition = unit["Primary Object Coalition"]
    if unit_coalition == "":
        continue
    unit_type = unit["Primary Object Name"]
    unit_pilot = unit["Primary Object Pilot"]
    unit_rio = "-"
    generator = (crew for crew in f14_crew if unit_pilot in crew.values())
    for item in generator:
        unit_rio = item["rio"]
    unit_killer = unit["Secondary Object Pilot"]
    unit_killer_rio = "-"
    generator = (crew for crew in f14_crew if unit_killer in crew.values())
    for item in generator:
        unit_killer_rio = item["rio"]

    if unit_type == "F-14B Tomcat":
        unit_dnd[unit_coalition]["destroyed"][unit_id] = {
            "Type": unit_type,
            "Pilot": unit_pilot,
            "Rio": unit_rio
        }
    elif unit_pilot != "":
        unit_dnd[unit_coalition]["destroyed"][unit_id] = {
            "Type": unit_type,
            "Pilot": unit_pilot
        }
    else:
        unit_dnd[unit_coalition]["destroyed"][unit_id] = {
            "Type": unit_type
        }

    if unit_killer != "":
        if unit_killer_rio != "-":
            unit_scored_kills.append([unit_killer, unit_killer_rio, unit_type])
        else:
            unit_scored_kills.append([unit_killer, "", unit_type])

for unit in unit_hit:
    unit_id = unit["Primary Object ID"]
    unit_coalition = unit["Primary Object Coalition"]
    unit_type = unit["Primary Object Name"]
    unit_pilot = unit["Primary Object Pilot"]
    unit_rio = "-"
    generator = (crew for crew in f14_crew if unit_pilot in crew.values())
    for item in generator:
        unit_rio = item["rio"]
    unit_killer = unit["Relevant Object Pilot"]
    unit_killer_rio = "-"
    generator = (crew for crew in f14_crew if unit_killer in crew.values())
    for item in generator:
        unit_killer_rio = item["rio"]

    if unit_killer != "":
        if unit_killer_rio != "-":
            unit_scored_hits.append([unit_killer, unit_killer_rio, unit_type])
        else:
            unit_scored_hits.append([unit_killer, "", unit_type])
    if unit_id not in unit_dnd[unit_coalition]["destroyed"]:
        if unit_type == "F-14B Tomcat":
            unit_dnd[unit_coalition]["damaged"][unit_id] = {
                "Type": unit_type,
                "Pilot": unit_pilot,
                "Rio": unit_rio
            }
        elif unit_pilot != "":
            unit_dnd[unit_coalition]["damaged"][unit_id] = {
                "Type": unit_type,
                "Pilot": unit_pilot,
            }
        else:
            unit_dnd[unit_coalition]["damaged"][unit_id] = {
                "Type": unit_type,
            }

# units destroyed
usa_sum_unit_lost = dict()
for unitid, unit in unit_dnd["USA"]["destroyed"].items():
    if unit["Type"] in usa_sum_unit_lost:
        usa_sum_unit_lost[unit["Type"]] += 1
    else:
        usa_sum_unit_lost[unit["Type"]] = 1

iran_sum_unit_lost = dict()
for unitid, unit in unit_dnd["Iran"]["destroyed"].items():
    if unit["Type"] in iran_sum_unit_lost:
        iran_sum_unit_lost[unit["Type"]] += 1
    else:
        iran_sum_unit_lost[unit["Type"]] = 1

# units damaged
usa_sum_unit_dmg = dict()
for unitid, unit in unit_dnd["USA"]["damaged"].items():
    if unit["Type"] in usa_sum_unit_dmg:
        usa_sum_unit_dmg[unit["Type"]] += 1
    else:
        usa_sum_unit_dmg[unit["Type"]] = 1

iran_sum_unit_dmg = dict()
for unitid, unit in unit_dnd["Iran"]["damaged"].items():
    if unit["Type"] in iran_sum_unit_dmg:
        iran_sum_unit_dmg[unit["Type"]] += 1
    else:
        iran_sum_unit_dmg[unit["Type"]] = 1


####################################################################################################################################################################################
# write google docs data
for statslist in [unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed]:
    if statslist == unit_spawned:
        TABLENAME = 'unit_spawned'
    elif statslist == unit_tookoff:
        TABLENAME = 'unit_tookoff'
    elif statslist == unit_landed:
        TABLENAME = 'unit_landed'
    elif statslist == unit_despawned:
        TABLENAME = 'unit_despawned'
    elif statslist == unit_fired:
        TABLENAME = 'unit_fired'
    elif statslist == unit_hit:
        TABLENAME = 'unit_hit'
    elif statslist == unit_destroyed:
        TABLENAME = 'unit_destroyed'

    values = list()
    headerrow = ['\ufeffMission Time',
                 'Primary Object ID',
                 'Primary Object Name',
                 'Primary Object Coalition',
                 'Primary Object Pilot',
                 'Event',
                 'Occurrences',
                 'Secondary Object ID',
                 'Secondary Object Name',
                 'Secondary Object Coalition',
                 'Secondary Object Pilot',
                 'Relevant Object ID',
                 'Relevant Object Name',
                 'Relevant Object Coalition',
                 'Relevant Object Pilot',
                 'Primary Object Rio']

    values.append(headerrow)

    for entry in statslist:
        row = list()
        for key, value in entry.items():
            row.append(value)
        values.append(row)

    body = {'values': values}

    # Call the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result1 = service.spreadsheets().values().clear(
        spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME]).execute()

    result2 = service.spreadsheets().values().update(
        spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME],
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result2.get('updatedCells')))


# write weapon uses
TABLENAME = "weapons_fired"

values = list()

for key, value in total_weapons_fired["USA"].items():
    wpn = key.replace('weapons.missiles.', "")
    wpn = wpn.replace('weapons.shells.', "")
    wpn = wpn.replace('weapons.bombs.', "")
    values.append([wpn, value, 0])


for key, value in total_weapons_fired["Iran"].items():
    weapon_found = False
    for line in values:
        if line[0] == key:
            line[2] = value
            weapon_found = True
    if not weapon_found:
        wpn = key.replace('weapons.missiles.', "")
        wpn = wpn.replace('weapons.shells.', "")
        wpn = wpn.replace('weapons.bombs.', "")
        values.append([wpn, 0, value])

values.sort()

values.insert(0, ["Weapon", "USA", "Iran"])

body = {'values': values}


service = build('sheets', 'v4', credentials=creds)
result1 = service.spreadsheets().values().clear(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME]).execute()

result2 = service.spreadsheets().values().update(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME],
    valueInputOption='USER_ENTERED', body=body).execute()
print('{0} cells updated.'.format(result2.get('updatedCells')))


# units destroyed and damaged
TABLENAME = "unit_kills"
TABLENAME2 = "unit_hits"

values = list()

for key, value in usa_sum_unit_lost.items():
    unt = key.replace('weapons.missiles.', "")
    unt = unt.replace('weapons.shells.', "")
    unt = unt.replace('weapons.bombs.', "")
    values.append([unt, value, 0])

for key, value in iran_sum_unit_lost.items():
    unit_found = False
    for line in values:
        if line[0] == key:
            line[2] = value
            unit_found = True
    if not unit_found:
        unt = key.replace('weapons.missiles.', "")
        unt = unt.replace('weapons.shells.', "")
        unt = unt.replace('weapons.bombs.', "")
        values.append([unt, 0, value])

values.sort()

values.insert(0, ["Unit lost", "USA", "Iran"])

values2 = list()

for key, value in usa_sum_unit_dmg.items():
    unt = key.replace('weapons.missiles.', "")
    unt = unt.replace('weapons.shells.', "")
    unt = unt.replace('weapons.bombs.', "")
    values2.append([unt, value, 0])

for key, value in iran_sum_unit_dmg.items():
    unit_found = False
    for line in values2:
        if line[0] == key:
            line[2] = value
            unit_found = True
    if not unit_found:
        unt = key.replace('weapons.missiles.', "")
        unt = unt.replace('weapons.shells.', "")
        unt = unt.replace('weapons.bombs.', "")
        values2.append([unt, 0, value])

values2.sort()

values2.insert(0, ["Unit damaged", "USA", "Iran"])

body = {'values': values}
body2 = {'values': values2}

service = build('sheets', 'v4', credentials=creds)
result1 = service.spreadsheets().values().clear(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME]).execute()

result2 = service.spreadsheets().values().update(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME],
    valueInputOption='USER_ENTERED', body=body).execute()
print('{0} cells updated.'.format(result2.get('updatedCells')))

result3 = service.spreadsheets().values().clear(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME2]).execute()

result4 = service.spreadsheets().values().update(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME2],
    valueInputOption='USER_ENTERED', body=body2).execute()
print('{0} cells updated.'.format(result4.get('updatedCells')))


# units hits and kills
TABLENAME = "hits"
TABLENAME2 = "kills"

values = list()

for item in unit_scored_hits:
    values.append(item)

values.sort()

values.insert(0, ["Pilot", "Rio", "Target hit"])

values2 = list()

for item in unit_scored_kills:
    values2.append(item)

values2.sort()

values2.insert(0, ["Pilot", "Rio", "Target kill"])

body = {'values': values}
body2 = {'values': values2}

service = build('sheets', 'v4', credentials=creds)
result1 = service.spreadsheets().values().clear(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME]).execute()

result2 = service.spreadsheets().values().update(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME],
    valueInputOption='USER_ENTERED', body=body).execute()
print('{0} cells updated.'.format(result2.get('updatedCells')))

result3 = service.spreadsheets().values().clear(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME2]).execute()

result4 = service.spreadsheets().values().update(
    spreadsheetId=MISSION_SPREADSHEET_ID, range=SPREADSHEETRANGE[TABLENAME2],
    valueInputOption='USER_ENTERED', body=body2).execute()
print('{0} cells updated.'.format(result4.get('updatedCells')))




