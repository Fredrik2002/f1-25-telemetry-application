from PyQt5.QtCore import QThread, pyqtSignal

from src.parsers import parser2025
from src.parsers.parser2025 import PacketHeader, Packet
from src.variables import PORT, dictionnary_settings


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