# Banked record packing

The 8 MiB MBC5 target is only useful if new data can actually be placed above the original 1 MiB ROM.

`tools/pack_banked_records.py` packs binary records into ROMX banks and emits the matching 16-bit logical-ID index.

By default packing starts at bank 64, immediately after the original 1 MiB Yellow image. Records never straddle a bank. If one does not fit in the remaining bytes, it starts at `$4000` in the next bank.

The packer is tested across the MBC5 boundary from bank 255 to bank 256, so the ninth bank bit is not silently dropped.

Outputs are build artifacts only. ROM binaries remain outside GitHub.
