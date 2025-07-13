from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView


class RaceDirection(QListWidget):
    def __init__(self, parent):
        super().__init__()

        tab = QWidget(parent)
        layout = QVBoxLayout()
        layout.addWidget(self)
        self.setFont(QFont("Segoe UI Emoji", 12))

        tab.setLayout(layout)

        parent.tabs.addTab(tab, "Race Direction")

        self.setWordWrap(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)