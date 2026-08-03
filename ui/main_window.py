from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
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
        self.scan_button.clicked.connect(self.scan_shortcuts)

        self.find_duplicates_button = QPushButton("Find Duplicates")
        layout.addWidget(self.find_duplicates_button)
        self.find_duplicates_button.clicked.connect(self.show_duplicates)

        # container
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def scan_shortcuts(self):

        shortcuts = self.shortcut_manager.load_shortcuts()
        self.populate_table(shortcuts)

        # self.table.setRowCount(len(shortcuts))
        # self.table.setColumnCount(9)
        # self.table.setHorizontalHeaderLabels(
        #     [
        #         "Icon",
        #         "Name",
        #         "Target",
        #         "Start Folder",
        #         "Args",
        #         "File Path",
        #         "Broken?",
        #         "Duplicate",
        #         "Extension",
        #     ]
        # )

        # for row, shortcut in enumerate(shortcuts):
        #     shortcut_status = "Broken" if shortcut.is_broken else "Working"
        #     shortcut_dup_status = (
        #         "Duplicate" if shortcut.is_duplicate else "Not Duplicate"
        #     )
        #     items = [
        #         QTableWidgetItem(shortcut.icon or ""),
        #         QTableWidgetItem(shortcut.name or ""),
        #         QTableWidgetItem(shortcut.target_path or ""),
        #         QTableWidgetItem(f"{shortcut.start_folder.value.title()} Folder"),
        #         QTableWidgetItem(shortcut.args or ""),
        #         QTableWidgetItem(shortcut.file_path or ""),
        #         QTableWidgetItem(shortcut_status or ""),
        #         QTableWidgetItem(shortcut_dup_status or ""),
        #         QTableWidgetItem(shortcut.extension or ""),
        #     ]
        #     for column, item in enumerate(items):
        #         self.table.setItem(row, column, item)
        #     if shortcut.is_broken:
        #         for column in range(len(items)):
        #             cell = self.table.item(row, column)
        #             if cell:
        #                 cell.setBackground(QColor("#ffcccc"))

        # self.table.resizeColumnsToContents()

    def show_duplicates(self):
        duplicates = self.shortcut_manager.find_duplicates()

        duplicate_shortcuts = []

        for shortcut_list in duplicates.values():
            duplicate_shortcuts.extend(shortcut_list)

        self.populate_table(duplicate_shortcuts)

    def populate_table(self, shortcuts):

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
            print(shortcut.icon)

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
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(shortcut.icon))

            items[0] = icon_item

            for column, item in enumerate(items):
                self.table.setItem(row, column, item)

            if shortcut.is_broken:
                for column in range(len(items)):
                    cell = self.table.item(row, column)
                    if cell:
                        cell.setBackground(QColor("#ffcccc"))
            elif shortcut.is_duplicate:
                for column in range(len(items)):
                    cell = self.table.item(row, column)
                    if cell:
                        cell.setBackground(QColor("#fff2cc"))

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
