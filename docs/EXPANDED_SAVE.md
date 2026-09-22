# YELLOW expanded SRAM

YELLOW's 10세대 대비 save expansion keeps the original 32 KiB Yellow SRAM intact and appends a versioned extension instead of rewriting the legacy save in place.

## Physical layout

MBC5 can address 16 external-RAM banks of 8 KiB each. The expanded profile therefore uses 128 KiB total SRAM.

| SRAM banks | Bytes | Role |
|---|---:|---|
| 0..3 | 32 KiB | original JP or international Yellow save, byte-exact |
| 4..15 | 96 KiB | YELLOW extension region |

The first extension byte is offset `0x8000`, which is bank 4.

## Why the legacy prefix stays untouched

Japanese and international Yellow have incompatible save structures. Keeping banks 0..3 byte-exact means:

- each source-family decoder can keep using its proven legacy layout;
- migration can be retried from source bytes;
- unknown or not-yet-decoded legacy fields are not destroyed;
- expanded data can be added subsystem-by-subsystem.

## Extension header v1

Bank 4 begins with a 64-byte header tagged `YLX1`. It records schema version, source legacy profile, source-save SHA-256, payload length and checksums.

The remaining bytes of banks 4..15 are initially `0xFF` and become a directory-backed extension area in later stages.

## Runtime boundary

The file-format/tooling layer is implemented now. Runtime activation remains gated on three engine changes:

1. migrate the JP runtime from MBC3 to the common MBC5 expansion profile;
2. add 4-bit MBC5 SRAM-bank switching and preserve/restore the active SRAM bank;
3. patch save/load/checksum paths so banks 4..15 are recognized.

Until those are integrated, the ROM header RAM-size code remains the legacy 32 KiB value.
