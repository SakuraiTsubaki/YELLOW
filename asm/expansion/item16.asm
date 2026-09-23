; YELLOW 16-bit item table resolver.

YellowResolveItemRecord16::
; Input: BC = logical item ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no item record exists.
    ld hl, YellowItemTableDescriptor
    jp YellowResolveTable16
