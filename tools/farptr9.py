#!/usr/bin/env python3
"""Reference encoder/decoder for YELLOW's 3-byte 9-bit-bank ROMX pointers."""
from __future__ import annotations

import argparse
import json

ROMX_BASE = 0x4000
ROMX_END = 0x8000
MAX_BANK = 0x1FF


def pack_farptr9(bank: int, address: int) -> bytes:
    if not 0 <= bank <= MAX_BANK:
        raise ValueError(f"bank out of range: {bank}")
    if not ROMX_BASE <= address < ROMX_END:
        raise ValueError(f"address is not ROMX: 0x{address:04X}")
    offset = address - ROMX_BASE
    packed = offset | (((bank >> 8) & 1) << 14)
    return bytes((bank & 0xFF, packed & 0xFF, (packed >> 8) & 0xFF))


def unpack_farptr9(raw: bytes) -> tuple[int, int]:
    if len(raw) != 3:
        raise ValueError("farptr9 must be exactly 3 bytes")
    low_bank = raw[0]
    packed = raw[1] | (raw[2] << 8)
    if packed & 0x8000:
        raise ValueError("reserved farptr9 bit 15 is set")
    bank = low_bank | (((packed >> 14) & 1) << 8)
    address = ROMX_BASE + (packed & 0x3FFF)
    return bank, address


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bank", type=lambda x: int(x, 0))
    parser.add_argument("address", type=lambda x: int(x, 0))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    raw = pack_farptr9(args.bank, args.address)
    bank, address = unpack_farptr9(raw)
    report = {
        "bank": bank,
        "address": f"0x{address:04X}",
        "bytes": raw.hex(),
    }
    print(json.dumps(report, indent=2) if args.json else report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
