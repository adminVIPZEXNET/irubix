"""Offline public API tests for the lazy Shad account-client adapter."""
import sys
import types
import unittest
from unittest.mock import patch

import irubix
from irubix import shad


class FakeMaxShad:
    def __init__(self, **kwargs):
        self.options = kwargs


class ShadAdapterTests(unittest.TestCase):
    def test_root_import_does_not_require_maxrubika(self):
        self.assertIn("shad", irubix.__all__)

    def test_shad_class_wraps_maxrubika_account_client(self):
        fake = types.ModuleType("maxrubika")
        fake.Shad = FakeMaxShad
        with patch.dict(sys.modules, {"maxrubika": fake}):
            # Resolve the lazy class after the fake dependency is installed.
            cls = shad._load_shad_class()
            client = cls(session="account.session", platform="shad_web")
        self.assertIsInstance(client, FakeMaxShad)
        self.assertEqual(client.options["session"], "account.session")
        self.assertEqual(client.options["platform"], "shad_web")
        self.assertEqual(client.options["api_version"], 6)
        self.assertFalse(client.options["show_welcome"])

    def test_supported_platforms_are_documented(self):
        from maxrubika.client.core.configs import PLATFORMS
        for platform in ("shad_web", "shad_pwa", "shad_android"):
            self.assertIn(platform, PLATFORMS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
