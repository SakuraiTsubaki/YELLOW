; YELLOW 16-bit species table resolver.
;
; Generated content provides YellowSpeciesTableDescriptor in ROM0.
; The descriptor points to a 3-byte farptr9 index whose array position is the
; 16-bit logical species ID.

YellowResolveSpeciesRecord16::
; Input: BC = logical species ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no species record exists.
    ld hl, YellowSpeciesTableDescriptor
    jp YellowResolveTable16
