#!/usr/bin/env python3
"""Prepare mapper-native expanded Pokémon Yellow ROM images.

This tool never commits ROMs. It consumes a local verified 1 MiB Yellow ROM,
preserves its mapper family, pads to that mapper's standard ROM ceiling, updates
the header ROM-size code, and recalculates both Game Boy checksums.

Stage 0 only creates capacity. New banks must not be populated until the bank
switching API and bank-ID storage have been audited/widened.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

BANK_SIZE = 0x4000
ONE_MIB = 1024 * 1024
ROM_SIZE_CODES = {
    2 * ONE_MIB: 0x06,
    4 * ONE_MIB: 0x07,
    8 * ONE_MIB: 0x08,
}

CART_MBC3_RAM_BATTERY = 0x13
CART_MBC5_RAM_BATTERY = 0x1B


def calc_header_checksum(data: bytes | bytearray) -> int:
    value = 0
    for byte in data[0x134:0x14D]:
        value = (value - byte - 1) & 0xFF
    return value


def calc_global_checksum(data: bytes | bytearray) -> int:
    return (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF


def checksums_ok(data: bytes | bytearray) -> bool:
    return (
        calc_header_checksum(data) == data[0x14D]
        and calc_global_checksum(data)
        == int.from_bytes(data[0x14E:0x150], "big")
    )


def mapper_native_target(cart_type: int) -> tuple[int, str]:
    if cart_type == CART_MBC3_RAM_BATTERY:
        return 2 * ONE_MIB, "mbc3-native-2m"
    if cart_type == CART_MBC5_RAM_BATTERY:
        return 8 * ONE_MIB, "mbc5-native-8m"
    raise ValueError(
        f"unsupported Yellow mapper/cart type: 0x{cart_type:02X}"
    )


def load_known_hashes(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            result[row["sha256"].lower()] = row["release_id"]
    return result


def expand_mapper_native(data: bytes, fill: int = 0xFF) -> tuple[bytes, dict]:
    if len(data) != ONE_MIB:
        raise ValueError(
            f"expected verified Yellow 1 MiB source, got {len(data)} bytes"
        )
    if not checksums_ok(data):
        raise ValueError("source ROM header/global checksum validation failed")

    cart_type = data[0x147]
    target_bytes, profile = mapper_native_target(cart_type)

    output = bytearray(data)
    output.extend(bytes([fill]) * (target_bytes - len(output)))

    output[0x148] = ROM_SIZE_CODES[target_bytes]
    output[0x14D] = calc_header_checksum(output)
    output[0x14E:0x150] = calc_global_checksum(output).to_bytes(2, "big")

    report = {
        "profile": profile,
        "source_bytes": len(data),
        "target_bytes": len(output),
        "source_banks": len(data) // BANK_SIZE,
        "target_banks": len(output) // BANK_SIZE,
        "new_banks": (len(output) - len(data)) // BANK_SIZE,
        "cartridge_type": f"0x{cart_type:02X}",
        "rom_size_code": f"0x{output[0x148]:02X}",
        "ram_size_code": f"0x{output[0x149]:02X}",
        "ram_size_unchanged": True,
        "bank_api_patch_required_before_using_all_new_banks": True,
        "header_checksum_ok": calc_header_checksum(output) == output[0x14D],
        "global_checksum_ok": (
            calc_global_checksum(output)
            == int.from_bytes(output[0x14E:0x150], "big")
        ),
    }
    return bytes(output), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_rom", type=Path)
    parser.add_argument("output_rom", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("manifests/rom-baselines.csv"),
    )
    parser.add_argument("--allow-unknown-source", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source = args.input_rom.read_bytes()
    source_sha256 = hashlib.sha256(source).hexdigest()
    known = load_known_hashes(args.manifest)
    release_id = known.get(source_sha256)

    if known and release_id is None and not args.allow_unknown_source:
        raise SystemExit(
            "input SHA-256 is not present in the verified Yellow ROM manifest"
        )

    expanded, report = expand_mapper_native(source)
    args.output_rom.write_bytes(expanded)

    report["source_sha256"] = source_sha256
    report["release_id"] = release_id
    report["output_sha256"] = hashlib.sha256(expanded).hexdigest()
    report["output"] = str(args.output_rom)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{release_id or 'unknown'}: {report['profile']} "
            f"{report['source_banks']} -> {report['target_banks']} banks"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
