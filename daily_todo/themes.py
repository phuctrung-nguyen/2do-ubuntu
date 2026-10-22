"""Color palettes and persistent theme preferences."""
import colorsys
import json
import re

THEMES = ('cyan', 'mint', 'blue', 'purple', 'rose', 'amber')
HUES = {'mint': 0.40, 'blue': 0.60, 'purple': 0.76, 'rose': 0.94, 'amber': 0.10}


def completion_css(theme):
    """Draw a bottom-up fill without fading the day number or labels."""
    color = theme_css('#66d4df', theme)
    rgb = ', '.join(str(int(color[i:i + 2], 16)) for i in (1, 3, 5))
    return '\n'.join(
        f'button.day.completion-{percent} {{ background-image: linear-gradient(to top, '
        f'rgba({rgb}, 0.38) 0%, rgba({rgb}, 0.38) {percent}%, '
        f'rgba({rgb}, 0) {percent}%, rgba({rgb}, 0) 100%); }}'
        for percent in range(101)
    )


def load_opacity(path):
    try:
        value = json.loads(path.read_text()).get('opacity')
        if type(value) in (int, float) and 0 <= value <= 100:
            return int(value)
    except (OSError, ValueError, AttributeError):
        pass
    return 35


def save_opacity(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'opacity': value}))
    temporary.replace(path)


def background_css(css, opacity, theme='cyan'):
    """Fade large surfaces only; text and interactive controls stay crisp."""
    alpha = opacity / 100
    overrides = []
    for selector, color in (
        ('window', '#0c1319'),
        ('.panel', '#111c24'),
        ('button.day', '#14232d'),
        ('button.day.weekend', '#122029'),
        ('list row', '#182a35'),
    ):
        color = theme_css(color, theme)
        rgb = ', '.join(str(int(color[i:i + 2], 16)) for i in (1, 3, 5))
        overrides.append(f'{selector} {{ background: rgba({rgb}, {alpha:.2f}); }}')
    return css + '\n' + '\n'.join(overrides)


def load_theme(path):
    try:
        value = json.loads(path.read_text()).get('theme')
        return value if value in THEMES else 'cyan'
    except (OSError, ValueError, AttributeError):
        return 'cyan'


def save_theme(path, theme):
    if theme not in THEMES:
        raise ValueError('Unknown theme')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'theme': theme}))
    temporary.replace(path)


def theme_css(css, theme):
    if theme == 'cyan':
        return css

    def recolor(match):
        rgb = tuple(int(match[0][i:i + 2], 16) / 255 for i in (1, 3, 5))
        hue, light, saturation = colorsys.rgb_to_hls(*rgb)
        # Keep destructive action colors recognizable in every palette.
        if hue > 0.90 or hue < 0.04:
            return match[0]
        result = colorsys.hls_to_rgb(HUES[theme], light, saturation)
        return '#' + ''.join(f'{round(channel * 255):02x}' for channel in result)

    return re.sub(r'#[0-9a-fA-F]{6}\b', recolor, css)
