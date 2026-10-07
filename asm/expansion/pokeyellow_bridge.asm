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

YellowSyncBattleMonMoveIndex16Locked::
; Input: D = move index 0..3.
; Player party battle source only: wWhichPokemon maps directly to canonical
; party slots 0..5. Mirrors wBattleMonMoves[D] + sidecar high byte.
; PRECONDITION: interrupts disabled.
    ld a, d
    cp 4
    ret nc

    ld a, [wWhichPokemon]
    cp PARTY_LENGTH
    jr nc, .transient
    ld b, a
    jr .have_slot
.transient
    ld b, $ff
.have_slot

    ld hl, wBattleMonMoves
    ld a, l
    add d
    ld l, a
    jr nc, .low_ptr_ok
    inc h
.low_ptr_ok
    ld c, [hl]

    ld a, d
    add a
    add LOW(wYellowBattleMonMoves)
    ld l, a
    ld a, HIGH(wYellowBattleMonMoves)
    adc 0
    ld h, a
    push hl
    push bc

    ld a, b
    cp $ff
    jr z, .zero_high
    ld a, d
    inc a
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

YellowSyncBattleMonMoves16::
; Called immediately after stock LoadBattleMonFromParty has populated
; wBattleMonMoves.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld d, 0
    call YellowSyncBattleMonMoveIndex16Locked
    ld d, 1
    call YellowSyncBattleMonMoveIndex16Locked
    ld d, 2
    call YellowSyncBattleMonMoveIndex16Locked
    ld d, 3
    call YellowSyncBattleMonMoveIndex16Locked

    pop af
    ldh [rIE], a
    ret

YellowSyncPlayerSelectedMove16::
; Mirror the current regular player move selection from the 16-bit battle-move
; array. Stock wPlayerSelectedMove remains the low byte for legacy consumers.
    ld a, [wPlayerMoveListIndex]
    cp 4
    ret nc
    add a
    ld e, a
    ld d, 0

    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_RUNTIME_SRAM_BANK
    ld [rRAMB], a

    ld hl, wYellowBattleMonMoves
    add hl, de
    ld a, [hli]
    ld [wYellowPlayerSelectedMove], a
    ld a, [hl]
    ld [wYellowPlayerSelectedMove + 1], a

    xor a
    ld [rRAMG], a

    pop af
    ldh [rIE], a
    ret

YellowPrepareCurrentMove16::
; First 16-bit consumer bridge for stock GetCurrentMove.
;
; Player path:
;   If the stock selected low byte still matches the selected battle slot,
;   consume the full 16-bit wYellowBattleMonMoves entry. Dynamic legacy moves
;   (Struggle/Metronome/Mirror Move/debug paths) fall back to high byte zero.
;
; Enemy path:
;   Enemy move generation is still legacy-width at this stage, so mirror the
;   selected low byte with high byte zero.
;
; The resolved logical ID is written to wYellowMoveNum and its move-core record
; is prefetched. Stock GetCurrentMove continues afterward, so IDs >255 remain
; gated until the legacy battle-view projection is integrated.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_RUNTIME_SRAM_BANK
    ld [rRAMB], a

    ldh a, [hWhoseTurn]
    and a
    jr nz, .enemy

    ; Fight debug bypasses the normal selected battle-slot source.
    ld a, [wStatusFlags7]
    bit BIT_TEST_BATTLE, a
    jr nz, .player_test

    ld a, [wPlayerMoveListIndex]
    cp NUM_MOVES
    jr nc, .player_legacy
    add a
    ld e, a
    ld d, 0
    ld hl, wYellowBattleMonMoves
    add hl, de

    ; Only trust the high byte when the stock low byte still names this slot.
    ld a, [wPlayerSelectedMove]
    cp [hl]
    jr nz, .player_legacy
    ld c, [hl]
    inc hl
    ld b, [hl]
    jr .store

.player_test
    ld a, [wTestBattlePlayerSelectedMove]
    jr .legacy_a

.player_legacy
    ld a, [wPlayerSelectedMove]
.legacy_a
    ld c, a
    ld b, 0
    jr .store

.enemy
    ld a, [wEnemySelectedMove]
    ld c, a
    ld b, 0

.store
    ld a, c
    ld [wYellowMoveNum], a
    ld a, b
    ld [wYellowMoveNum + 1], a

    call YellowPrefetchCurrentMoveCore16Locked
    call YellowPrefetchCurrentMoveName16Locked

    xor a
    ld [rRAMG], a

    pop af
    ldh [rIE], a
    ret


YellowLegacyMoveCoreSupportedLocked::
; Carry clear = the prefetched core/name can be represented safely by the
; stock six-byte Yellow battle move view. Carry set = keep legacy path.
; PRECONDITION: interrupts disabled, SRAM bank 15 selected.
    ld a, [wYellowMoveCoreStatus]
    cp 1
    jr nz, .fail
    ld a, [wYellowMoveNameStatus]
    cp 1
    jr nz, .fail

    ld a, [wYellowMoveCoreScratch + YMC_FLAGS]
    bit YMC_FLAG_LEGACY_VIEW_SAFE, a
    jr z, .fail

    ld a, [wYellowMoveCoreScratch + YMC_ANIMATION + 1]
    and a
    jr nz, .fail
    ld a, [wYellowMoveCoreScratch + YMC_ANIMATION]
    and a
    jr z, .fail
    cp NUM_ATTACK_ANIMS + 1
    jr nc, .fail

    ld a, [wYellowMoveCoreScratch + YMC_EFFECT + 1]
    and a
    jr nz, .fail
    ld a, [wYellowMoveCoreScratch + YMC_EFFECT]
    cp NUM_MOVE_EFFECTS + 1
    jr nc, .fail

    ld a, [wYellowMoveCoreScratch + YMC_POWER + 1]
    and a
    jr nz, .fail
    ld a, [wYellowMoveCoreScratch + YMC_ACCURACY + 1]
    and a
    jr nz, .fail

    ld a, [wYellowMoveCoreScratch + YMC_TYPE + 1]
    and a
    jr nz, .fail
    ld a, [wYellowMoveCoreScratch + YMC_TYPE]
    cp GHOST + 1
    jr c, .type_ok
    cp FIRE
    jr c, .fail
    cp DRAGON + 1
    jr nc, .fail
.type_ok

    ld a, [wYellowMoveCoreScratch + YMC_PP]
    cp 41
    jr nc, .fail

    ld a, [wYellowMoveNameScratch + YMN_LENGTH]
    and a
    jr z, .fail
    cp YMN_MAX_CHARS + 1
    jr nc, .fail

    and a
    ret
.fail
    scf
    ret

YellowTryProjectCurrentMoveLegacyView16::
; Project one explicitly compatible >255 move into stock Yellow's six-byte
; battle view and wNameBuffer.
;
; Low-ID moves always return carry set so the original Moves/MoveNames path
; stays byte-exact.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld a, $0a
    ld [rRAMG], a
    ld a, YELLOW_RUNTIME_SRAM_BANK
    ld [rRAMB], a

    ld a, [wYellowMoveNum + 1]
    and a
    jr z, .fail

    call YellowLegacyMoveCoreSupportedLocked
    jr c, .fail

    ldh a, [hWhoseTurn]
    and a
    jr z, .player
    ld de, wEnemyMoveNum
    jr .copy_view
.player
    ld de, wPlayerMoveNum

.copy_view
    ld a, [wYellowMoveCoreScratch + YMC_ANIMATION]
    ld [de], a
    inc de
    ld a, [wYellowMoveCoreScratch + YMC_EFFECT]
    ld [de], a
    inc de
    ld a, [wYellowMoveCoreScratch + YMC_POWER]
    ld [de], a
    inc de
    ld a, [wYellowMoveCoreScratch + YMC_TYPE]
    ld [de], a
    inc de
    ld a, [wYellowMoveCoreScratch + YMC_ACCURACY]
    ld [de], a
    inc de
    ld a, [wYellowMoveCoreScratch + YMC_PP]
    ld [de], a

    ld a, [wYellowMoveNameScratch + YMN_LENGTH]
    ld b, a
    ld hl, wYellowMoveNameScratch + YMN_TEXT
    ld de, wNameBuffer
.copy_name
    ld a, [hli]
    ld [de], a
    inc de
    dec b
    jr nz, .copy_name
    ld a, "@"
    ld [de], a

    xor a
    ld [rRAMG], a
    pop af
    ldh [rIE], a
    and a
    ret

.fail
    xor a
    ld [rRAMG], a
    pop af
    ldh [rIE], a
    scf
    ret
