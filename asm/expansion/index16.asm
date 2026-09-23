; YELLOW 16-bit logical-ID index reader.
;
; The generated index contains 3-byte yellow_farptr9 entries.
; Input logical ID is BC. The index itself is constrained to <= 5461 entries
; when placed wholly in one 16 KiB ROMX bank (3 bytes per entry).
;
; For Generation-10-scale species/move/item catalogs this is sufficient while
; avoiding the original "one-byte index times fixed record size" design.
; If a table ever exceeds 5461 logical IDs, a paged index can replace this ABI
; without changing the logical IDs themselves.

DEF YELLOW_INDEX16_ENTRY_SIZE EQU 3
DEF YELLOW_INDEX16_MAX_SINGLE_BANK_ENTRIES EQU $1555 ; floor($4000 / 3)

; Contract for generated symbols:
;   YellowSpeciesIndex16       ; array of farptr9 entries
;   YellowSpeciesIndex16Count  ; number of entries
;
; Similar indexes are generated for moves and items.

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

    ld a, [hli]
    cp $ff
    jr nz, .valid
    ld a, [hli]
    cp $ff
    jr nz, .invalid_mixed
    ld a, [hl]
    cp $ff
    jr z, .invalid
.invalid_mixed
    ; FF in bank-low is valid only if the full entry is not FF FF FF.
    dec hl
    dec hl
.valid
    jp YellowDecodeFarPtr9
.invalid
    scf
    ret
