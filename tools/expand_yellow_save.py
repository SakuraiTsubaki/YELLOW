#!/usr/bin/env python3
"""Create YELLOW's 128 KiB expanded SRAM image without rewriting legacy bytes.

Banks 0..3 (32 KiB) are the byte-exact legacy Yellow save.
Banks 4..14 (88 KiB) are persistent YELLOW extension storage.
Bank 15 (8 KiB) is reserved as volatile runtime-extension RAM; it is excluded
from persistent payload checksums and is reinitialized by the runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

SRAM_BANK_SIZE = 0x2000
LEGACY_SIZE = 0x8000
EXPANDED_SIZE = 0x20000
PERSISTENT_OFFSET = LEGACY_SIZE
RUNTIME_BANK = 15
RUNTIME_OFFSET = RUNTIME_BANK * SRAM_BANK_SIZE
PERSISTENT_END = RUNTIME_OFFSET
PERSISTENT_SIZE = PERSISTENT_END - PERSISTENT_OFFSET
RUNTIME_SIZE = EXPANDED_SIZE - RUNTIME_OFFSET
HEADER_SIZE = 0x40
MAGIC = b"YLX1"
SCHEMA_VERSION = 2

PROFILE_UNKNOWN = 0
PROFILE_JP = 1
PROFILE_INTL = 2

PROFILE_NAMES = {
    PROFILE_UNKNOWN: "unknown",
    PROFILE_JP: "yellow-jp-legacy",
    PROFILE_INTL: "yellow-intl-legacy",
}

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
    if len(payload) != PERSISTENT_SIZE - HEADER_SIZE:
        raise ValueError("invalid persistent extension payload length")

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
    if len(data) != EXPANDED_SIZE:
        raise ValueError("expanded save must be exactly 128 KiB")
    fields = HEADER_STRUCT.unpack(data[PERSISTENT_OFFSET:PERSISTENT_OFFSET + HEADER_SIZE])
    (
        magic, schema, header_size, profile, flags, reserved,
        payload_bytes, source_sha, payload_sum, header_sum, reserved_tail,
    ) = fields
    header = data[PERSISTENT_OFFSET:PERSISTENT_OFFSET + HEADER_SIZE]
    payload = data[PERSISTENT_OFFSET + HEADER_SIZE:PERSISTENT_END]
    return {
        "magic": magic.decode("ascii", errors="replace"),
        "schema_version": schema,
        "header_size": header_size,
        "source_profile_id": profile,
        "source_profile": PROFILE_NAMES.get(profile, "invalid"),
        "flags": flags,
        "reserved": reserved,
        "payload_bytes": payload_bytes,
        "payload_bytes_ok": payload_bytes == len(payload),
        "source_sha256": source_sha.hex(),
        "payload_sum16": payload_sum,
        "payload_sum16_ok": sum16(payload) == payload_sum,
        "header_sum16": header_sum,
        "header_sum16_ok": _header_sum(header) == header_sum,
        "reserved_tail_zero": reserved_tail == b"\x00" * 12,
        "runtime_bank_excluded_from_payload": True,
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
    payload = bytes([fill]) * (PERSISTENT_SIZE - HEADER_SIZE)
    runtime = bytes([fill]) * RUNTIME_SIZE
    header = build_header(
        source_profile=source_profile,
        source_sha256=source_sha,
        payload=payload,
    )
    expanded = legacy + header + payload + runtime
    assert len(expanded) == EXPANDED_SIZE

    report = parse_header(expanded)
    report.update({
        "legacy_bytes": LEGACY_SIZE,
        "expanded_bytes": EXPANDED_SIZE,
        "legacy_banks": LEGACY_SIZE // SRAM_BANK_SIZE,
        "expanded_banks": EXPANDED_SIZE // SRAM_BANK_SIZE,
        "persistent_extension_banks": PERSISTENT_SIZE // SRAM_BANK_SIZE,
        "runtime_banks": RUNTIME_SIZE // SRAM_BANK_SIZE,
        "runtime_bank": RUNTIME_BANK,
        "legacy_prefix_preserved": expanded[:LEGACY_SIZE] == legacy,
        "persistent_extension_offset": PERSISTENT_OFFSET,
        "runtime_offset": RUNTIME_OFFSET,
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
