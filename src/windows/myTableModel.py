from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QFont

from src.packet_management import *


class MyTableModel(QAbstractTableModel):
    def __init__(self, data, header):
        super().__init__()
        self._data = data  # liste de listes
        self._header = header
        self.header_dictionnary = {self._header[i]:i for i in range(len(self._header))}
        self.sorted_players_list : list[Player] = sorted(PLAYERS_LIST)

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
                return QColor(teams_color_dictionary[self.sorted_players_list[index.row()].teamId])


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

    def update_data(self, sorted_players_list, active_tab_name):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.sorted_players_list = sorted_players_list
        self._data = [player.tab_list(active_tab_name) for player in sorted_players_list if player.position != 0]
        self.layoutChanged.emit()


class MyTableModelWeatherForecast(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        self._header = ["Session", "Time\nOffset", "Rain %", "Weather", "Air\nTemperature", "Track\nTemperature"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 6

    def updateCell(self, row, column, value):
        self._data[row][column] = value
        index = self.index(row, column)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.FontRole:
            font = QFont("Segoe UI Emoji", 12)
            return font

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

    def update_data(self, a, b):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self._data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        self.layoutChanged.emit()


class MyTableModelPacketReception(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._header = ["Packet Type", "Reception"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def updateCell(self, row, column, value):
        self._data[row][column] = value
        index = self.index(row, column)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.FontRole:
            font = QFont("Segoe UI Emoji", 12)
            return font

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

    def update_data(self, data):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self._data = data
        self.layoutChanged.emit()