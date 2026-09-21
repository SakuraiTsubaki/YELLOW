import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit", ROOT / "tools" / "yellow_rom_save_audit.py")
audit = importlib.util.module_from_spec(SPEC)
sys.modules["audit"] = audit
SPEC.loader.exec_module(audit)


class YellowSaveAuditTests(unittest.TestCase):
    def _synthetic(self, profile):
        image = bytearray(audit.SRAM_SIZE)
        start = audit.sram_file_offset(1, profile.main_start_cpu)
        check = audit.sram_file_offset(1, profile.main_checksum_cpu)
        for i in range(profile.main_length):
            image[start + i] = (i * 17 + 3) & 0xFF
        image[check] = audit.checksum8(image[start:start + profile.main_length])
        return image

    def test_jp_main_checksum_offset_and_length(self):
        result = audit._main_check(self._synthetic(audit.JP), audit.JP)
        self.assertTrue(result["ok"])
        self.assertEqual(result["data_offset"], 0x2598)
        self.assertEqual(result["checksum_offset"], 0x3594)

    def test_intl_main_checksum_offset_and_length(self):
        result = audit._main_check(self._synthetic(audit.INTL), audit.INTL)
        self.assertTrue(result["ok"])
        self.assertEqual(result["data_offset"], 0x2598)
        self.assertEqual(result["checksum_offset"], 0x3523)

    def test_box_capacity_is_240_in_both_profiles(self):
        self.assertEqual(audit.JP.total_boxes * audit.JP.mons_per_box, 240)
        self.assertEqual(audit.INTL.total_boxes * audit.INTL.mons_per_box, 240)

    def test_wrapper_candidates_do_not_assume_metadata_side(self):
        raw = bytes(44) + bytes(audit.SRAM_SIZE)
        candidates = list(audit.candidate_sram_images(raw))
        self.assertEqual([x[0] for x in candidates], ["prefix", "suffix"])
        self.assertEqual(candidates[-1][1], 44)


if __name__ == "__main__":
    unittest.main()
