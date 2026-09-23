; Compile-time harness for YELLOW's original-GB expansion ABI.

DEF rROMB0 EQU $2000
DEF rROMB1 EQU $3000

SECTION "Harness HRAM", HRAM
hLoadedROMBank:: db

SECTION "Harness Expansion Code", ROM0
INCLUDE "asm/expansion/id16.inc"
INCLUDE "asm/expansion/farptr9.inc"
INCLUDE "asm/expansion/mbc5_bank9.asm"
INCLUDE "asm/expansion/index16.asm"
INCLUDE "asm/expansion/species16.asm"
INCLUDE "asm/expansion/move16.asm"
INCLUDE "asm/expansion/item16.asm"
INCLUDE "asm/expansion/wram_id16.asm"

SECTION "Harness WRAM", WRAM0
wHarnessBuffer:: ds YELLOW_SPECIES_CORE_V1_SIZE

SECTION "Harness Low Species", ROMX[$4000], BANK[$01]
HarnessLowSpecies::
    yellow_species_core_v1 35, 55, 30, 90, 50, 40, 50, 190, 1, 1, 64, 0, 127, 70, 20, 0
HarnessLowSpeciesEnd::

SECTION "Harness High Species", ROMX[$4000], BANK[$100]
HarnessHighSpecies::
    yellow_species_core_v1 100, 120, 90, 110, 130, 95, 110, 45, $0102, $0103, 320, 4, 127, 50, 40, 1
HarnessHighSpeciesEnd::

SECTION "Harness High Move", ROMX[$4100], BANK[$100]
HarnessHighMove::
    yellow_move_core_v1 $0102, $0201, 95, 100, 10, 0, 1, 0, 20, $00000001
HarnessHighMoveEnd::

SECTION "Harness Top Item", ROMX[$7ff0], BANK[$1ff]
HarnessTopItem::
    yellow_item_core_v1 120000, 1, 0, $0123, $0456, 80, 1, $0200, $0001
HarnessTopItemEnd::

SECTION "Harness Species Index", ROMX[$5000], BANK[$02]
YellowSpeciesIndex16::
    yellow_farptr9 HarnessLowSpecies
    yellow_farptr9 HarnessHighSpecies
YellowSpeciesIndex16End::

SECTION "Harness Move Index", ROMX[$5100], BANK[$02]
YellowMoveIndex16::
    yellow_farptr9 HarnessHighMove
    yellow_farptr9 HarnessLowSpecies
YellowMoveIndex16End::

SECTION "Harness Item Index", ROMX[$5200], BANK[$02]
YellowItemIndex16::
    yellow_farptr9 HarnessTopItem
    yellow_farptr9 HarnessLowSpecies
YellowItemIndex16End::

SECTION "Harness Descriptors", ROM0
YellowSpeciesTableDescriptor::
    yellow_table16_descriptor YellowSpeciesIndex16, 2
YellowMoveTableDescriptor::
    yellow_table16_descriptor YellowMoveIndex16, 2
YellowItemTableDescriptor::
    yellow_table16_descriptor YellowItemIndex16, 2
HarnessDescriptorsEnd::

ASSERT HarnessLowSpeciesEnd - HarnessLowSpecies == YELLOW_SPECIES_CORE_V1_SIZE
ASSERT HarnessHighSpeciesEnd - HarnessHighSpecies == YELLOW_SPECIES_CORE_V1_SIZE
ASSERT HarnessHighMoveEnd - HarnessHighMove == YELLOW_MOVE_CORE_V1_SIZE
ASSERT HarnessTopItemEnd - HarnessTopItem == YELLOW_ITEM_CORE_V1_SIZE
ASSERT YellowSpeciesIndex16End - YellowSpeciesIndex16 == 6
ASSERT YellowMoveIndex16End - YellowMoveIndex16 == 6
ASSERT YellowItemIndex16End - YellowItemIndex16 == 6
ASSERT HarnessDescriptorsEnd - YellowSpeciesTableDescriptor == 18

SECTION "Harness Calls", ROM0
HarnessLoadHighSpeciesCore::
    ld bc, 1
    ld hl, wHarnessBuffer
    di
    call YellowCopySpeciesCore16Locked
    ei
    ret

HarnessLoadHighMoveCore::
    ld bc, 0
    ld hl, wHarnessBuffer
    di
    call YellowCopyMoveCore16Locked
    ei
    ret

HarnessLoadTopItemCore::
    ld bc, 0
    ld hl, wHarnessBuffer
    di
    call YellowCopyItemCore16Locked
    ei
    ret
