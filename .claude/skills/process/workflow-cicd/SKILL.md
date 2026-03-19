---
name: workflow-cicd
triggers:
  - "workflow cicd"
description: "CI/CD 파이프라인(Continuous Integration/Delivery) 워크플로우 스킬. GitHub Actions, GitLab CI, 빌드/테스트/배포 자동화로 안전하고 빠른 배포 파이프라인을 구축한다."
argument-hint: "[플랫폼] - github-actions, gitlab-ci, deployment, rollback"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
model: claude-sonnet-4-6[1m]
context: |
  CI/CD 파이프라인 구축 및 배포 자동화 전략을 제공한다.
  코드 변경부터 프로덕션 배포까지의 전체 프로세스를 자동화한다.
agent: |
  CI/CD 전문가.
  GitHub Actions, GitLab CI, 배포 전략의 모범 사례를 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 워크플로우
skill-type: Atomic
references: []
referenced-by: []

---
# CI/CD 파이프라인 워크플로우

> GitHub Actions, GitLab CI로 빌드/테스트/배포를 자동화하는 CI/CD 파이프라인 구축 가이드

---

## 목적

- **자동화**: 코드 푸시부터 배포까지 수동 작업 제거
- **품질 보장**: 모든 변경에 대해 테스트 자동 실행
- **빠른 피드백**: 빌드 실패 즉시 알림
- **안전한 배포**: 단계별 승인 및 Rollback 메커니즘
- **환경 분리**: Dev → Staging → Prod 순차 배포

---

## 스킬 유형

**Composite Skill** - CI/CD 파이프라인 구축의 단계별 가이드

---

## 1. GitHub Actions 워크플로우

### 기본 구조

**.github/workflows/ci.yml** - 린트, 테스트, 빌드 자동화

**Jobs 구성**:
1. **lint**: Ruff + Mypy 검사
2. **test**: 단위 테스트 (Python 3.10-3.12)
3. **build**: Docker 이미지 빌드 (main 브랜치만)
4. **deploy**: 환경별 배포 (수동 승인)

**트리거**:
- `push`: main, develop 브랜치
- `pull_request`: main 브랜치
- `workflow_dispatch`: 수동 실행

**전체 예시**: [@templates/skill-examples/workflow-cicd/github-actions.yml]

### 주요 패턴

**Matrix Strategy** (다중 Python 버전):
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

**캐싱** (의존성 설치 속도 향상):
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**환경별 Secret 관리**:
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

---

## 2. GitLab CI/CD 파이프라인

### 기본 구조

**.gitlab-ci.yml** - Stage 기반 파이프라인

**Stages**:
1. **build**: 의존성 설치, 린트, 타입 체크
2. **test**: 단위 테스트, 통합 테스트
3. **package**: Docker 이미지 빌드
4. **deploy**: 환경별 배포 (dev → staging → prod)

**전체 예시**: [@templates/skill-examples/workflow-cicd/gitlab-ci.yml]

### 주요 패턴

**캐시 전략**:
```yaml
cache:
  paths:
    - .venv/
    - .cache/pip/
```

**서비스 컨테이너** (DB 테스트):
```yaml
services:
  - postgres:15
  - redis:7
```

**수동 배포 승인**:
```yaml
deploy:prod:
  when: manual
  only:
    - main
```

---

## 3. 배포 전략

### 환경별 배포 순서

```
1. Dev (자동) → 2. Staging (자동) → 3. Prod (수동 승인)
```

**Dev 환경**:
- 모든 PR merge 시 자동 배포
- 빠른 피드백, 실험 가능

**Staging 환경**:
- main 브랜치 푸시 시 자동 배포
- 프로덕션과 동일한 구성
- 최종 검증 단계

**Prod 환경**:
- 수동 승인 필수
- Rollback 준비 완료
- 모니터링 강화

### 배포 체크리스트

**배포 전**:
- [ ] 모든 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] 변경 사항 문서화
- [ ] Rollback 계획 수립

**배포 중**:
- [ ] Health check 확인
- [ ] 로그 모니터링
- [ ] 에러율 추적

**배포 후**:
- [ ] 기능 동작 확인
- [ ] 성능 메트릭 검증
- [ ] 사용자 피드백 수집

**체크리스트 상세**: [@templates/skill-examples/workflow-cicd/deployment-checklist.md]

---

## 4. Rollback 전략

### 즉시 Rollback

**트리거 조건**:
- 에러율 급증 (> 1%)
- 응답 시간 증가 (> 2초)
- Health check 실패

**GitHub Actions Rollback**:
```yaml
- name: Rollback on failure
  if: failure()
  run: |
    kubectl rollout undo deployment/{app-name}
```

**GitLab CI Rollback**:
```yaml
rollback:
  stage: deploy
  when: on_failure
  script:
    - kubectl rollout undo deployment/{app-name}
```

### Blue-Green 배포

**장점**:
- 즉시 전환 가능
- 다운타임 없음
- 안전한 Rollback

**단점**:
- 리소스 2배 필요
- 데이터베이스 마이그레이션 복잡

---

## 5. Secret 관리

### GitHub Secrets

**Repository → Settings → Secrets and variables → Actions**:
- `DATABASE_URL`
- `API_KEY`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

**환경별 Secrets**:
- Environments → dev/staging/prod
- 환경별로 다른 값 설정 가능

### GitLab CI/CD Variables

**Settings → CI/CD → Variables**:
- Masked: 로그에 숨김
- Protected: protected 브랜치에만 노출
- Environment scope: 환경별 다른 값

---

## 6. CI/CD 체크리스트

### 초기 설정

- [ ] `.github/workflows/ci.yml` 또는 `.gitlab-ci.yml` 생성
- [ ] Secret 변수 설정
- [ ] 환경별 배포 대상 설정
- [ ] Slack/Email 알림 연동

### 파이프라인 최적화

- [ ] 캐싱 설정 (의존성, 빌드 결과)
- [ ] 병렬 실행 활용 (lint + test 동시 실행)
- [ ] Matrix 전략으로 다중 환경 테스트
- [ ] Docker layer 캐싱

### 보안

- [ ] Secret 변수 사용 (하드코딩 금지)
- [ ] Pull request에서 Secret 노출 방지
- [ ] 이미지 스캔 (Trivy, Snyk)
- [ ] 의존성 취약점 검사 (Dependabot)

---

## 사용 예시

### GitHub Actions 기본 CI

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### GitLab CI 기본 파이프라인

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

**복잡한 예시**: [@templates/skill-examples/workflow-cicd/]

---

## 관련 스킬

| 스킬 | 관계 | 설명 |
|------|------|------|
| [@skills/setup-quality/SKILL.md] | 통합 | pre-commit hooks와 CI 연동 |
| [@skills/check-security/SKILL.md] | 통합 | CI에서 보안 검사 실행 |
| [@skills/convention-commit/SKILL.md] | 통합 | 커밋 메시지 검증 |

---

## 주의사항

1. **Secret 노출 방지**: 절대 하드코딩하지 말 것
2. **Protected 브랜치**: main 브랜치는 직접 푸시 금지, PR만 허용
3. **Timeout 설정**: 무한 대기 방지 (기본 60분)
4. **비용 최적화**: Self-hosted runner 고려 (대규모 프로젝트)

---

## 참고 자료

- GitHub Actions Docs: https://docs.github.com/en/actions
- GitLab CI/CD Docs: https://docs.gitlab.com/ee/ci/
- Kubernetes Deployment: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 2.0.0 | 2026-01-27 | 보수적 리팩토링 - 893줄 → 300줄. 템플릿 분리 |
| 1.0.0 | 2026-01-21 | 초기 생성 |
