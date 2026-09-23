; YELLOW move core v1.
;
; Modern move metadata stored independently from Gen I's one-byte move tables.

DEF YELLOW_MOVE_CORE_V1_SIZE EQU 24

DEF YMC_TYPE             EQU 0  ; dw
DEF YMC_POWER            EQU 2  ; dw
DEF YMC_ACCURACY         EQU 4  ; dw
DEF YMC_PP               EQU 6
DEF YMC_PRIORITY         EQU 7
DEF YMC_CATEGORY         EQU 8
DEF YMC_TARGET           EQU 9
DEF YMC_EFFECT           EQU 10 ; dw
DEF YMC_EFFECT_CHANCE    EQU 12
DEF YMC_GENERATION       EQU 13
DEF YMC_FLAGS            EQU 14 ; dl
DEF YMC_ANIMATION        EQU 18 ; dw
DEF YMC_EFFECT_SCRIPT    EQU 20 ; dw
DEF YMC_RESERVED         EQU 22 ; dw

MACRO yellow_move_core_v1
; type, power, accuracy, pp, priority, category, target,
; effect, effect_chance, generation, flags, animation, effect_script
    dw \1, \2, \3
    db \4, \5, \6, \7
    dw \8
    db \9, \10
    dl \11
    dw \12, \13, 0
ENDM
