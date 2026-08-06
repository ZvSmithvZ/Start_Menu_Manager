import json

from utils.paths import SETTINGS_FILE


class SettingsManager:
    def __init__(self):

        self.settings = {}

        SETTINGS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.load()

    def load(self):
        if not SETTINGS_FILE.exists:
            self.settings = {}
            self.save()
            return

        try:
            with SETTINGS_FILE.open("r") as file:
                self.settings = json.load(file)

        except json.JSONDecodeError:
            self.settings = {}
            self.save()

    def save(self):
        with SETTINGS_FILE.open("w") as file:
            json.dump(
                self.settings,
                file,
                indent=4,
            )

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
