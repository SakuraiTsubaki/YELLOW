# YELLOW Project

## Canonical direction

ポケットモンスター ピカチュウ / Pokémon Yellow의 **원본 Game Boy 런타임을 직접 확장**한다.

GBA/Generation III 리메이크는 별도 프로젝트다. 이 저장소에서는 pokeemerald, GBA 32 MiB ROM, Generation III save 구조를 YELLOW의 런타임 기준으로 사용하지 않는다.

## Master Reference

일본판 원본 ROM 네 revision을 모두 독립적으로 보존하고 조사한다.

- Rev 0A
- Rev B
- Rev C
- Rev D

지역판 EN / FR / DE / IT / ES도 각 ROM hash와 save profile을 별도로 유지한다.

## Runtime profiles

### Legacy exact profiles

- JP: 1 MiB ROM, MBC3+RAM+BATTERY, 32 KiB SRAM
- International: 1 MiB ROM, MBC5+RAM+BATTERY, 32 KiB SRAM

### Expanded profile

10세대 이후 검증 데이터까지 수용할 수 있도록 파생 빌드는 MBC5를 공통 확장 mapper로 사용한다.

- 8 MiB ROM ceiling
- 512 ROM banks
- 128 KiB SRAM ceiling
- 16 SRAM banks
- 9-bit ROM bank selectors
- 16-bit logical gameplay IDs
- banked tables / bank+address pointers

단순히 ROM header의 mapper 값을 바꾸는 것으로 끝내지 않는다. 256번 bank 이상을 사용하려면 MBC5의 high ROM-bank bit를 실제 bank-switch API에 통합해야 한다.

## Save rule

JP와 국제판의 기존 32 KiB save는 서로 호환되지 않는 legacy profile이다. 원형 save를 억지로 공통 구조로 덮어쓰지 않고, 확장 save에는 명시적 schema version과 migration을 둔다.

## Scope boundary

- 원본 GB/SGB/GBC 런타임 확장: 이 저장소
- GBA 리메이크: 별도 작업
- ROM 바이너리: 커밋 금지
