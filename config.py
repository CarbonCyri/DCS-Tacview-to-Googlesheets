# Tacview Flight Log Export File
import_file = "E:/Daten/Niclas/Owncloud/Desktop/Tacview-20190505-135644-DCS-Iranian_Intervention_Mission_2_Opening_Night.csv"

####################################################################################################
# MISSION DATA
# COALITIONS
coalitions = {
    "Enemies": "USA",
    "Allies": "Iran"
}

# F14 CREW
f14_crew = [
    {
        "pilot": "Tiger 1-1 Graywo1f",
        "rio": "Tiger 1-1 // =DFA=Tyrant"
    },
    {
        "pilot": "Tiger 1-2 Tequila",
        "rio": "Tiger 1-2 EinsteinEP"
    },
    {
        "pilot": "Panther 1-1 Lumberhax",
        "rio": "Panther 1-1 Dut"
    },
    {
        "pilot": "Panther 1-2 Tigerwolf",
        "rio": "Panther 1-2 Fletcher"
    },
]


# Google API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

MISSION_SPREADSHEET_ID = '1_jSAaQKzehmZ0vqOMS221kufiZNMFxfEQGEjJwAXSzA'
SPREADSHEETRANGE = {
    'unit_spawned': 'Spawned',
    'unit_tookoff': 'Tookoff',
    'unit_landed': 'Landed',
    'unit_despawned': 'Despawned',
    'unit_fired': 'Fired',
    'unit_hit': 'Hit',
    'unit_destroyed': 'Destroyed',
    'weapons_fired': 'Weapons Fired',
    'unit_kills': 'Units damaged or destroyed!A:C',
    'unit_hits': 'Units damaged or destroyed!E:G',
    'hits': 'Hits and Kills!A:C',
    'kills': 'Hits and Kills!E:G'
}
