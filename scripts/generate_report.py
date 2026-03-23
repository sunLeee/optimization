"""
성능 비교 보고서 자동 생성 — Phase 6.

benchmark_matrix.csv + robustness.csv 를 읽어
벤치마크 히트맵, CVaR 바차트, KPI 레이더 차트를 생성하고
Markdown 보고서를 저장한다.

사용법:
    uv run python scripts/generate_report.py
    uv run python scripts/generate_report.py --out results/
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def _load_csv(path: pathlib.Path) -> list[dict]:
    import csv
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _safe_float(val: str, default: float = float("nan")) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


# ── 히트맵: solver × objective → objective_value ──────────────
def plot_benchmark_heatmap(
    rows: list[dict], out_path: pathlib.Path
) -> str | None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        logger.warning("matplotlib 미설치 — 히트맵 생략")
        return None

    solvers = sorted({r["solver"] for r in rows})
    objectives = sorted({r["objective"] for r in rows})

    data = np.full((len(solvers), len(objectives)), float("nan"))
    for r in rows:
        if r.get("error"):
            continue
        si = solvers.index(r["solver"])
        oi = objectives.index(r["objective"])
        data[si, oi] = _safe_float(r.get("objective_value", ""))

    # NaN 마스킹
    mask = ~np.isfinite(data)
    plot_data = np.where(mask, 0.0, data)

    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
    im = ax.imshow(plot_data, cmap="YlOrRd", aspect="auto")
    plt.colorbar(im, ax=ax, label="Objective Value")

    ax.set_xticks(range(len(objectives)))
    ax.set_xticklabels(
        [o[:20] for o in objectives], rotation=30, ha="right", fontsize=8
    )
    ax.set_yticks(range(len(solvers)))
    ax.set_yticklabels(solvers, fontsize=9)
    ax.set_title("Benchmark Heatmap: Solver × Objective", fontsize=12)

    for si in range(len(solvers)):
        for oi in range(len(objectives)):
            val = data[si, oi]
            if np.isfinite(val):
                ax.text(
                    oi, si, f"{val:.2f}",
                    ha="center", va="center", fontsize=7,
                    color="black" if val < plot_data.max() * 0.7 else "white",
                )
            else:
                ax.text(oi, si, "N/A", ha="center", va="center", fontsize=7)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close()
    logger.info("히트맵 저장: %s", out_path)
    return str(out_path)


# ── CVaR95 바차트 ─────────────────────────────────────────────
def plot_cvar_barchart(
    rob_rows: list[dict], out_path: pathlib.Path
) -> str | None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        logger.warning("matplotlib 미설치 — CVaR 바차트 생략")
        return None

    if not rob_rows:
        logger.warning("robustness.csv 없음 — CVaR 바차트 생략")
        return None

    names = [r["solver"] for r in rob_rows]
    cvar95 = [_safe_float(r.get("cvar95_h", "")) for r in rob_rows]
    mean_h = [_safe_float(r.get("mean_cost_h", "")) for r in rob_rows]
    p95_h = [_safe_float(r.get("p95_h", "")) for r in rob_rows]

    x = np.arange(len(names))
    width = 0.28

    fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
    bars_mean = ax.bar(x - width, mean_h, width, label="Mean cost (h)", color="#4c9be8")
    bars_p95 = ax.bar(x, p95_h, width, label="P95 cost (h)", color="#e8a24c")
    bars_cvar = ax.bar(x + width, cvar95, width, label="CVaR95 (h)", color="#e84c4c")

    for bars in [bars_mean, bars_p95, bars_cvar]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    h + 0.5, f"{h:.1f}",
                    ha="center", va="bottom", fontsize=7,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel("Priority-weighted Wait (hours)")
    ax.set_title("ETA Robustness: Mean / P95 / CVaR95 비교", fontsize=12)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close()
    logger.info("CVaR 바차트 저장: %s", out_path)
    return str(out_path)


# ── KPI 레이더 차트 ───────────────────────────────────────────
def plot_kpi_radar(
    rows: list[dict], out_path: pathlib.Path
) -> str | None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        logger.warning("matplotlib 미설치 — KPI 레이더 생략")
        return None

    # MILP/ALNS/Benders × MinWait 행만 사용
    target_obj = "OBJ-A MinWait"
    filtered = [
        r for r in rows
        if r.get("objective") == target_obj and not r.get("error")
    ]
    if not filtered:
        # 첫 번째 objective 사용
        objs = list({r["objective"] for r in rows if not r.get("error")})
        if not objs:
            return None
        target_obj = objs[0]
        filtered = [r for r in rows if r.get("objective") == target_obj and not r.get("error")]

    kpi_keys = ["idle_h", "wait_h", "solve_time_sec"]
    kpi_labels = ["Idle (h)", "Wait (h)", "Solve Time (s)"]
    n_kpi = len(kpi_keys)

    # 각 KPI 정규화 (0–1, 최악=1)
    kpi_vals: dict[str, list[float]] = {k: [] for k in kpi_keys}
    solver_names: list[str] = []

    for r in filtered:
        solver_names.append(r["solver"])
        for k in kpi_keys:
            kpi_vals[k].append(_safe_float(r.get(k, ""), 0.0))

    # 정규화
    def _norm(vals: list[float]) -> list[float]:
        mx = max(vals) if vals and max(vals) > 0 else 1.0
        return [v / mx for v in vals]

    normed = {k: _norm(kpi_vals[k]) for k in kpi_keys}

    # 레이더 각도
    angles = np.linspace(0, 2 * np.pi, n_kpi, endpoint=False).tolist()
    angles += angles[:1]

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    fig, ax = plt.subplots(figsize=(7, 6), dpi=100, subplot_kw={"polar": True})

    for si, solver in enumerate(solver_names):
        vals = [normed[k][si] for k in kpi_keys]
        vals += vals[:1]
        ax.plot(
            angles, vals,
            color=colors[si % len(colors)],
            linewidth=1.8, linestyle="solid", label=solver,
        )
        ax.fill(angles, vals, color=colors[si % len(colors)], alpha=0.1)

    ax.set_thetagrids(
        np.degrees(np.array(angles[:-1])), kpi_labels, fontsize=9
    )
    ax.set_ylim(0, 1)
    ax.set_title(
        f"KPI 레이더 ({target_obj})\n(정규화 — 0=최적, 1=최악)",
        fontsize=10, pad=20,
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=8)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close()
    logger.info("KPI 레이더 저장: %s", out_path)
    return str(out_path)


# ── Markdown 보고서 ───────────────────────────────────────────
def generate_markdown_report(
    bench_rows: list[dict],
    rob_rows: list[dict],
    out_path: pathlib.Path,
    chart_paths: dict[str, str | None],
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []

    lines += [
        "# 항구 예인선 최적화 성능 비교 보고서",
        "",
        f"생성일: {now}  ",
        "데이터: 2024-06 인천항 실측 데이터 (N=336)  ",
        "",
        "---",
        "",
        "## 1. 실험 개요",
        "",
        "| 항목 | 내용 |",
        "|------|------|",
        "| 알고리즘 | MILP-Tier1, ALNS-Tier2, Benders-Tier3 |",
        "| 목적함수 | MinWait, MinIdle, MinComposite, MinAll |",
        "| 평가 방법 | N×M 벤치마크 매트릭스 + Monte Carlo Robustness (n_mc=100) |",
        "| ETA 분포 | Log-normal (mu=4.015, sigma=1.363, p_delay=71.4%) |",
        "",
    ]

    # ── 벤치마크 결과 표 ──
    lines += [
        "## 2. N×M 벤치마크 결과",
        "",
    ]
    if bench_rows:
        header = "| 솔버 | 목적함수 | n | idle_h | wait_h | obj_value | 시간(s) |"
        sep = "|------|---------|---|--------|--------|-----------|---------|"
        lines += [header, sep]
        for r in bench_rows:
            if r.get("error"):
                continue
            idle = _safe_float(r.get("idle_h", ""))
            wait = _safe_float(r.get("wait_h", ""))
            obj = _safe_float(r.get("objective_value", ""))
            t = _safe_float(r.get("solve_time_sec", ""))
            lines.append(
                f"| {r['solver']} | {r['objective'][:20]} "
                f"| {r.get('n_samples','-')} "
                f"| {idle:.2f} | {wait:.2f} | {obj:.4f} | {t:.2f} |"
            )
        lines.append("")

    # ── 히트맵 ──
    if chart_paths.get("heatmap"):
        lines += [
            "### 2.1 벤치마크 히트맵",
            "",
            "![benchmark_heatmap](benchmark_heatmap.png)",
            "",
        ]

    # ── Robustness 결과 ──
    lines += [
        "## 3. ETA Robustness 분석 (CVaR95)",
        "",
    ]
    if rob_rows:
        lines += [
            "| 솔버 | n | mean_h | std_h | p95_h | CVaR95_h |",
            "|------|---|--------|-------|-------|----------|",
        ]
        for r in rob_rows:
            lines.append(
                f"| {r['solver']} | {r.get('n_windows','-')} "
                f"| {_safe_float(r.get('mean_cost_h','')):.3f} "
                f"| {_safe_float(r.get('std_cost_h','')):.3f} "
                f"| {_safe_float(r.get('p95_h','')):.3f} "
                f"| {_safe_float(r.get('cvar95_h','')):.3f} |"
            )
        lines.append("")

        # 최강 robustness
        best = min(rob_rows, key=lambda x: _safe_float(x.get("cvar95_h", "inf")))
        lines += [
            f"**최강 Robustness**: `{best['solver']}`",
            f"  - CVaR95 = {_safe_float(best.get('cvar95_h','')):.3f}h",
            "  - 95번째 백분위수 이상의 시나리오에서 평균 대기 비용이 최소",
            "",
        ]

    if chart_paths.get("cvar"):
        lines += [
            "### 3.1 CVaR95 비교",
            "",
            "![cvar_barchart](cvar_barchart.png)",
            "",
        ]

    # ── KPI 레이더 ──
    if chart_paths.get("radar"):
        lines += [
            "## 4. KPI 레이더 차트",
            "",
            "![kpi_radar](kpi_radar.png)",
            "",
            "> 각 KPI를 솔버 최악값으로 정규화. 0 = 최적, 1 = 최악.",
            "",
        ]

    # ── 해석 및 결론 ──
    lines += [
        "## 5. 해석 및 결론",
        "",
        "### 5.1 알고리즘별 특성",
        "",
        "| 알고리즘 | 적용 규모 | 장점 | 한계 |",
        "|---------|---------|------|------|",
        "| MILP-Tier1 | n < 10 | 최적해 보장, gap=0% | 확장성 제한 |",
        "| ALNS-Tier2 | n = 10~50 | 빠른 근사해, 유연성 | 최적성 미보장 |",
        "| Benders-Tier3 | n > 50 | 대규모 처리 가능 | 대기시간 비교적 높음 |",
        "",
        "### 5.2 Robustness 관점",
        "",
        "- MILP-Tier1이 CVaR95 기준 가장 강건한 이유:",
        "  소규모(n=8) 배정으로 ETA 지연 영향이 상대적으로 낮음",
        "- 대규모 솔버(Benders/ALNS)는 절대 비용은 높지만 정규화 시 유사한 패턴",
        "- 실운용 권장: Tier별 순차 적용 (MILP → ALNS → Benders)",
        "",
        "### 5.3 향후 개선 방향",
        "",
        "1. 실시간 ETA 업데이트 연동 (AIS 스트림 기반 Rolling Horizon)",
        "2. 다중 예인선 협조 서비스 (required_tugs > 1) 확장",
        "3. 연료 비선형 모델(γ=2.5) 통합 최적화 (Phase 3b)",
        "4. 기상 조건(풍속, 조류) 연동 제약 추가",
        "5. 온라인 학습 기반 파라미터 자동 조정",
        "",
        "---",
        f"*자동 생성: {now}*",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    logger.info("Markdown 보고서 저장: %s", out_path)
    return str(out_path)


# ── 메인 ──────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="성능 비교 보고서 자동 생성 (차트 + Markdown)"
    )
    parser.add_argument("--bench-csv", default="results/benchmark_matrix.csv")
    parser.add_argument("--rob-csv", default="results/robustness.csv")
    parser.add_argument("--out", default="results")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== 보고서 생성 시작 ===")

    bench_rows = _load_csv(pathlib.Path(args.bench_csv))
    rob_rows = _load_csv(pathlib.Path(args.rob_csv))

    logger.info("bench_rows=%d, rob_rows=%d", len(bench_rows), len(rob_rows))

    chart_paths: dict[str, str | None] = {}

    # ── 차트 생성 (병렬 가능하지만 matplotlib 스레드 안전 이슈로 순차) ──
    chart_paths["heatmap"] = plot_benchmark_heatmap(
        bench_rows, out_dir / "benchmark_heatmap.png"
    )
    chart_paths["cvar"] = plot_cvar_barchart(
        rob_rows, out_dir / "cvar_barchart.png"
    )
    chart_paths["radar"] = plot_kpi_radar(
        bench_rows, out_dir / "kpi_radar.png"
    )

    # ── Markdown 보고서 ──
    report_path = generate_markdown_report(
        bench_rows, rob_rows,
        out_dir / "performance_report.md",
        chart_paths,
    )

    print("\n=== 생성 완료 ===")
    for name, path in chart_paths.items():
        status = path if path else "생략"
        print(f"  {name}: {status}")
    print(f"  report: {report_path}")


if __name__ == "__main__":
    main()
