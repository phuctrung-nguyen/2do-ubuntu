// Desktop stacking integration for GNOME Shell 46.
import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import Meta from 'gi://Meta';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const INTERFACE = `<node><interface name="local.daily.todo.Desktop">
    <method name="Ready"><arg type="b" direction="out" name="ready"/></method>
</interface></node>`;

export default class DesktopTodo extends Extension {
    enable() {
        this._windows = new Map();
        this._source = null;
        this._restacked = global.display.connect('restacked', () => this._queue());
        this._mapped = global.window_manager.connect('map', () => this._queue());
        this._workspace = global.window_manager.connect('switch-workspace', () => this._queue());
        this._overview = Main.overview.connect('hidden', () => this._queue());
        this._dbus = Gio.DBusExportedObject.wrapJSObject(INTERFACE, this);
        this._dbus.export(Gio.DBus.session, '/org/gnome/Shell/Extensions/DailyTodoDesktop');
        this._queue();
    }

    Ready() { return true; }

    _queue() {
        if (this._source !== null)
            return;
        this._source = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
            this._source = null;
            this._sync();
            return GLib.SOURCE_REMOVE;
        });
    }

    _isTodo(window) {
        return window.get_gtk_application_id() === 'local.daily.todo';
    }

    _isDesktop(window) {
        return window.get_window_type() === Meta.WindowType.DESKTOP ||
            Boolean(window.customJS_ding?.keepAtBottom);
    }

    _watch(window) {
        if (this._windows.has(window))
            return;
        const minimized = window.connect('notify::minimized', () => {
            if (window.minimized)
                window.unminimize();
            this._queue();
        });
        const unmanaged = window.connect('unmanaged', () => {
            window.disconnect(minimized);
            window.disconnect(unmanaged);
            this._windows.delete(window);
        });
        this._windows.set(window, [minimized, unmanaged]);
    }

    _sync() {
        // Do not use global.get_window_actors(): Desktop Icons NG overrides it
        // to filter out desktop surfaces, which are essential for input order.
        const windows = global.display.list_all_windows().filter(window => window.get_compositor_private()?.mapped);
        const sorted = global.display.sort_windows_by_stacking(windows);
        const desktops = sorted.filter(window => this._isDesktop(window));
        for (const todo of sorted.filter(window => this._isTodo(window))) {
            this._watch(todo);
            if (todo.is_above())
                todo.unmake_above();
            if (!todo.is_on_all_workspaces())
                todo.stick();
            const index = sorted.indexOf(todo);
            const misplaced = sorted.some((window, position) =>
                window !== todo && (this._isDesktop(window) ? position > index : position < index));
            if (!misplaced)
                continue;
            // Preserve the order and focus of application windows while putting
            // them above the widget. This avoids the Below layer entirely.
            for (const window of sorted) {
                if (window !== todo && !this._isDesktop(window) && !window.is_override_redirect())
                    window.raise();
            }
            for (const desktop of [...desktops].reverse())
                desktop.lower();
        }
    }

    disable() {
        global.display.disconnect(this._restacked);
        global.window_manager.disconnect(this._mapped);
        global.window_manager.disconnect(this._workspace);
        Main.overview.disconnect(this._overview);
        if (this._source !== null)
            GLib.source_remove(this._source);
        this._source = null;
        this._dbus.unexport();
        for (const [window, signals] of this._windows)
            for (const signal of signals)
                window.disconnect(signal);
        this._windows.clear();
    }
}
