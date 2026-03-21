# 항구 최적화 프로젝트 (Harbor Optimization)

## 프로젝트 개요

항구 운영 최적화 시스템. 예인선(Tugboat), 대형선박(Vessel), 항구(Port/Berth) 간의
스케줄·경로·연료 최적화를 수학적 최적화 기법으로 해결한다.

### 핵심 최적화 문제

| 문제 유형 | 설명 | 관련 문제 클래스 |
|-----------|------|----------------|
| 스케줄 최적화 | 예인선 배치 타임라인 최적화 | Tugboat Scheduling Problem (TSP-T) |
| 경로 최적화 | 예인선 이동 경로 최적화 | VRP with Time Windows (VRPTW) |
| 연료 최적화 | 속도-연료 관계 기반 소비 최소화 | Multi-objective Maritime Opt. |
| 선석 배분 | 선박-선석 매칭 및 시간 배분 | Berth Allocation Problem (BAP) |

### 불확실성 모델

- 선박 도착 스케줄은 **사전 확정**이 기본 가정
- 날씨 조건에 따라 도착 시간 ±2시간 변동 가능
- 확률분포: Log-normal 기본 (데이터 N≥200 시 KDE 대체)
- Rolling Horizon (실시간 dispatch) + 2-stage SP (사전 계획) 병행

## 기술 스택

- **언어**: Python 3.11+
- **최적화**: Pyomo + HiGHS (무료) / Gurobi (유료 벤치마크 병행)
- **수학적 formulation**: `docs/research/mathematical_formulation.md` 참조
- **알고리즘 선택**: `docs/research/algorithm_selection.md` 참조
- **품질 도구**: ruff (lint/format), mypy (타입 검사), pre-commit

## 배포 및 환경 설정

```bash
# 환경 초기화
bash .claude/setup.sh

# 의존성 설치
pip install -r requirements-research.txt

# 품질 도구 설치
pre-commit install
```

`setup.sh`는 `.claude/setup.sh`를 실행하며, Python 가상환경 생성 및 의존성 설치를 자동화한다.

## 워크플로우 규칙 (AW-001 ~ AW-010)

### AW-001: 새 기능 구현 전 deep-interview 필수

복잡한 최적화 기능(솔버 통합, 새 알고리즘) 구현 전 `deep-interview`로 요구사항을 명확화한다.
소크라테스식 질문으로 모호도 20% 이하까지 요구사항을 정제한 후 구현을 시작한다.

```bash
# deep-interview 실행
/oh-my-claudecode:deep-interview "구현할 기능 설명"
```

### AW-002: 전략적 계획은 ralplan으로 합의

알고리즘 선택, 솔버 스택, 모듈 구조 등 아키텍처 결정 시 `ralplan`을 통해
Planner → Architect → Critic 3-way 합의를 거친다.

```bash
# ralplan 실행
/oh-my-claudecode:ralplan "계획할 내용"
```

### AW-003: AskUserQuestion 전 omc-teams 사전 조사

새로운 라이브러리, 패턴, 방법론 선택 시 `omc-teams`로 codex+gemini에게
best practice를 먼저 조사한 후 사용자에게 질문한다.

### AW-004: ralplan 완료 후 deep-interview로 요구사항 검증

`ralplan`이 APPROVE를 받은 후에도 `deep-interview`로 실제 구현 요구사항을
재확인한다. 모호도 20% 이하를 유지한다.

### AW-005: 알고리즘 Tier 경계 준수

| 규모 | 알고리즘 | 솔버 |
|------|----------|------|
| n<10 | Exact MILP (McCormick 선형화) | HiGHS |
| n=10~50 | ALNS + eco-speed alternating | Pyomo |
| n>50 | Benders Decomposition | HiGHS/IPOPT |

### AW-006: 연료 모델 γ=2.5 고정 (데이터 피팅 기반)

`F(v,d) = α·v^2.5·d` — 실제 항구 데이터 피팅 기반. 단순화 시 `F=α·d` 허용.
`libs/fuel/consumption.py`에서 `fuel_consumption(v, d, alpha, gamma=2.5)` 사용.

### AW-007: 모듈 의존 방향 단방향 강제

```
libs/stochastic → libs/scheduling → libs/utils
libs/stochastic → libs/routing → libs/utils
libs/stochastic → libs/fuel → libs/utils
```

역방향 참조 금지. 위반 시 `check-anti-patterns` 실행.

### AW-008: 품질 게이트 90% 이상 유지

`bash .claude/check-criteria.sh --score` 결과 90 이상이어야 작업 완료.
ralplan 및 deep-interview 실행 이력이 CLAUDE.md에 반영되어야 한다.

### AW-009: 논문 인용 시 PDF 보존 의무

`docs/research/papers/references.md`에 메타정보 등록 + `scripts/download_papers_scihub.py`로
PDF 획득 시도. 수동 다운로드 필요 시 `docs/research/papers/download_status.md`에 기록.

### AW-010: ETA 분포 선택 기준

역사적 데이터 N≥200 → KDE 또는 GMM. N<200 → Log-normal(MLE 피팅). 데이터 없음 → TruncatedNormal(-2, +2).

**실측값 (2024-06 부산항, N=336, ADR-001):**
- `mu_log=4.015`, `sigma_log=1.363` (지연 중앙값 55.4분)
- `clip=[-6h, +6h]` (±2h 커버 81.5% → ±6h 89.6%)
- 지연 비율 71.4% / 조기 도착 28.6%
- 현행 `TwoStageConfig` 기본값에 반영 완료 (2026-03-21)

## 리서치 문서 구조

```
docs/research/
├── optimization_libraries.md    # Python 최적화 라이브러리 비교 (유/무료)
├── mathematical_formulation.md  # 논문 기반 수학적 formulation
├── algorithm_selection.md       # Big-O 복잡도별 알고리즘 가이드
├── stochastic_scheduling.md     # 확률적 스케줄링 불확실성 처리
├── eta_distributions.md         # ETA 분포 선택 가이드
└── papers/                      # 인용 논문 원문/요약
```

## 모듈 구조

```
libs/
├── scheduling/    # BAP, TSP-T (BerthAllocationModel, TugScheduleModel)
├── routing/       # VRPTW, ALNS (VRPTWModel, ALNSWithSpeedOptimizer)
├── fuel/          # 연료 소비 모델 (fuel_consumption, mccormick_linearize)
├── stochastic/    # Orchestrator (RollingHorizonOrchestrator, PortState)
└── utils/         # 인터페이스 계약 (TimeWindowSpec, SchedulingToRoutingSpec)
```

## 개발 원칙

- **커스터마이징 자유도 우선**: OR-Tools VRP 블랙박스 한계 인지 → Pyomo 직접 수식화
- **Tier별 알고리즘**: AW-005 준수
- **확률적 스케줄링**: AW-001, AW-004 절차로 요구사항 확정 후 구현
- **연료 모델**: AW-006 기준 (γ=2.5, 비선형 목적함수)
- **워크플로우**: deep-interview → ralplan → ultrawork 순서 준수

## 현재 상태

- [x] 프로젝트 구조 정의 (AW-001 ~ AW-010 설정)
- [x] 리서치 문서 생성 (6개 문서, 32편 논문, 24편 PDF)
- [x] ralplan 합의 완료 (Planner→Architect→Critic 3회 루프, APPROVE)
- [x] deep-interview 완료 (5라운드, 모호도 15%)
- [x] libs/ 모듈 구조 생성
- [x] 최적화 라이브러리 선정 (Pyomo+HiGHS)
- [x] 수학적 formulation 확정 (TSP-T MILP)
- [x] 알고리즘 구현 완료 (Step 1~4)
- [x] Phase 3: 대규모 벤치마크 (n=50/75 ALNS)
- [x] Phase 3: 멀티-예인선 배정 구현
- [x] Phase 3: AIS 데이터 처리 모듈
- [ ] Phase 3: 대시보드 고도화 (진행 중)
