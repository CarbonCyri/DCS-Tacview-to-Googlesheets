####################################################################################################
# EDIT THIS FOR EACH MISSION:
####################################################################################################

# write to total summary sheet?
write_to_summary = True

# campaign abbreviation for seperate statistics )Missions starting with this abbreviation will be included into the campaign statistics aswell as the total statistics)
campaign_abbreviation = "II: "

# path to Tacview Flight Log Export .csv File
# Filename = current_mission_name + .csv
import_path = "E:/Daten/Niclas/Owncloud/Documents/DCS/DFA/"

# CSV-DELIMITER
# ENTER THE DELIMITER IN THE CSV-FILE. USUALLY IT IS A ',' BUT MAY VARY WHEN YOU EDIT THE DATA
csv_delimiter = ";"

# MISSION DATA
# Current Mission Name to generate mission-data
current_mission = "01 Operation Arrival"

# replace coalitions "Enemies" and "Allies" according to mission/scenario
# COALITIONS
coalitions = {
    "Enemies": "USA",
    "Allies": "Iran"
}


####################################################################################################
# IF YOU PLAN ON STORING STATISTICS OVER A TIMEFRAME WITH MULTIPLE MISSION YOU MAY WANT TO EXTEND THE FOLLOWING LISTS
# IF YOU ONLY WANT TO EVALUATE A SINGLE MISSION YOU CAN MAKE A SINGLE ENTRY
####################################################################################################

# list containing AIC / GCI / Magic for each mission
# AIC / GCI / MAGIC
aic = {
    "01 Operation Arrival": "Graywo1f",
    "02 Operation Black Meteor": "Cyri",
    "Separatists Aggression 1 Breakout": "None"
}

# dictionary containing list of F14 Pilot&Rio crew for each mission
# F14 CREW
f14_crew = {
    "01 Operation Arrival": [
        {
            "pilot": "Lumberhax",
            "rio": "Tyrant"
        },
        {
            "pilot": "Tricker",
            "rio": "Sport"
        },
        {
            "pilot": "SoupyC",
            "rio": "SixMarbles"
        },
        {
            "pilot": "TigerWolf",
            "rio": "DocEast"
        }
    ],
    "02 Operation Black Meteor": [
        {
            "pilot": "Graywo1f",
            "rio": "Tyrant"
        },
        {
            "pilot": "Tequila",
            "rio": "EinsteinEP"
        },
        {
            "pilot": "Lumberhax",
            "rio": "Dut"
        },
        {
            "pilot": "Tigerwolf",
            "rio": "Fletcher"
        }
    ],
    "Separatists Aggression 1 Breakout": [
        {
            "pilot": "Graywo1f",
            "rio": "Cyri"
        },
        {
            "pilot": "Squinkys",
            "rio": "Keen"
        },
    ]
}

####################################################################################################
# ENTER THE ID OF EACH SPREADSHEET TO WRITE DATA INTO
# THE ID CAN BE FOUND IN THE URL OF THE SPREADSHEET
# https://docs.google.com/spreadsheets/d/1d0SPBhFzTTTzTLj9uVRJ7j5B1QxGhP5YHDetQnBOlMg/edit?usp=sharing
#                                        |--------------------URL-------------------|
####################################################################################################

# total statistics spreadsheet
# e.g. https://docs.google.com/spreadsheets/d/1d0SPBhFzTTTzTLj9uVRJ7j5B1QxGhP5YHDetQnBOlMg/edit?usp=sharing
total_summary_sheet = "1d0SPBhFzTTTzTLj9uVRJ7j5B1QxGhP5YHDetQnBOlMg"

# dictionary containing mission-spreadsheets of each mission
# e.g. https://docs.google.com/spreadsheets/d/1r0j8678ta6rijah7clXQOj7Cu0jDX0ItWpax0zM7Oho/edit?usp=sharing
list_mission_spreadsheet = {
    "01 Operation Arrival": "14zWn5XqDT0o69ul4NIDj6rXulohM0GvwvYedvvwDDjs",
    "02 Operation Black Meteor": "1Z69rekTdwquGu41sZpZbMkpWZckfHNTwJwSTEsaap-Y",
    "Separatists Aggression 1 Breakout": "1r0j8678ta6rijah7clXQOj7Cu0jDX0ItWpax0zM7Oho",
}

# DO NOT CHANGE THIS IF YOU USE THE PREMADE SPREADSHEETS
# Subsheet names & ranges
SPREADSHEETRANGE = {
    'unit_spawned': 'Spawned',
    'unit_tookoff': 'Tookoff',
    'unit_landed': 'Landed',
    'unit_despawned': 'Despawned',
    'unit_fired': 'Fired',
    'unit_hit': 'Hit',
    'unit_destroyed': 'Destroyed',
    'weapons_fired': 'Weapons Fired',
    'i_c_air_unit': 'Units damaged or destroyed!A:E',
    'i_c_ground_unit': 'Units damaged or destroyed!G:K',
    'pilot_overview': 'Pilot overview'
}

####################################################################################################
# ENTER THE NAMES OF YOUR PILOTS HERE. ONLY PILOTS IN THE LIST WILL BE ADDED TO THE SPREADSHEETS
####################################################################################################

# Squadron-pilot list
squadron_names = [
    "Acidic",
    "Cyri",
    "DocEast",
    "Dut",
    "EinsteinEP",
    "evilnate",
    "Fixierider",
    "Fletcher",
    "Franky_Riz",
    "Funkyb",
    "Graywo1f",
    "Grimes",
    "Hell_Gato",
    "Keen",
    "Lumberhax",
    "Phoenix702",
    "Pied Piper",
    "Riserburn",
    "Scare_St",
    "SixMarbles",
    "SoupyC",
    "Sport",
    "Squinkys",
    "Tequila",
    "Thendash",
    "Thump",
    "Tigerwolf",
    "Toast",
    "Tricker",
    "Tyrant",
    "Washout"
]

# Guest-pilot list
guest_names = [
    "alqadib alkabir aldukhum",
    "alshaytan alkabir",
    "Daamir al-Amer",
    "Ghus Al'um",
    "Iahm Kabir",
    "kabab 'umuk",
    "rawh allah alkhaminii",
]

####################################################################################################
####################################################################################################
# DO NOT CHANGE THE FOLLOWING:
####################################################################################################

# Scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# HEADER ROW
raw_headerrow = ['\ufeffMission Time',
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
