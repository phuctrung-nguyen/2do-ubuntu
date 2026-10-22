"""Run the desktop integration in an isolated, headless GNOME session.

Does not change the user's session, settings, or task data.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
UUID = 'daily-todo-desktop@local'


def run_inside():
    import gi
    from gi.repository import Gio, GLib
    settings = Gio.Settings.new('org.gnome.shell')
    settings.set_strv('enabled-extensions', [UUID])
    settings.set_boolean('disable-user-extensions', False)
    Gio.Settings.sync()
    log = open(Path(os.environ['XDG_CACHE_HOME']) / 'shell.log', 'w+')
    shell = subprocess.Popen(['gnome-shell', '--headless', '--wayland', '--sm-disable',
                              '--virtual-monitor=1280x900', '--wayland-display=daily-todo-test'],
                             stdout=log, stderr=log)
    clients = []
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def snapshot():
        value = bus.call_sync('org.gnome.Shell', '/org/gnome/Shell/Extensions/DailyTodoDesktop',
                              'local.daily.todo.Desktop', 'Snapshot', None, None,
                              Gio.DBusCallFlags.NONE, 500, None)
        return json.loads(value.unpack()[0])

    try:
        deadline = time.monotonic() + 18
        while True:
            try:
                snapshot()
                break
            except GLib.Error:
                if time.monotonic() > deadline or shell.poll() is not None:
                    raise RuntimeError('Isolated GNOME did not load the extension')
                time.sleep(.2)
        environment = dict(os.environ, WAYLAND_DISPLAY='daily-todo-test', GDK_BACKEND='wayland')
        environment.pop('DISPLAY', None)
        for title in ('Desktop fixture', 'Việc mỗi ngày', 'Normal application'):
            clients.append(subprocess.Popen([sys.executable, '-c', '''
import sys
sys.path.insert(0, sys.argv[1])
import gi
from gi.repository import GLib
GLib.set_prgname({'Desktop fixture': 'local.daily.fixture', 'Việc mỗi ngày': 'local.daily.todo', 'Normal application': 'local.daily.normal'}[sys.argv[2]])
from daily_todo import app
from gi.repository import Gtk, GLib, Gio
title = sys.argv[2]
window = Gtk.Window(title=title)
window.set_default_size(980 if title == 'Việc mỗi ngày' else 300, 650 if title == 'Việc mỗi ngày' else 200)
window.set_skip_taskbar_hint(title == 'Việc mỗi ngày')
window.show_all()
def raise_widget():
    window.present()
    return False
def minimize_widget():
    window.iconify()
    return False
if title == 'Việc mỗi ngày':
    GLib.timeout_add_seconds(2, raise_widget)
    GLib.timeout_add_seconds(4, minimize_widget)
Gtk.main()
''', str(ROOT), title], env=environment, stdout=log, stderr=log))
            time.sleep(.2)
        for attempt in range(60):
            time.sleep(.25)
            state = snapshot()
            titles = [row['title'] for row in state]
            if all(title in titles for title in ('Desktop fixture', 'Việc mỗi ngày', 'Normal application')) and all(row['mapped'] for row in state):
                break
        for _ in range(24):
            time.sleep(.25)
            state = snapshot()
            titles = [row['title'] for row in state]
            assert all(title in titles for title in ('Desktop fixture', 'Việc mỗi ngày', 'Normal application')), state
            assert titles.index('Desktop fixture') < titles.index('Việc mỗi ngày') < titles.index('Normal application'), state
            widget = next(row for row in state if row['title'] == 'Việc mỗi ngày')
            assert not widget['above'] and not widget['minimized'], state
        print('PASS: actual GNOME 46 extension loads; desktop < widget < normal app; raised widget is restacked; minimize restored')
    except Exception:
        log.flush(); log.seek(0)
        print(log.read()[-12000:], file=sys.stderr)
        raise
    finally:
        for process in [*clients, shell]:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
        log.close()


if '--inside' in sys.argv:
    run_inside()
else:
    with tempfile.TemporaryDirectory(prefix='todo-gnome-test-') as temporary:
        directory = Path(temporary)
        target = directory / 'data/gnome-shell/extensions' / UUID
        shutil.copytree(ROOT / 'integrations' / 'gnome-shell', target)
        source = (target / 'extension.js').read_text()
        # Test-only introspection and a mock desktop surface. Production exports
        # only Ready; it never enables Shell Eval or changes unsafe-mode.
        source = source.replace('<method name="Ready">', '<method name="Snapshot"><arg type="s" direction="out"/></method><method name="Ready">')
        source = source.replace('Ready() { return true; }', '''Ready() { return true; }
    Snapshot() {
        Main.overview.hide();
        const windows = global.display.list_all_windows();
        return JSON.stringify(global.display.sort_windows_by_stacking(windows).map(w => ({
            title: w.get_title(), above: w.above, minimized: w.minimized, skip: w.is_skip_taskbar(),
            todo: this._isTodo(w), desktop: this._isDesktop(w), app: w.get_wm_class(),
            mapped: w.get_compositor_private()?.mapped, workspace: w.get_workspace()?.index()
        })));
    }''')
        source = source.replace("window.get_gtk_application_id() === 'local.daily.todo'", "window.get_title() === 'Việc mỗi ngày'")
        source = source.replace('return window.get_window_type()', "return window.get_title() === 'Desktop fixture' || window.get_window_type()")
        (target / 'extension.js').write_text(source)
        environment = dict(os.environ, XDG_DATA_HOME=str(directory / 'data'),
                           XDG_CONFIG_HOME=str(directory / 'config'), XDG_CACHE_HOME=str(directory / 'cache'),
                           GSETTINGS_BACKEND='keyfile',
                           GNOME_SHELL_SESSION_MODE='user', XDG_CURRENT_DESKTOP='GNOME',
                           WAYLAND_DISPLAY='daily-todo-test', GIO_USE_VFS='local',
                           GTK_USE_PORTAL='0', NO_AT_BRIDGE='1', GTK_MODULES='')
        (directory / 'cache').mkdir()
        subprocess.run(['dbus-run-session', '--', sys.executable, str(Path(__file__).resolve()), '--inside'],
                       env=environment, check=True, timeout=40)
