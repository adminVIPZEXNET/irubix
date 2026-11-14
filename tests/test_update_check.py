"""Tests for IRubix version comparison."""
import unittest

from irubix._update import _is_newer


class UpdateCheckTests(unittest.TestCase):
    def test_detects_new_patch(self):
        self.assertTrue(_is_newer("0.8.2", "0.8.1"))

    def test_compares_numeric_parts(self):
        self.assertTrue(_is_newer("0.10.0", "0.9.9"))

    def test_same_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.1", "0.8.1"))

    def test_older_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.0", "0.8.1"))


if __name__ == "__main__":
    unittest.main()
