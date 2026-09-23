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

SECTION "Harness Index", ROMX[$5000], BANK[$02]
YellowSpeciesIndex16::
    yellow_farptr9 HarnessLowTarget
    yellow_farptr9 HarnessHighTarget
    yellow_farptr9 HarnessTopTarget
YellowSpeciesIndex16End::

SECTION "Harness Descriptor", ROM0
YellowSpeciesTableDescriptor::
    yellow_table16_descriptor YellowSpeciesIndex16, 3

ASSERT YellowSpeciesIndex16End - YellowSpeciesIndex16 == 9
ASSERT YellowSpeciesTableDescriptor + YELLOW_TABLE16_DESCRIPTOR_SIZE == @

SECTION "Harness Calls", ROM0
HarnessCallHigh::
    yellow_farcall9 HarnessHighTarget
    ret

HarnessResolveSpecies2::
    ld bc, 2
    call YellowGetLoadedROMBank9
    push bc
    ld bc, 2
    call YellowResolveSpeciesRecord16
    jr c, .restore
    call YellowSetROMBank9
.restore
    pop bc
    jp YellowSetROMBank9
