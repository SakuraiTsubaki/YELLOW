#!/usr/bin/env python3
"""Apply YELLOW Gen10-ready Stage 1 storage widening to pinned pokeemerald-expansion.

Stage 1 widens persistent species and held-item IDs to 16 bits without changing
the 80-byte BoxPokemon layout. It reuses exactly 11 bits that are unused in the
pinned upstream PokemonSubstruct0.

The patch is intentionally strict and pin-specific: every replacement must
match exactly once or the script fails instead of silently patching a different
upstream layout.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PIN = "75b806a3ab57a81ff1eb6179288981f0b3cc3050"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, got {count}")
    return text.replace(old, new, 1)


def patch_header(root: Path) -> None:
    path = root / "include" / "pokemon.h"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """    enum Species species:11; // 2047 species.
    enum Type teraType:5; // 30 types.
    enum Item heldItem:10; // 1023 items.
    u16 unused_02:6;
    u32 experience:21;
    u32 nickname11:8; // 11th character of nickname.
    u32 unused_04:3;
    u8 ppBonuses;
    u8 friendship;
    u16 pokeball:6; // 63 balls.
    u16 nickname12:8; // 12th character of nickname.
    u16 unused_0A:2;
""",
        """    // Low bits retain the pinned expansion layout. YELLOW stores the
    // remaining high bits in fields that were unused by this upstream pin,
    // keeping PokemonSubstruct0 and BoxPokemon byte sizes unchanged.
    enum Species species:11;
    enum Type teraType:5; // 30 types.
    enum Item heldItem:10;
    u16 heldItemHigh:6;   // held-item bits 10-15
    u32 experience:21;
    u32 nickname11:8;     // 11th character of nickname.
    u32 speciesHighMid:3; // species bits 11-13
    u8 ppBonuses;
    u8 friendship;
    u16 pokeball:6;       // 63 balls.
    u16 nickname12:8;     // 12th character of nickname.
    u16 speciesHighTop:2; // species bits 14-15
""",
        "PokemonSubstruct0 packing",
    )
    path.write_text(text, encoding="utf-8")


def patch_pokemon_c(root: Path) -> None:
    path = root / "src" / "pokemon.c"
    text = path.read_text(encoding="utf-8")

    marker = "u32 GetBoxMonData3(struct BoxPokemon *boxMon, s32 field, u8 *data)\n"
    helpers = r'''// YELLOW: Gen10-ready persistent ID packing.
//
// The pinned expansion uses 11 low species bits and 10 low held-item bits in
// PokemonSubstruct0. Stage 1 reuses its former spare bits for the upper bits.
// Old saves remain readable because those spare bits were zero.
static u16 YellowGetStoredSpeciesId(const struct PokemonSubstruct0 *substruct0)
{
    return (u16)substruct0->species
         | ((u16)substruct0->speciesHighMid << 11)
         | ((u16)substruct0->speciesHighTop << 14);
}

static void YellowSetStoredSpeciesId(struct PokemonSubstruct0 *substruct0, u16 species)
{
    substruct0->species = species & 0x07FF;
    substruct0->speciesHighMid = (species >> 11) & 0x7;
    substruct0->speciesHighTop = (species >> 14) & 0x3;
}

static u16 YellowGetStoredItemId(const struct PokemonSubstruct0 *substruct0)
{
    return (u16)substruct0->heldItem
         | ((u16)substruct0->heldItemHigh << 10);
}

static void YellowSetStoredItemId(struct PokemonSubstruct0 *substruct0, u16 item)
{
    substruct0->heldItem = item & 0x03FF;
    substruct0->heldItemHigh = (item >> 10) & 0x3F;
}

'''
    text = replace_once(text, marker, helpers + marker, "helper insertion")

    text = replace_once(
        text,
        "retVal = IsBadEgg(boxMon) ? SPECIES_EGG : GetSubstruct0(boxMon)->species;",
        "retVal = IsBadEgg(boxMon) ? SPECIES_EGG : YellowGetStoredSpeciesId(GetSubstruct0(boxMon));",
        "MON_DATA_SPECIES getter",
    )
    text = replace_once(
        text,
        "retVal = GetSubstruct0(boxMon)->heldItem;",
        "retVal = YellowGetStoredItemId(GetSubstruct0(boxMon));",
        "MON_DATA_HELD_ITEM getter",
    )

    # Species-or-egg has one direct read in the MON_DATA switch.
    text = replace_once(
        text,
        """        case MON_DATA_SPECIES_OR_EGG:
            retVal = GetSubstruct0(boxMon)->species;
            if (retVal && IsEggOrBadEgg(boxMon))
""",
        """        case MON_DATA_SPECIES_OR_EGG:
            retVal = YellowGetStoredSpeciesId(GetSubstruct0(boxMon));
            if (retVal && IsEggOrBadEgg(boxMon))
""",
        "MON_DATA_SPECIES_OR_EGG getter",
    )

    # Two feature cases gate on whether a valid species is present.
    direct_species_guard = "if (GetSubstruct0(boxMon)->species && !IsEggOrBadEgg(boxMon))"
    guard_count = text.count(direct_species_guard)
    if guard_count < 2:
        raise RuntimeError(f"species guard: expected at least 2 matches, got {guard_count}")
    text = text.replace(
        direct_species_guard,
        "if (YellowGetStoredSpeciesId(GetSubstruct0(boxMon)) && !IsEggOrBadEgg(boxMon))",
    )

    old_tera = """            {
                struct PokemonSubstruct0 *substruct0 = GetSubstruct0(boxMon);
                if (gSpeciesInfo[substruct0->species].forceTeraType)
                {
                    retVal = gSpeciesInfo[substruct0->species].forceTeraType;
                }
                else if (substruct0->teraType == TYPE_NONE) // Tera Type hasn't been modified so we can just use the personality
                {
                    const enum Type *types = gSpeciesInfo[substruct0->species].types;
"""
    new_tera = """            {
                struct PokemonSubstruct0 *substruct0 = GetSubstruct0(boxMon);
                enum Species storedSpecies = YellowGetStoredSpeciesId(substruct0);
                if (gSpeciesInfo[storedSpecies].forceTeraType)
                {
                    retVal = gSpeciesInfo[storedSpecies].forceTeraType;
                }
                else if (substruct0->teraType == TYPE_NONE) // Tera Type hasn't been modified so we can just use the personality
                {
                    const enum Type *types = gSpeciesInfo[storedSpecies].types;
"""
    text = replace_once(text, old_tera, new_tera, "tera species lookup")

    old_species_set = """        case MON_DATA_SPECIES:
        {
            struct PokemonSubstruct0 *substruct0 = GetSubstruct0(boxMon);
            SET16(substruct0->species);
            if (substruct0->species)
                boxMon->hasSpecies = TRUE;
            else
                boxMon->hasSpecies = FALSE;
            break;
        }
"""
    new_species_set = """        case MON_DATA_SPECIES:
        {
            struct PokemonSubstruct0 *substruct0 = GetSubstruct0(boxMon);
            u16 species;
            SET16(species);
            YellowSetStoredSpeciesId(substruct0, species);
            boxMon->hasSpecies = species != SPECIES_NONE;
            break;
        }
"""
    text = replace_once(text, old_species_set, new_species_set, "MON_DATA_SPECIES setter")

    text = replace_once(
        text,
        """        case MON_DATA_HELD_ITEM:
            SET16(GetSubstruct0(boxMon)->heldItem);
            break;
""",
        """        case MON_DATA_HELD_ITEM:
        {
            u16 item;
            SET16(item);
            YellowSetStoredItemId(GetSubstruct0(boxMon), item);
            break;
        }
""",
        "MON_DATA_HELD_ITEM setter",
    )

    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("upstream_root", type=Path)
    args = ap.parse_args()
    root = args.upstream_root.resolve()

    required = [root / "include" / "pokemon.h", root / "src" / "pokemon.c"]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit("missing pinned upstream files: " + ", ".join(missing))

    patch_header(root)
    patch_pokemon_c(root)
    print("YELLOW Gen10 storage Stage 1 applied: 16-bit species + held items, BoxPokemon size preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
