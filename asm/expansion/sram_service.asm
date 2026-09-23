; YELLOW SRAM-bank-15 runtime service.
;
; Include this file while assembling ROM bank $40. Bytes inside the LOAD block
; are emitted in the ROM service bank but linked to execute from SRAM bank 15.

DEF YELLOW_SRAM_SERVICE_ADDR EQU $BC00
DEF YELLOW_SRAM_SERVICE_BANK EQU 15
DEF YELLOW_SRAM_SERVICE_MAX  EQU $0400

YellowSRAMServiceImage::
LOAD "YELLOW SRAM Runtime Service", SRAM[YELLOW_SRAM_SERVICE_ADDR], BANK[YELLOW_SRAM_SERVICE_BANK]

INCLUDE "asm/expansion/mbc5_bank9.asm"
INCLUDE "asm/expansion/index16.asm"
INCLUDE "asm/expansion/species16.asm"
INCLUDE "asm/expansion/move16.asm"
INCLUDE "asm/expansion/item16.asm"

ENDL
YellowSRAMServiceImageEnd::

DEF YELLOW_SRAM_SERVICE_SIZE EQU YellowSRAMServiceImageEnd - YellowSRAMServiceImage
ASSERT YELLOW_SRAM_SERVICE_SIZE <= YELLOW_SRAM_SERVICE_MAX

YellowInstallSRAMServiceLocked::
; PRECONDITION:
;   - executing from the low expansion service bank (normally bank $40)
;   - interrupts disabled
; POSTCONDITION:
;   - service image copied to SRAM bank 15 at $BC00
;   - SRAM disabled
    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_SRAM_SERVICE_BANK
    ld [rRAMB], a

    ld hl, YellowSRAMServiceImage
    ld de, YELLOW_SRAM_SERVICE_ADDR
    ld bc, YELLOW_SRAM_SERVICE_SIZE
.copy
    ld a, [hli]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, .copy

    xor a
    ld [rRAMG], a
    ret

YellowEnterSRAMServiceLocked::
; Enable and select SRAM bank 15. Callers can then call service labels such as
; YellowCopySpeciesCore16Locked, which are linked to $BC00+ addresses.
    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_SRAM_SERVICE_BANK
    ld [rRAMB], a
    ret

YellowLeaveSRAMServiceLocked::
    xor a
    ld [rRAMG], a
    ret
