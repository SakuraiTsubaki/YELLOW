#!/usr/bin/env python3
"""YELLOW v1 persistent Pokémon extension-record helper."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

EXPANDED_SAVE_SIZE = 0x20000
TABLE_OFFSET = 0x8040
RECORD_SIZE = 16
PARTY_SLOTS = 6
DAYCARE_SLOTS = 1
PC_SLOTS = 240
TOTAL_SLOTS = PARTY_SLOTS + DAYCARE_SLOTS + PC_SLOTS
TABLE_SIZE = RECORD_SIZE * TOTAL_SLOTS
TABLE_END = TABLE_OFFSET + TABLE_SIZE

FLAG_NATURE_VALID = 1 << 0
FLAG_HELD_ITEM_VALID = 1 << 1
FLAG_ABILITY_VALID = 1 << 2
FLAG_FORM_VALID = 1 << 3

RECORD = struct.Struct("<B4BHHHBB3s")
assert RECORD.size == RECORD_SIZE
assert TABLE_SIZE == 3952
assert TABLE_END == 0x8FB0


def canonical_party_slot(index: int) -> int:
    if not 0 <= index < PARTY_SLOTS:
        raise ValueError("party index out of range")
    return index


def canonical_daycare_slot() -> int:
    return PARTY_SLOTS


def canonical_pc_slot(box: int, position: int, *, profile: str) -> int:
    if profile == "yellow-jp-legacy":
        boxes, per_box = 8, 30
    elif profile == "yellow-intl-legacy":
        boxes, per_box = 12, 20
    else:
        raise ValueError("unknown legacy profile")
    if not 0 <= box < boxes:
        raise ValueError("box out of range")
    if not 0 <= position < per_box:
        raise ValueError("box position out of range")
    linear = box * per_box + position
    return PARTY_SLOTS + DAYCARE_SLOTS + linear


def record_offset(slot: int) -> int:
    if not 0 <= slot < TOTAL_SLOTS:
        raise ValueError("canonical slot out of range")
    return TABLE_OFFSET + slot * RECORD_SIZE


def empty_record() -> bytes:
    return RECORD.pack(
        0,
        0, 0, 0, 0,
        0,
        0,
        0,
        0,
        0,
        b"\x00\x00\x00",
    )


def initialize_table(save: bytes) -> bytes:
    if len(save) != EXPANDED_SAVE_SIZE:
        raise ValueError("expected 128 KiB expanded save")
    out = bytearray(save)
    out[TABLE_OFFSET:TABLE_END] = empty_record() * TOTAL_SLOTS
    return bytes(out)


def decode_record(raw: bytes) -> dict:
    if len(raw) != RECORD_SIZE:
        raise ValueError("record must be 16 bytes")
    (
        species_high,
        move1_high, move2_high, move3_high, move4_high,
        held_item, ability, form, nature, flags, reserved,
    ) = RECORD.unpack(raw)
    return {
        "species_high": species_high,
        "move_high": [move1_high, move2_high, move3_high, move4_high],
        "held_item": held_item,
        "ability": ability,
        "form": form,
        "nature": nature,
        "flags": flags,
        "reserved": reserved.hex(),
    }


def combine_species(low: int, high: int) -> int:
    if not 0 <= low <= 0xFF or not 0 <= high <= 0xFF:
        raise ValueError("species bytes out of range")
    return low | (high << 8)


def combine_move(low: int, high: int) -> int:
    if not 0 <= low <= 0xFF or not 0 <= high <= 0xFF:
        raise ValueError("move bytes out of range")
    return low | (high << 8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("expanded_save", type=Path)
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--slot", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = args.expanded_save.read_bytes()
    if args.initialize:
        data = initialize_table(data)
        output = args.output or args.expanded_save
        output.write_bytes(data)

    report = {
        "table_offset": TABLE_OFFSET,
        "table_end": TABLE_END,
        "record_size": RECORD_SIZE,
        "total_slots": TOTAL_SLOTS,
        "table_size": TABLE_SIZE,
    }
    if args.slot is not None:
        off = record_offset(args.slot)
        report["slot"] = args.slot
        report["record_offset"] = off
        report["record"] = decode_record(data[off:off + RECORD_SIZE])

    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
