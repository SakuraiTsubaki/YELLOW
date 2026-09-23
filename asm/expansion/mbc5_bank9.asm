; YELLOW common MBC5 9-bit data-bank ABI
;
; Safety model:
; - Legacy engine execution stays in ROM banks 0..255.
; - ROM banks 256..511 are data-only.
; - ROMB1 must be 0 whenever interrupts are enabled / legacy code is running.
; - High-bank data access occurs only in an interrupt-locked copy window.
;
; This avoids widening every stock Yellow bank tracker before the upper 4 MiB
; can be used for Generation-10-scale data tables.

YellowSetROMBank9Locked::
; Input: BC = bank 0..511 (B bit0 = bank bit 8, C = low byte)
; PRECONDITION: interrupts are disabled and caller will restore a low bank
; before re-enabling them.
    ld a, c
    ld [rROMB0], a
    ld a, b
    and 1
    ld [rROMB1], a
    ret

YellowRestoreLegacyROMBankLocked::
; Input: A = legacy bank 0..255.
; Clears ROMB1 first, then restores the low byte.
; PRECONDITION: interrupts disabled.
    ld b, a
    xor a
    ld [rROMB1], a
    ld a, b
    ld [rROMB0], a
    ret

YellowCopyFromBank9Locked::
; Copy 1..255 bytes from a 9-bit MBC5 ROM bank into WRAM.
;
; Input:
;   BC = source bank 0..511
;   DE = source address in ROMX ($4000..$7fff)
;   HL = destination
;   A  = byte count (1..255)
;
; PRECONDITION:
;   - interrupts disabled
;   - ROMB1 is zero on entry
;   - hLoadedROMBank contains the active legacy low bank
;
; POSTCONDITION:
;   - original legacy low bank restored
;   - ROMB1 cleared to zero
;   - hLoadedROMBank is unchanged
;
; This routine intentionally never executes code from bank 256..511.
    push af

    ; Select requested data bank without changing the legacy tracker.
    ld a, c
    ld [rROMB0], a
    ld a, b
    and 1
    ld [rROMB1], a

    ; Save the legacy bank after BC is no longer needed for bank selection.
    ldh a, [hLoadedROMBank]
    ld b, a

    pop af
    ld c, a
.copy
    ld a, [de]
    inc de
    ld [hli], a
    dec c
    jr nz, .copy

    ; Return to the normal Yellow invariant: ROMB1 == 0.
    xor a
    ld [rROMB1], a
    ld a, b
    ld [rROMB0], a
    ret

YellowDecodeFarPtr9::
; Input: HL -> packed 3-byte far pointer (yellow_farptr9)
; Output: BC = bank 0..511
;         DE = target ROMX address $4000..$7fff
; Clobbers: A
    ld c, [hl]
    inc hl
    ld e, [hl]
    inc hl
    ld a, [hl]

    ld b, 0
    bit 6, a
    jr z, .bank_high_done
    inc b
.bank_high_done
    res 6, a
    and $3f
    or $40
    ld d, a
    ret
