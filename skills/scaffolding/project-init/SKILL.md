---
name: project-init
triggers:
  - "project init"
description: "Python 프로젝트 초기화 및 문서화 자동화 스킬. CLAUDE.md, settings.json, 스킬 패키지를 생성한다."
argument-hint: >-
  [project_name] [project_type] [license_type] [team_size]
  예: my-project data-science proprietary solo
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
  - TodoWrite
model: claude-sonnet-4-6[1m]
context: >-
  프로젝트 초기화 및 문서화 인프라 구축 컨텍스트.
  scaffold-structure, manage-claude-md, manage-readme와 통합 작동하며,
  초기 설정 이후 지속적 문서 업데이트를 자동화한다.
agent: >-
  시스템 아키텍트 페르소나로 작동. 폴더 생성 중 문제 발생 시 아키텍처 관점에서
  조언 및 오류 수정 제안을 제공한다. 사용자 입력이 모호할 때 명확화를 요청하며,
  최소 질문 원칙(95% 확신에 필요한 최소 질문)을 준수한다.
hooks:
  pre_execution:
    - verify_target_directory_empty
    - validate_project_name
  post_execution:
    - generate_initialization_report
    - create_initial_commit_message
category: 워크플로우
skill-type: Composite
references:
  - "@skills/3-step-workflow/SKILL.md"
  - "@skills/cleanup-memory/SKILL.md"
  - "@skills/convention-commit/SKILL.md"
  - "@skills/doc-prd/SKILL.md"
  - "@skills/doc-tasks/SKILL.md"
  - "@skills/license-guide/SKILL.md"
  - "@skills/manage-readme/SKILL.md"
  - "@skills/recommend-memory/SKILL.md"
  - "@skills/scaffold-structure/SKILL.md"
  - "@skills/setup-quality/SKILL.md"
  - "@skills/setup-uv-env/SKILL.md"
  - "@templates/folder-structures/_custom-template.md"
  - "@templates/folder-structures/data-science.md"
  - "@templates/folder-structures/backend-fastapi.md"
  - "@templates/folder-structures/cli-application.md"
  - "@templates/folder-structures/library-package.md"
  - "@templates/folder-structures/hypermodern-python.md"
  - "@templates/folder-structures/general-python.md"
referenced-by:
  - "@skills/cleanup-memory/SKILL.md"
  - "@skills/convention-commit/SKILL.md"
  - "@skills/doc-prd/SKILL.md"
  - "@skills/doc-tasks/SKILL.md"
  - "@skills/license-guide/SKILL.md"
  - "@skills/manage-readme/SKILL.md"
  - "@skills/prevent-context-overflow/SKILL.md"
  - "@skills/project-init-with-scenarios/SKILL.md"
  - "@skills/recommend-memory/SKILL.md"
  - "@skills/scaffold-structure/SKILL.md"
  - "@skills/setup-quality/SKILL.md"
  - "@skills/setup-uv-env/SKILL.md"

---
# project-init

> Python 프로젝트 초기화 및 문서화 자동화 스킬

---

## 목적

1. **프로젝트 기반 구축**: 폴더 구조, 설정 파일, 문서 자동 생성
2. **계층적 메모리 구조**: Level 1-3 문서 계층으로 컨텍스트 효율화
3. **추적성 (Traceability)**: 코드와 요구사항의 명확한 연결
4. **일관된 프로젝트 구조**: 베스트 프랙티스 적용

---

## 핵심 개념

**계층적 메모리 (Aidoc Framework 기반)**:
- **Level 1 (Core)**: 항상 로드 - CLAUDE.md, Quick Commands
- **Level 2 (Detailed)**: 필요 시 로드 - Conventions, Workflows
- **Level 3 (Reference)**: 명시적 참조 - Troubleshooting, ADR

**추적성**: 모든 코드는 요구사항과 명시적으로 연결

---

## 스킬 유형

**Composite Skill** - 다음 스킬들을 순차 조합:

| 순서 | 스킬 | 역할 |
|------|------|------|
| 1 | [@skills/scaffold-structure/SKILL.md] | 폴더 구조 결정 및 생성 |
| 2 | [@skills/setup-uv-env/SKILL.md] | uv 환경 초기화 (pyproject.toml, .venv) |
| 3 | [@skills/license-guide/SKILL.md] | 라이센스 선택 및 LICENSE 파일 생성 |
| 4 | (내장) | CLAUDE.md, settings.json, commands/ 생성 |
| 5 | [@skills/manage-readme/SKILL.md] | README.md 생성 |
| 6 | (내장) | Git 초기화 (선택) |

---

## 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|----------|------|--------|------|
| `project_name` | Yes | - | 프로젝트 이름 (snake_case 권장) |
| `project_type` | No | `data-science` | 프로젝트 타입 |
| `license_type` | No | `proprietary` | 라이선스 종류 |
| `team_size` | No | `solo` | 팀 규모 |

### project_type 옵션

| 타입 | 설명 | 주요 도구 |
|------|------|----------|
| `data-science` | 데이터 분석/ML | pandas, jupyter, scikit-learn |
| `backend-fastapi` | FastAPI 웹 API | fastapi, uvicorn, sqlalchemy |
| `cli-application` | CLI 도구 | typer, rich |
| `library-package` | PyPI 라이브러리 | build, twine, sphinx |
| `hypermodern-python` | 현대적 Python | uv, ruff, mypy |
| `general-python` | 범용 Python | pytest, ruff |

---

## 실행 프로세스

### Step 1: 초기화 방식 선택

AskUserQuestion으로 표준 타입 또는 커스텀 템플릿 중 선택한다.

- **표준 타입**: project_type 파라미터 기반으로 자동 생성
- **커스텀 템플릿**: `_custom-template.md` 기반으로 폴더별 선택

### Step 2: 파라미터 수집

파라미터 미제공 시 AskUserQuestion으로 대화형 입력:
1. project_name (필수)
2. project_type 또는 커스텀 폴더 선택
3. license_type (proprietary/MIT/Apache-2.0)
4. team_size (solo/small/medium/large)
5. Git 작성자 정보 (Git config에서 자동 추출 가능)

### Step 3: 사전 검증

```bash
# 현재 디렉토리 확인
ls -la

# 기존 파일 존재 시 경고
```

### Step 4: 디렉토리 구조 생성

`/scaffold-structure`를 호출하여 프로젝트 타입에 맞는 폴더 생성:

```
project-root/
├── .claude/
│   ├── CLAUDE.md               # Level 1: 핵심 컨텍스트
│   ├── settings.json
│   ├── commands/               # 커스텀 커맨드 (5개)
│   └── docs/                   # Level 2, 3 문서
├── src/{project_name}/
├── tests/
├── docs/
├── pyproject.toml
├── README.md
└── .gitignore
```

**프로젝트 타입별 추가 폴더**:
- **data-science**: data/, notebooks/, models/
- **backend-fastapi**: src/api/, src/core/, src/models/, docker/
- **cli-application**: src/cli/commands/

### Step 5: LICENSE 파일 생성

`/license-guide {license_type}` 호출하여 라이센스 파일 생성

### Step 6: CLAUDE.md 생성 (Level 1)

프로젝트 타입에 맞는 Quick Commands 포함:

```markdown
# {project_name} 프로젝트

## 빠른 명령어

| 명령어 | 설명 |
|--------|------|
| `uv sync` | 의존성 설치 |
| `pytest tests/ -v` | 테스트 실행 |
| `ruff check .` | 린트 검사 |
<프로젝트 타입별 추가 명령어>

## 참조 문서

- 전역 설정: `~/.claude/CLAUDE.md`
- Level 2: `@.claude/docs/conventions/`
- Level 3: `@.claude/docs/troubleshooting/`
```

**템플릿 상세**: [@templates/skill-examples/project-init/claude-md-template.md]

### Step 7: settings.json 및 커스텀 커맨드 생성

```json
{
  "permissions": {"mode": "delegate"},
  "hooks": {
    "on_context_complete": {"enabled": true},
    "on_nth_message": {"enabled": true, "n": 50}
  }
}
```

**커스텀 커맨드** (`.claude/commands/`):
- `/compact`: 컨텍스트 압축
- `/sync-diagrams`: 다이어그램 동기화
- `/recommend-memory`: CLAUDE.md 업데이트 추천
- `/cleanup-memory`: CLAUDE.md 정리
- `/update-docs`: 문서 일괄 업데이트

### Step 8: Level 2, 3 문서 템플릿 생성

**.claude/docs/** 구조:
- **conventions/**: python-style.md, testing.md, documentation.md
- **workflows/**: development.md, deployment.md, review.md
- **references/**: architecture.md
- **troubleshooting/**: guide.md
- **decisions/**: adr-template.md

### Step 9: pyproject.toml 생성

`/setup-uv-env init` 호출하여 uv 환경 초기화:

```toml
[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.12"
authors = [{name = "{git_name}", email = "{git_email}"}]
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.3", "mypy>=1.8"]
```

**authors 필드**: Git config에서 자동 추출 또는 수동 입력

**프로젝트 타입별 의존성**: [@templates/skill-examples/project-init/dependencies-by-type.md]

### Step 10: .gitignore 생성

AskUserQuestion으로 구성 방식 선택:
- **표준 템플릿**: Python + 프로젝트 타입별 패턴
- **최소**: __pycache__/, .venv/만
- **커스텀**: 기본만 생성 후 수동 편집

```gitignore
# Claude
.claude/CLAUDE.local.md
.claude/settings.local.json

# Python
__pycache__/
.venv/
.pytest_cache/
.mypy_cache/

# IDE
.vscode/
.idea/
```

### Step 11: README.md 생성

`/manage-readme` 호출하여 프로젝트 타입에 맞는 README 생성

### Step 12: Git 초기화 (선택)

AskUserQuestion으로 Git 초기화 여부 확인:

```bash
git init
git add .
git commit -m "chore: Initial project scaffolding"
```

---

## 사용 예시

### 예시 1: Data Science 프로젝트

```bash
/project-init transit-analysis data-science
```

자동으로 data/, notebooks/, models/ 폴더 및 data science 의존성 포함

### 예시 2: 대화형 입력

```bash
/project-init
```

프로젝트명, 타입, 라이센스, 팀 규모를 차례로 질문받음

### 예시 3: 커스텀 템플릿

```bash
/project-init my-project
```

초기화 방식 선택 → "커스텀 템플릿" → 폴더별 선택 (multiSelect)

---

## 계층적 메모리 사용법

### Level 1 참조 (항상 로드)

```markdown
.claude/CLAUDE.md의 내용은 항상 컨텍스트에 포함됨
```

### Level 2 참조 (필요 시 로드)

```markdown
@.claude/docs/conventions/python-style.md
@.claude/docs/conventions/testing.md
```

### Level 3 참조 (명시적 요청 시)

```markdown
@.claude/docs/troubleshooting/guide.md
@.claude/docs/decisions/adr-template.md
```

---

## 추적성 (Traceability)

모든 코드는 요구사항과 연결되어야 한다:

```python
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """데이터 전처리 수행.

    Traceability:
        - Upstream: REQ-001 (tasks/requirements.md#REQ-001)
        - Downstream: tests/test_process.py::test_process_data
    """
    ...
```

---

## 관련 스킬

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/scaffold-structure/SKILL.md] | 하위 | 폴더 구조 결정 및 생성 |
| [@skills/setup-uv-env/SKILL.md] | 하위 | uv 환경 초기화 |
| [@skills/license-guide/SKILL.md] | 하위 | 라이센스 파일 생성 |
| [@skills/manage-readme/SKILL.md] | 하위 | README.md 생성 |
| [@skills/brainstorming/SKILL.md] | 후속 | 프로젝트 아이디어 구체화 |
| [@skills/doc-prd/SKILL.md] | 후속 | PRD 문서 생성 |

---

## 주의사항

1. **기존 파일 덮어쓰기 금지**: 기존 파일 존재 시 경고 및 확인
2. **Git 초기화 선택적**: 사용자에게 Git 초기화 여부 질문
3. **.claude/* 패턴**: .gitignore에 포함되어 있음. 팀 협업 시 필요한 파일은 `git add -f`로 명시적 추가

---

## 다음 단계

초기화 후:

1. **TODO 플레이스홀더 설정**: `grep -r "\[TODO:" .claude/`로 미설정 항목 확인
2. **CLAUDE.md 작성**: 프로젝트 개요, 기술 스택 완성
3. **개발 표준 수립**: `.claude/docs/conventions/` 검토
4. **첫 ADR 작성**: 기술 스택 선정 근거 기록
5. **첫 기능 구현**: `/doc-prd` → `/doc-tasks` → `/3-step-workflow`

---

## 참조 템플릿

- **CLAUDE.md**: [@templates/skill-examples/project-init/claude-md-template.md]
- **README.md**: [@templates/skill-examples/project-init/readme-template.md]
- **Level 2 문서**: [@templates/skill-examples/project-init/level2-docs-template.md]
- **의존성 상세**: [@templates/skill-examples/project-init/dependencies-by-type.md]

---

## 참고 자료

- Aidoc Flow Framework: https://github.com/vladm3105/aidoc-flow-framework
- PyPA Packaging Guide: https://packaging.python.org/

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 4.0.0 | 2026-01-27 | 보수적 리팩토링 - 1,196줄 → 350줄. 템플릿 분리 |
| 3.1.1 | 2026-01-27 | .gitignore 템플릿 확장 |
| 3.1.0 | 2026-01-27 | AskUserQuestion 지점 5, 6 추가 |
| 3.0.0 | 2026-01-27 | 커스텀 템플릿 지원 추가 |
| 2.0.0 | 2026-01-21 | Aidoc Flow Framework 개념 적용 |
| 1.0.0 | 2026-01-21 | 초기 생성 |

## Gotchas (실패 포인트)

- pyproject.toml 없이 setup.py 사용 — 모던 Python 패키징 표준 미준수
- pre-commit install 누락 시 hook 미동작
- CLAUDE.md 없이 시작 시 Claude Code가 컨텍스트 파악 못함
- .gitignore에 .venv/ 누락 시 가상환경이 git에 포함됨
