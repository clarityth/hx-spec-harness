import csv
import tempfile
import unittest
from pathlib import Path

from solution import summarize


class OrderSummaryTests(unittest.TestCase):
    def summarize_rows(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.csv"
            with path.open("w", encoding="utf-8", newline="") as target:
                writer = csv.writer(target)
                writer.writerow(("order_id", "customer_id", "delay", "unit"))
                writer.writerows(rows)
            return summarize(path)

    def test_original_customer_ids_and_first_order_win(self):
        actual = self.summarize_rows(
            [
                ("a", "001", "60", "minutes"),
                ("a", "1", "999", "hours"),
                ("b", "1", "1", "hours"),
            ]
        )
        self.assertEqual(actual["counts"], {"001": 1, "1": 1})
        self.assertEqual(actual["duplicate_rows"], 1)
        self.assertEqual(actual["excluded_rows"], 0)

    def test_threshold_in_both_units_and_only_delayed_customers(self):
        actual = self.summarize_rows(
            [
                ("a", "z", "59.99", "minutes"),
                ("b", "b", "60", "minutes"),
                ("c", "a", "0.999", "hours"),
                ("d", "a", "1", "hours"),
            ]
        )
        self.assertEqual(actual["counts"], {"a": 1, "b": 1})
        self.assertEqual(list(actual["counts"]), ["a", "b"])

    def test_invalid_rows_and_duplicate_categories_do_not_overlap(self):
        actual = self.summarize_rows(
            [
                ("a", "", "70", "minutes"),
                ("a", "x", "70", "minutes"),
                ("b", "x", "no", "minutes"),
                ("c", "x", "-1", "hours"),
                ("d", "x", "70", "seconds"),
                ("e", "x", "NaN", "minutes"),
                ("f", "x", "Infinity", "hours"),
            ]
        )
        self.assertEqual(
            actual,
            {"counts": {}, "excluded_rows": 6, "duplicate_rows": 1},
        )


if __name__ == "__main__":
    unittest.main()
