# Yellow ROM / save evidence baseline

## Scope

This baseline was created from the actual Yellow/Pikachu ROM inputs available to the project workspace and cross-checked against the current `pret/pokeyellow` save source. ROM bytes are not committed.

Nine unique ROM binaries are present across fourteen filenames: four Japanese revisions and five localized international builds. Duplicate `.gb` / `.gbc` names with the same SHA-256 are aliases, not additional releases.

## Cartridge / SRAM evidence

All nine unique ROMs declare 32 KiB external RAM (`RAM size code 0x03`).

- Japanese Rev 0A/B/C/D: cartridge type `0x13`, MBC3+RAM+BATTERY, destination 0, CGB flag `0x00`.
- EN/FR/DE/IT/ES: cartridge type `0x1B`, MBC5+RAM+BATTERY, destination 1, CGB flag `0x80`.

The mapper differs, but the legacy save SRAM capacity is 32 KiB in both families.

## Checksum routine confirmed in ROM bytes

Every unique ROM contains the same 13-byte checksum core:

`16 00 2A 82 57 0B 78 B1 20 F8 7A 2F C9`

Semantically it sums the requested byte range modulo 256 and returns the one's complement of the sum.

The routine occurs at different ROM addresses by release, so YELLOW keys evidence by ROM hash/revision rather than one hard-coded ROM address.

## Japanese legacy save profile

Japanese Rev 0A/B/C/D directly show:

- main SRAM start `A598`, bank 1;
- main checksum range `0x0FFC`;
- main checksum byte `B594`;
- player-name length 6;
- main-data length `0x0737`;
- sprite-data length `0x0200`;
- party-data length `0x0158`;
- current-box length `0x0566`.

The box pointer table is `A000, A566, AACC, B032`, proving four `0x0566` boxes per SRAM bank. This yields 8 boxes × 30 Pokémon = 240 PC slots.

The ROM stores an aggregate box checksum at `B598` and literally loads a `0x1599` checksum span. Four boxes occupy `0x1598`, so exact semantics will not be guessed: a real Japanese save is required before the migrator freezes this rule.

## International legacy save profile

EN/FR/DE/IT/ES directly show:

- main SRAM start `A598`, bank 1;
- main checksum range `0x0F8B`;
- main checksum byte `B523`;
- player-name length 11;
- main-data length `0x0789`;
- sprite-data length `0x0200`;
- party-data length `0x0194`;
- current-box length `0x0462`.

The international family uses 6 boxes per SRAM bank, 12 total, 20 Pokémon each = 240 PC slots.

The aggregate box checksum is stored at `BA4C` over `0x1A4C` data bytes, followed by six individual box checksums. This agrees with the current `pret/pokeyellow` save source.

## Expansion consequence

There is no single "Yellow Gen-I save format" that can safely be widened in place. Japanese and international releases differ in field lengths, box counts, box capacities, mapper family, main-data length and box-checksum layout.

YELLOW therefore keeps two separate legacy profiles:

1. `yellow-jp-legacy`
2. `yellow-intl-legacy`

The **original Game Boy expanded runtime** gets a separate versioned save schema. The planned MBC5 expansion profile allows up to 128 KiB SRAM; migration metadata preserves the source profile and source-file hash. This is independent of any GBA remake work.

## Current save-file evidence status

No Yellow `.sav` file is mounted in the current runtime. ROM-derived structure is committed now, but byte-level validation against the user's actual Yellow saves remains intentionally incomplete.

`tools/yellow_rom_save_audit.py` accepts raw 32 KiB saves and larger wrapped emulator saves. For wrapped files it tests both prefix- and suffix-aligned 32 KiB SRAM candidates instead of assuming where emulator metadata lives.
