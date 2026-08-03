import win32com.client


class ShortcutWriter:

    def update_shortcut(self, shortcut):
        shell = win32com.client.Dispatch("WScript.Shell")

        link = shell.CreateShortcut(shortcut.file_path)

        link.TargetPath = shortcut.target_path
        link.Arguments = shortcut.args
        link.WorkingDirectory = shortcut.working_directory

        link.Save()
