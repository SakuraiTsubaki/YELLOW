import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_integrated",
    ROOT / "tools" / "verify_integrated_yellow_rom.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class VerifyIntegratedYellowRomTests(unittest.TestCase):
    def test_rejects_wrong_size(self):
        with self.assertRaises(ValueError):
            mod.verify(b"\x00" * 0x200)


if __name__ == "__main__":
    unittest.main()
