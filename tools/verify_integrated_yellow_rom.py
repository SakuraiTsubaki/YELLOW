#!/usr/bin/env python3
"""Verify the structural expanded Yellow integration build."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_BYTES = 2 * 1024 * 1024
EXPECTED_CART = 0x1B
EXPECTED_ROM_SIZE = 0x06
EXPECTED_RAM_SIZE = 0x04


def header_checksum(data: bytes) -> int:
    value = 0
    for byte in data[0x134:0x14D]:
        value = (value - byte - 1) & 0xFF
    return value


def global_checksum(data: bytes) -> int:
    return (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF


def verify(data: bytes) -> dict:
    report = {
        "bytes": len(data),
        "mib": len(data) / (1024 * 1024),
        "cartridge_type": data[0x147] if len(data) > 0x149 else None,
        "rom_size_code": data[0x148] if len(data) > 0x149 else None,
        "ram_size_code": data[0x149] if len(data) > 0x149 else None,
    }
    report["size_ok"] = len(data) == EXPECTED_BYTES
    report["mapper_ok"] = report["cartridge_type"] == EXPECTED_CART
    report["rom_size_ok"] = report["rom_size_code"] == EXPECTED_ROM_SIZE
    report["ram_size_ok"] = report["ram_size_code"] == EXPECTED_RAM_SIZE
    report["header_checksum_ok"] = (
        len(data) > 0x14D and header_checksum(data) == data[0x14D]
    )
    report["global_checksum_ok"] = (
        len(data) > 0x14F
        and global_checksum(data)
        == int.from_bytes(data[0x14E:0x150], "big")
    )
    if not all(
        report[key]
        for key in (
            "size_ok",
            "mapper_ok",
            "rom_size_ok",
            "ram_size_ok",
            "header_checksum_ok",
            "global_checksum_ok",
        )
    ):
        raise ValueError(f"expanded Yellow build verification failed: {report}")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = verify(args.rom.read_bytes())
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
