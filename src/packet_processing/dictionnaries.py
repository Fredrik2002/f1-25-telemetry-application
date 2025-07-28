from PySide6.QtGui import QColor


def rgbtohex(r,g,b):
    return f'#{r:02x}{g:02x}{b:02x}'

def valid_ip_address(adress):
    s = adress.split(".")
    drapeau = len(s)==4
    for element in s:
        if not (element.isdigit() and 0<=int(element)<=255):
            drapeau = False
    return drapeau

black = QColor("#000000")
white = QColor("#FFFFFF")
green = QColor("#00FF00")
blue = QColor("#0000FF")
yellow = QColor("#FFD700")
red = QColor("#FF0000")
purple = QColor("#880088")
gold = QColor("#FFD700")
grey = QColor("#4B4B4B")
orange = QColor("#FF9300")


tyres_dictionnary = {
    0: "S",
    16: "S",
    17: "M",
    18: "H",
    7: "I",
    8: "W"
}

tyres_color_dictionnary = {
    "S": QColor("#FF0000"),
    "M": QColor("#FFD700"),
    "H": QColor("#FFFFFF"),
    "I": QColor("#00FF00"),
    "W": QColor("#0000FF")
}

track_dictionary = { #(track name, highNumber=Small on canvas, x_offset, y_offset)
    0: ("melbourne", 3.5, 300, 300),
    1: ("paul_ricard", 2.5, 500, 300),
    2: ("shanghai", 2, 300, 300),
    3: ("sakhir", 2, 600, 350),
    4: ("catalunya", 2.5, 400, 300),
    5: ("monaco", 2, 300, 300),
    6: ("montreal", 3, 300, 100),
    7: ("silverstone", 3.5, 400, 250),
    8: ("hockenheim", 2, 300, 300),
    9: ("hungaroring", 2.5, 400, 300),
    10: ("spa", 3.5, 500, 350),
    11: ("monza", 4, 400, 300),
    12: ("singapore", 2, 400, 300),
    13: ("suzuka", 2.5, 500, 300),
    14: ("abu_dhabi", 2, 500, 250),
    15: ("texas", 2, 400, 50),
    16: ("brazil", 2, 600, 250),
    17: ("austria", 2, 300, 300),
    18: ("sochi", 2, 300, 300),
    19: ("mexico", 2.5, 500, 500),
    20: ("baku", 3, 400,400),
    21: ("sakhir_short", 2, 300, 300),
    22: ("silverstone_short", 2, 300, 300),
    23: ("texas_short", 2, 300, 300),
    24: ("suzuka_short", 2, 300, 300),
    25: ("hanoi", 2, 300, 300),
    26: ("zandvoort", 2, 500, 300),
    27: ("imola", 2, 500, 300),
    28: ("portimao", 2, 300, 300),
    29: ("jeddah", 4,500, 350),
    30:("Miami", 2,400,300),
    31:("Las Vegas", 4,400, 300),
    32:("Losail", 2.5,400,300),
    39: ("silverstone", 3.5, 400, 250),
    40: ("austria", 2, 300, 300),
    41: ("zandvoort", 2, 500, 300),
}

teams_color_dictionary = {
    -1: QColor("#FFFFFF"),
    0: QColor("#00C7CD"),
    1: QColor("#FF0000"),
    2: QColor("#0000FF"),
    3: QColor("#5097FF"),
    4: QColor("#00902A"),
    5: QColor("#009BFF"),
    6: QColor("#00446F"),
    7: QColor("#95ACBB"),
    8: QColor("#FFAE00"),
    9: QColor("#980404"),
    41:QColor("#000000"),
    104: QColor("#670498"),
    255: QColor("#670498")
}

teams_name_dictionary = {
    -1: "Unknown",
    0: "Mercedes",
    1: "Ferrari",
    2: "Red Bull",
    3: "Williams",
    4: "Aston Martin",
    5: "Alpine",
    6: "Alpha Tauri",
    7: "Haas",
    8: "McLaren",
    9: "Alfa Romeo",
    41:"Multi"
}

weather_dictionary = {
    0: "☀️ Clear",
    1: "🌥️ Light Cloud",
    2: "☁️ Overcast",
    3: "🌦️ Light Rain",
    4: "🌧️ Heavy Rain",
    5: "⛈️ Storm"
}

fuel_dict = {
    0: "Lean",
    1: "Standard",
    2: "Rich",
    3: "Max"
}

pit_dictionary = {
    0: "",
    1: "PIT",
    2: "PIT"
}

ERS_dictionary = {
    0: "NONE",
    1: "MEDIUM",
    2: "HOTLAP",
    3: "OVERTAKE",
    -1: "PRIVATE"
}

session_dictionary = {
    5: "Q1",
    6: "Q2",
    7: "Q3",
    8: "Short Qualifying",
    9: "One-Shot Qualifying",
    10: "Sprint Shootout 1",
    11: "Sprint Shootout 2",
    12: "Sprint Shootout 3",
    13: "Short Sprint Shootout",
    14: "One-Shot Sprint Shootout",
    15: "Race",
    18: "Time Trial"

}

color_flag_dict = {
    0: white, 1: green, 2: blue, 3: yellow, 4: red
}

DRS_dict = {0: "", 1: "DRS"}

WeatherForecastAccuracy = {
    -1: "Unknown",
    0: "Perfect",
    1: "Approximative"
}

packetDictionnary = {
    0:"PacketMotionData",
    1:"PacketSessionData",
    2:"PacketLapData",
    3:"PacketEventData",
    4:"PacketParticipantsData",
    5:"PacketCarSetupData",
    6:"PacketCarTelemetryData",
    7:"PacketCarStatusData",
    8:"PacketFinalClassificationData",
    9:"PacketLobbyInfoData",
    10:"PacketCarDamageData",
    11:"PacketSessionHistoryData",
    12:"PacketTyreSetsData",
    13:"PacketMotionExData",
    14:"PacketTimeTrialData",
    15:"PacketLapPositionsData"

}

safetyCarStatusDict = {
    0:"",
    1:"SC",
    2:"VSC",
    3:"FL",
    4:""
}

retirements_dictionnary = {
    0 : "",
    1 : "Manual Retirement",
    2 : "Finished !",
    3 : "Terminal Damage",
    4 : "Inactivity",
    5 : "Not enough laps completed",
    6 : "Disqualified",
    7 : "Red flagged",
    8 : "Mechanical failure",
    9 : "Session skipped",
    10 : "Session simulated"
}

drs_disabled_reasons = {
    0 : "Wet track",
    1 : "Safety Car Deployed",
    2 : "Red flag",
    3 : "Minimun lap not reached"
}



