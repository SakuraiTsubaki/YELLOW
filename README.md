# YELLOW

Generation I **Pokémon Yellow / Pocket Monsters Pikachu** remake project on a Generation III engine foundation.

## First principle: expand before content

YELLOW does not begin by hard-coding the original 151-species-era limits. The engine contract is prepared first so later-generation data can be added without renumbering the project or redesigning save data.

The current foundation targets:

- a Generation III / pokeemerald-expansion engine base;
- Japanese as the primary source/reference language, then Korean, then English;
- 16-bit runtime IDs for species, forms, moves, items, abilities, types, and other expandable domains;
- table-driven counts instead of fixed Generation IX ceilings;
- explicit save-schema versioning and migration hooks;
- capability flags for mechanics that can be enabled independently;
- a reserved future-generation boundary beginning at Generation X without guessing unreleased content counts.

## Engine baseline

Pinned stable upstream at initialization:

- `rh-hideout/pokeemerald-expansion@75b806a3ab57a81ff1eb6179288981f0b3cc3050` (`master`)
- observed future/upcoming line: `7d8165f68f68052c80230f379a17cefc0573bdbd` (`upcoming`), checked 2026-09-21

The upstream tree is a reference/base dependency. YELLOW-specific data, compatibility rules, manifests, and migrations belong here.

## Foundation files

- `include/yellow/expansion.h` — ID widths, sentinels, generation boundary, save schema contract.
- `config/expansion.json` — machine-readable expansion policy.
- `manifests/engine-base.yml` — pinned engine provenance.
- `manifests/generation-capacity.csv` — known content ceilings vs future reserved generations.
- `docs/EXPANSION_ARCHITECTURE.md` — design rules for Gen I through Gen X+.
- `tests/test_expansion_contract.py` — guards against accidentally shrinking the future-ready contract.

ROM binaries are not stored in this repository.
