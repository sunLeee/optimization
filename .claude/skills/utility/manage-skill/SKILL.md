---
name: manage-skill
triggers:
  - "manage skill"
description: "스킬 파일을 체계적으로 생성, 수정, 삭제, 조회, 검증한다. YAML frontmatter와 마크다운 구조를 관리하며 일관성을 유지한다."
argument-hint: "[action] [skill-name] - 액션: create, edit, delete, list, validate"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: 이 스킬은 `.claude/skills/` 디렉토리 내의 스킬 파일들을 관리한다. 스킬은 Claude Code의 확장 기능으로, 특정 작업을 자동화하거나 워크플로우를 정의한다. 각 스킬은 `{skill-name}/SKILL.md` 형태로 저장되며, YAML frontmatter와 마크다운 본문으로 구성된다.
agent: 당신은 Claude Code 스킬 관리 전문가입니다. 스킬 파일의 구조, YAML frontmatter 규칙, 마크다운 작성 컨벤션을 정확히 이해하고 있습니다. 모든 작업에서 일관성과 명확성을 유지하며, 변경 이력을 Changelog에 기록합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Atomic
references: []
referenced-by:
  - "@skills/sync-skill-catalog/SKILL.md"

---
# 스킬 관리

스킬 파일을 체계적으로 생성, 수정, 삭제, 조회, 검증하는 스킬이다.

## 목적

프로젝트 진행 중 스킬 파일을 체계적으로 관리하여:
- 새로운 스킬을 일관된 템플릿으로 생성
- 기존 스킬의 내용을 안전하게 수정
- 사용하지 않는 스킬을 의존성 검사 후 삭제
- 프로젝트 내 모든 스킬을 조회
- YAML frontmatter의 유효성을 검증

## 사용법

```
/manage-skill [action] [skill-name]
```

### 액션

| 액션 | 설명 | 예시 |
|------|------|------|
| `create` | 새 스킬 생성 | `/manage-skill create my-new-skill` |
| `edit` | 기존 스킬 수정 | `/manage-skill edit systematic-debugging` |
| `delete` | 스킬 삭제 | `/manage-skill delete deprecated-skill` |
| `list` | 스킬 목록 조회 | `/manage-skill list` |
| `validate` | YAML frontmatter 검증 | `/manage-skill validate my-skill` |

## 지침

### 1. create 액션

새로운 스킬을 생성한다.

**프로세스**:
1. 스킬 이름 유효성 검사 (kebab-case 확인)
2. 기존 스킬 중복 확인
3. 사용자에게 스킬 목적, 설명 입력 요청
4. 템플릿 기반으로 SKILL.md 생성
5. 디렉토리 생성: `.claude/skills/{skill-name}/SKILL.md`
6. 생성 완료 메시지 출력

**생성 시 확인 사항**:
- 스킬 이름은 kebab-case (예: `my-new-skill`)
- 중복 스킬 이름 불가
- 필수 frontmatter 필드 모두 포함

### 2. edit 액션

기존 스킬을 수정한다.

**프로세스**:
1. 스킬 존재 여부 확인
2. 기존 스킬 파일 읽기
3. 사용자에게 수정할 내용 확인
4. 변경 사항 적용
5. YAML frontmatter 검증
6. Changelog 업데이트 (날짜, 변경 내용)
7. 저장

**수정 시 주의사항**:
- frontmatter 필수 필드 삭제 금지
- 기존 Changelog 유지
- 수정 후 반드시 검증 실행

### 3. delete 액션

스킬을 삭제한다.

**프로세스**:
1. 스킬 존재 여부 확인
2. 의존성 검사 (다른 스킬에서 참조하는지 확인)
   - SKILL.md의 `referenced-by` 필드 확인
   - 또는 `scripts/analyze-skill-references.sh` 실행
3. 사용자 확인 요청 (의존성 있으면 경고 표시)
4. 삭제 승인 시 디렉토리 전체 삭제
5. 삭제 완료 메시지 출력

**삭제 시 주의사항**:
- 의존성이 있는 스킬은 경고 후 확인 필요
- 삭제는 되돌릴 수 없음 (Git 복구 안내)

**의존성 검사 도구**:
```bash
# 방법 1: referenced-by 필드 확인
grep "referenced-by" skills/{skill-name}/SKILL.md

# 방법 2: 스크립트 사용
./scripts/analyze-skill-references.sh | grep {skill-name}
```

### 4. list 액션

프로젝트 내 모든 스킬을 조회한다.

**출력 형식**:
```
| 스킬 이름 | 설명 | user-invocable |
|----------|------|----------------|
| manage-skill | 스킬 파일 관리 | true |
| diagram-generator | Mermaid 다이어그램 생성 | true |
```

### 5. validate 액션

스킬의 YAML frontmatter를 검증한다.

**검증 항목**:
- 필수 필드 존재 여부 (name, description)
- 필드 타입 검증
- allowed-tools 유효성
- model 필드 유효성

**검증 결과 출력**:
- 성공: "스킬 '{skill-name}' 검증 통과"
- 실패: 오류 항목 상세 표시

## 스킬 템플릿

새 스킬 생성 시 다음 템플릿을 사용한다:

```markdown
---
name: {skill-name}
description: "{스킬 설명 - 여러 줄 가능}"
argument-hint: "{인수 힌트}"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: |
  {컨텍스트 설명}
agent: |
  {에이전트 페르소나}
hooks:
  pre_execution: []
  post_execution: []
category: {카테고리}
skill-type: Atomic
references: []
referenced-by: []
---

# {Skill Name}

{간단한 소개}

## 목적

{스킬 목적 설명}

## 사용법

```
/{skill-name} [args]
```

## Instructions

{상세 지침}

## 예제

{사용 예제}

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| {YYYY-MM-DD} | 초기 생성 |
```

## YAML Frontmatter 필드 설명

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | O | 스킬 이름 (kebab-case) | [@skills/manage-skill/SKILL.md] |
| `description` | O | 스킬 설명 (여러 줄 가능) | 스킬 파일 관리... |
| `argument-hint` | - | 인수 힌트 (help에 표시) | `[action] [name]` |
| `disable-model-invocation` | - | 모델 자동 호출 비활성화 | `false` |
| `user-invocable` | - | 사용자 직접 호출 가능 | `true` |
| `allowed-tools` | - | 사용 가능한 도구 목록 | `[Read, Write]` |
| `model` | - | 사용할 모델 | `claude-sonnet-4-5-20250929` |
| `context` | - | 스킬 컨텍스트 설명 | 이 스킬은... |
| `agent` | - | 에이전트 페르소나 | 당신은... |
| `hooks` | - | 실행 전후 훅 | `pre_execution: []` |
| `category` | O | 스킬 카테고리 | `문서 관리` |
| `skill-type` | O | 스킬 타입 (Atomic/Composite) | `Atomic` |
| `references` | - | 참조하는 스킬 목록 | `[@skills/...]` |
| `referenced-by` | - | 역참조 (자동 생성) | `[]` |

## 유효한 카테고리 목록

| 카테고리 | 설명 | 스킬명 패턴 |
|---------|------|------------|
| 문서 관리 | 문서 생성/관리 | manage-*, doc-* |
| 코드 검증 | 코드 품질 검사 | check-* |
| 품질 관리 | 품질 도구 설정 | quality-* |
| 컨벤션 참조 | 코딩 규칙 참조 | convention-* |
| 환경 설정 | 프로젝트 설정 | setup-* |
| 레퍼런스/시나리오 | 외부 데이터 수집 | ref-* |
| 워크플로우 | 복합 작업 흐름 | *-workflow |
| 개발 지원 | 일반 개발 도구 | - |

## 유효한 skill-type

| 타입 | 설명 | 사용 시점 |
|------|------|----------|
| `Atomic` | 단일 기능 수행 | 독립적 작업 |
| `Composite` | 다른 스킬 조합 실행 | 2개 이상 스킬 호출 |

## 유효한 모델 목록

- `claude-sonnet-4-5-20250929`
- `claude-opus-4-5-20251101`
- `claude-haiku-4-5-20250910`

## 유효한 도구 목록

- `Read` - 파일 읽기
- `Write` - 파일 쓰기
- `Edit` - 파일 수정
- `Glob` - 파일 패턴 검색
- `Grep` - 내용 검색
- `Bash` - 명령어 실행
- `WebFetch` - 웹 페이지 가져오기
- `WebSearch` - 웹 검색
- `TodoWrite` - 작업 목록 관리
- `NotebookEdit` - Jupyter 노트북 편집
- `Task` - 서브 에이전트 호출

## 예제

### 새 스킬 생성

```
/manage-skill create code-review
```

**출력**:
```
스킬 'code-review' 생성을 시작합니다.

다음 정보를 입력해주세요:
1. 스킬 설명: 코드 리뷰를 수행하고 개선점을 제안합니다.
2. 인수 힌트: [file-path]
3. 사용 도구: Read, Grep, Glob

스킬이 생성되었습니다: .claude/skills/code-review/SKILL.md
```

### 스킬 목록 조회

```
/manage-skill list
```

**출력**:
```
현재 프로젝트의 스킬 목록:

| 스킬 이름 | 설명 | user-invocable |
|----------|------|----------------|
| manage-skill | 스킬 파일 관리 | true |
| diagram-generator | Mermaid 다이어그램 생성 | true |
| markdown-converter | PDF를 Markdown으로 변환 | true |

총 3개의 스킬이 있습니다.
```

### 스킬 검증

```
/manage-skill validate manage-skill
```

**출력**:
```
스킬 'manage-skill' 검증 결과:

[PASS] name: 유효한 kebab-case
[PASS] description: 존재함
[PASS] allowed-tools: 모든 도구 유효
[PASS] model: 유효한 모델

검증 통과: 모든 항목이 유효합니다.
```

## 관련 스킬

- [@skills/manage-claude-md/SKILL.md] - CLAUDE.md 파일 관리
- [@skills/manage-readme/SKILL.md] - README.md 파일 관리
- [@skills/manage-docs/SKILL.md] - 문서 통합 관리

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.2.0 | 템플릿에 category, skill-type, references, referenced-by 필드 추가. delete 액션 의존성 검사 도구 문서화 |
| 2026-01-21 | 1.1.0 | 전체 한국어화 (Instructions → 지침) |
| 2026-01-21 | 1.0.0 | 초기 생성 - create, edit, delete, list, validate 액션 지원 |

## Gotchas (실패 포인트)

- skill 이름 변경 시 `triggers:` 필드와 `name:` 필드 모두 수정 필요
- 동일 이름 skill이 전역과 프로젝트에 모두 있으면 프로젝트 우선 (의도 확인)
- SKILL.md description이 1024자 초과 시 시스템 프롬프트 비대화
- skill 삭제 후 참조 제거 누락 시 broken link
