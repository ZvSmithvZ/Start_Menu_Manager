from dataclasses import dataclass
from enum import Enum


class StartFolder(Enum):
    COMMON = "common"  # example C:\ProgramData\Microsoft\Windows\Start Menu\Programs
    USER = "user"  # example  C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs


@dataclass
class Shortcut:
    uuid: str
    name: str
    file_path: str
    extension: str
    target_path: str
    icon: str
    args: str
    is_broken: bool
    start_folder: StartFolder
    is_duplicate: bool
    is_selected: bool
