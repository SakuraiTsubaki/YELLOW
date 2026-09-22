import unittest


def encode_species(value: int):
    if not 0 <= value <= 0xFFFE:
        raise ValueError(value)
    return value & 0x7FF, (value >> 11) & 0x7, (value >> 14) & 0x3


def decode_species(low: int, mid: int, top: int):
    return low | (mid << 11) | (top << 14)


def encode_item(value: int):
    if not 0 <= value <= 0xFFFE:
        raise ValueError(value)
    return value & 0x3FF, (value >> 10) & 0x3F


def decode_item(low: int, high: int):
    return low | (high << 10)


class Gen10StorageModelTests(unittest.TestCase):
    def test_species_roundtrip_boundaries(self):
        for value in (0, 1, 1572, 2047, 2048, 16383, 16384, 65534):
            self.assertEqual(decode_species(*encode_species(value)), value)

    def test_item_roundtrip_boundaries(self):
        for value in (0, 1, 873, 1023, 1024, 4095, 65534):
            self.assertEqual(decode_item(*encode_item(value)), value)

    def test_invalid_sentinel_is_not_encodable_as_content(self):
        with self.assertRaises(ValueError):
            encode_species(0xFFFF)
        with self.assertRaises(ValueError):
            encode_item(0xFFFF)

    def test_stage1_consumes_exactly_all_legacy_spare_bits(self):
        old_spare_bits = 6 + 3 + 2
        required_high_bits = (16 - 11) + (16 - 10)
        self.assertEqual(old_spare_bits, 11)
        self.assertEqual(required_high_bits, old_spare_bits)


if __name__ == "__main__":
    unittest.main()
