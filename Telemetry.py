import sys

from PySide6.QtWidgets import QApplication

from src.windows.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open("style.css", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())