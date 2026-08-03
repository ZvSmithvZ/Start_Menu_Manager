from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

DATA_DIR = ROOT_DIR / "data"

SETTINGS_FILE = DATA_DIR / "settings.json"

BACKUP_DIR = DATA_DIR / "backups"

MANUAL_BACKUP_DIR = BACKUP_DIR / "manual_backups"

AUTO_BACKUP_DIR = BACKUP_DIR / "automatic_backups"
