; YELLOW 16-bit move table resolver and core loader.

INCLUDE "asm/expansion/move_core.inc"

YellowResolveMoveRecord16::
; Input: BC = logical move ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no move record exists.
    ld hl, YellowMoveTableDescriptor
    jp YellowResolveTable16

YellowCopyMoveCore16Locked::
; Input: BC = logical move ID, HL = WRAM destination.
; PRECONDITION: interrupts disabled.
    push hl
    call YellowResolveMoveRecord16
    pop hl
    ret c
    ld a, YELLOW_MOVE_CORE_V1_SIZE
    call YellowCopyFromBank9Locked
    and a
    ret
