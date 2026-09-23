#!/usr/bin/env python3
"""Build YELLOW's 16-bit logical-ID -> 9-bit-bank ROMX pointer index.

The index is generated from a list of logical IDs and target bank/address pairs.
Each entry is a 3-byte farptr9. IDs need not be contiguous; missing IDs encode
the invalid pointer FF FF FF.

This is the bridge that removes direct "ID * record_size inside one bank"
assumptions from the original Yellow engine.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

INVALID = b"\xff\xff\xff"
MAX_VALID_ID = 0xFFFE
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


def unpack_farptr9(raw: bytes) -> tuple[int, int] | None:
    if raw == INVALID:
        return None
    if len(raw) != 3:
        raise ValueError("entry must be exactly 3 bytes")
    low = raw[0]
    packed = raw[1] | (raw[2] << 8)
    if packed & 0x8000:
        raise ValueError("reserved farptr9 bit set")
    bank = low | (((packed >> 14) & 1) << 8)
    address = ROMX_BASE + (packed & 0x3FFF)
    return bank, address


def build_index(rows: list[tuple[int, int, int]], *, max_id: int | None = None) -> bytes:
    if not rows and max_id is None:
        return b""
    seen=set()
    for logical_id, bank, address in rows:
        if not 0 <= logical_id <= MAX_VALID_ID:
            raise ValueError(f"logical id out of range: {logical_id}")
        if logical_id in seen:
            raise ValueError(f"duplicate logical id: {logical_id}")
        seen.add(logical_id)
        pack_farptr9(bank,address)
    highest=max((x[0] for x in rows), default=-1)
    if max_id is None:
        max_id=highest
    if max_id < highest:
        raise ValueError("max_id smaller than highest input id")
    if max_id > MAX_VALID_ID:
        raise ValueError("max_id out of range")

    out=bytearray(INVALID * (max_id+1))
    for logical_id,bank,address in rows:
        off=logical_id*3
        out[off:off+3]=pack_farptr9(bank,address)
    return bytes(out)


def read_csv(path: Path) -> list[tuple[int,int,int]]:
    rows=[]
    with path.open(newline="",encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append((
                int(row["id"],0),
                int(row["bank"],0),
                int(row["address"],0),
            ))
    return rows


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("input_csv",type=Path)
    ap.add_argument("output_bin",type=Path)
    ap.add_argument("--max-id",type=lambda x:int(x,0))
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()

    rows=read_csv(args.input_csv)
    index=build_index(rows,max_id=args.max_id)
    args.output_bin.write_bytes(index)
    report={
        "entries":len(index)//3,
        "bytes":len(index),
        "defined":len(rows),
        "missing":len(index)//3-len(rows),
        "max_defined_id":max((x[0] for x in rows),default=None),
        "output":str(args.output_bin),
    }
    print(json.dumps(report,indent=2,sort_keys=True) if args.json else report)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
