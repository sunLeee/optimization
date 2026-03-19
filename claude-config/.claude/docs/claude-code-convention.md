# Claude Code 대형 프로젝트 관리 Best Practices

> 조사 방법: claude + codex + gemini 3-agent 병렬 조사 (omc-teams)
> 작성일: 2026-03-18
> 항목 수: 28개 (8개 카테고리)

---

## 1. CLAUDE.md 구조 설계

**Practice 1: Nested CLAUDE.md 계층 구조**

루트 `CLAUDE.md`에는 전역 규칙만, 패키지/모듈 디렉토리에는 해당 도메인 규칙만 작성한다. Claude Code는 현재 파일 위치에서 상위로 올라가며 모든 `CLAUDE.md`를 자동으로 병합한다.

- 상황 1: `agents/demand_analyst/CLAUDE.md`에 ADK 에이전트 구현 패턴만 명시. 루트에 중복 작성 불필요.
- 상황 2: `libs/data/CLAUDE.md`에 data pipeline 패턴과 파일 경로 규칙만 작성. 다른 패키지에는 전파되지 않아 규칙 오염 방지.

---

**Practice 2: 200줄 제한과 분리 기준**

`CLAUDE.md` 파일이 200줄을 초과하면 도메인별로 분리한다. 독립적으로 수정 가능한 관심사(test 규칙, API 설계, data 패턴)를 별도 파일로 추출한다.

- 상황 1: 루트 `CLAUDE.md`가 300줄이 되면 test 규칙을 `docs/conventions/testing.md`로 분리하고 루트에서 링크 참조.
- 상황 2: 에이전트별 도구 설계 규칙이 늘어나면 `agents/CLAUDE.md`를 만들어 에이전트 공통 패턴(ToolContext, session state) 기술.

---

**Practice 3: 섹션 구조 표준화**

`CLAUDE.md`는 Build/Run/Test, Code Style, Architecture, Git Workflow, Team Operations 5개 섹션으로 고정한다. 순서를 일관되게 유지하면 에이전트가 관련 규칙을 빠르게 탐색한다.

- 상황 1: 신규 개발자가 합류했을 때 에이전트에게 "test 실행 방법"을 물으면 Build/Run/Test 섹션에서 즉시 답변.
- 상황 2: 새 라이브러리 추가 규칙은 Architecture 섹션의 Workspace Structure 하위에만 추가. 분산 배치 방지.

---

**Practice 4: 명령어 예시 code block 필수화**

`CLAUDE.md`에 기술하는 모든 명령어는 실행 가능한 code block으로 작성한다. 자연어 설명만 있는 경우 에이전트가 잘못된 명령을 생성할 확률이 높다.

- 상황 1: "uv로 test 실행" 대신 `` `uv run pytest -m unit` `` code block으로 명시. 에이전트가 올바른 flag와 함께 실행.
- 상황 2: 새 패키지 추가 절차를 numbered list + 각 단계별 code block으로 작성. 에이전트가 절차를 순서대로 실행.

---

## 2. Skills/Agents 활용 패턴

**Practice 5: 도메인별 custom skill 등록**

반복적으로 수행하는 작업(컨벤션 검사, 특정 패턴의 code 생성)은 `/manage-skill`로 skill 파일로 등록한다. Skill은 재사용 가능한 prompt template이다.

- 상황 1: ADK 에이전트 boilerplate 생성을 `/convention-adk-agent` skill로 등록. 새 에이전트 생성 시 skill 호출로 일관된 구조 생성.
- 상황 2: data pipeline 검증 로직(파일 경로 패턴, ToolContext 사용)을 `/check-data-pipeline` skill로 등록하여 PR review 시 자동 검사.

---

**Practice 6: 에이전트 역할 분리 원칙**

`explore`(탐색), `executor`(구현), `verifier`(검증) 역할을 분리하여 순차 실행한다. 하나의 에이전트에 탐색과 구현을 동시에 맡기면 context가 오염된다.

- 상황 1: bug 수정 시 `debugger`로 원인 파악 → `executor`로 수정 → `verifier`로 test 통과 확인. 각 단계 결과를 요약본으로 전달.
- 상황 2: 신기능 구현 시 `explore`로 관련 파일 목록 획득 → `planner`로 구현 계획 작성 → `executor`로 구현.

---

**Practice 7: 에이전트 model 크기 매칭**

단순 탐색은 `haiku`, 표준 구현은 `sonnet`, architecture 설계나 복잡한 분석은 `opus`를 지정한다.

- 상황 1: 파일 위치 찾기(`explore haiku`), function 구현(`executor sonnet`), 전체 architecture review(`architect opus`)를 명시적으로 구분.
- 상황 2: 5개 파일 이하의 소규모 변경은 `verifier haiku`로 검증. 보안 관련 변경은 `security-reviewer opus`로 격상.

---

**Practice 8: 전문 에이전트 chain 구성**

`document-specialist`를 먼저 호출하여 공식 문서를 조회한 후 `executor`에게 구현을 맡긴다. SDK/API 사용 시 hallucination을 방지한다.

- 상황 1: Google ADK 새 기능 사용 시 `document-specialist`로 공식 API 문서 조회 → 결과를 `executor`에 전달하여 구현.
- 상황 2: `pandas` 새 버전 migration 시 `document-specialist`로 변경 사항 조회 → `build-fixer`에 전달하여 type 오류 수정.

---

## 3. 멀티 에이전트 Workflow

**Practice 9: Ralph 모드로 완전 자율 실행**

복잡한 기능 구현 시 `/ralph`를 사용하여 explore → plan → execute → verify → fix loop를 자동화한다.

- 상황 1: "demands 분석 에이전트에 새로운 집계 지표 추가"를 ralph로 실행. 관련 파일 탐색부터 test 통과까지 자동 완료.
- 상황 2: legacy code refactoring 시 ralph를 사용하여 기존 test가 모두 통과하는 것을 확인할 때까지 반복 실행.

---

**Practice 10: Ultrawork로 병렬 구현**

독립적인 모듈 여러 개를 동시에 구현할 때 `/ultrawork`를 사용한다.

- 상황 1: 3개의 data 전처리 모듈(H3 지리, ML 전처리, 집계)을 동시에 구현. 순차 실행 대비 3배 속도 향상.
- 상황 2: 각 에이전트 패키지의 단위 test를 ultrawork로 병렬 작성. 에이전트 간 의존성이 없으므로 충돌 없음.

---

**Practice 11: omc-teams로 외부 모델 활용**

`codex`와 `gemini`를 병렬로 사용하여 best practice 조사, code review, 대안 구현 탐색을 수행한다.

- 상황 1: 새로운 data pipeline 패턴 도입 전 `2:codex`와 `2:gemini`로 Python best practice 조사. pros/cons 비교 후 결정.
- 상황 2: 복잡한 algorithm 구현 시 codex에게 하나의 방식, gemini에게 다른 방식으로 구현 요청. Claude가 두 결과를 비교하여 최적안 선택.

---

**Practice 12: Team 모드로 단계별 품질 보증**

`/team`으로 plan → exec → verify → fix pipeline을 구성한다.

- 상황 1: 새 에이전트 전체 구현 시 team 모드 사용. `planner`가 설계하고 `executor`가 구현하고 `verifier`가 test하는 흐름이 자동 조율.
- 상황 2: 대규모 refactoring 시 `team ralph`로 실행. 팀이 완료를 선언할 때까지 fix loop가 반복.

---

## 4. 코딩 컨벤션 강제 방법

**Practice 13: Pre-commit Hook으로 컨벤션 자동 강제**

`pre-commit` 설정 파일에 ruff, mypy, pytest를 등록하여 commit 시 자동으로 컨벤션 검사를 실행한다.

- 상황 1: executor 에이전트가 type hint를 누락한 function을 작성했을 때, pre-commit의 mypy 검사가 commit을 block. 에이전트가 자동으로 수정 후 재commit.
- 상황 2: ruff format을 pre-commit에 등록하여 들여쓰기, import 순서가 일관되게 유지. code review에서 style 논의 불필요.

---

**Practice 14: 필수 skill chain 실행 강제**

`CLAUDE.md`의 "구현 시 필수 스킬" 테이블에 code 작성 전 반드시 실행해야 할 skill 목록을 명시한다.

- 상황 1: Python function 구현 시 `/convention-python` → `/check-anti-patterns` → `/adversarial-review` 순서로 skill 실행. 안티패턴 조기 발견.
- 상황 2: 새로운 도메인 컨벤션 정의 시 테이블에 행 추가. 다음 구현부터 해당 skill 자동 실행.

---

**Practice 15: Stop Hook으로 자동 검증**

Claude Code Stop hook에 `/check-python-style` skill을 등록하여 응답 완료 후 자동으로 style 검사를 실행한다.

- 상황 1: executor가 function을 작성하고 멈추는 순간 Stop hook이 ruff + mypy를 실행. 위반 사항 즉시 보고.
- 상황 2: 79자 초과 줄이 발견되면 Stop hook이 경고 메시지 출력. 다음 iteration에서 에이전트가 수정.

---

## 5. PR/ADR 설계문서 관리

**Practice 16: PR description 구조화 template 강제**

PR 설명에 Summary, Test Plan, ADR Links, Breaking Changes 섹션을 필수로 포함하는 template을 `.github/pull_request_template.md`에 작성한다.

- 상황 1: `git-master` 에이전트가 PR을 생성할 때 template을 자동으로 채운다. reviewer가 변경 목적과 test 방법을 즉시 파악 가능.
- 상황 2: Breaking change가 포함된 PR에서 해당 섹션이 비어 있으면 CI가 PR을 block.

---

**Practice 17: ADR 자동 생성 workflow**

새로운 architecture 결정 시 `architect` 에이전트가 ADR 초안을 작성하고 `critic` 에이전트가 검토하는 workflow를 정의한다.

- 상황 1: 새 라이브러리 도입 결정 시 `/ralplan --deliberate`를 실행. Planner, Architect, Critic이 타당성을 검토하고 ADR 초안 생성.
- 상황 2: API 설계 변경 시 `architect`가 ADR을 작성하고 `code-reviewer opus`가 하위 호환성 영향을 검토하여 ADR에 추가.

---

**Practice 18: Rule of Small — PR = 설계 결정 하나**

하나의 PR은 하나의 설계 결정만 다룬다. 코드 변경량이 아니라 설계 결정의 수로 PR 범위를 정의한다.

- 상황 1: 데이터 pipeline 리팩토링 시 "파일 경로 패턴 변경"과 "column 네이밍 규칙 변경"을 별도 PR로 분리. 각 PR이 독립적으로 review 가능.
- 상황 2: 큰 기능 추가 시 설계문서 PR 먼저 merge → code 구현 PR 순서로 진행. 설계 검토와 code 검토 분리.

---

## 6. Context 관리

**Practice 19: 서브에이전트에 최소 context 전달**

서브에이전트 호출 시 전체 히스토리 대신 요약본 + 핵심 파일 경로 목록만 전달한다. Context 창의 25% 이하로 유지.

- 상황 1: `explore`가 반환한 30개 파일 목록 중 실제 수정 대상 5개만 `executor`에 전달.
- 상황 2: 10라운드 진행된 대화를 `executor`에 넘길 때 "완료된 작업: X, 남은 작업: Y, 관련 파일: [경로]" 형식으로 압축.

---

**Practice 20: LSP 도구로 대용량 파일 선택적 읽기**

800줄 이상 파일은 전체 읽기 대신 `lsp_document_symbols`로 symbol 목록을 먼저 조회하고 필요한 function만 `offset`/`limit`으로 부분 읽기한다.

- 상황 1: `config.py`가 600줄일 때 `lsp_document_symbols`로 function 목록 조회 후 필요한 function 위치만 Read로 조회.
- 상황 2: 대규모 에이전트 파일에서 특정 패턴을 찾을 때 `ast_grep_search`로 구조적 검색. 전체 파일 읽기 없이 정확한 위치만 반환.

---

**Practice 21: 세션 간 project memory 활용**

`project_memory_write`로 주요 architecture 결정, 파일 구조 요약, 반복 사용 경로를 영구 저장한다.

- 상황 1: 각 패키지의 entry point 경로를 project memory에 저장. 새 세션에서 `explore`로 재탐색하는 비용 절약.
- 상황 2: 반복적으로 수정하는 `cli_runner/config.py`의 function 목록을 project memory notes에 추가.

---

## 7. 폴더 구조 Best Practice

**Practice 22: 기능별 분류 (타입별 분류 금지)**

`utils/`, `helpers/`, `models/` 같은 type 기반 폴더 대신 `demand_analysis/`, `regional_data/`, `preprocessing/` 같은 기능/도메인 기반 폴더를 사용한다.

- 상황 1: data loader, 전처리, 집계 기능을 모두 `utils/`에 넣는 대신 `libs/data/`, `libs/preprocessing/`으로 분리.
- 상황 2: 에이전트 관련 도구를 에이전트 폴더 내부에 위치시킴(`agents/demand_analyst/tools/`). 다른 에이전트에서 무분별한 import 방지.

---

**Practice 23: uv workspace 패키지 레이아웃 표준화**

모든 패키지에 `src/{package_name}/__init__.py`, `tests/__init__.py`, `pyproject.toml` 구조를 강제한다.

- 상황 1: 신규 라이브러리 추가 시 `executor`가 CLAUDE.md의 패키지 레이아웃을 참조하여 동일한 구조로 생성.
- 상황 2: `tests/__init__.py` 누락으로 pytest 탐색 실패하는 문제를 표준 레이아웃에 명시하여 사전 방지.

---

**Practice 24: output/임시 파일 전용 디렉토리 분리**

생성된 report, log, 임시 data는 `output/`과 `data/` 디렉토리로 분리하고 `.gitignore`에 등록한다.

- 상황 1: 에이전트가 생성한 report를 `output/reports/`에 저장. source code 디렉토리 오염 방지.
- 상황 2: `data/` 디렉토리의 대용량 CSV는 `.gitignore`에 등록하고 S3 경로만 `CLAUDE.md`에 기록.

---

## 8. Python 프로젝트 특화 규칙

**Practice 25: 모든 function에 type hint 강제**

`CLAUDE.md`에 "All function arguments and return values MUST be typed"를 명시하고 mypy를 CI에 통합한다.

- 상황 1: `executor`가 `def load_data(file):` 형태로 작성하면 pre-commit mypy가 block. 에이전트가 `def load_data(file: str) -> pd.DataFrame:` 형태로 수정.
- 상황 2: ADK ToolContext를 인자로 받는 모든 도구 function에 `tool_context: ToolContext` type hint가 자동으로 포함됨.

---

**Practice 26: 상대 import 금지와 절대 import 강제**

`CLAUDE.md`에 "NEVER use relative imports across packages"를 명시하고 ruff rule `TID252`를 활성화하여 자동 감지한다.

- 상황 1: `executor`가 `from ..utils import PromptLoader`로 작성하면 ruff가 오류 반환. 에이전트가 절대 import로 수정.
- 상황 2: sys.path 조작 code가 포함된 PR은 `code-reviewer`가 CLAUDE.md 규칙 위반으로 즉시 반려.

---

**Practice 27: ToolContext state를 통한 도구 의존성 주입**

ADK 도구 function은 파일 경로를 직접 인자로 받지 않고 `tool_context.state`에서 읽는다.

- 상황 1: `executor`가 `def load_csv(file_path: str)` 형태로 도구를 작성하면 CLAUDE.md 패턴 위반. `tool_context.state.get("app:file")`로 수정.
- 상황 2: 도구 function에서 파일 존재 여부 재검사를 시도하면 `check-anti-patterns`가 "중복 검증" 패턴으로 감지.

---

**Practice 28: Pandas vectorization 강제**

pandas code는 반드시 DataFrame을 vector적 관점으로 최적화한다. `iterrows()` 사용 금지.

- 상황 1: `df.iterrows()`로 loop 처리하는 code → `df.apply()` 또는 vectorized 연산으로 대체. 100만 row 기준 10배 이상 속도 차이.
- 상황 2: Query 작성 시 반드시 ANSI SQL로 구현. DB engine 종속성 제거로 Spark, DuckDB, SQLite 모두 동일한 query 사용 가능.

---

## 참고

- 출처: claude + codex + gemini 3-agent 병렬 조사 (omc-teams, 2026-03-18)
- 관련 이슈: [issue-74-ai-pr-workflow.md](../references/github-issues/issue-74-ai-pr-workflow.md)
- 관련 스펙: [deep-interview-general-rules.md](../../.omc/specs/deep-interview-general-rules.md)
