import unittest
from parse_qualified_historical import parse


class ParserTests(unittest.TestCase):
    def test_same_name_different_modules_and_failure_override(self):
        rows = parse('FirstTest\n  * test shared\r  * test shared (1ms)\n'
                     '  1) test shared (FirstTest)\nSecondTest\n  * test shared (0.2ms)\n'
                     '2 tests, 1 failure\n')
        self.assertEqual([(r['module'], r['status']) for r in rows],
                         [('FirstTest', 'FAILED'), ('SecondTest', 'PASSED')])

    def test_failure_before_completion(self):
        rows = parse('FirstTest\n  1) test bad (FirstTest)\n  * test bad (1ms)\n1 tests, 1 failure')
        self.assertEqual(rows[0]['status'], 'FAILED')

    def test_rejects_incomplete_or_ambiguous_logs(self):
        for text in ['FirstTest\n  * test unfinished\n1 tests, 0 failures',
                     '  * test orphan (1ms)\n1 tests, 0 failures',
                     'FirstTest\n  * test a (1ms)\n',
                     'FirstTest\n  * test a (1ms)\n  * test a (1ms)\n2 tests, 0 failures',
                     'FirstTest\n  * test a (1ms)\n1 tests, 1 failure']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse(text)


if __name__ == '__main__':
    unittest.main()
