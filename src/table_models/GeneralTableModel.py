"""
 This file contains the main table structure for most of the tabs :
    - Main
    - Damage
    - Temperatures
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView

from src.packet_processing.Player import Player
from src.packet_processing.packet_management import *
from src.packet_processing.variables import PLAYERS_LIST
from src.table_models.utils import MultiTextDelegate


class GeneralTableModel(QAbstractTableModel):
    def __init__(self, header, data, column_sizes):
        super().__init__()
        self._header = header
        self._data = data
        self.column_sizes = column_sizes

        self.table = QTableView()
        self.create_table()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

        if role == Qt.FontRole:
            return QFont("Segoe UI Emoji", 12)


    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
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

    def create_table(self):
        """
        Create the QTableView object for this QAbstractTableModel
        """
        self.table.setModel(self)
        self.table.setWordWrap(True)

        for i in range(len(self._header)):
            if self._header[i] in ["Tyres\nBlister", "Tyres\nWear"]:
                self.table.setItemDelegateForColumn(i, MultiTextDelegate(self.table))

        self.table.verticalHeader().setVisible(False)

        self.table.resizeRowsToContents()
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionsMovable(False)

        self.resize()

    def resize(self):
        width = self.table.viewport().width()
        for i in range(len(self._header)):
            self.table.setColumnWidth(i, int(width / 75 * self.column_sizes[i]))

