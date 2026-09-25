; YELLOW runtime extension state.
;
; Stock Yellow has 0 free WRAM0 and 0 free HRAM in the structural reference,
; so expanded ID state is not allocated there. It lives in volatile SRAM bank
; 15 while the expanded MBC5 runtime is active.

DEF YELLOW_RUNTIME_SRAM_BANK EQU 15
DEF YELLOW_RUNTIME_BASE      EQU $A000
DEF YELLOW_RUNTIME_MAGIC     EQU $A000
DEF YELLOW_RUNTIME_VERSION   EQU $A004
DEF YELLOW_RUNTIME_VERSION_VALUE EQU 1

DEF wYellowCurSpecies         EQU $A006 ; 2 bytes
DEF wYellowCurPartySpecies    EQU $A008 ; 2 bytes
DEF wYellowCurItem            EQU $A00A ; 2 bytes
DEF wYellowMoveNum            EQU $A00C ; 2 bytes
DEF wYellowPlayerSelectedMove EQU $A00E ; 2 bytes
DEF wYellowEnemySelectedMove  EQU $A010 ; 2 bytes
DEF wYellowCapturedMonSpecies EQU $A012 ; 2 bytes
DEF wYellowPlayerStarter      EQU $A014 ; 2 bytes
DEF wYellowRivalStarter       EQU $A016 ; 2 bytes
DEF wYellowFossilMon          EQU $A018 ; 2 bytes
DEF wYellowEnemySpecies       EQU $A01A ; 2 bytes
DEF wYellowTrainerClass       EQU $A01C ; 2 bytes

DEF YELLOW_RUNTIME_STATE_END  EQU $A01E
DEF YELLOW_RUNTIME_STATE_SIZE EQU YELLOW_RUNTIME_STATE_END - YELLOW_RUNTIME_BASE
