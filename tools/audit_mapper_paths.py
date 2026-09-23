#!/usr/bin/env python3
"""Audit Yellow mapper-write surfaces in ROM bytes or an RGBDS source tree.

ROM mode reports instruction candidates: EA ll hh is LD [a16], A.
Source mode finds explicit RGBDS mapper-register writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

REGISTERS = {
    0x0000: "ram_enable",
    0x2000: "rom_bank_low",
    0x3000: "rom_bank_high_mbc5",
    0x4000: "ram_bank_or_rtc",
    0x6000: "mode_or_latch",
}

SOURCE_PATTERNS = {
    "rROMB": re.compile(r"\bld\s+\[rROMB\],\s*a\b"),
    "rROMB0": re.compile(r"\bld\s+\[rROMB0\],\s*a\b"),
    "rROMB1": re.compile(r"\bld\s+\[rROMB1\],\s*a\b"),
    "rRAMB": re.compile(r"\bld\s+\[rRAMB\],\s*a\b"),
    "rBMODE": re.compile(r"\bld\s+\[rBMODE\],\s*a\b"),
}

def scan_rom(path: Path) -> dict:
    data = path.read_bytes()
    out = {
        "mode": "rom",
        "path": str(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "cartridge_type": f"0x{data[0x147]:02X}" if len(data) > 0x147 else None,
        "registers": {},
    }
    for addr, role in REGISTERS.items():
        pat = bytes((0xEA, addr & 0xff, (addr >> 8) & 0xff))
        hits = []
        start = 0
        while True:
            pos = data.find(pat, start)
            if pos < 0:
                break
            hits.append(pos)
            start = pos + 1
        out["registers"][f"0x{addr:04X}"] = {
            "role": role,
            "candidate_count": len(hits),
            "offsets": [f"0x{x:06X}" for x in hits],
        }
    out["direct_mbc5_high_bank_candidate_count"] = out["registers"]["0x3000"]["candidate_count"]
    return out

def scan_source(root: Path) -> dict:
    files = sorted(p for p in root.rglob("*.asm") if p.is_file())
    hits = {k: [] for k in SOURCE_PATTERNS}
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in SOURCE_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                hits[name].append({
                    "path": str(path.relative_to(root)),
                    "line": line,
                })
    return {
        "mode": "source",
        "root": str(root),
        "counts": {k: len(v) for k, v in hits.items()},
        "hits": hits,
        "mbc5_high_bank_explicitly_used": bool(hits["rROMB1"]),
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rom", type=Path)
    group.add_argument("--source-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = scan_rom(args.rom) if args.rom else scan_source(args.source_root)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
