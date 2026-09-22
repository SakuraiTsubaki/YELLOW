# YELLOW expansion architecture

## Goal

Expand **Pokémon Yellow's original Game Boy runtime**, not a GBA remake.

The source ROMs remain immutable evidence. Expanded builds are derived ROMs that keep Yellow's GB/SGB/GBC execution model while removing the 1 MiB / 8-bit-ID assumptions that prevent later-generation data from being represented.

## 1. Source profiles stay exact

The verified source family is split at the cartridge layer.

- Japanese Rev 0A/B/C/D: MBC3+RAM+BATTERY, 1 MiB ROM, 32 KiB SRAM.
- EN/FR/DE/IT/ES: MBC5+RAM+BATTERY, 1 MiB ROM, 32 KiB SRAM.

The expanded profile does not overwrite those identities.

## 2. Expanded mapper profile

The common expansion target is MBC5.

- ROM: 512 × 16 KiB banks = 8 MiB.
- SRAM: 16 × 8 KiB banks = 128 KiB.
- ROM bank selection therefore needs 9 bits.
- Any old u8 bank field is a hard blocker for banks 256..511.

Japanese MBC3 code must be migrated through an explicit mapper abstraction. A header edit alone is not considered an implementation.

## 3. 16-bit logical IDs

Species, forms, moves, items, abilities, types, locations and maps use a 16-bit logical representation contract. `0xFFFF` is invalid.

This is **representation**, not allocation. Tables use verified content counts and banked indexes rather than allocating 65,535 records.

## 4. Banked data model

Data that can exceed one 16 KiB bank uses generated indexes carrying at least:

- 9-bit ROM bank;
- 16-bit CPU-visible address or bank-relative offset.

Large tables are split by record boundaries so a single record does not silently straddle banks unless the reader explicitly supports it.

## 5. Save expansion

The original Japanese and international 32 KiB save layouts remain separate legacy formats.

The expanded profile may use 128 KiB SRAM, but it must have:

- a schema version;
- explicit migration from each legacy profile;
- enlarged species/move/item storage where needed;
- data-driven Pokédex bitsets;
- expanded box records;
- checksums covering the new layout.

ROM capacity and SRAM capacity are separate budgets.

## 6. Generation X rule

Generation 10 is a reserved provenance boundary only. No unreleased species/move/item counts are invented.

The purpose of the 16-bit ID and 9-bit bank contracts is to avoid another representation migration when verified data arrives.

## 7. Implementation order

1. keep the nine verified ROM identities and two save families fixed;
2. add a reproducible ROM expander for the MBC5 derived profile;
3. add mapper abstraction and 9-bit ROM-bank switching;
4. audit all ROM-bank values and banked pointers;
5. add 16-bit logical species/move/item/form IDs;
6. convert table readers to generated banked indexes;
7. define the 128 KiB expanded save schema and migrators;
8. widen party/box/trainer/wild/script formats one subsystem at a time;
9. import verified later-generation data only after the corresponding reader is widened;
10. preserve source-version reproduction modes separately from the expanded mode.

## 8. GBA boundary

GBA/Generation III remake work is intentionally outside this repository's runtime architecture.
