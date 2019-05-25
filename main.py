import pickle
import os.path
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import *
from dcs_config import *

# CREATE EMPTY LISTS
unit_spawned = list()
unit_tookoff = list()
unit_landed = list()
unit_despawned = list()
unit_fired = list()
unit_hit = list()
unit_destroyed = list()
unit_scored_hits = list()
unit_scored_kills = list()


# GOOGLE OAUTH CREDENTIALS
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


# IMPORT MISSION.CSV FILE AND STORE RAW DATA INTO SEPERATED LISTS
def import_csv(csv_file):
    global csv_delimiter
    tacview_log = []

    # check for delimiter
    if csv_delimiter is None:
        csv_delimiter = ","

    # open file and read datra
    with open(csv_file, "r", encoding="utf8") as file:
        reader = csv.DictReader(file, delimiter=csv_delimiter)
        for line in reader:
            tacview_log.append(line)

    # modify data and distribute data to the matching list
    for line in tacview_log:
        # create propper mission time (0:00:00 equals mission start)
        hours = int(float(line["\ufeffMission Time"]) / 60 / 60)
        minutes = int(float(line["\ufeffMission Time"]) / 60 % 60)
        seconds = int(float(line["\ufeffMission Time"]) % 60)
        line["\ufeffMission Time"] = "%s:%s:%s" % (hours, minutes, seconds)

        # Replace "Enemies"/"Allies" with the Coalition set in config.py
        if line["Primary Object Coalition"] != "":
            line["Primary Object Coalition"] = coalitions[line["Primary Object Coalition"]]
        if line["Secondary Object Coalition"] != "":
            line["Secondary Object Coalition"] = coalitions[line["Secondary Object Coalition"]]
        if line["Relevant Object Coalition"] != "":
            line["Relevant Object Coalition"] = coalitions[line["Relevant Object Coalition"]]

        # distribute data to the matching list
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

    # Create Entry "Primary Object Rio" for F14s according to Crew-list in config.py
    for unit_list in [unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed]:
        for x in range(len(unit_list)):
            if unit_list[x]["Primary Object Name"] == "F-14B Tomcat":
                generator = (crew for crew in f14_crew[current_mission] if unit_list[x]["Primary Object Pilot"] in crew.values())
                for item in generator:
                    unit_list[x]["Primary Object Pilot"] = item["pilot"]
                    unit_list[x]["Primary Object Rio"] = item["rio"]

    return


# GET ID LIST
def get_id_list():
    id_list = {
        "unit_air": dict(),
        "unit_ground": dict(),
        "weapons": dict(),
        "misc": dict()
    }

    # UNIT_SPAWNED
    for line in unit_spawned:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 1,
                "despawns": 0,
                "sorties": 0,
                "landings": 0,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["spawns"] += 1

    # UNIT_TAKEOFFS
    for line in unit_tookoff:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 1,
                "landings": 0,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["sorties"] += 1

    # UNIT_LANDINGS
    for line in unit_landed:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 0,
                "landings": 1,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["landings"] += 1

    # UNIT_DESPAWNS
    for line in unit_despawned:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 1,
                "sorties": 0,
                "landings": 0,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["despawns"] += 1

    # UNIT_WEAPONS_FIRED
    for line in unit_fired:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 0,
                "landings": 0,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": [line["Secondary Object ID"]],
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["weapons_fired"].append(line["Secondary Object ID"])

        # if weapon_id not already in weaponlist
        if line["Secondary Object ID"] not in id_list["weapons"]:
            id_list["weapons"][line["Secondary Object ID"]] = {
                "weapon_type": line["Secondary Object Name"],
                "weapon_count": line["Occurrences"],
                "weapon_coalition": line["Secondary Object Coalition"],
                "hits": list(),
            }
        # if weapon_id already in weaponlist
        else:
            id_list["weapons"][line["Secondary Object ID"]]["weapon_count"] += line["Occurrences"]

    # UNIT_HITS_RECEIVED
    for line in unit_hit:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 0,
                "landings": 0,
                "deaths": 0,
                "hit_received": [line["Secondary Object ID"]],
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["hit_received"].append(line["Secondary Object ID"])

        # if weapon_id not already in weaponlist
        if line["Secondary Object ID"] not in id_list["weapons"]:
            id_list["weapons"][line["Secondary Object ID"]] = {
                "weapon_type": line["Secondary Object Name"],
                "weapon_count": 0,
                "weapon_coalition": line["Secondary Object Coalition"],
                "hits": [id_list[prim_unit_type][line["Primary Object ID"]]],
            }
        # if weapon_id already in weaponlist
        else:
            id_list["weapons"][line["Secondary Object ID"]]["hits"].append(line["Primary Object ID"])

    # UNIT_KILLED_BY
    for line in unit_destroyed:
        prim_unit_type = "misc"
        if line["Primary Object Name"] in aircrafts:
            prim_unit_type = "unit_air"
        elif line["Primary Object Name"] in groundunits:
            prim_unit_type = "unit_ground"

        # if id not already in list
        if line["Primary Object ID"] not in id_list[prim_unit_type]:
            id_list[prim_unit_type][line["Primary Object ID"]] = {
                "unit_type": line["Primary Object Name"],
                "unit_pilot": line["Primary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Primary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 0,
                "landings": 0,
                "deaths": 1,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": list(),
            }
        # if id already in list
        else:
            id_list[prim_unit_type][line["Primary Object ID"]]["deaths"] += 1

        secd_unit_type = "misc"
        if line["Secondary Object Name"] in aircrafts:
            secd_unit_type = "unit_air"
        elif line["Secondary Object Name"] in groundunits:
            secd_unit_type = "unit_ground"

        # write scored kill
        # if killer_id not already in list
        if line["Secondary Object ID"] not in id_list[secd_unit_type]:
            id_list[secd_unit_type][line["Secondary Object ID"]] = {
                "unit_type": line["Secondary Object Name"],
                "unit_pilot": line["Secondary Object Pilot"],
                "unit_rio": "",
                "unit_coalition": line["Secondary Object Coalition"],
                "spawns": 0,
                "despawns": 0,
                "sorties": 0,
                "landings": 0,
                "deaths": 0,
                "hit_received": list(),
                "weapons_fired": list(),
                "kills": [line["Primary Object ID"]],
            }
        # if killer_id already in list
        else:
            id_list[secd_unit_type][line["Secondary Object ID"]]["kills"].append(line["Primary Object ID"])

    # add RIO to every F14 according to crewlist in config.py
    for key, value in id_list["unit_air"].items():
        if value["unit_type"] == "F-14B Tomcat":
            generator = (crew for crew in f14_crew[current_mission] if value["unit_pilot"] in crew.values())
            for item in generator:
                id_list["unit_air"][key]["unit_pilot"] = item["pilot"]
                id_list["unit_air"][key]["unit_rio"] = item["rio"]

    return id_list


# CREATE WEAPON USED LIST
def get_weapons_used(id_list):
    weapons_used = dict()

    for key, value in id_list["weapons"].items():
        if value["weapon_type"] not in weapon_misc:
            weapon_type = value["weapon_type"].replace("weapons.", "")
            weapon_type = weapon_type.replace("missiles.", "")
            weapon_type = weapon_type.replace("bombs.", "")
            weapon_type = weapon_type.replace("shells.", "")

            if weapon_type not in weapons_used:
                weapons_used[weapon_type] = {
                    coalitions["Enemies"]: 0,
                    coalitions["Allies"]: 0,
                }
            if value["weapon_coalition"] != "":
                weapons_used[weapon_type][value["weapon_coalition"]] += int(value["weapon_count"])

    return weapons_used


# CREATE UNIT DAMAGED OR DESTROYED LIST
def get_inventory_changes(id_list):
    inventory_changes = {
        "unit_air": dict(),
        "unit_ground": dict(),
    }

    # Air_Units
    for key, value in id_list["unit_air"].items():
        if value["unit_type"] not in inventory_changes["unit_air"]:
            inventory_changes["unit_air"][value["unit_type"]] = {
                "damaged": {
                    coalitions["Enemies"]: 0,
                    coalitions["Allies"]: 0,
                },
                "destroyed": {
                    coalitions["Enemies"]: 0,
                    coalitions["Allies"]: 0,
                },
            }

        if value["deaths"] != 0:
            inventory_changes["unit_air"][value["unit_type"]]["destroyed"][value["unit_coalition"]] += 1
        elif len(value["hit_received"]) > 0:
            inventory_changes["unit_air"][value["unit_type"]]["damaged"][value["unit_coalition"]] += 1

    # Ground_Units
    for key, value in id_list["unit_ground"].items():
        if value["unit_type"] not in inventory_changes["unit_ground"]:
            inventory_changes["unit_ground"][value["unit_type"]] = {
                "damaged": {
                    coalitions["Enemies"]: 0,
                    coalitions["Allies"]: 0,
                },
                "destroyed": {
                    coalitions["Enemies"]: 0,
                    coalitions["Allies"]: 0,
                },
            }

        if value["deaths"] != 0:
            inventory_changes["unit_ground"][value["unit_type"]]["destroyed"][value["unit_coalition"]] += 1
        elif len(value["hit_received"]) > 0:
            inventory_changes["unit_ground"][value["unit_type"]]["damaged"][value["unit_coalition"]] += 1

    return inventory_changes


# CREATE PILOTLIST
def get_pilotlist(id_list):
    pilotlist = dict()

    for key, value in id_list["unit_air"].items():
        if any(pilot.upper() in value["unit_pilot"].upper() for pilot in squadron_names) or any(pilot.upper() in value["unit_pilot"].upper() for pilot in guest_names):
            # PILOT
            # if Pilot not in list
            if value["unit_pilot"] not in pilotlist:
                a2a_shots = 0
                a2a_hits = 0
                a2g_shots = 0
                a2g_hits = 0
                for shot in value["weapons_fired"]:
                    if shot in id_list["weapons"]:
                        if id_list["weapons"][shot]["weapon_type"] in weapon_a2a:
                            a2a_shots += int(id_list["weapons"][shot]["weapon_count"])
                            a2a_hits += len(id_list["weapons"][shot]["hits"])
                        elif id_list["weapons"][shot]["weapon_type"] in weapon_a2g:
                            a2g_shots += int(id_list["weapons"][shot]["weapon_count"])
                            a2g_hits += len(id_list["weapons"][shot]["hits"])

                a2a_kills = 0
                a2g_kills = 0
                killed_units = str()
                for kill in value["kills"]:
                    if kill in id_list["unit_air"]:
                        a2a_kills += 1
                        killed_units += id_list["unit_air"][kill]["unit_type"]
                        killed_units += ", "
                    elif kill in id_list["unit_ground"]:
                        a2g_kills += 1
                        killed_units += id_list["unit_ground"][kill]["unit_type"]
                        killed_units += ", "

                pilotlist[value["unit_pilot"]] = {
                    "sorties": value["sorties"],
                    "landings": value["landings"],
                    "deaths": value["deaths"],
                    "used_airframes": value["unit_type"],
                    "a2a_shots": a2a_shots,
                    "a2a_hits": a2a_hits,
                    "a2a_kills": a2a_kills,
                    "a2g_shots": a2g_shots,
                    "a2g_hits": a2g_hits,
                    "a2g_kills": a2g_kills,
                    "killed_units": killed_units,
                }

            # if Pilot already in list
            else:
                pilotlist[value["unit_pilot"]]["sorties"] += value["sorties"]
                pilotlist[value["unit_pilot"]]["landings"] += value["landings"]
                pilotlist[value["unit_pilot"]]["deaths"] += value["deaths"]
                pilotlist[value["unit_pilot"]]["used_airframes"] += ", %s" % value["unit_type"]

                for shot in value["weapons_fired"]:
                    if shot in id_list["weapons"]:
                        if id_list["weapons"][shot]["weapon_type"] in weapon_a2a:
                            pilotlist[value["unit_pilot"]]["a2a_shots"] += int(id_list["weapons"][shot]["weapon_count"])
                            pilotlist[value["unit_pilot"]]["a2a_hits"] += len(id_list["weapons"][shot]["hits"])
                        elif id_list["weapons"][shot]["weapon_type"] in weapon_a2g:
                            pilotlist[value["unit_pilot"]]["a2g_shots"] += int(id_list["weapons"][shot]["weapon_count"])
                            pilotlist[value["unit_pilot"]]["a2g_hits"] += len(id_list["weapons"][shot]["hits"])

                killed_units = str()
                for kill in value["kills"]:
                    if kill in id_list["unit_air"]:
                        pilotlist[value["unit_pilot"]]["a2a_kills"] += 1
                        killed_units += id_list["unit_air"][kill]["unit_type"]
                        killed_units += ", "
                    elif kill in id_list["unit_ground"]:
                        pilotlist[value["unit_pilot"]]["a2g_kills"] += 1
                        killed_units += id_list["unit_ground"][kill]["unit_type"]
                        killed_units += ", "
                pilotlist[value["unit_pilot"]]["killed_units"] += killed_units

            # RIO
            if value["unit_rio"] != "":
                if value["unit_rio"] not in pilotlist:
                    a2a_shots = 0
                    a2a_hits = 0
                    a2g_shots = 0
                    a2g_hits = 0
                    for shot in value["weapons_fired"]:
                        if shot in id_list["weapons"]:
                            if id_list["weapons"][shot]["weapon_type"] in weapon_a2a:
                                a2a_shots += int(id_list["weapons"][shot]["weapon_count"])
                                a2a_hits += len(id_list["weapons"][shot]["hits"])
                            elif id_list["weapons"][shot]["weapon_type"] in weapon_a2g:
                                a2g_shots += int(id_list["weapons"][shot]["weapon_count"])
                                a2g_hits += len(id_list["weapons"][shot]["hits"])

                    a2a_kills = 0
                    a2g_kills = 0
                    killed_units = str()
                    for kill in value["kills"]:
                        if kill in id_list["unit_air"]:
                            a2a_kills += 1
                            killed_units += id_list["unit_air"][kill]["unit_type"]
                            killed_units += ", "
                        elif kill in id_list["unit_ground"]:
                            a2g_kills += 1
                            killed_units += id_list["unit_ground"][kill]["unit_type"]
                            killed_units += ", "

                    pilotlist[value["unit_rio"]] = {
                        "sorties": value["sorties"],
                        "landings": value["landings"],
                        "deaths": value["deaths"],
                        "used_airframes": "%s [RIO]" % value["unit_type"],
                        "a2a_shots": a2a_shots,
                        "a2a_hits": a2a_hits,
                        "a2a_kills": a2a_kills,
                        "a2g_shots": a2g_shots,
                        "a2g_hits": a2g_hits,
                        "a2g_kills": a2g_kills,
                        "killed_units": killed_units,
                    }

                # if already in list
                else:
                    pilotlist[value["unit_rio"]]["sorties"] += value["sorties"]
                    pilotlist[value["unit_rio"]]["landings"] += value["landings"]
                    pilotlist[value["unit_rio"]]["deaths"] += value["deaths"]
                    pilotlist[value["unit_rio"]]["used_airframes"] += ", %s [RIO]" % value["unit_type"]

                    for shot in value["weapons_fired"]:
                        if shot in id_list["weapons"]:
                            if id_list["weapons"][shot]["weapon_type"] in weapon_a2a:
                                pilotlist[value["unit_rio"]]["a2a_shots"] += int(id_list["weapons"][shot]["weapon_count"])
                                pilotlist[value["unit_rio"]]["a2a_hits"] += len(id_list["weapons"][shot]["hits"])
                            elif id_list["weapons"][shot]["weapon_type"] in weapon_a2g:
                                pilotlist[value["unit_rio"]]["a2g_shots"] += int(id_list["weapons"][shot]["weapon_count"])
                                pilotlist[value["unit_rio"]]["a2g_hits"] += len(id_list["weapons"][shot]["hits"])

                    killed_units = str()
                    for kill in value["kills"]:
                        if kill in id_list["unit_air"]:
                            pilotlist[value["unit_rio"]]["a2a_kills"] += 1
                            killed_units += id_list["unit_air"][kill]["unit_type"]
                            killed_units += ", "
                        elif kill in id_list["unit_ground"]:
                            pilotlist[value["unit_rio"]]["a2g_kills"] += 1
                            killed_units += id_list["unit_ground"][kill]["unit_type"]
                            killed_units += ", "
                    pilotlist[value["unit_rio"]]["killed_units"] += killed_units

    return pilotlist


# WRITE RAW LISTS TO GOOGLE SPREADSHEET
def write_doc_rawdata(creds, spreadsheet_id, spreadsheet_range, header, valuelist):
    # create data to write
    service = build('sheets', 'v4', credentials=creds)

    values = list()
    values.append(header)

    for entry in valuelist:
        row = list()
        for key, value in entry.items():
            row.append(value)
        values.append(row)

    body = {'values': values}

    # Call the Sheets API, clear Range, write Data
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=spreadsheet_range).execute()

    result2 = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=spreadsheet_range,
        valueInputOption='RAW', body=body).execute()
    print('%s: %s cells updated.' % (spreadsheet_range, result2.get('updatedCells')))

    return


# WRITE CUSTOM LISTS TO GOOGLE SPREADSHEET
def write_doc_list(creds, spreadsheet_id, spreadsheet_range, values):
    # create data to write
    service = build('sheets', 'v4', credentials=creds)

    body = {'values': values}

    # Call the Sheets API, clear Range, write Data
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=spreadsheet_range).execute()

    result2 = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=spreadsheet_range,
        valueInputOption='RAW', body=body).execute()
    print('%s: %s cells updated.' % (spreadsheet_range, result2.get('updatedCells')))

    return


# MAIN FUNCTION
def main():
    global unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed, unit_scored_hits, unit_scored_kills

    # get Mission-Spreadsheet
    mission_spreadsheet_id = list_mission_spreadsheet[current_mission]

    # get OAUTH-token
    creds = oauth()

    # import csv-file
    import_file = import_path + current_mission + ".csv"
    import_csv(import_file)

    # create id_list
    id_list = get_id_list()

    # create weapons_used list
    weapons_used = get_weapons_used(id_list)

    # create inventory_changes list
    inventroy_changes = get_inventory_changes(id_list)

    # create pilotlist (summary of mission) list
    pilotlist = get_pilotlist(id_list)

    # write raw-event-data
    for rawlist in [unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed]:
        if rawlist == unit_spawned:
            tablerangename = 'unit_spawned'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_tookoff:
            tablerangename = 'unit_tookoff'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_landed:
            tablerangename = 'unit_landed'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_despawned:
            tablerangename = 'unit_despawned'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_fired:
            tablerangename = 'unit_fired'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_hit:
            tablerangename = 'unit_hit'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)
        elif rawlist == unit_destroyed:
            tablerangename = 'unit_destroyed'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], raw_headerrow, rawlist)

    # write Weapons Fired
    tablerangename = 'weapons_fired'
    weapons_fired_list = list()

    for key, value in weapons_used.items():
        weapons_fired_list.append([key, value[coalitions["Enemies"]], value[coalitions["Allies"]]])

    weapons_fired_list.sort()
    headerrow = ["Weapon", coalitions["Enemies"], coalitions["Allies"]]
    weapons_fired_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], weapons_fired_list)
    if write_to_summary:
        mission_range = current_mission + "!O:Q"
        write_doc_list(creds, total_summary_sheet, mission_range, weapons_fired_list)

    # write units destroyed and damaged
    air_tablerangename = 'i_c_air_unit'
    ground_tablerangename = 'i_c_ground_unit'
    i_c_air = list()
    i_c_ground = list()

    for key, value in inventroy_changes["unit_air"].items():
        i_c_air.append([key, value["damaged"][coalitions["Enemies"]], value["damaged"][coalitions["Allies"]], value["destroyed"][coalitions["Enemies"]], value["destroyed"][coalitions["Allies"]]])

    for key, value in inventroy_changes["unit_ground"].items():
        i_c_ground.append([key, value["damaged"][coalitions["Enemies"]], value["damaged"][coalitions["Allies"]], value["destroyed"][coalitions["Enemies"]], value["destroyed"][coalitions["Allies"]]])

    i_c_air.sort()
    i_c_ground.sort()

    i_c_air.insert(0, ["", coalitions["Enemies"], coalitions["Allies"], coalitions["Enemies"], coalitions["Allies"]])
    i_c_air.insert(0, ["Aircraft", "Damaged", "", "Destroyed"])
    i_c_air.insert(0, ["Aircraft"])
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[air_tablerangename], i_c_air)
    if write_to_summary:
        mission_range = current_mission + "!T:X"
        write_doc_list(creds, total_summary_sheet, mission_range, i_c_air)

    i_c_ground.insert(0, ["", coalitions["Enemies"], coalitions["Allies"], coalitions["Enemies"], coalitions["Allies"]])
    i_c_ground.insert(0, ["Ground Unit", "Damaged", "", "Destroyed"])
    i_c_ground.insert(0, ["Ground Unit"])
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[ground_tablerangename], i_c_ground)
    if write_to_summary:
        mission_range = current_mission + "!Z:AD"
        write_doc_list(creds, total_summary_sheet, mission_range, i_c_ground)

    # Pilot overview
    finallist = list()

    for key, value in pilotlist.items():
        finallist.append([
            key,
            value["sorties"],
            value["landings"],
            value["deaths"],
            value["used_airframes"],
            value["a2a_shots"],
            value["a2a_hits"],
            value["a2a_kills"],
            value["a2g_shots"],
            value["a2g_hits"],
            value["a2g_kills"],
            value["killed_units"],
        ])

    finallist.sort()

    finallist.insert(0, [aic[current_mission], "AIC", 0, 0, "", 0, 0, 0, 0, 0, 0, ""])

    tablerangename = 'pilot_overview'
    headerrow = ["Pilot", "Sorties", "Landings", "Deaths", "Used Airframes", "A2A-Shots", "A2A-Hits", "A2A-Kills", "A2G-Shots", "A2G-Hits", "A2G-Kills", "Killed Units"]
    finallist.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], finallist)
    if write_to_summary:
        mission_range = current_mission + "!A1:N"
        write_doc_list(creds, total_summary_sheet, mission_range, finallist)
    return


# RUN MAIN
if __name__ == '__main__':
    main()
