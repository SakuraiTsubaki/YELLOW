; YELLOW 16-bit move-name resolver.

INCLUDE "asm/expansion/move_name.inc"

YellowResolveMoveNameRecord16::
; Input: BC = logical move ID
; Output: BC = record bank 0..511, DE = record ROMX address
; Carry set if no name record exists.
    ld hl, YellowMoveNameTableDescriptor
    jp YellowResolveTable16

YellowCopyMoveName16Locked::
; Input: BC = logical move ID
;        HL = destination for 13-byte move-name v1 record
; PRECONDITION: interrupts disabled.
    push hl
    call YellowResolveMoveNameRecord16
    pop hl
    ret c
    ld a, YELLOW_MOVE_NAME_V1_SIZE
    call YellowCopyFromBank9Locked
    and a
    ret

YellowPrefetchCurrentMoveName16Locked::
; PRECONDITION:
;   - interrupts disabled
;   - SRAM enabled, bank 15 selected
;   - wYellowMoveNum contains selected 16-bit move ID
    xor a
    ld [wYellowMoveNameStatus], a

    ld a, [wYellowMoveNum]
    ld c, a
    ld a, [wYellowMoveNum + 1]
    ld b, a
    ld hl, wYellowMoveNameScratch
    call YellowCopyMoveName16Locked
    ret c

    ld a, 1
    ld [wYellowMoveNameStatus], a
    and a
    ret
