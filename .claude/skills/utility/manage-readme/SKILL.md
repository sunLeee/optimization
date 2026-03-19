---
name: manage-readme
triggers:
  - "manage readme"
description: README.md 생성 및 업데이트를 관리하며 프로젝트 타입을 자동 감지한다. 사용자가 "README 생성", "README 업데이트" 등을 요청할 때 사용한다. 호출 컨텍스트: - Composite: project-init에서 자동 호출됨 - 단독 사용: README만 업데이트할 때 직접 호출
argument-hint: "[action|type] - generate, update, validate, interactive, python, nodejs, go, rust, java, auto"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Edit
  - Write
  - Bash
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: 프로젝트 루트의 README.md 파일을 관리한다. 프로젝트 타입을 자동 감지하여 적절한 템플릿을 적용한다.
agent: README 문서화 전문가. 프로젝트 구조를 분석하고 표준 형식의 README.md를 생성/업데이트한다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 관리
skill-type: Atomic
references: []
referenced-by:
  - "@skills/manage-docs/SKILL.md"
  - "@skills/project-init/SKILL.md"
  - "@skills/scaffold-structure/SKILL.md"

---
# README 관리 스킬

프로젝트의 README.md 생성 및 업데이트를 관리하는 스킬. 프로젝트 타입을 자동 감지하고 템플릿을 그에 맞게 조정한다.

## 기능

- 처음부터 새로운 README.md 파일 생성
- 기존 README.md 파일 업데이트 (커스텀 내용 보존)
- 프로젝트 타입 자동 감지 (Node.js, Python, Go, Rust, Java 등)
- 모든 표준 문서화 섹션 포함
- Changelog 섹션 유지

## 사용법

### 기본 사용 (자동 감지)

```bash
/manage-readme                    # README 생성 또는 업데이트
/manage-readme generate           # 새 README 강제 생성
/manage-readme update             # 기존 README 병합 업데이트
/manage-readme validate           # README 구조 검증
```

### 대화형 사용

```bash
/manage-readme interactive        # 대화형 모드 (단계별 질문)
```

**대화형 모드 프로세스**:
1. 프로젝트 타입 선택 (자동 감지 실패 시)
2. 프로젝트 이름 입력
3. 간단 설명 입력
4. 라이선스 선택
5. 추가 섹션 선택 (API 문서, 배포 가이드 등)
6. README 생성 및 검증

### 타입 직접 지정 (수동 선택)

```bash
/manage-readme python             # Python 템플릿 강제 적용
/manage-readme nodejs             # Node.js 템플릿
/manage-readme go                 # Go 템플릿
/manage-readme rust               # Rust 템플릿
/manage-readme java               # Java 템플릿
```

**중요**: 타입 지정 시 자동 감지를 건너뛰고 해당 템플릿을 바로 적용합니다.

## Quick Reference (빠른 참조)

### 1분 요약

**자동 감지되는 프로젝트 타입**:
- Node.js (`package.json`)
- Python (`pyproject.toml`, `requirements.txt`)
- Go (`go.mod`)
- Rust (`Cargo.toml`)
- Java (`pom.xml`, `build.gradle`)

**필수 섹션**:
1. 설명, 2. 설치, 3. 사용법, 4. 설정, 5. 테스트, 6. 기여, 7. 변경이력, 8. 라이선스

**빠른 명령어**:
```bash
/manage-readme              # 자동 감지 후 생성/업데이트
/manage-readme interactive  # 대화형 모드
/manage-readme python       # Python 템플릿 강제 적용
/manage-readme validate     # 현재 README 검증만
```

**언어별 템플릿 바로가기**:
- [Node.js / TypeScript](#nodejs--javascript--typescript-템플릿)
- [Python](#python-템플릿)
- [Go](#go-템플릿)
- [Rust](#rust-템플릿)
- [Java (Maven)](#java-maven-템플릿)

---

## 프로세스

이 스킬이 호출되면 다음 단계를 따른다:

### 1단계: 프로젝트 타입 감지 (자동 + 대화형)

**자동 감지 시도**:

프로젝트 루트의 설정 파일을 스캔하여 프로젝트 타입을 결정한다:

| 파일 | 프로젝트 타입 | 우선순위 |
|------|--------------|:--------:|
| `package.json` | Node.js / JavaScript / TypeScript | 1 |
| `pyproject.toml`, `requirements.txt`, `setup.py` | Python | 2 |
| `go.mod` | Go | 3 |
| `Cargo.toml` | Rust | 4 |
| `pom.xml`, `build.gradle` | Java | 5 |
| `Gemfile` | Ruby | 6 |
| `composer.json` | PHP | 7 |
| `*.csproj`, `*.sln` | .NET / C# | 8 |

**여러 파일 발견 시**: 우선순위가 높은 타입 선택 (예: `package.json`과 `pyproject.toml`이 모두 있으면 Node.js 선택)

**자동 감지 실패 시 (대화형 모드)**:

AskUserQuestion으로 사용자에게 타입 직접 선택 요청:

```yaml
AskUserQuestion:
  questions:
    - question: "프로젝트 타입을 선택해주세요"
      header: "프로젝트 타입"
      multiSelect: false
      options:
        - label: "Node.js / JavaScript / TypeScript (권장)"
          description: "npm, yarn, pnpm 사용"
        - label: "Python"
          description: "pip, poetry, uv 사용"
        - label: "Go"
          description: "go.mod 기반"
        - label: "Rust"
          description: "Cargo.toml 기반"
        - label: "Java (Maven)"
          description: "pom.xml 또는 build.gradle"
```

### 2단계: 프로젝트 메타데이터 추출

감지된 프로젝트 타입을 기반으로 다음 정보를 추출한다:

- 프로젝트 이름
- 버전
- 설명
- 작성자/유지보수자
- 라이선스
- 의존성
- 스크립트/명령어

### 3단계: README 생성 또는 업데이트

감지된 프로젝트 타입에 맞게 명령어와 예시를 조정하여 다음 템플릿 구조를 사용한다:

```markdown
# {프로젝트 이름}

{프로젝트 간단 설명}

## 목차

- [설명](#설명)
- [설치](#설치)
- [사용법](#사용법)
- [설정](#설정)
- [테스트](#테스트)
- [기여](#기여)
- [변경 이력](#변경-이력)
- [라이선스](#라이선스)

## 설명

{프로젝트의 상세 설명, 목적, 주요 기능}

## 설치

### 사전 요구사항

{프로젝트 타입에 따른 사전 요구사항 목록}

### 설정

{프로젝트 타입에 따른 설치 명령어}

## 사용법

{사용 예시 및 명령어}

### 기본 예시

{프로젝트 타입에 적합한 코드 예시}

## 설정

{설정 옵션, 환경 변수, 설정 파일}

### 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| {변수명} | {설명} | {기본값} |

### 설정 파일

{적용 가능한 경우 설정 파일 설명}

## 테스트

{프로젝트 타입에 따른 테스트 안내}

### 테스트 실행

{테스트 명령어}

### 테스트 커버리지

{적용 가능한 경우 커버리지 리포트 안내}

## 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/멋진-기능`)
3. 변경사항 커밋 (`git commit -m '멋진 기능 추가'`)
4. 브랜치에 푸시 (`git push origin feature/멋진-기능`)
5. Pull Request 생성

### 개발 환경 설정

{개발 환경 설정 안내}

### 코드 스타일

{코드 스타일 가이드라인 및 린팅 정보}

## 변경 이력

### [미배포]

- 초기 배포 준비

### [1.0.0] - YYYY-MM-DD

#### 추가
- 초기 프로젝트 설정
- 핵심 기능

#### 변경
- 해당 없음

#### 수정
- 해당 없음

## 라이선스

{LICENSE 파일 또는 패키지 메타데이터에서 감지한 라이선스 정보}
```

### 4단계: 프로젝트별 템플릿 적용

## 프로젝트별 템플릿

### Node.js / JavaScript / TypeScript 템플릿

```markdown
## 설치

\`\`\`bash
npm install
# 또는
yarn install
# 또는
pnpm install
\`\`\`

## 사용법

\`\`\`bash
npm start
# 또는
npm run dev
\`\`\`

## 테스트

\`\`\`bash
npm test
npm run test:coverage
\`\`\`
```

### Python 템플릿

```markdown
## 설치

\`\`\`bash
pip install -r requirements.txt
# 또는 poetry 사용
poetry install
# 또는 pip 사용
pip install .
\`\`\`

## 사용법

\`\`\`bash
python main.py
# 또는
python -m {패키지명}
\`\`\`

## 테스트

\`\`\`bash
pytest
pytest --cov={패키지명}
\`\`\`
```

### Go 템플릿

```markdown
## 설치

\`\`\`bash
go mod download
go build
\`\`\`

## 사용법

\`\`\`bash
go run main.go
# 또는
./{바이너리명}
\`\`\`

## 테스트

\`\`\`bash
go test ./...
go test -cover ./...
\`\`\`
```

### Rust 템플릿

```markdown
## 설치

\`\`\`bash
cargo build
cargo build --release
\`\`\`

## 사용법

\`\`\`bash
cargo run
# 또는
./target/release/{바이너리명}
\`\`\`

## 테스트

\`\`\`bash
cargo test
cargo test -- --nocapture
\`\`\`
```

### Java (Maven) 템플릿

```markdown
## 설치

\`\`\`bash
mvn install
mvn package
\`\`\`

## 사용법

\`\`\`bash
mvn exec:java
# 또는
java -jar target/{아티팩트}.jar
\`\`\`

## 테스트

\`\`\`bash
mvn test
mvn verify
\`\`\`
```

### 5단계: 커스텀 내용 보존 규칙

기존 README 업데이트 시 다음 규칙으로 병합합니다:

**보존 우선순위**:
1. **사용자 작성 내용 우선**: 템플릿과 다른 내용이 있으면 보존
2. **섹션 제목 표준화**: 제목은 템플릿 형식으로 통일 (`## Install` → `## 설치`)
3. **누락 섹션 추가**: 템플릿에 있으나 기존 README에 없는 섹션만 추가
4. **메타데이터 자동 업데이트**: 버전, 의존성은 package.json/pyproject.toml 기준으로 갱신

**병합 예시**:

| 기존 README | 템플릿 | 최종 결과 | 이유 |
|-------------|--------|----------|------|
| `## Install` | `## 설치` | `## 설치` (기존 내용 보존) | 제목만 표준화 |
| 섹션 없음 | `## 테스트` | `## 테스트` (템플릿 추가) | 누락 섹션 추가 |
| `version: 1.0.0` | `version: 1.2.0` | `version: 1.2.0` | 메타데이터 갱신 |
| 사용자 작성 설명 | 템플릿 설명 | 사용자 작성 보존 | 커스텀 우선 |

**플레이스홀더 처리**:
- 기존 README에 `{프로젝트명}` 같은 플레이스홀더가 있으면 package.json에서 자동 대체
- 사용자가 작성한 내용은 절대 덮어쓰지 않음

**병합 프로세스**:
1. 기존 README를 섹션별로 파싱
2. 보존해야 할 커스텀 내용 식별
3. 템플릿 업데이트와 기존 커스텀 내용 병합
4. 누락된 새 섹션 추가
5. 메타데이터 기반 내용 업데이트 (버전, 의존성)

### 6단계: README 자동 검증

`/manage-readme validate` 실행 시 다음 항목을 자동 검사합니다:

**1. 구조 검증**:
- [ ] 8개 필수 섹션 존재 여부 (설명, 설치, 사용법, 설정, 테스트, 기여, 변경이력, 라이선스)
- [ ] 목차 링크가 실제 섹션과 일치하는지 검사

**2. 내용 검증**:
- [ ] 코드 블록에 언어 지정자 있는지 (`bash`, `python` 등)
- [ ] 플레이스홀더 텍스트 남아있는지 (`{프로젝트명}`, `{설명}`)
- [ ] 깨진 내부 링크 존재 여부

**3. 메타데이터 검증**:
- [ ] LICENSE 파일과 라이선스 섹션 일치 여부
- [ ] package.json/pyproject.toml 버전과 Changelog 버전 일치

**검증 실패 시 경고 출력**:

```bash
⚠️ 플레이스홀더 발견: 23줄 "{프로젝트명}" → 실제 이름으로 대체 필요
⚠️ 코드 블록 언어 누락: 45줄 - 언어 지정자 추가 권장
⚠️ 깨진 링크: 67줄 [API 문서](docs/api.md) - 파일 없음
✅ 목차와 실제 섹션 일치
✅ 라이선스 정보 정확함 (MIT)
```

**검증 성공 시**:
```bash
✅ README.md 검증 완료
- 필수 섹션: 8/8 통과
- 코드 블록: 15/15 언어 지정자 있음
- 링크: 12/12 유효
- 메타데이터: 일치
```

---

## 대화형 모드 (Interactive Mode)

`/manage-readme interactive` 실행 시 단계별로 질문하며 README를 생성합니다.

### 프로세스

```
/manage-readme interactive
    |
    v
[Step 1] 프로젝트 타입 감지/선택
    |-- 자동 감지 성공 시 확인 요청
    |-- 자동 감지 실패 시 AskUserQuestion
    |
    v
[Step 2] 프로젝트 메타데이터 입력
    |-- 프로젝트 이름
    |-- 간단 설명
    |-- 작성자 (Git 설정에서 자동 추출 가능)
    |
    v
[Step 3] 라이선스 선택
    |-- MIT, Apache 2.0, GPL-3.0, Proprietary
    |-- LICENSE 파일 자동 생성 여부
    |
    v
[Step 4] 추가 섹션 선택 (multiSelect)
    |-- API 문서
    |-- 배포 가이드
    |-- 트러블슈팅
    |-- FAQ
    |-- 성능 벤치마크
    |
    v
[Step 5] README 생성
    |-- 입력 정보 기반 템플릿 생성
    |-- 선택한 추가 섹션 포함
    |
    v
[Step 6] 자동 검증 실행
    |-- validate 로직 실행
    |-- 경고 발생 시 수정 제안
    |
    v
완료 보고
```

### AskUserQuestion 예시

**Step 2 - 프로젝트 메타데이터**:

```yaml
AskUserQuestion:
  questions:
    - question: "프로젝트 이름을 입력해주세요"
      header: "프로젝트 이름"
      options:
        - label: "package.json에서 자동 추출 (권장)"
          description: "현재: my-awesome-project"
        - label: "직접 입력"
          description: "새 이름 입력"
```

**Step 3 - 라이선스 선택**:

```yaml
AskUserQuestion:
  questions:
    - question: "라이선스를 선택해주세요"
      header: "라이선스"
      multiSelect: false
      options:
        - label: "MIT (권장)"
          description: "가장 자유로운 오픈소스 라이선스"
        - label: "Apache 2.0"
          description: "특허 보호 포함"
        - label: "GPL-3.0"
          description: "카피레프트 라이선스"
        - label: "Proprietary"
          description: "비공개 프로젝트"
```

**Step 4 - 추가 섹션**:

```yaml
AskUserQuestion:
  questions:
    - question: "추가할 섹션을 선택해주세요"
      header: "추가 섹션"
      multiSelect: true
      options:
        - label: "API 문서"
          description: "API 엔드포인트 문서 섹션"
        - label: "배포 가이드"
          description: "프로덕션 배포 안내"
        - label: "트러블슈팅"
          description: "자주 발생하는 문제 해결"
        - label: "FAQ"
          description: "자주 묻는 질문"
```

### 대화형 모드 출력 예시

```
=== README 대화형 생성 ===

[1/6] 프로젝트 타입 감지...
✅ Node.js 프로젝트 감지됨 (package.json)

[2/6] 프로젝트 메타데이터 입력...
→ 프로젝트 이름을 입력해주세요

User: package.json에서 자동 추출 (권장)

✅ 프로젝트명: my-awesome-api
✅ 설명: A RESTful API for awesome things

[3/6] 라이선스 선택...
→ 라이선스를 선택해주세요

User: MIT (권장)

✅ MIT 라이선스 선택됨

[4/6] 추가 섹션 선택...
→ 추가할 섹션을 선택해주세요

User: API 문서, 배포 가이드

✅ 2개 추가 섹션 선택됨

[5/6] README 생성 중...
✅ README.md 생성 완료

[6/6] 자동 검증 실행...
✅ 필수 섹션: 8/8 통과
✅ 코드 블록: 12/12 언어 지정자 있음
✅ 링크: 5/5 유효

=== 완료 ===

생성된 README.md:
- 기본 섹션: 8개
- 추가 섹션: 2개 (API 문서, 배포 가이드)
- 라이선스: MIT
- 검증: 통과
```

---

## 출력

실행 후 이 스킬은:

1. 프로젝트 루트에 `README.md` 생성 또는 업데이트
2. 추가, 업데이트, 보존된 섹션 보고
3. 개선을 위한 경고 또는 제안 목록 출력
4. (대화형 모드 시) 자동 검증 결과 출력

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/manage-claude-md/SKILL.md] | CLAUDE.md 파일 관리 |
| [@skills/manage-docs/SKILL.md] | 문서 통합 관리 |
| [@skills/project-init/SKILL.md] | 프로젝트 초기화 시 README 자동 생성 |

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 2.0.0 | 사용성 개선 - Quick Reference, 대화형 모드, 프로젝트 타입 수동 선택, 검증 로직 구체화, 보존 규칙 명확화 |
| 2026-01-21 | 1.1.0 | 한국어화 |
| 2026-01-21 | 1.0.0 | 초기 생성 |
