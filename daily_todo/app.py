#!/usr/bin/env python3
"""A small local daily task list for Ubuntu."""
import calendar
import json
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .positioning import valid_position, resolve_position
from .i18n import (
    MONTHS,
    SHORT_DAYS,
    display_date,
    load_language,
    save_language,
    translate,
)

# XWayland permits native GTK positioning on a Wayland desktop.
# Select the backend before GTK initializes its display connection.
if os.environ.get('DISPLAY'):
    os.environ['GDK_BACKEND'] = 'x11'

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Gio

HANOI = ZoneInfo('Asia/Ho_Chi_Minh')
RESOURCES = Path(__file__).resolve().parent / 'resources'


def hanoi_now():
    return datetime.now(HANOI)


DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'daily-todo/tasks.json'
POSITION = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'daily-todo/position.json'
SETTINGS = POSITION.with_name('settings.json')


class Todo(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='local.daily.todo')
        self.current_date = hanoi_now().date()
        self.day = self.current_date.isoformat()
        self.tasks = {}
        self.window = None
        self.month = self.current_date.replace(day=1)
        self.moving = False
        self.language = load_language(SETTINGS)
        self.position_hint_key = 'pinned'
        self.translated_widgets = []
        self.desktop_mode = False
        self.position_source = None
        self.locked_position = None
        self.saved_position = None
        try:
            saved = json.loads(POSITION.read_text())
            if valid_position(saved):
                self.saved_position = saved
        except (OSError, ValueError):
            pass

    def do_activate(self):
        if self.window:
            if not self.desktop_mode:
                self.window.present()
            return
        self.desktop_mode = self.desktop_available()
        try:
            self.tasks = json.loads(DATA.read_text()) if DATA.exists() else {}
            if not isinstance(self.tasks, dict) or any(
                not isinstance(items, list) or any(
                    not isinstance(t, dict) or not isinstance(t.get('id'), str)
                    or not isinstance(t.get('text'), str) or not isinstance(t.get('done'), bool)
                    for t in items
                ) for items in self.tasks.values()
            ):
                raise ValueError(self.tr('invalid'))
        except (OSError, ValueError) as exc:
            dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE, text=self.tr('read_error'))
            dialog.format_secondary_text(f'{DATA}\n{exc}\n{self.tr("preserved")}')
            dialog.run()
            dialog.destroy()
            self.quit()
            return
        self.build_window()

    def desktop_available(self):
        try:
            result = Gio.bus_get_sync(Gio.BusType.SESSION, None).call_sync(
                'org.gnome.Shell', '/org/gnome/Shell/Extensions/DailyTodoDesktop',
                'local.daily.todo.Desktop', 'Ready', None, GLib.VariantType.new('(b)'),
                Gio.DBusCallFlags.NONE, 500, None)
            return result.unpack()[0]
        except GLib.Error:
            return False

    def refresh_desktop_mode(self):
        available = self.desktop_available()
        if available != self.desktop_mode:
            self.desktop_mode = available
            self.window.set_skip_taskbar_hint(True)
            self.window.set_skip_pager_hint(True)
            self.window.set_focus_on_map(not available)
            self.refresh_desktop_status()
        return GLib.SOURCE_CONTINUE

    def build_window(self):
        self.window = Gtk.ApplicationWindow(application=self, title='Việc mỗi ngày')
        self.window.set_default_size(980, 650)
        self.window.set_resizable(False)
        self.window.set_decorated(False)
        # Keep the normal stacking layer: both DESKTOP and BELOW can put an
        # XWayland window behind Desktop Icons NG's transparent input surface.
        self.window.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.window.set_accept_focus(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_focus_on_map(not self.desktop_mode)
        self.window.stick()
        self.window.set_keep_above(False)
        self.window.set_keep_below(False)
        self.window.connect('configure-event', self.enforce_position)
        provider = Gtk.CssProvider()
        provider.load_from_path(str(RESOURCES / 'style.css'))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin=20)
        self.window.add(box)
        header = Gtk.Box(spacing=12)
        header.pack_start(Gtk.Image.new_from_file(str(RESOURCES / 'robotics-mark.svg')), False, False, 0)
        title = Gtk.Label(label='✦  Việc mỗi ngày', xalign=0)
        self.title = title
        title.get_style_context().add_class('brand')
        drag_area = Gtk.EventBox()
        brand = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        eyebrow = Gtk.Label(xalign=0)
        eyebrow.get_style_context().add_class('eyebrow')
        self.translated_widgets.append((eyebrow, 'set_text', 'eyebrow'))
        brand.pack_start(eyebrow, False, False, 0)
        brand.pack_start(title, False, False, 0)
        drag_area.add(brand)
        drag_area.connect('button-press-event', self.drag_window)
        header.pack_start(drag_area, True, True, 0)
        self.pin_button = Gtk.Button(label='Di chuyển')
        self.pin_button.connect('clicked', self.toggle_position)
        header.pack_start(self.pin_button, False, False, 0)
        self.language_button = Gtk.ComboBoxText()
        self.language_button.append('vi', 'VI · Tiếng Việt')
        self.language_button.append('en', 'EN · English')
        self.language_button.set_active_id(self.language)
        self.language_button.connect('changed', self.change_language)
        header.pack_start(self.language_button, False, False, 0)
        close = Gtk.Button(label='×')
        close.get_style_context().add_class('close-button')
        close.set_tooltip_text('Đóng ứng dụng')
        self.translated_widgets.append((close, 'set_tooltip_text', 'close'))
        close.connect('clicked', lambda _button: self.window.close())
        header.pack_end(close, False, False, 0)
        box.pack_start(header, False, False, 0)
        metadata = Gtk.Box(spacing=12)
        box.pack_start(metadata, False, False, 0)
        self.desktop_status = Gtk.Label(xalign=1)
        self.desktop_status.get_style_context().add_class('muted')
        self.position_hint = Gtk.Label(label='Đã ghim · Nhấn Di chuyển để chọn vị trí khác', xalign=0)
        self.position_hint.get_style_context().add_class('muted')
        self.clock = Gtk.Label(xalign=0)
        self.clock.get_style_context().add_class('clock')
        metadata.pack_start(self.clock, True, True, 0)
        metadata.pack_end(self.desktop_status, False, False, 0)
        body = Gtk.Box(spacing=14)
        box.pack_start(body, True, True, 0)
        self.calendar_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.calendar_panel.get_style_context().add_class('panel')
        body.pack_start(self.calendar_panel, True, True, 0)
        navigation = Gtk.Box(spacing=8)
        self.month_title = Gtk.Label(xalign=0)
        self.month_title.get_style_context().add_class('heading')
        navigation.pack_start(self.month_title, True, True, 0)
        for caption, delta in [('‹', -1), ('›', 1)]:
            button = Gtk.Button(label=caption)
            button.set_tooltip_text('Tháng trước' if delta < 0 else 'Tháng sau')
            self.translated_widgets.append((button, 'set_tooltip_text', 'previous' if delta < 0 else 'next'))
            button.connect('clicked', self.change_month, delta)
            navigation.pack_start(button, False, False, 0)
        self.calendar_panel.pack_start(navigation, False, False, 0)
        self.calendar_grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True)
        self.calendar_panel.pack_start(self.calendar_grid, True, True, 0)
        legend = Gtk.Label(label='● Hôm nay    ·    Chọn một ngày để lên kế hoạch', xalign=0)
        self.translated_widgets.append((legend, 'set_text', 'legend'))
        legend.get_style_context().add_class('muted')
        self.calendar_panel.pack_start(legend, False, False, 0)
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        sidebar.get_style_context().add_class('panel')
        sidebar.set_size_request(310, -1)
        body.pack_start(sidebar, False, False, 0)
        task_header = Gtk.Box(spacing=10)
        task_title = Gtk.Label(xalign=0)
        task_title.get_style_context().add_class('eyebrow')
        self.translated_widgets.append((task_title, 'set_text', 'task_heading'))
        task_header.pack_start(task_title, True, True, 0)
        today = Gtk.Button(label='Về hôm nay')
        today.get_style_context().add_class('quiet-button')
        self.translated_widgets.append((today, 'set_label', 'today'))
        today.connect('clicked', self.today)
        task_header.pack_end(today, False, False, 0)
        sidebar.pack_start(task_header, False, False, 0)
        self.selected_date = Gtk.Label(xalign=0)
        self.selected_date.get_style_context().add_class('selected-date')
        sidebar.pack_start(self.selected_date, False, False, 0)
        self.status = Gtk.Label(xalign=0)
        self.status.get_style_context().add_class('muted')
        sidebar.pack_start(self.status, False, False, 0)
        self.progress = Gtk.ProgressBar()
        sidebar.pack_start(self.progress, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.rows = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scroll.add(self.rows)
        sidebar.pack_start(scroll, True, True, 0)
        entry_row = Gtk.Box(spacing=6)
        self.entry = Gtk.Entry(placeholder_text='Thêm việc cần làm…', max_length=500)
        self.entry.connect('activate', self.add_task)
        add = Gtk.Button(label='Thêm')
        self.translated_widgets.append((add, 'set_label', 'add'))
        add.get_style_context().add_class('primary')
        add.connect('clicked', self.add_task)
        entry_row.pack_start(self.entry, True, True, 0)
        entry_row.pack_start(add, False, False, 0)
        sidebar.pack_start(entry_row, False, False, 0)
        footer = Gtk.Box(spacing=12)
        footer.pack_start(self.position_hint, True, True, 0)
        keyboard_hint = Gtk.Label(xalign=1)
        keyboard_hint.get_style_context().add_class('muted')
        self.translated_widgets.append((keyboard_hint, 'set_text', 'keyboard_hint'))
        footer.pack_end(keyboard_hint, False, False, 0)
        box.pack_start(footer, False, False, 0)
        self.refresh_language()
        self.clock_source = GLib.timeout_add_seconds(1, self.update_clock)
        self.desktop_source = GLib.timeout_add_seconds(5, self.refresh_desktop_mode)
        self.window.show_all()
        self.window.unmaximize()
        if not self.desktop_mode:
            self.window.present()
        self.position_source = GLib.timeout_add(200, self.restore_position)
        self.screen = self.window.get_screen()
        self.monitor_signal = self.screen.connect('monitors-changed', self.monitors_changed)

    def tr(self, key, **values):
        return translate(self.language, key, **values)

    def refresh_desktop_status(self):
        self.desktop_status.set_text(self.tr('desktop_badge_ready' if self.desktop_mode else 'desktop_badge_pending'))
        self.desktop_status.set_tooltip_text(self.tr('desktop_ready' if self.desktop_mode else 'desktop_pending'))

    def change_language(self, combo):
        language = combo.get_active_id()
        if language == self.language:
            return
        try:
            save_language(SETTINGS, language)
        except OSError as exc:
            combo.set_active_id(self.language)
            self.position_hint.set_text(self.tr('language_error', error=exc))
            return
        self.language = language
        self.refresh_language()

    def refresh_language(self):
        self.window.set_title(self.tr('title'))
        self.title.set_text(self.tr('title'))
        self.pin_button.set_label(self.tr('pin' if self.moving else 'move'))
        self.position_hint.set_text(self.tr(self.position_hint_key))
        self.language_button.set_tooltip_text(self.tr('language_tip'))
        self.refresh_desktop_status()
        self.entry.set_placeholder_text(self.tr('placeholder'))
        for widget, setter, key in self.translated_widgets:
            getattr(widget, setter)(self.tr(key))
        self.update_clock()
        self.render()

    def monitors_changed(self, _screen):
        if self.position_source:
            GLib.source_remove(self.position_source)
        self.position_source = GLib.timeout_add(200, self.restore_position)

    def restore_position(self):
        self.position_source = None
        if self.moving:
            return GLib.SOURCE_REMOVE
        display = self.window.get_display()
        monitors = [display.get_monitor(i) for i in range(display.get_n_monitors())]
        if not monitors:
            return GLib.SOURCE_REMOVE
        primary = display.get_primary_monitor()
        primary_index = monitors.index(primary) if primary in monitors else 0
        areas = []
        for monitor in monitors:
            area = monitor.get_workarea()
            areas.append((area.x, area.y, area.width, area.height))
        self.locked_position = resolve_position(self.saved_position, areas, primary_index, self.window.get_size())
        self.window.move(*self.locked_position)
        self.window.set_keep_above(False)
        self.window.set_keep_below(False)
        self.window.stick()
        return GLib.SOURCE_REMOVE

    def enforce_position(self, _window, event):
        if (not self.moving and self.locked_position is not None
                and (event.x, event.y) != self.locked_position and not self.position_source):
            self.position_source = GLib.idle_add(self.restore_position)
        return False

    def drag_window(self, _widget, event):
        if self.moving and event.button == 1:
            self.window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def toggle_position(self, _button):
        if self.moving:
            display = self.window.get_display()
            monitor = display.get_monitor_at_window(self.window.get_window())
            area = monitor.get_workarea()
            x, y = self.window.get_position()
            index = next(i for i in range(display.get_n_monitors()) if display.get_monitor(i) == monitor)
            saved = dict(monitor=index, x=x - area.x, y=y - area.y)
            try:
                POSITION.parent.mkdir(parents=True, exist_ok=True)
                temp = POSITION.with_suffix('.tmp')
                temp.write_text(json.dumps(saved))
                temp.replace(POSITION)
            except OSError as exc:
                self.position_hint.set_text(self.tr('position_error', error=exc))
                return
            self.saved_position = saved
            self.locked_position = (x, y)
        self.moving = not self.moving
        self.position_hint_key = 'moving' if self.moving else 'position_saved'
        self.pin_button.set_label(self.tr('pin' if self.moving else 'move'))
        self.position_hint.set_text(self.tr(self.position_hint_key))

    def do_shutdown(self):
        if hasattr(self, 'desktop_source'):
            GLib.source_remove(self.desktop_source)
        if self.position_source:
            GLib.source_remove(self.position_source)
        if hasattr(self, 'monitor_signal'):
            self.screen.disconnect(self.monitor_signal)
        if hasattr(self, 'clock_source'):
            GLib.source_remove(self.clock_source)
        Gtk.Application.do_shutdown(self)

    def update_clock(self):
        now = hanoi_now()
        self.clock.set_text(f'{display_date(now.date(), self.language)}   /   {now:%H:%M:%S}   /   {self.tr("timezone")}')
        if now.date() != self.current_date:
            follow_today = self.day == self.current_date.isoformat()
            self.current_date = now.date()
            if follow_today:
                self.today(None)
            else:
                self.render_calendar()
        return GLib.SOURCE_CONTINUE

    def save(self):
        try:
            DATA.parent.mkdir(parents=True, exist_ok=True)
            temp = DATA.with_suffix('.tmp')
            temp.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2))
            temp.replace(DATA)
        except OSError as exc:
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True,
                message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE,
                text=self.tr('save_error'))
            dialog.format_secondary_text(str(exc))
            dialog.run()
            dialog.destroy()

    def select_day(self, _button, selected):
        self.day = selected.isoformat()
        self.month = selected.replace(day=1)
        self.render()

    def change_month(self, _button, delta):
        index = self.month.year * 12 + self.month.month - 1 + delta
        year, month = divmod(index, 12)
        if 1 <= year <= 9999:
            self.month = date(year, month + 1, 1)
            self.render_calendar()

    def render_calendar(self):
        self.month_title.set_text(self.tr('month', month=self.month.month, year=self.month.year,
            month_name=MONTHS[self.month.month - 1]))
        for child in self.calendar_grid.get_children():
            self.calendar_grid.remove(child)
        for col, name in enumerate(SHORT_DAYS[self.language]):
            label = Gtk.Label(label=name)
            label.set_size_request(-1, 22)
            label.get_style_context().add_class('muted')
            self.calendar_grid.attach(label, col, 0, 1, 1)
        for row, week in enumerate(calendar.Calendar().monthdayscalendar(self.month.year, self.month.month), 1):
            for col, number in enumerate(week):
                if not number:
                    continue
                selected = self.month.replace(day=number)
                tasks = self.tasks.get(selected.isoformat(), [])
                remaining = sum(not task['done'] for task in tasks)
                button = Gtk.Button()
                button.set_hexpand(True)
                button.set_vexpand(True)
                button.get_style_context().add_class('day')
                if selected == self.current_date:
                    button.get_style_context().add_class('today')
                if selected.isoformat() == self.day:
                    button.get_style_context().add_class('selected')
                if col >= 5:
                    button.get_style_context().add_class('weekend')
                contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=4)
                number_label = Gtk.Label(label=f'{number:02d}', xalign=0)
                number_label.get_style_context().add_class('day-number')
                contents.pack_start(number_label, False, False, 0)
                summary = self.tr('tasks', count=remaining) if remaining else (self.tr('done') if tasks else '—')
                hint = Gtk.Label(label=summary, xalign=0)
                hint.get_style_context().add_class('day-summary')
                contents.pack_start(hint, False, False, 0)
                button.add(contents)
                button.set_tooltip_text(display_date(selected, self.language) + ('\n' + '\n'.join(t['text'] for t in tasks[:5]) if tasks else ''))
                button.connect('clicked', self.select_day, selected)
                self.calendar_grid.attach(button, col, row, 1, 1)
        self.calendar_grid.show_all()

    def today(self, _button):
        now = hanoi_now().date()
        self.month = now.replace(day=1)
        self.day = now.isoformat()
        self.render()

    def add_task(self, _widget):
        text = self.entry.get_text().strip()
        if text:
            self.tasks.setdefault(self.day, []).append(dict(id=uuid.uuid4().hex, text=text, done=False))
            self.save()
            self.entry.set_text('')
            self.render()

    def toggle(self, button, task):
        task['done'] = button.get_active()
        self.save()
        self.render()

    def remove(self, _button, task):
        self.tasks[self.day].remove(task)
        self.save()
        self.render()

    def render(self):
        self.render_calendar()
        for child in self.rows.get_children():
            self.rows.remove(child)
        items = self.tasks.get(self.day, [])
        completed = sum(t['done'] for t in items)
        self.progress.set_fraction(completed / len(items) if items else 0)
        self.selected_date.set_text(display_date(date.fromisoformat(self.day), self.language))
        self.status.set_text(self.tr('progress', done=completed, total=len(items)))
        if not items:
            empty = Gtk.Label(label=self.tr('empty'), margin=12)
            empty.set_justify(Gtk.Justification.CENTER)
            empty.get_style_context().add_class('muted')
            empty.get_style_context().add_class('empty-state')
            self.rows.add(empty)
        for task in items:
            row = Gtk.Box(spacing=6, margin=4)
            check = Gtk.CheckButton()
            check.set_active(task['done'])
            check.connect('toggled', self.toggle, task)
            label = Gtk.Label(xalign=0, wrap=True, max_width_chars=25)
            text = GLib.markup_escape_text(task['text'])
            label.set_markup(f'<s>{text}</s>' if task['done'] else text)
            if task['done']:
                label.get_style_context().add_class('muted')
            delete = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
            delete.get_style_context().add_class('delete-button')
            delete.set_tooltip_text(self.tr('delete'))
            delete.connect('clicked', self.remove, task)
            row.pack_start(check, False, False, 0)
            row.pack_start(label, True, True, 0)
            row.pack_start(delete, False, False, 0)
            self.rows.add(row)
        self.rows.show_all()
