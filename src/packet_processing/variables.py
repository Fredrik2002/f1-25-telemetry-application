
import datetime

from PySide6.QtGui import QColor

import src.packet_processing.Session as Session
import src.packet_processing.Player as Player
import json
import sys
from pathlib import Path

current_file = Path(__file__).resolve().parent

settings_path = current_file.parent.parent / "settings.txt"
tracks_folder = current_file.parent.parent /  "tracks"

def format_minutes(millis):
    texte = str(datetime.timedelta(seconds=millis))
    liste = texte.split(":")
    return f"{liste[1]} min {liste[2]}s"


def format_milliseconds(ms):
    ms = int(ms)
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    if minutes > 0:
        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"
    else:
        return f"{seconds:02d}.{milliseconds:03d}"

def interpolate_color_damage(percent):
    start_color = (0, 200, 0) # 0% -> Green
    middle_color = (207, 163, 0) # 50% -> Yellow
    end_color = (255, 0, 0) # 100% -> Red

    return QColor(*interpolate_color(percent, start_color, end_color, middle_color))


def interpolate_color(percent, color_start=(0, 200, 0), color_end=(255, 0, 0), color_middle=(207,163,0)):
    percent = float(percent) / 100
    if percent < 0.5:
        r = int(color_start[0] + (color_middle[0] - color_start[0]) * 2*percent)
        g = int(color_start[1] + (color_middle[1] - color_start[1]) * 2*percent)
        b = int(color_start[2] + (color_middle[2] - color_start[2]) * 2*percent)
    else:
        r = int(color_middle[0] + (color_end[0] - color_middle[0]) * 2*(percent-0.5))
        g = int(color_middle[1] + (color_end[1] - color_middle[1]) * 2*(percent-0.5))
        b = int(color_middle[2] + (color_end[2] - color_middle[2]) * 2*(percent-0.5))

    return (r, g, b)


with open(settings_path, "r") as f:
    dictionnary_settings = json.load(f)

if len(sys.argv)==2:
    dictionnary_settings["port"] = int(sys.argv[1])



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
    "Main": [8, 15, 8, 8, 10, 5, 10, 10, 10, 5, 5],
    "Damage": [8, 15, 8, 15, 15, 12, 12, 10, 10, 10],
    "Laps": [8, 15, 8, 25, 25, 25],
    "Temperatures": [8, 15, 8, 12, 12],
    "ERS && Fuel": [8, 15, 8, 8, 10, 10, 10],
    "Weather Forecast": [15, 8, 10, 12, 12, 12],
    "Packet Reception" : [15, 10]
}