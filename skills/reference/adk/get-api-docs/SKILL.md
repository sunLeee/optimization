---
name: get-api-docs
description: 외부 SDK/라이브러리 공식 문서를 직접 조회하여 hallucination을 방지한다. context-hub 방식으로 최신 API 시그니처를 가져온다.
triggers:
  - "API 문서 가져와"
  - "get api docs"
  - "공식 문서 조회"
  - "SDK 문서 확인"
  - "hallucination 방지"
category: reference
subcategory: adk
version: "1.0"
author: team
---

# get-api-docs

외부 SDK/라이브러리 사용 전 공식 문서를 조회하여 hallucination을 방지한다.
context-hub(Andrew Ng, 2026) 방식에서 영감을 받아, 로컬 document-specialist agent가 공식 docs를 직접 읽어온다.

## 동작 방식

1. 인자로 패키지명 수신 (예: `fastapi`, `pydantic`, `google-adk`)
2. `document-specialist` agent에게 공식 docs URL 전달
3. 핵심 API 시그니처 + 예제 추출
4. `.omc/research/{library}-api-docs.md`에 저장
5. 이후 구현 시 해당 파일을 컨텍스트로 참조

## 사용법

```
/get-api-docs fastapi
/get-api-docs "google.adk.agents"
/get-api-docs pydantic --version 2.0
```

## Gotchas

- 내부망 환경에서 PyPI JSON API 직접 호출 실패 시: 공식 docs URL을 수동으로 지정
- `document-specialist` agent가 없는 경우: `WebFetch`로 직접 조회
- 캐시된 결과는 `.omc/research/`에 저장되므로 재실행 시 재사용 가능
- 항상 `document-specialist`로 먼저 시도 → 실패 시 `WebFetch` fallback

## 레퍼런스

- context-hub (Andrew Ng): https://github.com/andrewyng/context-hub
- ADR-042: .claude/docs/adr/ADR-042-context-hub-api-docs.md
