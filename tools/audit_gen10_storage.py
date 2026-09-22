#!/usr/bin/env python3
"""Audit the pinned expansion's persistent-ID headroom and YELLOW Stage 1 patch."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED_PIN = "75b806a3ab57a81ff1eb6179288981f0b3cc3050"

BASELINE = {
    "species_count": 1573,
    "species_storage_bits": 11,
    "item_count": 874,
    "item_storage_bits": 10,
    "regular_move_count": 848,
    "move_storage_bits": 11,
    "ability_count": 320,
    "tera_type_storage_bits": 5,
    "pokeball_storage_bits": 6,
    "met_location_storage_bits": 8,
    "boxpokemon_bytes": 80,
    "pc_boxes": 14,
    "mons_per_box": 30,
    "pc_capacity": 420,
    "saveblock3_max_bytes": 1624,
}


def read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def require(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text, re.MULTILINE) is None:
        raise RuntimeError(f"missing invariant: {label}")


def report_baseline(root: Path) -> dict:
    pokemon_h = read(root, "include/pokemon.h")
    storage_h = read(root, "include/pokemon_storage_system.h")
    save_h = read(root, "include/save.h")
    global_h = read(root, "include/global.h")

    require(pokemon_h, r"enum Species species:11;", "11-bit baseline species")
    require(pokemon_h, r"enum Item heldItem:10;", "10-bit baseline item")
    require(pokemon_h, r"enum Move move1:11;", "11-bit baseline move")
    require(storage_h, r"#define TOTAL_BOXES_COUNT\s+14", "14 PC boxes")
    require(storage_h, r"#define IN_BOX_ROWS\s+5", "5 PC rows")
    require(storage_h, r"#define IN_BOX_COLUMNS\s+6", "6 PC columns")
    require(save_h, r"#define SAVE_BLOCK_3_CHUNK_SIZE 116", "116-byte SaveBlock3 sector chunk")
    require(save_h, r"#define NUM_SECTORS_PER_SLOT\s+14", "14 sectors per save slot")
    require(global_h, r"struct SaveBlock3", "SaveBlock3")
    require(global_h, r"/\* max size 1624 bytes \*/", "SaveBlock3 1624-byte ceiling")

    out = dict(BASELINE)
    out["species_storage_max_id"] = (1 << out["species_storage_bits"]) - 1
    out["item_storage_max_id"] = (1 << out["item_storage_bits"]) - 1
    out["move_storage_max_id"] = (1 << out["move_storage_bits"]) - 1
    out["species_headroom_ids"] = (1 << out["species_storage_bits"]) - out["species_count"]
    out["item_headroom_ids"] = (1 << out["item_storage_bits"]) - out["item_count"]
    out["regular_move_headroom_ids"] = (1 << out["move_storage_bits"]) - out["regular_move_count"]
    out["saveblock3_default_feature_note"] = "default pin disables DexNav search levels/follower/fake RTC/first-time item descriptions"
    return out


def report_patched(root: Path) -> dict:
    pokemon_h = read(root, "include/pokemon.h")
    pokemon_c = read(root, "src/pokemon.c")

    for pat, label in [
        (r"u16 heldItemHigh:6;", "held item high 6 bits"),
        (r"u32 speciesHighMid:3;", "species high middle 3 bits"),
        (r"u16 speciesHighTop:2;", "species high top 2 bits"),
        (r"YellowGetStoredSpeciesId", "species decode helper"),
        (r"YellowSetStoredSpeciesId", "species encode helper"),
        (r"YellowGetStoredItemId", "item decode helper"),
        (r"YellowSetStoredItemId", "item encode helper"),
    ]:
        require(pokemon_h + "\n" + pokemon_c, pat, label)

    forbidden = [
        "unused_02:6",
        "unused_04:3",
        "unused_0A:2",
        "SET16(substruct0->species)",
        "SET16(GetSubstruct0(boxMon)->heldItem)",
        "retVal = GetSubstruct0(boxMon)->heldItem;",
    ]
    present = [x for x in forbidden if x in pokemon_h or x in pokemon_c]
    if present:
        raise RuntimeError("Stage 1 stale narrow access remains: " + ", ".join(present))

    # Direct low-species use outside the helper is dangerous for IDs >= 2048.
    helper_start = pokemon_c.index("static u16 YellowGetStoredSpeciesId")
    data_start = pokemon_c.index("u32 GetBoxMonData3")
    helper_text = pokemon_c[helper_start:data_start]
    rest = pokemon_c[:helper_start] + pokemon_c[data_start:]
    dangerous = [
        "gSpeciesInfo[substruct0->species]",
        "retVal = GetSubstruct0(boxMon)->species;",
    ]
    leaked = [x for x in dangerous if x in rest]
    if leaked:
        raise RuntimeError("direct low-species access remains: " + ", ".join(leaked))

    return {
        "stage": 1,
        "species_storage_bits": 16,
        "held_item_storage_bits": 16,
        "species_max_valid_id": 65534,
        "held_item_max_valid_id": 65534,
        "boxpokemon_size_change_bytes": 0,
        "legacy_spare_bits_consumed": 11,
        "legacy_spare_bits_available": 11,
        "move_storage_bits": 11,
        "move_stage2_required": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("upstream_root", type=Path)
    ap.add_argument("--mode", choices=("baseline", "patched"), required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = args.upstream_root.resolve()
    result = report_baseline(root) if args.mode == "baseline" else report_patched(root)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
