from models.shortcut import Shortcut, StartFolder


class ShortcutSerializer:

    def serialize(self, shortcut: Shortcut) -> dict:
        return {
            "name": shortcut.name,
            "file_path": shortcut.file_path,
            "target_path": shortcut.target_path,
            "extension": shortcut.extension,
            "icon": shortcut.icon_path,
            "args": shortcut.args,
            "working_directory": shortcut.working_dir,
            "start_folder": shortcut.start_folder.value,
        }

    def deserialize(self, data: dict) -> Shortcut:
        return Shortcut(
            name=data["name"],
            file_path=data["file_path"],
            target_path=data["target_path"],
            extension=data["extension"],
            icon_path=data["icon"],
            args=data["args"],
            working_dir=data["working_directory"],
            is_broken=False,
            start_folder=StartFolder(data["start_folder"]),
            is_duplicate=False,
            is_selected=False,
            is_windows_entry=False,
            is_hidden=False,
        )
