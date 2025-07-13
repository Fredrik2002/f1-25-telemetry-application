"""
 This file contains the main table structure for most of the tabs :
    - Main
    - Damage
    - Temperatures
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView

from src.packet_processing.Player import Player
from src.packet_processing.packet_management import *
from src.packet_processing.variables import PLAYERS_LIST
from src.table_models.GeneralTableModel import GeneralTableModel
from src.table_models.utils import MultiTextDelegate


class MainTableModel(GeneralTableModel):
    def __init__(self):
        data = [player.main_tab() for player in PLAYERS_LIST if player.position != 0]
        header = ["Pos", "Driver", "", "Tyres\nAge", "Gap\n(Leader)",
                         "ERS", "ERS Mode", "Warnings", "Race\nNum", "DRS", "PIT"]
        column_sizes = [5, 20, 1, 6, 10, 8, 10, 10, 7, 7, 7]

        super().__init__(header, data, column_sizes)

        self.sorted_players_list : list[Player] = sorted(PLAYERS_LIST)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.ForegroundRole:
            if index.column() in [0, 1]:
                return QColor(teams_color_dictionary[self.sorted_players_list[index.row()].teamId])
            elif index.column() == 2:  # Tyres column : they have their own color
                return QColor(tyres_color_dictionnary[self._data[index.row()][index.column()]])
            elif index.column() == 9:
                if self._data[index.row()][index.column()] == "DRS_a":
                    self._data[index.row()][index.column()] = "DRS"
                    return orange
                elif self._data[index.row()][index.column()] == "DRS":
                    return green

        if role == Qt.FontRole:
            font = QFont("Segoe UI Emoji", 12)
            if index.column() == 2:
                font.setBold(True)
            return font
        if role == Qt.TextAlignmentRole:
            if index.column() == 0: # Position
                return Qt.AlignRight | Qt.AlignVCenter
            elif index.column() in {2, 3, 5, 10}: # Tyres
                return Qt.AlignHCenter | Qt.AlignVCenter


    def update(self):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.sorted_players_list : list[Player] = sorted(PLAYERS_LIST)
        self._data = [player.main_tab() for player in self.sorted_players_list if player.position != 0]
        self.layoutChanged.emit()
