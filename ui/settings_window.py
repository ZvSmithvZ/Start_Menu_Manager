from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)


class SettingsWindow(QDialog):
    def __init__(self, settings_manager):
        super().__init__()

        self.settings_manager = settings_manager

        self.setWindowTitle("Settings")
        self.resize(400, 300)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # Table settings

        table_group = QGroupBox("Table Settings")
        table_layout = QVBoxLayout()

        # layout.addWidget(QLabel("Table Settings"))

        self.auto_fit_checkbox = QCheckBox("Auto Fit Column Widths to Window")
        self.show_extensions_checkbox = QCheckBox("Show file extensions column")

        table_layout.addWidget(self.auto_fit_checkbox)
        table_layout.addWidget(self.show_extensions_checkbox)

        table_group.setLayout(table_layout)

        # Backup settings

        backup_group = QGroupBox("Backup Settings")
        backup_layout = QVBoxLayout()

        # backup_layout.addWidget(QLabel("Backup Settings"))
        self.auto_backup_checkbox = QCheckBox("Create automatic backup before changes")
        backup_layout.addWidget(self.auto_backup_checkbox)

        backup_group.setLayout(backup_layout)

        main_layout.addWidget(table_group)
        main_layout.addWidget(backup_group)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        main_layout.addLayout(button_layout)

    def load_settings(self):

        self.auto_fit_checkbox.setChecked(
            self.settings_manager.get(
                "auto_fit_column_widths",
                True,
            )
        )

        self.show_extensions_checkbox.setChecked(
            self.settings_manager.get(
                "show_extensions",
                False,
            )
        )

        self.auto_backup_checkbox.setChecked(
            self.settings_manager.get(
                "auto_backup_before_changes",
                False,
            )
        )

    def save_settings(self):

        self.settings_manager.set(
            "auto_fit_column_widths",
            self.auto_fit_checkbox.isChecked(),
        )

        self.settings_manager.set(
            "show_extensions",
            self.show_extensions_checkbox.isChecked(),
        )

        self.settings_manager.set(
            "auto_backup_before_changes",
            self.auto_backup_checkbox.isChecked(),
        )

        self.settings_manager.save()
        self.accept()
