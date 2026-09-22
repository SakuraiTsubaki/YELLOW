; YELLOW common MBC5 9-bit bank-switch ABI
;
; Integration contract:
; - rROMB0 = $2000 (MBC5 ROM bank low byte)
; - rROMB1 = $3000 (MBC5 ROM bank high bit)
; - hLoadedROMBank remains the legacy low-byte tracker.
; - hLoadedROMBankHigh is one new HRAM byte holding bank bit 8.
; - JumpToAddress is the existing Yellow jp hl trampoline.
;
; Existing low-bank callers can continue using the legacy ABI once their common
; switch routine is changed to clear hLoadedROMBankHigh/rROMB1. New content in
; banks 256..511 uses YellowBankswitch9.

YellowSetROMBank9::
; Input: BC = bank 0..511 (B bit0 = bit8, C = low byte)
; Preserves: DE, HL
    ld a, c
    ldh [hLoadedROMBank], a
    ld [rROMB0], a

    ld a, b
    and 1
    ldh [hLoadedROMBankHigh], a
    ld [rROMB1], a
    ret

YellowBankswitchCommonLow::
; Compatibility replacement for the old 8-bit BankswitchCommon.
; Input: A = bank 0..255.
; Important: explicitly clears the MBC5 high bit so returning from a high bank
; can never leave legacy code in bank 256+ by accident.
    ldh [hLoadedROMBank], a
    ld [rROMB0], a
    xor a
    ldh [hLoadedROMBankHigh], a
    ld [rROMB1], a
    ret

YellowBankswitch9::
; Input: BC = bank 0..511, HL = callable address in $4000..$7fff.
; Saves/restores both current bank bytes around the far call.
    ldh a, [hLoadedROMBankHigh]
    ld d, a
    ldh a, [hLoadedROMBank]
    ld e, a
    push de

    call YellowSetROMBank9
    call JumpToAddress

    pop de
    ld b, d
    ld c, e
    jp YellowSetROMBank9

YellowDecodeFarPtr9::
; Input: HL -> packed 3-byte far pointer (yellow_farptr9)
; Output: BC = bank 0..511
;         DE = ROMX CPU address $4000..$7fff
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

MACRO yellow_farcall9
    ld bc, BANK(\1)
    ld hl, \1
    call YellowBankswitch9
ENDM

MACRO yellow_farjp9
    ld bc, BANK(\1)
    ld hl, \1
    jp YellowBankswitch9
ENDM
