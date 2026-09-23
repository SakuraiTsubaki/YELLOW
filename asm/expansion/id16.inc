; YELLOW logical 16-bit ID ABI for the original GB runtime.
;
; Convention:
;   BC = general 16-bit logical ID
;   C  = low byte (legacy-compatible ID byte)
;   B  = high byte
;
; Existing low-ID routines may be used only after asserting B == 0.
; New table readers and expanded-save routines consume the full BC value.

DEF YELLOW_ID_INVALID EQU $ffff
DEF YELLOW_ID_MAX     EQU $fffe

MACRO yellow_load_id16
    ld c, [\1]
    ld b, [\1 + 1]
ENDM

MACRO yellow_store_id16
    ld a, c
    ld [\1], a
    ld a, b
    ld [\1 + 1], a
ENDM

MACRO yellow_assert_legacy_id
    ld a, b
    and a
    ASSERT \1 <= $ff
ENDM

; Use these paired variables in the expansion WRAM block.
; They are deliberately separate from legacy aliases until each call path is
; migrated, so the original memory layout is not silently shifted.
MACRO yellow_id16_var
\1Low:: db
\1High:: db
ENDM
