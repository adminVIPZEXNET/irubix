"""Public import paths and direct callable constructors for every platform."""
import subprocess
import sys
import unittest


class PlatformImportTests(unittest.TestCase):
    def test_all_platforms_are_directly_callable(self):
        code = """
from irubix import Rubika, rubika, bale, soroush, telegram

assert callable(Rubika)
assert callable(rubika)
assert callable(bale)
assert callable(soroush)
assert callable(telegram)

assert isinstance(Rubika("TEST_TOKEN"), Rubika.IRubix)
assert isinstance(rubika("TEST_TOKEN"), rubika.IRubix)
assert isinstance(bale("TEST_TOKEN"), bale.IRubix)
assert isinstance(soroush("TEST_TOKEN"), soroush.IRubix)
assert isinstance(telegram("TEST_TOKEN"), telegram.IRubix)

assert Rubika.IRubix is Rubika.Bot
assert bale.IRubix is bale.Bot
assert soroush.IRubix is soroush.Bot
assert telegram.IRubix is telegram.Bot
"""
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
