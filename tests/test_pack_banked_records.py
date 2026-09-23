import importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("pack_banked_records",ROOT/"tools"/"pack_banked_records.py")
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

def unpack(raw):
    if raw==mod.INVALID:return None
    low=raw[0];word=raw[1]|(raw[2]<<8)
    return low|(((word>>14)&1)<<8),0x4000+(word&0x3fff)

class PackBankedRecordsTests(unittest.TestCase):
    def test_record_never_straddles_bank(self):
        banks,index,layout=mod.pack_records([(1,b"A"*0x3ff0),(2,b"B"*0x40)],start_bank=64)
        self.assertEqual(layout[0]["bank"],64);self.assertEqual(layout[1]["bank"],65)
        self.assertEqual(layout[1]["address"],0x4000);self.assertEqual(len(banks),2*mod.BANK_SIZE)
    def test_crosses_bank_255_to_256(self):
        records=[(i,bytes([i&0xff])*0x4000) for i in range(3)]
        banks,index,layout=mod.pack_records(records,start_bank=254,end_bank=256)
        self.assertEqual([x["bank"] for x in layout],[254,255,256])
        self.assertEqual(unpack(index[6:9]),(256,0x4000))
    def test_missing_ids_are_invalid(self):
        _,index,_=mod.pack_records([(2,b"x")],start_bank=64)
        self.assertEqual(index[0:3],mod.INVALID);self.assertEqual(index[3:6],mod.INVALID)
        self.assertEqual(unpack(index[6:9]),(64,0x4000))
    def test_alignment(self):
        _,_,layout=mod.pack_records([(0,b"a"),(1,b"b")],start_bank=64,alignment=16)
        self.assertEqual(layout[0]["bank_offset"],0);self.assertEqual(layout[1]["bank_offset"],16)
    def test_rejects_record_larger_than_bank(self):
        with self.assertRaises(ValueError):mod.pack_records([(0,b"x"*(mod.BANK_SIZE+1))])
    def test_rejects_overflow_past_bank_511(self):
        with self.assertRaises(ValueError):mod.pack_records([(0,b"x"*mod.BANK_SIZE),(1,b"y")],start_bank=511,end_bank=511)
if __name__=="__main__":unittest.main()
