import sys

from PyQt5.QtCore import QSize, Qt, QPointF, QRectF, QAbstractTableModel

sys.path.append(".")
sys.path.append("..")
sys.path.append("../src")

from PyQt5.QtGui import QFont, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel, QAbstractItemView,
    QTabBar, QListWidget
)

from src.packet_management import *
from src.windows.myTableModel import MyTableModel, MyTableModelWeatherForecast, MyTableModelPacketReception
from src.windows.SocketThread import SocketThread


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
        self.setWindowTitle("TableView with Auto Sort")
        self.resize(1440, 800)

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
        self.create_tab(["Position", "Driver", "Tyres", "Tyres\nWear",
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
        font.setWeight(18)
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
        self.map_canvas.redraw_map = True
        super().resizeEvent(event)


class Canvas(QWidget):
    PADDING = 30
    RADIUS = 3
    FONT = QFont("Arial", 12)

    def __init__(self):
        super().__init__()
        # Those values are automatically calculated in the create_map function according to the canvas size
        self.coeff = None
        self.offset_x = None
        self.offset_x = None


    def paintEvent(self, event):
        global REDRAW_MAP
        painter = QPainter(self)
        painter.setFont(Canvas.FONT)
        if REDRAW_MAP:
            self.create_map(painter)
            self.draw_circles(painter)
            REDRAW_MAP = False
        else:
            for index, polygon in enumerate(session.segments):
                painter.setPen(QPen(color_flag_dict[session.marshalZones[index].m_zone_flag]))
                painter.drawPolyline(polygon)
            for player in PLAYERS_LIST:
                x_map = int(player.worldPositionX / self.coeff + self.offset_x - Canvas.RADIUS)
                z_map = int(player.worldPositionZ / self.coeff + self.offset_z - Canvas.RADIUS)
                player.oval.moveTo(x_map, z_map)
                painter.setPen(player.qpen)
                painter.drawText(x_map+20, z_map+20, player.name)
                painter.drawEllipse(player.oval)


    def update_data(self, a, b):
        self.update()


    def create_map(self, painter):
        session.segments.clear()
        cmi = 1
        L0, L1, = [], []
        L = [[]]
        track_name, coeff, x_offset, z_offset = track_dictionary[session.track]
        with open(tracks_folder / f"{track_name}_2020_racingline.txt", "r") as file:
            for index, line in enumerate(file):
                if index not in [0,1]:
                    dist, z, x, y, _, _ = line.strip().split(",")
                    if cmi == 1:
                        L0.append((float(z), float(x)))
                    elif cmi == session.num_marshal_zones:
                        L1.append((float(z), float(x)))
                    else:
                        L[-1].append((float(z), float(x)))
                    if (float(dist) / session.trackLength) > session.marshalZones[
                        cmi].m_zone_start and cmi != session.num_marshal_zones:
                        if cmi != 1:
                            L.append([])
                        cmi += 1
        L.insert(0, L1+L0)
        L.pop()
        x_min = min([min(element)[0] for element in L])
        x_max = max([max(element)[0] for element in L])
        z_min = min([min(element, key=lambda x: x[1])[1] for element in L])
        z_max = max([max(element, key=lambda x: x[1])[1] for element in L])

        # We don't want the map to touch the edge of our canvas
        canvas_width = self.width() - 2*Canvas.PADDING
        canvas_height = self.height() - 2 * Canvas.PADDING

        # Minimum coefficient by which we have to smallen the map to fit it into the canvas in both directions
        coeff_x = (x_max - x_min) / canvas_width
        coeff_z = (z_max - z_min) / canvas_height

        # We take the worst coefficient (to fit the map in both directions)
        self.coeff = max(coeff_x, coeff_z)

        # The offset is the minimum coordinates + Padding + a certain amount to have to map in the middle of the canvas
        self.offset_x = -x_min/self.coeff + (canvas_width - (x_max-x_min)/self.coeff)/2 + Canvas.PADDING
        self.offset_z = -z_min/self.coeff + (canvas_height - (z_max-z_min)/self.coeff)/2 + Canvas.PADDING

        # We create a polygon for each minisector
        for index, zone in enumerate(L):
            points = [QPointF(x / self.coeff + self.offset_x, z / self.coeff + self.offset_z) for x, z in zone]
            polygon = QPolygonF(points)
            painter.setPen(QPen(color_flag_dict[session.marshalZones[index].m_zone_flag]))
            session.segments.append(polygon)
            painter.setPen(QPen(Qt.red))
            painter.drawPolyline(polygon)

    def draw_circles(self, painter):
        for player in PLAYERS_LIST:
            player.oval = QRectF(player.worldPositionX/self.coeff + self.offset_x - Canvas.RADIUS,
                                 player.worldPositionZ/self.coeff + self.offset_z - Canvas.RADIUS,
                                 2*Canvas.RADIUS, 2*Canvas.RADIUS)
            player.qpen = QPen(teams_color_dictionary[player.teamId], 2*Canvas.RADIUS)
            painter.setPen(player.qpen)
            painter.drawEllipse(player.oval)


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
        font-size: 12pt;
    }
    
    QTabBar::tab:selected {
        background: #222;
        color: white;
        font-weight: bold;
        font-size: 12pt;
    }
    
    QTabBar::tab:hover {
        background: #444;
        font-size: 12pt;
    }
    
    QLabel{
        font-size: 18pt;
    }
    """

    app.setStyleSheet(dark_stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())