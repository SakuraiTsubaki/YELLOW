; Compile-time harness for YELLOW's original-GB expansion ABI.

DEF rROMB0 EQU $2000
DEF rROMB1 EQU $3000

SECTION "Harness HRAM", HRAM
hLoadedROMBank:: db
hLoadedROMBankHigh:: db

SECTION "Harness Home", ROM0
JumpToAddress::
    jp hl

INCLUDE "asm/expansion/id16.inc"
INCLUDE "asm/expansion/farptr9.inc"
INCLUDE "asm/expansion/mbc5_bank9.asm"
INCLUDE "asm/expansion/index16.asm"
INCLUDE "asm/expansion/species16.asm"
INCLUDE "asm/expansion/move16.asm"
INCLUDE "asm/expansion/item16.asm"
INCLUDE "asm/expansion/wram_id16.asm"

SECTION "Harness Low Target", ROMX[$4000], BANK[$01]
HarnessLowTarget::
    ret

SECTION "Harness High Target", ROMX[$4000], BANK[$100]
HarnessHighTarget::
    ret

SECTION "Harness Top Target", ROMX[$7fff], BANK[$1ff]
HarnessTopTarget::
    db 0

SECTION "Harness Species Index", ROMX[$5000], BANK[$02]
YellowSpeciesIndex16::
    yellow_farptr9 HarnessLowTarget
    yellow_farptr9 HarnessHighTarget
    yellow_farptr9 HarnessTopTarget
YellowSpeciesIndex16End::

SECTION "Harness Move Index", ROMX[$5100], BANK[$02]
YellowMoveIndex16::
    yellow_farptr9 HarnessHighTarget
    yellow_farptr9 HarnessLowTarget
YellowMoveIndex16End::

SECTION "Harness Item Index", ROMX[$5200], BANK[$02]
YellowItemIndex16::
    yellow_farptr9 HarnessTopTarget
    yellow_farptr9 HarnessLowTarget
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
HarnessCallHigh::
    yellow_farcall9 HarnessHighTarget
    ret

HarnessResolveSpecies2::
    call YellowGetLoadedROMBank9
    push bc
    ld bc, 2
    call YellowResolveSpeciesRecord16
    jr c, .restore
    call YellowSetROMBank9
.restore
    pop bc
    jp YellowSetROMBank9

HarnessResolveMove1::
    call YellowGetLoadedROMBank9
    push bc
    ld bc, 1
    call YellowResolveMoveRecord16
    jr c, .restore
    call YellowSetROMBank9
.restore
    pop bc
    jp YellowSetROMBank9

HarnessResolveItem0::
    call YellowGetLoadedROMBank9
    push bc
    ld bc, 0
    call YellowResolveItemRecord16
    jr c, .restore
    call YellowSetROMBank9
.restore
    pop bc
    jp YellowSetROMBank9
