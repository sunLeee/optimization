---
name: convention-environment-config
triggers:
  - "convention environment config"
description: "환경 설정(Environment Configuration) 컨벤션 참조 스킬. Dev/Staging/Prod 환경별 설정, 비밀 관리, 환경 변수로 안전하고 재현 가능한 배포 환경을 구축한다."
argument-hint: "[섹션] - environments, secrets, validation, 12-factor, all"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  환경별 설정 관리 및 비밀 보호 전략을 제공한다.
  12-Factor App 원칙을 따라 안전한 배포 환경을 구축한다.
agent: |
  환경 설정 전문가.
  환경 분리, 비밀 관리, 설정 검증의 모범 사례를 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 환경 설정(Environment Configuration) 컨벤션

Dev/Staging/Prod 환경별 설정, 비밀 관리, 환경 변수로 안전한 배포 환경을 구축하는 규칙.

## 목적

- **환경 분리**: Dev, Staging, Prod 환경별 독립적 설정
- **비밀 관리**: API 키, DB 비밀번호 등 민감 정보 보호
- **설정 검증**: 런타임 전 설정 유효성 확인
- **재현성**: 동일 설정으로 어디서나 실행 가능
- **12-Factor App**: 표준 원칙 준수로 이식성 확보

---

## 1. 환경별 설정 구조

### 1.1 기본 환경 정의

**Environment enum**: [@templates/skill-examples/convention-environment-config/environment-enum.py]

**핵심 환경 타입**:
- `DEVELOPMENT`: 로컬 개발 환경
- `STAGING`: 프로덕션 테스트 환경
- `PRODUCTION`: 실제 서비스 환경
- `TEST`: CI/CD 테스트 환경

### 1.2 환경별 설정 파일 구조

```
config/
├── .env.development      # Dev 환경 (로컬)
├── .env.staging          # Staging 환경
├── .env.production       # Prod 환경 (민감 정보 제외)
├── .env.test             # Test 환경 (CI/CD)
├── config.yaml           # 공통 설정 (비밀 제외)
└── schemas/              # 설정 검증 스키마
    └── config_schema.py
```

**규칙**:
- `.env.*` 파일은 `.gitignore`에 추가 (비밀 노출 방지)
- `config.yaml`은 버전 관리 (공개 정보만)
- Staging/Prod 환경 변수는 CI/CD 시스템에서 주입

---

## 2. 환경 변수 관리

### 2.1 python-dotenv 사용

**환경 변수 로드 함수**: [@templates/skill-examples/convention-environment-config/dotenv-loader.py]

**핵심 로직**:
1. 환경별 `.env.{environment}` 파일 경로 구성
2. 파일 존재 확인 및 load_dotenv 실행
3. 파일 없을 시 시스템 환경 변수 사용

### 2.2 .env 파일 예시

**.env 파일 템플릿**: [@templates/skill-examples/convention-environment-config/docker-k8s-examples.md]

**차이점**:
- Development: DEBUG=true, 로컬 DB URL, 가짜 AWS 키
- Production: DEBUG=false, Secrets Manager 주입, 풀 크기 확대

---

## 3. 비밀 관리

### 3.1 AWS Secrets Manager 통합

**AWS 비밀 로드**: [@templates/skill-examples/convention-environment-config/aws-secrets.py]

**핵심 함수**:
- `load_secrets_from_aws()`: boto3로 Secrets Manager 조회
- `inject_secrets_to_env()`: 비밀을 환경 변수로 주입 (값 마스킹)

### 3.2 HashiCorp Vault 통합

**Vault 비밀 로드**: [@templates/skill-examples/convention-environment-config/vault-secrets.py]

**핵심 함수**:
- `load_secrets_from_vault()`: hvac 클라이언트로 KV v2 secret 조회
- data.data에서 실제 비밀 추출

---

## 4. 설정 검증 (Pydantic)

### 4.1 Pydantic BaseSettings

**설정 모델 정의**: [@templates/skill-examples/convention-environment-config/pydantic-settings.py]

**핵심 기능**:
- 환경 변수 자동 로드 (.env 파일 지원)
- Field 검증 (타입, 범위, 길이)
- @field_validator로 커스텀 검증
- ValidationError 시 상세 오류 출력

---

## 5. 환경별 동작 제어

### 5.1 환경별 조건부 실행

**환경별 앱 설정**: [@templates/skill-examples/convention-environment-config/environment-control.py]

**핵심 함수**:
- `configure_app_for_environment()`: 환경별 로깅 레벨 설정
- `is_feature_enabled()`: 환경별 피처 플래그 제어

---

## 6. 12-Factor App 원칙

### 6.1 핵심 원칙 체크리스트

| # | 원칙 | 설명 | 구현 |
|---|------|------|------|
| 1 | **Codebase** | 하나의 코드베이스, 여러 배포 | Git ✅ |
| 2 | **Dependencies** | 명시적 의존성 선언 | requirements.txt ✅ |
| 3 | **Config** | 환경 변수로 설정 분리 | .env ✅ |
| 4 | **Backing Services** | 외부 서비스는 리소스로 취급 | DATABASE_URL ✅ |
| 5 | **Build/Release/Run** | 빌드, 릴리스, 실행 분리 | CI/CD ✅ |
| 6 | **Processes** | 무상태 프로세스 | Stateless ✅ |
| 7 | **Port Binding** | 포트 바인딩으로 서비스 노출 | PORT ✅ |
| 8 | **Concurrency** | 프로세스 모델로 확장 | Gunicorn ✅ |
| 9 | **Disposability** | 빠른 시작/종료 | Graceful shutdown ✅ |
| 10 | **Dev/Prod Parity** | 개발과 프로덕션 환경 최소 차이 | Docker ✅ |
| 11 | **Logs** | 로그를 이벤트 스트림으로 취급 | stdout ✅ |
| 12 | **Admin Processes** | 관리 작업을 일회성 프로세스로 실행 | CLI ✅ |

### 6.2 Config (III) 구현 예제

12-Factor App의 Config 원칙 구현은 종합 예제를 참조하세요.

---

## 7. 종합 예제: 프로덕션 앱 초기화

**앱 초기화 종합 예제**: [@templates/skill-examples/convention-environment-config/app-init.py]

**초기화 단계 (7단계)**:
1. 현재 환경 감지 (`get_current_environment()`)
2. 환경별 .env 파일 로드
3. AWS Secrets Manager에서 비밀 주입 (프로덕션만)
4. Pydantic으로 설정 검증
5. 환경별 앱 설정 조정
6. DB, Redis 연결 초기화
7. 초기화 완료 로깅

---

## 8. 환경 설정 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] 환경 타입 정의 (Dev/Staging/Prod/Test)
- [ ] .env 파일 생성 (환경별)
- [ ] .gitignore에 .env.* 추가
- [ ] python-dotenv 설치 및 로드 코드
- [ ] Pydantic BaseSettings 정의
- [ ] 필수 환경 변수 검증
- [ ] 비밀 관리 (AWS Secrets Manager 또는 Vault)
- [ ] 환경별 동작 제어 (디버그, 로그 레벨)
- [ ] 12-Factor App 원칙 준수
- [ ] 설정 문서화 (README.md에 필수 환경 변수 나열)
- [ ] 프로덕션 배포 시 비밀 주입 테스트

---

## 9. 외부 도구

**Docker & Kubernetes 예시**: [@templates/skill-examples/convention-environment-config/docker-k8s-examples.md]

**지원 도구**:
- Docker Compose: 환경별 서비스 분리
- Kubernetes: ConfigMap + Secret 관리

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-config/SKILL.md] | OmegaConf + Pydantic 설정 |
| [@skills/convention-security-hardening/SKILL.md] | 비밀 보호 |
| [@skills/convention-data-validation/SKILL.md] | 설정 검증 |
| [@skills/workflow-cicd/SKILL.md] | CI/CD에서 환경 변수 주입 |

---

## 참고

- 12-Factor App: https://12factor.net/
- python-dotenv: https://github.com/theskumar/python-dotenv
- Pydantic Settings: https://docs.pydantic.dev/latest/usage/settings/
- AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
- HashiCorp Vault: https://www.vaultproject.io/

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | 보수적 리팩토링 - 834→394줄. Python 코드 예시를 템플릿으로 분리 |
| 2026-01-21 | 1.0.0 | 초기 생성 - 환경 분리, 비밀 관리, 12-Factor |

## Gotchas (실패 포인트)

- 환경 변수 없으면 즉시 실패 대신 기본값으로 동작하다 나중에 발견하는 경우
- dev/staging/prod 환경별 변수가 혼재하면 배포 시 prod에 dev 값 적용 위험
- `os.getenv('KEY')` 사용 시 None 반환 — 반드시 기본값 또는 예외 처리
- 비밀값을 코드에 하드코딩 후 git에 commit — 영구 기록
