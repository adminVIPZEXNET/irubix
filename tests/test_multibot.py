"""Offline tests for the MultiBot manager."""
import unittest

from ertebat import MultiBot


class MultiBotTests(unittest.TestCase):
    def test_add_and_get_clients(self):
        app = MultiBot()
        rubika = app.add("rubika", "TEST_RUBIKA")
        telegram = app.add("telegram", "TEST_TELEGRAM")
        self.assertIs(app.get("rubika"), rubika)
        self.assertIs(app.get("telegram"), telegram)
        self.assertEqual(len(app), 2)

    def test_soroush_plus_alias(self):
        app = MultiBot()
        client = app.add("soroush-plus", "TEST_SOROUSH")
        self.assertIs(client, app.get("soroush_plus"))

    def test_multiple_bots_on_same_platform(self):
        app = MultiBot()
        first = app.add("bale", "TOKEN_1")
        second = app.add("bale", "TOKEN_2", name="bale_backup")
        self.assertIsNot(first, second)
        self.assertEqual(len(app), 2)

    def test_rejects_unknown_platform(self):
        with self.assertRaises(ValueError):
            MultiBot().add("unknown", "TOKEN")

    def test_rejects_duplicate_name(self):
        app = MultiBot()
        app.add("rubika", "TOKEN")
        with self.assertRaises(ValueError):
            app.add("telegram", "TOKEN", name="rubika")

    def test_remove(self):
        app = MultiBot()
        app.add("rubika", "TOKEN")
        removed = app.remove("rubika")
        self.assertEqual(len(app), 0)
        self.assertFalse(removed._running)

    def test_stop_all(self):
        app = MultiBot()
        first = app.add("rubika", "TOKEN_1")
        second = app.add("telegram", "TOKEN_2")
        first._running = True
        second._running = True
        app.stop()
        self.assertFalse(first._running)
        self.assertFalse(second._running)

    def test_start_requires_registered_bots(self):
        import asyncio
        with self.assertRaisesRegex(RuntimeError, "No bots registered"):
            asyncio.run(MultiBot().start())


if __name__ == "__main__":
    unittest.main()
