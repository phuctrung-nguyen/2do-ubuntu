"""Manual desktop smoke test: temporarily uses the pointer; isolated test data.

Run explicitly with: /usr/bin/python3 tests/gui_input_smoke.py
"""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

with tempfile.TemporaryDirectory() as directory:
    os.environ.update(XDG_DATA_HOME=directory + '/data', XDG_CONFIG_HOME=directory + '/config')
    from daily_todo import app
    from gi.repository import GLib, GdkX11

    x11 = ctypes.CDLL('libX11.so.6')
    xtest = ctypes.CDLL('libXtst.so.6')
    x11.XOpenDisplay.restype = ctypes.c_void_p
    connection = x11.XOpenDisplay(None)
    x11.XFlush.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    xtest.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
    xtest.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtest.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    application = app.Todo()
    application.set_application_id('local.daily.todo.inputtest')
    pointer = app.Gdk.Display.get_default().get_default_seat().get_pointer()
    _, original_x, original_y = pointer.get_position()
    errors = []
    workspace_test = '--empty-workspace' in sys.argv

    def switch_workspace(right):
        codes = [x11.XKeysymToKeycode(connection, symbol) for symbol in (0xffe3, 0xffe9, 0xff53 if right else 0xff51)]
        for code in codes:
            xtest.XTestFakeKeyEvent(connection, code, 1, 0)
        for code in reversed(codes):
            xtest.XTestFakeKeyEvent(connection, code, 0, 0)
        x11.XFlush(connection)

    def later(function):
        def run():
            try:
                function()
            except Exception:
                errors.append(traceback.format_exc())
                application.quit()
            return False
        GLib.timeout_add(300, run)

    def click(widget):
        x, y = widget.translate_coordinates(application.window, 0, 0)
        wx, wy = application.window.get_position()
        xtest.XTestFakeMotionEvent(connection, -1, wx + x + widget.get_allocated_width() // 2,
                                  wy + y + widget.get_allocated_height() // 2, 0)
        xtest.XTestFakeButtonEvent(connection, 1, 1, 0)
        xtest.XTestFakeButtonEvent(connection, 1, 0, 0)
        x11.XFlush(connection)

    def key(character):
        code = x11.XKeysymToKeycode(connection, ord(character))
        xtest.XTestFakeKeyEvent(connection, code, 1, 0)
        xtest.XTestFakeKeyEvent(connection, code, 0, 0)
        x11.XFlush(connection)

    def prepare():
        # Exercise the exact default window state, without raising it or
        # overriding its stacking flags to make the test artificially pass.
        if workspace_test:
            switch_workspace(True)
        later(edit)

    def edit():
        click(application.entry)
        later(type_text)

    def type_text():
        assert application.entry.has_focus(), 'Entry did not receive the actual pointer click'
        application.entry.reset_im_context()
        application.entry.set_text('')
        key('a'); key('b')
        later(add)

    def add():
        assert application.entry.get_text() == 'ab', application.entry.get_text()
        button = next(widget for widget, _, key in application.translated_widgets if key == 'add')
        click(button)
        later(unlock)

    def unlock():
        assert application.tasks[application.day][0]['text'] == 'ab'
        click(application.pin_button)
        later(pin)

    def pin():
        assert application.moving
        click(application.pin_button)
        later(finish)

    def finish():
        assert not application.moving
        assert app.POSITION.exists()
        application.restore_position()
        later(check_layer)

    def check_layer():
        xid = application.window.get_window().get_xid()
        state = subprocess.check_output(['xprop', '-id', str(xid), '_NET_WM_STATE', '_NET_WM_WINDOW_TYPE'], text=True)
        assert '_NET_WM_WINDOW_TYPE_NORMAL' in state, state
        assert '_NET_WM_STATE_BELOW' not in state, state
        assert '_NET_WM_STATE_ABOVE' not in state, state
        print('PASS: default window state, real mouse clicks, keyboard input, add task, unlock/pin, saved position, no forced ABOVE/BELOW')
        application.quit()

    later(prepare)
    try:
        application.run(None)
    finally:
        if workspace_test:
            switch_workspace(False)
        xtest.XTestFakeMotionEvent(connection, -1, original_x, original_y, 0)
        x11.XFlush(connection)
        x11.XCloseDisplay(connection)
    if errors:
        raise RuntimeError('\n'.join(errors))
