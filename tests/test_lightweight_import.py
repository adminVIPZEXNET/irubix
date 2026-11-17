"""Ensure the core package imports without optional platform dependencies."""
import subprocess
import sys
import unittest


class LightweightImportTests(unittest.TestCase):
    def test_core_import_does_not_load_optional_dependencies(self):
        code = (
            "import sys, ertebat; "
            "assert 'aiohttp' not in sys.modules; "
            "assert not any(name == 'Crypto' or name.startswith('Crypto.') "
            "for name in sys.modules); "
            "assert 'ertebat.shad' not in sys.modules"
        )
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
