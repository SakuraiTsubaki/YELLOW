; pret/pokeyellow integration bridge for YELLOW 16-bit runtime IDs.
;
; This file is copied only into the structural integration checkout. It may
; reference stock pokeyellow WRAM/constants directly.

DEF YELLOW_CANONICAL_DAYCARE_SLOT EQU 6
DEF YELLOW_CANONICAL_PC_BASE      EQU 7

YellowSyncLoadedPersistentSpecies16::
; Mirror the species selected by LoadMonData_ into YELLOW's 16-bit runtime
; state. Stock behavior is untouched: wCurPartySpecies/wCurSpecies remain the
; original one-byte fields until each downstream consumer is migrated.
;
; Persistent sources use the sidecar high byte:
;   player party -> canonical slots 0..5
;   daycare      -> slot 6
;   current PC   -> canonical slots 7..246
; Enemy party is transient and currently mirrors high byte 0.
;
; Interrupt safety:
; We temporarily clear rIE rather than changing IME with DI/EI. This preserves
; the caller's IME state while preventing an interrupt from observing a
; temporary SRAM bank selection.
    ldh a, [rIE]
    push af
    xor a
    ldh [rIE], a

    ld a, [wMonDataLocation]
    cp PLAYER_PARTY_DATA
    jr z, .party
    cp BOX_DATA
    jr z, .box
    cp DAYCARE_DATA
    jr z, .daycare
    jr .legacy_only

.party
    ld a, [wWhichPokemon]
    cp PARTY_LENGTH
    jr nc, .legacy_only
    ld d, a
    jr .compose

.daycare
    ld d, YELLOW_CANONICAL_DAYCARE_SLOT
    jr .compose

.box
    ld a, [wCurrentBoxNum]
    and $7f
    cp NUM_BOXES
    jr nc, .legacy_only

    ; HL = box * 20 without relying on a multiply helper in another bank.
    ld l, a
    ld h, 0
    add hl, hl ; *2
    add hl, hl ; *4
    push hl
    add hl, hl ; *8
    add hl, hl ; *16
    pop de     ; DE = *4
    add hl, de ; *20

    ld a, [wWhichPokemon]
    cp MONS_PER_BOX
    jr nc, .legacy_only
    ld e, a
    ld d, 0
    add hl, de
    ld de, YELLOW_CANONICAL_PC_BASE
    add hl, de
    ld a, h
    and a
    jr nz, .legacy_only
    ld d, l

.compose
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
