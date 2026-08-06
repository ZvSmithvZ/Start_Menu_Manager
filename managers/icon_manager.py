from PySide6.QtCore import QFileInfo
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileIconProvider


class IconManager:
    def __init__(self):
        self.icon_provider = QFileIconProvider()
        self.icon_cache: dict[str, QIcon] = {}

    def get_icon(self, shortcut_path: str) -> QIcon:
        if shortcut_path not in self.icon_cache:
            self.icon_cache[shortcut_path] = self.icon_provider.icon(
                QFileInfo(shortcut_path)
            )

        return self.icon_cache[shortcut_path]

    def clear_cache(self):
        self.icon_cache.clear()
