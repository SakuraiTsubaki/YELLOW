# Runtime 16-bit ID migration

The persistent Pokémon sidecar solves storage, but it does not make the running Gen I engine 16-bit-safe by itself.

## Confirmed byte chokepoints

The structural Yellow source model uses one-byte IDs in all of these live paths:

- Pokémon box/party/battle species;
- four move IDs in box/party/battle records;
- current species and current party species;
- current item;
- current/selected player/selected enemy move;
- captured species;
- player/rival starter;
- fossil result species;
- the combined enemy-species/trainer-class selector.

The combined enemy/trainer byte is especially important: widening it as-is would preserve a Gen I namespace collision. YELLOW instead splits it into separate logical species and trainer-class IDs.

## Migration rule

Do not change the size of stock WRAM structs globally in one step. Many routines use hard-coded offsets and copy lengths.

Migration is staged:

1. add a dedicated expansion WRAM block containing paired low/high bytes;
2. wrap boundaries that load from persistent sidecars or expanded ROM tables;
3. migrate core species lookup and move lookup routines to consume BC;
4. migrate battle working structs;
5. migrate trainer/wild/script formats;
6. only then allow IDs above 255 in generated content.

Legacy code paths are allowed only when the high byte is zero.

## Pokedex

The original seen/owned bitsets are tied to the Gen I species count. They remain as the legacy compatibility view. Expanded seen/owned bitsets live in the extension SRAM and are paged/loaded as needed.

## Link and trade

The serial protocol is a separate compatibility surface. Extended IDs are not sent to a legacy peer. Version negotiation and an extended party packet are required before multiplayer can carry IDs above 255.
