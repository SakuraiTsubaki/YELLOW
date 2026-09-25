#!/usr/bin/env python3
"""Apply YELLOW's original-GB expansion runtime overlay to pret/pokeyellow.

The reference checkout is treated as a structural build target. This script:
- copies YELLOW's expansion ASM into the checkout;
- adds ROM bank $40 for the SRAM runtime service;
- adds a bank-$7F anchor so the linked image is exactly 2 MiB;
- installs the SRAM service during Init while interrupts are disabled;
- changes the expanded build RAM header from 32 KiB to 128 KiB.

It is strict and idempotent: unexpected source text aborts instead of guessing.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SERVICE_BLOCK = """
; YELLOW EXPANSION OVERLAY BEGIN
SECTION "YELLOW Expansion Service ROM", ROMX[$4000], BANK[$40]
INCLUDE "asm/expansion/sram_service.asm"

SECTION "YELLOW Expansion ROM Anchor", ROMX[$7fff], BANK[$7f]
    db $ff
; YELLOW EXPANSION OVERLAY END
""".lstrip()

LAYOUT_BLOCK = """ROMX $40
	"YELLOW Expansion Service ROM"
ROMX $7F
	org $7FFF
	"YELLOW Expansion ROM Anchor"
"""

INIT_OLD = """	call ClearSprites

	ld a, BANK(WriteDMACodeToHRAM)
"""
INIT_NEW = """	call ClearSprites

	; YELLOW expansion: install the SRAM-bank-15 runtime service while
	; interrupts are still disabled and legacy bank state is zeroed.
	ld b, BANK(YellowInstallSRAMServiceLocked)
	ld hl, YellowInstallSRAMServiceLocked
	call Bankswitch

	ld a, BANK(WriteDMACodeToHRAM)
"""

EXPANSION_FILES = (
    "farptr9.inc",
    "id16.inc",
    "index16.asm",
    "item16.asm",
    "item_core.inc",
    "mbc5_bank9.asm",
    "move16.asm",
    "move_core.inc",
    "species16.asm",
    "species_core.inc",
    "sram_service.asm",
    "wram_id16.asm",
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 source match, got {count}")
    return text.replace(old, new, 1)


def patch_main(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "YELLOW EXPANSION OVERLAY BEGIN" not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + SERVICE_BLOCK
    path.write_text(text, encoding="utf-8")


def patch_layout(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if '"YELLOW Expansion Service ROM"' not in text:
        marker = "WRAM0\n"
        if text.count(marker) != 1:
            raise RuntimeError("layout.link: WRAM0 marker is not unique")
        text = text.replace(marker, LAYOUT_BLOCK + marker, 1)
    path.write_text(text, encoding="utf-8")


def patch_init(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, INIT_OLD, INIT_NEW, "home/init.asm")
    path.write_text(text, encoding="utf-8")


def patch_makefile(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    expanded = 'RGBFIXFLAGS += -cjsv -k 01 -l 0x33 -m MBC5+RAM+BATTERY -r 04 -t "POKEMON YELLOW"'
    legacy = 'RGBFIXFLAGS += -cjsv -k 01 -l 0x33 -m MBC5+RAM+BATTERY -r 03 -t "POKEMON YELLOW"'
    if expanded not in text:
        if text.count(legacy) != 1:
            raise RuntimeError("Makefile: expected one Yellow RGBFIXFLAGS line")
        text = text.replace(legacy, expanded, 1)
    path.write_text(text, encoding="utf-8")


def copy_expansion(repo_root: Path, target_root: Path) -> None:
    source = repo_root / "asm" / "expansion"
    dest = target_root / "asm" / "expansion"
    dest.mkdir(parents=True, exist_ok=True)
    for name in EXPANSION_FILES:
        src = source / name
        if not src.is_file():
            raise RuntimeError(f"missing YELLOW expansion source: {src}")
        shutil.copy2(src, dest / name)


def apply(repo_root: Path, target_root: Path) -> None:
    for rel in ("main.asm", "layout.link", "home/init.asm", "Makefile"):
        if not (target_root / rel).is_file():
            raise RuntimeError(f"not a pokeyellow checkout: missing {rel}")

    copy_expansion(repo_root, target_root)
    patch_main(target_root / "main.asm")
    patch_layout(target_root / "layout.link")
    patch_init(target_root / "home" / "init.asm")
    patch_makefile(target_root / "Makefile")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_root", type=Path)
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = ap.parse_args()
    apply(args.repo_root.resolve(), args.target_root.resolve())
    print("YELLOW runtime overlay applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
