#!/usr/bin/env python3
"""Report longest 00/FF padding run in a Game Boy ROM0 bank."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROM0_SIZE=0x4000

def longest_padding(data: bytes) -> dict:
    chunk=data[:ROM0_SIZE]
    best=(0,0,0,None)
    i=0
    while i<len(chunk):
        value=chunk[i]
        j=i+1
        while j<len(chunk) and chunk[j]==value:
            j+=1
        if value in (0x00,0xFF) and j-i>best[2]:
            best=(i,j,j-i,value)
        i=j
    start,end,length,value=best
    return {
        "start":start,
        "end_exclusive":end,
        "length":length,
        "fill":None if value is None else f"0x{value:02X}",
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("rom",type=Path)
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    data=args.rom.read_bytes()
    report={
        "path":str(args.rom),
        "sha256":hashlib.sha256(data).hexdigest(),
        "rom0":longest_padding(data),
    }
    print(json.dumps(report,indent=2,sort_keys=True) if args.json else report)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
