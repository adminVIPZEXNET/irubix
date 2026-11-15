"""Public import paths for every supported messaging platform."""

import subprocess
import sys
import unittest


class PlatformImportTests(unittest.TestCase):
    def test_all_platforms_have_a_consistent_import_path(self):
        code = """
from irubix import rubika, bale, soroush, telegram
from irubix import IRubix

assert rubika.IRubix is IRubix
assert callable(bale.IRubix)
assert callable(soroush.IRubix)
assert callable(telegram.IRubix)
"""
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
