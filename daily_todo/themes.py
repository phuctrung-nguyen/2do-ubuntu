"""Color palettes and persistent theme preferences."""
import colorsys
import json
import re

THEMES = ('cyan', 'mint', 'blue', 'purple', 'rose', 'amber')
HUES = {'mint': 0.40, 'blue': 0.60, 'purple': 0.76, 'rose': 0.94, 'amber': 0.10}


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
