from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
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

        layout = QVBoxLayout(self)

        # Table settings
        layout.addWidget(QLabel("Table Settings"))

        self.dynamic_columns_checkbox = QCheckBox("Auto Fit Column Widths to Window")

        self.show_extensions_checkbox = QCheckBox("Show file extensions")

        layout.addWidget(self.dynamic_columns_checkbox)
        layout.addWidget(self.show_extensions_checkbox)

        # Backup settings
        layout.addWidget(QLabel("Backup Settings"))
        self.auto_backup_checkbox = QCheckBox("Create automatic backup before changes")
        layout.addWidget(self.auto_backup_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def load_settings(self):

        self.dynamic_columns_checkbox.setChecked(
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
            self.dynamic_columns_checkbox.isChecked(),
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
