; YELLOW 16-bit move table resolver.

YellowResolveMoveRecord16::
; Input: BC = logical move ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no move record exists.
    ld hl, YellowMoveTableDescriptor
    jp YellowResolveTable16
