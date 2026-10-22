#!/usr/bin/env python3
"""A small local daily task list for Ubuntu."""
import calendar
import json
import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .positioning import valid_position, resolve_position, saved_size
from .routines import daily_tasks, validate_routine
from .themes import THEMES, load_theme, save_theme, theme_css, load_opacity, save_opacity, background_css, completion_css
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
from gi.repository import Gtk, GLib, Gdk, Gio, GdkPixbuf

# Import GTK-based widgets only after choosing X11. Importing visuals above
# the backend selection initializes GTK on Wayland, where move/get_position
# cannot restore or save the actual desktop coordinates.
from .visuals import Water

HANOI = ZoneInfo('Asia/Ho_Chi_Minh')
RESOURCES = Path(__file__).resolve().parent / 'resources'


def hanoi_now():
    return datetime.now(HANOI)


DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'daily-todo/tasks.json'
POSITION = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'daily-todo/position.json'
SETTINGS = POSITION.with_name('settings.json')
THEME = POSITION.with_name('theme.json')
APPEARANCE = POSITION.with_name('appearance.json')
ROUTINES = DATA.with_name('routines.json')


class Todo(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='local.daily.todo')
        self.current_date = hanoi_now().date()
        self.day = self.current_date.isoformat()
        self.tasks = {}
        self.routines = []
        self.water_levels = {}
        self.water_source = None
        self.window = None
        self.month = self.current_date.replace(day=1)
        self.moving = False
        self.language = load_language(SETTINGS)
        self.theme = load_theme(THEME)
        self.background_opacity = load_opacity(APPEARANCE)
        self.position_hint_key = 'pinned'
        self.translated_widgets = []
        self.desktop_mode = False
        self.position_source = None
        self.startup_restore_source = None
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
            self.window.show_all()
            if not self.moving:
                self.restore_position()
            if not self.desktop_mode:
                self.window.present()
            return
        self.desktop_mode = self.desktop_available()
        try:
            self.routines = json.loads(ROUTINES.read_text()) if ROUTINES.exists() else []
            if not isinstance(self.routines, list):
                raise ValueError('Invalid recurring task data')
            for routine in self.routines:
                validate_routine(routine)
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
        self.window = Gtk.ApplicationWindow(application=self, title='2DO')
        self.window.set_icon_from_file(str(RESOURCES / 'calendar.svg'))
        visual = self.window.get_screen().get_rgba_visual()
        if visual is not None:
            self.window.set_visual(visual)
        self.window.set_default_size(*saved_size(self.saved_position))
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
        self.css_provider = Gtk.CssProvider()
        self.logo = Gtk.Image()
        self.apply_theme()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin=20)
        viewport = Gtk.ScrolledWindow()
        viewport.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        viewport.set_min_content_width(640)
        viewport.set_min_content_height(420)
        self.window.add(viewport)
        viewport.add(box)
        header = Gtk.Box(spacing=12)
        header.pack_start(self.logo, False, False, 0)
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
        self.layout_controls = Gtk.Revealer()
        self.layout_controls.set_no_show_all(True)
        layout_bar = Gtk.Box(spacing=10)
        self.layout_controls.add(layout_bar)
        for key, value, lower, upper in (
                ('layout_width', saved_size(self.saved_position)[0], 640, 7680),
                ('layout_height', saved_size(self.saved_position)[1], 420, 4320)):
            label = Gtk.Label()
            self.translated_widgets.append((label, 'set_text', key))
            layout_bar.pack_start(label, False, False, 0)
            spin = Gtk.SpinButton.new_with_range(lower, upper, 10)
            spin.set_value(value)
            setattr(self, key, spin)
            spin.connect('value-changed', self.resize_layout)
            layout_bar.pack_start(spin, False, False, 0)
        grip = Gtk.EventBox()
        grip.add(Gtk.Label(label='↘'))
        self.translated_widgets.append((grip, 'set_tooltip_text', 'resize_tip'))
        grip.connect('button-press-event', self.drag_resize)
        layout_bar.pack_end(grip, False, False, 0)
        box.pack_start(self.layout_controls, False, False, 0)
        metadata = Gtk.Box(spacing=12)
        box.pack_start(metadata, False, False, 0)
        self.desktop_status = Gtk.Label(xalign=1)
        self.desktop_status.get_style_context().add_class('muted')
        self.position_hint = Gtk.Label(label='Đã ghim · Nhấn Di chuyển để chọn vị trí khác', xalign=0)
        self.position_hint.get_style_context().add_class('muted')
        self.clock = Gtk.Label(xalign=0)
        self.clock.get_style_context().add_class('clock')
        metadata.pack_start(self.clock, True, True, 0)
        routines_button = Gtk.Button()
        routines_button.get_style_context().add_class('quiet-button')
        self.translated_widgets.append((routines_button, 'set_label', 'routines'))
        routines_button.connect('clicked', self.manage_routines)
        metadata.pack_end(routines_button, False, False, 0)
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
        tomorrow_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tomorrow_panel.get_style_context().add_class('panel')
        tomorrow_panel.set_size_request(280, -1)
        body.pack_start(tomorrow_panel, False, False, 0)
        tomorrow_heading = Gtk.Label(xalign=0)
        tomorrow_heading.get_style_context().add_class('eyebrow')
        self.translated_widgets.append((tomorrow_heading, 'set_text', 'tomorrow_heading'))
        tomorrow_panel.pack_start(tomorrow_heading, False, False, 0)
        self.tomorrow_date = Gtk.Label(xalign=0, wrap=True, max_width_chars=28)
        self.tomorrow_date.get_style_context().add_class('selected-date')
        tomorrow_panel.pack_start(self.tomorrow_date, False, False, 0)
        self.tomorrow_status = Gtk.Label(xalign=0)
        self.tomorrow_status.get_style_context().add_class('muted')
        tomorrow_panel.pack_start(self.tomorrow_status, False, False, 0)
        self.tomorrow_progress = Gtk.ProgressBar()
        tomorrow_panel.pack_start(self.tomorrow_progress, False, False, 0)
        tomorrow_scroll = Gtk.ScrolledWindow()
        tomorrow_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.tomorrow_rows = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        tomorrow_scroll.add(self.tomorrow_rows)
        tomorrow_panel.pack_start(tomorrow_scroll, True, True, 0)
        footer = Gtk.Box(spacing=12)
        self.theme_button = Gtk.ComboBoxText()
        self.refresh_theme_options()
        self.theme_button.connect('changed', self.change_theme)
        footer.pack_start(self.theme_button, False, False, 0)
        opacity_label = Gtk.Label()
        opacity_label.get_style_context().add_class('muted')
        self.translated_widgets.append((opacity_label, 'set_text', 'opacity'))
        footer.pack_start(opacity_label, False, False, 0)
        self.opacity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.opacity_scale.set_size_request(110, -1)
        self.opacity_scale.set_digits(0)
        self.opacity_scale.set_value(self.background_opacity)
        self.opacity_scale.connect('value-changed', self.change_opacity)
        footer.pack_start(self.opacity_scale, False, False, 0)
        footer.pack_start(self.position_hint, True, True, 0)
        keyboard_hint = Gtk.Label(xalign=1)
        keyboard_hint.get_style_context().add_class('muted')
        self.translated_widgets.append((keyboard_hint, 'set_text', 'keyboard_hint'))
        footer.pack_end(keyboard_hint, False, False, 0)
        box.pack_start(footer, False, False, 0)
        self.refresh_language()
        self.clock_source = GLib.timeout_add_seconds(1, self.update_clock)
        self.desktop_source = GLib.timeout_add_seconds(5, self.refresh_desktop_mode)
        self.window.realize()
        self.restore_position()
        self.window.show_all()
        self.window.unmaximize()
        if not self.desktop_mode:
            self.window.present()
        self.position_source = GLib.timeout_add(200, self.restore_position)
        # GNOME may place the window and enumerate monitors after its first map.
        # Reapply the saved layout while the desktop session settles.
        self.startup_restore_attempts = 0
        self.startup_restore_source = GLib.timeout_add(300, self.restore_startup_layout)
        self.screen = self.window.get_screen()
        self.monitor_signal = self.screen.connect('monitors-changed', self.monitors_changed)
        self.screen_size_signal = self.screen.connect('size-changed', self.monitors_changed)

    def tr(self, key, **values):
        return translate(self.language, key, **values)

    def apply_theme(self):
        css = (RESOURCES / 'style.css').read_text()
        css = background_css(theme_css(css, self.theme), self.background_opacity, self.theme)
        self.css_provider.load_from_data((css + '\n' + completion_css(self.theme)).encode())
        svg = (RESOURCES / 'robotics-mark.svg').read_text()
        svg = svg.replace('#102329', '#111c24')
        svg = svg.replace('fill="#111c24"', f'fill="#111c24" fill-opacity="{self.background_opacity / 100:.2f}"')
        loader = GdkPixbuf.PixbufLoader.new_with_type('svg')
        loader.write(theme_css(svg, self.theme).encode())
        loader.close()
        self.logo.set_from_pixbuf(loader.get_pixbuf())

    def change_opacity(self, scale):
        value = int(scale.get_value())
        if value == self.background_opacity:
            return
        try:
            save_opacity(APPEARANCE, value)
        except OSError as exc:
            scale.set_value(self.background_opacity)
            self.position_hint.set_text(self.tr('theme_error', error=exc))
            return
        self.background_opacity = value
        self.apply_theme()

    def refresh_theme_options(self):
        self.theme_button.remove_all()
        for theme in THEMES:
            self.theme_button.append(theme, self.tr('theme_' + theme))
        self.theme_button.set_active_id(self.theme)
        self.theme_button.set_tooltip_text(self.tr('theme_tip'))

    def change_theme(self, combo):
        theme = combo.get_active_id()
        if theme is None or theme == self.theme:
            return
        try:
            save_theme(THEME, theme)
        except OSError as exc:
            combo.set_active_id(self.theme)
            self.position_hint.set_text(self.tr('theme_error', error=exc))
            return
        self.theme = theme
        self.apply_theme()

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
        self.refresh_theme_options()
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

    def restore_startup_layout(self):
        self.startup_restore_attempts += 1
        if not self.moving:
            self.restore_position()
        if self.moving or self.startup_restore_attempts >= 8:
            self.startup_restore_source = None
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

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
        names = [monitor.get_model() for monitor in monitors]
        geometries = []
        for monitor in monitors:
            geometry = monitor.get_geometry()
            geometries.append((geometry.x, geometry.y, geometry.width, geometry.height))
        if self.saved_position:
            size = saved_size(self.saved_position)
            if tuple(self.window.get_size()) != size:
                self.window.resize(*size)
        else:
            size = self.window.get_size()
        self.locked_position = resolve_position(self.saved_position, areas, primary_index,
                                                size, names, geometries)
        self.window.move(*self.locked_position)
        self.window.set_keep_above(False)
        self.window.set_keep_below(False)
        self.window.stick()
        return GLib.SOURCE_REMOVE

    def enforce_position(self, _window, event):
        if (not self.moving and self.locked_position is not None
                and ((event.x, event.y) != self.locked_position
                     or (self.saved_position and (event.width, event.height) != saved_size(self.saved_position)))
                and not self.position_source):
            self.position_source = GLib.idle_add(self.restore_position)
        return False

    def drag_window(self, _widget, event):
        if self.moving and event.button == 1:
            self.window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def drag_resize(self, _widget, event):
        if self.moving and event.button == 1:
            self.window.begin_resize_drag(Gdk.WindowEdge.SOUTH_EAST, event.button,
                                          int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def resize_layout(self, _spin):
        if self.moving:
            self.window.resize(self.layout_width.get_value_as_int(), self.layout_height.get_value_as_int())

    def toggle_position(self, _button):
        if self.moving:
            display = self.window.get_display()
            monitor = display.get_monitor_at_window(self.window.get_window())
            area = monitor.get_geometry()
            x, y = self.window.get_position()
            index = next(i for i in range(display.get_n_monitors()) if display.get_monitor(i) == monitor)
            width, height = self.window.get_size()
            saved = dict(monitor=index, x=x - area.x, y=y - area.y, width=width, height=height,
                         coordinate_space='monitor')
            name = monitor.get_model()
            if name:
                saved['monitor_name'] = name
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
        if not self.moving:
            width, height = self.window.get_size()
            self.layout_width.set_value(width)
            self.layout_height.set_value(height)
        self.moving = not self.moving
        self.window.set_resizable(self.moving)
        if self.moving:
            self.layout_controls.show()
            self.layout_controls.get_child().show_all()
        self.layout_controls.set_reveal_child(self.moving)
        self.position_hint_key = 'moving' if self.moving else 'position_saved'
        self.pin_button.set_label(self.tr('pin' if self.moving else 'move'))
        self.position_hint.set_text(self.tr(self.position_hint_key))

    def do_shutdown(self):
        if self.startup_restore_source:
            GLib.source_remove(self.startup_restore_source)
        if self.water_source:
            GLib.source_remove(self.water_source)
        if hasattr(self, 'desktop_source'):
            GLib.source_remove(self.desktop_source)
        if self.position_source:
            GLib.source_remove(self.position_source)
        if hasattr(self, 'monitor_signal'):
            self.screen.disconnect(self.monitor_signal)
            self.screen.disconnect(self.screen_size_signal)
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
                self.render_tomorrow()
        return GLib.SOURCE_CONTINUE

    def save(self):
        try:
            DATA.parent.mkdir(parents=True, exist_ok=True)
            temp = DATA.with_suffix('.tmp')
            temp.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2))
            temp.replace(DATA)
            return True
        except OSError as exc:
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True,
                message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE,
                text=self.tr('save_error'))
            dialog.format_secondary_text(str(exc))
            dialog.run()
            dialog.destroy()
            return False

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
        if self.water_source:
            GLib.source_remove(self.water_source)
            self.water_source = None
        animations = []
        animate = Gtk.Settings.get_default().get_property('gtk-enable-animations')
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
                tasks = daily_tasks(self.tasks, self.routines, selected.isoformat())
                completed = sum(task['done'] for task in tasks)
                percent = round(100 * completed / len(tasks)) if tasks else 0
                button = Gtk.Button()
                button.set_hexpand(True)
                button.set_vexpand(True)
                button.get_style_context().add_class('day')
                if tasks:
                    day_key = selected.isoformat()
                    initial = self.water_levels.get(day_key, 0) if animate else percent
                    self.water_levels[day_key] = initial
                    water = Water(initial)
                    animations.append([water, day_key, initial, percent, initial])
                else:
                    self.water_levels[selected.isoformat()] = 0
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
                summary = ('✓ ' if tasks and completed == len(tasks) else '') + f'{percent}%' if tasks else '—'
                hint = Gtk.Label(label=summary, xalign=0)
                hint.get_style_context().add_class('day-summary')
                if tasks:
                    hint.get_style_context().add_class('day-progress')
                contents.pack_start(hint, False, False, 0)
                if tasks:
                    overlay = Gtk.Overlay()
                    overlay.add(water)
                    overlay.add_overlay(contents)
                    overlay.set_overlay_pass_through(contents, True)
                    button.add(overlay)
                else:
                    button.add(contents)
                tooltip = display_date(selected, self.language)
                if tasks:
                    tooltip += '\n' + self.tr('progress', done=completed, total=len(tasks))
                    tooltip += '\n' + '\n'.join(t['text'] for t in tasks[:5])
                button.set_tooltip_text(tooltip)
                button.connect('clicked', self.select_day, selected)
                self.calendar_grid.attach(button, col, row, 1, 1)
        self.calendar_grid.show_all()
        if any(item[2] != item[3] for item in animations):
            started = GLib.get_monotonic_time()

            def animate_water():
                elapsed = min(1.0, (GLib.get_monotonic_time() - started) / 450000)
                eased = 1 - (1 - elapsed) ** 3
                for item in animations:
                    water, day_key, initial, target, previous = item
                    level = round(initial + (target - initial) * eased)
                    if level != previous:
                        water.set_level(level)
                        item[4] = level
                    self.water_levels[day_key] = level
                if elapsed >= 1:
                    self.water_source = None
                    return GLib.SOURCE_REMOVE
                return GLib.SOURCE_CONTINUE

            self.water_source = GLib.timeout_add(16, animate_water)

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
        self.remember_occurrence(task)
        task['done'] = button.get_active()
        self.save()
        self.render(completed_id=task['id'] if task['done'] else None)

    def remember_occurrence(self, task):
        items = self.tasks.setdefault(self.day, [])
        if not any(item['id'] == task['id'] for item in items):
            items.append(task)

    def store_routines(self, routines, error_label):
        try:
            ROUTINES.parent.mkdir(parents=True, exist_ok=True)
            temporary = ROUTINES.with_suffix('.tmp')
            temporary.write_text(json.dumps(routines, ensure_ascii=False, indent=2))
            temporary.replace(ROUTINES)
        except OSError as exc:
            error_label.set_text(self.tr('save_error') + ': ' + str(exc))
            return False
        self.routines = routines
        self.render()
        return True

    def manage_routines(self, _button):
        dialog = Gtk.Dialog(title=self.tr('routines'), transient_for=self.window, modal=True)
        dialog.set_default_size(520, 460)
        dialog.add_button(self.tr('close'), Gtk.ResponseType.CLOSE)
        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_border_width(16)
        note = Gtk.Label(label=self.tr('routine_note'), xalign=0, wrap=True, max_width_chars=60)
        content.pack_start(note, False, False, 0)
        name = Gtk.Entry(placeholder_text=self.tr('placeholder'), max_length=500)
        content.pack_start(name, False, False, 0)
        times = Gtk.Box(spacing=8)
        start = Gtk.Entry(text='08:00', width_chars=6, max_length=5)
        end = Gtk.Entry(text='09:00', width_chars=6, max_length=5)
        for widget in (Gtk.Label(label=self.tr('start_time')), start,
                       Gtk.Label(label=self.tr('end_time')), end):
            times.pack_start(widget, False, False, 0)
        content.pack_start(times, False, False, 0)
        weekdays = Gtk.Box(spacing=6)
        checks = []
        for index, caption in enumerate(SHORT_DAYS[self.language]):
            check = Gtk.CheckButton(label=caption)
            check.set_active(index < 5)
            checks.append(check)
            weekdays.pack_start(check, False, False, 0)
        content.pack_start(weekdays, False, False, 0)
        error = Gtk.Label(xalign=0, wrap=True, max_width_chars=60)
        content.pack_start(error, False, False, 0)
        add = Gtk.Button(label=self.tr('save_routine'))
        content.pack_start(add, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        listing = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.add(listing)
        content.pack_start(scroll, True, True, 0)
        editing = [None]

        def refresh():
            for child in listing.get_children():
                listing.remove(child)
            for routine in self.routines:
                row = Gtk.Box(spacing=8)
                days = ', '.join(SHORT_DAYS[self.language][day] for day in routine['weekdays'])
                label = Gtk.Label(label=f"{routine['start']}–{routine['end']} · {routine['text']}\n{days}",
                                  xalign=0, wrap=True, max_width_chars=35)
                row.pack_start(label, True, True, 0)
                edit = Gtk.Button(label=self.tr('edit_routine'))
                edit.connect('clicked', edit_item, routine)
                row.pack_start(edit, False, False, 0)
                delete = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
                delete.set_tooltip_text(self.tr('delete_routine'))
                delete.connect('clicked', delete_item, routine)
                row.pack_start(delete, False, False, 0)
                listing.pack_start(row, False, False, 0)
            listing.show_all()

        def edit_item(_widget, routine):
            editing[0] = routine
            name.set_text(routine['text'])
            start.set_text(routine['start'])
            end.set_text(routine['end'])
            for index, check in enumerate(checks):
                check.set_active(index in routine['weekdays'])

        def delete_item(_widget, routine):
            if self.store_routines([item for item in self.routines if item['id'] != routine['id']], error):
                if editing[0] and editing[0]['id'] == routine['id']:
                    editing[0] = None
                    name.set_text('')
                refresh()

        def save_item(_widget):
            previous = editing[0]
            routine = dict(id=previous['id'] if previous else uuid.uuid4().hex,
                           text=name.get_text().strip(), start=start.get_text().strip(),
                           end=end.get_text().strip(),
                           weekdays=[i for i, check in enumerate(checks) if check.get_active()],
                           since=previous['since'] if previous else hanoi_now().date().isoformat())
            try:
                validate_routine(routine)
            except ValueError:
                error.set_text(self.tr('routine_invalid'))
                return
            updated = [item for item in self.routines if item['id'] != routine['id']] + [routine]
            if self.store_routines(updated, error):
                editing[0] = None
                name.set_text('')
                error.set_text('')
                refresh()

        add.connect('clicked', save_item)
        refresh()
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def remove(self, _button, task):
        if task['id'].startswith('routine:'):
            self.remember_occurrence(task)
            task['hidden'] = True
        else:
            self.tasks[self.day].remove(task)
        self.save()
        self.render()

    def task_double_click(self, widget, event, task):
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.edit_task(widget, task)
            return True
        return False

    def edit_task(self, _button, task):
        day = self.day
        dialog = Gtk.Dialog(title=self.tr('edit_task'), transient_for=self.window, modal=True)
        dialog.add_button(self.tr('cancel'), Gtk.ResponseType.CANCEL)
        save_button = dialog.add_button(self.tr('save_task'), Gtk.ResponseType.OK)
        save_button.get_style_context().add_class('primary')
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_default_size(420, -1)
        content = dialog.get_content_area()
        content.set_border_width(16)
        content.set_spacing(10)
        date_label = Gtk.Label(label=display_date(date.fromisoformat(day), self.language), xalign=0)
        date_label.get_style_context().add_class('muted')
        content.pack_start(date_label, False, False, 0)
        entry = Gtk.Entry(text=task['text'], max_length=500, activates_default=True)
        entry.connect('changed', lambda widget: save_button.set_sensitive(bool(widget.get_text().strip())))
        content.pack_start(entry, False, False, 0)
        if task['id'].startswith('routine:'):
            note = Gtk.Label(label=self.tr('edit_occurrence_note'), xalign=0, wrap=True, max_width_chars=48)
            note.get_style_context().add_class('muted')
            content.pack_start(note, False, False, 0)
        dialog.show_all()
        entry.grab_focus()
        entry.select_region(0, -1)
        while dialog.run() == Gtk.ResponseType.OK:
            text = entry.get_text().strip()
            if not text:
                continue
            if text == task['text']:
                break
            items = self.tasks.setdefault(day, [])
            is_new = not any(item['id'] == task['id'] for item in items)
            previous = task['text']
            task['text'] = text
            if is_new:
                items.append(task)
            if self.save():
                self.render()
                break
            task['text'] = previous
            if is_new:
                items.remove(task)
        dialog.destroy()

    def render(self, completed_id=None):
        self.render_calendar()
        self.render_tomorrow()
        for child in self.rows.get_children():
            self.rows.remove(child)
        items = daily_tasks(self.tasks, self.routines, self.day)
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
            caption = (f"{task['start']}–{task['end']}  ·  " if task.get('start') else '') + task['text']
            text = GLib.markup_escape_text(caption)
            label.set_markup(f'<s>{text}</s>' if task['done'] else text)
            if task['done']:
                label.get_style_context().add_class('muted')
            delete = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
            delete.get_style_context().add_class('delete-button')
            delete.set_tooltip_text(self.tr('delete'))
            delete.connect('clicked', self.remove, task)
            row.pack_start(check, False, False, 0)
            task_text = Gtk.EventBox()
            task_text.set_visible_window(False)
            task_text.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            task_text.set_tooltip_text(self.tr('double_click_edit'))
            task_text.add(label)
            task_text.connect('button-press-event', self.task_double_click, task)
            row.pack_start(task_text, True, True, 0)
            row.pack_start(delete, False, False, 0)
            self.rows.add(row)
            if task['id'] == completed_id and Gtk.Settings.get_default().get_property('gtk-enable-animations'):
                row.get_parent().get_style_context().add_class('completion-burst')
                label.get_style_context().add_class('completion-text')
        self.rows.show_all()

    def render_tomorrow(self):
        tomorrow = hanoi_now().date() + timedelta(days=1)
        items = daily_tasks(self.tasks, self.routines, tomorrow.isoformat())
        self.tomorrow_date.set_text(display_date(tomorrow, self.language))
        completed = sum(task['done'] for task in items)
        self.tomorrow_status.set_text(self.tr('progress', done=completed, total=len(items)))
        self.tomorrow_progress.set_fraction(completed / len(items) if items else 0)
        for child in self.tomorrow_rows.get_children():
            self.tomorrow_rows.remove(child)
        if not items:
            empty = Gtk.Label(label=self.tr('tomorrow_empty'), xalign=0, wrap=True,
                              max_width_chars=28, margin=12)
            empty.get_style_context().add_class('muted')
            self.tomorrow_rows.add(empty)
        for task in items:
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=6)
            if task.get('start'):
                time = Gtk.Label(label=f"{task['start']}–{task['end']}", xalign=0)
                time.get_style_context().add_class('eyebrow')
                content.pack_start(time, False, False, 0)
            label = Gtk.Label(xalign=0, wrap=True, max_width_chars=28)
            text = GLib.markup_escape_text(task['text'])
            label.set_markup(f'✓ <s>{text}</s>' if task['done'] else text)
            if task['done']:
                label.get_style_context().add_class('muted')
            content.pack_start(label, False, False, 0)
            self.tomorrow_rows.add(content)
        self.tomorrow_rows.show_all()
