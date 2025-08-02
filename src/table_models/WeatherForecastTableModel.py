"""
 This file contains the table structure for the 'Weather Forecast' Tab
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableView, QAbstractItemView

from src.packet_processing.dictionnaries import WeatherForecastAccuracy
from src.packet_processing.variables import session
from src.table_models.GeneralTableModel import GeneralTableModel


class WeatherForecastTableModel(GeneralTableModel):
    def __init__(self):
        data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        header = ["Session", "Time\nOffset", "Rain %", "Weather", "Air\nTemperature", "Track\nTemperature"]
        column_sizes = [20, 10, 8, 8, 8, 8]
        super().__init__(header, data, column_sizes)

        self.label_weather_accuracy = QLabel(
            f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")

        self.layout = QVBoxLayout()

        self.create_layout()

    def create_layout(self):
        self.label_weather_accuracy.setFont(QFont("Segoe UI Emoji", 12))

        table = QTableView()
        table.setWordWrap(True)

        table.setModel(self)
        table.verticalHeader().setVisible(False)

        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.layout.addWidget(self.label_weather_accuracy)
        self.layout.addWidget(table)

    def update(self):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self.label_weather_accuracy.setText(f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")
        self._data = [session.show_weather_sample(i) for i in range(session.nb_weatherForecastSamples)]
        self.layoutChanged.emit()

