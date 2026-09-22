import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "farptr9", ROOT / "tools" / "farptr9.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FarPtr9Tests(unittest.TestCase):
    def test_roundtrip_boundaries(self):
        for bank in (0, 1, 0x7F, 0xFF, 0x100, 0x101, 0x1FE, 0x1FF):
            for address in (0x4000, 0x4001, 0x5ABC, 0x7FFE, 0x7FFF):
                raw = mod.pack_farptr9(bank, address)
                self.assertEqual(len(raw), 3)
                self.assertEqual(mod.unpack_farptr9(raw), (bank, address))

    def test_high_bank_bit_is_not_lost(self):
        low = mod.pack_farptr9(0x00, 0x4567)
        high = mod.pack_farptr9(0x100, 0x4567)
        self.assertNotEqual(low, high)
        self.assertEqual(low[0], high[0])
        self.assertNotEqual(low[2], high[2])

    def test_rejects_non_romx_addresses(self):
        for address in (0x0000, 0x3FFF, 0x8000, 0xFFFF):
            with self.assertRaises(ValueError):
                mod.pack_farptr9(1, address)

    def test_rejects_bank_512(self):
        with self.assertRaises(ValueError):
            mod.pack_farptr9(0x200, 0x4000)

    def test_reserved_bit_rejected(self):
        with self.assertRaises(ValueError):
            mod.unpack_farptr9(bytes((0, 0, 0x80)))


if __name__ == "__main__":
    unittest.main()
