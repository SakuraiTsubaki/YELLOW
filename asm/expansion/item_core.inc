; YELLOW item core v1.
;
; This record is independent from the Gen I bag entry format.

DEF YELLOW_ITEM_CORE_V1_SIZE EQU 24

DEF YIC_PRICE          EQU 0  ; dl
DEF YIC_POCKET         EQU 4
DEF YIC_CATEGORY       EQU 5
DEF YIC_BATTLE_USE     EQU 6
DEF YIC_FIELD_USE      EQU 7
DEF YIC_HELD_EFFECT    EQU 8  ; dw
DEF YIC_EFFECT         EQU 10 ; dw
DEF YIC_PARAMETER      EQU 12 ; dw
DEF YIC_FLING_POWER    EQU 14 ; dw
DEF YIC_FLAGS          EQU 16 ; dl
DEF YIC_EFFECT_SCRIPT  EQU 20 ; dw
DEF YIC_RESERVED       EQU 22 ; dw

MACRO yellow_item_core_v1
; price, pocket, category, battle_use, field_use,
; held_effect, effect, parameter, fling_power, flags, effect_script
    dl \1
    db \2, \3, \4, \5
    dw \6, \7, \8, \9
    dl \10
    dw \11, 0
ENDM
