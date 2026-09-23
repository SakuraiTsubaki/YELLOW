; YELLOW move core v1.
DEF YELLOW_MOVE_CORE_V1_SIZE EQU 16

DEF YMC_TYPE          EQU 0  ; dw
DEF YMC_EFFECT        EQU 2  ; dw
DEF YMC_POWER         EQU 4
DEF YMC_ACCURACY      EQU 5
DEF YMC_PP            EQU 6
DEF YMC_PRIORITY      EQU 7
DEF YMC_CATEGORY      EQU 8
DEF YMC_TARGET        EQU 9
DEF YMC_EFFECT_CHANCE EQU 10
DEF YMC_FLAGS         EQU 12 ; dd

MACRO yellow_move_core_v1
; type, effect, power, accuracy, pp, priority, category, target,
; effect_chance, flags32
    dw \1, \2
    db \3, \4, \5, \6, \7, \8, \9, 0
    dd \10
ENDM
