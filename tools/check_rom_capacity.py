#!/usr/bin/env python3
"""Check a built GBA ROM against YELLOW's native 32 MiB budget."""

from __future__ import annotations
import argparse
import json
from pathlib import Path

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = capacity_report(args.rom.stat().st_size)
    report["path"] = str(args.rom)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"{args.rom}: {report['size_mib']:.3f} MiB / 32.000 MiB "
            f"({report['used_percent']:.2f}%), "
            f"{report['remaining_mib']:.3f} MiB remaining"
        )
        if report["inside_tail_reserve"]:
            print("warning: build has entered YELLOW's final 256 KiB emergency reserve")
        elif report["warn"]:
            print("warning: ROM usage is at or above 90%")

    return 1 if report["over_native_limit"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
