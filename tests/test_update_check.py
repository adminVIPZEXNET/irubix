"""Tests for Ertebat version comparison and update notices."""
import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from ertebat._update import _check, _is_newer, _latest_github_version


class _FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.content.encode("utf-8")


class UpdateCheckTests(unittest.TestCase):
    def test_detects_new_patch(self):
        self.assertTrue(_is_newer("0.8.2", "0.8.1"))

    def test_compares_numeric_parts(self):
        self.assertTrue(_is_newer("0.10.0", "0.9.9"))

    def test_same_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.1", "0.8.1"))

    def test_older_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.0", "0.8.1"))

    @patch("ertebat._update.urlopen")
    def test_reads_version_from_github(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse('__version__ = "0.9.4"')
        self.assertEqual(_latest_github_version(), "0.9.4")

    @patch("ertebat._update.urlopen")
    def test_prints_english_notice_for_github_update(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse('__version__ = "0.9.4"')
        output = io.StringIO()
        with redirect_stderr(output):
            _check("0.9.3")
        message = output.getvalue()
        self.assertIn("[Ertebat] A new version is available!", message)
        self.assertIn("Current version: 0.9.3", message)
        self.assertIn("Latest version: 0.9.4", message)
        self.assertIn("github.com/adminVIPZEXNET/ertebat/archive/refs/heads/main.zip", message)

    @patch("ertebat._update.urlopen")
    def test_no_notice_when_already_up_to_date(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse('__version__ = "0.9.4"')
        output = io.StringIO()
        with redirect_stderr(output):
            _check("0.9.4")
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
