; YELLOW species core v1.
;
; This is a ROM data record, not the legacy Gen I BaseStats struct.
; It carries enough width for later-generation core stats while keeping
; sprites, learnsets, abilities and forms in separate indexed tables.

DEF YELLOW_SPECIES_CORE_V1_SIZE EQU 20

DEF YSC_HP              EQU 0
DEF YSC_ATTACK          EQU 1
DEF YSC_DEFENSE         EQU 2
DEF YSC_SPEED           EQU 3
DEF YSC_SP_ATTACK       EQU 4
DEF YSC_SP_DEFENSE      EQU 5
DEF YSC_LEGACY_SPECIAL  EQU 6
DEF YSC_CATCH_RATE      EQU 7
DEF YSC_TYPE1           EQU 8  ; dw
DEF YSC_TYPE2           EQU 10 ; dw
DEF YSC_BASE_EXP        EQU 12 ; dw
DEF YSC_GROWTH_RATE     EQU 14
DEF YSC_GENDER_RATIO    EQU 15
DEF YSC_BASE_FRIENDSHIP EQU 16
DEF YSC_EGG_CYCLES      EQU 17
DEF YSC_FLAGS           EQU 18
DEF YSC_RESERVED        EQU 19

MACRO yellow_species_core_v1
; hp, atk, def, speed, spa, spd, legacy_special, catch,
; type1, type2, base_exp, growth, gender, friendship, egg_cycles, flags
    db \1, \2, \3, \4, \5, \6, \7, \8
    dw \9, \10, \11
    db \12, \13, \14, \15, \16, 0
ENDM
