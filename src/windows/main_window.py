from PySide6.QtCore import QSize, QAbstractTableModel
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel, QAbstractItemView,
    QTabBar
)

from src.packet_processing.packet_management import *
from src.table_models.DamageTableModel import DamageTableModel
from src.table_models.ERSAndFuelTableMable import ERSAndFuelTableModel
from src.table_models.LapTableModel import LapTableModel

from src.table_models.MainTableModel import MainTableModel
from src.table_models.PacketReceptionTableModel import PacketReceptionTableModel
from src.table_models.TemperatureTableModel import TemperatureTableModel
from src.table_models.WeatherForecastTableModel import WeatherForecastTableModel
from src.table_models.RaceDirection import RaceDirection

from src.table_models.Canvas import Canvas
from src.windows.SocketThread import SocketThread
from src.packet_processing.variables import PLAYERS_LIST, COLUMN_SIZE_DICTIONARY, session
import src


class FixedSizeTabBar(QTabBar):
    def tabSizeHint(self, index):
        default_size = super().tabSizeHint(index)
        custom_widths = {
            0: 90,
            1: 110,
            2: 90,
            3: 180,
            4: 140,
            5: 70,
            6: 220,
            7: 200,
            8: 200
        }
        width = custom_widths.get(index, default_size.width())
        return QSize(width, default_size.height())

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telemetry Application")
        self.resize(1080, 720)

        self.socketThread = SocketThread()
        self.socketThread.data_received.connect(self.update_table)
        self.socketThread.start()

        self.main_layout = QVBoxLayout()
        self.map_canvas = None
        self.weather_table = None
        self.label_weather_accuracy = None


        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged)
        self.tabs.setTabBar(FixedSizeTabBar())
        self.create_title()

        self.main_layout.addWidget(self.tabs)
        self.models : dict[str, QAbstractTableModel] = {}
        self.tables : dict[str, QTableView] = {}

        self.packet_reception_dict = [0 for _ in range(16)]
        self.last_update = 0

        self.mainModel = MainTableModel(self)
        self.damageModel = DamageTableModel(self)
        self.lapModel = LapTableModel(self)
        self.temperatureModel = TemperatureTableModel(self)
        self.mapCanvas = Canvas(self)
        self.ersAndFuelModel = ERSAndFuelTableModel(self)
        self.weatherForecastModel = WeatherForecastTableModel(self)
        self.packetReceptionTableModel = PacketReceptionTableModel(self)
        self.raceDirectorModel = RaceDirection(self)

        MainWindow.function_hashmap = [  # PacketId : (fonction, arguments)
            lambda packet : update_motion(packet),                                   # 0 : PacketMotion
            lambda packet : update_session(packet),                                  # 1 : PacketSession
            lambda packet : update_lap_data(packet),                                 # 2 : PacketLapData
            lambda packet : update_event(packet, self.raceDirectorModel),            # 3 : PacketEvent
            lambda packet : update_participants(packet),                             # 4 : PacketParticipants
            lambda packet : update_car_setups(packet),                               # 5 : PacketCarSetup
            lambda packet : update_car_telemetry(packet),                            # 6 : PacketCarTelemetry
            lambda packet : update_car_status(packet),                               # 7 : PacketCarStatus
            lambda packet : None,                                                    # 8 : PacketFinalClassification
            lambda packet : None,                                                    # 9 : PacketLobbyInfo
            lambda packet : update_car_damage(packet),                               # 10 : PacketCarDamage
            lambda packet : None,                                                    # 11 : PacketSessionHistory
            lambda packet : None,                                                    # 12 : PacketTyreSetsData
            lambda packet : update_motion_extended(packet),                          # 13 : PacketMotionExData
            lambda packet : None,                                                    # 14 : PacketTimeTrialData
            lambda packet : None                                                     # 15 : PacketLapPositions
        ]

        MainWindow.update_data_hashmap = [
            lambda: self.mainModel.update_data(),
            lambda: self.damageModel.update_data(),
            lambda: self.lapModel.update_data(),
            lambda: self.temperatureModel.update_data(),
            lambda: self.mapCanvas.update(),
            lambda: self.ersAndFuelModel.update_data(),
            lambda: self.weatherForecastModel.update_data(),
            lambda: None,
            lambda: self.raceDirectorModel.viewport().update()
        ]

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        return

        self.create_race_direction_tab()

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        self.setup_table_columns()

    def tabChanged(self):
        self.setup_table_columns()

    def setup_table_columns(self):
        for name, table in self.tables.items():
            width = table.viewport().width()
            for i in range(self.models[name].columnCount()):
                table.setColumnWidth(i, int(width/100*COLUMN_SIZE_DICTIONARY[name][i]))

    def create_title(self):
        h_layout = QHBoxLayout()
        self.title_label = QLabel()
        font = QFont()
        font.setWeight(QFont.Weight(18))
        self.title_label.setFont(font)

        h_layout.addWidget(self.title_label)
        self.main_layout.addLayout(h_layout)

    def update_table(self, header, packet):
        MainWindow.function_hashmap[header.m_packet_id](packet)

        index = self.tabs.currentIndex()
        MainWindow.update_data_hashmap[index]()
        return
        if active_tab_name not in ["Packet Reception", "Race Direction"]:
            self.models[active_tab_name].update_data(sorted_players_list, active_tab_name)

        if header.m_packet_id == 1:
            self.title_label.setText(session.title_display())
            self.label_weather_accuracy.setText(f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")

        self.packet_reception_dict[header.m_packet_id] += 1
        if time.time() > self.last_update + 1:
            self.packetReceptionTableModel.update_data(self.packet_reception_dict)
            self.packet_reception_dict = [0 for _ in range(16)]
            self.last_update = time.time()


    def create_map_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.map_canvas = Canvas()
        self.models["Map"] = self.map_canvas
        layout.addWidget(self.map_canvas)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Map")



    def create_packet_reception_tab(self):
        data = [
            [packetDictionnary[i], str(self.packet_reception_dict[i]) + "/s"]
            for i in range(len(packetDictionnary))
        ]
        name = "Packet Reception"
        tab = QWidget(self)
        layout = QVBoxLayout()
        table = QTableView()
        table.setWordWrap(True)
        self.tables[name] = table
        self.models[name] = PacketReceptionTableModel(data)

        table.setModel(self.models[name])
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab,name)
        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def create_race_direction_tab(self):
        tab = QWidget(self)
        layout = QVBoxLayout()
        self.race_direction_list = QListWidget()
        self.race_direction_list.setFont(QFont("Segoe UI Emoji", 12))

        layout.addWidget(self.race_direction_list)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Race Direction")
        self.race_direction_list.setWordWrap(True)
        self.race_direction_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.race_direction_list.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def resizeEvent(self, event):
        self.setup_table_columns()
        src.packet_processing.variables.REDRAW_MAP = True
        super().resizeEvent(event)
        self.map_canvas.update()



