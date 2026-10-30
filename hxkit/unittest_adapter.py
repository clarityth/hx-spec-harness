"""Execute named unittest cases in a child process and record each outcome."""

import json
from pathlib import Path
import sys
import unittest


class RecordingResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.records = []
        self._positions = {}

    def startTest(self, test):
        super().startTest(test)
        self._positions[id(test)] = len(self.records)
        self.records.append({"id": test.id(), "status": "running", "executed": True})

    def _set(self, test, status):
        if id(test) not in self._positions:
            # unittest reports class/module fixture errors with an _ErrorHolder.
            self._positions[id(test)] = len(self.records)
            self.records.append({"id": test.id(), "status": status, "executed": False})
            return
        self.records[self._positions[id(test)]]["status"] = status

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "failed" if issubclass(err[0], AssertionError) else "error"
            self._set(test, status)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._set(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._set(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        self._set(test, "error")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._set(test, "skipped")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._set(test, "expected_failure")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._set(test, "unexpected_success")


def main():
    result_path = Path(sys.argv[1])
    test_dir = Path(sys.argv[2])
    names = json.loads(sys.argv[3])
    nonce = sys.argv[4]
    sys.path.insert(0, str(Path.cwd()))
    sys.path.insert(0, str(test_dir))
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    result = RecordingResult()
    suite.run(result)
    for label, entries in (("failure", result.failures), ("error", result.errors),
                           ("expected failure", result.expectedFailures)):
        for test, details in entries:
            print(f"{label}: {test.id()}\n{details}", file=sys.stderr)
    for test, reason in result.skipped:
        print(f"skipped: {test.id()}: {reason}", file=sys.stderr)
    result_path.write_text(json.dumps({
        "nonce": nonce,
        "tests_run": result.testsRun,
        "tests": result.records,
    }), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
