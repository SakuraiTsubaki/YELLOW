#!/usr/bin/env python3
"""Audit the original Yellow source model for 8-bit ID chokepoints.

This audit is intentionally source-structural. It does not claim that the
public disassembly is the Japanese master ROM; Japanese ROM hashes remain the
project's canonical evidence. The source tree is used to make width assumptions
explicit and reproducible.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CHECKS = [
    ("persistent", "macros/ram.asm", r"\\1Species::\s+db", "box/party species is 8-bit"),
    ("persistent", "macros/ram.asm", r"\\1Moves::\s+ds\s+NUM_MOVES", "four persistent moves are byte entries"),
    ("runtime", "macros/ram.asm", r"MACRO battle_struct[\s\S]*?\\1Species::\s+db", "battle species is 8-bit"),
    ("runtime", "macros/ram.asm", r"MACRO battle_struct[\s\S]*?\\1Moves::\s+ds\s+NUM_MOVES", "battle moves are byte entries"),
    ("runtime", "ram/wram.asm", r"wCurSpecies::[\s\S]{0,100}?db", "current species is 8-bit"),
    ("runtime", "ram/wram.asm", r"wCurPartySpecies::[\s\S]{0,80}?db", "current party species alias is 8-bit"),
    ("runtime", "ram/wram.asm", r"wCurItem::[\s\S]{0,80}?db", "current item is 8-bit"),
    ("runtime", "ram/wram.asm", r"wMoveNum::\s+db", "current move is 8-bit"),
    ("runtime", "ram/wram.asm", r"wPlayerSelectedMove::\s+db", "selected player move is 8-bit"),
    ("runtime", "ram/wram.asm", r"wEnemySelectedMove::\s+db", "selected enemy move is 8-bit"),
    ("runtime", "ram/wram.asm", r"wCapturedMonSpecies::\s+db", "captured species is 8-bit"),
    ("runtime", "ram/wram.asm", r"wPlayerStarter::\s+db", "player starter is 8-bit"),
    ("runtime", "ram/wram.asm", r"wRivalStarter::\s+db", "rival starter is 8-bit"),
    ("runtime", "ram/wram.asm", r"wFossilMon::\s+db", "fossil result species is 8-bit"),
    ("runtime", "ram/wram.asm", r"wEnemyMonOrTrainerClass::\s+db", "enemy species/trainer selector shares one byte"),
    ("dex", "ram/wram.asm", r"wPokedexOwned::\s+flag_array\s+NUM_POKEMON", "Pokedex owned bitset is compile-time species count"),
    ("dex", "ram/wram.asm", r"wPokedexSeen::\s+flag_array\s+NUM_POKEMON", "Pokedex seen bitset is compile-time species count"),
    ("bank", "ram/hram.asm", r"hLoadedROMBank::\s+db", "loaded ROM bank tracker is 8-bit"),
    ("bank", "ram/hram.asm", r"hMapROMBank::\s+db", "map ROM bank tracker is 8-bit"),
]

ROM_TABLE_PATTERNS = [
    ("wild", "data/wild", "level/species pairs use one-byte species in Gen I format"),
    ("trainer", "data/trainers", "trainer party species IDs use Gen I byte format"),
    ("base_stats", "data/pokemon/base_stats.asm", "base-stat table is indexed by Gen I species index"),
    ("names", "data/pokemon/names.asm", "name table is indexed by Gen I species index"),
    ("evos_moves", "data/pokemon/evos_moves.asm", "evolution/learnset pointers use Gen I species index"),
]


def read(root: Path, rel: str) -> str:
    path=root/rel
    if not path.is_file():
        raise FileNotFoundError(rel)
    return path.read_text(encoding="utf-8")


def audit(root: Path) -> dict:
    results=[]
    failures=[]
    cache={}
    for layer, rel, pattern, note in CHECKS:
        text=cache.setdefault(rel, read(root, rel))
        ok=re.search(pattern,text,re.MULTILINE) is not None
        row={"layer":layer,"path":rel,"pattern":pattern,"confirmed":ok,"note":note}
        results.append(row)
        if not ok:
            failures.append(row)

    tables=[]
    for layer, rel, note in ROM_TABLE_PATTERNS:
        path=root/rel
        exists=path.exists()
        tables.append({"layer":layer,"path":rel,"confirmed_present":exists,"note":note})
        if not exists:
            failures.append(tables[-1])

    return {
        "source_root":str(root),
        "confirmed_checks":sum(1 for x in results if x["confirmed"]),
        "total_checks":len(results),
        "all_required_patterns_present":not failures,
        "checks":results,
        "rom_table_surfaces":tables,
        "migration_layers":{
            "persistent":"sidecar v1 already defined",
            "runtime":"must widen working IDs before IDs >255 are enabled",
            "rom_tables":"must add 16-bit/banked generated formats",
            "protocol":"link/trade needs explicit compatibility/versioning",
        },
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("source_root",type=Path)
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    report=audit(args.source_root.resolve())
    print(json.dumps(report,indent=2,sort_keys=True) if args.json else report)
    return 0 if report["all_required_patterns_present"] else 1

if __name__=="__main__":
    raise SystemExit(main())
