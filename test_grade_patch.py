import unittest
from grade_patch import assess


class GradingTests(unittest.TestCase):
    expected = {'FAIL_TO_PASS': [{'module': 'A', 'test': 'same'}],
                'PASS_TO_PASS': [{'module': 'B', 'test': 'same'}]}

    def test_required_inventory_does_not_accept_compile_failure(self):
        expected = {'REQUIRED_PASS': [{'module': 'A', 'test': 'new API'}]}
        self.assertFalse(assess([], expected, 1)['resolved'])
        self.assertFalse(assess([], expected, 0)['resolved'])
        rows = [{'module': 'A', 'test': 'new API', 'status': 'PASSED'}]
        self.assertTrue(assess(rows, expected, 0)['resolved'])
        self.assertFalse(assess(rows, expected, 1)['resolved'])

    def test_both_qualified_tests_required(self):
        rows = [{'module': 'A', 'test': 'same', 'status': 'PASSED'},
                {'module': 'B', 'test': 'same', 'status': 'PASSED'}]
        self.assertTrue(assess(rows, self.expected, 0)['resolved'])
        self.assertFalse(assess(rows[:1], self.expected, 0)['resolved'])
        self.assertFalse(assess(rows, self.expected, 1)['resolved'])
        rows[1]['status'] = 'FAILED'
        self.assertFalse(assess(rows, self.expected, 0)['resolved'])

    def test_duplicate_identity_rejected(self):
        row = {'module': 'A', 'test': 'same', 'status': 'PASSED'}
        with self.assertRaises(ValueError):
            assess([row, row], self.expected, 0)

    def test_unexpected_test_is_not_silently_accepted(self):
        rows = [{'module': r['module'], 'test': r['test'], 'status': 'PASSED'}
                for group in self.expected.values() for r in group]
        rows.append({'module': 'C', 'test': 'extra', 'status': 'PASSED'})
        self.assertFalse(assess(rows, self.expected, 0)['resolved'])


if __name__ == '__main__':
    unittest.main()
