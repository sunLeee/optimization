# libs/scheduling/ — 스케줄링 MILP 모델

## 역할

BAP(선석 배분), TSP-T(예인선 스케줄), Benders Decomposition 구현.
의존: `libs/utils/` (단방향).

## 파일 목록

| 파일 | 주요 클래스 | Tier | 알고리즘 |
|------|-----------|------|---------|
| `bap.py` | `BerthAllocationModel`, `BAPInput`, `BAPResult` | — | 이산 BAP MILP |
| `tsp_t_milp.py` | `TugScheduleModel`, `SolverResult` | 1 | Exact MILP (n<10) |
| `benders.py` | `BendersDecomposition`, `BendersConfig`, `BendersResult` | 3 | Benders (n>50) |

## BAP → TSP-T 파이프라인 ([I1])

```python
bap_result = BerthAllocationModel(bap_input).solve()
tug_result = TugScheduleModel(
    windows=bap_result.time_windows,      # TimeWindowSpec 리스트
    berth_locations=bap_result.berth_positions,
    ...
).solve()
```

`BAPResult.time_windows` → `TugScheduleModel.windows` 직결.
`berth_id`가 `berth_locations` dict의 키와 반드시 일치해야 함 (KeyError 방지).

## Benders Phase 구분

| Phase | `use_speed_opt` | 연료 모델 | 솔버 |
|-------|----------------|---------|------|
| 3a | `False` (기본) | v_eco 고정 | HiGHS |
| 3b | `True` | EcoSpeedOptimizer v^2.5 | CVXPY + HiGHS |

Phase 3b 활성화:
```python
cfg = BendersConfig(use_speed_opt=True)
result = BendersDecomposition(windows, tugs, berths, cfg=cfg).solve()
print(result.fuel_cost_mt)   # v^2.5 정확 연료비
```

## Benders Cut 방식

- `_generate_benders_cut()`: 한계비용 subgradient
  `beta[j,k] = max(0, Q(y'_{j→k}) - Q(y*))`
- LB > UB 발생 시 `LB = UB * (1 - gap_tol)` 보정

## 솔버 호출 규칙

- 반드시 `uv run` 환경에서 실행 (`uv run python ...`)
- `time_limit_sec`, `mip_gap` 파라미터로 제한
- HiGHS 미설치 시: `uv pip install highspy`

## Big-M 계산

`_compute_big_m()`: `max(latest_start + service_duration) - min(earliest_start)`
toy_n5 예상값: 1020분.
