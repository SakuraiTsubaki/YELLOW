import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MoveLegacyProjectionTests(unittest.TestCase):
    def test_bridge_has_explicit_projection_guards(self):
        text = (ROOT / "asm" / "expansion" / "pokeyellow_bridge.asm").read_text(encoding="utf-8")
        for token in (
            "YMC_FLAG_LEGACY_VIEW_SAFE",
            "NUM_ATTACK_ANIMS + 1",
            "NUM_MOVE_EFFECTS + 1",
            "YMN_MAX_CHARS + 1",
            "wYellowMoveCoreStatus",
            "wYellowMoveNameStatus",
        ):
            self.assertIn(token, text)

    def test_high_id_projection_is_separate_from_low_id_path(self):
        text = (ROOT / "asm" / "expansion" / "pokeyellow_bridge.asm").read_text(encoding="utf-8")
        self.assertIn("ld a, [wYellowMoveNum + 1]", text)
        self.assertIn("jr z, .fail", text)

    def test_projected_view_writes_all_six_stock_fields(self):
        text = (ROOT / "asm" / "expansion" / "pokeyellow_bridge.asm").read_text(encoding="utf-8")
        for field in (
            "YMC_ANIMATION",
            "YMC_EFFECT",
            "YMC_POWER",
            "YMC_TYPE",
            "YMC_ACCURACY",
            "YMC_PP",
        ):
            self.assertIn("wYellowMoveCoreScratch + " + field, text)

    def test_move_name_record_is_fixed_and_stock_width_limited(self):
        text = (ROOT / "asm" / "expansion" / "move_name.inc").read_text(encoding="utf-8")
        self.assertIn("YELLOW_MOVE_NAME_V1_SIZE EQU 13", text)
        self.assertIn("YMN_MAX_CHARS            EQU 12", text)


if __name__ == "__main__":
    unittest.main()
