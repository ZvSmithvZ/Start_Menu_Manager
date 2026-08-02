# from models.shortcut import Shortcut
from pathlib import Path

from models.shortcut import StartFolder


class ShortcutScanner:
    COMMON_START_MENU = Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs")

    USER_START_MENU = (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
    )

    def scan_common_start_menu(self) -> list[tuple[Path, StartFolder]]:
        return [
            (path, StartFolder.COMMON) for path in self.COMMON_START_MENU.rglob("*lnk")
        ]

    def scan_user_start_menu(self) -> list[tuple[Path, StartFolder]]:

        return [(path, StartFolder.USER) for path in self.USER_START_MENU.rglob("*lnk")]

    def scan_all_start_menus(self) -> list[tuple[Path, StartFolder]]:

        return self.scan_common_start_menu() + self.scan_user_start_menu()
