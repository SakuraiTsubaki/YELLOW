; Compile-time harness for YELLOW's original-GB expansion ABI.
; Built with the same RGBDS line used by pret/pokeyellow.

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
HarnessFarPtrs::
    yellow_farptr9 HarnessLowTarget
    yellow_farptr9 HarnessHighTarget
    yellow_farptr9 HarnessTopTarget
HarnessFarPtrsEnd::

ASSERT HarnessFarPtrsEnd - HarnessFarPtrs == 9

SECTION "Harness Calls", ROM0
HarnessCallHigh::
    yellow_farcall9 HarnessHighTarget
    ret

HarnessCallTop::
    yellow_farcall9 HarnessTopTarget
    ret
