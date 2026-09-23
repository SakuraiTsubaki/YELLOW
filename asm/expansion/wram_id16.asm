; YELLOW expansion WRAM overlay requirements.
;
; These variables are new expansion state; do not insert them into the middle
; of the stock WRAM layout. Place them in a dedicated free/relocated expansion
; WRAM section after the linker/layout audit.

SECTION "YELLOW ID16 Runtime State", WRAM0

yellow_id16_var wYellowCurSpecies
yellow_id16_var wYellowCurPartySpecies
yellow_id16_var wYellowCurItem
yellow_id16_var wYellowMoveNum
yellow_id16_var wYellowPlayerSelectedMove
yellow_id16_var wYellowEnemySelectedMove
yellow_id16_var wYellowCapturedMonSpecies
yellow_id16_var wYellowPlayerStarter
yellow_id16_var wYellowRivalStarter
yellow_id16_var wYellowFossilMon

; wEnemyMonOrTrainerClass mixes two namespaces in stock Yellow. The expanded
; runtime must split them instead of merely widening that ambiguous byte.
yellow_id16_var wYellowEnemySpecies
yellow_id16_var wYellowTrainerClass
