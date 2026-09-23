; YELLOW 16-bit species table resolver and core-record loader.

INCLUDE "asm/expansion/species_core.inc"

YellowResolveSpeciesRecord16::
; Input: BC = logical species ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no species record exists.
    ld hl, YellowSpeciesTableDescriptor
    jp YellowResolveTable16

YellowCopySpeciesCore16Locked::
; Input:
;   BC = logical species ID
;   HL = WRAM destination (at least YELLOW_SPECIES_CORE_V1_SIZE bytes)
; Output:
;   Carry set if species ID is invalid/missing.
;
; PRECONDITION: interrupts disabled.
; POSTCONDITION on success: source bank restored, ROMB1 zero.
    push hl
    call YellowResolveSpeciesRecord16
    pop hl
    ret c
    ld a, YELLOW_SPECIES_CORE_V1_SIZE
    call YellowCopyFromBank9Locked
    and a
    ret
