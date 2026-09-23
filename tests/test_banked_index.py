import importlib.util
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "build_banked_index", ROOT/"tools"/"build_banked_index.py"
)
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class BankedIndexTests(unittest.TestCase):
    def test_crosses_8bit_bank_boundary(self):
        rows=[
            (1,0x001,0x4000),
            (255,0x0ff,0x7fff),
            (256,0x100,0x4000),
            (1025,0x1ff,0x6123),
        ]
        data=mod.build_index(rows)
        for logical_id,bank,address in rows:
            raw=data[logical_id*3:logical_id*3+3]
            self.assertEqual(mod.unpack_farptr9(raw),(bank,address))

    def test_missing_id_is_invalid_pointer(self):
        data=mod.build_index([(2,1,0x4000)],max_id=4)
        self.assertEqual(data[0:3],mod.INVALID)
        self.assertEqual(data[3:6],mod.INVALID)
        self.assertEqual(data[6:9],mod.pack_farptr9(1,0x4000))
        self.assertEqual(data[9:12],mod.INVALID)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            mod.build_index([(1,1,0x4000),(1,2,0x4000)])

    def test_invalid_id_sentinel_not_content(self):
        with self.assertRaises(ValueError):
            mod.build_index([(0xffff,1,0x4000)])

    def test_index_for_two_thousand_species_is_small(self):
        data=mod.build_index([],max_id=1999)
        self.assertEqual(len(data),6000)
        self.assertLess(len(data),0x4000)


if __name__=="__main__":
    unittest.main()
