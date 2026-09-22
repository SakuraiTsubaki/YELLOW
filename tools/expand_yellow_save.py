#!/usr/bin/env python3
"""Create YELLOW's 128 KiB expanded SRAM image without rewriting legacy bytes.

Banks 0..3 (first 32 KiB) are preserved byte-for-byte.
Banks 4..15 form a versioned 96 KiB extension region.

This tool deliberately does not interpret or "repair" the Japanese or
international legacy save. It only wraps verified/raw legacy bytes so the
runtime can migrate subsystems incrementally without destroying source data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

LEGACY_SIZE = 0x8000
EXPANDED_SIZE = 0x20000
SRAM_BANK_SIZE = 0x2000
EXT_OFFSET = LEGACY_SIZE
EXT_SIZE = EXPANDED_SIZE - LEGACY_SIZE
HEADER_SIZE = 0x40
MAGIC = b"YLX1"
SCHEMA_VERSION = 1

PROFILE_UNKNOWN = 0
PROFILE_JP = 1
PROFILE_INTL = 2

PROFILE_NAMES = {
    PROFILE_UNKNOWN: "unknown",
    PROFILE_JP: "yellow-jp-legacy",
    PROFILE_INTL: "yellow-intl-legacy",
}

# Header layout, all integers little-endian:
# 00  magic[4]             YLX1
# 04  schema_version u16
# 06  header_size u16
# 08  source_profile u8
# 09  flags u8
# 0A  reserved u16
# 0C  extension_bytes u32  bytes after this header
# 10  source_sha256[32]
# 30  payload_sum16 u16    additive checksum over extension payload
# 32  header_sum16 u16     additive checksum over header with this field zero
# 34  reserved[12]
HEADER_STRUCT = struct.Struct("<4sHHBBHI32sHH12s")
assert HEADER_STRUCT.size == HEADER_SIZE


def sum16(data: bytes | bytearray) -> int:
    return sum(data) & 0xFFFF


def _header_sum(raw_header: bytes) -> int:
    tmp = bytearray(raw_header)
    tmp[0x32:0x34] = b"\x00\x00"
    return sum16(tmp)


def build_header(
    *,
    source_profile: int,
    source_sha256: bytes,
    payload: bytes,
    flags: int = 0,
) -> bytes:
    if source_profile not in PROFILE_NAMES:
        raise ValueError("invalid source profile")
    if len(source_sha256) != 32:
        raise ValueError("source_sha256 must be 32 raw bytes")
    if len(payload) != EXT_SIZE - HEADER_SIZE:
        raise ValueError("invalid extension payload length")

    payload_sum = sum16(payload)
    raw = HEADER_STRUCT.pack(
        MAGIC,
        SCHEMA_VERSION,
        HEADER_SIZE,
        source_profile,
        flags & 0xFF,
        0,
        len(payload),
        source_sha256,
        payload_sum,
        0,
        b"\x00" * 12,
    )
    header_sum = _header_sum(raw)
    return HEADER_STRUCT.pack(
        MAGIC,
        SCHEMA_VERSION,
        HEADER_SIZE,
        source_profile,
        flags & 0xFF,
        0,
        len(payload),
        source_sha256,
        payload_sum,
        header_sum,
        b"\x00" * 12,
    )


def parse_header(data: bytes) -> dict:
    if len(data) < EXT_OFFSET + HEADER_SIZE:
        raise ValueError("expanded save is too small")
    fields = HEADER_STRUCT.unpack(data[EXT_OFFSET:EXT_OFFSET + HEADER_SIZE])
    (
        magic, schema, header_size, profile, flags, reserved,
        payload_bytes, source_sha, payload_sum, header_sum, reserved_tail,
    ) = fields
    header = data[EXT_OFFSET:EXT_OFFSET + HEADER_SIZE]
    payload = data[EXT_OFFSET + HEADER_SIZE:]
    return {
        "magic": magic.decode("ascii", errors="replace"),
        "schema_version": schema,
        "header_size": header_size,
        "source_profile_id": profile,
        "source_profile": PROFILE_NAMES.get(profile, "invalid"),
        "flags": flags,
        "reserved": reserved,
        "payload_bytes": payload_bytes,
        "source_sha256": source_sha.hex(),
        "payload_sum16": payload_sum,
        "payload_sum16_ok": sum16(payload) == payload_sum,
        "header_sum16": header_sum,
        "header_sum16_ok": _header_sum(header) == header_sum,
        "reserved_tail_zero": reserved_tail == b"\x00" * 12,
    }


def expand_save(
    legacy: bytes,
    *,
    source_profile: int,
    fill: int = 0xFF,
) -> tuple[bytes, dict]:
    if len(legacy) != LEGACY_SIZE:
        raise ValueError(
            f"expected raw 32 KiB Yellow SRAM, got {len(legacy)} bytes"
        )
    if not 0 <= fill <= 0xFF:
        raise ValueError("fill must fit in one byte")

    source_sha = hashlib.sha256(legacy).digest()
    payload = bytes([fill]) * (EXT_SIZE - HEADER_SIZE)
    header = build_header(
        source_profile=source_profile,
        source_sha256=source_sha,
        payload=payload,
    )
    expanded = legacy + header + payload
    assert len(expanded) == EXPANDED_SIZE

    report = parse_header(expanded)
    report.update({
        "legacy_bytes": LEGACY_SIZE,
        "expanded_bytes": EXPANDED_SIZE,
        "legacy_banks": LEGACY_SIZE // SRAM_BANK_SIZE,
        "expanded_banks": EXPANDED_SIZE // SRAM_BANK_SIZE,
        "extension_banks": EXT_SIZE // SRAM_BANK_SIZE,
        "legacy_prefix_preserved": expanded[:LEGACY_SIZE] == legacy,
        "extension_offset": EXT_OFFSET,
    })
    return expanded, report


def profile_from_arg(value: str) -> int:
    aliases = {
        "jp": PROFILE_JP,
        "yellow-jp-legacy": PROFILE_JP,
        "intl": PROFILE_INTL,
        "international": PROFILE_INTL,
        "yellow-intl-legacy": PROFILE_INTL,
        "unknown": PROFILE_UNKNOWN,
    }
    try:
        return aliases[value.lower()]
    except KeyError as exc:
        raise argparse.ArgumentTypeError(f"unknown profile: {value}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_save", type=Path)
    parser.add_argument("output_save", type=Path)
    parser.add_argument("--profile", required=True, type=profile_from_arg)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    legacy = args.input_save.read_bytes()
    expanded, report = expand_save(legacy, source_profile=args.profile)
    args.output_save.write_bytes(expanded)
    report["output"] = str(args.output_save)
    report["expanded_sha256"] = hashlib.sha256(expanded).hexdigest()

    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
