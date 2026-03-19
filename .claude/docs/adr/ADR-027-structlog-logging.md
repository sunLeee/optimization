# ADR-027: 운영 서비스에 structlog 채택

- **상태**: Accepted
- **날짜**: 2026-03-19

## 결정
운영 서비스: structlog. 단순 스크립트: Python 표준 logging.

## 이유
- JSON 로그 → 로그 분석 도구와 연동 용이
- Context binding → 요청 ID 추적
- 이벤트 기반 구조화 → AI 파싱 용이

## Gotchas
- f-string in logger 절대 금지: `logger.info(f'...')` → 성능 저하
- 개인정보(email, user_id 전체) 로그 금지
- python-backend.md rule에 structlog 명시됨
