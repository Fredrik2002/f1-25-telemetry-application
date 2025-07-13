from PySide6.QtCore import QSize, QAbstractTableModel
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel, QAbstractItemView,
    QTabBar, QStackedWidget, QSizePolicy
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

        self.index = 0

        self.menu = QListWidget()
        self.menu.addItems(["Main", "Damage", "Laps", "Temperatures", "Map", "ERS & Fuel",
                            "Weather Forecast", "Packet Reception", "Race Director"])
        self.menu.setCurrentRow(self.index)

        self.mainModel = MainTableModel()
        self.damageModel = DamageTableModel()
        self.lapModel = LapTableModel()
        self.temperatureModel = TemperatureTableModel()
        self.mapCanvas = Canvas()
        self.ersAndFuelModel = ERSAndFuelTableModel()
        self.weatherForecastModel = WeatherForecastTableModel()
        self.packetReceptionTableModel = PacketReceptionTableModel(self)
        self.raceDirectorModel = RaceDirection()

        self.models = [
            self.mainModel,
            self.damageModel,
            self.lapModel,
            self.temperatureModel,
            self.mapCanvas,
            self.ersAndFuelModel,
            self.weatherForecastModel,
            self.packetReceptionTableModel,
            self.raceDirectorModel
        ]

        self.stack = QStackedWidget()
        self.menu.currentRowChanged.connect(self.on_row_changed)

        self.title_label = QLabel()

        self.create_layout()

        self.packet_reception_dict = [0 for _ in range(16)]
        self.last_update = 0

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)


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

    def closeEvent(self, event):
        self.socketThread.stop()
        self.close()

    def create_layout(self):
        self.title_label.setFont(QFont("Segoe UI Emoji", 12))

        self.menu.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.menu.setMaximumWidth(150)
        self.menu.setFont(QFont("Segoe UI Emoji", 12))

        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()

        self.stack.addWidget(self.mainModel.table)
        self.stack.addWidget(self.damageModel.table)
        self.stack.addWidget(self.lapModel.table)
        self.stack.addWidget(self.temperatureModel.table)
        self.stack.addWidget(self.mapCanvas)
        self.stack.addWidget(self.ersAndFuelModel.table)
        self.stack.addWidget(self.weatherForecastModel.table)
        self.stack.addWidget(self.packetReceptionTableModel.table)
        self.stack.addWidget(self.raceDirectorModel)

        h_layout1.addWidget(self.title_label)
        h_layout2.addWidget(self.menu)
        h_layout2.addWidget(self.stack)

        self.main_layout.addLayout(h_layout1)
        self.main_layout.addLayout(h_layout2)

    def update_table(self, header, packet):
        MainWindow.function_hashmap[header.m_packet_id](packet)

        self.models[self.index].update()

        if header.m_packet_id == 1:
            self.title_label.setText(session.title_display())

        self.packet_reception_dict[header.m_packet_id] += 1
        if time.time() > self.last_update + 1:
            self.packetReceptionTableModel.update_each_second()
            self.packet_reception_dict = [0 for _ in range(16)]
            self.last_update = time.time()

    def on_row_changed(self, index):
        self.stack.setCurrentIndex(index)
        self.index = index

    def resizeEvent(self, event):
        src.packet_processing.variables.REDRAW_MAP = True
        super().resizeEvent(event)
        self.models[self.index].update()




