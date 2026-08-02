from managers.shortcut_manager import ShortcutManager
from services.scanner import ShortcutScanner

# manager = ShortcutManager()
# manager.load_shortcuts()


scanner = ShortcutScanner()
manager = ShortcutManager()
# print(scanner.scan_user_start_menu())
# print("END OF USER")
# print(scanner.scan_common_start_menu())
# print("END of COMMON")
# print(scanner.scan_all_start_menus())

manager.load_shortcuts()
print(manager.find_duplicates())
