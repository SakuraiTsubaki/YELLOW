; YELLOW move-name v1.
;
; Fixed 13-byte record:
;   byte 0      = encoded character length (1..12)
;   bytes 1..12 = Game Boy text-encoded characters; bytes after length ignored.
;
; The runtime appends the stock '@' terminator in wNameBuffer.

DEF YELLOW_MOVE_NAME_V1_SIZE EQU 13
DEF YMN_LENGTH               EQU 0
DEF YMN_TEXT                 EQU 1
DEF YMN_MAX_CHARS            EQU 12
