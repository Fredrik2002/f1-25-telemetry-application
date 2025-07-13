from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRect
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QStyledItemDelegate

from src.packet_processing.Player import Player
from src.packet_processing.packet_management import *
from src.packet_processing.variables import PLAYERS_LIST, session

class MultiTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        # Expects: list of tuples like [("A", QColor("red")), ("B", QColor("green")), ...]
        data = index.data()

        rect = option.rect

        font = QFont("Segoe UI Emoji", 12)
        painter.setFont(font)

        w = rect.width() // 2
        h = rect.height() // 2

        positions = [
            QRect(rect.left(), rect.top(), w, h),  # haut gauche
            QRect(rect.left() + w, rect.top(), w, h),  # haut droit
            QRect(rect.left(), rect.top() + h, w, h),  # bas gauche
            QRect(rect.left() + w, rect.top() + h, w, h)  # bas droit
        ]

        for (text, color), pos in zip(data, positions):
            painter.setPen(color)
            painter.drawText(pos, Qt.AlignCenter, text)
        painter.restore()