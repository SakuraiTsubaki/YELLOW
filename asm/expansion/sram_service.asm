; YELLOW SRAM-bank-15 runtime service.
;
; Include this file while assembling ROM bank $40. Bytes inside the LOAD block
; are emitted in the ROM service bank but linked to execute from SRAM bank 15.

DEF YELLOW_SRAM_SERVICE_ADDR EQU $BC00
DEF YELLOW_SRAM_SERVICE_BANK EQU 15
DEF YELLOW_SRAM_SERVICE_MAX  EQU $0400

YellowSRAMServiceImage::
LOAD "YELLOW SRAM Runtime Service", SRAM[YELLOW_SRAM_SERVICE_ADDR], BANK[YELLOW_SRAM_SERVICE_BANK]

INCLUDE "asm/expansion/wram_id16.asm"
INCLUDE "asm/expansion/mbc5_bank9.asm"
INCLUDE "asm/expansion/index16.asm"
INCLUDE "asm/expansion/species16.asm"
INCLUDE "asm/expansion/move16.asm"
INCLUDE "asm/expansion/item16.asm"

YellowInitRuntimeStateLocked::
; PRECONDITION:
;   - SRAM enabled
;   - SRAM bank 15 selected
;   - interrupts disabled
; Clears only the volatile runtime-state window. It never touches the service
; image at $BC00 or the persistent banks 0..14.
    xor a
    ld hl, YELLOW_RUNTIME_BASE
    ld bc, YELLOW_RUNTIME_STATE_SIZE
.clear
    ld [hli], a
    dec bc
    ld a, b
    or c
    jr nz, .clear

    ld hl, YELLOW_RUNTIME_MAGIC
    ld a, $59 ; Y
    ld [hli], a
    ld a, $52 ; R
    ld [hli], a
    ld a, $54 ; T
    ld [hli], a
    ld a, $31 ; 1
    ld [hli], a

    ld a, LOW(YELLOW_RUNTIME_VERSION_VALUE)
    ld [hli], a
    ld a, HIGH(YELLOW_RUNTIME_VERSION_VALUE)
    ld [hl], a
    ret

; Default descriptors live with the SRAM service so stock Yellow ROM0 does not
; need to surrender any space. Real generated tables may define
; YELLOW_EXTERNAL_TABLE_DESCRIPTORS and provide replacement descriptors.
IF !DEF(YELLOW_EXTERNAL_TABLE_DESCRIPTORS)
YellowSpeciesTableDescriptor::
    dw 0, 0, 0
YellowMoveTableDescriptor::
    dw 0, 0, 0
YellowItemTableDescriptor::
    dw 0, 0, 0
ENDC

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
;   - volatile runtime state initialized with YRT1/version
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

    call YellowInitRuntimeStateLocked

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

; ROM-resident bridge for persistent sidecar banks 4..14.
INCLUDE "asm/expansion/mon_sidecar_runtime.asm"
