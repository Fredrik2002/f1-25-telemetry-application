"""
 This file contains the table structure for the tabs :
    - Packet Reception
    - Motion Extended
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QAbstractItemView

from src.packet_processing.dictionnaries import packetDictionnary


class PacketReceptionTableModel(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__()
        self._data = [
            [packetDictionnary[i], "0/s"]
            for i in range(len(packetDictionnary))
        ]
        self._header = ["Packet Type", "Reception"]

        self.create_tab(parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def updateCell(self, row, column, value):
        self._data[row][column] = value
        index = self.index(row, column)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.FontRole:
            font = QFont("Segoe UI Emoji", 12)
            return font

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

    def create_tab(self, parent):

        tab = QWidget(parent)
        layout = QVBoxLayout()
        table = QTableView()
        table.setWordWrap(True)

        table.setModel(self)
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)
        tab.setLayout(layout)

        parent.tabs.addTab(tab, "Packet Reception")
        table.resizeRowsToContents()
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def update_data(self, packet_reception_dict):
        """
        sorted_players_list (list : Player) : List of Player sorted by position
        active_tab_name (str) : Gives the name of the current tab
        """
        self._data = [
            [packetDictionnary[i], str(packet_reception_dict[i]) + "/s"]
            for i in range(len(packetDictionnary))
        ]
        self.layoutChanged.emit()