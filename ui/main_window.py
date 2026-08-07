import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QButtonGroup,
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

from managers.icon_manager import IconManager
from managers.settings_manager import SettingsManager
from models.shortcut import Shortcut
from models.ui_table import TableView
from services.shortcut_writer import ShortcutWriter
from ui.settings_window import SettingsWindow
from ui.shortcut_editor import ShortcutEditor


class MainWindow(QMainWindow):

    def __init__(self, shortcut_manager, backup_manager):
        super().__init__()
        self.table_view = TableView.ALL_VIEW

        self.shortcut_manager = shortcut_manager
        self.backup_manager = backup_manager

        self.icon_manager = IconManager()
        self.settings_manager = SettingsManager()

        self.current_shortcuts = []

        self.broken_color = QColor("#ffcccc")
        self.duplicate_color = QColor("#fff2cc")

        # window settings
        self.setWindowTitle("Start Menu Manager")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

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
        self.get_checked_button = QPushButton("Print checked")
        self.get_checked_button.clicked.connect(self.get_checked_shortcuts)
        button_layout.addWidget(self.get_checked_button)

        # self.fit_data_button = QPushButton("Fit Data")
        # self.fit_data_button.clicked.connect(self.fit_data)
        # button_layout.addWidget(self.fit_data_button)

        # self.toggle_auto_fit_button = QPushButton("Toggle Auto Fit")
        # self.toggle_auto_fit_button.clicked.connect(self.toggle_auto_fit)
        # button_layout.addWidget(self.toggle_auto_fit_button)

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
        # highlight checked rows
        self.table.itemChanged.connect(self.checkbox_changed)

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

        self.table.cellDoubleClicked.connect(self.double_click_edit)

        # build the top menu bar
        self.create_menu_bar()
        # apply column settings
        self.apply_settings()

        # initially called to populate the table
        self.scan_shortcuts()

    def scan_shortcuts(self):

        # self.current_shortcuts = self.shortcut_manager.load_shortcuts()
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
        self.current_shortcuts = self.shortcut_manager.load_shortcuts()
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
        if self.table_view == TableView.ALL_VIEW:
            return
        self.table_view = TableView.ALL_VIEW
        self.populate_table(self.current_shortcuts)

    def show_duplicate_shortcuts(self):
        if self.table_view == TableView.DUP_VIEW:
            return
        self.table_view = TableView.DUP_VIEW
        self.populate_table(self.duplicate_shortcuts)

    def show_broken_shortcuts(self):
        if self.table_view == TableView.BROKE_VIEW:
            return
        self.table_view = TableView.BROKE_VIEW
        self.populate_table(self.broken_shortcuts)

    def show_windows_shortcuts(self):
        if self.table_view == TableView.WIN_VIEW:
            return

        self.table_view = TableView.WIN_VIEW
        self.populate_table(self.windows_shortcuts)

    def populate_table(self, shortcuts):
        print("Populate TABLE")
        self.table.blockSignals(True)
        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)

        self.table.clearContents()

        self.table.setRowCount(len(shortcuts))
        self.table.setColumnCount(10)

        self.table.setHorizontalHeaderLabels(
            [
                "",
                "Icon",
                "Name",
                "Target",
                "Folder",
                "Args",
                "Starts In",
                "File Path",
                "Broken?",
                "Duplicate",
                "Extension",
            ]
        )

        header = self.table.horizontalHeader()

        if self.auto_fit_enabled:

            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 20)

            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(1, 35)

            for column in [2, 3, 5, 6]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

            for column in [4, 7, 8, 9, 10]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)

        else:
            self.table.setColumnWidth(0, 20)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

            for column in [2, 3, 5, 6]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

            for column in [4, 7, 8, 9, 10]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

        for row, shortcut in enumerate(shortcuts):

            shortcut_status = "Broken" if shortcut.is_broken else "Working"

            shortcut_dup_status = (
                "Duplicate" if shortcut.is_duplicate else "Not Duplicate"
            )

            # Create normal text items
            items = [
                None,  # checkbox placeholder
                None,  # Icon placeholder
                QTableWidgetItem(shortcut.name or ""),
                QTableWidgetItem(shortcut.target_path or ""),
                QTableWidgetItem(f"{shortcut.start_folder.value.title()} Folder"),
                QTableWidgetItem(shortcut.args or ""),
                QTableWidgetItem(shortcut.working_dir or ""),
                QTableWidgetItem(shortcut.file_path or ""),
                QTableWidgetItem(shortcut_status),
                QTableWidgetItem(shortcut_dup_status),
                QTableWidgetItem(shortcut.extension or ""),
            ]

            # creating checkbox
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )

            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            items[0] = checkbox_item

            # Create icon item separately
            icon = self.icon_manager.get_icon(shortcut.file_path)

            icon_item = QTableWidgetItem()
            icon_item.setIcon(icon)

            items[1] = icon_item

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
        self.table.blockSignals(False)

    def fit_data(self):
        self.table.resizeColumnsToContents()

    def toggle_auto_fit(self):
        self.auto_fit_enabled = not self.settings_manager.get(
            "auto_fit_column_widths", True
        )
        self.settings_manager.set(
            "auto_fit_column_widths",
            self.auto_fit_enabled,
        )

        self.settings_manager.save()
        self.apply_auto_fit_settings()

    def apply_auto_fit_settings(self):
        self.auto_fit_enabled = self.settings_manager.get(
            "auto_fit_column_widths", True
        )

        header = self.table.horizontalHeader()
        if self.auto_fit_enabled:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 20)

            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(1, 35)

            for column in [2, 3, 5, 6]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

            for column in [4, 7, 8, 9, 10]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)

            self.toggle_auto_fit_action.setChecked(True)

        else:
            self.table.setColumnWidth(0, 20)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

            for column in [2, 3, 5, 6]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

            for column in [4, 7, 8, 9, 10]:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

    def apply_column_visibility(self):
        show_extensions = self.settings_manager.get("show_extensions", False)
        self.table.setColumnHidden(9, not show_extensions)

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

    def get_shortcut_at_row(self, row):
        shortcuts = self.get_displayed_shortcuts()

        if row < 0 or row >= len(shortcuts):
            return None

        return shortcuts[row]

    def get_checked_shortcuts(self):

        checked = []

        shortcuts = self.get_displayed_shortcuts()

        for row in range(self.table.rowCount()):

            item = self.table.item(row, 0)

            if item is None:
                return

            if item.checkState() == Qt.CheckState.Checked:
                checked.append(shortcuts[row])

        print(checked)

        return checked

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

    def apply_settings(self):
        self.apply_auto_fit_settings()
        self.apply_column_visibility()

    def open_settings(self):
        settings_window = SettingsWindow(self.settings_manager)
        if settings_window.exec():
            self.apply_settings()

    def create_menu_bar(self):

        # grab auto fit setting
        self.auto_fit_enabled = self.settings_manager.get(
            "auto_fit_column_widths", True
        )

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        create_backup_action = QAction("Create Backup", self)
        create_backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(create_backup_action)

        restore_backup_action = QAction("Restore Backup", self)
        restore_backup_action.triggered.connect(self.restore_backup)
        file_menu.addAction(restore_backup_action)

        file_menu.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)

        file_menu.addAction(settings_action)
        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        self.tools_menu = menu_bar.addMenu("Tools")

        refresh_action = QAction("Refresh Shortcuts", self)
        refresh_action.triggered.connect(self.scan_shortcuts)
        self.tools_menu.addAction(refresh_action)

        file_menu.addSeparator()

        self.toggle_auto_fit_action = QAction("Auto Fit Column Widths to Window", self)
        self.toggle_auto_fit_action.triggered.connect(self.toggle_auto_fit)
        self.tools_menu.addAction(self.toggle_auto_fit_action)
        self.toggle_auto_fit_action.setCheckable(True)
        if self.auto_fit_enabled:
            self.toggle_auto_fit_action.setChecked(True)
        else:
            self.toggle_auto_fit_action.setChecked(False)

        file_menu.addSeparator()

        fit_columns_to_data = QAction("Set Column Widths to Data", self)
        fit_columns_to_data.triggered.connect(self.fit_data)
        self.tools_menu.addAction(fit_columns_to_data)

    def show_context_menu(self, position):
        menu = QMenu()

        row = self.table.rowAt(position.y())

        shortcut = self.get_shortcut_at_row(row)

        if not shortcut:
            return

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

    def double_click_edit(self, row, column):
        shortcut = self.get_shortcut_at_row(row)
        if not shortcut:
            return

        self.edit_shortcut(shortcut)

    def edit_shortcut(self, shortcut):
        self.shortcut_writer = ShortcutWriter()

        editor = ShortcutEditor(shortcut, self.icon_manager)
        old_name = shortcut.name

        if editor.exec():

            updated_shortcut = editor.get_shortcut()

            if updated_shortcut.name != old_name:
                self.shortcut_writer.rename_shortcut(
                    updated_shortcut,
                    updated_shortcut.name,
                )

            self.shortcut_writer.update_shortcut(updated_shortcut)

            self.icon_manager.clear_cache()
            self.scan_shortcuts()

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

    def delete_checked_shortcuts(self):

        shortcuts = self.get_checked_shortcuts()

        if shortcuts is None:
            return

        for shortcut in shortcuts:
            self.delete_shortcut(shortcut)

    def checkbox_changed(self, item):
        print("CHECKBOX CHANGED", item.row(), item.column())
        if item.column() != 0:
            return

        row = item.row()

        self.table.blockSignals(True)

        try:
            if item.checkState() == Qt.CheckState.Checked:

                # Store existing colors before changing them
                for col in range(self.table.columnCount()):
                    cell = self.table.item(row, col)

                    if cell:
                        cell.setData(
                            Qt.ItemDataRole.UserRole + 1,
                            cell.background(),
                        )
                        cell.setBackground(QColor("#d0e7ff"))

            else:

                # Restore previous colors
                for col in range(self.table.columnCount()):
                    cell = self.table.item(row, col)

                    if cell:
                        old_color = cell.data(Qt.ItemDataRole.UserRole + 1)

                        if old_color:
                            cell.setBackground(old_color)

        finally:
            self.table.blockSignals(False)
