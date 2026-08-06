from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Settings coming soon..."))
