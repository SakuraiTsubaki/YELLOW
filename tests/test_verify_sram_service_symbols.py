import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_sram_service_symbols",
    ROOT / "tools" / "verify_sram_service_symbols.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class VerifySramServiceSymbolsTests(unittest.TestCase):
    def test_accepts_expected_rom_and_sram_placement(self):
        symbols = mod.parse_symbols(
            "40:4000 YellowSRAMServiceImage\n"
            "0f:bc40 YellowCopySpeciesCore16Locked\n"
            "0f:bc80 YellowCopyMoveCore16Locked\n"
            "0f:bcc0 YellowCopyItemCore16Locked\n"
        )
        report = mod.verify(symbols)
        self.assertEqual(
            report["YellowSRAMServiceImage"]["bank"], 0x40
        )
        self.assertEqual(
            report["YellowCopySpeciesCore16Locked"]["bank"], 0x0F
        )

    def test_rejects_service_outside_reserved_window(self):
        symbols = mod.parse_symbols(
            "40:4000 YellowSRAMServiceImage\n"
            "0f:bbff YellowCopySpeciesCore16Locked\n"
            "0f:bc80 YellowCopyMoveCore16Locked\n"
            "0f:bcc0 YellowCopyItemCore16Locked\n"
        )
        with self.assertRaises(ValueError):
            mod.verify(symbols)


if __name__ == "__main__":
    unittest.main()
