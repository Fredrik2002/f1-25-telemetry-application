from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView


class RaceDirection(QListWidget):
    def __init__(self):
        super().__init__()

        self.setFont(QFont("Segoe UI Emoji", 12))

        self.setWordWrap(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def update(self):
        self.viewport().update()