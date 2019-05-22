import pickle
import os.path
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import *

# VARIABLES
unit_spawned = list()
unit_tookoff = list()
unit_landed = list()
unit_despawned = list()
unit_fired = list()
unit_hit = list()
unit_destroyed = list()
unit_scored_hits = list()
unit_scored_kills = list()


# OAUTH CREDENTIALS
# Load credentials from token.pickle if possible, else request token using credentials.json from google oauth
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


# CSV-READER
# import Mission.csv file; default delimiter = ','
def import_csv(csv_file):
    tacview_log = []

    with open(csv_file, "r", encoding="utf8") as file:
        if csv_delimiter is None:
            csv_delimiter = ','
        reader = csv.DictReader(file, delimiter=csv_delimiter)
        for line in reader:
            tacview_log.append(line)

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

    # add Rio to Primary Unit if Unit == F-14B, if Pilot/Rio pair is in config-list
    for unit_list in [unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed]:
        for x in range(len(unit_list)):
            if unit_list[x]["Primary Object Name"] == "F-14B Tomcat":
                generator = (crew for crew in f14_crew[current_mission] if unit_list[x]["Primary Object Pilot"] in crew.values())
                for item in generator:
                    unit_list[x]["Primary Object Pilot"] = item["pilot"]
                    unit_list[x]["Primary Object Rio"] = item["rio"]

    return


# GET WEAPONS FIRED
# dict: [coalition][weapon_type] = count
def get_weapons_fired():
    # create initial dict
    total_weapons_fired = dict()
    for coalition in coalitions:
        total_weapons_fired[coalitions] = dict()
    
    # write data
    for shot in unit_fired:
        weapon_name = shot["Secondary Object Name"]
        weapon_count = shot["Occurrences"]
        weapon_coalition = shot["Primary Object Coalition"]
        # if weapon already in dict
        if weapon_name in total_weapons_fired[weapon_coalition]:
            total_weapons_fired[weapon_coalition][weapon_name] += int(weapon_count)
        # if weapon not already in dict
        else:
            total_weapons_fired[weapon_coalition][weapon_name] = int(weapon_count)

    return total_weapons_fired


# GET UNIT DAMAGED OR DESTROYED
# dict: [coalition][destroyed/damaged][unit_type] = count
def get_unit_damage():
    # create initial dict
    unit_dnd = dict()
    for coalition in coalitions:
        unit_dnd[coalition] = {
                               "destroyed": {},
                               "damaged": {}
                               }

    # write data
    for unit in unit_destroyed:
        unit_id = unit["Primary Object ID"]
        unit_coalition = unit["Primary Object Coalition"]
        # if no unit_coalition
        if unit_coalition == "":
            continue
        unit_type = unit["Primary Object Name"]
        unit_pilot = unit["Primary Object Pilot"]
        unit_rio = "-"
        # check for Rio for primary_unit
        generator = (crew for crew in f14_crew[current_mission] if unit_pilot in crew.values())
        for item in generator:
            unit_pilot = item["pilot"]
            unit_rio = item["rio"]
        unit_killer = unit["Secondary Object Pilot"]
        unit_killer_rio = "-"
        # check for Rio for secondary_unit
        generator = (crew for crew in f14_crew[current_mission] if unit_killer in crew.values())
        for item in generator:
            unit_killer = = item["pilot"]
            unit_killer_rio = item["rio"]

        # if unit == F-14B
        if unit_type == "F-14B Tomcat":
            unit_dnd[unit_coalition]["destroyed"][unit_id] = {
                "Type": unit_type,
                "Pilot": unit_pilot,
                "Rio": unit_rio
            }
        # if unit != AI
        elif unit_pilot != "":
            unit_dnd[unit_coalition]["destroyed"][unit_id] = {
                "Type": unit_type,
                "Pilot": unit_pilot
            }
        # if unit == AI
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
        if unit_coalition == "":
            continue
        unit_type = unit["Primary Object Name"]
        unit_pilot = unit["Primary Object Pilot"]
        unit_rio = "-"
        generator = (crew for crew in f14_crew[current_mission] if unit_pilot in crew.values())
        for item in generator:
            unit_pilot = item["pilot"]
            unit_rio = item["rio"]
        unit_killer = unit["Relevant Object Pilot"]
        unit_killer_rio = "-"
        generator = (crew for crew in f14_crew[current_mission] if unit_killer in crew.values())
        for item in generator:
            unit_killer = item["pilot"]
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

    return unit_dnd


# GET INVENTORY CHANGE
def get_inventory_changes(unit_dnd):
    inventroy_changes = {
        "USA": {
            "destroyed": dict(),
            "damaged": dict()
        },
        "Iran": {
            "destroyed": dict(),
            "damaged": dict()
        },
    }

    # units destroyed
    for unitid, unit in unit_dnd["USA"]["destroyed"].items():
        if unit["Type"] in inventroy_changes["USA"]["destroyed"]:
            inventroy_changes["USA"]["destroyed"][unit["Type"]] += 1
        else:
            inventroy_changes["USA"]["destroyed"][unit["Type"]] = 1

    for unitid, unit in unit_dnd["Iran"]["destroyed"].items():
        if unit["Type"] in inventroy_changes["Iran"]["destroyed"]:
            inventroy_changes["Iran"]["destroyed"][unit["Type"]] += 1
        else:
            inventroy_changes["Iran"]["destroyed"][unit["Type"]] = 1

    # units damaged
    for unitid, unit in unit_dnd["USA"]["damaged"].items():
        if unit["Type"] in inventroy_changes["USA"]["damaged"]:
            inventroy_changes["USA"]["damaged"][unit["Type"]] += 1
        else:
            inventroy_changes["USA"]["damaged"][unit["Type"]] = 1

    for unitid, unit in unit_dnd["Iran"]["damaged"].items():
        if unit["Type"] in inventroy_changes["Iran"]["damaged"]:
            inventroy_changes["Iran"]["damaged"][unit["Type"]] += 1
        else:
            inventroy_changes["Iran"]["damaged"][unit["Type"]] = 1

    return inventroy_changes


# GET WEAPON TYPE
def get_weapon_type(weapon):
    if weapon in weapon_gun:
        return "gun"
    elif weapon in weapon_a2a:
        return "a2a"
    elif weapon in weapon_a2g:
        return "a2g"
    elif weapon in weapon_g2a:
        return "g2a"
    elif weapon in weapon_g2g:
        return "g2g"
    elif weapon in weapon_misc:
        return "misc"


# create Pilotlist summary
def get_pilot_summary():
    pilotlist = dict()
    iran_pilotlist = dict()

    # Takeoffs
    for item in unit_tookoff:
        if item["Primary Object Pilot"] == "":
            continue

        if item["Primary Object Name"] == "F-14B Tomcat":
            item["Primary Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Primary Object Pilot"] in crew.values())
            for item2 in generator:
                item["Primary Object Pilot"] = item2["pilot"]
                item["Primary Object Rio"] = item2["rio"]

            # USA Rio
            if item["Primary Object Coalition"] == "USA":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in pilotlist:
                    pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 1,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": "%s [Rio]" % item["Primary Object Name"],
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    pilotlist[item["Primary Object Rio"]]["Sorties"] += 1
                    pilotlist[item["Primary Object Rio"]]["Used Airframes"] += ", %s [Rio]" % item["Primary Object Name"]

            # Iran Rio
            elif item["Primary Object Coalition"] == "Iran":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 1,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": "%s [Rio]" % item["Primary Object Name"],
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    iran_pilotlist[item["Primary Object Rio"]]["Sorties"] += 1
                    iran_pilotlist[item["Primary Object Rio"]]["Used Airframes"] += ", %s [Rio]" % item["Primary Object Name"]

        # USA Pilot
        if item["Primary Object Coalition"] == "USA":
            if item["Primary Object Pilot"] not in pilotlist:
                pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 1,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": item["Primary Object Name"],
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                pilotlist[item["Primary Object Pilot"]]["Sorties"] += 1
                pilotlist[item["Primary Object Pilot"]]["Used Airframes"] += ", %s" % item["Primary Object Name"]

        # Iran Pilot
        elif item["Primary Object Coalition"] == "Iran":
            if item["Primary Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 1,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": item["Primary Object Name"],
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                iran_pilotlist[item["Primary Object Pilot"]]["Sorties"] += 1
                iran_pilotlist[item["Primary Object Pilot"]]["Used Airframes"] += ", %s" % item["Primary Object Name"]

    # Landings
    for item in unit_landed:
        if item["Primary Object Pilot"] == "":
            continue

        if item["Primary Object Name"] == "F-14B Tomcat":
            item["Primary Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Primary Object Pilot"] in crew.values())
            for item2 in generator:
                item["Primary Object Pilot"] = item2["pilot"]
                item["Primary Object Rio"] = item2["rio"]

            # USA Rio
            if item["Primary Object Coalition"] == "USA":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in pilotlist:
                    pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 1,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    pilotlist[item["Primary Object Rio"]]["Landings"] += 1

            # Iran Rio
            elif item["Primary Object Coalition"] == "Iran":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 1,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    iran_pilotlist[item["Primary Object Rio"]]["Landings"] += 1

        # USA Pilot
        if item["Primary Object Coalition"] == "USA":
            if item["Primary Object Pilot"] not in pilotlist:
                pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 1,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                pilotlist[item["Primary Object Pilot"]]["Landings"] += 1

        # Iran Pilot
        elif item["Primary Object Coalition"] == "Iran":
            if item["Primary Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 1,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                iran_pilotlist[item["Primary Object Pilot"]]["Landings"] += 1

    # Deaths
    for item in unit_destroyed:
        if item["Primary Object Pilot"] == "":
            continue

        if item["Primary Object Name"] == "F-14B Tomcat":
            item["Primary Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Primary Object Pilot"] in crew.values())
            for item2 in generator:
                item["Primary Object Pilot"] = item2["pilot"]
                item["Primary Object Rio"] = item2["rio"]

            # USA Rio
            if item["Primary Object Coalition"] == "USA":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in pilotlist:
                    pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 1,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    pilotlist[item["Primary Object Rio"]]["Deaths"] += 1

            # Iran Rio
            elif item["Primary Object Coalition"] == "Iran":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 1,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }
                elif item["Primary Object Rio"] is not None:
                    iran_pilotlist[item["Primary Object Rio"]]["Deaths"] += 1

        # USA Pilot
        if item["Primary Object Coalition"] == "USA":
            if item["Primary Object Pilot"] not in pilotlist:
                pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 1,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                pilotlist[item["Primary Object Pilot"]]["Deaths"] += 1

        # Iran Pilot
        elif item["Primary Object Coalition"] == "Iran":
            if item["Primary Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 1,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }
            else:
                iran_pilotlist[item["Primary Object Pilot"]]["Deaths"] += 1

    # Shots
    for item in unit_fired:
        if item["Primary Object Pilot"] == "":
            continue
        elif item["Secondary Object Name"] == "weapons.shells.M56A3_HE_RED":
            continue

        # Get Weapon Type
        weapontype = get_weapon_type(item["Secondary Object Name"])

        if item["Primary Object Name"] == "F-14B Tomcat":
            item["Primary Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Primary Object Pilot"] in crew.values())
            for item2 in generator:
                item["Primary Object Pilot"] = item2["pilot"]
                item["Primary Object Rio"] = item2["rio"]

            # USA Rio
            if item["Primary Object Coalition"] == "USA":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in pilotlist:
                    pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Primary Object Rio"] is not None:
                    if weapontype == "a2a":
                        pilotlist[item["Primary Object Rio"]]["a2a_Shots"] += int(item["Occurrences"])
                    elif weapontype == "a2g":
                        pilotlist[item["Primary Object Rio"]]["a2g_Shots"] += int(item["Occurrences"])

            # Iran Rio
            if item["Primary Object Coalition"] == "Iran":
                if item["Primary Object Rio"] is not None and item["Primary Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Primary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Primary Object Rio"] is not None:
                    if weapontype == "a2a":
                        iran_pilotlist[item["Primary Object Rio"]]["a2a_Shots"] += int(item["Occurrences"])
                    elif weapontype == "a2g":
                        iran_pilotlist[item["Primary Object Rio"]]["a2g_Shots"] += int(item["Occurrences"])

        # USA Pilot
        if item["Primary Object Coalition"] == "USA":
            if item["Primary Object Pilot"] not in pilotlist:
                pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if weapontype == "a2a":
                pilotlist[item["Primary Object Pilot"]]["a2a_Shots"] += int(item["Occurrences"])
            elif weapontype == "a2g":
                pilotlist[item["Primary Object Pilot"]]["a2g_Shots"] += int(item["Occurrences"])

        # Iran Pilot
        if item["Primary Object Coalition"] == "Iran":
            if item["Primary Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Primary Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if weapontype == "a2a":
                iran_pilotlist[item["Primary Object Pilot"]]["a2a_Shots"] += int(item["Occurrences"])
            elif weapontype == "a2g":
                iran_pilotlist[item["Primary Object Pilot"]]["a2g_Shots"] += int(item["Occurrences"])

    # Hits
    for item in unit_hit:
        if item["Relevant Object Pilot"] == "":
            continue

        # Get Weapon Type
        weapontype = get_weapon_type(item["Secondary Object Name"])

        if item["Relevant Object Name"] == "F-14B Tomcat":
            item["Relevant Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Relevant Object Pilot"] in crew.values())
            for item2 in generator:
                item["Relevant Object Pilot"] = item2["pilot"]
                item["Relevant Object Rio"] = item2["rio"]

            # USA Rio
            if item["Relevant Object Coalition"] == "USA":
                if item["Relevant Object Rio"] is not None and item["Relevant Object Rio"] not in pilotlist:
                    pilotlist[item["Relevant Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Relevant Object Rio"] is not None:
                    if weapontype == "a2a":
                        pilotlist[item["Relevant Object Rio"]]["a2a_Hits"] += int(item["Occurrences"])
                    elif weapontype == "a2g":
                        pilotlist[item["Relevant Object Rio"]]["a2g_Hits"] += int(item["Occurrences"])

            # Iran Rio
            if item["Relevant Object Coalition"] == "Iran":
                if item["Relevant Object Rio"] is not None and item["Relevant Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Relevant Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Relevant Object Rio"] is not None:
                    if weapontype == "a2a":
                        iran_pilotlist[item["Relevant Object Rio"]]["a2a_Hits"] += int(item["Occurrences"])
                    elif weapontype == "a2g":
                        iran_pilotlist[item["Relevant Object Rio"]]["a2g_Hits"] += int(item["Occurrences"])

        # USA Pilot
        if item["Relevant Object Coalition"] == "USA":
            if item["Relevant Object Pilot"] not in pilotlist:
                pilotlist[item["Relevant Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if weapontype == "a2a":
                pilotlist[item["Relevant Object Pilot"]]["a2a_Hits"] += int(item["Occurrences"])
            elif weapontype == "a2g":
                pilotlist[item["Relevant Object Pilot"]]["a2g_Hits"] += int(item["Occurrences"])

        # Iran Pilot
        if item["Relevant Object Coalition"] == "Iran":
            if item["Relevant Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Relevant Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if weapontype == "a2a":
                iran_pilotlist[item["Relevant Object Pilot"]]["a2a_Hits"] += int(item["Occurrences"])
            elif weapontype == "a2g":
                iran_pilotlist[item["Relevant Object Pilot"]]["a2g_Hits"] += int(item["Occurrences"])

    # Kills
    for item in unit_destroyed:
        if item["Secondary Object Pilot"] == "":
            continue

        # Get Weapon Type
        if item["Primary Object Name"] in aircrafts:
            targettype = "air"
        elif item["Primary Object Name"] in groundunits:
            targettype = "ground"
        else:
            targettype = None

        if item["Secondary Object Name"] == "F-14B Tomcat":
            item["Secondary Object Rio"] = None
            generator = (crew for crew in f14_crew[current_mission] if item["Secondary Object Pilot"] in crew.values())
            for item2 in generator:
                item["Secondary Object Pilot"] = item2["pilot"]
                item["Secondary Object Rio"] = item2["rio"]

            # USA Rio
            if item["Secondary Object Coalition"] == "USA":
                if item["Secondary Object Rio"] is not None and item["Secondary Object Rio"] not in pilotlist:
                    pilotlist[item["Secondary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Secondary Object Rio"] is not None:
                    if targettype == "air":
                        pilotlist[item["Secondary Object Rio"]]["a2a_Kills"] += int(item["Occurrences"])
                    elif targettype == "ground":
                        pilotlist[item["Secondary Object Rio"]]["a2g_Kills"] += int(item["Occurrences"])

                    if pilotlist[item["Secondary Object Rio"]]["Killed Units"] is None:
                        pilotlist[item["Secondary Object Rio"]]["Killed Units"] = "%s" % item["Primary Object Name"]
                    else:
                        pilotlist[item["Secondary Object Rio"]]["Killed Units"] += ", %s" % item["Primary Object Name"]

            # Iran Rio
            if item["Secondary Object Coalition"] == "Iran":
                if item["Secondary Object Rio"] is not None and item["Secondary Object Rio"] not in iran_pilotlist:
                    iran_pilotlist[item["Secondary Object Rio"]] = {
                        "Sorties": 0,
                        "Landings": 0,
                        "Deaths": 0,
                        "Used Airframes": None,
                        "a2a_Shots": 0,
                        "a2a_Hits": 0,
                        "a2a_Kills": 0,
                        "a2g_Shots": 0,
                        "a2g_Hits": 0,
                        "a2g_Kills": 0,
                        "Killed Units": None
                    }

                if item["Secondary Object Rio"] is not None:
                    if targettype == "air":
                        iran_pilotlist[item["Secondary Object Rio"]]["a2a_Kills"] += int(item["Occurrences"])
                    elif targettype == "ground":
                        iran_pilotlist[item["Secondary Object Rio"]]["a2g_Kills"] += int(item["Occurrences"])

                    if iran_pilotlist[item["Secondary Object Rio"]]["Killed Units"] is None:
                        iran_pilotlist[item["Secondary Object Rio"]]["Killed Units"] = "%s" % item["Primary Object Name"]
                    else:
                        iran_pilotlist[item["Secondary Object Rio"]]["Killed Units"] += ", %s" % item["Primary Object Name"]

        # USA Pilot
        if item["Secondary Object Coalition"] == "USA":
            if item["Secondary Object Pilot"] not in pilotlist:
                pilotlist[item["Secondary  Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if targettype == "air":
                pilotlist[item["Secondary Object Pilot"]]["a2a_Kills"] += int(item["Occurrences"])
            elif targettype == "ground":
                pilotlist[item["Secondary Object Pilot"]]["a2g_Kills"] += int(item["Occurrences"])

            if pilotlist[item["Secondary Object Pilot"]]["Killed Units"] is None:
                pilotlist[item["Secondary Object Pilot"]]["Killed Units"] = "%s" % item["Primary Object Name"]
            else:
                pilotlist[item["Secondary Object Pilot"]]["Killed Units"] += ", %s" % item["Primary Object Name"]

        # Iran Pilot
        if item["Secondary Object Coalition"] == "Iran":
            if item["Secondary Object Pilot"] not in iran_pilotlist:
                iran_pilotlist[item["Secondary  Object Pilot"]] = {
                    "Sorties": 0,
                    "Landings": 0,
                    "Deaths": 0,
                    "Used Airframes": None,
                    "a2a_Shots": 0,
                    "a2a_Hits": 0,
                    "a2a_Kills": 0,
                    "a2g_Shots": 0,
                    "a2g_Hits": 0,
                    "a2g_Kills": 0,
                    "Killed Units": None
                }

            if targettype == "air":
                iran_pilotlist[item["Secondary Object Pilot"]]["a2a_Kills"] += int(item["Occurrences"])
            elif targettype == "ground":
                iran_pilotlist[item["Secondary Object Pilot"]]["a2g_Kills"] += int(item["Occurrences"])

            if iran_pilotlist[item["Secondary Object Pilot"]]["Killed Units"] is None:
                iran_pilotlist[item["Secondary Object Pilot"]]["Killed Units"] = "%s" % item["Primary Object Name"]
            else:
                iran_pilotlist[item["Secondary Object Pilot"]]["Killed Units"] += ", %s" % item["Primary Object Name"]

    return pilotlist, iran_pilotlist


# write google docs rawdata
def write_doc_rawdata(creds, spreadsheet_id, spreadsheet_range, header, valuelist):
    # Call the Sheets API
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


# write google docs data
def write_doc_list(creds, spreadsheet_id, spreadsheet_range, values):
    # Call the Sheets API
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


def main():
    global unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed, unit_scored_hits, unit_scored_kills

    mission_spreadsheet_id = list_mission_spreadsheet[current_mission]

    creds = oauth()
    import_file = import_path + current_mission + ".csv"
    import_csv(import_file)
    total_weapons_fired = get_weapons_fired()
    unit_dnd = get_unit_damage()
    inventory_changes = get_inventory_changes(unit_dnd)
    pilot_summary, iran_pilot_summary = get_pilot_summary()

    # Google Docs
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

    # write raw-data
    for rawlist in [unit_spawned, unit_tookoff, unit_landed, unit_despawned, unit_fired, unit_hit, unit_destroyed]:
        if rawlist == unit_spawned:
            tablerangename = 'unit_spawned'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_tookoff:
            tablerangename = 'unit_tookoff'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_landed:
            tablerangename = 'unit_landed'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_despawned:
            tablerangename = 'unit_despawned'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_fired:
            tablerangename = 'unit_fired'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_hit:
            tablerangename = 'unit_hit'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)
        elif rawlist == unit_destroyed:
            tablerangename = 'unit_destroyed'
            write_doc_rawdata(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], headerrow, rawlist)

    ##################################################
    # write Weapons Fired
    tablerangename = 'weapons_fired'
    weapons_fired_list = list()

    for key, value in total_weapons_fired["USA"].items():
        wpn = key.replace('weapons.missiles.', "")
        wpn = wpn.replace('weapons.shells.', "")
        wpn = wpn.replace('weapons.bombs.', "")
        weapons_fired_list.append([wpn, value, 0])

    for key, value in total_weapons_fired["Iran"].items():
        weapon_found = False
        for line in weapons_fired_list:
            if line[0] == key:
                line[2] = value
                weapon_found = True
        if not weapon_found:
            wpn = key.replace('weapons.missiles.', "")
            wpn = wpn.replace('weapons.shells.', "")
            wpn = wpn.replace('weapons.bombs.', "")
            weapons_fired_list.append([wpn, 0, value])

    weapons_fired_list.sort()
    headerrow = ["Weapon", "USA", "Iran"]
    weapons_fired_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], weapons_fired_list)
    ii_smissum_range = current_mission + "!O:Q"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, weapons_fired_list)

    ##################################################
    # write units destroyed and damaged
    air_des_list = list()
    air_dmg_list = list()
    gnd_des_list = list()
    gnd_dmg_list = list()

    # USA
    # destroyed
    for key, value in inventory_changes["USA"]["destroyed"].items():
        unit = key.replace('weapons.missiles.', "")
        unit = unit.replace('weapons.shells.', "")
        unit = unit.replace('weapons.bombs.', "")
        if unit in aircrafts:
            air_des_list.append([unit, value, 0])
        elif unit in groundunits:
            gnd_des_list.append([unit, value, 0])

    # damaged
    for key, value in inventory_changes["USA"]["damaged"].items():
        unit = key.replace('weapons.missiles.', "")
        unit = unit.replace('weapons.shells.', "")
        unit = unit.replace('weapons.bombs.', "")
        if unit in aircrafts:
            air_dmg_list.append([unit, value, 0])
        elif unit in groundunits:
            gnd_dmg_list.append([unit, value, 0])

    # Iran
    # destroyed
    for key, value in inventory_changes["Iran"]["destroyed"].items():
        unit = key.replace('weapons.missiles.', "")
        unit = unit.replace('weapons.shells.', "")
        unit = unit.replace('weapons.bombs.', "")
        unit_found = False

        if unit in aircrafts:
            for line in air_des_list:
                if line[0] == key:
                    line[2] = value
                    unit_found = True
        elif unit in groundunits:
            for line in gnd_des_list:
                if line[0] == key:
                    line[2] = value
                    unit_found = True

        if not unit_found:
            if unit in aircrafts:
                air_des_list.append([unit, 0, value])
            elif unit in groundunits:
                gnd_des_list.append([unit, 0, value])

    # damaged
    for key, value in inventory_changes["Iran"]["damaged"].items():
        unit = key.replace('weapons.missiles.', "")
        unit = unit.replace('weapons.shells.', "")
        unit = unit.replace('weapons.bombs.', "")
        unit_found = False

        if unit in aircrafts:
            for line in air_dmg_list:
                if line[0] == key:
                    line[2] = value
                    unit_found = True
        elif unit in groundunits:
            for line in gnd_dmg_list:
                if line[0] == key:
                    line[2] = value
                    unit_found = True

        if not unit_found:
            if unit in aircrafts:
                air_dmg_list.append([unit, 0, value])
            elif unit in groundunits:
                gnd_dmg_list.append([unit, 0, value])

    # sort lists
    air_des_list.sort()
    air_dmg_list.sort()
    gnd_des_list.sort()
    gnd_dmg_list.sort()

    tablerangename = 'air_unit_des'
    headerrow = ["Aircraft lost", "USA", "Iran"]
    air_des_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], air_des_list)
    ii_smissum_range = current_mission + "!X2:Z"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, air_des_list)

    tablerangename = 'air_unit_dmg'
    headerrow = ["Aircraft damaged", "USA", "Iran"]
    air_dmg_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], air_dmg_list)
    ii_smissum_range = current_mission + "!T2:V"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, air_dmg_list)

    tablerangename = 'gnd_unit_des'
    headerrow = ["Ground Unit lost", "USA", "Iran"]
    gnd_des_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], gnd_des_list)
    ii_smissum_range = current_mission + "!AF2:AH"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, gnd_des_list)

    tablerangename = 'gnd_unit_dmg'
    headerrow = ["Ground Unit Damaged", "USA", "Iran"]
    gnd_dmg_list.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], gnd_dmg_list)
    ii_smissum_range = current_mission + "!AB2:AD"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, gnd_dmg_list)

    ##################################################
    # Hits and Kills

    air_hits = list()
    air_kills = list()
    gnd_hits = list()
    gnd_kills = list()

    for item in unit_scored_hits:
        if item[2] in aircrafts:
            air_hits.append(item)
        elif item[2] in groundunits:
            gnd_hits.append(item)

    for item in unit_scored_kills:
        if item[2] in aircrafts:
            air_kills.append(item)
        elif item[2] in groundunits:
            gnd_kills.append(item)

    air_hits.sort()
    air_kills.sort()
    gnd_hits.sort()
    gnd_kills.sort()

    tablerangename = 'air_hits'
    headerrow = ["Pilot", "Rio", "Target"]
    air_hits.insert(0, headerrow)
    air_kills.insert(0, headerrow)
    gnd_hits.insert(0, headerrow)
    gnd_kills.insert(0, headerrow)

    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], air_hits)

    tablerangename = 'air_kills'
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], air_kills)

    tablerangename = 'gnd_hits'
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], gnd_hits)

    tablerangename = 'gnd_kills'
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], gnd_kills)

    ##################################################
    # Pilot overview
    pilotlist = list()
    iran_pilotlist = list()
    finallist = list()

    for key, value in pilot_summary.items():
        pilotname = key

        for name in dfa_names:
            if name.upper() in key.upper():
                pilotname = name

        pilotlist.append([
            pilotname,
            value["Sorties"],
            value["Landings"],
            value["Deaths"],
            value["Used Airframes"],
            value["a2a_Shots"],
            value["a2a_Hits"],
            value["a2a_Kills"],
            value["a2g_Shots"],
            value["a2g_Hits"],
            value["a2g_Kills"],
            value["Killed Units"]
        ])

    pilotlist.sort()

    for key, value in iran_pilot_summary.items():
        pilotname = key

        for name in dfa_names:
            if name.upper() in key.upper():
                pilotname = name

        iran_pilotlist.append([
            pilotname,
            value["Sorties"],
            value["Landings"],
            value["Deaths"],
            value["Used Airframes"],
            value["a2a_Shots"],
            value["a2a_Hits"],
            value["a2a_Kills"],
            value["a2g_Shots"],
            value["a2g_Hits"],
            value["a2g_Kills"],
            value["Killed Units"]
        ])

    iran_pilotlist.sort()

    finallist.append([aic[current_mission], "AIC"])
    finallist.append([])
    for line in pilotlist:
        finallist.append(line)
    finallist.append([])
    for line in iran_pilotlist:
        finallist.append(line)

    tablerangename = 'pilot_overview'
    headerrow = ["Pilot", "Sorties", "Landings", "Deaths", "Used Airframes", "A2A-Shots", "A2A-Hits", "A2A-Kills", "A2G-Shots", "A2G-Hits", "A2G-Kills", "Killed Units"]
    finallist.insert(0, headerrow)
    write_doc_list(creds, mission_spreadsheet_id, SPREADSHEETRANGE[tablerangename], finallist)
    ii_smissum_range = current_mission + "!A1:L"
    write_doc_list(creds, iranian_intervention_spreadsheet, ii_smissum_range, finallist)
    return


# RUN MAIN
if __name__ == '__main__':
    main()
