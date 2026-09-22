#ifndef GUARD_YELLOW_EXPANSION_H
#define GUARD_YELLOW_EXPANSION_H

#include <stdint.h>

/*
 * YELLOW original-Game-Boy expansion contract.
 * This describes logical widths used by tooling/generated data. The runtime
 * implementation remains the GB/SGB/GBC Yellow engine; GBA is out of scope.
 */

typedef uint16_t YellowSpeciesId;
typedef uint16_t YellowFormId;
typedef uint16_t YellowMoveId;
typedef uint16_t YellowItemId;
typedef uint16_t YellowAbilityId;
typedef uint16_t YellowTypeId;
typedef uint16_t YellowLocationId;
typedef uint16_t YellowMapId;
typedef uint16_t YellowSaveSchemaVersion;
typedef uint16_t YellowRomBankId;

enum
{
    YELLOW_ID_NONE = 0x0000,
    YELLOW_ID_INVALID = 0xFFFF,
    YELLOW_ID_MAX_VALID = 0xFFFE,
};

enum YellowGeneration
{
    YELLOW_GEN_NONE = 0,
    YELLOW_GEN_I = 1,
    YELLOW_GEN_II = 2,
    YELLOW_GEN_III = 3,
    YELLOW_GEN_IV = 4,
    YELLOW_GEN_V = 5,
    YELLOW_GEN_VI = 6,
    YELLOW_GEN_VII = 7,
    YELLOW_GEN_VIII = 8,
    YELLOW_GEN_IX = 9,
    YELLOW_GEN_X = 10,
};

#define YELLOW_ROM_BANK_SIZE       0x4000u
#define YELLOW_MBC5_ROM_BANKS      512u
#define YELLOW_MBC5_ROM_BANK_BITS  9u
#define YELLOW_MBC5_ROM_MAX_BYTES  0x800000u
#define YELLOW_SRAM_BANK_SIZE      0x2000u
#define YELLOW_MBC5_SRAM_BANKS     16u
#define YELLOW_MBC5_SRAM_MAX_BYTES 0x20000u

#define YELLOW_SAVE_SCHEMA_V1 1
#define YELLOW_SAVE_SCHEMA_CURRENT YELLOW_SAVE_SCHEMA_V1

typedef char YellowSpeciesIdMustBe16Bit[(sizeof(YellowSpeciesId) == 2) ? 1 : -1];
typedef char YellowMoveIdMustBe16Bit[(sizeof(YellowMoveId) == 2) ? 1 : -1];
typedef char YellowItemIdMustBe16Bit[(sizeof(YellowItemId) == 2) ? 1 : -1];
typedef char YellowRomBankMustHold9Bits[(sizeof(YellowRomBankId) >= 2) ? 1 : -1];

#endif
