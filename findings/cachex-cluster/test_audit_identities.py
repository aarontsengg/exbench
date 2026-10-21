import unittest
from audit_identities import parse

class TraceAdapterTests(unittest.TestCase):
    def test_same_name_in_two_modules_stays_separate(self):
        text = ('Example.A [test/a_test.exs]\n'
                '  * test same [L#2]\n  * test same (1.0ms) [L#2]\n'
                'Example.B [test/b_test.exs]\n'
                '  * test same (2.0ms) [L#3]\n'
                '  1) test same (Example.B)\n2 tests, 1 failure\n')
        rows = parse(text)
        self.assertEqual([(r['module'], r['status']) for r in rows],
                         [('Example.A', 'PASSED'), ('Example.B', 'FAILED')])

    def test_started_but_unfinished_test_cannot_pass(self):
        with self.assertRaises(ValueError):
            parse('Example.A [test/a.exs]\n  * test unfinished [L#1]\n1 tests, 0 failures\n')

    def test_missing_summary_cannot_pass(self):
        with self.assertRaises(ValueError):
            parse('Example.A [test/a.exs]\n  * test done (1ms) [L#1]\n')

if __name__ == '__main__':
    unittest.main()
