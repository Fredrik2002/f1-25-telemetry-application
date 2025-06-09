import sys

from PyQt5.QtCore import QSize

sys.path.append(".")
sys.path.append("..")
sys.path.append("../src")

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel, QAbstractItemView,
    QTabBar
)

from src.packet_management import *
from src.windows.myTableModel import MyTableModel
from src.windows.SocketThread import SocketThread


class FixedSizeTabBar(QTabBar):
    def tabSizeHint(self, index):
        # Exemple : taille différente selon l'index
        default_size = super().tabSizeHint(index)
        custom_widths = {
            0: 100,
            1: 120,
            2: 100,
            3: 180
        }
        width = custom_widths.get(index, default_size.width())
        return QSize(width, default_size.height())

class MainWindow(QMainWindow):
    function_hashmap = {  # PacketId : (fonction, arguments)
        0: (update_motion, ()),  # PacketMotion
        1: (update_session, ()),  # PacketSession
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
        self.resize(1440, 800)

        self.socketThread = SocketThread()
        self.socketThread.data_received.connect(self.update_table)
        self.socketThread.start()

        self.main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged)
        self.tabs.setTabBar(FixedSizeTabBar())
        self.create_title()

        self.main_layout.addWidget(self.tabs)
        self.models : dict[str, MyTableModel] = {}
        self.tables : dict[str, QTableView] = {}

        self.create_tab(["Position", "Driver", "Tyres", "Tyres\nAge", "Gap\n(Leader)",
                         "ERS", "ERS Mode", "Warnings", "Race\nNumber", "PIT"], "Main")
        self.create_tab(["Position", "Driver", "Tyres", "Tyres\nWear",
                         "Tyres\nBlister", "Front Wing\nDamage",
                  "Rear Wing\nDamage", "Floor\nDamage", "Diffuser\nDamage", "Sidepod\nDamage"], "Damage")
        self.create_tab(["Position", "Driver", "Tyres", "Current Lap", "Last Lap", "Fastest Lap"], "Laps")
        self.create_tab(["Position", "Driver", "Tyres", "Tyres Surface\nTemperatures",
                         "Tyres Inner\nTemperatures"], "Temperatures")


        self.setup_table_columns()
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

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
        font.setWeight(18)
        self.title_label.setFont(font)

        h_layout.addWidget(self.title_label)
        self.main_layout.addLayout(h_layout)

    def update_table(self, header, packet):
        func, args = MainWindow.function_hashmap[header.m_packet_id]
        func(packet, *args)
        active_tab_name = self.tabs.tabText(self.tabs.currentIndex())
        sorted_players_list = sorted(PLAYERS_LIST)
        self.models[active_tab_name].update_data(sorted_players_list, active_tab_name)

        if header.m_packet_id == 1:
            self.title_label.setText(session.title_display())

    def create_tab(self, header, name):
        data = [player.tab_list(name) for player in PLAYERS_LIST if player.position != 0]

        tab = QWidget(self)
        layout = QVBoxLayout()
        table = QTableView()
        table.setWordWrap(True)
        self.tables[name] = table
        self.models[name] = MyTableModel(data=data,
                              header=header)

        table.setModel(self.models[name])
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, name)
        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def resizeEvent(self, event):
        self.setup_table_columns()
        super().resizeEvent(event)


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
        font-size: 12pt;
        font-weight: bold
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
        height: 40px;
        background: #333;
        color: white;
        padding: 6px;
        border: 1px solid #555;
        border-bottom: none;
        font-size: 14pt;
    }
    
    QTabBar::tab:selected {
        background: #222;
        color: white;
        font-weight: bold;
        font-size: 14pt;
    }
    
    QTabBar::tab:hover {
        background: #444;
        font-size: 14pt;
    }
    
    QLabel{
        font-size: 18pt;
    }
    """

    app.setStyleSheet(dark_stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())