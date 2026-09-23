import importlib.util
import pathlib
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("audit_mapper_paths",ROOT/"tools"/"audit_mapper_paths.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class MapperAuditTests(unittest.TestCase):
    def test_rom_scanner_finds_direct_register_patterns(self):
        data=bytearray([0]*0x200)
        data[0x147]=0x1B
        data[0x20:0x23]=bytes((0xEA,0x00,0x20))
        data[0x30:0x33]=bytes((0xEA,0x00,0x30))
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"x.gb"
            p.write_bytes(data)
            report=mod.scan_rom(p)
        self.assertEqual(report["registers"]["0x2000"]["candidate_count"],1)
        self.assertEqual(report["registers"]["0x3000"]["candidate_count"],1)

    def test_source_scanner_separates_low_and_high_mbc5_writes(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"x.asm").write_text(
                "ld [rROMB], a\nld [rROMB0], a\nld [rROMB1], a\n",
                encoding="utf-8",
            )
            report=mod.scan_source(root)
        self.assertEqual(report["counts"]["rROMB"],1)
        self.assertEqual(report["counts"]["rROMB0"],1)
        self.assertEqual(report["counts"]["rROMB1"],1)
        self.assertTrue(report["mbc5_high_bank_explicitly_used"])

if __name__=="__main__":
    unittest.main()
