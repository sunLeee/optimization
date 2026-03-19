---
name: ref-url-fetcher
triggers:
  - "ref url fetcher"
description: URL 콘텐츠를 가져와 마크다운으로 변환한다. 웹 페이지, 문서, API 문서를 레퍼런스로 저장한다.
argument-hint: "[url] - 수집할 URL"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - WebFetch
  - Write
  - Read
model: claude-sonnet-4-6[1m]
context: URL 콘텐츠 수집 스킬이다. WebFetch로 페이지 내용을 가져와 마크다운으로 정리한다.
agent: 당신은 웹 콘텐츠 큐레이터입니다. 웹 페이지에서 핵심 내용을 추출하고 정리합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 레퍼런스/시나리오
skill-type: Atomic
references: []
referenced-by:
  - "@skills/prd-workflow/SKILL.md"
  - "@skills/ref-workflow/SKILL.md"

---
# ref-url-fetcher

URL 콘텐츠를 마크다운으로 변환하는 스킬.

## 목적

- 웹 페이지 콘텐츠 수집
- HTML을 마크다운으로 변환
- 기술 문서 레퍼런스화

## 사용법

```
/ref-url-fetcher https://fastapi.tiangolo.com/tutorial/security/
/ref-url-fetcher https://docs.python.org/3/library/asyncio.html
```

## 프로세스

```
/ref-url-fetcher [url]
    |
    v
[Step 1] URL 검증
    |-- URL 형식 확인
    |-- 접근 가능 여부 확인
    |
    v
[Step 2] WebFetch 실행
    |-- 페이지 콘텐츠 수집
    |-- HTML → Markdown 변환
    |
    v
[Step 3] 콘텐츠 정리
    |-- 불필요한 요소 제거 (광고, 네비게이션)
    |-- 핵심 콘텐츠 추출
    |
    v
[Step 4] 메타데이터 추가
    |-- 원본 URL
    |-- 수집 날짜
    |-- 페이지 제목
    |
    v
[Step 5] 파일 저장
    |-- docs/references/external/{domain}-{slug}.md
    |
    v
완료
```

## 출력 템플릿

```markdown
# {페이지 제목}

> **URL**: {url}
>
> **도메인**: {domain}
>
> **수집일**: {YYYY-MM-DD}

---

## 콘텐츠

{추출된 마크다운 콘텐츠}

---

## 참고

- 원본: [{url}]({url})
- 수집 날짜: {date}
```

## 예제

```
User: /ref-url-fetcher https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Claude:
=== URL 콘텐츠 수집 ===

URL: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

[1/3] WebFetch 실행 중...
  - 페이지 로드 완료
  - 콘텐츠 추출 중

[2/3] 마크다운 변환 중...
  - 코드 블록: 12개
  - 헤딩: 8개
  - 리스트: 5개

[3/3] 파일 저장...

=== 완료 ===

파일: docs/references/external/fastapi-oauth2-jwt.md

### 주요 내용
- OAuth2 with Password flow
- JWT 토큰 생성
- Depends를 이용한 인증 주입
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/ref-web-search/SKILL.md] | 선행 | 검색 후 상세 URL 수집 |
| [@skills/markdown-converter/SKILL.md] | 유사 | 범용 마크다운 변환 |
| [@skills/prd-workflow/SKILL.md] | 부모 | 레퍼런스 수집 단계 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |
