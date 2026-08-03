from PySide6.QtWidgets import QApplication

from managers.backup_manager import BackupManager
from managers.shortcut_manager import ShortcutManager
from services.scanner import ShortcutScanner
from services.shortcut_serializer import ShortcutSerializer
from ui.main_window import MainWindow

shortcut_scanner = ShortcutScanner()
shortcut_manager = ShortcutManager()

serializer = ShortcutSerializer()

backup_manager = BackupManager(serializer)


app = QApplication([])
window = MainWindow(shortcut_manager, backup_manager)


window.show()

app.exec()
