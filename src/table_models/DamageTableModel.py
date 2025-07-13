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
from src.table_models.utils import MultiTextDelegate


class DamageTableModel(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__()
        self._data = [player.damage_tab() for player in PLAYERS_LIST if player.position != 0]
        self._header = ["Pos", "Driver", "Tyres", "Wear/\nLap", "Tyres\nWear",
                         "Tyres\nBlister", "Front Wing\nDamage",
                  "Rear Wing\nDamage", "Floor\nDamage", "Diffuser\nDamage", "Sidepod\nDamage"]
        self.header_dictionnary = {self._header[i]:i for i in range(len(self._header))}
        self.sorted_players_list : list[Player] = sorted(PLAYERS_LIST)
        self.column_sizes = [4, 15, 8, 6, 15, 15, 12, 12, 10, 10, 10]

        self.create_table(parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def updateCell(self, row, column, value):
        self._data[row][column] = value
        index = self.index(row, column)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.ForegroundRole:
            if index.column() in [0, 1]:
                return QColor(teams_color_dictionary[self.sorted_players_list[index.row()].teamId])
            if index.column() == 2:  # Tyres column : they have their own color
                return QColor(tyres_color_dictionnary[self._data[index.row()][index.column()]])
            elif self._header[index.column()] == "DRS":
                if self._data[index.row()][index.column()] == "DRS_a":
                    self._data[index.row()][index.column()] = "DRS"
                    return orange
                elif self._data[index.row()][index.column()] == "DRS":
                    return green
                else:
                    return white
            elif self._header[index.column()] == "PIT":
                return white
            else:
                return white

        if role == Qt.FontRole:
            font = QFont("Segoe UI Emoji", 12)
            if index.column() == 2:  # ← cellule spécifique
                font.setBold(True)
            return font
        if role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignRight | Qt.AlignVCenter
            elif any(column in self._header[index.column()] for column in ["Temperatures", "Tyres"]):
                return Qt.AlignCenter

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.sort_data()
            self.layoutChanged.emit()
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEnabled

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]
        if role == Qt.FontRole:
            font = QFont()
            font.setBold(True)
            return font

    def create_table(self, parent):
        """
        Create the QTableView object for this QAbstractTableModel
        """
        tab = QWidget(parent)
        layout = QVBoxLayout()
        table = QTableView()
        table.setWordWrap(True)

        for i in range(len(self._header)):
            if self._header[i] in ["Tyres\nBlister", "Tyres\nWear"]:
                table.setItemDelegateForColumn(i, MultiTextDelegate(table))

        table.setModel(self)
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)

        parent.tabs.addTab(tab, "Damage")

        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        width = table.viewport().width()
        for i in range(len(self._header)):
            table.setColumnWidth(i, int(width / 100 * self.column_sizes[i]))

    def update_data(self):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.sorted_players_list : list[Player] = sorted(PLAYERS_LIST)
        self._data = [player.damage_tab() for player in self.sorted_players_list if player.position != 0]
        self.layoutChanged.emit()
