; YELLOW 16-bit item table resolver and core-record loader.

INCLUDE "asm/expansion/item_core.inc"

YellowResolveItemRecord16::
; Input: BC = logical item ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no item record exists.
    ld hl, YellowItemTableDescriptor
    jp YellowResolveTable16

YellowCopyItemCore16Locked::
; Input BC = logical item ID
;       HL = WRAM destination
; PRECONDITION: interrupts disabled.
    push hl
    call YellowResolveItemRecord16
    pop hl
    ret c
    ld a, YELLOW_ITEM_CORE_V1_SIZE
    call YellowCopyFromBank9Locked
    and a
    ret
