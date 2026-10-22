"""Small Cairo effects that keep calendar labels sharp and clickable."""
import math

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Water(Gtk.DrawingArea):
    def __init__(self, level):
        super().__init__()
        self.set_size_request(52, 48)
        self.level = level
        self.phase = 0
        self.last_frame = 0
        self.tick = None
        self.connect('draw', self.draw_water)
        self.connect('map', self.start)
        self.connect('unmap', self.stop)

    def start(self, _widget):
        if self.tick is None:
            self.tick = self.add_tick_callback(self.frame)

    def stop(self, _widget):
        if self.tick is not None:
            self.remove_tick_callback(self.tick)
            self.tick = None

    def frame(self, _widget, clock):
        now = clock.get_frame_time()
        enabled = self.get_settings().get_property('gtk-enable-animations')
        if enabled and 0 < self.level < 100 and now - self.last_frame >= 33000:
            self.phase = now / 1800000
            self.last_frame = now
            self.queue_draw()
        return True

    def set_level(self, value):
        self.level = value
        self.queue_draw()

    def draw_water(self, _widget, cr):
        width, height = self.get_allocated_width(), self.get_allocated_height()
        if self.level <= 0 or width <= 0 or height <= 0:
            return False
        radius = min(7, width / 2, height / 2)
        for x, y, angle in ((width-radius, radius, -math.pi/2),
                            (width-radius, height-radius, 0),
                            (radius, height-radius, math.pi/2),
                            (radius, radius, math.pi)):
            cr.arc(x, y, radius, angle, angle + math.pi/2)
        cr.close_path()
        cr.clip()
        color = '#2699f5'
        rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
        baseline = height * (1 - self.level / 100)
        amplitude = min(2.5, baseline * .45, (height-baseline) * .45)
        for offset, alpha in ((1.8, .18), (0, .42)):
            points = []
            for x in range(0, width + 3, 3):
                y = baseline + amplitude * math.sin(x / max(width, 1) * math.tau + self.phase + offset)
                points.append((x, y))
            cr.move_to(*points[0])
            for point in points[1:]:
                cr.line_to(*point)
            cr.line_to(width, height)
            cr.line_to(0, height)
            cr.close_path()
            cr.set_source_rgba(*rgb, alpha)
            cr.fill()
            if 0 < self.level < 100:
                cr.move_to(*points[0])
                for point in points[1:]:
                    cr.line_to(*point)
                cr.set_source_rgba(*rgb, .55 if offset == 0 else .2)
                cr.set_line_width(1)
                cr.stroke()
        return False
