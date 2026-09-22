# YELLOW

**ポケットモンスター ピカチュウ / Pokémon Yellow 원본 Game Boy 엔진 자체를 확장하는 프로젝트**입니다.

## 현재 정본 방향

- 일본판 Rev 0A / B / C / D를 Master Reference로 유지합니다.
- EN / FR / DE / IT / ES는 각 지역판 ROM·세이브 차이를 독립 프로필로 보존합니다.
- 실행 대상은 **Game Boy / Super Game Boy / Game Boy Color 계열의 Yellow 런타임**입니다.
- **GBA 리메이크는 별도 작업**이며 이 저장소의 런타임 기준으로 사용하지 않습니다.
- ROM과 save는 별도 증거 계층으로 관리합니다.
- 미출시 세대의 종수·기술수·아이템수는 추측하지 않습니다.

## 10세대 대비 확장 축

원본 1 MiB Yellow ROM을 그대로 증거로 보존하면서, 확장 빌드는 표준 MBC5 범위 안에서 다음 계약을 사용합니다.

- 최대 ROM: 8 MiB / 512 × 16 KiB banks
- 최대 SRAM: 128 KiB / 16 × 8 KiB banks
- ROM bank ID: 9-bit
- 확장 gameplay ID: 16-bit logical IDs
- 데이터 테이블: 실제 수량 기반, 65,535개 고정 배열 금지
- legacy save: JP/국제판을 각각 별도 호환·마이그레이션 프로필로 유지

일본판 원본은 MBC3+RAM+BATTERY, 해외판은 MBC5+RAM+BATTERY다. 확장 MBC5 프로필은 원본 ROM을 덮어쓰는 정본이 아니라 **별도의 파생 런타임 프로필**이다.

## 근거

- ROM/save 기준선: `manifests/rom-baselines.csv`, `manifests/legacy-save-profiles.json`
- 실제 ROM/save 조사: `research/rom-save-evidence.md`
- 하드웨어 확장 계약: `manifests/hardware-capacity.yml`
- 구현 구조: `docs/EXPANSION_ARCHITECTURE.md`

ROM 바이너리는 GitHub에 커밋하지 않습니다.
