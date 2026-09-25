; YELLOW persistent Pokémon sidecar runtime bridge.
;
; These routines execute from expansion ROM bank $40, not SRAM. That is
; intentional: code running from SRAM bank 15 cannot switch to persistent SRAM
; bank 4 without unmapping itself.

DEF YELLOW_MON_EXT_SRAM_BANK   EQU 4
DEF YELLOW_MON_EXT_BASE        EQU $A040
DEF YELLOW_MON_EXT_RECORD_SIZE EQU 16
DEF YELLOW_MON_EXT_SLOT_COUNT  EQU 247

DEF YELLOW_MON_EXT_SPECIES_HIGH EQU 0
DEF YELLOW_MON_EXT_MOVE1_HIGH   EQU 1
DEF YELLOW_MON_EXT_MOVE2_HIGH   EQU 2
DEF YELLOW_MON_EXT_MOVE3_HIGH   EQU 3
DEF YELLOW_MON_EXT_MOVE4_HIGH   EQU 4

YellowMonExtAddress::
; Input: A = canonical persistent slot 0..246
; Output: HL = SRAM-bank-4 address of the 16-byte extension record
; Carry set if slot is invalid.
    cp YELLOW_MON_EXT_SLOT_COUNT
    jr nc, .invalid
    ld l, a
    ld h, 0
    add hl, hl ; *2
    add hl, hl ; *4
    add hl, hl ; *8
    add hl, hl ; *16
    ld de, YELLOW_MON_EXT_BASE
    add hl, de
    and a
    ret
.invalid
    scf
    ret

YellowReadMonExtByteLocked::
; Input:
;   A = canonical slot 0..246
;   C = field offset 0..15
; Output:
;   A = byte
;   Carry set for invalid slot/field.
;
; PRECONDITION:
;   - interrupts disabled
;   - executing from ROM bank $40
;   - caller does not require another SRAM bank to stay mapped
; POSTCONDITION:
;   - SRAM disabled
    ld b, a
    ld a, c
    cp YELLOW_MON_EXT_RECORD_SIZE
    jr nc, .invalid
    ld a, b
    call YellowMonExtAddress
    ret c

    ld b, 0
    add hl, bc

    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_MON_EXT_SRAM_BANK
    ld [rRAMB], a
    ld b, [hl]

    xor a
    ld [rRAMG], a
    ld a, b
    and a
    ret
.invalid
    scf
    ret

YellowComposePersistentSpecies16Locked::
; Input:
;   A = legacy species low byte
;   D = canonical persistent slot 0..246
; Output:
;   BC = 16-bit logical species ID
; Carry set if slot is invalid.
    push af
    ld a, d
    ld c, YELLOW_MON_EXT_SPECIES_HIGH
    call YellowReadMonExtByteLocked
    jr c, .invalid
    ld b, a
    pop af
    ld c, a
    and a
    ret
.invalid
    pop af
    scf
    ret

YellowReadPersistentMoveHighLocked::
; Input:
;   A = canonical persistent slot
;   D = move index 0..3
; Output:
;   A = high byte for the selected move
; Carry set if slot or move index is invalid.
    ld e, a
    ld a, d
    cp 4
    jr nc, .invalid
    inc a
    ld c, a
    ld a, e
    jp YellowReadMonExtByteLocked
.invalid
    scf
    ret
