import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../src")

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, pyqtSignal

from src.dictionnaries import tyres_color_dictionnary
from src.parsers import parser2025
from src.parsers.parser2025 import PacketHeader, Packet
from src.variables import *
from src.packet_management import *


# Thread qui lit un socket
class SocketThread(QThread):
    data_received = pyqtSignal(PacketHeader, Packet)

    def __init__(self):
        super().__init__()
        self.running = True
        self.listener = parser2025.Listener(port=PORT[0],
                        redirect=dictionnary_settings["redirect_active"],
                        adress=dictionnary_settings["ip_adress"],
                        redirect_port=int(dictionnary_settings["redirect_port"]))

    def run(self):
        while self.running:
            a = self.listener.get()
            if a is not None:
                self.data_received.emit(*a)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

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
            else:
                return QColor(teams_color_dictionary[self.sorted_players_list[index.row()].teamId])
        if role == Qt.FontRole:
            font = QFont()
            if index.column() == 2:  # ← cellule spécifique
                font.setBold(True)
            return font

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


class MainWindow(QMainWindow):
    function_hashmap = {  # PacketId : (fonction, arguments)
        0: (nothing, ()),  # PacketMotion
        1: (nothing, ()),  # PacketSession
        2: (update_lap_data, ()),  # PacketLapData
        3: (warnings, ()),  # PacketEvent
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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TableView with Auto Sort")
        self.resize(1080, 720)

        self.socketThread = SocketThread()
        self.socketThread.data_received.connect(self.update_table)
        self.socketThread.start()

        self.main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.create_title()
        self.main_layout.addWidget(self.tabs)
        self.models : dict[str, MyTableModel] = {}

        self.create_tab(["Position", "Driver", "Tyres", "Tyres Age", "Gap (Leader)",
                         "ERS %", "ERS Mode", "Warnings", "Race Number"], "Main")
        self.create_tab(["Position", "Driver", "Tyres", "Tyres Wear", "Tyres Blister", "Front Wing Damage",
                  "Rear Wing Damage", "Floor Damage", "Diffuser Damage", "Sidepod Damage", ""], "Damage")
        self.create_tab(["Position", "Driver", "Tyres", "Current Lap", "Last Lap", "Fastest Lap"], "Laps")


        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def create_title(self):
        h_layout = QHBoxLayout()
        self.title_label = QLabel()

        h_layout.addWidget(self.title_label)
        self.main_layout.addLayout(h_layout)

    def update_table(self, header, packet):
        func, args = MainWindow.function_hashmap[header.m_packet_id]
        func(packet, *args)
        active_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        SORTED_PLAYERS_LIST = sorted(PLAYERS_LIST)
        self.models[active_tab_name].update_data(SORTED_PLAYERS_LIST, active_tab_name)

    def create_tab(self, header, name):
        data = [player.tab_list(name) for player in PLAYERS_LIST if player.position != 0]

        tab = QWidget(self)
        layout = QVBoxLayout()
        table = QTableView()
        self.models[name] = MyTableModel(data=data,
                              header=header)

        table.setModel(self.models[name])
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #f0f0f0;
    }
    QTabWidget::pane {
        border: 1px solid #444;
    }
    QHeaderView::section {
        background-color: #3c3c3c;
        color: white;
        padding: 4px;
        border: 1px solid #444;
    }
    QTableView {
        gridline-color: #555;
        selection-background-color: #555;
        selection-color: white;
    }
    QTabWidget::pane {
    border: 1px solid #444;
    background-color: #222;
    }
    
    QTabBar::tab {
        background: #333;
        color: white;
        padding: 6px;
        border: 1px solid #555;
        border-bottom: none;
    }
    
    QTabBar::tab:selected {
        background: #222;
        color: white;
        font-weight: bold;
    }
    
    QTabBar::tab:hover {
        background: #444;
    }
    """

    app.setStyleSheet(dark_stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())