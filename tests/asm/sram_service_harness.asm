; RGBDS link harness for YELLOW's SRAM-bank-15 runtime service.

DEF rRAMG  EQU $0000
DEF rROMB0 EQU $2000
DEF rROMB1 EQU $3000
DEF rRAMB  EQU $4000

SECTION "SRAM Service Harness HRAM", HRAM
hLoadedROMBank:: db

SECTION "SRAM Service Harness WRAM", WRAM0
wHarnessBuffer:: ds 32

DEF YELLOW_EXTERNAL_TABLE_DESCRIPTORS EQU 1

SECTION "SRAM Service Harness Descriptors", ROM0
YellowSpeciesTableDescriptor::
    dw 1
    dw $02
    dw $5000
YellowMoveTableDescriptor::
    dw 1
    dw $02
    dw $5100
YellowItemTableDescriptor::
    dw 1
    dw $02
    dw $5200

SECTION "SRAM Service Harness Species", ROMX[$4000], BANK[$100]
HarnessSpeciesRecord::
    ds 20, $11

SECTION "SRAM Service Harness Move", ROMX[$4100], BANK[$101]
HarnessMoveRecord::
    ds 24, $22

SECTION "SRAM Service Harness Item", ROMX[$4200], BANK[$102]
HarnessItemRecord::
    ds 24, $33

SECTION "SRAM Service Harness Index", ROMX[$5000], BANK[$02]
    db LOW(BANK(HarnessSpeciesRecord)), LOW(HarnessSpeciesRecord - $4000), $40 | HIGH(HarnessSpeciesRecord - $4000)
    ds $100 - 3, $ff
    db LOW(BANK(HarnessMoveRecord)), LOW(HarnessMoveRecord - $4000), $40 | HIGH(HarnessMoveRecord - $4000)
    ds $100 - 3, $ff
    db LOW(BANK(HarnessItemRecord)), LOW(HarnessItemRecord - $4000), $40 | HIGH(HarnessItemRecord - $4000)

SECTION "YELLOW Expansion Service ROM", ROMX[$4000], BANK[$40]
INCLUDE "asm/expansion/sram_service.asm"

ASSERT BANK(YellowSRAMServiceImage) == $40
ASSERT YellowSRAMServiceImage >= $4000 && YellowSRAMServiceImage < $8000
ASSERT YELLOW_SRAM_SERVICE_SIZE <= $0400
ASSERT YellowCopySpeciesCore16Locked >= $BC00 && YellowCopySpeciesCore16Locked < $C000
ASSERT YellowPrefetchCurrentSpeciesCore16Locked >= $BC00 && YellowPrefetchCurrentSpeciesCore16Locked < $C000
ASSERT YellowCopyMoveCore16Locked >= $BC00 && YellowCopyMoveCore16Locked < $C000
ASSERT YellowCopyItemCore16Locked >= $BC00 && YellowCopyItemCore16Locked < $C000
ASSERT BANK(YellowReadMonExtByteLocked) == $40
ASSERT BANK(YellowComposePersistentSpecies16Locked) == $40

SECTION "SRAM Service Harness Calls", ROM0
HarnessInstallService::
    di
    call YellowInstallSRAMServiceLocked
    ei
    ret

HarnessCallSpeciesService::
    di
    call YellowEnterSRAMServiceLocked
    ld bc, 0
    ld hl, wHarnessBuffer
    call YellowCopySpeciesCore16Locked
    push af
    call YellowLeaveSRAMServiceLocked
    pop af
    ei
    ret

HarnessCallMoveService::
    di
    call YellowEnterSRAMServiceLocked
    ld bc, 0
    ld hl, wHarnessBuffer
    call YellowCopyMoveCore16Locked
    push af
    call YellowLeaveSRAMServiceLocked
    pop af
    ei
    ret

HarnessCallItemService::
    di
    call YellowEnterSRAMServiceLocked
    ld bc, 0
    ld hl, wHarnessBuffer
    call YellowCopyItemCore16Locked
    push af
    call YellowLeaveSRAMServiceLocked
    pop af
    ei
    ret
