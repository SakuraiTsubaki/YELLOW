; Compile-time harness for YELLOW's original-GB expansion ABI.

DEF rROMB0 EQU $2000
DEF rROMB1 EQU $3000

SECTION "Harness HRAM", HRAM
hLoadedROMBank:: db

INCLUDE "asm/expansion/id16.inc"
INCLUDE "asm/expansion/farptr9.inc"
INCLUDE "asm/expansion/mbc5_bank9.asm"
INCLUDE "asm/expansion/index16.asm"
INCLUDE "asm/expansion/species16.asm"
INCLUDE "asm/expansion/move16.asm"
INCLUDE "asm/expansion/item16.asm"
INCLUDE "asm/expansion/wram_id16.asm"

SECTION "Harness WRAM", WRAM0
wHarnessBuffer:: ds 16

SECTION "Harness Low Data", ROMX[$4000], BANK[$01]
HarnessLowData::
    db $11, $12, $13, $14

SECTION "Harness High Data", ROMX[$4000], BANK[$100]
HarnessHighData::
    db $21, $22, $23, $24

SECTION "Harness Top Data", ROMX[$7ffc], BANK[$1ff]
HarnessTopData::
    db $31, $32, $33, $34

SECTION "Harness Species Index", ROMX[$5000], BANK[$02]
YellowSpeciesIndex16::
    yellow_farptr9 HarnessLowData
    yellow_farptr9 HarnessHighData
    yellow_farptr9 HarnessTopData
YellowSpeciesIndex16End::

SECTION "Harness Move Index", ROMX[$5100], BANK[$02]
YellowMoveIndex16::
    yellow_farptr9 HarnessHighData
    yellow_farptr9 HarnessLowData
YellowMoveIndex16End::

SECTION "Harness Item Index", ROMX[$5200], BANK[$02]
YellowItemIndex16::
    yellow_farptr9 HarnessTopData
    yellow_farptr9 HarnessLowData
YellowItemIndex16End::

SECTION "Harness Descriptors", ROM0
YellowSpeciesTableDescriptor::
    yellow_table16_descriptor YellowSpeciesIndex16, 3
YellowMoveTableDescriptor::
    yellow_table16_descriptor YellowMoveIndex16, 2
YellowItemTableDescriptor::
    yellow_table16_descriptor YellowItemIndex16, 2
HarnessDescriptorsEnd::

ASSERT YellowSpeciesIndex16End - YellowSpeciesIndex16 == 9
ASSERT YellowMoveIndex16End - YellowMoveIndex16 == 6
ASSERT YellowItemIndex16End - YellowItemIndex16 == 6
ASSERT HarnessDescriptorsEnd - YellowSpeciesTableDescriptor == 18

SECTION "Harness Calls", ROM0
HarnessCopyHighData::
    ld bc, BANK(HarnessHighData)
    ld de, HarnessHighData
    ld hl, wHarnessBuffer
    ld a, 4
    di
    call YellowCopyFromBank9Locked
    ei
    ret

HarnessResolveSpecies2::
    ld bc, 2
    call YellowResolveSpeciesRecord16
    ret c
    ld hl, wHarnessBuffer
    ld a, 4
    di
    call YellowCopyFromBank9Locked
    ei
    ret

HarnessResolveMove1::
    ld bc, 1
    call YellowResolveMoveRecord16
    ret c
    ld hl, wHarnessBuffer
    ld a, 4
    di
    call YellowCopyFromBank9Locked
    ei
    ret

HarnessResolveItem0::
    ld bc, 0
    call YellowResolveItemRecord16
    ret c
    ld hl, wHarnessBuffer
    ld a, 4
    di
    call YellowCopyFromBank9Locked
    ei
    ret
