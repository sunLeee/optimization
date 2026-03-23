"""
수렴 곡선 시각화 — SolveResult.metadata 기반.

SolveResult.metadata["convergence_history"]의 비용 이력을 matplotlib으로
수렴 곡선으로 저장한다. AW-007 준수: libs/utils/에만 의존.

사용 예:
    from libs.visualization.convergence import plot_convergence
    plot_convergence(result, out_path="results/convergence_ALNS.png")

Phase 7 개선 예정:
    ALNSWithSpeedOptimizer에 iteration별 콜백 추가 후
    metadata["convergence_history"]에 Per-iteration 비용 기록 가능해짐.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def plot_convergence(
    result: object,
    out_path: str = "results/convergence.png",
    title: str | None = None,
    show: bool = False,
) -> str | None:
    """SolveResult.metadata에서 수렴 곡선을 PNG로 저장.

    metadata["convergence_history"] 포맷:
        [{"iter": int, "cost": float, "elapsed_sec": float}, ...]

    또는 Benders용:
        metadata["lb_history"]: list[float]
        metadata["ub_history"]: list[float]

    Args:
        result: SolveResult 인스턴스
        out_path: PNG 저장 경로
        title: 그래프 제목 (None이면 solver_name 사용)
        show: True면 plt.show() 호출

    Returns:
        저장된 파일 경로 (성공 시), None (데이터 없을 때)

    Raises:
        ImportError: matplotlib 미설치 시 경고 후 None 반환
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib 미설치. `uv add matplotlib`로 설치 필요.")
        return None

    import pathlib

    metadata: dict = getattr(result, "metadata", {})
    solver_name: str = getattr(result, "solver_name", "Unknown")

    # ── 데이터 추출 ──────────────────────────────────────────
    history = metadata.get("convergence_history", [])
    lb_history = metadata.get("lb_history", [])
    ub_history = metadata.get("ub_history", [])

    has_history = bool(history)
    has_lb_ub = bool(lb_history) and bool(ub_history)

    if not has_history and not has_lb_ub:
        logger.warning(
            "%s: metadata에 수렴 이력 없음 "
            "(convergence_history / lb_history / ub_history). "
            "Phase 7 개선 후 Per-iteration 로깅 가능.",
            solver_name,
        )
        return None

    # ── 그래프 생성 ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    _title = title or f"수렴 곡선 — {solver_name}"
    ax.set_title(_title, fontsize=12)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Cost")

    if has_history:
        iters = [h["iter"] for h in history]
        costs = [h["cost"] for h in history]
        ax.plot(iters, costs, "b-o", label="Cost", markersize=4)

    if has_lb_ub:
        iters_bd = list(range(len(lb_history)))
        ax.plot(iters_bd, lb_history, "g--", label="Lower Bound", linewidth=1.5)
        ax.plot(iters_bd, ub_history, "r--", label="Upper Bound", linewidth=1.5)
        ax.fill_between(iters_bd, lb_history, ub_history, alpha=0.1, color="gray")

    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)

    # ── 저장 ─────────────────────────────────────────────────
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    logger.info("수렴 곡선 저장: %s", out)
    return str(out)


def plot_convergence_comparison(
    results: list[object],
    out_path: str = "results/convergence_comparison.png",
    title: str = "알고리즘별 수렴 비교",
    show: bool = False,
) -> str | None:
    """여러 SolveResult의 수렴 곡선을 한 그래프에 비교.

    Args:
        results: SolveResult 리스트
        out_path: PNG 저장 경로
        title: 그래프 제목
        show: True면 plt.show() 호출

    Returns:
        저장된 파일 경로 (성공 시), None (데이터 없을 때)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib 미설치.")
        return None

    import pathlib

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Cost")

    plotted = 0
    for result in results:
        metadata: dict = getattr(result, "metadata", {})
        solver_name: str = getattr(result, "solver_name", "Unknown")
        history = metadata.get("convergence_history", [])
        if not history:
            continue
        iters = [h["iter"] for h in history]
        costs = [h["cost"] for h in history]
        ax.plot(iters, costs, "-o", label=solver_name, markersize=3)
        plotted += 1

    if plotted == 0:
        logger.warning("비교할 수렴 이력 데이터 없음.")
        plt.close(fig)
        return None

    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)

    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    logger.info("수렴 비교 곡선 저장: %s", out)
    return str(out)
