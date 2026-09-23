# 16-bit banked record indexes

Original Yellow commonly turns a one-byte ID directly into an offset within one table. That fails twice for later-generation data: the ID exceeds 255 and the table can exceed one ROM bank.

YELLOW replaces that assumption with a generated index.

Each logical ID maps to one three-byte `farptr9` entry:

- 9-bit MBC5 ROM bank;
- 14-bit address offset inside `$4000..$7fff`;
- one reserved bit.

Missing logical IDs contain `FF FF FF`.

## Why this works for the 10-generation target

A 16 KiB ROM bank can hold 5,461 three-byte index entries. Species, move, item, ability and form catalogs can therefore use full 16-bit logical IDs without forcing their actual records into a single bank.

The ID space remains 16-bit even though the generated index only contains the verified active range. If an index eventually exceeds 5,461 entries, only the index reader needs paging; saved IDs and table records do not need renumbering.

## First migration target: species

The stock `GetMonHeader` path multiplies an 8-bit species-derived Pokédex number by `BASE_DATA_SIZE` inside one `BaseStats` table.

The replacement path is:

1. load the 16-bit logical species ID;
2. resolve it through `YellowSpeciesIndex16`;
3. switch to the record's 9-bit MBC5 bank;
4. copy the record into the working mon header;
5. retain a legacy low-ID compatibility path only for source-version reproduction.

Names, sprites, cries and learnsets use the same index pattern rather than assuming all species tables share one order or bank.
