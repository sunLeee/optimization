# Skill 작성 및 관리 가이드

> 참조: docs/ref/bestpractice/claude-code-rule-convention.md (Practice 5, 14)
> 참조: 전역 CLAUDE.md의 구현 시 필수 스킬 테이블

## 1. Skill 포맷 (SKILL.md)

모든 skill은 `.claude/skills/{skill-name}/SKILL.md` 경로에 위치한다.

```yaml
---
name: skill-name
description: 한 줄 설명. 에이전트가 언제 이 skill을 사용할지 판단하는 기준.
triggers:
  - "트리거 키워드 1"
  - "트리거 키워드 2"
user-invocable: true  # /skill-name으로 직접 호출 가능
---
```

**필수 섹션**:
1. frontmatter (name, description, triggers, user-invocable)
2. 언제 사용하는가 (When to Use)
3. 어떻게 작동하는가 (How It Works)
4. 구체적 상황 예시 2개 이상

**상황 1**: `/convention-python` 입력 → frontmatter의 triggers와 매칭 → skill 자동 로딩
**상황 2**: CLAUDE.md의 "구현 시 필수 스킬" 테이블에 등록 → 에이전트가 코드 작성 시 자동 참조

## 2. 이 프로젝트의 현재 Skill 목록 (동적 조회)

정적 목록 대신 실시간으로 확인한다.

```bash
# 현재 활성 skill 목록
ls .claude/skills/

# deprecated skill 확인
grep -r "deprecated" .claude/skills/*/SKILL.md

# 특정 skill 내용 확인
cat .claude/skills/convention-python/SKILL.md
```

**카테고리**:
- `convention-*`: Python/commit/design/logging/adr/pr 코딩 컨벤션
- `check-*`: anti-patterns, security, design-doc 검증
- `python-*`: python-testing, python-patterns (deprecated)
- 유틸리티: code-simplifier, lint-fix

## 3. 새 Skill 작성 절차

```bash
# 1. 디렉토리 생성
mkdir -p .claude/skills/{skill-name}

# 2. SKILL.md 작성 (frontmatter + 내용)
# 3. CLAUDE.md 구현 시 필수 스킬 테이블에 추가
# 4. /manage-skill로 등록 확인
```

**상황 1**: 새 도메인 컨벤션 정의 시 → `/manage-skill`로 `convention-{domain}` 생성
**상황 2**: 반복 실수 패턴 발견 시 → Stop hook에서 추출하여 새 skill로 등록

## 4. Continuous Learning (Stop Hook 기반)

세션 종료 시 자동으로 학습 패턴을 추출하여 skill을 업데이트한다.

```json
// .claude/settings.json — Stop hook
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "echo '[Stop Hook 알림] /check-python-style 실행 권장'"
      }]
    }]
  }
}
```

**현재 이 프로젝트**: Stop hook은 정보성 알림만 (실제 강제는 pre-commit)
**확장 방법**: Stop hook에 세션 요약 저장 스크립트 추가

**상황 1**: 같은 실수를 3번 반복 → Stop hook이 패턴 감지 → skill에 추가
**상황 2**: 디버깅 기법 발견 → `/learn` 명령어로 즉시 skill 추출

## 5. Skill 트리거 최적화

에이전트가 올바른 상황에 skill을 자동으로 선택하도록 triggers를 구체화한다.

```yaml
# 너무 일반적 (피해야 함)
triggers:
  - "python"
  - "코드"

# 구체적 (권장)
triggers:
  - "python 코딩 규칙"
  - "PEP8"
  - "타입힌트 어떻게"
  - "docstring 작성법"
```

**상황 1**: "PEP8 규칙 알려줘" → `convention-python` 자동 선택
**상황 2**: 너무 일반적인 trigger → 잘못된 skill이 선택됨 → trigger 수정

## 6. /manage-skill로 skill 관리

```bash
/manage-skill list          # 전체 목록
/manage-skill add           # 새 skill 생성 가이드
/manage-skill edit {name}   # 기존 skill 수정
/manage-skill search {query} # skill 검색
```

**상황 1**: 새 컨벤션 필요 → `/manage-skill add`로 대화형 생성
**상황 2**: 기존 skill이 outdated → `/manage-skill edit {name}`으로 수정

## 참조

- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — Practice 5, 14
- 전역 CLAUDE.md 구현 시 필수 스킬 테이블
