import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple avec QTabWidget + QTableWidget")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Top horizontal layout
        top_layout = QHBoxLayout()
        btn1 = QPushButton("Bouton 1")
        btn2 = QPushButton("Bouton 2")
        top_layout.addWidget(btn1)
        top_layout.addWidget(btn2)
        main_layout.addLayout(top_layout)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_table_tab("Tableau 1"), "Onglet 1")
        tabs.addTab(self.create_table_tab("Tableau 2"), "Onglet 2")
        main_layout.addWidget(tabs)

        self.setLayout(main_layout)

    def create_table_tab(self, label):
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Colonne A", "Colonne B", "Colonne C"])
        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"{label} - {row},{col}")
                table.setItem(row, col, item)
        return table


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
