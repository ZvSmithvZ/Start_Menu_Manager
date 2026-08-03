import subprocess

from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileIconProvider,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.ui_table import TableView


class MainWindow(QMainWindow):

    def __init__(self, shortcut_manager):
        super().__init__()
        self.table_view = TableView.ALL_VIEW

        self.shortcut_manager = shortcut_manager
        self.icon_cache = {}

        self.current_shortcuts = []

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
        button_layout = QHBoxLayout()

        self.scan_button = QPushButton("Refresh")
        self.scan_button.clicked.connect(self.scan_shortcuts)
        button_layout.addWidget(self.scan_button)

        self.auto_size_columns_button = QPushButton("Auto Size Columns")
        self.auto_size_columns_button.clicked.connect(self.auto_size_columns)
        button_layout.addWidget(self.auto_size_columns_button)

        # --grouped view buttons
        self.view_group = QButtonGroup(self)

        self.view_all_button = QPushButton("View All")
        self.view_all_button.clicked.connect(self.show_all_shortcuts)

        self.view_all_button.setCheckable(True)
        self.view_group.addButton(self.view_all_button)
        button_layout.addWidget(self.view_all_button)
        self.view_all_button.setChecked(True)

        self.view_duplicates_button = QPushButton("View Duplicates")
        self.view_duplicates_button.clicked.connect(self.show_duplicate_shortcuts)

        self.view_duplicates_button.setCheckable(True)
        self.view_group.addButton(self.view_duplicates_button)
        button_layout.addWidget(self.view_duplicates_button)

        self.view_brokens_button = QPushButton("View Broken")
        self.view_brokens_button.clicked.connect(self.show_broken_shortcuts)

        self.view_brokens_button.setCheckable(True)
        self.view_group.addButton(self.view_brokens_button)
        button_layout.addWidget(self.view_brokens_button)

        self.view_group.setExclusive(True)
        # end of view group

        self.show_windows_entries_button = QPushButton("Show Windows Entries")
        self.show_windows_entries_button.setCheckable(True)
        button_layout.addWidget(self.show_windows_entries_button)

        # adding button row to main layout

        layout.addLayout(button_layout)

        # container
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #3399ff;
                color: white;
            }
        """)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # disabling ability to edit info in the table
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # initially called to populate the table
        self.scan_shortcuts()

    def scan_shortcuts(self):

        self.current_shortcuts = self.shortcut_manager.load_shortcuts()
        self.refresh_duplicates()
        self.refresh_brokens()

        if self.table_view == TableView.ALL_VIEW:
            self.populate_table(self.current_shortcuts)
        elif self.table_view == TableView.DUP_VIEW:
            self.populate_table(self.duplicate_shortcuts)
        elif self.table_view == TableView.BROKE_VIEW:
            self.populate_table(self.broken_shortcuts)

    def refresh_duplicates(self):
        self.duplicate_shortcuts = []
        self.duplicates = self.shortcut_manager.find_duplicates()
        for shortcut_list in self.duplicates.values():
            self.duplicate_shortcuts.extend(shortcut_list)

    def refresh_brokens(self):
        self.broken_shortcuts = self.shortcut_manager.find_brokens()

    def show_all_shortcuts(self):
        self.populate_table(self.current_shortcuts)
        self.table_view = TableView.ALL_VIEW

    def show_duplicate_shortcuts(self):
        self.populate_table(self.duplicate_shortcuts)
        self.table_view = TableView.DUP_VIEW

    def show_broken_shortcuts(self):
        self.populate_table(self.broken_shortcuts)
        self.table_view = TableView.BROKE_VIEW

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

    def show_context_menu(self, position):
        menu = QMenu()

        # getting the shortcut of the row to modify
        row = self.table.rowAt(position.y())
        if row < 0:
            return

        shortcut = self.current_shortcuts[row]

        # open location menu entry
        open_location_action = menu.addAction("Open Shortcut Location")
        open_location_action.triggered.connect(
            lambda: self.open_shortcut_location(shortcut)
        )

        menu.exec(self.table.viewport().mapToGlobal(position))

    def open_shortcut_location(self, shortcut):
        subprocess.run(["explorer", "/select,", shortcut.file_path])  # noqa: PLW1510
