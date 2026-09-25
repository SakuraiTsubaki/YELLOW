import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "overlay", ROOT / "tools" / "apply_pokeyellow_runtime_overlay.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class RuntimeOverlayTests(unittest.TestCase):
    def test_init_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "init.asm"
            path.write_text(
                "x\n" + mod.INIT_OLD + "y\n",
                encoding="utf-8",
            )
            mod.patch_init(path)
            once = path.read_text(encoding="utf-8")
            mod.patch_init(path)
            twice = path.read_text(encoding="utf-8")
            self.assertEqual(once, twice)
            self.assertIn("YellowInstallSRAMServiceLocked", twice)

    def test_layout_adds_bank_40_and_7f_before_wram(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "layout.link"
            path.write_text("ROM0\nWRAM0\n", encoding="utf-8")
            mod.patch_layout(path)
            text = path.read_text(encoding="utf-8")
            self.assertLess(text.index("ROMX $40"), text.index("WRAM0"))
            self.assertIn("ROMX $7F", text)

    def test_load_mon_data_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "load_mon_data.asm"
            path.write_text(
                "x\n" + mod.LOAD_MON_DATA_OLD + "y\n",
                encoding="utf-8",
            )
            mod.patch_load_mon_data(path)
            once = path.read_text(encoding="utf-8")
            mod.patch_load_mon_data(path)
            twice = path.read_text(encoding="utf-8")
            self.assertEqual(once, twice)
            self.assertIn("YellowSyncLoadedPersistentSpecies16", twice)

    def test_makefile_promotes_ram_header_to_128k(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "Makefile"
            path.write_text(
                'RGBFIXFLAGS += -cjsv -k 01 -l 0x33 -m MBC5+RAM+BATTERY -r 03 -t "POKEMON YELLOW"\n',
                encoding="utf-8",
            )
            mod.patch_makefile(path)
            self.assertIn("-r 04", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
