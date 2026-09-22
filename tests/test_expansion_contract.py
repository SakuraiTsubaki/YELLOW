import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ExpansionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "expansion.json").read_text(encoding="utf-8"))
        cls.header = (ROOT / "include" / "yellow" / "expansion.h").read_text(encoding="utf-8")

    def test_runtime_is_original_game_boy_not_gba(self):
        self.assertEqual(self.config["target"]["platform_family"], "game-boy")
        self.assertEqual(self.config["target"]["runtime_base"], "original-yellow")
        self.assertTrue(self.config["target"]["gba_remake_is_separate"])

    def test_future_generation_boundary_exists(self):
        policy = self.config["generation_policy"]
        self.assertGreaterEqual(policy["reserved_from"], 10)
        self.assertFalse(policy["guess_future_content_counts"])
        self.assertRegex(self.header, r"YELLOW_GEN_X\s*=\s*10")

    def test_expandable_ids_are_16_bit(self):
        policy = self.config["id_policy"]
        for key in ("species_bits","form_bits","move_bits","item_bits","ability_bits","type_bits","location_bits","map_bits"):
            self.assertEqual(policy[key], 16, key)

    def test_mbc5_expanded_profile_is_9_bit_banked(self):
        profile = self.config["cartridge_profiles"]["expanded"]
        self.assertEqual(profile["mapper"], "MBC5+RAM+BATTERY")
        self.assertEqual(profile["rom_max_bytes"], 8 * 1024 * 1024)
        self.assertEqual(profile["rom_banks"], 512)
        self.assertEqual(profile["rom_bank_bits"], 9)
        self.assertEqual(profile["sram_max_bytes"], 128 * 1024)
        self.assertTrue(self.config["banking_policy"]["require_mbc5_high_rom_bank_bit"])

    def test_legacy_profiles_remain_distinct(self):
        profiles = self.config["save_policy"]["legacy_profiles"]
        self.assertEqual(profiles, ["yellow-jp-legacy", "yellow-intl-legacy"])


if __name__ == "__main__":
    unittest.main()
