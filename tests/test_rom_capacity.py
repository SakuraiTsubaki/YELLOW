import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capacity", ROOT / "tools" / "check_rom_capacity.py")
capacity = importlib.util.module_from_spec(SPEC)
sys.modules["capacity"] = capacity
SPEC.loader.exec_module(capacity)


class RomCapacityTests(unittest.TestCase):
    def test_exact_32_mib_is_valid(self):
        report = capacity.capacity_report(32 * 1024 * 1024)
        self.assertFalse(report["over_native_limit"])
        self.assertEqual(report["remaining_bytes"], 0)
        self.assertTrue(report["inside_tail_reserve"])

    def test_one_byte_over_32_mib_fails(self):
        report = capacity.capacity_report(32 * 1024 * 1024 + 1)
        self.assertTrue(report["over_native_limit"])

    def test_tail_reserve_begins_after_preferred_budget(self):
        self.assertFalse(capacity.capacity_report(capacity.USABLE_BEFORE_RESERVE)["inside_tail_reserve"])
        self.assertTrue(capacity.capacity_report(capacity.USABLE_BEFORE_RESERVE + 1)["inside_tail_reserve"])

    def test_90_percent_warns_at_first_representable_byte(self):
        self.assertFalse(capacity.capacity_report(capacity.WARN_BYTES - 1)["warn"])
        self.assertTrue(capacity.capacity_report(capacity.WARN_BYTES)["warn"])

    def test_parse_rom_end_symbol(self):
        nm = (
            "08000000 T Start\n"
            "09123456 A __rom_end\n"
            "02000000 B gSomeEwramSymbol\n"
        )
        self.assertEqual(capacity.parse_nm_rom_end(nm), 0x09123456)

    def test_linked_size_math_ignores_padding(self):
        rom_end = 0x08000000 + 19 * 1024 * 1024 + 123
        size = rom_end - capacity.ROM_BASE_ADDRESS
        report = capacity.capacity_report(size)
        self.assertLess(report["size_mib"], 20)
        self.assertGreater(report["remaining_mib"], 12)


if __name__ == "__main__":
    unittest.main()
