<p align="center">
  <img src="daily_todo/resources/robotics-mark.svg" width="72" height="72" alt="Daily To-do robotics logo">
</p>

<h1 align="center">Daily To-do</h1>

<p align="center">
  A calendar and daily task list for your Ubuntu desktop.<br>
  Robotics-inspired design · English and Vietnamese · Local storage
</p>

Plan your day, organize upcoming tasks, and track completed work in a desktop panel with a graphite, cyan, and mint color palette. Daily To-do stores your tasks locally and works without an account.

## Features

- Monthly calendar with a separate task list for each day.
- A read-only Tomorrow column beside Daily Tasks previews the next day's tasks, time ranges, and completion progress.
- Weekly recurring tasks with start/end times and independent completion for each date.
- Add, delete, and complete tasks. Calendar days show completion percentages with a bottom-up color fill: 50% fills half the cell, and 100% fills it completely. Days without tasks show a dash.
- Completion progress and task previews when hovering over calendar days.
- Calendar completion levels animate smoothly over 450 ms, with subtle hover transitions on controls. Water animation follows GTK's system animation setting.
- Partially completed days have two gentle animated waves, and fully completed days show a check mark. Completing a task briefly highlights its row and fades its text. Motion effects follow GTK's animation setting; wave updates pause when the calendar is not mapped.
- Switch between English and Vietnamese; your language preference is saved.
- Choose Cyan, Mint, Blue, Purple, Rose, or Amber from the color selector in the footer. Colors update immediately and your choice is saved.
- Adjust **Background** in the footer from 0 (transparent surfaces) to 100 (solid surfaces). The default is 35; text and controls remain opaque. Transparency requires desktop compositing and an RGBA visual.
- Live clock using Hanoi time (UTC+7).
- When viewing today, automatically follow the new date after midnight or waking the computer.
- Move the panel and save its position with **Layout → drag the app title or resize → Save layout**.
- Optional automatic startup after signing in.
- Bundled GNOME extension keeps the panel behind application windows while allowing mouse input on the desktop.
- Hidden from the dock and Alt+Tab.
- Local JSON storage with no cloud synchronization.

## Requirements

| Component | Requirement |
| --- | --- |
| Target desktop | Ubuntu Desktop 24.04 with GNOME Shell 46 |
| Python | System Python 3.9 or later |
| Interface | GTK 3 and PyGObject |
| Wayland sessions | XWayland and an available `DISPLAY` environment variable |
| Desktop integration | Bundled extension, currently declaring support for GNOME Shell 46 |
| Panel size | Default 1300 × 650; adjustable through Layout, with scrolling for smaller windows |

Other GNOME versions, desktop environments, Windows, and macOS are not confirmed supported. Without the GNOME extension, the interface can run as a regular window, but full desktop pinning is unavailable.

The app runs from source. There is currently no `.deb` or AppImage package.

## Installation

### 1. Download the source

```bash
git clone https://github.com/phuctrung-nguyen/2tolist-ubuntu.git
cd 2tolist-ubuntu
```

Alternatively, select **Code → Download ZIP** on GitHub, extract it, and open a terminal in the folder containing `app.py`.

Keep the source in a permanent location. The desktop launcher stores its absolute path.

### 2. Install system dependencies

On Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 xwayland tzdata
```

Check that GTK is available:

```bash
/usr/bin/python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK', Gtk.MAJOR_VERSION)"
```

Use **`/usr/bin/python3`** for the commands below. Conda or virtual environment interpreters may not find the PyGObject packages installed through apt. This installation method does not require `pip install` or a virtual environment.

### 3. Run the app

From the project directory:

```bash
/usr/bin/python3 app.py
```

You can also run it as a Python package:

```bash
/usr/bin/python3 -m daily_todo
```

Select **EN · English** at the top of the panel to switch the interface to English.

### 4. Enable desktop integration and automatic startup

Check your GNOME version:

```bash
gnome-shell --version
```

For **GNOME Shell 46**, run:

```bash
/usr/bin/python3 setup.py --autostart --corner
```

Save any open work, then **sign out and sign back in once** so GNOME can load the newly installed extension.

To also place a clickable calendar icon on your desktop, run `/usr/bin/python3 setup.py --autostart --corner --desktop-shortcut`. The launcher is named **2DO** and uses a bundled calendar icon. If Ubuntu asks, right-click the desktop shortcut and select **Allow Launching**. The app opens automatically after signing in and restores its saved layout. Clicking the launcher reuses the running app or starts it if closed. Desktop integration keeps it behind other application windows.

The installer creates an application launcher named **2DO**, enables startup after signing in, and installs the `daily-todo-desktop@local` extension. It also removes the older `daily-todo-corner@local` extension from the enabled list if present.

Run the installer as your normal user, **without sudo**. If you move or rename the source folder, run setup again from its new location.

| Command | Result |
| --- | --- |
| `/usr/bin/python3 setup.py` | Install the application launcher |
| `/usr/bin/python3 setup.py --autostart` | Install the launcher and enable login startup |
| `/usr/bin/python3 setup.py --corner` | Install the launcher and GNOME integration |
| `/usr/bin/python3 setup.py --autostart --corner` | Install all of the above |

## Usage

| Action | How to do it |
| --- | --- |
| Add a task | Select a date, enter a task, then press **Enter** or click **Add** |
| Complete a task | Click its checkbox |
| Delete a task | Click the trash icon beside it |
| Edit a task | Double-click its text, change it, then press Enter or click **Save**. **Cancel** keeps the original text. |
| Browse months | Use **‹ / ›** |
| Return to the current date | Click **Go to today** |
| Change the interface language | Select **EN · English** or the Vietnamese option in the language selector |
| Set up a fixed weekly schedule | Click **Recurring tasks**, enter a name and a 24-hour time range, select weekdays, then click **Save schedule** |
| Move or resize the panel | Click **Layout**, drag the title to move, adjust **Width/Height** or drag **↘**, then click **Save layout** |
| Close the app | Click **×**; saved tasks remain on disk |
| Reopen the app | Find **2DO** in the application list or run `/usr/bin/python3 app.py` |

When integration is active, the status badge reads **Desktop pinned**. The panel appears across workspaces behind application windows. Interact with it through an uncovered area of the desktop.

Automatic startup runs after you sign in to your desktop session. Closing the panel does not immediately reopen it; use the launcher or wait until your next sign-in.

Recurring schedules start on the day you create them and follow the app's Hanoi time zone. Their tasks appear automatically on matching dates, sorted by start time. Completing or deleting an occurrence affects that date only. Use **Edit** in the schedule dialog to change a schedule, or its trash button to stop repeating it. Previously saved daily records remain unchanged. Time ranges must end later on the same day; overnight ranges and notifications are not supported.

## Customization

Restart the app after changing source files or styles.

| Setting | File or location |
| --- | --- |
| Colors, fonts, borders, and spacing | [style.css](daily_todo/resources/style.css) |
| Robotics icon | [robotics-mark.svg](daily_todo/resources/robotics-mark.svg) |
| Interface text | `TEXT` in [i18n.py](daily_todo/i18n.py) |
| Window size | `self.window.set_default_size(1300, 650)` in [app.py](daily_todo/app.py) |
| Calendar and task layout | `build_window()` in [app.py](daily_todo/app.py) |
| Time zone | `HANOI = ZoneInfo(...)` in [app.py](daily_todo/app.py) |
| Monitor positioning | [positioning.py](daily_todo/positioning.py) |
| Desktop window stacking | [extension.js](integrations/gnome-shell/extension.js) |

For example, change the Add button and selected date colors in `daily_todo/resources/style.css`:

```css
button.primary {
    background-color: #91dfbf;
    border-color: #91dfbf;
    color: #08251b;
}

button.day.selected {
    background-color: #203b34;
    border-color: #91dfbf;
}
```

The app uses GTK CSS, which supports a different set of properties from browser CSS.

To use another time zone, change the `HANOI` constant, for example:

```python
HANOI = ZoneInfo('Asia/Tokyo')
```

Also update the `timezone` label in both languages in `daily_todo/i18n.py`. The new zone affects the clock and calendar; existing tasks keep their saved dates.

After editing the GNOME extension, rerun `/usr/bin/python3 setup.py --corner`, then sign out and back in. Changing only `shell-version` in the extension metadata does not establish compatibility with another GNOME release.

## Data and backups

| Content | Default location |
| --- | --- |
| Daily tasks | `~/.local/share/daily-todo/tasks.json` |
| Recurring schedules | `~/.local/share/daily-todo/routines.json` |
| Saved panel position and size | `~/.config/daily-todo/position.json` |
| Language preference | `~/.config/daily-todo/settings.json` |
| Color preference | `~/.config/daily-todo/theme.json` |
| Background opacity | `~/.config/daily-todo/appearance.json` |
| Login startup entry | `~/.config/autostart/daily-todo.desktop` |
| Application launcher | `~/.local/share/applications/local.daily.todo.desktop` |
| GNOME extension | `~/.local/share/gnome-shell/extensions/daily-todo-desktop@local/` |

If `XDG_DATA_HOME` or `XDG_CONFIG_HOME` is set, the app uses those directories instead of the corresponding defaults.

Tasks are saved when you add, delete, or complete them. Text still in the input field is not saved until you press Enter or click Add.

To back up or move your data, close the app and copy the `daily-todo` data and configuration directories to a safe location. On another computer, install the source and dependencies, then restore the files to the corresponding directories.

## Updating

1. Close the app.
2. Run `git pull` in the project directory, or replace the source files if you downloaded a ZIP.
3. Rerun `/usr/bin/python3 setup.py --autostart --corner` if you use the full installation.
4. Sign out and back in if the extension changed.

Personal data is stored outside the source folder. Save any custom source or CSS changes before updating.

## Troubleshooting

### Python cannot import `gi`, or GTK is missing

Install the system dependencies above and run the app with `/usr/bin/python3`. A Conda or virtual environment interpreter may not see apt-installed packages.

### The panel is not pinned to the desktop

Check that you are using GNOME Shell 46, rerun setup with `--autostart --corner`, and sign out and back in. If user extensions are globally disabled, enable them in the **Extensions** app.

Inspect the extension with:

```bash
gnome-extensions info daily-todo-desktop@local
```

### The app does not appear in the dock or Alt+Tab

This is intentional. Return to the desktop or find **2DO** in the application list. In desktop mode, launching the app again does not bring the panel above your other applications.

### The panel does not respond to mouse input

Check whether another window covers it. Avoid manually enabling **Always on Top** or **Always on Bottom**, because the GNOME integration manages its stacking position. If the problem persists, include your GNOME version and extension status in a bug report.

### The panel is too large or clipped

The default size is 1300 × 650. Click **Layout** to change the window dimensions (minimum 640 × 420), then **Save layout** to remember its size and position. Smaller windows provide scrolling to keep all three columns accessible.

### The app does not start automatically

Check the autostart file and its source path. If you moved the project folder, rerun setup. Startup happens after signing in to a desktop session.

## Disabling startup and uninstalling

Close the app first. To disable automatic startup, remove `daily-todo.desktop` from your account's autostart directory listed above.

Disable the GNOME integration with:

```bash
gnome-extensions disable daily-todo-desktop@local
```

Then remove the application launcher, autostart entry, and extension directory listed in the data table. You can also delete the source folder.

Task data and preferences remain available for backup or reinstallation. Remove their directories separately if you want to delete your personal data.

## Project structure

```text
.
├── daily_todo/
│   ├── __init__.py
│   ├── __main__.py               # Package entry point
│   ├── app.py                    # Interface and task management
│   ├── i18n.py                   # English and Vietnamese translations
│   ├── positioning.py            # Monitor coordinates and work areas
│   └── resources/
│       ├── style.css
│       └── robotics-mark.svg
├── integrations/
│   └── gnome-shell/
│       ├── extension.js
│       └── metadata.json
├── scripts/
│   └── install.py                # Launcher, startup, and extension installer
├── tests/                        # Unit tests and desktop smoke tests
├── app.py                        # Compatibility entry point
├── setup.py                      # Compatibility installer entry point
├── .gitignore
└── README.md
```

## Development checks

Run the unit tests without interacting with the desktop:

```bash
/usr/bin/python3 -m unittest discover -s tests
```

Run these integration checks separately in a suitable desktop environment:

- `/usr/bin/python3 tests/gui_input_smoke.py` opens a test window, uses real mouse and keyboard input, and restores the pointer position afterward.
- `/usr/bin/python3 tests/gnome_stack_smoke.py` creates a separate headless GNOME session to check window stacking. It requires GNOME Shell, D-Bus, and a compatible graphics environment.

These checks use separate temporary data. They cover input behavior and sample-window stacking, and do not replace testing on real desktop configurations.

## Current limitations

- No notifications, cloud sync, or dragging tasks between dates.
- Editing a recurring task in Daily Tasks changes only that date; use **Recurring tasks** to update the repeating schedule.
- Unfinished tasks do not automatically move to the next day.
- When viewing another date, the app keeps that date selected; click **Go to today** to return.
- Time zone and window size are configured in source rather than a settings screen.
- The GNOME extension currently targets Shell 46; other versions need compatibility testing.
- **Show Desktop / Super+D** behavior can depend on GNOME and other extensions and has not been confirmed across all configurations.

## Contributing

Open an issue to report a bug or suggest a feature. Include your Ubuntu and GNOME versions, session type (X11 or Wayland), reproduction steps, and any terminal errors. Avoid attaching personal task data unless necessary.

For pull requests, describe the change and how you verified it. Check interface changes in both English and Vietnamese.

## License

This repository does not currently include a `LICENSE` file. The repository owner can add one to specify terms for using, modifying, and distributing the source.
