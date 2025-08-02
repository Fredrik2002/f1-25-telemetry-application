from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.packet_processing.dictionnaries import color_flag_dict, track_dictionary, teams_color_dictionary
from src.packet_processing.variables import session, PLAYERS_LIST, tracks_folder
import src


class Canvas(QWidget):
    PADDING = 30
    RADIUS = 2
    FONT = QFont("Arial", 10)

    def __init__(self):
        super().__init__()
        # Those values are automatically calculated in the create_map function according to the canvas size
        self.coeff = None
        self.offset_x = None
        self.offset_z = None


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(Canvas.FONT)
        if src.packet_processing.variables.REDRAW_MAP:
            self.create_map(painter)
            self.draw_circles(painter)
            src.packet_processing.variables.REDRAW_MAP = False
        else:
            for index, polygon in enumerate(session.segments):
                painter.setPen(QPen(color_flag_dict[session.marshalZones[index].m_zone_flag]))
                painter.drawPolyline(polygon)
            for player in PLAYERS_LIST:
                if player.resultStatus < 4 and player.networkId != 255:
                    x_map = int(player.worldPositionX / self.coeff + self.offset_x - Canvas.RADIUS)
                    z_map = int(player.worldPositionZ / self.coeff + self.offset_z - Canvas.RADIUS)
                    player.oval.moveTo(x_map, z_map)
                    painter.setPen(player.qpen)
                    painter.drawText(x_map+20, z_map+20, player.name)
                    painter.drawEllipse(player.oval)


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
            if player.resultStatus < 4 and player.networkId != 255:
                player.oval = QRectF(player.worldPositionX/self.coeff + self.offset_x - Canvas.RADIUS,
                                     player.worldPositionZ/self.coeff + self.offset_z - Canvas.RADIUS,
                                     2*Canvas.RADIUS, 2*Canvas.RADIUS)
                player.qpen = QPen(teams_color_dictionary[player.teamId], 2*Canvas.RADIUS)
                painter.setPen(player.qpen)
                painter.drawEllipse(player.oval)

