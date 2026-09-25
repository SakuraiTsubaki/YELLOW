#!/usr/bin/env python3
"""Verify RGBDS symbol placement for YELLOW's SRAM runtime service."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LINE_RE = re.compile(r"^([0-9A-Fa-f]{2}):([0-9A-Fa-f]{4})\s+(.+)$")

REQUIRED = {
    "YellowSRAMServiceImage": ("rom_image", 0x40, 0x4000, 0x7FFF),
    "YellowCopySpeciesCore16Locked": ("sram_code", 0x0F, 0xBC00, 0xBFFF),
    "YellowCopyMoveCore16Locked": ("sram_code", 0x0F, 0xBC00, 0xBFFF),
    "YellowCopyItemCore16Locked": ("sram_code", 0x0F, 0xBC00, 0xBFFF),
}


def parse_symbols(text: str) -> dict[str, tuple[int, int]]:
    out = {}
    for line in text.splitlines():
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        bank = int(m.group(1), 16)
        addr = int(m.group(2), 16)
        name = m.group(3).split()[0]
        out[name] = (bank, addr)
    return out


def verify(symbols: dict[str, tuple[int, int]]) -> dict:
    report = {}
    for name, (kind, expected_bank, lo, hi) in REQUIRED.items():
        if name not in symbols:
            raise ValueError(f"missing symbol: {name}")
        bank, addr = symbols[name]
        if bank != expected_bank:
            raise ValueError(
                f"{name}: bank {bank:#x}, expected {expected_bank:#x}"
            )
        if not lo <= addr <= hi:
            raise ValueError(
                f"{name}: address {addr:#06x}, expected {lo:#06x}..{hi:#06x}"
            )
        report[name] = {
            "kind": kind,
            "bank": bank,
            "address": addr,
        }

    service_addrs = [
        report[name]["address"]
        for name in REQUIRED
        if REQUIRED[name][0] == "sram_code"
    ]
    report["service_span"] = {
        "lowest_checked_address": min(service_addrs),
        "highest_checked_address": max(service_addrs),
        "window_start": 0xBC00,
        "window_end_exclusive": 0xC000,
    }
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sym", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = verify(parse_symbols(args.sym.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
