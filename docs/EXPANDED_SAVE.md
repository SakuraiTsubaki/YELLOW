# YELLOW expanded SRAM

The expanded MBC5 profile uses the full 128 KiB SRAM address space without forcing new runtime state into Yellow's already-full WRAM0/HRAM.

| SRAM banks | Size | Role |
|---|---:|---|
| 0..3 | 32 KiB | byte-exact legacy JP/international save |
| 4..14 | 88 KiB | persistent YELLOW extension |
| 15 | 8 KiB | volatile runtime extension/service RAM |

Bank 4 starts with the versioned `YLX1` header. Schema v2 stops the persistent payload checksum at file offset `0x1E000`, the start of bank 15.

## Why bank 15 is volatile

The structural Yellow reference has no free WRAM0 or HRAM, and the verified source ROMs do not share a safe ROM0 cavity. MBC5 nevertheless exposes sixteen external-RAM banks. YELLOW therefore reserves the final bank as runtime memory.

The runtime can copy a small service image from new ROM bank `0x40` into SRAM bank 15 and execute it from the mapped `$A000-$BFFF` cartridge-RAM window. That service can change ROMB0/ROMB1 while its own instructions remain available, then restore the legacy low ROM bank before returning.

Persistent save data never depends on the contents of bank 15. It is reinitialized by the expanded runtime.

## Persistent compatibility

The first 32 KiB remains byte-exact, so the JP 8x30 and international 12x20 legacy layouts stay independently decodable. Persistent extension records, including the 247-slot Pokémon sidecar, remain in bank 4 and are unaffected by reserving bank 15.
