#!/usr/bin/env python3
"""Audit Pokémon Yellow/Pocket Monsters Pikachu ROM and save evidence."""

from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROM_SIZE = 1024 * 1024
SRAM_SIZE = 32 * 1024
BANK_SIZE = 0x2000
CHECKSUM_ROUTINE = bytes.fromhex("16 00 2A 82 57 0B 78 B1 20 F8 7A 2F C9")
CART_TYPES = {0x13: "MBC3+RAM+BATTERY", 0x1B: "MBC5+RAM+BATTERY"}
RAM_SIZES = {0x00:0,0x01:2*1024,0x02:8*1024,0x03:32*1024,0x04:128*1024,0x05:64*1024}

@dataclass(frozen=True)
class LegacySaveProfile:
    id: str
    main_start_cpu: int
    main_length: int
    main_checksum_cpu: int
    player_name_length: int
    main_data_length: int
    sprite_data_length: int
    party_data_length: int
    current_box_length: int
    boxes_per_bank: int
    total_boxes: int
    mons_per_box: int
    box_checksum_cpu: int
    box_checksum_span_literal: int
    individual_box_checksums: int

JP = LegacySaveProfile("yellow-jp-legacy",0xA598,0x0FFC,0xB594,6,0x0737,0x0200,0x0158,0x0566,4,8,30,0xB598,0x1599,0)
INTL = LegacySaveProfile("yellow-intl-legacy",0xA598,0x0F8B,0xB523,11,0x0789,0x0200,0x0194,0x0462,6,12,20,0xBA4C,0x1A4C,6)
PROFILES = (JP, INTL)

def checksum8(data: bytes) -> int:
    return (~(sum(data) & 0xFF)) & 0xFF

def sram_file_offset(bank: int, cpu_addr: int) -> int:
    if not 0xA000 <= cpu_addr <= 0xBFFF:
        raise ValueError(f"not an SRAM CPU address: {cpu_addr:#06x}")
    return bank * BANK_SIZE + (cpu_addr - 0xA000)

def header_checksum_ok(data: bytes) -> bool:
    x=0
    for v in data[0x134:0x14D]:
        x=(x-v-1)&0xFF
    return x == data[0x14D]

def global_checksum_ok(data: bytes) -> bool:
    calc=(sum(data[:0x14E])+sum(data[0x150:]))&0xFFFF
    return calc == int.from_bytes(data[0x14E:0x150],"big")

def find_all(data: bytes, pattern: bytes) -> list[int]:
    out=[]; start=0
    while True:
        pos=data.find(pattern,start)
        if pos<0: return out
        out.append(pos); start=pos+1

def _has_main_checksum_pattern(data: bytes, p: LegacySaveProfile) -> bool:
    prefix=bytes((0x21,p.main_start_cpu&0xFF,p.main_start_cpu>>8,0x01,p.main_length&0xFF,p.main_length>>8,0xCD))
    addr=bytes((p.main_checksum_cpu&0xFF,p.main_checksum_cpu>>8))
    return any(addr in data[pos:pos+24] for pos in find_all(data,prefix))

def detect_rom_profile(data: bytes) -> LegacySaveProfile | None:
    m=[p for p in PROFILES if _has_main_checksum_pattern(data,p)]
    return m[0] if len(m)==1 else None

def audit_rom(path: Path) -> dict:
    data=path.read_bytes()
    if len(data)!=ROM_SIZE:
        raise ValueError(f"{path}: expected 1 MiB Yellow ROM, got {len(data)} bytes")
    p=detect_rom_profile(data); cart=data[0x147]; ram=data[0x149]
    return {
        "kind":"rom","path":str(path),"size":len(data),
        "sha1":hashlib.sha1(data).hexdigest(),"sha256":hashlib.sha256(data).hexdigest(),
        "title_raw_hex":data[0x134:0x144].hex(),"cgb_flag":data[0x143],"sgb_flag":data[0x146],
        "cartridge_type":cart,"cartridge_type_name":CART_TYPES.get(cart,"unknown"),
        "ram_size_code":ram,"ram_bytes":RAM_SIZES.get(ram),"destination_code":data[0x14A],
        "header_version":data[0x14C],"header_checksum_ok":header_checksum_ok(data),
        "global_checksum_ok":global_checksum_ok(data),"checksum_routine_offsets":find_all(data,CHECKSUM_ROUTINE),
        "legacy_save_profile":p.id if p else None,
    }

def candidate_sram_images(raw: bytes) -> Iterable[tuple[str,int,bytes]]:
    if len(raw)==SRAM_SIZE:
        yield ("exact",0,raw); return
    if len(raw)>=SRAM_SIZE:
        yield ("prefix",0,raw[:SRAM_SIZE])
        off=len(raw)-SRAM_SIZE
        if off: yield ("suffix",off,raw[off:])

def _main_check(image: bytes, p: LegacySaveProfile) -> dict:
    start=sram_file_offset(1,p.main_start_cpu); chk=sram_file_offset(1,p.main_checksum_cpu)
    calc=checksum8(image[start:start+p.main_length]); stored=image[chk]
    return {"calculated":calc,"stored":stored,"ok":calc==stored,"data_offset":start,"checksum_offset":chk}

def _intl_box_checks(image: bytes, p: LegacySaveProfile) -> list[dict]:
    out=[]
    for bank in (2,3):
        base=bank*BANK_SIZE; chk=sram_file_offset(bank,p.box_checksum_cpu)
        calc=checksum8(image[base:base+p.box_checksum_span_literal])
        row={"bank":bank,"aggregate_calculated":calc,"aggregate_stored":image[chk],"aggregate_ok":calc==image[chk],"individual":[]}
        for i in range(p.boxes_per_bank):
            s=base+i*p.current_box_length; c=checksum8(image[s:s+p.current_box_length]); st=image[chk+1+i]
            row["individual"].append({"box_in_bank":i,"calculated":c,"stored":st,"ok":c==st})
        out.append(row)
    return out

def _jp_box_observations(image: bytes, p: LegacySaveProfile) -> list[dict]:
    out=[]; data_only=p.current_box_length*p.boxes_per_bank
    for bank in (2,3):
        base=bank*BANK_SIZE; chk=sram_file_offset(bank,p.box_checksum_cpu)
        out.append({
            "bank":bank,"stored":image[chk],"data_only_span":data_only,
            "data_only_calculated":checksum8(image[base:base+data_only]),
            "rom_literal_span":p.box_checksum_span_literal,
            "rom_literal_calculated":checksum8(image[base:base+p.box_checksum_span_literal]),
            "status":"observation_only_until_real_save_validation",
        })
    return out

def audit_save(path: Path) -> dict:
    raw=path.read_bytes(); candidates=[]
    for position,offset,image in candidate_sram_images(raw):
        for p in PROFILES:
            main=_main_check(image,p)
            candidates.append({
                "position":position,"wrapper_offset":offset,"profile":p.id,"main":main,
                "boxes":_intl_box_checks(image,p) if p is INTL else _jp_box_observations(image,p),
            })
    candidates.sort(key=lambda x: bool(x["main"]["ok"]),reverse=True)
    return {
        "kind":"save","path":str(path),"size":len(raw),
        "sha1":hashlib.sha1(raw).hexdigest(),"sha256":hashlib.sha256(raw).hexdigest(),
        "candidates":candidates,
        "best_profile":candidates[0]["profile"] if candidates and candidates[0]["main"]["ok"] else None,
    }

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("inputs",nargs="+",type=Path); ap.add_argument("--json",action="store_true")
    args=ap.parse_args(); results=[]
    for path in args.inputs:
        results.append(audit_rom(path) if path.suffix.lower() in {".gb",".gbc"} else audit_save(path))
    print(json.dumps(results,ensure_ascii=False,indent=2) if args.json else "\n".join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in results))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
