"""
Benders Decomposition 벤치마크 스크립트.

용도:
  - Phase 3a (v² QP) vs Phase 3b (v^2.5 OA) 연료비 오차 측정
  - large_n80 성능 검증 (gap ≤ 5%, ≤30분)

실행:
    python scripts/benchmark_benders.py --n 12 --compare-gamma
    python scripts/benchmark_benders.py --n 80 --tugs 20 --berths 6
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (scripts/ 에서 직접 실행 시)
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.scheduling.benders import BendersDecomposition, BendersConfig
from libs.fuel.consumption import fuel_consumption
from libs.utils.time_window import TimeWindowSpec


def make_windows(n: int, n_berths: int = 2) -> list[TimeWindowSpec]:
    """n척 선박의 시간창 생성 (균등 도착)."""
    return [
        TimeWindowSpec(
            vessel_id=f"V{i}",
            berth_id=f"B{i % n_berths}",
            earliest_start=float(60 + i * 15),
            latest_start=float(120 + i * 15),
            service_duration=30.0,
            priority=(i % 5) + 1,
        )
        for i in range(n)
    ]


def make_berths(n_berths: int) -> dict[str, tuple[float, float]]:
    """선석 위치 (부산항 근방 격자)."""
    base_lat, base_lon = 35.098, 129.037
    return {
        f"B{b}": (base_lat + b * 0.003, base_lon + b * 0.004)
        for b in range(n_berths)
    }


def run_benders(
    n: int,
    n_tugs: int,
    n_berths: int,
    gamma: float,
    max_iter: int = 50,
    time_limit_sec: int = 1800,
    use_speed_opt: bool = False,
) -> dict:
    """Benders 벤치마크 실행."""
    windows = make_windows(n, n_berths)
    berths = make_berths(n_berths)
    tugs = [f"T{k}" for k in range(n_tugs)]

    cfg = BendersConfig(
        max_iter=max_iter,
        gap_tol=0.05,
        time_limit_sec=time_limit_sec,
        alpha=0.5,
        gamma=gamma,
        v_eco=10.0,
        use_speed_opt=use_speed_opt,
    )
    solver = BendersDecomposition(windows, tugs, berths, cfg=cfg)

    t0 = time.perf_counter()
    result = solver.solve()
    elapsed = time.perf_counter() - t0

    return {
        "gamma": gamma,
        "n": n,
        "n_tugs": n_tugs,
        "converged": result.converged,
        "gap": result.optimality_gap,
        "n_cuts": result.n_cuts,
        "iterations": result.iterations,
        "total_cost": result.total_cost,
        "fuel_cost_mt": result.fuel_cost_mt,
        "elapsed_sec": elapsed,
    }


def compare_gamma(n: int, n_tugs: int, n_berths: int) -> None:
    """Phase 3a(v² 고정속도) vs Phase 3b(v^2.5 속도최적화) 연료비 오차 측정."""
    print(f"\n{'='*60}")
    print(f"Phase 3a vs 3b 연료비 비교 (n={n}, tugs={n_tugs})")
    print(f"{'='*60}")

    r3a = run_benders(n, n_tugs, n_berths, gamma=2.5, use_speed_opt=False)
    r3b = run_benders(n, n_tugs, n_berths, gamma=2.5, use_speed_opt=True)

    print(f"\n[Phase 3a] cost={r3a['total_cost']:.4f}, fuel={r3a['fuel_cost_mt']:.4f}MT, "
          f"gap={r3a['gap']:.3f}, time={r3a['elapsed_sec']:.2f}s")
    print(f"[Phase 3b] cost={r3b['total_cost']:.4f}, fuel={r3b['fuel_cost_mt']:.4f}MT, "
          f"gap={r3b['gap']:.3f}, time={r3b['elapsed_sec']:.2f}s")

    fuel3a = r3a["fuel_cost_mt"]
    fuel3b = r3b["fuel_cost_mt"]
    if fuel3a > 1e-9:
        improvement = (fuel3a - fuel3b) / fuel3a
        print(f"\nPhase 3b 연료비 개선: {improvement:.1%}")
        print()
        if improvement > 0.01:
            print("→ 개선 > 1%: Phase 3b 효과 확인")
        else:
            print("→ 개선 ≤ 1%: Phase 3a로 충분")
    else:
        print("→ 연료비 0 (단거리 시나리오): 비교 불가")


def run_performance(n: int, n_tugs: int, n_berths: int) -> None:
    """대규모 성능 벤치마크 (large_n80 수용 기준 검증)."""
    print(f"\n{'='*60}")
    print(f"성능 벤치마크: n={n}, tugs={n_tugs}, berths={n_berths}")
    print(f"목표: gap ≤ 5%, time ≤ 1800s, n_cuts ≥ 10")
    print(f"{'='*60}")

    r = run_benders(n, n_tugs, n_berths, gamma=2.5, max_iter=100, time_limit_sec=1800)

    print(f"\n결과:")
    print(f"  converged: {r['converged']}")
    print(f"  gap:       {r['gap']:.3f}  {'✓' if r['gap'] <= 0.05 else '✗'} (≤5%)")
    print(f"  time:      {r['elapsed_sec']:.1f}s  {'✓' if r['elapsed_sec'] <= 1800 else '✗'} (≤1800s)")
    print(f"  n_cuts:    {r['n_cuts']}  {'✓' if r['n_cuts'] >= 10 else '✗'} (≥10)")
    print(f"  cost:      {r['total_cost']:.4f}")
    print(f"  iter:      {r['iterations']}")

    passed = r['gap'] <= 0.05 and r['elapsed_sec'] <= 1800 and r['n_cuts'] >= 10
    print(f"\n{'✓ 수용 기준 통과' if passed else '✗ 수용 기준 미달'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benders Decomposition 벤치마크")
    parser.add_argument("--n", type=int, default=12, help="선박 수")
    parser.add_argument("--tugs", type=int, default=4, help="예인선 수")
    parser.add_argument("--berths", type=int, default=2, help="선석 수")
    parser.add_argument("--compare-gamma", action="store_true",
                        help="γ=2 vs γ=2.5 연료비 오차 측정")
    parser.add_argument("--mode", choices=["perf", "gamma", "both"], default="perf",
                        help="실행 모드")
    args = parser.parse_args()

    if args.compare_gamma or args.mode in ("gamma", "both"):
        compare_gamma(args.n, args.tugs, args.berths)

    if not args.compare_gamma and args.mode in ("perf", "both"):
        run_performance(args.n, args.tugs, args.berths)


if __name__ == "__main__":
    main()
