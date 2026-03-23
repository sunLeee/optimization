"""
Before/After comparison charts for harbor tugboat scheduling optimization.

Generates three charts saved to results/:
  1. daily_wait_comparison.png  - Bar chart: baseline vs optimized avg wait per vessel
  2. daily_distance_km.png      - Bar chart: travel + service distance per day (optimized)
  3. solution_overview.png      - 3-panel summary figure

Data sources:
  - data/raw/scheduling/data/2024-06_SchData.csv          (N=336, executed schedules)
  - data/raw/scheduling/data/2024-06_FristAllSchData.csv  (N=967, initial requests)
  - results/real_optimization.json                        (optimized KPIs by day)

Usage:
    uv run python scripts/plot_before_after.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

DATA_DIR = REPO / "data" / "raw" / "scheduling" / "data"
RESULTS_DIR = REPO / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SCH_DATA = DATA_DIR / "2024-06_SchData.csv"
OPT_JSON = RESULTS_DIR / "real_optimization.json"

plt.rcParams["figure.dpi"] = 150

# Use a non-interactive backend so the script works headlessly
matplotlib.use("Agg")

# ---------------------------------------------------------------------------
# Font: try to use a Korean font; fall back to default if unavailable
# ---------------------------------------------------------------------------
def _setup_font() -> bool:
    """Return True if a Korean-capable font was found and set."""
    import matplotlib.font_manager as fm

    korean_candidates = [
        "AppleGothic",       # macOS
        "NanumGothic",
        "Malgun Gothic",     # Windows
        "NanumBarunGothic",
        "UnDotum",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in korean_candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return True
    return False


KOREAN_AVAILABLE = _setup_font()

# Label helpers — English when no Korean font
def L(korean: str, english: str) -> str:
    return korean if KOREAN_AVAILABLE else english


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_baseline() -> pd.DataFrame:
    """
    Load SchData.csv, apply single-tug filter, and compute delay per vessel.

    Delay = max(0, actual_start - initial_schedule) in minutes.
    Rows where 기준예선 contains a comma are multi-tug and are excluded.
    """
    df = pd.read_csv(SCH_DATA)

    # Single-tug filter: 기준예선 must not contain a comma
    single = df[~df["기준예선"].astype(str).str.contains(",", na=False)].copy()

    # Parse timestamps (ISO 8601 with Z)
    single["actual_start"] = pd.to_datetime(single["실제 스케줄 시작 시각"], utc=True)
    single["initial_start"] = pd.to_datetime(single["최초 스케줄 시각"], utc=True)

    # Delay in minutes (clamped at 0 — early arrivals count as 0 delay)
    diff_min = (single["actual_start"] - single["initial_start"]).dt.total_seconds() / 60.0
    single["delay_min"] = diff_min.clip(lower=0)

    # Date (local-naive date string) for grouping
    single["date"] = single["actual_start"].dt.date.astype(str)

    return single


def load_optimized() -> pd.DataFrame:
    """Parse real_optimization.json into a per-day DataFrame."""
    with open(OPT_JSON) as f:
        data = json.load(f)

    rows = []
    for day in data["by_day"]:
        rows.append(
            {
                "date": day["date"],
                "n": day["n"],
                "wait_h": day["kpi"]["wait_h"],
                "idle_h": day["kpi"]["idle_h"],
            }
        )
    return pd.DataFrame(rows)


def load_distance() -> pd.DataFrame:
    """
    Compute total travel and service distance per day from SchData (single-tug).

    Uses the actual measured distances in the CSV:
      - 작업까지 이동 거리(km): travel from anchorage to work start berth
      - 작업중 이동 거리(km):   distance during service (start → end berth)
    """
    df = pd.read_csv(SCH_DATA)
    single = df[~df["기준예선"].astype(str).str.contains(",", na=False)].copy()

    single["actual_start"] = pd.to_datetime(single["실제 스케줄 시작 시각"], utc=True)
    single["date"] = single["actual_start"].dt.date.astype(str)

    dist = (
        single.groupby("date")
        .agg(
            travel_km=("작업까지 이동 거리(km)", "sum"),
            service_km=("작업중 이동 거리(km)", "sum"),
        )
        .reset_index()
    )
    return dist


# ---------------------------------------------------------------------------
# Chart 1: daily_wait_comparison.png
# ---------------------------------------------------------------------------

def plot_daily_wait(baseline: pd.DataFrame, optimized: pd.DataFrame) -> None:
    # Baseline: avg delay per vessel per day
    bl_daily = (
        baseline.groupby("date")["delay_min"]
        .mean()
        .reset_index()
        .rename(columns={"delay_min": "baseline_avg_wait_min"})
    )

    # Optimized: wait_h → minutes per vessel
    opt_daily = optimized.copy()
    opt_daily["opt_avg_wait_min"] = (opt_daily["wait_h"] * 60.0) / opt_daily["n"].clip(lower=1)

    # Merge on date
    merged = pd.merge(bl_daily, opt_daily[["date", "opt_avg_wait_min"]], on="date", how="inner")
    merged = merged.sort_values("date")

    dates = merged["date"].tolist()
    x = np.arange(len(dates))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 5))
    bars_bl = ax.bar(
        x - width / 2,
        merged["baseline_avg_wait_min"],
        width,
        label=L("기준 (실행 스케줄)", "Baseline (Executed)"),
        color="#E57373",
        alpha=0.88,
    )
    bars_opt = ax.bar(
        x + width / 2,
        merged["opt_avg_wait_min"],
        width,
        label=L("최적화 (MILP)", "Optimized (MILP)"),
        color="#42A5F5",
        alpha=0.88,
    )

    ax.set_xticks(x)
    ax.set_xticklabels([d[5:] for d in dates], rotation=45, ha="right", fontsize=8)
    ax.set_xlabel(L("날짜 (2024-06-)", "Date (2024-06-)"))
    ax.set_ylabel(L("평균 대기 시간 (분/선박)", "Avg Wait Time (min/vessel)"))
    ax.set_title(L("일별 평균 선박 대기 시간: 기준 vs 최적화", "Daily Avg Vessel Wait Time: Baseline vs Optimized"))
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Annotate bars with values
    for bar in bars_bl:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.3,
                f"{h:.1f}",
                ha="center",
                va="bottom",
                fontsize=6.5,
                color="#B71C1C",
            )
    for bar in bars_opt:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.3,
                f"{h:.1f}",
                ha="center",
                va="bottom",
                fontsize=6.5,
                color="#1565C0",
            )

    fig.tight_layout()
    out = RESULTS_DIR / "daily_wait_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Chart 2: daily_distance_km.png
# ---------------------------------------------------------------------------

def plot_daily_distance(dist: pd.DataFrame) -> None:
    dist = dist.sort_values("date")
    dates = dist["date"].tolist()
    x = np.arange(len(dates))
    width = 0.55

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.bar(
        x,
        dist["travel_km"],
        width,
        label=L("이동 거리 (정계지→작업)", "Travel (anchorage→berth)"),
        color="#66BB6A",
        alpha=0.88,
    )
    ax.bar(
        x,
        dist["service_km"],
        width,
        bottom=dist["travel_km"],
        label=L("작업 중 거리 (작업 시작→종료)", "Service (start→end berth)"),
        color="#FFA726",
        alpha=0.88,
    )

    ax.set_xticks(x)
    ax.set_xticklabels([d[5:] for d in dates], rotation=45, ha="right", fontsize=8)
    ax.set_xlabel(L("날짜 (2024-06-)", "Date (2024-06-)"))
    ax.set_ylabel(L("총 이동 거리 (km)", "Total Distance (km)"))
    ax.set_title(L("일별 예인선 이동 거리 분류 (단일 예선 기준)", "Daily Tugboat Distance Breakdown (Single-tug)"))
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    total = dist["travel_km"] + dist["service_km"]
    for i, (xi, tot) in enumerate(zip(x, total)):
        ax.text(xi, tot + 0.2, f"{tot:.1f}", ha="center", va="bottom", fontsize=6.5)

    fig.tight_layout()
    out = RESULTS_DIR / "daily_distance_km.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Chart 3: solution_overview.png  (3-panel)
# ---------------------------------------------------------------------------

def plot_solution_overview(
    baseline: pd.DataFrame,
    optimized: pd.DataFrame,
    dist: pd.DataFrame,
) -> None:
    # --- shared date axis ---
    bl_daily = (
        baseline.groupby("date")["delay_min"]
        .mean()
        .reset_index()
        .rename(columns={"delay_min": "baseline_avg_min"})
    )
    opt_daily = optimized.copy()
    opt_daily["opt_avg_min"] = (opt_daily["wait_h"] * 60.0) / opt_daily["n"].clip(lower=1)
    merged = pd.merge(
        bl_daily,
        opt_daily[["date", "opt_avg_min", "n"]],
        on="date",
        how="inner",
    ).sort_values("date")

    dates_str = merged["date"].tolist()
    x_idx = np.arange(len(dates_str))
    x_labels = [d[5:] for d in dates_str]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        L("항구 예인선 스케줄 최적화 요약 (2024년 6월)", "Harbor Tugboat Scheduling Optimization — June 2024"),
        fontsize=13,
        fontweight="bold",
    )

    # --- Panel 1: scatter/dot timeline of per-day avg wait ---
    ax1 = axes[0]
    ax1.plot(
        x_idx,
        merged["baseline_avg_min"],
        "o-",
        color="#E57373",
        linewidth=1.5,
        markersize=6,
        label=L("기준", "Baseline"),
    )
    ax1.plot(
        x_idx,
        merged["opt_avg_min"],
        "s-",
        color="#42A5F5",
        linewidth=1.5,
        markersize=6,
        label=L("최적화", "Optimized"),
    )
    ax1.fill_between(
        x_idx,
        merged["opt_avg_min"],
        merged["baseline_avg_min"],
        alpha=0.15,
        color="#7E57C2",
        label=L("개선폭", "Improvement"),
    )
    ax1.set_xticks(x_idx)
    ax1.set_xticklabels(x_labels, rotation=60, ha="right", fontsize=7)
    ax1.set_ylabel(L("평균 대기 (분/선박)", "Avg Wait (min/vessel)"))
    ax1.set_title(L("일별 선박 평균 대기 시간", "Daily Avg Wait per Vessel"))
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    # --- Panel 2: cumulative wait hours (baseline vs optimized) ---
    ax2 = axes[1]
    # baseline total wait hours per day = avg_min * n / 60
    n_by_date = optimized.set_index("date")["n"]
    merged["bl_total_h"] = merged.apply(
        lambda r: r["baseline_avg_min"] * n_by_date.get(r["date"], r["n"] if "n" in r else 1) / 60.0,
        axis=1,
    )
    merged["opt_total_h"] = optimized.set_index("date").reindex(merged["date"])["wait_h"].values

    cum_bl = merged["bl_total_h"].cumsum().values
    cum_opt = merged["opt_total_h"].cumsum().values

    ax2.plot(x_idx, cum_bl, "o-", color="#E57373", linewidth=2, markersize=5, label=L("기준 누적", "Baseline Cumul."))
    ax2.plot(x_idx, cum_opt, "s-", color="#42A5F5", linewidth=2, markersize=5, label=L("최적화 누적", "Optimized Cumul."))
    ax2.fill_between(x_idx, cum_opt, cum_bl, alpha=0.15, color="#26A69A")
    ax2.set_xticks(x_idx)
    ax2.set_xticklabels(x_labels, rotation=60, ha="right", fontsize=7)
    ax2.set_ylabel(L("누적 대기 시간 (시간)", "Cumulative Wait (hours)"))
    ax2.set_title(L("누적 선박 대기 시간 (24일)", "Cumulative Vessel Wait Hours (24 days)"))
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    # Annotate final savings
    saving_h = cum_bl[-1] - cum_opt[-1]
    ax2.annotate(
        f"{L('절감', 'Saved')}: {saving_h:.1f}h",
        xy=(x_idx[-1], cum_opt[-1]),
        xytext=(x_idx[-1] - 4, (cum_bl[-1] + cum_opt[-1]) / 2),
        arrowprops=dict(arrowstyle="->", color="#555"),
        fontsize=8,
        color="#1B5E20",
    )

    # --- Panel 3: distance breakdown pie ---
    ax3 = axes[2]
    dist_sorted = dist.sort_values("date")
    total_travel = dist_sorted["travel_km"].sum()
    total_service = dist_sorted["service_km"].sum()
    # Rough return-to-anchorage estimate: equal to travel distance
    total_return = total_travel

    sizes = [total_travel, total_service, total_return]
    labels = [
        L("이동 (정계지→작업)", "Travel (anch→berth)"),
        L("작업 중", "Service"),
        L("귀환 추정 (작업→정계지)", "Return est."),
    ]
    colors = ["#66BB6A", "#FFA726", "#78909C"]
    explode = (0.04, 0.04, 0.04)

    wedges, texts, autotexts = ax3.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 8},
    )
    for at in autotexts:
        at.set_fontsize(8)
    ax3.set_title(L("이동 거리 분류 (단일 예선, 6월 합계)", "Distance Breakdown (Single-tug, June total)"))

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = RESULTS_DIR / "solution_overview.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading baseline data...")
    baseline = load_baseline()
    print(f"  Single-tug rows: {len(baseline)}")

    print("Loading optimized results...")
    optimized = load_optimized()
    print(f"  Days in JSON: {len(optimized)}")

    print("Computing distance data...")
    dist = load_distance()

    print("Generating chart 1: daily_wait_comparison.png")
    plot_daily_wait(baseline, optimized)

    print("Generating chart 2: daily_distance_km.png")
    plot_daily_distance(dist)

    print("Generating chart 3: solution_overview.png")
    plot_solution_overview(baseline, optimized, dist)

    print("All charts saved to results/")


if __name__ == "__main__":
    main()
