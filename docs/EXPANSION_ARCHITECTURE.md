# YELLOW expansion architecture

## Goal

Build the expansion layer from the **actual Yellow ROM and save formats**, then remake Yellow on top of it.

The project preserves original-format import compatibility while being able to absorb later-generation data without repeatedly widening IDs or replacing the save schema.

## 1. Source evidence comes first

`manifests/rom-baselines.csv` records the nine unique Yellow/Pikachu ROM binaries currently verified by SHA-1/SHA-256. `manifests/legacy-save-profiles.json` records the two legacy save families extracted from their save code.

A release name is not enough. ROM revision, ROM hash, legacy save profile and save-file hash are separate identities and must not be conflated.

## 2. Yellow has two legacy save families

The original 32 KiB SRAM layout is not universal.

- Japanese Rev 0A/B/C/D: MBC3, 8 boxes × 30 Pokémon, 6-byte player-name storage, larger Japanese box records, main checksum at `B594`.
- International EN/FR/DE/IT/ES: MBC5, 12 boxes × 20 Pokémon, 11-byte player-name storage, main checksum at `B523`, aggregate plus individual box checksums.

Both retain 240-PC-Pokémon capacity, but the byte layouts are incompatible.

Therefore the modern YELLOW save **does not expand either 32 KiB format in place**. Both are read-only import/migration profiles. The target GBA engine gets a separate versioned save schema.

## 3. Representation is not allocation

Expandable gameplay identifiers use a 16-bit representation contract. `0xFFFF` is reserved as invalid.

This does not allocate 65,535-entry GBA arrays. Runtime tables remain generated from selected data, so ROM/RAM cost follows actual content rather than the numeric ID ceiling.

## 4. Generation X is a boundary, not guessed content

Generation X is reserved as generation number 10. No species, form, move, item, ability, type or mechanic counts are invented for it.

Verified future data can be appended without another ID-width migration.

## 5. Mechanics are capabilities

Generation describes provenance. Battle behavior is enabled through independent capability flags: abilities, physical/special split, regional forms, Mega Evolution, Z-Moves, Dynamax, Terastallization and future mechanics.

## 6. Forms are first-class identities

The target model separates base species, persistent form, battle-only form, cosmetic state, form arguments, regional provenance and form/evolution conditions. Later-generation form metadata is not packed into the original one-byte Gen I species representation.

## 7. Save migration contract

Every expanded save carries a schema version. A legacy import retains at least:

- legacy profile (`yellow-jp-legacy` or `yellow-intl-legacy`);
- source save SHA-256;
- source ROM/release identity when known;
- migration schema version.

A layout change requires an explicit migration path. Raw struct size is never the sole format identifier.

The Japanese aggregate box-checksum instruction sequence has a ROM-literal `0x1599` span whose exact save-byte semantics still require validation against a real Japanese `.sav`. That uncertainty is preserved rather than guessed away.

## 8. Implementation order

1. ROM/save evidence and validators;
2. real user `.sav` validation for JP and international profiles;
3. engine/toolchain bootstrap;
4. ID-width/table-count audit across the imported engine;
5. versioned expanded-save envelope and legacy migrators;
6. species/forms/personal data;
7. types, moves, abilities, items;
8. evolution/form-change/learnset systems;
9. modern battle mechanics;
10. Yellow maps/story/events/assets.

The engine grows from Yellow's real data model outward; it is not a generic expansion pasted on before the source formats are understood.
