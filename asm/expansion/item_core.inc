; YELLOW item core v1.
DEF YELLOW_ITEM_CORE_V1_SIZE EQU 16

DEF YIC_PRICE        EQU 0  ; dd
DEF YIC_POCKET       EQU 4
DEF YIC_IMPORTANCE   EQU 5
DEF YIC_HOLD_EFFECT  EQU 6  ; dw
DEF YIC_PARAMETER    EQU 8  ; dw
DEF YIC_FLING_POWER  EQU 10
DEF YIC_BATTLE_USAGE EQU 11
DEF YIC_FIELD_USE    EQU 12 ; dw
DEF YIC_FLAGS        EQU 14 ; dw

MACRO yellow_item_core_v1
; price32, pocket, importance, hold_effect, parameter,
; fling_power, battle_usage, field_use, flags
    dd \1
    db \2, \3
    dw \4, \5
    db \6, \7
    dw \8, \9
ENDM
