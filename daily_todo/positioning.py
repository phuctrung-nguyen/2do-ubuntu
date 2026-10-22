"""Monitor-relative positioning, independent of the interface toolkit."""


def saved_size(value):
    """Accept old position files without size and reject corrupt dimensions."""
    if isinstance(value, dict) and all(type(value.get(key)) is int for key in ('width', 'height')):
        if 640 <= value['width'] <= 7680 and 420 <= value['height'] <= 4320:
            return value['width'], value['height']
    return 1300, 650


def valid_position(value):
    return (isinstance(value, dict)
            and all(type(value.get(key)) is int for key in ('monitor', 'x', 'y'))
            and value['monitor'] >= 0)


def resolve_position(saved, areas, primary, size, monitor_names=None, geometries=None):
    """Return a visible position, falling back to the primary monitor."""
    monitor = saved['monitor'] if valid_position(saved) else primary
    if (valid_position(saved) and monitor_names and saved.get('monitor_name')
            and saved['monitor_name'] in monitor_names):
        monitor = monitor_names.index(saved['monitor_name'])
    if not 0 <= monitor < len(areas):
        monitor = primary
    area = areas[monitor]
    left, top, width, height = area
    max_x, max_y = max(0, width - size[0]), max(0, height - size[1])
    x = saved['x'] if valid_position(saved) else max_x - 12
    y = saved['y'] if valid_position(saved) else 12
    if valid_position(saved) and saved.get('coordinate_space') == 'monitor' and geometries:
        origin_x, origin_y = geometries[monitor][:2]
        x += origin_x - left
        y += origin_y - top
    return left + min(max(0, x), max_x), top + min(max(0, y), max_y)
