"""Behavior checks for the local check runner."""

from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hxkit.runner import execute  # noqa: E402


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence"
        (self.root / "tests").mkdir()

    def run_check(self, check):
        return execute(self.root, {"id": "case", "timeout_seconds": 2, **check}, self.evidence)

    def write_tests(self, source):
        (self.root / "tests" / "test_sample.py").write_text(source, encoding="utf-8")

    def test_unittest_records_each_outcome_and_rejects_skip(self):
        self.write_tests("""import unittest
class Cases(unittest.TestCase):
    def test_pass(self): self.assertTrue(True)
    @unittest.skip('not ready')
    def test_skip(self): self.fail('must not run')
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases"]})
        self.assertEqual(result["status"], "failed")
        self.assertEqual({item["status"] for item in result["tests"]}, {"passed", "skipped"})
        self.assertEqual(result["evidence_strength"], "behavior")

    def test_unittest_failure_error_and_expected_failure(self):
        self.write_tests("""import unittest
class Cases(unittest.TestCase):
    def test_fail(self): self.fail('failed')
    def test_error(self): raise RuntimeError('error')
    @unittest.expectedFailure
    def test_expected(self): self.fail('expected')
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases"]})
        self.assertEqual(result["status"], "failed")
        self.assertEqual({item["status"] for item in result["tests"]},
                         {"failed", "error", "expected_failure"})
        log = (self.evidence / result["log"]).read_text(encoding="utf-8")
        self.assertIn("RuntimeError: error", log)
        self.assertIn("AssertionError: failed", log)

    def test_project_module_import_and_subtest_failure(self):
        (self.root / "solution.py").write_text("VALUE = 3\n", encoding="utf-8")
        self.write_tests("""import unittest
from solution import VALUE
class Cases(unittest.TestCase):
    def test_module(self): self.assertEqual(VALUE, 3)
    def test_subtests(self):
        for value in (1, 2):
            with self.subTest(value=value):
                self.assertEqual(value, 1)
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases"]})
        self.assertEqual(result["status"], "failed")
        self.assertEqual({item["id"].split(".")[-1]: item["status"] for item in result["tests"]},
                         {"test_module": "passed", "test_subtests": "failed"})
        self.assertTrue(all(item["executed"] for item in result["tests"]))
        self.assertIn("(value=2)", (self.evidence / result["log"]).read_text(encoding="utf-8"))

    def test_setup_class_error_is_recorded_without_claiming_test_execution(self):
        self.write_tests("""import unittest
class Cases(unittest.TestCase):
    @classmethod
    def setUpClass(cls): raise RuntimeError('fixture failure')
    def test_never_runs(self): self.fail('should not run')
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases"]})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(result["tests"]), 1)
        self.assertEqual(result["tests"][0]["status"], "error")
        self.assertFalse(result["tests"][0]["executed"])
        self.assertIn("fixture failure", (self.evidence / result["log"]).read_text(encoding="utf-8"))

    def test_unittest_empty_and_missing_names_do_not_pass(self):
        self.assertEqual(self.run_check({"kind": "unittest", "tests": []})["status"], "failed")
        self.write_tests("import unittest\n")
        zero = self.run_check({"kind": "unittest", "tests": ["test_sample"]})
        self.assertEqual(zero["status"], "failed")
        self.assertEqual(zero["reason"], "zero tests executed")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Missing"]})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["tests"][0]["status"], "error")

    def test_missing_child_result_is_error(self):
        self.write_tests("""import os
import unittest
class Cases(unittest.TestCase):
    def test_exit(self): os._exit(0)
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases.test_exit"]})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason"], "unittest adapter result missing")

    def test_unittest_real_pass(self):
        self.write_tests("""import unittest
class Cases(unittest.TestCase):
    def test_ok(self): self.assertEqual(2, 1 + 1)
""")
        result = self.run_check({"kind": "unittest", "tests": ["test_sample.Cases.test_ok"]})
        self.assertEqual(result["status"], "passed")
        self.assertEqual(len(result["tests"]), 1)

    def test_json_strict_comparison_and_boolean_type(self):
        cases = [("true", True, "passed"), ("true", 1, "failed"),
                 ('{"a":1,"a":2}', {"a": 2}, "failed"),
                 ("NaN", None, "failed"), ("1 2", 1, "failed")]
        for output, expected, status in cases:
            with self.subTest(output=output, expected=expected):
                result = self.run_check({"kind": "json", "argv": ["{python}", "-c",
                                        "print(" + repr(output) + ")"], "expected": expected})
                self.assertEqual(result["status"], status)

    def test_command_zero_exit_only_proves_process(self):
        result = self.run_check({"kind": "command", "argv": ["{python}", "-c", "pass"]})
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["evidence_strength"], "process")

    def test_timeout_and_large_output_fail(self):
        timeout = self.run_check({"kind": "command", "timeout_seconds": 1,
                                  "argv": ["{python}", "-c", "import time; time.sleep(5)"]})
        self.assertEqual(timeout["status"], "failed")
        self.assertEqual(timeout["reason"], "timeout")
        large = self.run_check({"kind": "command", "argv": ["{python}", "-c",
                                "import sys; sys.stdout.write('x' * 300000)"]})
        self.assertEqual(large["status"], "failed")
        self.assertTrue(large["output_truncated"])
        self.assertLess((self.evidence / large["log"]).stat().st_size, 263000)

    def test_environment_and_log_redaction(self):
        result = self.run_check({"kind": "command", "argv": ["{python}", "-c",
                                "import os; print('HOME=' + str(os.getenv('HOME'))); print('password=topsecret'); print('{\"token\":\"jsonsecret\"}')"]})
        log = (self.evidence / result["log"]).read_text(encoding="utf-8")
        self.assertIn("HOME=None", log)
        self.assertNotIn("topsecret", log)
        self.assertNotIn("jsonsecret", log)
        self.assertIn("[REDACTED]", log)


if __name__ == "__main__":
    unittest.main()
