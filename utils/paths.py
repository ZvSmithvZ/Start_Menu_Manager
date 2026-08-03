from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

DATA_DIR = ROOT_DIR / "data"

SETTINGS_FILE = DATA_DIR / "settings.json"

BACKUP_DIR = DATA_DIR / "backups"

AUTO_BACKUP_DIR = DATA_DIR / "backups" / "automatic_backups"

# BACKUP_DIR.mkdir(parents=True, exist_ok=True)
