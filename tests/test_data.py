"""Checks for bounded, read-only CSV/TSV inspection."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hxkit import data
from hxkit.data import join_profile, profile


class DataInspectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_profile_preserves_ids_na_and_counts_full_row_duplicates(self) -> None:
        path = self.file("raw.csv", "id,value\n001,NA\n001,NA\n1,\n002,NaN\n")
        before = path.read_bytes()
        result = profile(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(result["header"], ["id", "value"])
        self.assertEqual(result["rows_scanned"], 4)
        self.assertTrue(result["complete"])
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(result["columns"]["id"]["distinct"], 3)
        self.assertEqual(result["columns"]["id"]["leading_zero_count"], 3)
        self.assertEqual(result["columns"]["id"]["numeric_candidate"], {"count": 4, "min": "1", "max": "2"})
        self.assertEqual(result["columns"]["value"]["empty"], 1)
        self.assertEqual(result["columns"]["value"]["distinct"], 3)
        self.assertEqual(result["columns"]["value"]["numeric_candidate"]["count"], 0)
        self.assertNotIn("001", json.dumps(result))
        self.assertNotIn("NA", json.dumps(result))

    def test_profile_detects_sample_boundary_and_tsv(self) -> None:
        path = self.file("raw.tsv", "id\tamount\na\t1\nb\t2\nc\t3\n")
        partial = profile(path, limit=2)
        self.assertEqual(partial["rows_scanned"], 2)
        self.assertFalse(partial["complete"])
        self.assertTrue(partial["warnings"])
        self.assertTrue(profile(path, limit=3)["complete"])

    def test_sample_boundary_does_not_parse_malformed_following_row(self) -> None:
        path = self.file("boundary.csv", 'id,value\na,1\nb,2\n"broken')
        result = profile(path, limit=2)
        self.assertEqual(result["rows_scanned"], 2)
        self.assertEqual(result["malformed_rows"], 0)
        self.assertFalse(result["complete"])
        with self.assertRaises(ValueError):
            profile(path, limit=3)

        right = self.file("right.csv", "id,value\na,1\n")
        joined = join_profile(path, right, ["id"], limit=2)
        self.assertFalse(joined["left_complete"])
        self.assertEqual(joined["expected_inner_rows"], 1)

    def test_sample_boundary_handles_multiline_records_and_blank_lines(self) -> None:
        content = 'id,value\n1,"first\n\nsecond"\n'
        self.assertTrue(profile(self.file("one_record.csv", content), limit=1)["complete"])
        only_blanks = self.file("only_blanks.csv", content + "\n\r\n")
        self.assertFalse(profile(only_blanks, limit=1)["complete"])
        all_rows = profile(only_blanks, limit=3)
        self.assertTrue(all_rows["complete"])
        self.assertEqual(all_rows["malformed_rows"], 2)
        following = self.file("following.csv", content + "\n\r\n2,next\n")
        result = profile(following, limit=1)
        self.assertEqual(result["rows_scanned"], 1)
        self.assertFalse(result["complete"])
        self.assertFalse(profile(following, limit=2)["complete"])
        self.assertTrue(profile(following, limit=4)["complete"])

    def test_profile_reports_malformed_rows(self) -> None:
        path = self.file("raw.csv", "id,value\na,1\nb\nc,3,extra\na,1\n")
        result = profile(path)
        self.assertEqual(result["rows_scanned"], 4)
        self.assertEqual(result["malformed_rows"], 2)
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(result["columns"]["value"]["distinct"], 1)
        self.assertTrue(result["warnings"])

    def test_sample_character_limit_rejects_wide_input_and_suggests_smaller_limit(self) -> None:
        wide = self.file("wide.csv", "id\n" + "abcdefghij\n" * 20)
        right = self.file("right.csv", "id\nabcdefghij\n")
        with patch.object(data, "MAX_SAMPLE_CHARS", 100):
            with self.assertRaisesRegex(ValueError, "limit을 줄여 표본을 축소"):
                profile(wide, limit=20)
            with self.assertRaisesRegex(ValueError, "limit을 줄여 표본을 축소"):
                join_profile(wide, right, ["id"], limit=20)
            smaller = profile(wide, limit=5)
            self.assertEqual(smaller["rows_scanned"], 5)
            self.assertFalse(smaller["complete"])

    def test_sample_character_limit_does_not_include_following_record(self) -> None:
        path = self.file("large_following.csv", 'id,value\na,1\nb,2\n"' + "x" * 150_000)
        with patch.object(data, "MAX_SAMPLE_CHARS", len("id,value\na,1\nb,2\n")):
            self.assertFalse(profile(path, limit=2)["complete"])
            with self.assertRaisesRegex(ValueError, "limit을 줄여 표본을 축소"):
                profile(path, limit=3)

    def test_profile_rejects_invalid_headers_and_files(self) -> None:
        for name, content in (
            ("empty.csv", ""),
            ("duplicate.csv", "id,id\na,b\n"),
            ("blank.csv", "id,\na,b\n"),
            ("broken.csv", 'id,value\na,"unfinished\n'),
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                profile(self.file(name, content))
        with self.assertRaises(ValueError):
            profile(self.file("wrong.txt", "id\na\n"))
        with self.assertRaises(ValueError):
            profile(self.file("valid.csv", "id\na\n"), limit=0)

    def test_join_counts_one_to_many_and_many_to_many_expansion(self) -> None:
        left = self.file("left.csv", "id\n001\n002\n003\n")
        right = self.file("right.csv", "id\n001\n001\n002\n004\n")
        result = join_profile(left, right, ["id"])
        self.assertEqual(result["relationship"], "one-to-many")
        self.assertEqual(result["expected_inner_rows"], 3)
        self.assertEqual(result["expected_left_rows"], 4)
        self.assertEqual(result["matched_left_rows"], 2)
        self.assertEqual(result["matched_right_rows"], 3)
        self.assertEqual(result["unmatched_left_rows"], 1)
        self.assertEqual(result["unmatched_right_rows"], 1)

        left = self.file("left_many.csv", "id\n001\n001\n002\n")
        result = join_profile(left, right, ["id"])
        self.assertEqual(result["relationship"], "many-to-many")
        self.assertEqual(result["expected_inner_rows"], 5)
        self.assertEqual(result["expected_left_rows"], 5)

    def test_join_uses_raw_composite_keys_and_preserves_empty_left_keys(self) -> None:
        left = self.file("left.tsv", "id\tpart\n001\tA\n001\tA\n001\t\n1\tA\nNA\tB\n")
        right = self.file("right.tsv", "id\tpart\n001\tA\n001\tB\n1\tA\n\tA\n")
        result = join_profile(left, right, ["id", "part"])
        self.assertEqual(result["missing_key_left_rows"], 1)
        self.assertEqual(result["missing_key_right_rows"], 1)
        self.assertEqual(result["matched_left_rows"], 3)
        self.assertEqual(result["expected_inner_rows"], 3)
        self.assertEqual(result["expected_left_rows"], 5)
        self.assertEqual(result["relationship"], "many-to-one")
        self.assertEqual(result["unmatched_left_rows"], 1)

    def test_join_reports_partial_and_rejects_missing_key(self) -> None:
        left = self.file("left.csv", "id\na\nb\nc\n")
        right = self.file("right.csv", "id\na\nb\n")
        result = join_profile(left, right, ["id"], limit=2)
        self.assertFalse(result["left_complete"])
        self.assertTrue(result["right_complete"])
        self.assertTrue(result["warnings"])
        with self.assertRaisesRegex(ValueError, "조인 열"):
            join_profile(left, right, ["other"])

    def test_join_without_common_key_has_undetermined_relationship(self) -> None:
        left = self.file("left.csv", "id\na\na\n")
        right = self.file("right.csv", "id\nb\nb\n")
        result = join_profile(left, right, ["id"])
        self.assertEqual(result["relationship"], "undetermined")
        self.assertEqual(result["expected_inner_rows"], 0)
        self.assertEqual(result["expected_left_rows"], 2)
        self.assertTrue(any("관계를 확인할 수 없습니다" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
