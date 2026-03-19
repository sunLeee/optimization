# 멀티에이전트 & 병렬화 가이드

> 참조: docs/ref/bestpractice/claude-code-rule-convention.md (Practice 9~12)
> 참조: 전역 CLAUDE.md의 team_pipeline, parallelization 섹션

## 1. 워크플로우 선택 기준

| 도구 | 사용 시점 | 예시 |
|------|---------|------|
| `/ralph` | 완료 보장이 필요한 단일 작업 | 버그 수정, 새 기능 구현 |
| `/ultrawork` | 독립적인 여러 작업 병렬 실행 | 여러 패키지에 테스트 추가 |
| `/omc-teams` | 외부 AI 모델 조사 (codex, gemini) | best practice 조사 |
| `/team` | 단계별 품질 보증 필요 | plan→exec→verify→fix 파이프라인 |
| `/ralplan` | 구현 전 합의 필요 | 아키텍처 결정, 설계 문서 작성 |

**상황 1**: 간단한 버그 수정 → `/ralph`로 충분
**상황 2**: 5개 독립 모듈에 테스트 작성 → `/ultrawork`로 병렬 실행 (5배 빠름)

## 2. Git Worktrees 병렬화

여러 Claude 인스턴스가 독립적으로 작업하려면 git worktree로 격리한다.

```bash
# worktree 생성
git worktree add ../shucle-ai-agent-feature-a feature-a
git worktree add ../shucle-ai-agent-refactor refactor-branch

# 각 worktree에서 Claude 독립 실행
cd ../shucle-ai-agent-feature-a && claude
cd ../shucle-ai-agent-refactor && claude

# 현재 프로젝트 worktree 목록
ls /Users/hmc123/Documents/SHUCLE-AI-AGENT-WORKTREE/
```

**이 프로젝트 현재 worktrees**:
```bash
ls /Users/hmc123/Documents/SHUCLE-AI-AGENT-WORKTREE/
# shucle-ai-agent, lib-data-pipeline, shucle-ai-agent-general-rules
```

**상황 1**: 기능 A와 B를 동시 개발 → 각 worktree에서 독립적으로 Claude 실행
**상황 2**: 같은 파일을 두 인스턴스가 수정 → worktree 없으면 충돌. worktree로 격리.

## 3. 검증 루프 패턴

### Checkpoint-based (선형 워크플로우)
```
[구현] → [체크포인트 검증] → pass? → [다음 단계]
                             ↓ fail
                           [수정] → 재검증
```

**언제**: 명확한 마일스톤이 있는 기능 구현

### Continuous (장시간 탐색)
```
[작업] → [N분마다 / 변경마다] → [테스트 실행] → pass → [계속]
                                               ↓ fail
                                             [중단 + 수정]
```

**언제**: 리팩토링, 탐색적 개발

**이 프로젝트 검증 명령어**:
```bash
uv run pytest -m unit              # 빠른 검증 (API key 불필요)
uv run pytest -m integration       # 전체 검증 (API key 필요)
uv run ruff check . --select E,W   # 스타일 검증
```

**상황 1**: 새 기능 추가 → 각 서브 태스크마다 unit test 통과 확인 (checkpoint)
**상황 2**: 대규모 리팩토링 → 변경마다 ruff + pytest 자동 실행 (continuous)

## 4. pass@k vs pass^k

에이전트 성능 측정 지표.

| 지표 | 의미 | 사용 시점 |
|------|------|---------|
| `pass@k` | k번 시도 중 1번이라도 성공 | "어떻게든 되면 됨" |
| `pass^k` | k번 시도 모두 성공 (일관성) | "항상 같은 결과 필요" |

```python
# pass@3 = 70%, 91%, 97% (시도 횟수에 따라)
# pass^3 = 70%, 34%, 17% (일관성은 높은 k에서 급감)
```

**상황 1**: 테스트 통과만 확인 → `pass@k` 사용 (하나라도 통과하면 OK)
**상황 2**: 문서 생성 일관성 검증 → `pass^k` 사용 (3번 모두 같은 품질)

## 5. 토큰 최적화 전략

**모델 티어 분리**:
```python
# 탐색: haiku (5x 저렴)
Task(explore, model="haiku", prompt="파일 위치 탐색")

# 구현: sonnet (표준)
Task(executor, model="sonnet", prompt="함수 구현")

# 아키텍처 리뷰: opus (내부망 제한 → sonnet 대체)
```

**Modular 코드베이스**: 파일이 작을수록 Claude가 적은 토큰으로 처리
```bash
# 800줄 초과 파일 찾기 (200~400줄이 최적)
find . -name "*.py" | xargs wc -l | awk '$1 > 800 {print}' | sort -rn
```

**Background 프로세스**: 긴 출력은 tmux에서 실행, 요약만 Claude에 제공
```bash
# Claude가 직접 스트리밍하지 않아도 되는 작업
tmux new-window -n "test-runner" "uv run pytest -v 2>&1 | tee /tmp/test-output.txt"
```

**상황 1**: pytest 전체 suite → tmux에서 실행, 결과 요약만 Claude에 전달
**상황 2**: 모든 작업에 opus → haiku/sonnet 티어로 교체 시 비용 5x 절감

## 참조

- [docs/ref/bestpractice/claude-code-rule-convention.md](../../ref/bestpractice/claude-code-rule-convention.md) — Practice 9~12
- 전역 CLAUDE.md Team Operations (AW-007~010)
