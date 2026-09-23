#!/usr/bin/env python3
"""Pack logical-ID records into 16 KiB MBC5 ROMX banks and build a farptr9 index."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

BANK_SIZE=0x4000
ROMX_BASE=0x4000
MAX_BANK=0x1FF
MAX_ID=0xFFFE
INVALID=b"\xff\xff\xff"

def align_up(value:int,alignment:int)->int:
    if alignment<=0 or alignment&(alignment-1):
        raise ValueError("alignment must be a positive power of two")
    return (value+alignment-1)&~(alignment-1)

def pack_farptr9(bank:int,address:int)->bytes:
    if not 0<=bank<=MAX_BANK:
        raise ValueError(f"bank out of range: {bank}")
    if not ROMX_BASE<=address<0x8000:
        raise ValueError(f"address not ROMX: 0x{address:04X}")
    off=address-ROMX_BASE
    word=off|(((bank>>8)&1)<<14)
    return bytes((bank&0xff,word&0xff,(word>>8)&0xff))

def read_manifest(path:Path)->list[tuple[int,Path]]:
    rows=[];seen=set()
    with path.open(newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            logical_id=int(row["id"],0)
            if not 0<=logical_id<=MAX_ID:
                raise ValueError(f"id out of range: {logical_id}")
            if logical_id in seen:
                raise ValueError(f"duplicate id: {logical_id}")
            seen.add(logical_id)
            rows.append((logical_id,(path.parent/row["path"]).resolve()))
    rows.sort(key=lambda x:x[0])
    return rows

def pack_records(records:list[tuple[int,bytes]],*,start_bank:int=64,end_bank:int=MAX_BANK,alignment:int=1,fill:int=0xff)->tuple[bytes,bytes,list[dict]]:
    if not 0<=start_bank<=end_bank<=MAX_BANK:
        raise ValueError("invalid bank range")
    if not 0<=fill<=0xff:
        raise ValueError("fill byte out of range")
    if not records:
        return b"",b"",[]
    highest=max(x[0] for x in records)
    index=bytearray(INVALID*(highest+1))
    bank=start_bank;offset=0;bank_images={};layout=[]
    for logical_id,data in sorted(records,key=lambda x:x[0]):
        if len(data)>BANK_SIZE:
            raise ValueError(f"record {logical_id} exceeds one ROM bank")
        aligned=align_up(offset,alignment)
        if aligned+len(data)>BANK_SIZE:
            bank+=1;offset=0;aligned=0
        if bank>end_bank:
            raise ValueError("record set exceeds configured ROM bank range")
        image=bank_images.setdefault(bank,bytearray([fill])*BANK_SIZE)
        image[aligned:aligned+len(data)]=data
        address=ROMX_BASE+aligned
        index[logical_id*3:logical_id*3+3]=pack_farptr9(bank,address)
        layout.append({"id":logical_id,"bank":bank,"address":address,"bank_offset":aligned,"size":len(data)})
        offset=aligned+len(data)
    first=min(bank_images);last=max(bank_images)
    out=bytearray()
    for b in range(first,last+1):
        out.extend(bank_images.get(b,bytearray([fill])*BANK_SIZE))
    return bytes(out),bytes(index),layout

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest",type=Path)
    ap.add_argument("output_banks",type=Path)
    ap.add_argument("output_index",type=Path)
    ap.add_argument("output_layout",type=Path)
    ap.add_argument("--start-bank",type=lambda x:int(x,0),default=64)
    ap.add_argument("--end-bank",type=lambda x:int(x,0),default=0x1ff)
    ap.add_argument("--alignment",type=lambda x:int(x,0),default=1)
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    manifest_rows=read_manifest(args.manifest)
    records=[(i,p.read_bytes()) for i,p in manifest_rows]
    banks,index,layout=pack_records(records,start_bank=args.start_bank,end_bank=args.end_bank,alignment=args.alignment)
    args.output_banks.write_bytes(banks)
    args.output_index.write_bytes(index)
    with args.output_layout.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["id","bank","address","bank_offset","size"]);w.writeheader();w.writerows(layout)
    report={"records":len(records),"index_entries":len(index)//3,"index_bytes":len(index),"packed_bytes":len(banks),"banks_emitted":len(banks)//BANK_SIZE,"first_bank":layout[0]["bank"] if layout else None,"last_bank":layout[-1]["bank"] if layout else None}
    print(json.dumps(report,indent=2,sort_keys=True) if args.json else report)
    return 0
if __name__=="__main__":
    raise SystemExit(main())
