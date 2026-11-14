"""Ensure importing the core package does not load optional Shad dependencies."""
import subprocess
import sys
import unittest


class LightweightImportTests(unittest.TestCase):
    def test_core_import_is_lazy(self):
        code = (
            "import sys, irubix; "
            "assert 'aiohttp' not in sys.modules; "
            "assert not any(name == 'Crypto' or name.startswith('Crypto.') "
            "for name in sys.modules)"
        )
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
