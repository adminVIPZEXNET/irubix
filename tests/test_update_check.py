"""Tests for IRubix version comparison and update notices."""
import io
import json
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from irubix._update import _check, _is_newer


class _FakeResponse:
    def __init__(self, version):
        self.version = version

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"info": {"version": self.version}}).encode("utf-8")


class UpdateCheckTests(unittest.TestCase):
    def test_detects_new_patch(self):
        self.assertTrue(_is_newer("0.8.2", "0.8.1"))

    def test_compares_numeric_parts(self):
        self.assertTrue(_is_newer("0.10.0", "0.9.9"))

    def test_same_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.1", "0.8.1"))

    def test_older_version_is_not_newer(self):
        self.assertFalse(_is_newer("0.8.0", "0.8.1"))

    @patch("irubix._update.urlopen")
    def test_prints_english_notice_when_update_exists(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse("0.9.3")
        output = io.StringIO()
        with redirect_stderr(output):
            _check("0.9.2")
        message = output.getvalue()
        self.assertIn("[IRubix] A new version is available!", message)
        self.assertIn("Current version: 0.9.2", message)
        self.assertIn("Latest version: 0.9.3", message)
        self.assertIn("python -m pip install --upgrade irubix", message)

    @patch("irubix._update.urlopen")
    def test_no_notice_when_already_up_to_date(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse("0.9.2")
        output = io.StringIO()
        with redirect_stderr(output):
            _check("0.9.2")
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
