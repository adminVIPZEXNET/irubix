"""Public import paths and direct callable constructors for every platform."""
import subprocess
import sys
import unittest


class PlatformImportTests(unittest.TestCase):
    def test_all_platforms_are_directly_callable(self):
        code = """
from ertebat import Rubika, rubika, bale, soroush, telegram

assert callable(Rubika)
assert callable(rubika)
assert callable(bale)
assert callable(soroush)
assert callable(telegram)

assert isinstance(Rubika("TEST_TOKEN"), Rubika.Ertebat)
assert isinstance(rubika("TEST_TOKEN"), rubika.Ertebat)
assert isinstance(bale("TEST_TOKEN"), bale.Ertebat)
assert isinstance(soroush("TEST_TOKEN"), soroush.Ertebat)
assert isinstance(telegram("TEST_TOKEN"), telegram.Ertebat)

assert Rubika.Ertebat is Rubika.Bot
assert bale.Ertebat is bale.Bot
assert soroush.Ertebat is soroush.Bot
assert telegram.Ertebat is telegram.Bot
"""
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
