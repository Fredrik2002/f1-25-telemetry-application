
import src.parsers.parser2025 as parser2025
import src.Session as Session
import src.Player as Player
import json
import sys

with open("../../settings.txt", "r") as f:
    dictionnary_settings = json.load(f)

if len(sys.argv)==2:
    dictionnary_settings["port"] = int(sys.argv[1])


try: # No need to create the variables again
    PORT[0] = int(dictionnary_settings["port"])
except NameError:  # If the variables were not created yet
    PORT = [int(dictionnary_settings["port"])]

    PLAYERS_LIST: list[Player] = [Player.Player() for _ in range(22)]
    session: Session = Session.Session()
    created_map = False
    WIDTH_POINTS = 6
    button_list: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                                  "Packet Reception"]
    POSITION_CHANGED = False
    REDRAW_MAP = True


    COLUMN_SIZE_DICTIONARY = {
        "Main": [8, 15, 8, 8, 10, 5, 10, 10, 10, 5],
        "Damage": [8, 15, 8, 15, 15, 12, 12, 10, 10, 10],
        "Laps": [8, 15, 8, 25, 25, 25],
        "Temperatures": [8, 15, 8, 12, 12],
        "ERS && Fuel": [8, 15, 8, 8, 10, 10, 10],
        "Weather Forecast": [15, 8, 10, 12, 12, 12]
    }