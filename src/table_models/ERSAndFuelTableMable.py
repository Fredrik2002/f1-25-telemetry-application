"""
 This file contains the main table structure for most of the tabs :
    - Main
    - Damage
    - Temperatures
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QAbstractItemView

from src.packet_processing.Player import Player
from src.packet_processing.packet_management import *
from src.packet_processing.variables import PLAYERS_LIST
from src.table_models.GeneralTableModel import GeneralTableModel
from src.table_models.utils import MultiTextDelegate


class ERSAndFuelTableModel(GeneralTableModel):
    def __init__(self):
        data = [player.ers_and_fuel_tab() for player in PLAYERS_LIST if player.position != 0]
        header = ["Pos", "Driver", "", "ERS", "ERS Mode", "Fuel", "Fuel Mix"]
        column_sizes = [4, 20, 1, 8, 15, 10, 10]
        super().__init__(header, data, column_sizes)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.ForegroundRole:
            if index.column() in [0, 1]:
                return teams_color_dictionary[self.sorted_players_list[index.row()].teamId]
            elif index.column() == 2:  # Tyres column : they have their own color
                return tyres_color_dictionnary[self._data[index.row()][index.column()]]

        if role == Qt.FontRole:
            if index.column() == 2:
                return main_font_bolded
            return main_font

        if role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignRight | Qt.AlignVCenter
            elif any(column in self._header[index.column()] for column in ["Temperatures", "Tyres"]):
                return Qt.AlignCenter


    def update(self):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.sorted_players_list: list[Player] = sorted(PLAYERS_LIST)
        self._data = [player.ers_and_fuel_tab() for player in self.sorted_players_list if player.position != 0]
        self.layoutChanged.emit()
