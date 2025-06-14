import math

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPen

from src.dictionnaries import *
from src.utils import conversion


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

    def __str__(self):
        return self.name + str(self.position)

    def __lt__(self, other):  # For sorting players by positions
        if self.position == 0:  # We want this player at the bottom of our table (not displayed)
            return False
        try:
            return self.position < other.position
        except AttributeError:
            raise AttributeError("Cannot compare Player with a non-Player object")

    def show_tyres_list(self, tyres_list):
        return f"{tyres_list[2]} {tyres_list[3]} \n{tyres_list[0]} {tyres_list[1]}"

    def show_front_wing_damage(self):
        return f"{self.frontLeftWingDamage}-{self.frontRightWingDamage}"

    def tab_list(self, name):
        if name == "Main":
            return [self.position, self.name, tyres_dictionnary[self.tyres], self.tyresAgeLaps,
                    self.gap_to_leader, str(self.ERS_pourcentage)+'%', ERS_dictionary[self.ERS_mode], self.warnings,
                    self.raceNumber, pit_dictionary[self.pit]]
        elif name == "Damage":
            return [self.position, self.name, tyres_dictionnary[self.tyres], self.show_tyres_list(self.tyre_wear),
                    self.show_tyres_list(self.tyre_blisters), self.show_front_wing_damage(),
             self.rearWingDamage, self.floorDamage, self.diffuserDamage, self.sidepodDamage]
        elif name == "Laps":
            return [self.position, self.name, tyres_dictionnary[self.tyres],
                    f"{conversion(self.currentLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.currentSectors)}]",
                    f"{conversion(self.lastLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.lastLapSectors)}]",
                    f"{conversion(self.fastestLapTime, 2)} [{', '.join('%.3f' % truc for truc in self.bestLapSectors)}]",
                    ]
        elif name == "Temperatures":
            return [self.position, self.name, tyres_dictionnary[self.tyres],
            self.show_tyres_list(self.tyres_temp_surface), self.show_tyres_list(self.tyres_temp_inner)]
        else:
            raise ValueError(f"Unrecognized Tab Name : {name}")

    def printing(self, buttonId, liste_joueurs, session):
        if buttonId == 0:  # Menu principal
            if session in [5, 6, 7, 8, 9, 13]: # Qualif
                return (
                    f"P{self.position}, {self.name} Lap :{conversion(self.currentLapTime, 2)} {ERS_dictionary[self.ERS_mode]},"
                    f" num = {self.raceNumber} Last lap : {conversion(self.lastLapTime, 2)}"
                    f" Fastest lap : {conversion(self.fastestLapTime, 2)} {pit_dictionary[self.pit]}")
            else: #Course
                return f"P{self.position}, {self.name} {self.tyresAgeLaps} tours " \
                       f"Gap :{'%.3f'%(self.gap_to_leader / 1000)} {self.ERS_pourcentage}% {ERS_dictionary[self.ERS_mode]} " \
                       f"Warnings = {self.warnings} num = {self.raceNumber} {pit_dictionary[self.pit]} {DRS_dict[self.drs]} "

        elif buttonId == 1:  # Dégâts
            return (f"P{self.position}, {self.name} "
                    f"usure = {self.tyre_wear}, blisters = {self.tyre_blisters}, FW = [{self.frontLeftWingDamage},  "
                    f"{self.frontRightWingDamage}] | "
                    f"RW ={self.rearWingDamage} | "
                    f"floor = {self.floorDamage} | "
                    f"diffuser = {self.diffuserDamage} | "
                    f"sidepod = {self.sidepodDamage} | "
                    f"{pit_dictionary[self.pit]}")

        elif buttonId == 2:  # Températures
            return (
                f"P{self.position}  {self.name},  RL : {self.tyres_temp_surface[0]}|{self.tyres_temp_inner[0]}, "
                f"RR :{self.tyres_temp_surface[1]}|{self.tyres_temp_inner[1]} "
                f"FL : {self.tyres_temp_surface[2]}|{self.tyres_temp_inner[2]}, "
                f"FR : {self.tyres_temp_surface[3]}|{self.tyres_temp_inner[3]}, {pit_dictionary[self.pit]} ")

        elif buttonId == 3:  # Laps
            return f"P{self.position}, {self.name} "+ \
            f"Current lap : {conversion(self.currentLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.currentSectors)}] " + \
            f"Last lap : {conversion(self.lastLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.lastLapSectors)}]  " + \
            f"Fastest lap : {conversion(self.fastestLapTime, 2)} [{', '.join('%.3f' % truc for truc in self.bestLapSectors)}] "  + \
            f"{pit_dictionary[self.pit]}"

        elif buttonId == 4:
            return f"P{self.position}, {self.name} ERS = {self.ERS_pourcentage}% | {ERS_dictionary[self.ERS_mode]}  " \
                   f"Fuel = {round(self.fuelRemainingLaps, 2)} tours | {self.penalties}s | {self.speed_trap}km/h"

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


