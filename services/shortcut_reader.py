from pathlib import Path

import win32com.client

from models.shortcut import Shortcut, StartFolder


class ShortcutReader:

    def read_shortcut(self, path: Path, start_folder: StartFolder) -> Shortcut:

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(path))
        return Shortcut(
            name=path.stem,
            file_path=str(path),
            extension=path.suffix,
            target_path=shortcut.TargetPath,
            icon=shortcut.IconLocation,
            args=shortcut.Arguments,
            is_broken=not Path(shortcut.TargetPath).exists(),
            start_folder=start_folder,
            is_duplicate=False,
            is_selected=False,
            is_windows_entry=shortcut.TargetPath.startswith(r"C:\Windows"),
            is_hidden=False,
        )
