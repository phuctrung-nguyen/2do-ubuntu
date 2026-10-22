#!/usr/bin/env python3
"""Install launchers for the current user; optionally enable login startup."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def quote(value):
    """Quote a single Exec argument using the desktop-entry escape rules."""
    escaped = (
        str(value)
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('`', '\\`')
        .replace('$', '\\$')
        .replace('%', '%%')
    )
    return f'"{escaped}"'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--autostart', action='store_true', help='Tự chạy khi đăng nhập')
    parser.add_argument('--corner', action='store_true', help='Cài tích hợp desktop GNOME 46')
    parser.add_argument('--desktop-shortcut', action='store_true', help='Tạo biểu tượng lịch trên desktop')
    args = parser.parse_args()
    app = ROOT / 'app.py'
    data = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
    icon = data / 'icons/hicolor/scalable/apps/local.daily.todo.svg'
    icon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'daily_todo/resources/calendar.svg', icon)
    desktop = '\n'.join([
        '[Desktop Entry]', 'Type=Application', 'Name=2DO',
        'Comment=Daily calendar, tasks and recurring schedules',
        'Keywords=calendar;planner;tasks;todo;',
        f'Exec={quote(sys.executable)} {quote(app)}',
        f'Icon={icon}', 'Terminal=false', 'Categories=Office;Calendar;',
        'StartupNotify=false', 'StartupWMClass=local.daily.todo',
        'X-GNOME-Autostart-enabled=true', '',
    ])
    targets = [data / 'applications/local.daily.todo.desktop']
    if args.autostart:
        config = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
        targets.append(config / 'autostart/daily-todo.desktop')
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(desktop)
        print(f'Đã tạo: {target}')
    legacy = data / 'applications/daily-todo.desktop'
    if legacy.exists() and str(app) in legacy.read_text():
        legacy.unlink()
    if args.desktop_shortcut:
        result = subprocess.run(['xdg-user-dir', 'DESKTOP'], check=True, capture_output=True, text=True)
        directory = Path(result.stdout.strip())
        if not directory.is_absolute() or directory == Path.home():
            raise RuntimeError('Desktop folder is not configured; launcher and autostart were installed.')
        directory.mkdir(parents=True, exist_ok=True)
        shortcut = directory / 'daily-todo.desktop'
        shortcut.write_text(desktop)
        shortcut.chmod(0o755)
        trusted = subprocess.run(['gio', 'set', str(shortcut), 'metadata::trusted', 'true'],
                                 capture_output=True, text=True)
        print(f'Đã tạo biểu tượng lịch: {shortcut}')
        if trusted.returncode:
            print('Nếu cần, bấm chuột phải biểu tượng trên desktop → Allow Launching.')
    if args.corner:
        import gi
        from gi.repository import Gio
        settings = Gio.Settings.new('org.gnome.shell')
        uuid = 'daily-todo-desktop@local'
        target = data / 'gnome-shell/extensions' / uuid
        target.mkdir(parents=True, exist_ok=True)
        for name in ('metadata.json', 'extension.js'):
            shutil.copy2(ROOT / 'integrations' / 'gnome-shell' / name, target / name)
        enabled = list(settings.get_strv('enabled-extensions'))
        if 'daily-todo-corner@local' in enabled:
            enabled.remove('daily-todo-corner@local')
        if uuid not in enabled:
            enabled.append(uuid)
        if not settings.set_strv('enabled-extensions', enabled):
            raise RuntimeError('Không bật được tích hợp desktop GNOME')
        Gio.Settings.sync()
        print('Đã cài tích hợp desktop. Đăng xuất/đăng nhập một lần để GNOME nạp extension mới.')
        if settings.get_boolean('disable-user-extensions'):
            print('GNOME đang tắt toàn bộ extension; hãy bật lại trong ứng dụng Extensions.')


if __name__ == '__main__':
    main()
