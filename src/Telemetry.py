import cProfile
import re

from PyQt6.QtWidgets import QApplication

from src.windows.main_window import MainWindow
import pstats
from pstats import SortKey
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    #cProfile.run("window.run()", "stats")
    #p = pstats.Stats('stats')
    #p.sort_stats("tottime").print_stats()







