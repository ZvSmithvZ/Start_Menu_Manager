from PySide6.QtCore import QFileInfo
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFileIconProvider,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class ShortcutEditor(QDialog):
    def __init__(self, shortcut, icon_manager):
        super().__init__()

        self.shortcut = shortcut
        self.icon_manager = icon_manager

        self.setWindowTitle("Edit Shortcut")
        self.resize(600, 250)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Name"))

        # Icon

        icon = self.icon_manager.get_icon(shortcut.file_path)

        self.icon_label.setPixmap(icon.pixmap(48, 48))

        self.change_icon_button = QPushButton("Browse...")
        self.change_icon_button.clicked.connect(self.pick_icon)
        icon_layout = QHBoxLayout()

        icon_layout.addWidget(self.icon_label)
        icon_layout.addWidget(self.change_icon_button)

        layout.addLayout(icon_layout)

        # Name
        self.name_edit = QLineEdit(shortcut.name)
        layout.addWidget(self.name_edit)

        # Target
        layout.addWidget(QLabel("Target"))

        target_layout = QHBoxLayout()

        self.target_edit = QLineEdit(shortcut.target_path)

        self.browse_target_button = QPushButton("Browse...")
        self.browse_target_button.clicked.connect(self.pick_target)

        target_layout.addWidget(self.target_edit)
        target_layout.addWidget(self.browse_target_button)

        layout.addLayout(target_layout)

        # Arguments
        layout.addWidget(QLabel("Arguments"))

        self.args_edit = QLineEdit(shortcut.args)
        layout.addWidget(self.args_edit)

        # working dir
        layout.addWidget(QLabel("Start In"))

        self.working_directory_edit = QLineEdit(shortcut.working_dir)

        layout.addWidget(self.working_directory_edit)

        # Cancel/Save Buttons
        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save")

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self.accept)

    def get_shortcut(self):
        self.shortcut.name = self.name_edit.text()
        self.shortcut.target_path = self.target_edit.text()
        self.shortcut.args = self.args_edit.text()
        self.shortcut.working_dir = self.working_directory_edit.text()

        return self.shortcut

    def pick_target(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose executable",
            self.target_edit.text(),
            "Programs (*.exe);;All Files (*)",
        )

        if filename:
            self.target_edit.setText(filename)

    def pick_icon(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose icon", "", "Icons (*.ico *.exe *.dll);;All Files (*)"
        )

        if filename:
            self.shortcut.icon_path = filename

            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(filename))

            self.icon_label.setPixmap(icon.pixmap(48, 48))
