"""
 This file contains the table structure for the 'Weather Forecast' Tab
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableView, QAbstractItemView

from src.packet_processing.dictionnaries import WeatherForecastAccuracy
from src.packet_processing.variables import session


class WeatherForecastTableModel(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__()
        self._data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        self._header = ["Session", "Time\nOffset", "Rain %", "Weather", "Air\nTemperature", "Track\nTemperature"]

        self.label_weather_accuracy = QLabel(
            f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")
        self.label_weather_accuracy.setFont(QFont("Segoe UI Emoji", 12))

        self.create_weather_tab(parent)

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

    def create_weather_tab(self, parent):
        tab = QWidget(parent)
        layout = QVBoxLayout()

        table = QTableView()
        table.setWordWrap(True)

        table.setModel(self)
        table.verticalHeader().setVisible(False)
        layout.addWidget(self.label_weather_accuracy)
        layout.addWidget(table)
        tab.setLayout(layout)
        parent.tabs.addTab(tab, "Weather Forecast")

        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def update_data(self):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.label_weather_accuracy.setText(f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")
        self._data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        self.layoutChanged.emit()

