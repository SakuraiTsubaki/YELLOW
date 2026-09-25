; pret/pokeyellow integration bridge for YELLOW 16-bit runtime IDs.
;
; This file is copied only into the structural integration checkout. It may
; reference stock pokeyellow WRAM/constants directly.

DEF YELLOW_CANONICAL_DAYCARE_SLOT EQU 6
DEF YELLOW_CANONICAL_PC_BASE      EQU 7

YellowGetLoadedPersistentCanonicalSlot::
; Output: A = canonical slot 0..246, carry clear.
; Carry set for transient/invalid sources (enemy party, bad index).
    ld a, [wMonDataLocation]
    cp PLAYER_PARTY_DATA
    jr z, .party
    cp BOX_DATA
    jr z, .box
    cp DAYCARE_DATA
    jr z, .daycare
    jr .invalid

.party
    ld a, [wWhichPokemon]
    cp PARTY_LENGTH
    jr nc, .invalid
    and a
    ret

.daycare
    ld a, YELLOW_CANONICAL_DAYCARE_SLOT
    and a
    ret

.box
    ld a, [wCurrentBoxNum]
    and $7f
    cp NUM_BOXES
    jr nc, .invalid

    ; HL = box * MONS_PER_BOX; the loop works for either 8x30 JP or 12x20 intl.
    ld b, a
    ld hl, 0
    ld de, MONS_PER_BOX
.box_mul
    ld a, b
    and a
    jr z, .box_mul_done
    add hl, de
    dec b
    jr .box_mul
.box_mul_done
    ld a, [wWhichPokemon]
    cp MONS_PER_BOX
    jr nc, .invalid
    ld e, a
    ld d, 0
    add hl, de
    ld de, YELLOW_CANONICAL_PC_BASE
    add hl, de
    ld a, h
    and a
    jr nz, .invalid
    ld a, l
    cp 247
    jr nc, .invalid
    and a
    ret

.invalid
    scf
    ret

YellowSyncLoadedPersistentSpecies16::
; Mirror the species selected by LoadMonData_ into YELLOW's 16-bit runtime.
; Persistent sources use the sidecar; transient sources use high byte zero.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    call YellowGetLoadedPersistentCanonicalSlot
    jr c, .legacy_only
    ld d, a
    ld a, [wCurPartySpecies]
    call YellowComposePersistentSpecies16Locked
    jr nc, .store

.legacy_only
    ld a, [wCurPartySpecies]
    ld c, a
    ld b, 0

.store
    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_RUNTIME_SRAM_BANK
    ld [rRAMB], a

    ld a, c
    ld [wYellowCurPartySpecies], a
    ld [wYellowCurSpecies], a
    ld a, b
    ld [wYellowCurPartySpecies + 1], a
    ld [wYellowCurSpecies + 1], a

    ; The service is executable now because SRAM bank 15 is selected.
    ; Missing descriptors/records are allowed here; status remains 0.
    call YellowPrefetchCurrentSpeciesCore16Locked

    xor a
    ld [rRAMG], a

    pop af
    ldh [rIE], a
    ret

YellowSyncLoadedMoveIndex16Locked::
; Input: D = move index 0..3.
; Mirrors wLoadedMonMoves[D] + persistent sidecar high byte into
; wYellowLoadedMoves[D]. Transient sources get high byte zero.
; PRECONDITION: interrupts disabled.
    ld a, d
    cp 4
    ret nc
    push de
    call YellowGetLoadedPersistentCanonicalSlot
    jr c, .transient
    ld b, a
    jr .have_slot
.transient
    ld b, $ff
.have_slot
    pop de

    ; Load the legacy low byte.
    ld hl, wLoadedMonMoves
    ld a, l
    add d
    ld l, a
    jr nc, .low_ptr_ok
    inc h
.low_ptr_ok
    ld c, [hl]

    ; Compute destination before the sidecar reader clobbers HL/DE.
    ld a, d
    add a
    add LOW(wYellowLoadedMoves)
    ld l, a
    ld a, HIGH(wYellowLoadedMoves)
    adc 0
    ld h, a
    push hl
    push bc

    ld a, b
    cp $ff
    jr z, .zero_high
    ld a, d
    inc a ; sidecar fields 1..4 are move high bytes
    ld c, a
    ld a, b
    call YellowReadMonExtByteLocked
    jr .have_high
.zero_high
    xor a
.have_high
    pop bc
    pop hl
    ld b, a
    jp YellowStoreRuntimeWordLocked

YellowSyncLoadedPersistentMoves16::
; Called after LoadMonData_ has copied the legacy record to wLoadedMon.
; Preserves caller IME state by masking/restoring rIE around SRAM bank changes.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld d, 0
    call YellowSyncLoadedMoveIndex16Locked
    ld d, 1
    call YellowSyncLoadedMoveIndex16Locked
    ld d, 2
    call YellowSyncLoadedMoveIndex16Locked
    ld d, 3
    call YellowSyncLoadedMoveIndex16Locked

    pop af
    ldh [rIE], a
    ret
