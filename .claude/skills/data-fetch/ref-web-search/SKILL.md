---
name: ref-web-search
triggers:
  - "ref web search"
description: 웹 검색을 수행하고 결과를 마크다운으로 저장한다. 기술 레퍼런스 수집을 자동화한다.
argument-hint: "[query] - 검색 쿼리"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - WebSearch
  - Write
  - Read
model: claude-sonnet-4-6[1m]
context: 웹 검색 레퍼런스 수집 스킬이다. 검색 결과를 정리하여 docs/references/에 저장한다.
agent: 당신은 기술 리서처입니다. 관련성 높은 정보를 선별하고 체계적으로 정리합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 레퍼런스/시나리오
skill-type: Atomic
references:
  - "@skills/ref-url-fetcher/SKILL.md"
referenced-by:
  - "@skills/prd-workflow/SKILL.md"
  - "@skills/ref-workflow/SKILL.md"

---
# ref-web-search

웹 검색을 수행하고 결과를 마크다운으로 저장하는 스킬.

## 목적

- 웹 검색 자동화
- 검색 결과 정리 및 저장
- 기술 레퍼런스 수집

## 사용법

```
/ref-web-search "FastAPI authentication best practices 2026"
/ref-web-search "Python async patterns" --domain stackoverflow.com
```

## 프로세스

```
/ref-web-search [query]
    |
    v
[Step 1] WebSearch 실행
    |-- 검색 쿼리 실행
    |-- 결과 수집
    |
    v
[Step 2] 결과 필터링
    |-- 관련성 높은 결과 선별 (상위 5-10개)
    |-- 중복 제거
    |
    v
[Step 3] 마크다운 변환
    |-- 구조화된 형식으로 정리
    |-- 소스 URL 기록
    |
    v
[Step 4] 파일 저장
    |-- docs/references/search-{query-slug}.md
    |
    v
완료
```

## 출력 템플릿

```markdown
# {검색 쿼리} - 웹 검색 결과

> **검색일**: {YYYY-MM-DD}
>
> **쿼리**: {query}

---

## 검색 결과 요약

{AI 생성 요약 - 핵심 인사이트 3-5줄}

---

## 상세 결과

### 1. {제목 1}
- **URL**: {url}
- **발췌**: {snippet}
- **관련성**: 높음

### 2. {제목 2}
- **URL**: {url}
- **발췌**: {snippet}
- **관련성**: 높음

...

---

## 핵심 인사이트

- {인사이트 1}
- {인사이트 2}
- {인사이트 3}

---

## 참고 자료

- [{제목 1}]({url1})
- [{제목 2}]({url2})
```

## 예제

```
User: /ref-web-search "FastAPI JWT authentication 2026"

Claude:
=== 웹 검색 실행 ===

쿼리: "FastAPI JWT authentication 2026"

[1/3] WebSearch 실행 중...
  - 10개 결과 수집

[2/3] 결과 분석 중...
  - 관련성 높은 결과: 7개
  - 기술 문서: 4개
  - 튜토리얼: 2개
  - Stack Overflow: 1개

[3/3] 문서 생성 중...

=== 완료 ===

파일: docs/references/search-fastapi-jwt-authentication.md

### 핵심 인사이트

1. python-jose 대신 PyJWT 권장 (보안 업데이트)
2. OAuth2PasswordBearer + Depends 패턴 표준
3. 토큰 갱신은 별도 엔드포인트 권장

다음 단계: /ref-url-fetcher로 상세 문서 수집
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/ref-url-fetcher/SKILL.md] | 관련 | 특정 URL 상세 수집 |
| [@skills/prd-workflow/SKILL.md] | 부모 | 레퍼런스 수집 단계 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |
