import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mon_extension", ROOT / "tools" / "mon_extension.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class MonExtensionTests(unittest.TestCase):
    def test_table_fits_entirely_in_sram_bank_four(self):
        self.assertGreaterEqual(mod.TABLE_OFFSET, 0x8000)
        self.assertLessEqual(mod.TABLE_END, 0xA000)
        self.assertEqual(mod.TABLE_SIZE, 247 * 16)

    def test_jp_and_intl_pc_layouts_cover_same_240_slots(self):
        jp = {
            mod.canonical_pc_slot(box, pos, profile="yellow-jp-legacy")
            for box in range(8)
            for pos in range(30)
        }
        intl = {
            mod.canonical_pc_slot(box, pos, profile="yellow-intl-legacy")
            for box in range(12)
            for pos in range(20)
        }
        expected = set(range(7, 247))
        self.assertEqual(jp, expected)
        self.assertEqual(intl, expected)

    def test_initialization_does_not_touch_legacy_32k(self):
        source = bytes((i * 13) & 0xFF for i in range(0x8000))
        save = source + bytes([0xFF]) * (0x20000 - 0x8000)
        initialized = mod.initialize_table(save)
        self.assertEqual(initialized[:0x8000], source)
        self.assertEqual(
            initialized[mod.TABLE_OFFSET:mod.TABLE_END],
            mod.empty_record() * mod.TOTAL_SLOTS,
        )

    def test_16bit_species_and_move_reconstruction(self):
        self.assertEqual(mod.combine_species(0x34, 0x12), 0x1234)
        self.assertEqual(mod.combine_move(0xCD, 0xAB), 0xABCD)

    def test_slot_boundaries(self):
        self.assertEqual(mod.canonical_party_slot(0), 0)
        self.assertEqual(mod.canonical_party_slot(5), 5)
        self.assertEqual(mod.canonical_daycare_slot(), 6)
        self.assertEqual(
            mod.canonical_pc_slot(7, 29, profile="yellow-jp-legacy"),
            246,
        )
        self.assertEqual(
            mod.canonical_pc_slot(11, 19, profile="yellow-intl-legacy"),
            246,
        )


if __name__ == "__main__":
    unittest.main()
