#ifndef GUARD_YELLOW_EXPANSION_H
#define GUARD_YELLOW_EXPANSION_H

#include <stdint.h>

/*
 * YELLOW expansion contract
 *
 * IDs are intentionally wider than the original Gen III storage assumptions.
 * Actual table sizes remain build-time/data-driven; these are representation
 * limits, not requests to allocate arrays of 65,535 entries.
 */

typedef uint16_t YellowSpeciesId;
typedef uint16_t YellowFormId;
typedef uint16_t YellowMoveId;
typedef uint16_t YellowItemId;
typedef uint16_t YellowAbilityId;
typedef uint16_t YellowTypeId;
typedef uint16_t YellowLocationId;
typedef uint16_t YellowTrainerClassId;
typedef uint16_t YellowMapId;
typedef uint16_t YellowSaveSchemaVersion;

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

    /*
     * Reserved boundary for future content. Do not assign species/move/item
     * counts here until they are independently verified.
     */
    YELLOW_GEN_X = 10,
};

#define YELLOW_GENERATION_STORAGE_BITS 8
#define YELLOW_GENERATION_MAX 255

#define YELLOW_SAVE_SCHEMA_V1 1
#define YELLOW_SAVE_SCHEMA_CURRENT YELLOW_SAVE_SCHEMA_V1

/*
 * Capability words allow mechanics to be composed without making generation
 * number itself control behavior. Future mechanics add bits instead of
 * rewriting the core species/save model.
 */
enum YellowCapabilityBit
{
    YELLOW_CAP_ABILITIES = 0,
    YELLOW_CAP_NATURES,
    YELLOW_CAP_HELD_ITEMS,
    YELLOW_CAP_DOUBLE_BATTLES,
    YELLOW_CAP_PHYSICAL_SPECIAL_SPLIT,
    YELLOW_CAP_FAIRY_TYPE,
    YELLOW_CAP_REGIONAL_FORMS,
    YELLOW_CAP_BATTLE_FORMS,
    YELLOW_CAP_MEGA_EVOLUTION,
    YELLOW_CAP_Z_MOVES,
    YELLOW_CAP_DYNAMAX,
    YELLOW_CAP_TERASTALLIZATION,
    YELLOW_CAP_FUTURE_MECHANIC_0 = 24,
    YELLOW_CAP_FUTURE_MECHANIC_1,
    YELLOW_CAP_FUTURE_MECHANIC_2,
    YELLOW_CAP_FUTURE_MECHANIC_3,
};

typedef uint32_t YellowCapabilityWord;

#define YELLOW_CAP(bit) ((YellowCapabilityWord)1u << (bit))

/*
 * Compile-time invariants. These must remain true even when content tables grow.
 */
typedef char YellowSpeciesIdMustBe16Bit[(sizeof(YellowSpeciesId) == 2) ? 1 : -1];
typedef char YellowMoveIdMustBe16Bit[(sizeof(YellowMoveId) == 2) ? 1 : -1];
typedef char YellowItemIdMustBe16Bit[(sizeof(YellowItemId) == 2) ? 1 : -1];
typedef char YellowAbilityIdMustBe16Bit[(sizeof(YellowAbilityId) == 2) ? 1 : -1];
typedef char YellowSaveSchemaMustBe16Bit[(sizeof(YellowSaveSchemaVersion) == 2) ? 1 : -1];

#endif /* GUARD_YELLOW_EXPANSION_H */
