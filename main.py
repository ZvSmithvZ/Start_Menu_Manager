from PySide6.QtWidgets import QApplication

from managers.shortcut_manager import ShortcutManager
from services.scanner import ShortcutScanner
from ui.main_window import MainWindow

scanner = ShortcutScanner()
manager = ShortcutManager()


app = QApplication([])
window = MainWindow(manager)

window.show()
app.exec()


# manager.load_shortcuts()
# manager.find_duplicates()
