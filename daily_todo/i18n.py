"""Vietnamese and English translations and language preferences."""
import json

TEXT = {
    'vi': {
        'theme_tip': 'Chọn màu giao diện', 'theme_error': 'Chưa lưu được màu: {error}',
        'theme_cyan': 'Cyan', 'theme_mint': 'Xanh mint', 'theme_blue': 'Xanh dương',
        'theme_purple': 'Tím', 'theme_rose': 'Hồng', 'theme_amber': 'Vàng hổ phách',
        'title': 'Việc mỗi ngày', 'move': 'Di chuyển', 'pin': 'Ghim tại đây',
        'close': 'Đóng ứng dụng', 'pinned': 'Đã ghim · Nhấn Di chuyển để chọn vị trí khác',
        'moving': 'Kéo vùng tên ứng dụng đến vị trí bạn thích, rồi nhấn Ghim tại đây.',
        'position_saved': 'Đã lưu vị trí · Sẽ khôi phục khi đăng nhập lần sau',
        'position_error': 'Chưa lưu được vị trí: {error}',
        'language_error': 'Chưa lưu được ngôn ngữ: {error}',
        'language_tip': 'Ngôn ngữ: Tiếng Việt · Chọn để đổi',
        'previous': 'Tháng trước', 'next': 'Tháng sau', 'today': 'Về hôm nay',
        'legend': '● Hôm nay    ·    Chọn một ngày để lên kế hoạch',
        'placeholder': 'Thêm việc cần làm…', 'add': 'Thêm', 'delete': 'Xóa công việc',
        'month': 'Tháng {month:02d} / {year}', 'tasks': '{count} việc', 'done': '✓ Xong',
        'progress': '{done}/{total} hoàn thành',
        'empty': '✧\nMột ngày đầy khả năng\nThêm việc đầu tiên bên dưới nhé.',
        'timezone': 'Hà Nội (UTC+7)', 'invalid': 'Dữ liệu không đúng định dạng',
        'read_error': 'Không đọc được dữ liệu công việc', 'preserved': 'Dữ liệu cũ được giữ nguyên.',
        'save_error': 'Không lưu được công việc',
        'desktop_ready': 'Chế độ desktop · Luôn nằm sau cửa sổ ứng dụng',
        'desktop_pending': 'Chưa có tích hợp desktop · Đăng xuất/đăng nhập sau khi cài phần ghim GNOME',
        'eyebrow': 'HUSTER / KẾ HOẠCH MỖI NGÀY',
        'task_heading': 'VIỆC TRONG NGÀY', 'total': 'Tổng việc', 'remaining': 'Còn lại', 'completed': 'Đã xong',
        'keyboard_hint': 'Enter ↵ để thêm việc',
        'desktop_badge_ready': '● Ghim desktop', 'desktop_badge_pending': '○ Chưa ghim desktop',
    },
    'en': {
        'theme_tip': 'Choose interface colors', 'theme_error': 'Could not save theme: {error}',
        'theme_cyan': 'Cyan', 'theme_mint': 'Mint', 'theme_blue': 'Blue',
        'theme_purple': 'Purple', 'theme_rose': 'Rose', 'theme_amber': 'Amber',
        'title': 'DAILY TO-DO', 'move': 'Move', 'pin': 'Pin here',
        'close': 'Close app', 'pinned': 'Pinned · Click Move to choose another position',
        'moving': 'Drag the app title to your preferred position, then click Pin here.',
        'position_saved': 'Position saved · Restored the next time you sign in',
        'position_error': 'Could not save position: {error}',
        'language_error': 'Could not save language: {error}',
        'language_tip': 'Language: English · Select to switch',
        'previous': 'Previous month', 'next': 'Next month', 'today': 'Go to today',
        'legend': '● Today    ·    Choose a day to plan',
        'placeholder': 'Add a task…', 'add': 'Add', 'delete': 'Delete task',
        'month': '{month_name} {year}', 'tasks': '{count} tasks', 'done': '✓ Done',
        'progress': '{done}/{total} completed',
        'empty': '✧\nA day full of possibilities\nAdd your first task below.',
        'timezone': 'Hanoi (UTC+7)', 'invalid': 'Invalid task data format',
        'read_error': 'Could not read tasks', 'preserved': 'Your existing data has been kept unchanged.',
        'save_error': 'Could not save tasks',
        'desktop_ready': 'Desktop mode · Always behind application windows',
        'desktop_pending': 'Desktop integration unavailable · Sign out/in after installing the GNOME extension',
        'eyebrow': 'HUSTER / DAILY PLANNER',
        'task_heading': 'DAILY TASKS', 'total': 'Total', 'remaining': 'To do', 'completed': 'Done',
        'keyboard_hint': 'Enter ↵ to add a task',
        'desktop_badge_ready': '● Desktop pinned', 'desktop_badge_pending': '○ Desktop not pinned',
    },
}
WEEKDAYS = {
    'vi': ('Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật'),
    'en': ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
}
SHORT_DAYS = {'vi': ('T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'),
              'en': ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')}
MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December')


def translate(language, key, **values):
    if language == 'en' and key == 'tasks' and values.get('count') == 1:
        return '1 task'
    return TEXT[language][key].format(**values)


def display_date(day, language='vi'):
    return f'{WEEKDAYS[language][day.weekday()]}, {day:%d/%m/%Y}'


def load_language(path):
    try:
        settings = json.loads(path.read_text())
        value = settings.get('language') if isinstance(settings, dict) else None
        return value if value in ('vi', 'en') else 'vi'
    except (OSError, ValueError):
        return 'vi'


def save_language(path, language):
    if language not in TEXT:
        raise ValueError('Unsupported language')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'language': language}))
    temporary.replace(path)
