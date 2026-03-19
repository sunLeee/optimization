# OMC 워크플로우 한국어 가이드

> OMC 설치 시 `~/.claude/CLAUDE.md`에 영어 워크플로우 목록이 자동 생성된다.
> 이 파일은 그 내용의 **한국어 참조 문서**다. OMC 업데이트에 덮어쓰이지 않는다.
> 원문: `~/.claude/CLAUDE.md` § skills > Workflow 섹션

---

## 워크플로우 skill 목록

| Skill | 트리거 키워드 | 한국어 설명 | 사용 시점 |
|-------|------------|----------|---------|
| `autopilot` | "autopilot", "build me", "I want a" | 아이디어 → 작동 코드까지 완전 자율 실행 | 명확한 요구사항이 있고 전체 파이프라인을 자동으로 돌릴 때 |
| `ralph` | "ralph", "don't stop", "must complete" | verifier 검증 포함 자기참조 루프. ultrawork 포함 | 반드시 완료되어야 하는 구현. max iter 100 (AW-007) |
| `ultrawork` | "ulw", "ultrawork" | 병렬 agent 오케스트레이션으로 최대 병렬성 | 독립적인 다수 태스크를 동시에 처리할 때 |
| `team` | "team", "coordinated team", "team ralph" | N개의 Claude agent를 공유 task list로 조율 | 대형 기능 구현, 여러 파일에 걸친 복잡한 작업 |
| `omc-teams` | "omc-teams", "codex", "gemini" | tmux pane에 CLI worker (codex/gemini) 생성 | 사전조사, 병렬 분석, 다중 모델 의견 수집 |
| `ccg` | "ccg", "tri-model", "claude codex gemini" | Codex+Gemini에 fan-out → Claude가 종합 | 3개 모델의 의견을 한번에 받아 비교할 때 |
| `ultraqa` | autopilot에서 자동 활성화 | 테스트 → 검증 → 수정 반복 | QA 사이클이 필요한 구현 |
| `omc-plan` | "plan this", "plan the" | 전략적 계획. `--consensus`, `--review` 지원 | 구현 전 계획 수립 |
| `ralplan` | "ralplan", "consensus plan" | `/omc-plan --consensus` 별칭. Planner→Architect→Critic 합의 루프 | 되돌리기 어려운 설계 결정 전 (AW-009) |
| `sciomc` | "sciomc" | 병렬 scientist agent로 종합 분석 | 데이터 분석, 연구 조사 |
| `external-context` | — | document-specialist agent들이 웹 검색 | 외부 문서/라이브러리 참조가 필요할 때 |
| `deepinit` | "deepinit" | 계층적 AGENTS.md로 코드베이스 깊은 초기화 | 새 프로젝트 시작 또는 large codebase 파악 |

---

## OMC 업데이트 시 주의사항

```
~/.claude/CLAUDE.md
├── <!-- OMC:START -->  ← OMC 자동 관리 영역 (수정 금지)
│   │ 영어 workflow 목록
│   │ agent catalog
│   │ skills 섹션
│   └── ...
└── <!-- OMC:END -->  ← 여기까지만 OMC가 관리

아래 섹션은 사용자 커스터마이즈 영역 (OMC가 건드리지 않음)
```

**OMC 업데이트 후 체크:**
1. `<!-- OMC:END -->` 이후 사용자 커스터마이즈가 유지되는지 확인
2. 이 파일 (omc-workflows-ko.md)은 OMC가 관리하지 않으므로 항상 유지됨

---

## 권장 워크플로우 선택 기준

```
요청 유형               → 워크플로우
─────────────────────────────────────────────
새 기능 (소규모)        → deep-interview → ralplan → ralph
새 기능 (대규모)        → deep-interview → ralplan → team
빠른 수정               → ralph (--no-prd)
사전 조사               → omc-teams (codex + gemini)
3 모델 비교             → ccg
전체 파이프라인 자동화  → autopilot
계획만                  → ralplan
QA 집중                 → ultraqa
```

---

## 참조

- [omc.md](./omc.md) — OMC 상세 운영 가이드
- [agents.md](./agents.md) — Agent 선택 기준
- [CLAUDE.md](../../CLAUDE.md) — 전체 규칙 요약
- [team-operations-guide.md](./team-operations-guide.md) — AW-007 (ralph max 100) 등
