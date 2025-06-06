
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
    listener = parser2025.Listener(port=PORT[0],
                        redirect=dictionnary_settings["redirect_active"],
                        adress=dictionnary_settings["ip_adress"],
                        redirect_port=int(dictionnary_settings["redirect_port"]))

    LISTE_JOUEURS: list[Player] = [Player.Player() for _ in range(22)]
    session: Session = Session.Session()
    created_map = False
    WIDTH_POINTS = 6
    LISTE_FRAMES = []
    button_list: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                                  "Packet Reception"]