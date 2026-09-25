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
DEF wYellowSpeciesCoreStatus   EQU $A01E ; 0 missing/not loaded, 1 ready
DEF wYellowRuntimeFlags        EQU $A01F

DEF YELLOW_RUNTIME_STATE_END  EQU $A020
DEF YELLOW_RUNTIME_STATE_SIZE EQU YELLOW_RUNTIME_STATE_END - YELLOW_RUNTIME_BASE

; Core-record scratch buffers. These live below the $BC00 service image and
; never overlap the persistent extension, which is in SRAM banks 4..14.
DEF wYellowSpeciesCoreScratch EQU $A020
DEF wYellowMoveCoreScratch    EQU $A040
DEF wYellowItemCoreScratch    EQU $A060

DEF YELLOW_SPECIES_SCRATCH_SIZE EQU $20
DEF YELLOW_MOVE_SCRATCH_SIZE    EQU $20
DEF YELLOW_ITEM_SCRATCH_SIZE    EQU $20

ASSERT wYellowSpeciesCoreScratch + YELLOW_SPECIES_SCRATCH_SIZE <= wYellowMoveCoreScratch
ASSERT wYellowMoveCoreScratch + YELLOW_MOVE_SCRATCH_SIZE <= wYellowItemCoreScratch
ASSERT wYellowItemCoreScratch + YELLOW_ITEM_SCRATCH_SIZE <= $BC00

; Four 16-bit logical moves corresponding to stock wLoadedMonMoves[0..3].
DEF wYellowLoadedMoves EQU $A080 ; 8 bytes
DEF YELLOW_LOADED_MOVES_SIZE EQU 8
ASSERT wYellowLoadedMoves + YELLOW_LOADED_MOVES_SIZE <= $BC00

; Player battle-mon logical moves, mirrored from wBattleMonMoves plus sidecar.
DEF wYellowBattleMonMoves EQU $A088 ; 8 bytes
DEF YELLOW_BATTLE_MOVES_SIZE EQU 8
ASSERT wYellowBattleMonMoves + YELLOW_BATTLE_MOVES_SIZE <= $BC00
