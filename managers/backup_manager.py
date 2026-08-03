import json
from datetime import datetime
from pathlib import Path

from models.shortcut import Shortcut
from services.shortcut_serializer import ShortcutSerializer
from utils.paths import AUTO_BACKUP_DIR, BACKUP_DIR


class BackupManager:
    def __init__(self, serializer: ShortcutSerializer):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        AUTO_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        self.serializer = serializer

    def save_backup(
        self, shortcuts: list[Shortcut], manual: bool, backup_name: str | None = None
    ) -> Path:

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")  # noqa: DTZ005

        invalid_chars = '<>:"/\\|?*'

        if backup_name:
            for char in invalid_chars:
                backup_name = backup_name.replace(char, "_")

        if not backup_name:
            backup_name = f"start_menu_shortcuts_backup_{timestamp}.json"

        if not backup_name.endswith(".json"):
            backup_name += ".json"

        if manual:
            backup_path = BACKUP_DIR / backup_name

        else:
            backup_path = AUTO_BACKUP_DIR / backup_name

        backup_path = self.get_unique_backup_path(backup_path)

        backup_data = [self.serializer.serialize(shortcut) for shortcut in shortcuts]

        with backup_path.open("w") as file:
            json.dump(backup_data, file, indent=4)

        return backup_path

    def get_backups(self):
        return list(BACKUP_DIR.glob("*.json"))

    def load_backup(self, backup_path: Path) -> list[Shortcut]:

        with backup_path.open("r") as file:
            backup_data = json.load(file)

        return [self.serializer.deserialize(shortcut) for shortcut in backup_data]

    def get_unique_backup_path(self, backup_path: Path) -> Path:
        counter = 1

        original_path = backup_path

        while backup_path.exists():
            backup_path = original_path.with_stem(f"{original_path.stem} ({counter})")
            counter += 1

        return backup_path
