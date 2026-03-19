---
name: scaffold-structure
triggers:
  - "scaffold structure"
description: "프로젝트 폴더 구조를 사용자와 소통하며 결정하고 생성한다. 프로젝트 타입별 베스트 프랙티스를 참조한다."
argument-hint: "[project_type] [--mode=direct|checklist] - 프로젝트 타입 (data-science, backend-fastapi, general-python, hypermodern-python, cli-application, library-package)"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: 프로젝트 폴더 구조 결정 시 사용. 레퍼런스 문서: @templates/folder-structures/
agent: 폴더 구조 설계사 - 베스트 프랙티스를 기반으로 프로젝트에 최적화된 폴더 구조를 제안하고, 각 결정의 이유를 설명하며 사용자와 합의한다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Composite
references:
  - "@skills/manage-claude-md/SKILL.md"
  - "@skills/manage-readme/SKILL.md"
  - "@skills/project-init/SKILL.md"
  - "@templates/folder-structures/"
  - "@templates/folder-structures/_custom-template.md"
  - "@templates/folder-structures/backend-fastapi.md"
  - "@templates/folder-structures/clean-architecture-python.md"
  - "@templates/folder-structures/cli-application.md"
  - "@templates/folder-structures/data-science.md"
  - "@templates/folder-structures/general-python.md"
  - "@templates/folder-structures/hypermodern-python.md"
  - "@templates/folder-structures/library-package.md"
  - "@templates/folder-structures/{type}.md"
referenced-by:
  - "@skills/manage-claude-md/SKILL.md"
  - "@skills/manage-readme/SKILL.md"
  - "@skills/project-init/SKILL.md"

---
# scaffold-structure

> 프로젝트 폴더 구조를 베스트 프랙티스 기반으로 결정하고 생성

---

## 목적

1. **프로젝트 타입별 베스트 프랙티스 적용**: 검증된 구조 제안
2. **사용자와 소통하며 결정**: 각 폴더 역할 설명 + 동의 확인
3. **마크다운 체크리스트 기반 확인**: 사용자가 검토 후 확정

---

## 지원 프로젝트 타입

| 타입 | 설명 | 레퍼런스 |
|------|------|----------|
| `custom-best-practice` | 사용자 정의 베스트 프랙티스 | `../../templates/folder-structures/_custom-template.md` |
| `data-science` | 데이터 분석, ML 프로젝트 | `../../templates/folder-structures/data-science.md` |
| `backend-fastapi` | FastAPI 백엔드 API | `../../templates/folder-structures/backend-fastapi.md` |
| `general-python` | 범용 Python 패키지 | `../../templates/folder-structures/general-python.md` |
| `hypermodern-python` | uv + Ruff 현대적 Python | `../../templates/folder-structures/hypermodern-python.md` |
| `cli-application` | Typer + Rich CLI 앱 | `../../templates/folder-structures/cli-application.md` |
| `library-package` | PyPI 배포용 라이브러리 | `../../templates/folder-structures/library-package.md` |
| `clean-architecture-python` | Clean Architecture Python | `../../templates/folder-structures/clean-architecture-python.md` |

---

## 실행 프로세스

### Phase 1: 프로젝트 타입 확인

```
1. 사용자에게 프로젝트 타입 질문 (또는 인자로 받음)
2. 해당 타입의 레퍼런스 문서 로드
   - @templates/folder-structures/{type}.md
3. 상호작용 모드 선택:
   - direct: AskUserQuestion 도구로 실시간 질문
   - checklist: 마크다운 체크리스트 파일 생성 후 검토
```

#### AskUserQuestion 활용 지점

**지점 1: 프로젝트 타입 확인**

```yaml
AskUserQuestion:
  questions:
    - question: "프로젝트 타입을 선택해주세요"
      header: "프로젝트 타입"
      multiSelect: false
      options:
        - label: "data-science (권장)"
          description: "Jupyter, pandas, ML | 데이터 분석 프로젝트"
        - label: "backend-fastapi"
          description: "FastAPI | REST API, 마이크로서비스"
        - label: "cli-application"
          description: "Typer + Rich | 명령줄 도구"
        - label: "library-package"
          description: "PyPI 배포 | 재사용 라이브러리"
        - label: "hypermodern-python"
          description: "uv + Ruff | 최신 베스트 프랙티스"
        - label: "general-python"
          description: "범용 Python | 최소 구조"
```

**지점 2: 상호작용 모드 선택**

```yaml
AskUserQuestion:
  questions:
    - question: "어떤 방식으로 폴더 구조를 확정할까요?"
      header: "상호작용 모드"
      multiSelect: false
      options:
        - label: "Direct - 실시간 질문 (권장)"
          description: "각 폴더마다 즉시 동의 확인 | 빠른 진행"
        - label: "Checklist - 체크리스트 파일"
          description: "마크다운 파일로 검토 후 확정 | 신중한 검토"
```

**지점 3: 폴더별 동의 확인 (Direct 모드)**

```yaml
AskUserQuestion:
  questions:
    - question: "config/ 폴더 구조를 사용할까요?"
      header: "폴더 구조"
      multiSelect: false
      options:
        - label: "사용 (권장)"
          description: "역할: 설정 파일 중앙 관리 | Omegaconf + Pydantic 패턴"
        - label: "제외"
          description: "설정 파일을 다른 방식으로 관리"
        - label: "커스터마이제이션"
          description: "구조 수정 필요"
```

**지점 4: 체크리스트 수정사항 반영 (Checklist 모드)**

```yaml
AskUserQuestion:
  questions:
    - question: "체크리스트의 수정사항을 적용할까요?"
      header: "수정 반영"
      multiSelect: false
      options:
        - label: "네 - 수정사항 반영 (권장)"
          description: "체크리스트 코멘트 기반 구조 조정"
        - label: "아니오 - 다시 검토"
          description: "체크리스트 재작성"
```

**지점 5: 최종 확정**

```yaml
AskUserQuestion:
  questions:
    - question: "폴더 생성을 진행할까요?"
      header: "최종 확정"
      multiSelect: false
      options:
        - label: "네 - 폴더 생성 (권장)"
          description: "확정된 구조로 폴더 생성 시작"
        - label: "아니오 - 검토 계속"
          description: "추가 검토 필요"
```

### Phase 2: 폴더 구조 제안 및 설명

각 폴더에 대해 **역할과 이유**를 설명하며 동의 확인.

#### 상호작용 모드 A: Direct (AskUserQuestion 사용)

실시간으로 사용자에게 질문하며 구조를 확정한다:

```
AskUserQuestion 도구 호출:
- question: "config/ 폴더 구조를 사용할까요?"
- header: "폴더 구조"
- options:
  1. "사용 (Recommended)" - Omegaconf + Pydantic 패턴 적용
  2. "제외" - 설정 파일을 다른 방식으로 관리
- description: "역할: 설정 파일 중앙 관리. 이유: 하드코딩 방지, 환경별 분리"
```

**장점**: 빠른 피드백, 대화 흐름 유지
**적합**: 폴더 5개 이하, 빠른 결정 필요 시

#### 상호작용 모드 B: Checklist (마크다운 파일 사용)

마크다운 체크리스트를 생성하여 사용자가 검토 후 확정:

**출력 형식:**

```markdown
## 제안 폴더 구조

### 1. `config/` 폴더
| 항목 | 내용 |
|------|------|
| **역할** | 설정 파일 중앙 관리 (config.yaml, 스키마) |
| **이유** | 하드코딩 방지, 환경별 설정 분리, Omegaconf + Pydantic 패턴 적용 |

**동의하시나요?** 이 폴더 구조를 사용할까요?

### 2. `src/{project_name}/` 폴더
| 항목 | 내용 |
|------|------|
| **역할** | 소스 코드 (src layout 적용) |
| **이유** | 설치된 패키지와 로컬 코드 명확히 분리, 테스트 신뢰성 향상 |

**동의하시나요?** 이 폴더 구조를 사용할까요?
```

### Phase 3: 체크리스트 파일 생성

사용자가 검토할 수 있도록 **마크다운 체크리스트** 파일 생성:

**파일 위치**: `docs/architecture/folder-structure-checklist.md`

```markdown
# 폴더 구조 확정 체크리스트

> 동의하는 항목에 [x] 표시, 수정이 필요한 항목에 [ ] 유지 후 코멘트 작성
> 검토 완료 후 "최종 확정"에 [x] 표시

## 공통 구조

- [ ] `.claude/` - Claude Code 설정
- [ ] `config/` - 설정 파일 (Omegaconf + Pydantic)
- [ ] `docs/` - 프로젝트 문서
- [ ] `src/{project_name}/` - 소스 코드 (src layout)
- [ ] `tests/` - 테스트 코드

## Data Science 전용 (해당 시)

- [ ] `data/raw/` - 원본 데이터 (불변, 절대 수정 금지)
- [ ] `data/interim/` - 중간 처리 데이터
- [ ] `data/processed/` - 최종 처리 데이터
- [ ] `notebooks/` - Jupyter 노트북 (01_, 02_ prefix)
- [ ] `models/` - 학습된 모델
- [ ] `figures/` - 생성된 시각화

## Backend FastAPI 전용 (해당 시)

- [ ] `src/{name}/api/` - API 라우터
- [ ] `src/{name}/core/` - 설정, 보안, 예외
- [ ] `src/{name}/models/` - ORM 모델
- [ ] `src/{name}/schemas/` - Pydantic 스키마
- [ ] `src/{name}/services/` - 비즈니스 로직
- [ ] `src/{name}/repositories/` - 데이터 접근 계층
- [ ] `src/{name}/db/` - DB 연결 및 마이그레이션

## 수정 요청 사항

<!-- 수정이 필요한 경우 아래에 작성 -->

---

## 최종 확정

- [ ] **위 구조에 동의하며 폴더 생성을 진행합니다.**

서명: _________________ 날짜: _________________
```

### Phase 4: 체크리스트 읽기 및 처리

```
1. 체크리스트 파일 읽기 (Read 도구)
2. 파싱:
   - [x] 표시된 항목 → 확정 목록에 추가
   - [ ] 표시된 항목 + 코멘트 → 수정 필요 목록
3. "최종 확정" 체크 여부 확인
   - [x] 이면 → Phase 5 진행
   - [ ] 이면 → 수정 사항 논의 후 Phase 3 반복
```

### Phase 5: 폴더 생성

```bash
# 확정된 구조대로 폴더 생성
mkdir -p .claude
mkdir -p config/schemas
mkdir -p docs/{references,prd,adr,architecture}
mkdir -p src/{project_name}
mkdir -p tests/{unit,integration}

# .gitkeep 파일 생성 (빈 폴더 유지)
touch data/raw/.gitkeep
touch models/.gitkeep

# 기본 파일 생성
touch src/{project_name}/__init__.py
touch tests/conftest.py
```

### Phase 6: 결과 보고

```markdown
## 폴더 구조 생성 완료

### 생성된 폴더
- [x] config/
- [x] docs/
- [x] src/{project_name}/
- [x] tests/
...

### 다음 단계
1. `pyproject.toml` 설정 → `/project-init` 실행
2. CLAUDE.md 생성 → `/manage-claude-md create`
3. README.md 생성 → `/manage-readme`
```

---

## 사용 예시

### 예시 1: Data Science 프로젝트

```
User: /scaffold-structure data-science

Claude: 레퍼런스 문서를 확인했습니다. Data Science 프로젝트 구조를 제안합니다.

### 1. `data/` 폴더 구조
| 항목 | 내용 |
|------|------|
| **역할** | 데이터 저장 (raw → interim → processed) |
| **이유** | 원본 데이터 불변 원칙, 파이프라인 단계별 분리 |

이 구조를 사용할까요?

User: 네, 동의합니다.

Claude: 체크리스트 파일을 생성했습니다.
파일: docs/architecture/folder-structure-checklist.md

검토 후 [x] 표시해주세요. 완료되면 말씀해주세요.

User: 검토 완료했습니다.

Claude: (체크리스트 파일 읽기)
모든 항목이 확정되었습니다. 폴더를 생성합니다...
```

### 예시 2: Backend FastAPI 프로젝트 (Checklist 모드)

```
User: /scaffold-structure backend-fastapi

Claude: FastAPI 백엔드 프로젝트 구조를 제안합니다.

Clean Architecture 패턴을 적용하여 계층을 분리합니다:
- API Layer (api/) → HTTP 요청/응답
- Service Layer (services/) → 비즈니스 로직
- Repository Layer (repositories/) → 데이터 접근
- Domain Layer (models/, schemas/) → 엔티티

이 계층 구조에 동의하시나요?
```

### 예시 3: Direct 모드 (AskUserQuestion)

```
User: /scaffold-structure cli-application --mode=direct

Claude: CLI Application 프로젝트 구조를 결정합니다.
AskUserQuestion 도구로 각 폴더에 대해 질문합니다.

[AskUserQuestion 도구 호출]
question: "cli/ 폴더 구조를 어떻게 구성할까요?"
header: "CLI 구조"
options:
  - label: "Typer 서브커맨드 패턴 (Recommended)"
    description: "cli/commands/에 서브커맨드 분리, 확장성 높음"
  - label: "단일 파일 구조"
    description: "cli/main.py에 모든 명령어, 규모가 작을 때 적합"
User: (Typer 서브커맨드 패턴 선택)

Claude: Typer 서브커맨드 패턴으로 확정했습니다.

[다음 AskUserQuestion 호출]
question: "utils/ 폴더 구성은 어떻게 할까요?"
header: "유틸리티"
options:
  - label: "console.py + logger.py 분리 (Recommended)"
    description: "Rich console과 로깅을 별도 관리"
  - label: "통합 utils.py"
    description: "단일 파일로 유틸리티 관리"
...
```

### 예시 4: Hypermodern Python 프로젝트

```
User: /scaffold-structure hypermodern-python

Claude: Hypermodern Python 구조를 제안합니다.

핵심 특징:
- uv + Ruff 현대적 도구 체인
- src layout 필수
- 100% 타입 힌트 + mypy strict
- pre-commit 자동 린트/포맷

체크리스트 파일을 생성할까요, 아니면 바로 질문할까요?
```

---

## 관련 스킬

| 스킬 | 역할 | 연계 |
|------|------|------|
| [@skills/project-init/SKILL.md] | 프로젝트 초기화 | scaffold-structure 결과 사용 |
| [@skills/manage-claude-md/SKILL.md] | CLAUDE.md 생성 | 폴더 구조 반영 |
| [@skills/doc-sys/SKILL.md] | 시스템 아키텍처 문서 | 폴더 구조 문서화 |

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.1.0 | 2026-01-21 | AskUserQuestion 모드 추가, 프로젝트 타입 6개로 확장 |
| 1.0.0 | 2026-01-21 | 초기 생성 - 3개 프로젝트 타입 지원 |

## Gotchas (실패 포인트)

- 폴더 구조가 너무 깊으면 탐색 어려움 — 최대 4단계 권장
- 하이픈 디렉터리는 Python import 불가 — snake_case 사용
- 처음부터 완벽한 구조 추구 금지 — Gall's Law: 단순부터 진화
- src/ 레이아웃과 flat 레이아웃 혼용 금지
