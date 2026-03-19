# 명명 규칙 가이드 (Naming Conventions)

> 이 파일은 프로젝트 전반의 일반 명명 규칙을 정의한다.
> 프로젝트 특화 규칙 (도메인 컬럼명, 파일 포맷 패턴)은 프로젝트 CLAUDE.md에 별도 정의.
> 관련: [.claude/skills/reference/python/SKILL.md](../skills/reference/python/SKILL.md) § 네이밍 규칙

---

## Python 코드 명명

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수/함수 | `snake_case` (동사_명사) | `zone_id`, `load_demand_data()` |
| 클래스 | `PascalCase` | `DataProcessor`, `DemandAgent` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_RETRY`, `DEFAULT_TIMEOUT` |
| 비공개 | `_` 접두사 | `_validate_files()` |
| 매직 메서드 | `__name__` | `__init__`, `__repr__` |

**함수명 패턴:**

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `load_` | 데이터 로딩 | `load_csv_data()` |
| `get_` | 단순 반환 | `get_zone_id()` |
| `process_` | 변환/처리 | `process_demand()` |
| `validate_` | 검증 | `validate_zone_id()` |
| `create_` | 객체 생성 | `create_agent()` |
| `save_` | 저장 | `save_to_parquet()` |

---

## 파일 시스템 명명

| 대상 | 규칙 | 예시 |
|------|------|------|
| Python 모듈/파일 | `snake_case` | `demand_analysis.py`, `data_loader.py` |
| Python 디렉터리/패키지 | `snake_case` (단수형) | `libs/data/`, `agents/demand_analyst/` |
| 문서 파일 (.md) | `kebab-case` | `api-guide.md`, `setup-guide.md` |
| Git 브랜치 | `kebab-case` | `feat/issue-74-pr-rules` |
| Skill 이름 | `kebab-case` | `convention-python`, `check-anti-patterns` |
| YAML/JSON 설정 | `snake_case` | `zone_config.yaml` |

**원칙:**
- `snake_case` = Python namespace (import 가능해야 함)
- `kebab-case` = 파일시스템/URL/CLI 단위 (import 불가)
- 하이픈(`-`) 포함 디렉터리는 Python import 불가 → 패키지 디렉터리는 반드시 `snake_case`

---

## 구성 키 (Config Keys)

| 도구 | 규칙 | 예시 |
|------|------|------|
| OmegaConf/YAML | `snake_case` | `zone_id: 40`, `max_retries: 3` |
| 환경 변수 | `UPPER_SNAKE_CASE` | `API_KEY`, `DATABASE_URL` |
| JSON 키 | `snake_case` | `"zone_id": 40` |

---

## Git 관련

| 대상 | 규칙 | 예시 |
|------|------|------|
| 브랜치명 | `{type}/issue-{number}-{subject}` | `feat/issue-74-ai-pr-rules` |
| Commit 타입 | `feat/fix/docs/refactor/test/chore` | `feat(demand): add zone tool` |
| Commit 스코프 | 필수, 영역 표기 | `feat(adk): add agent` |

---

## Gotchas (실패 포인트)

- **Python 디렉터리에 하이픈 사용**: `grid-population/` → import 불가. `grid_population/` 사용
- **YAML 키에 하이픈**: `grid-population:` → OmegaConf에서 attribute access 불가. `grid_population:` 사용
- **상수를 변수명으로**: `max_retry = 3` → `MAX_RETRY = 3`으로 정의해야 IDE가 상수로 인식
- **클래스를 snake_case로**: `data_processor` → `DataProcessor`로 정의
- **영어/한국어 혼용**: 변수명은 영어만, 주석/docstring은 한국어

---

## 참조

- [skills/reference/python/SKILL.md](../skills/reference/python/SKILL.md) § 네이밍 규칙
- [team-operations.md](./team-operations.md) § 명명 규칙 요약표
- [CLAUDE.md](../../CLAUDE.md) § 언어 규칙
