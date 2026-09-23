; YELLOW 16-bit logical-ID index reader.
;
; Index arrays live in legacy-addressable ROM banks 0..255.
; Entries may point to records anywhere in the full 0..511 MBC5 range.
; Consumers copy resolved records to WRAM through YellowCopyFromBank9Locked.

DEF YELLOW_INDEX16_ENTRY_SIZE EQU 3
DEF YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES EQU $1555 ; floor($4000 / 3)
DEF YELLOW_TABLE16_DESCRIPTOR_SIZE EQU 6

MACRO yellow_table16_descriptor
; args: index_label, entry_count
    ASSERT BANK(\1) <= $ff
    ASSERT \1 >= $4000 && \1 < $8000
    ASSERT \2 <= YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES
    dw \2
    dw BANK(\1)
    dw \1
ENDM

YellowIndex16Offset::
; Input: BC = logical ID
; Output: HL = ID * 3
    ld h, b
    ld l, c
    add hl, hl
    add hl, bc
    ret

YellowLookupIndex16::
; Input:
;   BC = logical ID
;   DE = base address of a currently mapped 3-byte index
; Output:
;   BC = target bank 0..511
;   DE = target ROMX address
; Carry set if entry is invalid FF FF FF.
    push de
    call YellowIndex16Offset
    pop de
    add hl, de

    push hl
    ld a, [hli]
    cp $ff
    jr nz, .valid
    ld a, [hli]
    cp $ff
    jr nz, .valid
    ld a, [hl]
    cp $ff
    jr z, .invalid

.valid
    pop hl
    call YellowDecodeFarPtr9
    and a
    ret

.invalid
    pop hl
    scf
    ret

YellowResolveTable16::
; Input:
;   BC = logical ID
;   HL = ROM0 address of descriptor:
;        dw count, dw index_bank, dw index_address
; Output:
;   BC = target bank 0..511
;   DE = target ROMX address
; Carry set if ID is out of range, descriptor invalid, or entry invalid.
;
; The index bank is constrained to 0..255. The routine maps that bank
; temporarily and restores the caller's legacy bank before returning.
; Global invariant: ROMB1 == 0 whenever normal Yellow code is executing.

    ; Count -> DE; require BC < DE.
    ld a, [hli]
    ld e, a
    ld a, [hli]
    ld d, a

    ld a, b
    cp d
    jr c, .in_range
    jr nz, .out_of_range
    ld a, c
    cp e
    jr nc, .out_of_range

.in_range
    ; Save caller bank first, then logical ID.
    ldh a, [hLoadedROMBank]
    push af
    push bc

    ; Descriptor index-bank word. Generated descriptors require high byte 0.
    ld a, [hli]
    ld c, a
    ld a, [hli]
    and a
    jr nz, .bad_descriptor

    ; Index base -> DE.
    ld a, [hli]
    ld e, a
    ld a, [hl]
    ld d, a

    ; Map the low index bank.
    ld a, c
    ldh [hLoadedROMBank], a
    ld [rROMB0], a

    ; Restore logical ID and resolve the 3-byte entry.
    pop bc
    call YellowLookupIndex16
    jr c, .lookup_invalid

    ; Preserve resolved address in HL while restoring caller bank.
    ld h, d
    ld l, e
    pop af
    ldh [hLoadedROMBank], a
    ld [rROMB0], a
    ld d, h
    ld e, l
    and a
    ret

.bad_descriptor
    pop bc
    pop af
    scf
    ret

.lookup_invalid
    pop af
    ldh [hLoadedROMBank], a
    ld [rROMB0], a
    scf
    ret

.out_of_range
    scf
    ret
