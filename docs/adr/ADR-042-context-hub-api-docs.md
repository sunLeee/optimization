# ADR-042: context-hub 방식 API 문서 조회 (get-api-docs skill)

- **상태**: Accepted
- **날짜**: 2026-03-19
- **범용 여부**: ✅ 모든 프로젝트 적용 가능

## 맥락

Claude 등 LLM은 외부 SDK/라이브러리 API를 hallucination하는 경향이 있다.
특히 자주 변경되는 라이브러리(pydantic v2, google-adk 등)에서 오래된 API 시그니처를
사용하여 코드 오류를 유발한다.

context-hub(Andrew Ng, 2026)은 CLI를 통해 curated, versioned API 문서를 에이전트에게 제공하는
방식으로 이 문제를 해결했다. 우리는 이 아이디어를 `get-api-docs` skill로 내재화한다.

## 결정

새로운 외부 SDK/라이브러리 사용 전에 `get-api-docs` skill을 실행하여
공식 문서를 `.omc/research/{library}-api-docs.md`에 저장하고 이를 구현 컨텍스트로 참조한다.

## 이유

- **Hallucination 방지**: 공식 문서 직접 조회로 오래된 API 패턴 사용 방지
- **세션 간 지속성**: `.omc/research/`에 저장하여 재사용 가능
- **document-specialist 통합**: 기존 에이전트 체인에 자연스럽게 통합
- **내부망 호환**: document-specialist → WebFetch fallback으로 네트워크 제한 대응

## 대안 검토

| 대안 | 거부 이유 |
|------|----------|
| chub CLI 직접 설치 | npm 글로벌 설치 필요, 내부망 npm 제한 가능성 |
| LLM 기본 지식에 의존 | Hallucination 위험, 구버전 API 패턴 사용 |
| 매번 WebFetch 직접 호출 | skill로 추상화되지 않아 일관성 없음 |

## 결과

- `get-api-docs` skill: `.claude/skills/reference/adk/get-api-docs/SKILL.md`
- 사용 패턴: SDK 첫 사용 시 `document-specialist` 투입 (agents.md § 5 참조)
- 저장 위치: `.omc/research/{library}-api-docs.md`

## Gotchas

- 내부망 SSL 제한 환경: `NODE_TLS_REJECT_UNAUTHORIZED=0` + Gemini CLI 활용
- 캐시 유효기간: `.omc/research/` 파일은 라이브러리 버전 업 시 재조회 필요

## 참조

- [context-hub](https://github.com/andrewyng/context-hub)
- [get-api-docs SKILL.md](./../../../skills/reference/adk/get-api-docs/SKILL.md)
- [agents.md](../agents.md) § 4. 전문 에이전트 chain 구성
