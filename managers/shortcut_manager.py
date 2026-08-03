from services.scanner import ShortcutScanner
from services.shortcut_reader import ShortcutReader


class ShortcutManager:
    def __init__(self):
        self.shortcuts = []

    def add_shortcut(self, shortcut):
        self.shortcuts.append(shortcut)

    def load_shortcuts(self):
        self.shortcuts = []
        shortcut_path_scanner = ShortcutScanner()
        all_scanned_paths = shortcut_path_scanner.scan_all_start_menus()
        # all_scanned_paths = shortcut_path_scanner.scan_user_start_menu()
        shortcut_reader = ShortcutReader()
        for path, start_folder in all_scanned_paths:
            self.add_shortcut(shortcut_reader.read_shortcut(path, start_folder))
        return self.shortcuts

    def find_duplicates(self):
        shortcut_targets = {}
        possible_duplicates = {}
        for shortcut in self.shortcuts:
            shortcut.is_duplicate = False
            duplicate_key = (shortcut.target_path, shortcut.args)
            shortcut_targets.setdefault(duplicate_key, []).append(shortcut)

        for key, value in shortcut_targets.items():
            if len(value) > 1:

                possible_duplicates[key] = value

                for shortcut in value:
                    shortcut.is_duplicate = True
        return possible_duplicates
