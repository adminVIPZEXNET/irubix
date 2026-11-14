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
    def test_root_import_does_not_require_eager_shad_dependency(self):
        self.assertIn("shad", irubix.__all__)
        self.assertTrue(hasattr(shad, "_load_shad_class"))

    def test_shad_adapter_forwards_account_options(self):
        fake = types.ModuleType("maxrubika")
        fake.Shad = FakeMaxShad
        with patch.dict(sys.modules, {"maxrubika": fake}):
            cls = shad._load_shad_class()
            client = cls(session="account.session", platform="shad_web")
        self.assertIsInstance(client, FakeMaxShad)
        self.assertEqual(client.options["session"], "account.session")
        self.assertEqual(client.options["platform"], "shad_web")
        self.assertEqual(client.options["api_version"], 6)
        self.assertFalse(client.options["show_welcome"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
