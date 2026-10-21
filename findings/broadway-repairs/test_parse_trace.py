import unittest
from parse_trace import parse

class DoctestTests(unittest.TestCase):
    trace='Example.Test [test/example_test.exs]\n  * doctest module Example (1) (0.1ms) [L#4]\n  * test basic (1.0ms) [L#8]\n'
    def test_both_kinds_count(self):
        rows=parse(self.trace+'1 doctest, 1 test, 0 failures\n')
        self.assertEqual(len(rows),2)
        self.assertIn('[doctest] module Example (1)',[r['test'] for r in rows])
    def test_failed_doctest_retained(self):
        rows=parse(self.trace+'  1) doctest module Example (1) (Example.Test)\n1 doctest, 1 test, 1 failure\n')
        self.assertEqual([r['test'] for r in rows if r['status']=='FAILED'],['[doctest] module Example (1)'])
    def test_missing_doctest_rejected(self):
        with self.assertRaises(ValueError):
            parse('Example.Test [test/example_test.exs]\n  * test basic (1.0ms) [L#8]\n1 doctest, 1 test, 0 failures\n')
    def test_carriage_return_progress(self):
        text=self.trace.replace('  * doctest module Example (1) (0.1ms)', '  * doctest module Example (1) [L#4]\r  * doctest module Example (1) (0.1ms)')
        self.assertEqual(len(parse(text+'1 doctest, 1 test, 0 failures\n')),2)
if __name__=='__main__':unittest.main()
