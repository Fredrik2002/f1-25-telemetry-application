from PySide6.QtCore import QRectF
from PySide6.QtGui import QPen

from src.packet_processing.dictionnaries import *
import src


class Player:
    def __init__(self):
        self.position: int = 1
        self.tyre_wear = ["0.00", "0.00", "0.00", "0.00"]
        self.tyre_blisters = [0,0,0,0]
        self.tyres = 0
        self.warnings = 0
        self.ERS_mode = -1
        self.ERS_pourcentage = 0
        self.fuelRemainingLaps = 0
        self.fuelMix = 0
        self.raceNumber = 0
        self.teamId = -1
        self.pit: int = 0
        self.frontLeftWingDamage = 0
        self.frontRightWingDamage = 0
        self.tyres_temp_inner = [0, 0, 0, 0]
        self.tyres_temp_surface = [0, 0, 0, 0]
        self.tyresAgeLaps = 0
        self.lastLapTime: float = 0
        self.currentSectors = [0] * 3
        self.lastLapSectors = [0] * 3
        self.bestLapSectors = [0] * 3
        self.worldPositionX = 0
        self.worldPositionZ = 0
        self.penalties = 0
        self.driverStatus = 0
        self.fastestLapTime = 0
        self.drs: int = 0
        self.DRS_allowed : int = 0
        self.DRS_activation_distance : int = 0
        self.yourTelemetry: int = 0
        self.speed: int = 0
        self.rearWingDamage = 0
        self.floorDamage = 0
        self.diffuserDamage = 0
        self.sidepodDamage = 0
        self.name = " "
        self.S200_reached = True
        self.currentLapTime = 0
        self.setup_array = []
        self.oval : QRectF = None
        self.qpen : QPen = None
        self.Xmove = 0
        self.Zmove = 0
        self.etiquette = ""
        self.aiControlled = -1
        self.hasRetired = False
        self.speed_trap = 0
        self.gap_to_leader = 0
        self.currentLapInvalid = 1
        self.resultStatus = 0
        self.networkId = 0
        self.lapDistance = 0

    def __str__(self):
        return self.name + str(self.position)

    def __lt__(self, other):  # For sorting players by positions
        if self.position == 0:  # We want this player at the bottom of our table (not displayed)
            return False
        try:
            return self.position < other.position
        except AttributeError:
            raise AttributeError("Cannot compare Player with a non-Player object")

    def reset(self):
        self.S200_reached = False
        self.warnings = 0
        self.lastLapSectors = [0] * 3
        self.bestLapSectors = [0] * 3
        self.lastLapTime = 0
        self.currentSectors = [0] * 3
        self.fastestLapTime = 0


    def show_tyres_list_damage(self, tyres_list):
        return [(str(tyres_list[i]), src.packet_processing.variables.interpolate_color_damage(tyres_list[i])) for i in
                [2, 3, 0, 1]]

    def get_average_tyre_wear(self):
        max_wear = max(self.tyre_wear, key=float)
        trackPourcentage = self.lapDistance / src.packet_processing.variables.session.trackLength
        return str(round(float(max_wear) / (self.tyresAgeLaps+trackPourcentage+0.001), 2)) + "%"


    def show_tyres_list(self, tyres_list):
        return f"{tyres_list[2]} {tyres_list[3]} \n{tyres_list[0]} {tyres_list[1]}"

    def show_front_wing_damage(self):
        return f"{self.frontLeftWingDamage}-{self.frontRightWingDamage}"

    def show_fuel(self):
        if src.packet_processing.variables.session.Session in [15, 16, 17]:
            if self.fuelRemainingLaps > 0:
                return "+" + '%.2f'% self.fuelRemainingLaps + " Laps"
        return '%.2f'% self.fuelRemainingLaps + " Laps"

    def show_drs(self):
        if self.DRS_allowed or self.drs:
            return "DRS"
        elif self.DRS_activation_distance > 0:
            return str(self.DRS_activation_distance) + "m"
        else:
            return ""

    def main_tab(self):
        return [self.position, self.name, tyres_dictionnary[self.tyres], self.tyresAgeLaps,
                self.gap_to_leader, str(self.ERS_pourcentage) + '%', ERS_dictionary[self.ERS_mode], self.warnings,
                self.raceNumber, self.show_drs(), pit_dictionary[self.pit]]

    def damage_tab(self):
        return [self.position, self.name, tyres_dictionnary[self.tyres], self.tyresAgeLaps,
                self.get_average_tyre_wear(), self.show_tyres_list_damage(self.tyre_wear),
                self.show_tyres_list_damage(self.tyre_blisters), self.show_front_wing_damage(),
                self.rearWingDamage, self.floorDamage, self.diffuserDamage, self.sidepodDamage]

    def lap_tab(self):
        return [self.position, self.name, tyres_dictionnary[self.tyres],
                f"{src.packet_processing.variables.format_milliseconds(self.currentLapTime)} [{', '.join('%.3f' % truc for truc in self.currentSectors)}]",
                f"{src.packet_processing.variables.format_milliseconds(self.lastLapTime)} [{', '.join('%.3f' % truc for truc in self.lastLapSectors)}]",
                f"{src.packet_processing.variables.format_milliseconds(self.fastestLapTime)} [{', '.join('%.3f' % truc for truc in self.bestLapSectors)}]",
                ]

    def temperature_tab(self):
        return [self.position, self.name, tyres_dictionnary[self.tyres],
                self.show_tyres_list(self.tyres_temp_surface), self.show_tyres_list(self.tyres_temp_inner)]

    def ers_and_fuel_tab(self):
        return [self.position, self.name, tyres_dictionnary[self.tyres], str(self.ERS_pourcentage) + '%',
                ERS_dictionary[self.ERS_mode], self.show_fuel(), fuel_dict[self.fuelMix]]


    def is_not_on_lap(self):
        return self.currentLapTime == 0 or (self.yourTelemetry==1 and self.ERS_mode == 0) or \
               (self.currentSectors[0] + 1 > self.bestLapSectors[0] != 0) or \
               (self.currentSectors[1] + 1 > self.bestLapSectors[1] != 0)

    def gestion_qualif(self, MnT_team):
        if MnT_team is None:
            return "black"
        else:
            if self.teamId == MnT_team:
                return "blue"
            else:
                return "green" if self.is_not_on_lap() else "red"


