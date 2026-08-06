# Start Menu Manager

A desktop application for cleaning up and organizing the Windows Start Menu.

Start Menu Manager scans both Windows Start Menu locations, detects duplicate and broken shortcuts, and provides a fast, spreadsheet-style interface for managing them. Instead of digging through hidden folders in File Explorer, you can organize everything from a single window.

## Features

* 🔍 Scan both Windows Start Menu directories
* ⚠️ Detect duplicate shortcuts
* ❌ Find broken shortcuts that point to missing files
* 📊 Sort by multiple columns to quickly locate entries
* ✏️ Edit shortcut properties
* 🗑️ Delete unwanted shortcuts
* 💾 Backup Start Menu shortcuts before making changes
* 📥 Import previously created backups
* ⚡ Fast table interface for managing hundreds of shortcuts

## Preview

### Search bar and header sorting
![Search bar and sorting demo](images/search_bar_sorting.gif)


### Filters to show duplicate shortcuts, broken shortcuts, and system shortcuts
![Duplicates, broken, and system shortcuts filters](images/filter_duplicates_broken_sys.gif)


### Responsive settings to auto-fit column data
![Duplicates, broken, and system shortcuts filters](images/auto_resize_columns_to_window.gif)


### Simple UI for Start Menu shortcut editing and settings
![Shortcut UI editor](images/editing_shortcut_UI_and_settings.gif)


## Why I Built This

Managing the Windows Start Menu usually requires navigating multiple hidden system folders and manually searching for shortcuts. There is no built-in way to quickly identify duplicates or broken entries.

This project was created to provide a simple interface that makes Start Menu maintenance significantly faster and easier.

## Tech Stack

* Python
* PyQt6
* Windows Shortcut (.lnk) APIs
* JSON settings
* Object-oriented architecture

## Installation

```bash
git git clone https://github.com/ZvSmithvZ/Start_Menu_Manager.git
cd Start_Menu_Manager
pip install -r requirements.txt
```

## Running
```bash
python main.py
```

## Future Plans

* Full settings menu 
* Batch editing
* Improved backup management
* Startup shortcuts management

## License

This project is licensed under the MIT License.
