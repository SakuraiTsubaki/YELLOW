; YELLOW 16-bit logical-ID index reader.
;
; A table descriptor lives in ROM0 and points at one single-bank array of
; 3-byte yellow_farptr9 entries. This makes the index itself relocatable.

DEF YELLOW_INDEX16_ENTRY_SIZE EQU 3
DEF YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES EQU $1555 ; floor($4000 / 3)
DEF YELLOW_TABLE16_DESCRIPTOR_SIZE EQU 6

MACRO yellow_table16_descriptor
; args: index_label, entry_count
    ASSERT BANK(\1) <= YELLOW_MBC5_MAX_BANK
    ASSERT \1 >= $4000 && \1 < $8000
    ASSERT \2 <= YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES
    dw \2
    dw BANK(\1)
    dw \1
ENDM

YellowIndex16Offset::
; Input: BC = logical ID
; Output: HL = ID * 3
; Clobbers: A
    ld h, b
    ld l, c
    add hl, hl      ; *2
    add hl, bc      ; *3
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
;   HL = ROM0 address of a 6-byte descriptor:
;        dw count, dw index_bank, dw index_address
; Output:
;   BC = target bank 0..511
;   DE = target ROMX address
; Carry set if ID is out of range or the index entry is invalid.
;
; If the ID is in range, the routine temporarily maps the index bank and leaves
; that bank selected on return. Callers that need to preserve the original bank
; should save it with YellowGetLoadedROMBank9 before calling and restore it
; after consuming/copying the resolved target record.

    ; Read count into DE.
    ld a, [hli]
    ld e, a
    ld a, [hli]
    ld d, a

    ; Require BC < DE.
    ld a, b
    cp d
    jr c, .in_range
    jr nz, .out_of_range
    ld a, c
    cp e
    jr nc, .out_of_range

.in_range
    push bc ; save logical ID

    ; Read 9-bit index bank into BC.
    ld a, [hli]
    ld c, a
    ld a, [hli]
    ld b, a

    ; Read index base address into DE.
    ld a, [hli]
    ld e, a
    ld a, [hl]
    ld d, a

    call YellowSetROMBank9

    pop bc
    jp YellowLookupIndex16

.out_of_range
    scf
    ret
