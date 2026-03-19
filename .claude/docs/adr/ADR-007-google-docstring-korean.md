# ADR-007: Google 스타일 Docstring + 한국어 + Logics 섹션

- **상태**: Accepted
- **날짜**: 2026-03-19

## 맥락
Docstring 스타일 통일 필요. 팀 언어가 한국어이므로 한국어 docstring이 이해도 높음.

## 결정
Google Style Docstring + 한국어 작성 + `Logics:` 섹션 필수.
- 첫 줄 설명: **73자 이하**
- AI가 처리 순서를 파악하도록 `Logics:` 섹션 추가

## 이유
- Google Style: Args/Returns/Raises 구조화 → AI 파싱 용이
- 한국어: 팀 커뮤니케이션 언어와 일치 → 이해도 향상
- Logics 섹션: Claude가 알고리즘 의도를 파악하여 더 나은 코드 작성

## 결과
- convention-python skill에 예시 포함
- pre-commit에서 Logics 섹션 확인 가능
