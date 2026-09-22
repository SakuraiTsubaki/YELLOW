import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "expand_yellow_rom", ROOT / "tools" / "expand_yellow_rom.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def fixture(cart_type):
    data = bytearray([0xFF] * mod.ONE_MIB)
    data[0x134:0x140] = b"POKEMON YELL"
    data[0x143] = 0x00 if cart_type == mod.CART_MBC3_RAM_BATTERY else 0x80
    data[0x146] = 0x03
    data[0x147] = cart_type
    data[0x148] = 0x05
    data[0x149] = 0x03
    data[0x14D] = mod.calc_header_checksum(data)
    data[0x14E:0x150] = mod.calc_global_checksum(data).to_bytes(2, "big")
    return bytes(data)


class ExpandYellowRomTests(unittest.TestCase):
    def test_japanese_mbc3_expands_to_two_mib(self):
        source = fixture(mod.CART_MBC3_RAM_BATTERY)
        output, report = mod.expand_mapper_native(source)
        self.assertEqual(len(output), 2 * mod.ONE_MIB)
        self.assertEqual(report["target_banks"], 128)
        self.assertEqual(output[0x147], mod.CART_MBC3_RAM_BATTERY)
        self.assertEqual(output[0x148], 0x06)
        self.assertEqual(output[0x149], 0x03)
        self.assertTrue(mod.checksums_ok(output))

    def test_international_mbc5_expands_to_eight_mib(self):
        source = fixture(mod.CART_MBC5_RAM_BATTERY)
        output, report = mod.expand_mapper_native(source)
        self.assertEqual(len(output), 8 * mod.ONE_MIB)
        self.assertEqual(report["target_banks"], 512)
        self.assertEqual(output[0x147], mod.CART_MBC5_RAM_BATTERY)
        self.assertEqual(output[0x148], 0x08)
        self.assertEqual(output[0x149], 0x03)
        self.assertTrue(mod.checksums_ok(output))

    def test_source_payload_is_preserved_except_header_checksums_and_rom_size(self):
        source = fixture(mod.CART_MBC5_RAM_BATTERY)
        output, _ = mod.expand_mapper_native(source)
        ignored = {0x148, 0x14D, 0x14E, 0x14F}
        for i in range(len(source)):
            if i not in ignored:
                self.assertEqual(output[i], source[i], i)

    def test_new_area_is_ff_filled(self):
        source = fixture(mod.CART_MBC3_RAM_BATTERY)
        output, _ = mod.expand_mapper_native(source)
        self.assertEqual(set(output[len(source):]), {0xFF})

    def test_rejects_bad_checksum(self):
        source = bytearray(fixture(mod.CART_MBC3_RAM_BATTERY))
        source[0x200] ^= 1
        with self.assertRaises(ValueError):
            mod.expand_mapper_native(bytes(source))


if __name__ == "__main__":
    unittest.main()
