"""Weekly recurring tasks and date-specific completion records."""
import re
from datetime import date


def validate_routine(item):
    if not isinstance(item, dict):
        raise ValueError('Invalid routine')
    if not isinstance(item.get('id'), str) or not isinstance(item.get('text'), str) or not item['text'].strip():
        raise ValueError('A task name is required')
    days = item.get('weekdays')
    if not isinstance(days, list) or not days or any(type(day) is not int or not 0 <= day <= 6 for day in days):
        raise ValueError('Select at least one weekday')
    for key in ('start', 'end'):
        if not isinstance(item.get(key), str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', item[key]):
            raise ValueError('Use HH:MM (24-hour time)')
    if item['start'] >= item['end']:
        raise ValueError('End time must be after start time')
    if not isinstance(item.get('since'), str):
        raise ValueError('Invalid start date')
    date.fromisoformat(item['since'])


def daily_tasks(tasks, routines, day):
    selected = date.fromisoformat(day)
    saved = tasks.get(day, [])
    ids = {task['id'] for task in saved}
    generated = []
    for routine in routines:
        if day >= routine['since'] and selected.weekday() in routine['weekdays']:
            identity = 'routine:' + routine['id']
            if identity not in ids:
                generated.append(dict(id=identity, text=routine['text'], done=False,
                                      start=routine['start'], end=routine['end']))
    return sorted([task for task in saved + generated if not task.get('hidden')],
                  key=lambda task: task.get('start', '99:99'))
