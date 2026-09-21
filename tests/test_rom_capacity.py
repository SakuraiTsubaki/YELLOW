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

    def test_90_percent_warns(self):
        size = int(capacity.MAX_BYTES * 0.90)
        self.assertTrue(capacity.capacity_report(size)["warn"])


if __name__ == "__main__":
    unittest.main()
