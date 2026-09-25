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

YellowPrefetchCurrentSpeciesCore16Locked::
; Prefetch the currently mirrored 16-bit species core into SRAM-bank-15
; scratch. This routine runs from the SRAM service itself.
;
; PRECONDITION:
;   - interrupts disabled
;   - SRAM enabled, bank 15 selected
;   - wYellowCurSpecies contains the logical ID
; OUTPUT:
;   Carry clear: wYellowSpeciesCoreScratch contains species core v1
;   Carry set: no descriptor/record exists for the logical ID
    xor a
    ld [wYellowSpeciesCoreStatus], a

    ld a, [wYellowCurSpecies]
    ld c, a
    ld a, [wYellowCurSpecies + 1]
    ld b, a
    ld hl, wYellowSpeciesCoreScratch
    call YellowCopySpeciesCore16Locked
    ret c

    ld a, 1
    ld [wYellowSpeciesCoreStatus], a
    and a
    ret
