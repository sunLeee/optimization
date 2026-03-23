# Makefile — Harbor Optimization
# 실행: make <target>
# 전제 조건: uv 설치 + uv sync 완료

.PHONY: help fit fit-eta fit-shaw test lint typecheck quality experiment dashboard-check

# ── 기본 타겟 ──────────────────────────────────────────────────

help:
	@echo "Harbor Optimization — Makefile 타겟 목록"
	@echo ""
	@echo "  파라미터 피팅:"
	@echo "    make fit        ETA + Shaw 파라미터 피팅 (순차)"
	@echo "    make fit-eta    ETA 지연 분포 피팅 → configs/eta_params.yaml"
	@echo "    make fit-shaw   Shaw lambda 피팅  → configs/shaw_params.yaml"
	@echo ""
	@echo "  품질 검사:"
	@echo "    make test            pytest 전체 실행"
	@echo "    make lint            ruff 린트 검사"
	@echo "    make typecheck       mypy 타입 검사"
	@echo "    make quality         lint + typecheck + test 순서 실행"
	@echo ""
	@echo "  실험:"
	@echo "    make experiment      4종 목적함수 실증 실험 → results/objective_comparison.csv"
	@echo "    make dashboard-check 대시보드 AST 파싱 검증"

# ── 파라미터 피팅 ───────────────────────────────────────────────

DATA_PATH ?= data/raw/scheduling/data/2024-06_SchData.csv

## ETA 지연 분포 MLE 피팅 → configs/eta_params.yaml
fit-eta:
	uv run python scripts/fit_eta_parameters.py --data $(DATA_PATH) --out configs/eta_params.yaml

## Shaw Destroy lambda 피팅 → configs/shaw_params.yaml
fit-shaw:
	uv run python scripts/fit_shaw_parameters.py --data $(DATA_PATH) --out configs/shaw_params.yaml

## 두 피팅 순차 실행 (ETA 먼저)
fit: fit-eta fit-shaw
	@echo ""
	@echo "=== 피팅 완료 ==="
	@echo "  configs/eta_params.yaml"
	@echo "  configs/shaw_params.yaml"

# ── 품질 검사 ───────────────────────────────────────────────────

## pytest 전체 실행
test:
	uv run pytest tests/ -v

## ruff 린트 (전체)
lint:
	uv run ruff check libs/ scripts/ tests/

## ruff 린트 (신규 파일만: optimization, evaluation, experiment, tests)
lint-new:
	uv run ruff check \
		libs/optimization/ \
		libs/evaluation/ \
		scripts/run_objective_experiment.py \
		tests/test_objective.py \
		tests/test_backtester.py

## mypy 타입 검사
typecheck:
	uv run mypy libs/ --ignore-missing-imports

## 전체 품질 게이트 (lint → typecheck → test)
quality: lint typecheck test
	@echo ""
	@echo "=== 품질 게이트 통과 ==="

## 신규 파일 품질 게이트 (lint-new → test)
quality-new: lint-new
	uv run pytest tests/test_objective.py tests/test_backtester.py -v
	@echo ""
	@echo "=== 신규 파일 품질 게이트 통과 ==="

# ── 벤치마크 ────────────────────────────────────────────────────

## Phase 3a vs 3b 연료비 비교 (n=12)
benchmark-small:
	uv run python scripts/benchmark_benders.py --n 12 --tugs 4 --berths 2 --compare-gamma

## 대규모 벤치마크 (n=80, gap ≤ 5% 검증)
benchmark-large:
	uv run python scripts/benchmark_benders.py --n 80 --tugs 20 --berths 6

# ── 실험 ────────────────────────────────────────────────────────────

EXPERIMENT_DATA ?= data/raw/scheduling/data/2024-06_SchData.csv
EXPERIMENT_OUT  ?= results/objective_comparison.csv

## 4종 목적함수 실증 비교 실험 (N=336 실데이터)
experiment:
	uv run python scripts/run_objective_experiment.py \
		--data $(EXPERIMENT_DATA) \
		--out $(EXPERIMENT_OUT) \
		--seed 42
	@echo ""
	@echo "=== 실험 완료: $(EXPERIMENT_OUT) ==="

## 대시보드 AST 파싱 검증 (런타임 실행 없이 문법 확인)
dashboard-check:
	uv run python -c "import ast, sys; ast.parse(open('scripts/harbor_dashboard.py').read()); print('dashboard: AST parse OK')"
