from PySide6.QtCore import QFileInfo
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileIconProvider,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self, shortcut_manager):
        super().__init__()

        self.shortcut_manager = shortcut_manager
        self.icon_cache = {}

        self.broken_color = QColor("#ffcccc")
        self.duplicate_color = QColor("#fff2cc")

        # used for icons in the table
        self.icon_provider = QFileIconProvider()

        # window settings
        self.setWindowTitle("Start Menu Manager")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # vertical stacking system
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # buttons
        self.scan_button = QPushButton("Scan Start Menu")
        layout.addWidget(self.scan_button)
        self.scan_button.clicked.connect(self.rescan_shortcuts)

        self.find_duplicates_button = QPushButton("Find Duplicates")
        layout.addWidget(self.find_duplicates_button)
        self.find_duplicates_button.clicked.connect(self.show_duplicates)

        self.auto_size_columns_button = QPushButton("Find Duplicates")
        layout.addWidget(self.auto_size_columns_button)
        self.auto_size_columns_button.clicked.connect(self.auto_size_columns)

        # container
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.rescan_shortcuts()

    def rescan_shortcuts(self):

        shortcuts = self.shortcut_manager.load_shortcuts()
        self.duplicates = self.shortcut_manager.find_duplicates()
        self.populate_table(shortcuts)

    def show_duplicates(self):
        duplicate_shortcuts = []

        for shortcut_list in self.duplicates.values():
            duplicate_shortcuts.extend(shortcut_list)

        self.populate_table(duplicate_shortcuts)

    def populate_table(self, shortcuts):

        self.table.setUpdatesEnabled(False)
        self.table.clearContents()

        self.table.setRowCount(len(shortcuts))
        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels(
            [
                "Icon",
                "Name",
                "Target",
                "Folder",
                "Args",
                "File Path",
                "Broken?",
                "Duplicate",
                "Extension",
            ]
        )

        for row, shortcut in enumerate(shortcuts):

            shortcut_status = "Broken" if shortcut.is_broken else "Working"

            shortcut_dup_status = (
                "Duplicate" if shortcut.is_duplicate else "Not Duplicate"
            )

            # Create normal text items
            items = [
                None,  # Icon placeholder
                QTableWidgetItem(shortcut.name or ""),
                QTableWidgetItem(shortcut.target_path or ""),
                QTableWidgetItem(f"{shortcut.start_folder.value.title()} Folder"),
                QTableWidgetItem(shortcut.args or ""),
                QTableWidgetItem(shortcut.file_path or ""),
                QTableWidgetItem(shortcut_status),
                QTableWidgetItem(shortcut_dup_status),
                QTableWidgetItem(shortcut.extension or ""),
            ]

            # Create icon item separately
            if shortcut.file_path not in self.icon_cache:
                self.icon_cache[shortcut.file_path] = self.icon_provider.icon(
                    QFileInfo(shortcut.file_path)
                )

            icon = self.icon_cache[shortcut.file_path]
            # icon = self.icon_provider.icon(QFileInfo(shortcut.file_path))

            icon_item = QTableWidgetItem()
            icon_item.setIcon(icon)

            items[0] = icon_item

            # populating the table with items
            for column, item in enumerate(items):
                self.table.setItem(row, column, item)

            if shortcut.is_broken:
                for column in range(len(items)):
                    cell = self.table.item(row, column)
                    if cell:
                        cell.setBackground(self.broken_color)

            elif shortcut.is_duplicate:
                for column in range(len(items)):
                    cell = self.table.item(row, column)
                    if cell:
                        cell.setBackground(self.duplicate_color)

        self.table.setUpdatesEnabled(True)

    def auto_size_columns(self):
        self.table.resizeColumnsToContents()

    # name: str
    # file_path: str
    # extension: str
    # target_path: str
    # icon: str
    # args: str
    # is_broken: bool
    # start_folder: StartFolder
    # is_duplicate: bool
    # is_selected: bool
