"""Vietnamese and English translations and language preferences."""
import json

TEXT = {
    'vi': {
        'double_click_edit': 'Nháy đúp để sửa nội dung công việc',
        'edit_task': 'Sửa nội dung công việc', 'save_task': 'Lưu', 'cancel': 'Hủy',
        'edit_occurrence_note': 'Chỉ đổi nội dung cho ngày này. Để sửa lịch lặp lại, mở Lịch cố định.',
        'tomorrow_heading': 'CÔNG VIỆC NGÀY MAI',
        'tomorrow_empty': 'Ngày mai chưa có công việc.',
        'routines': 'Lịch cố định', 'start_time': 'Từ', 'end_time': 'Đến',
        'save_routine': 'Lưu lịch', 'edit_routine': 'Sửa', 'delete_routine': 'Xóa lịch lặp lại',
        'routine_note': 'Lặp lại theo các thứ đã chọn, từ hôm nay, theo giờ Hà Nội. Đánh dấu xong hoặc xóa trong danh sách chỉ áp dụng cho ngày đó. Xóa lịch tại đây để dừng lặp lại. Các ngày đã lưu trạng thái vẫn được giữ. Chức năng này không phát thông báo.',
        'routine_invalid': 'Nhập tên việc, chọn ít nhất một thứ và giờ HH:MM (00:00–23:59). Giờ kết thúc phải sau giờ bắt đầu trong cùng ngày.',
        'opacity': 'Độ đậm nền',
        'theme_tip': 'Chọn màu giao diện', 'theme_error': 'Chưa lưu được màu: {error}',
        'theme_cyan': 'Cyan', 'theme_mint': 'Xanh mint', 'theme_blue': 'Xanh dương',
        'theme_purple': 'Tím', 'theme_rose': 'Hồng', 'theme_amber': 'Vàng hổ phách',
        'title': 'Việc mỗi ngày', 'move': 'Bố trí', 'pin': 'Lưu bố trí',
        'layout_width': 'Rộng', 'layout_height': 'Cao', 'resize_tip': 'Kéo để thay đổi kích thước',
        'close': 'Đóng ứng dụng', 'pinned': 'Đã khóa · Nhấn Bố trí để đổi vị trí và kích thước',
        'moving': 'Kéo tên để di chuyển, chỉnh Rộng/Cao hoặc kéo ↘, rồi nhấn Lưu bố trí.',
        'position_saved': 'Đã lưu vị trí và kích thước · Khôi phục khi mở lại',
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
        'double_click_edit': 'Double-click to edit task',
        'edit_task': 'Edit task', 'save_task': 'Save', 'cancel': 'Cancel',
        'edit_occurrence_note': 'Changes apply to this date only. Use Recurring tasks to edit the repeating schedule.',
        'tomorrow_heading': 'TOMORROW',
        'tomorrow_empty': 'No tasks for tomorrow yet.',
        'routines': 'Recurring tasks', 'start_time': 'From', 'end_time': 'To',
        'save_routine': 'Save schedule', 'edit_routine': 'Edit', 'delete_routine': 'Delete recurring schedule',
        'routine_note': 'Repeat on selected weekdays, starting today, in Hanoi time. Completing or deleting a daily item affects only that date. Delete its schedule here to stop repeating. Saved daily records are kept. This feature does not send notifications.',
        'routine_invalid': 'Enter a name, select at least one weekday, and use HH:MM (00:00–23:59). End time must be after start time on the same day.',
        'opacity': 'Background',
        'theme_tip': 'Choose interface colors', 'theme_error': 'Could not save theme: {error}',
        'theme_cyan': 'Cyan', 'theme_mint': 'Mint', 'theme_blue': 'Blue',
        'theme_purple': 'Purple', 'theme_rose': 'Rose', 'theme_amber': 'Amber',
        'title': 'DAILY TO-DO', 'move': 'Layout', 'pin': 'Save layout',
        'layout_width': 'Width', 'layout_height': 'Height', 'resize_tip': 'Drag to resize',
        'close': 'Close app', 'pinned': 'Locked · Click Layout to move or resize',
        'moving': 'Drag the title to move, adjust Width/Height or drag ↘, then Save layout.',
        'position_saved': 'Position and size saved · Restored when reopened',
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
