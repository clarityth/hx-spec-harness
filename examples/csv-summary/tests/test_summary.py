import unittest
from solution import summarize


class SummaryTests(unittest.TestCase):
    def test_raw_ids_and_duplicates(self):
        result = summarize([{'product_id': '001', 'quantity': '2'},
                            {'product_id': '001', 'quantity': '1'},
                            {'product_id': '1', 'quantity': '4'}])
        self.assertEqual(result, {'001': 3, '1': 4})

    def test_inclusive_boundary_and_sort(self):
        self.assertEqual(list(summarize([{'product_id': 'b', 'quantity': '3'},
                                       {'product_id': 'a', 'quantity': '4'},
                                       {'product_id': 'c', 'quantity': '2'}])), ['a', 'b'])

    def test_invalid_rows(self):
        for row in [{'product_id': '', 'quantity': '3'},
                    {'product_id': 'x', 'quantity': '-1'},
                    {'product_id': 'x', 'quantity': '3.2'}]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                summarize([row])
