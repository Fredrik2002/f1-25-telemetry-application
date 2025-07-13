"""
 This file contains the table structure for the tabs :
    - Packet Reception
    - Motion Extended
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QAbstractItemView

from src.packet_processing.dictionnaries import packetDictionnary
from src.table_models.GeneralTableModel import GeneralTableModel


class PacketReceptionTableModel(GeneralTableModel):
    def __init__(self, parent):
        data = [
            [packetDictionnary[i], "0/s"]
            for i in range(len(packetDictionnary))
        ]
        header = ["Packet Type", "Reception"]
        column_sizes = [30, 15]
        super().__init__(header, data, column_sizes)

        self.parent = parent


    def update(self):
        pass


    def update_each_second(self):
        self._data = [
            [packetDictionnary[i], str(self.parent.packet_reception_dict[i]) + "/s"]
            for i in range(len(packetDictionnary))
        ]
        self.layoutChanged.emit()