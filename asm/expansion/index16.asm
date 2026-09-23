; YELLOW 16-bit logical-ID index reader.
;
; The generated index contains 3-byte yellow_farptr9 entries.
; Input logical ID is BC. The index itself is constrained to <= 5461 entries
; when placed wholly in one 16 KiB ROMX bank (3 bytes per entry).

DEF YELLOW_INDEX16_ENTRY_SIZE EQU 3
DEF YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES EQU $1555 ; floor($4000 / 3)

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
;   DE = base address of a single-bank 3-byte index
; Output:
;   BC = target bank 0..511
;   DE = target ROMX address
; Carry set if entry is invalid FF FF FF.
;
; Caller is responsible for range-checking against the generated table count.
    push de
    call YellowIndex16Offset
    pop de
    add hl, de

    ; Preserve the start of the entry while checking the invalid sentinel.
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
    and a           ; clear carry on a valid pointer
    ret

.invalid
    pop hl
    scf
    ret
