import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileIconProvider,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.shortcut import Shortcut
from models.ui_table import TableView


class MainWindow(QMainWindow):

    def __init__(self, shortcut_manager, backup_manager):
        super().__init__()
        self.table_view = TableView.ALL_VIEW

        self.shortcut_manager = shortcut_manager
        self.backup_manager = backup_manager

        self.auto_fit_enabled = True

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

        self.create_menu_bar()

        # vertical stacking system
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # buttons and search bar area
        button_layout = QHBoxLayout()

        # search bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search shortcuts...")
        self.search_box.textChanged.connect(self.filter_table)

        button_layout.addWidget(self.search_box)

        # start of horizontal buttons
        self.scan_button = QPushButton("Refresh")
        self.scan_button.clicked.connect(self.scan_shortcuts)
        button_layout.addWidget(self.scan_button)

        self.fit_data_button = QPushButton("Fit Data")
        self.fit_data_button.clicked.connect(self.fit_data)
        button_layout.addWidget(self.fit_data_button)

        self.toggle_auto_fit_button = QPushButton("Toggle Auto Fit")
        self.toggle_auto_fit_button.clicked.connect(self.toggle_auto_fit)
        button_layout.addWidget(self.toggle_auto_fit_button)

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

        self.show_windows_shortcuts_button = QPushButton("View System Shortcuts")
        self.show_windows_shortcuts_button.clicked.connect(self.show_windows_shortcuts)

        self.show_windows_shortcuts_button.setCheckable(True)
        self.view_group.addButton(self.show_windows_shortcuts_button)
        button_layout.addWidget(self.show_windows_shortcuts_button)

        self.view_group.setExclusive(True)
        # end of view group

        # adding button row to main layout
        layout.addLayout(button_layout)

        # container
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # setting highlight row color to light blue
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #3399ff;
                color: white;
            }
        """)

        # setting the selection behavior to highlight the whole row
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Context menu policy set to custom
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # disabling ability to edit info in the table
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # sorting by clicking headers
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)

        # initially called to populate the table
        self.scan_shortcuts()

    def scan_shortcuts(self):

        self.current_shortcuts = self.shortcut_manager.load_shortcuts()
        self.refresh_all_shortcuts()

        if self.table_view == TableView.ALL_VIEW:
            self.populate_table(self.current_shortcuts)
        elif self.table_view == TableView.DUP_VIEW:
            self.populate_table(self.duplicate_shortcuts)
        elif self.table_view == TableView.BROKE_VIEW:
            self.populate_table(self.broken_shortcuts)
        elif self.table_view == TableView.WIN_VIEW:
            self.populate_table(self.windows_shortcuts)

    def refresh_all_shortcuts(self):
        self.refresh_duplicates()
        self.refresh_brokens()
        self.refresh_windows_shortcuts()

    def refresh_duplicates(self):
        self.duplicate_shortcuts = []
        self.duplicates = self.shortcut_manager.find_duplicates()
        for shortcut_list in self.duplicates.values():
            self.duplicate_shortcuts.extend(shortcut_list)

    def refresh_brokens(self):
        self.broken_shortcuts = self.shortcut_manager.find_brokens()

    def refresh_windows_shortcuts(self):
        self.windows_shortcuts = self.shortcut_manager.find_windows_entries()

    def show_all_shortcuts(self):
        self.populate_table(self.current_shortcuts)
        self.table_view = TableView.ALL_VIEW

    def show_duplicate_shortcuts(self):
        self.populate_table(self.duplicate_shortcuts)
        self.table_view = TableView.DUP_VIEW

    def show_broken_shortcuts(self):
        self.populate_table(self.broken_shortcuts)
        self.table_view = TableView.BROKE_VIEW

    def show_windows_shortcuts(self):
        self.populate_table(self.windows_shortcuts)
        self.table_view = TableView.WIN_VIEW

    def populate_table(self, shortcuts):

        self.table.setSortingEnabled(False)

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

        header = self.table.horizontalHeader()

        if self.auto_fit_enabled:

            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 35)

            for column in [1, 2, 4, 5]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

            for column in [3, 6, 7, 8]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)

        else:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

            for column in [1, 2, 4, 5]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

            for column in [3, 6, 7, 8]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

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
        self.table.setSortingEnabled(True)

    def fit_data(self):
        self.table.resizeColumnsToContents()

    def toggle_auto_fit(self):
        self.auto_fit_enabled = not self.auto_fit_enabled

        header = self.table.horizontalHeader()

        if self.auto_fit_enabled:

            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 35)

            for column in [1, 2, 4, 5]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

            for column in [3, 6, 7, 8]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)

            self.toggle_auto_fit_action.setChecked(True)

        else:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

            for column in [1, 2, 4, 5]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

            for column in [3, 6, 7, 8]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

            self.toggle_auto_fit_action.setChecked(False)

    def filter_table(self, text: str):
        text = text.lower()

        for row in range(self.table.rowCount()):
            match = False

            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)

                if item and text in item.text().lower():
                    match = True
                    break

            self.table.setRowHidden(row, not match)

    def get_displayed_shortcuts(self) -> list[Shortcut]:
        if self.table_view == TableView.ALL_VIEW:
            return self.current_shortcuts

        elif self.table_view == TableView.DUP_VIEW:
            return self.duplicate_shortcuts

        elif self.table_view == TableView.BROKE_VIEW:
            return self.broken_shortcuts

        elif self.table_view == TableView.WIN_VIEW:
            return self.windows_shortcuts

        return []

    def create_auto_backup(self):
        backup_path = self.backup_manager.save_backup(
            self.shortcut_manager.shortcuts, False, None
        )

        print(f"Backup saved: {backup_path}")

    def create_backup(self):
        default_name = f"start_menu_shortcuts_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"  # noqa: DTZ005

        filename, ok = QInputDialog.getText(
            self, "Create Backup", "Backup name:", text=default_name
        )

        if ok:
            backup_path = self.backup_manager.save_backup(
                self.shortcut_manager.shortcuts, True, filename
            )

            print(f"Backup saved: {backup_path}")

    def restore_backup(self):

        backups = self.backup_manager.get_backups()
        if not backups:
            return

        backup_names = [f"{backup.parent.name}: {backup.name}" for backup in backups]

        selected_name, ok = QInputDialog.getItem(
            self,
            "Restore Backup",
            "Choose a backup:",
            backup_names,
            0,
            False,
        )

        if not ok:
            return

        # auto_backup on importing a file
        self.backup_manager.save_backup(self.shortcut_manager.shortcuts, False, None)

        backup_lookup = {
            f"{backup.parent.name}: {backup.name}": backup for backup in backups
        }
        selected_path = backup_lookup[selected_name]

        restored_shortcuts = self.backup_manager.load_backup(selected_path)

        self.shortcut_manager.restore_shortcuts(restored_shortcuts)

        self.current_shortcuts = self.shortcut_manager.shortcuts

        self.refresh_all_shortcuts()

        self.populate_table(self.current_shortcuts)

    def create_menu_bar(self):

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        create_backup_action = QAction("Create Backup", self)
        create_backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(create_backup_action)

        restore_backup_action = QAction("Restore Backup", self)
        restore_backup_action.triggered.connect(self.restore_backup)
        file_menu.addAction(restore_backup_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        self.tools_menu = menu_bar.addMenu("Tools")

        self.toggle_auto_fit_action = QAction("Auto Fit Column Widths to Window", self)
        self.toggle_auto_fit_action.triggered.connect(self.toggle_auto_fit)
        self.tools_menu.addAction(self.toggle_auto_fit_action)
        self.toggle_auto_fit_action.setCheckable(True)
        if self.auto_fit_enabled:
            self.toggle_auto_fit_action.setChecked(True)
        else:
            self.toggle_auto_fit_action.setChecked(False)

    def show_context_menu(self, position):
        menu = QMenu()

        row = self.table.rowAt(position.y())

        if row < 0:
            return

        shortcuts = self.get_displayed_shortcuts()
        shortcut = shortcuts[row]

        # open location menu entry
        open_location_action = menu.addAction("Open Shortcut Location")
        open_location_action.triggered.connect(
            lambda: self.open_shortcut_location(shortcut)
        )
        open_target_action = menu.addAction("Open Target Location")
        open_target_action.triggered.connect(
            lambda: self.open_shortcut_target(shortcut)
        )

        menu.addSeparator()

        edit_action = menu.addAction("Edit Shortcut")
        edit_action.triggered.connect(lambda: self.edit_shortcut(shortcut))

        menu.addSeparator()

        delete_action = menu.addAction("Delete Shortcut")
        delete_action.triggered.connect(lambda: self.delete_shortcut(shortcut))

        menu.exec(self.table.viewport().mapToGlobal(position))

    def open_shortcut_location(self, shortcut):
        subprocess.run(["explorer", "/select,", shortcut.file_path])  # noqa: PLW1510

    def open_shortcut_target(self, shortcut: Shortcut):
        subprocess.Popen(["explorer", "/select,", shortcut.target_path])

    def edit_shortcut(self, shortcut):
        pass

    def delete_shortcut(self, shortcut: Shortcut):

        shortcut_path = Path(shortcut.file_path)

        if shortcut_path.suffix.lower() != ".lnk":
            return

        answer = QMessageBox.question(
            self,
            "Delete Shortcut",
            f"Delete {shortcut.name}?",
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        shortcut_path.unlink()

        self.scan_shortcuts()
