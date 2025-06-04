import cProfile
import re
from src.windows.main_window import MainWindow
import pstats
from pstats import SortKey


if __name__ == '__main__':
    window = MainWindow()
    cProfile.run("window.run()", "stats")
    p = pstats.Stats('stats')
    p.sort_stats("tottime").print_stats()
    #window.run()







