# Tacview Flight Log Export File
import_path = "E:/Daten/Niclas/Owncloud/Documents/DCS/DFA Iranian Intervention/"

####################################################################################################
# MISSION DATA
current_mission = "01 Operation Arrival"

# COALITIONS
coalitions = {
    "Enemies": "USA",
    "Allies": "Iran"
}

aic = {
    "01 Operation Arrival": "Graywo1f",
    "02 Operation Black Meteor": "Cyri"
}

# F14 CREW
f14_crew = {
    "01 Operation Arrival": [
        {
            "pilot": "Lumberhax",
            "rio": "=DFA=Tyrant"
        },
        {
            "pilot": "Tricker",
            "rio": "=DFA=Sport"
        },
        {
            "pilot": "SoupyC",
            "rio": "=DFA=SixMarbles"
        },
        {
            "pilot": "TigerWolf",
            "rio": "=DFA= DocEast"
        }
    ],
    "02 Operation Black Meteor": [
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
        }
    ]
}

# Google API
iranian_intervention_spreadsheet = "1Rb__sMln1LxBQ7uksMI9D3SCDxB1ARLeDYFmxVTzH2w"

list_mission_spreadsheet = {
    "01 Operation Arrival": "1dHN4WhJplvqF2AeoR7WL-y_Mi72Ij0oD5B7Nb2RGkfw",
    "02 Operation Black Meteor": "1_jSAaQKzehmZ0vqOMS221kufiZNMFxfEQGEjJwAXSzA"
}

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEETRANGE = {
    'unit_spawned': 'Spawned',
    'unit_tookoff': 'Tookoff',
    'unit_landed': 'Landed',
    'unit_despawned': 'Despawned',
    'unit_fired': 'Fired',
    'unit_hit': 'Hit',
    'unit_destroyed': 'Destroyed',
    'weapons_fired': 'Weapons Fired',
    'air_unit_dmg': 'Units damaged or destroyed!A2:C',
    'air_unit_des': 'Units damaged or destroyed!E2:G',
    'gnd_unit_dmg': 'Units damaged or destroyed!I2:K',
    'gnd_unit_des': 'Units damaged or destroyed!M2:O',
    'air_hits': 'Hits and Kills!A3:C',
    'air_kills': 'Hits and Kills!E3:G',
    'gnd_hits': 'Hits and Kills!I3:K',
    'gnd_kills': 'Hits and Kills!M3:O',
    'pilot_overview': 'Pilot overview'
}

dfa_names = [
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


####################################################################################################
# DCS Units
# Weapons
weapon_gun = [
    "2A7_23_HE",
    "GSH23_23_AP",
    "M56A3_HE_RED",
    "M61_20_AP",
    "M61_20_HE"
]

weapon_a2a = [
    "AIM-120B AMRAAM",
    "AIM-120C AMRAAM",
    "AIM-54A-MK",
    "AIM-54C",
    "AIM-7 Sparrow",
    "AIM-7M Sparrow III",
    "AIM-9 Sidewinder",
    "AIM-9M Sidewinder",
    "AIM-9X Sidewinder",
    "R-27R (AA-10 Alamo-A)",
    "AIM-9L Sidewinder"
]

weapon_a2g = [
    "ADM_141A",
    "9K114 Shturm",
    "AGM-88 HARM",
    "GBU_10",
    "X_25ML",
    "X_25MP",
    "X_31P",
    "KH-31A"
]

weapon_g2a = [
    "3M9M",
    "5V55R",
    "9M33",
    "FIM_92C",
    "Igla_1E",
    "MIM-104",
    "MIM-23B",
    "RIM-66"
]

weapon_g2g = [
    "BGM_109B"
]

weapon_misc = [
    "Missile",
    "Pilot",
    "APU-170"
]

# Aircraft
aircrafts = [
    "B-52H Stratofortress",
    "C-17A Globemaster III",
    "E-3A Sentry",
    "F-14B Tomcat",
    "F-15C Eagle",
    "F-4E Phantom II",
    "F-5E-3 Tiger II",
    "F/A-18C Hornet",
    "KC-135 Stratotanker",
    "Mi-8MT Hip",
    "MiG-29A Fulcrum-A",
    "S-3B Viking",
    "Su-24M Fencer-D",
    "Tu-142",
    "UH-1H Huey"
]

# Groundunits
groundunits = [
    "55G6 Nebo",
    "CG-47 Ticonderoga",
    "Dog Ear Radar",
    "M 818",
    "M163 Vulcan",
    "MIM-23 Hawk (AN/MPQ-46 TR)",
    "MIM-23 Hawk (PCP CT)",
    "MIM-23 Hawk (AN/MPQ-50 SR)",
    "MIM-23 Hawk (M192 LN)",
    "MIM-104 Patriot (AN/MPQ-53 STR)",
    "MIM-104 Patriot (M901 LN)",
    "SA-13 Gopher",
    "SA-2 Guideline (Fan Song E TR)",
    "SA-3 Goa (SR)",
    "Silkworm_SR",
    "Land_Rover_101_FC",
    "S_75M_Volhov",
    "Ural-375",
    "ZU-23-2",
    "hy_launcher"
]
