import hashlib
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "expand_yellow_save", ROOT / "tools" / "expand_yellow_save.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ExpandYellowSaveTests(unittest.TestCase):
    def legacy_fixture(self):
        return bytes((i * 37 + 11) & 0xFF for i in range(mod.LEGACY_SIZE))

    def test_expands_32k_to_128k(self):
        legacy = self.legacy_fixture()
        expanded, report = mod.expand_save(
            legacy, source_profile=mod.PROFILE_JP
        )
        self.assertEqual(len(expanded), 128 * 1024)
        self.assertEqual(report["legacy_banks"], 4)
        self.assertEqual(report["expanded_banks"], 16)
        self.assertEqual(report["extension_banks"], 12)

    def test_first_four_sram_banks_are_byte_exact(self):
        legacy = self.legacy_fixture()
        expanded, report = mod.expand_save(
            legacy, source_profile=mod.PROFILE_INTL
        )
        self.assertEqual(expanded[:mod.LEGACY_SIZE], legacy)
        self.assertTrue(report["legacy_prefix_preserved"])

    def test_header_starts_at_bank_four(self):
        legacy = self.legacy_fixture()
        expanded, _ = mod.expand_save(
            legacy, source_profile=mod.PROFILE_JP
        )
        self.assertEqual(expanded[0x8000:0x8004], b"YLX1")
        parsed = mod.parse_header(expanded)
        self.assertEqual(parsed["schema_version"], 1)
        self.assertEqual(parsed["source_profile"], "yellow-jp-legacy")
        self.assertEqual(
            parsed["source_sha256"], hashlib.sha256(legacy).hexdigest()
        )

    def test_checksums_cover_extension_header_and_payload(self):
        legacy = self.legacy_fixture()
        expanded, _ = mod.expand_save(
            legacy, source_profile=mod.PROFILE_INTL
        )
        parsed = mod.parse_header(expanded)
        self.assertTrue(parsed["header_sum16_ok"])
        self.assertTrue(parsed["payload_sum16_ok"])

        damaged = bytearray(expanded)
        damaged[-1] ^= 1
        parsed = mod.parse_header(bytes(damaged))
        self.assertFalse(parsed["payload_sum16_ok"])

    def test_payload_is_ff_initialized(self):
        legacy = self.legacy_fixture()
        expanded, _ = mod.expand_save(
            legacy, source_profile=mod.PROFILE_JP
        )
        payload = expanded[mod.EXT_OFFSET + mod.HEADER_SIZE:]
        self.assertEqual(set(payload), {0xFF})

    def test_rejects_non_32k_legacy_save(self):
        with self.assertRaises(ValueError):
            mod.expand_save(
                b"\x00" * 123,
                source_profile=mod.PROFILE_JP,
            )


if __name__ == "__main__":
    unittest.main()
