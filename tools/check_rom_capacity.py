#!/usr/bin/env python3
"""Check YELLOW's native 32 MiB GBA ROM budget.

A built .gba may be padded to the full cartridge size, so linked usage should be
measured from the ELF linker symbol __rom_end. Raw file-size mode remains useful
for enforcing the physical image ceiling.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROM_BASE_ADDRESS = 0x08000000
MAX_BYTES = 32 * 1024 * 1024
RESERVE_TAIL_BYTES = 256 * 1024
USABLE_BEFORE_RESERVE = MAX_BYTES - RESERVE_TAIL_BYTES
WARN_PERCENT = 90
WARN_BYTES = (MAX_BYTES * WARN_PERCENT + 99) // 100


def capacity_report(size: int) -> dict:
    if size < 0:
        raise ValueError("size must be non-negative")
    used_percent = (size / MAX_BYTES * 100.0) if MAX_BYTES else 0.0
    return {
        "size_bytes": size,
        "size_mib": size / (1024 * 1024),
        "max_bytes": MAX_BYTES,
        "max_mib": 32,
        "remaining_bytes": max(0, MAX_BYTES - size),
        "remaining_mib": max(0, MAX_BYTES - size) / (1024 * 1024),
        "used_percent": used_percent,
        "over_native_limit": size > MAX_BYTES,
        "inside_tail_reserve": USABLE_BEFORE_RESERVE < size <= MAX_BYTES,
        "over_preferred_budget": size > USABLE_BEFORE_RESERVE,
        "warn": size >= WARN_BYTES,
    }


def parse_nm_rom_end(output: str) -> int:
    for line in output.splitlines():
        match = re.match(r"^\s*([0-9A-Fa-f]+)\s+\S\s+__rom_end\s*$", line)
        if match:
            return int(match.group(1), 16)
    raise ValueError("__rom_end symbol not found in nm output")


def linked_rom_size_from_elf(path: Path, nm: str = "arm-none-eabi-nm") -> tuple[int, int]:
    output = subprocess.check_output(
        [nm, "-n", str(path)],
        text=True,
        stderr=subprocess.STDOUT,
    )
    rom_end = parse_nm_rom_end(output)
    if rom_end < ROM_BASE_ADDRESS:
        raise ValueError(
            f"__rom_end {rom_end:#010x} is below GBA ROM base {ROM_BASE_ADDRESS:#010x}"
        )
    return rom_end - ROM_BASE_ADDRESS, rom_end


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", type=Path)
    ap.add_argument(
        "--elf",
        action="store_true",
        help="measure linked usage from __rom_end instead of padded file size",
    )
    ap.add_argument("--nm", default="arm-none-eabi-nm")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.elf:
        size, rom_end = linked_rom_size_from_elf(args.artifact, args.nm)
        source_kind = "linked_elf"
    else:
        size = args.artifact.stat().st_size
        rom_end = None
        source_kind = "raw_file"

    report = capacity_report(size)
    report["path"] = str(args.artifact)
    report["source_kind"] = source_kind
    report["rom_base_address"] = ROM_BASE_ADDRESS
    if rom_end is not None:
        report["rom_end_address"] = rom_end

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"{args.artifact}: {report['size_mib']:.3f} MiB / 32.000 MiB "
            f"({report['used_percent']:.2f}%), "
            f"{report['remaining_mib']:.3f} MiB remaining "
            f"[{source_kind}]"
        )
        if report["inside_tail_reserve"]:
            print("warning: linked usage has entered YELLOW's final 256 KiB emergency reserve")
        elif report["warn"]:
            print("warning: ROM usage is at or above 90%")

    return 1 if report["over_native_limit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
