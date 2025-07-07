from PySide6.QtCore import QSize, QAbstractTableModel
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel, QAbstractItemView,
    QTabBar
)

from src.packet_processing.packet_management import *
from src.windows.Canvas import Canvas
from src.windows.SocketThread import SocketThread
from src.windows.myTableModel import MyTableModel, MyTableModelWeatherForecast, MyTableModelPacketReception, \
    MultiTextDelegate
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
        self.race_direction_list = None

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged)
        self.tabs.setTabBar(FixedSizeTabBar())
        self.create_title()

        self.main_layout.addWidget(self.tabs)
        self.models : dict[str, QAbstractTableModel] = {}
        self.tables : dict[str, QTableView] = {}

        self.packet_reception_dict = {i: 0 for i in range(16)}
        self.last_update = 0

        self.create_tab(["Position", "Driver", "Tyres", "Tyres\nAge", "Gap\n(Leader)",
                         "ERS", "ERS Mode", "Warnings", "Race\nNumber", "DRS", "PIT"], "Main")
        self.create_tab(["Position", "Driver", "Tyres", "Average\nTyre Wear/Lap", "Tyres\nWear",
                         "Tyres\nBlister", "Front Wing\nDamage",
                  "Rear Wing\nDamage", "Floor\nDamage", "Diffuser\nDamage", "Sidepod\nDamage"], "Damage")
        self.create_tab(["Position", "Driver", "Tyres", "Current Lap", "Last Lap", "Fastest Lap"], "Laps")
        self.create_tab(["Position", "Driver", "Tyres", "Tyres Surface\nTemperatures",
                         "Tyres Inner\nTemperatures"], "Temperatures")
        self.create_tab(["Position", "Driver", "Tyres", "ERS", "ERS Mode", "Fuel", "Fuel Mix"],
                        "ERS && Fuel")
        self.create_map_tab()
        self.create_weather_tab()
        self.create_packet_reception_tab()
        self.create_race_direction_tab()

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        self.setup_table_columns()

        MainWindow.function_hashmap = {  # PacketId : (fonction, arguments)
            0: (update_motion, ()),  # PacketMotion
            1: (update_session, ()),  # PacketSession
            2: (update_lap_data, ()),  # PacketLapData
            3: (update_event, [self.race_direction_list]),  # PacketEvent
            4: (update_participants, ()),  # PacketParticipants
            5: (update_car_setups, ()),  # PacketCarSetup
            6: (update_car_telemetry, ()),  # PacketCarTelemetry
            7: (update_car_status, ()),  # PacketCarStatus
            8: (nothing, ()),  # PacketFinalClassification
            9: (nothing, ()),  # PacketLobbyInfo
            10: (update_car_damage, ()),  # PacketCarDamage
            11: (nothing, ()),  # PacketSessionHistory
            12: (nothing, ()),
            13: (nothing, ()),
            14: (nothing, ()),
            15: (nothing, ())
        }

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
        func, args = MainWindow.function_hashmap[header.m_packet_id]
        func(packet, *args)
        active_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        sorted_players_list = sorted(PLAYERS_LIST)
        if active_tab_name not in ["Packet Reception", "Race Direction"]:
            self.models[active_tab_name].update_data(sorted_players_list, active_tab_name)

        if header.m_packet_id == 1:
            self.title_label.setText(session.title_display())
            self.label_weather_accuracy.setText(f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")

        self.packet_reception_dict[header.m_packet_id] += 1
        if time.time() > self.last_update + 1:
            data = [
                [packetDictionnary[i], str(self.packet_reception_dict[i]) + "/s"]
                for i in range(len(packetDictionnary))
            ]
            self.models["Packet Reception"].update_data(data)
            self.packet_reception_dict = {i: 0 for i in range(16)}
            self.last_update = time.time()


    def create_tab(self, header, name):
        data = [player.tab_list(name) for player in PLAYERS_LIST if player.position != 0]

        tab = QWidget(self)
        layout = QVBoxLayout()
        table = QTableView()
        table.setWordWrap(True)
        self.tables[name] = table
        self.models[name] = MyTableModel(data=data,
                              header=header)

        for i in range(len(header)):
            if header[i] in ["Tyres\nBlister", "Tyres\nWear"]:
                table.setItemDelegateForColumn(i, MultiTextDelegate(table))

        table.setModel(self.models[name])
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, name)
        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def create_map_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.map_canvas = Canvas()
        self.models["Map"] = self.map_canvas
        layout.addWidget(self.map_canvas)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Map")

    def create_weather_tab(self):
        tab = QWidget(self)
        layout = QVBoxLayout()
        self.label_weather_accuracy = QLabel(f"Weather accuracy : {WeatherForecastAccuracy[session.weatherForecastAccuracy]}")
        self.label_weather_accuracy.setFont(QFont("Segoe UI Emoji", 12))
        table = QTableView()
        table.setWordWrap(True)
        self.tables["Weather Forecast"] = table
        self.models["Weather Forecast"] = MyTableModelWeatherForecast()

        table.setModel(self.models["Weather Forecast"])
        table.verticalHeader().setVisible(False)
        layout.addWidget(self.label_weather_accuracy)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Weather Forecast")
        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

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
        self.models[name] = MyTableModelPacketReception(data)

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



