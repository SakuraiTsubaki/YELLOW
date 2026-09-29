; YELLOW 16-bit move table resolver and core-record loader.

INCLUDE "asm/expansion/move_core.inc"

YellowResolveMoveRecord16::
; Input: BC = logical move ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no move record exists.
    ld hl, YellowMoveTableDescriptor
    jp YellowResolveTable16

YellowCopyMoveCore16Locked::
; Input BC = logical move ID
;       HL = WRAM destination
; PRECONDITION: interrupts disabled.
    push hl
    call YellowResolveMoveRecord16
    pop hl
    ret c
    ld a, YELLOW_MOVE_CORE_V1_SIZE
    call YellowCopyFromBank9Locked
    and a
    ret

YellowPrefetchCurrentMoveCore16Locked::
; Prefetch the current logical move core into SRAM-bank-15 scratch.
;
; PRECONDITION:
;   - interrupts disabled
;   - SRAM enabled, bank 15 selected
;   - wYellowMoveNum contains the selected 16-bit logical move ID
; OUTPUT:
;   Carry clear: wYellowMoveCoreScratch contains move core v1
;   Carry set: descriptor/record missing for the logical ID
    xor a
    ld [wYellowMoveCoreStatus], a

    ld a, [wYellowMoveNum]
    ld c, a
    ld a, [wYellowMoveNum + 1]
    ld b, a
    ld hl, wYellowMoveCoreScratch
    call YellowCopyMoveCore16Locked
    ret c

    ld a, 1
    ld [wYellowMoveCoreStatus], a
    and a
    ret
