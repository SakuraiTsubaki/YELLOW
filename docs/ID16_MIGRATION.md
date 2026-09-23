# YELLOW 16-bit ID migration

## Persistent Pokémon strategy

The original Yellow Pokémon record stores species and each of the four moves as one byte. YELLOW keeps those legacy low bytes in place and adds a per-slot extension record in SRAM bank 4.

For a persistent Pokémon:

`logical_species = legacy_species_low | (species_high << 8)`

`logical_move[i] = legacy_move_low[i] | (move_high[i] << 8)`

This makes all original values byte-identical while allowing logical IDs through `0xFFFE`.

The extension record also carries 16-bit held-item, ability and form IDs, because those concepts either do not exist in the Gen I record or cannot be represented safely by repurposing original bytes.

## Canonical persistent slots

Both Yellow save families store exactly 240 PC Pokémon despite different physical layouts.

- JP: 8 boxes × 30.
- International: 12 boxes × 20.

YELLOW maps both to linear PC slots 0..239. Combined with party 0..5 and daycare, the persistent extension table contains 247 records.

## What this does not solve yet

Battle and working-RAM structures still contain one-byte species/move fields. ROM trainer/wild/script tables and many selection variables are also one byte.

Therefore persistent sidecars are only one layer. Runtime migration still needs:

- 16-bit current species/move/item variables;
- widened or paired high-byte fields for battle structs;
- 16-bit table readers and comparisons;
- generated banked indexes for names/base stats/learnsets;
- widened trainer and wild encounter formats;
- explicit link/trade protocol versioning.

The project must not enable IDs above 255 until those runtime readers are migrated.
