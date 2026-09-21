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

    def test_future_generation_boundary_exists(self):
        policy = self.config["generation_policy"]
        self.assertGreaterEqual(policy["reserved_from"], 10)
        self.assertFalse(policy["guess_future_content_counts"])
        self.assertRegex(self.header, r"YELLOW_GEN_X\s*=\s*10")

    def test_expandable_ids_are_16_bit(self):
        policy = self.config["id_policy"]
        for key in (
            "species_bits",
            "form_bits",
            "move_bits",
            "item_bits",
            "ability_bits",
            "type_bits",
            "location_bits",
            "map_bits",
        ):
            self.assertEqual(policy[key], 16, key)

    def test_invalid_sentinel_is_outside_valid_range(self):
        policy = self.config["id_policy"]
        self.assertEqual(policy["invalid"], 65535)
        self.assertEqual(policy["max_valid"], 65534)
        self.assertGreater(policy["invalid"], policy["max_valid"])

    def test_save_layout_is_versioned(self):
        save = self.config["save_policy"]
        self.assertEqual(save["schema_version_bits"], 16)
        self.assertGreaterEqual(save["current_schema"], 1)
        self.assertTrue(save["migration_required_on_layout_change"])

    def test_mechanics_are_not_generation_coupled(self):
        mechanics = self.config["mechanics_policy"]
        self.assertTrue(mechanics["generation_number_does_not_imply_mechanics"])
        self.assertTrue(mechanics["use_capability_flags"])


if __name__ == "__main__":
    unittest.main()
