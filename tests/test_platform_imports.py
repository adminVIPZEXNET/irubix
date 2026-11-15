"""Public import paths for every supported messaging platform."""

import subprocess
import sys
import unittest


class PlatformImportTests(unittest.TestCase):
    def test_all_platforms_have_a_consistent_import_path(self):
        code = """
from irubix import Rubika, rubika, bale, soroush, telegram

assert Rubika.IRubix is Rubika.Bot
assert rubika.IRubix is Rubika.IRubix
try:
    from irubix import IRubix
except ImportError:
    pass
else:
    raise AssertionError('Legacy top-level IRubix import must not be exposed')
assert callable(bale.IRubix)
assert callable(soroush.IRubix)
assert callable(telegram.IRubix)
"""
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
