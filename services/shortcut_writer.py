from pathlib import Path

import win32com.client


class ShortcutWriter:

    INVALID_CHARS = '<>:"/\\|?*'

    def update_shortcut(self, shortcut):
        shell = win32com.client.Dispatch("WScript.Shell")

        link = shell.CreateShortcut(shortcut.file_path)

        link.TargetPath = shortcut.target_path
        link.Arguments = shortcut.args

        if shortcut.icon_path:
            link.IconLocation = shortcut.icon_path

        if shortcut.working_dir:
            link.WorkingDirectory = shortcut.working_dir

        link.Save()

    def rename_shortcut(self, shortcut, new_name):

        new_name = new_name.removesuffix(".lnk")

        # Replace invalid filename characters
        for char in self.INVALID_CHARS:
            new_name = new_name.replace(char, "_")

        # Remove extra spaces at ends
        new_name = new_name.strip()

        old_path = Path(shortcut.file_path)

        new_path = old_path.with_name(f"{new_name}{old_path.suffix}")
        # Handle duplicate filenames
        counter = 1
        while new_path.exists():
            new_path = old_path.with_name(f"{new_name} ({counter}){old_path.suffix}")
            counter += 1

        old_path.rename(new_path)

        shortcut.file_path = str(new_path)
        shortcut.name = new_path.stem
