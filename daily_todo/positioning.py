"""Monitor-relative positioning, independent of the interface toolkit."""


def valid_position(value):
    return (isinstance(value, dict)
            and all(type(value.get(key)) is int for key in ('monitor', 'x', 'y'))
            and value['monitor'] >= 0)


def resolve_position(saved, areas, primary, size):
    """Return a visible position, falling back to the primary monitor."""
    monitor = saved['monitor'] if valid_position(saved) else primary
    if not 0 <= monitor < len(areas):
        monitor = primary
    area = areas[monitor]
    left, top, width, height = area
    max_x, max_y = max(0, width - size[0]), max(0, height - size[1])
    x = saved['x'] if valid_position(saved) else max_x - 12
    y = saved['y'] if valid_position(saved) else 12
    return left + min(max(0, x), max_x), top + min(max(0, y), max_y)
