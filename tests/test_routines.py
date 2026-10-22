import unittest
from daily_todo.routines import daily_tasks, validate_routine


class RoutineTests(unittest.TestCase):
    def setUp(self):
        self.routine = dict(id='lab', text='Lab work', start='08:00', end='10:00',
                            weekdays=[0, 1, 2, 3, 4], since='2026-10-22')

    def test_weekdays_start_date_and_time(self):
        validate_routine(self.routine)
        self.assertEqual(daily_tasks({}, [self.routine], '2026-10-21'), [])
        self.assertEqual(daily_tasks({}, [self.routine], '2026-10-24'), [])
        items = daily_tasks({}, [self.routine], '2026-10-22')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['start'], '08:00')

    def test_completion_and_skip_are_per_date(self):
        item = daily_tasks({}, [self.routine], '2026-10-22')[0]
        item['done'] = True
        tasks = {'2026-10-22': [item]}
        self.assertEqual(len(daily_tasks(tasks, [self.routine], '2026-10-22')), 1)
        self.assertTrue(daily_tasks(tasks, [self.routine], '2026-10-22')[0]['done'])
        self.assertFalse(daily_tasks(tasks, [self.routine], '2026-10-23')[0]['done'])
        item['hidden'] = True
        self.assertEqual(daily_tasks(tasks, [self.routine], '2026-10-22'), [])
        self.assertEqual(len(daily_tasks(tasks, [self.routine], '2026-10-23')), 1)

    def test_removed_schedule_keeps_saved_records(self):
        item = daily_tasks({}, [self.routine], '2026-10-22')[0]
        item['done'] = True
        tasks = {'2026-10-22': [item]}
        self.assertEqual(daily_tasks(tasks, [], '2026-10-22'), [item])
        self.assertEqual(daily_tasks(tasks, [], '2026-10-23'), [])

    def test_validation(self):
        for change in (dict(text=' '), dict(weekdays=[]), dict(weekdays=[7]),
                       dict(start='25:00'), dict(end='07:00'), dict(end='08:00'),
                       dict(start='8:00'), dict(since=None)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_routine(dict(self.routine, **change))

    def test_timed_tasks_sort_before_untimed(self):
        tasks = {'2026-10-22': [dict(id='normal', text='Other', done=False)]}
        items = daily_tasks(tasks, [self.routine], '2026-10-22')
        self.assertEqual([item['id'] for item in items], ['routine:lab', 'normal'])
