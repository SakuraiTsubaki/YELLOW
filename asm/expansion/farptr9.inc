; YELLOW 9-bit MBC5 far-pointer format
;
; 3 bytes encode:
;   byte 0      : ROM bank low 8 bits
;   bytes 1..2  : bit14 = ROM bank bit 8
;                 bits0..13 = offset inside the 16 KiB ROMX bank
;                 bit15 = reserved
;
; This packs a 9-bit bank plus a 14-bit ROMX offset into 23 bits.

DEF YELLOW_ROMX_BASE      EQU $4000
DEF YELLOW_ROMX_SIZE      EQU $4000
DEF YELLOW_MBC5_MAX_BANK  EQU $1ff

MACRO yellow_farptr9
    ASSERT BANK(\1) <= YELLOW_MBC5_MAX_BANK
    ASSERT \1 >= $4000 && \1 < $8000
    db LOW(BANK(\1))
    dw (((BANK(\1) >> 8) & 1) << 14) | ((\1) - YELLOW_ROMX_BASE)
ENDM
