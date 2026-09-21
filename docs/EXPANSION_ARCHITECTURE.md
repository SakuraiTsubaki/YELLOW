# YELLOW expansion architecture

## Goal

Build the expansion layer **before** remaking Yellow content.

YELLOW must be able to absorb verified data from later generations without repeating the historical pattern of widening IDs, rewriting save layouts, and coupling mechanics to a single generation ceiling.

## 1. Representation is not allocation

All expandable gameplay identifiers use a 16-bit representation contract.

That gives a valid encoded range of `0x0000..0xFFFE`, with `0xFFFF` reserved as invalid. It does **not** mean the GBA allocates 65,535-entry tables. Compiled table counts remain generated from the selected data set.

This distinction is mandatory for ROM/RAM efficiency.

## 2. Generation X is a boundary, not guessed content

Generation X is reserved as generation number 10. No species, form, move, item, ability, type, or mechanic count is invented for it.

When verified Gen X data exists, it is imported into manifests and generated tables. The engine contract should not need another ID-width migration.

## 3. Mechanics are capabilities

A generation number describes provenance. It must not be the sole switch for battle behavior.

Features such as abilities, the physical/special split, regional forms, Mega Evolution, Z-Moves, Dynamax, Terastallization, and future mechanics are represented as independent capabilities.

This lets YELLOW choose modern rules deliberately instead of accidentally inheriting every rule from a generation label.

## 4. Forms are first-class identities

Do not pack all form meaning into a single legacy species byte.

The target model separates at least:

- base species identity;
- persistent form identity;
- battle-only form state;
- cosmetic state;
- form arguments/parameters;
- regional provenance;
- evolution/form-change conditions.

This is compatible with the research already collected in EMERALD and avoids forcing later-generation form fields into the stock Gen III personal struct.

## 5. Save data is versioned from day one

Every YELLOW save layout must carry a schema version. Any layout change requires an explicit migration path.

Never make raw struct size the only format identifier.

Future fields should be introduced so older saves can be migrated and unrecognized extension data can be preserved whenever practical.

## 6. Upstream strategy

Bootstrap from the pinned `pokeemerald-expansion` stable base. Track its `upcoming` branch separately, but do not silently rebase YELLOW onto moving upstream code.

YELLOW-specific systems stay in an extension layer so upstream updates can be audited instead of mixed with project logic.

## 7. Import order

1. engine/toolchain bootstrap;
2. ID-width and table-count audit;
3. save-schema envelope;
4. species + forms + personal data;
5. types;
6. moves;
7. abilities;
8. items;
9. evolutions and form-change rules;
10. learnsets;
11. battle mechanics;
12. Yellow story/maps/events/assets.

The original Yellow remake content starts **after** the engine can safely represent the intended modern data model.
