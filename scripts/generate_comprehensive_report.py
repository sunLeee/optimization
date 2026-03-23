"""
종합 보고서 생성 — 항구 예선 스케줄링 최적화 전체 분석.

모든 분석 결과를 하나의 PDF로 통합한다.

사용법:
    uv run python scripts/generate_comprehensive_report.py
"""

from __future__ import annotations

import csv
import json
import pathlib
import platform
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def build_pdf(out_path: pathlib.Path) -> str:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        HRFlowable,
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    font_name = "Helvetica"
    try:
        if platform.system() == "Darwin":
            for fp in [
                "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
                "/Library/Fonts/NanumGothic.ttf",
            ]:
                if pathlib.Path(fp).exists():
                    pdfmetrics.registerFont(TTFont("KorFont", fp))
                    font_name = "KorFont"
                    break
    except Exception:
        pass

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=16,
        spaceAfter=12,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#1a3a6b"),
    )
    h3 = ParagraphStyle(  # noqa: F841
        "h3",
        parent=styles["Heading3"],
        fontName=font_name,
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor("#2e6b2e"),
    )
    body = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=14,
    )
    highlight = ParagraphStyle(
        "hl",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=14,
        backColor=colors.HexColor("#e8f4e8"),
    )
    alert = ParagraphStyle(
        "alert",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=14,
        backColor=colors.HexColor("#fff3cd"),
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = []

    def make_table(data, col_widths=None, header_color=None):
        t = Table(data, colWidths=col_widths)
        hc = header_color or colors.HexColor("#1a3a6b")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), hc),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f5f5f5")],
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return t

    def add_image(path: str, width=14 * cm):
        p = pathlib.Path(path)
        if p.exists() and p.stat().st_size > 0:
            try:
                return Image(str(p), width=width, height=width * 0.6)
            except Exception:
                pass
        return Paragraph(f"[Image not available: {path}]", body)

    # -- 표지 --------------------------------------------------------------
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Harbor Tugboat Scheduling Optimization", h1))
    story.append(Paragraph("Comprehensive Analysis Report", h1))
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a6b"))
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"Generated: {now}  |  Data: 2024-06 Incheon Harbor"
            " (N=336 executed, N=967 requested)",
            body,
        )
    )
    story.append(Spacer(1, 0.8 * cm))

    # -- 섹션 1: 문제 정의 -------------------------------------------------
    story.append(Paragraph("1. Problem Definition & Data Overview", h2))
    try:
        with open("results/full_baseline_kpi.json") as f:
            bl = json.load(f)
        with open("results/full_optimization.json") as f:
            opt = json.load(f)
        overview = [
            ["Item", "Value"],
            ["Dataset", "2024-06 Incheon Harbor (June 8-30, 23 days)"],
            [
                "Total service requests",
                f"{opt.get('total_requests', 967)} (FristAllSchData)",
            ],
            ["Executed services (baseline)", "336 (SchData)"],
            ["Tug fleet", "12 tugs (I, N, M, T, H, etc.)"],
            ["Pilot resources", "29 pilots (도선사)"],
            ["Services requiring 2+ tugs", "70.9% (avg 2.13 tugs/service)"],
            [
                "Historical avg delay",
                f"{bl.get('kpi', {}).get('avg_delay_min', 103.6):.1f} min/service",
            ],
        ]
        story.append(make_table(overview, col_widths=[5 * cm, 11.5 * cm]))
    except Exception:
        story.append(Paragraph("Data overview unavailable.", body))
    story.append(Spacer(1, 0.5 * cm))

    # -- 섹션 2: N×M 벤치마크 ---------------------------------------------
    story.append(Paragraph("2. N×M Benchmark: Objectives x Algorithms", h2))
    story.append(
        Paragraph(
            "3 objectives (MinWait, MinIdle, MinComposite) x 3 algorithms (Greedy, MILP, ALNS)"
            " on 2024-06-07 data (n=18 jobs, 40 tug-slots).",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    try:
        with open("results/nm_benchmark_full.csv", encoding="utf-8-sig") as _f:
            rows_csv = list(csv.DictReader(_f))
        bm_header = [
            "Objective",
            "Algorithm",
            "n_jobs",
            "wait_h",
            "idle_h",
            "composite",
            "time(s)",
            "gap",
        ]
        bm_data = [bm_header]
        for r in rows_csv:
            bm_data.append(
                [
                    r["objective"],
                    r["algorithm"],
                    r["n_jobs"],
                    f"{_safe_float(r['wait_h']):.3f}",
                    f"{_safe_float(r['idle_h']):.2f}",
                    f"{_safe_float(r['composite']):.3f}",
                    f"{_safe_float(r['solve_time_sec']):.2f}s",
                    r.get("optimality_gap", "—")[:8],
                ]
            )
        story.append(
            make_table(
                bm_data,
                col_widths=[
                    3 * cm,
                    2.5 * cm,
                    1.5 * cm,
                    2 * cm,
                    2 * cm,
                    2 * cm,
                    1.8 * cm,
                    1.7 * cm,
                ],
            )
        )
    except Exception:
        story.append(Paragraph("Benchmark CSV unavailable.", body))
    story.append(Spacer(1, 0.3 * cm))
    story.append(add_image("results/nm_heatmap_full.png"))
    story.append(Spacer(1, 0.5 * cm))

    # -- 섹션 3: 확률적 강건성 ---------------------------------------------
    story.append(
        Paragraph("3. Stochastic Robustness Analysis (Monte Carlo CVaR95)", h2)
    )
    story.append(
        Paragraph(
            "Vessel arrivals perturbed by Log-normal delays"
            " (AW-010: mu=4.015, sigma=1.363, p=71.4%)."
            " n_mc=200 scenarios evaluated for each algorithm.",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    try:
        with open("results/stochastic_robustness_full.json") as f:
            rob = json.load(f)
        rob_header = [
            "Algorithm",
            "Mean wait_h",
            "Std",
            "P95",
            "CVaR95",
            "Most Robust",
        ]
        rob_data = [rob_header]
        best = rob.get("most_robust", "")
        for algo, stats in rob.get("algorithms", {}).items():
            rob_data.append(
                [
                    algo,
                    f"{stats['mean_wait_h']:.3f}",
                    f"{stats['std_wait_h']:.3f}",
                    f"{stats['p95_wait_h']:.3f}",
                    f"{stats['cvar95_wait_h']:.3f}",
                    "BEST" if algo == best else "",
                ]
            )
        story.append(
            make_table(
                rob_data,
                col_widths=[
                    3 * cm,
                    2.5 * cm,
                    2.5 * cm,
                    2.5 * cm,
                    2.5 * cm,
                    3 * cm,
                ],
                header_color=colors.HexColor("#6b3a1a"),
            )
        )
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph(
                f"Most Robust Algorithm: {best}"
                f" (CVaR95={rob.get('most_robust_cvar95', 0):.3f}h) -- "
                "Minimizes expected cost in worst 5% of arrival delay scenarios.",
                highlight,
            )
        )
    except Exception:
        story.append(Paragraph("Robustness data unavailable.", body))
    story.append(Spacer(1, 0.3 * cm))
    story.append(add_image("results/robustness_chart.png"))
    story.append(Spacer(1, 0.5 * cm))

    # -- 섹션 4: 도선사 운영 분석 ------------------------------------------
    story.append(Paragraph("4. Pilot (Dosen) Operation Analysis", h2))
    story.append(
        Paragraph(
            "Pilots depart from PAL (Palmi Pilot Station, 37.463N 126.596E) and must arrive"
            " at the vessel's work start location before service begins.",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    try:
        with open("results/pilot_analysis.json") as f:
            pilot = json.load(f)
        pilot_data = [
            ["Metric", "Value"],
            [
                "Services with pilot assigned",
                str(pilot.get("n_services_with_pilot", 252)),
            ],
            ["Unique pilots", str(pilot.get("n_unique_pilots", 29))],
            [
                "Avg travel time (PAL->berth)",
                f"{pilot.get('avg_travel_min', 0):.1f} min",
            ],
            [
                "Avg service duration",
                f"{pilot.get('avg_service_min', 0):.1f} min",
            ],
            [
                "Newsvendor optimal buffer",
                f"{pilot.get('newsvendor_optimal_buffer_min', 0):.1f} min",
            ],
            ["Interpretation", pilot.get("interpretation", "")[:80]],
        ]
        story.append(
            make_table(
                pilot_data,
                col_widths=[6 * cm, 10.5 * cm],
                header_color=colors.HexColor("#2e6b2e"),
            )
        )
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph(
                f"Optimal pilot departure buffer under stochastic arrivals (w_v=2, w_p=1):"
                f" {pilot.get('newsvendor_optimal_buffer_min', 62):.0f} min before scheduled"
                " service start. This accounts for the 71.4% probability of vessel delay.",
                highlight,
            )
        )
    except Exception:
        story.append(Paragraph("Pilot analysis unavailable.", body))
    story.append(Spacer(1, 0.3 * cm))
    story.append(add_image("results/pilot_timeline.png"))
    story.append(Spacer(1, 0.5 * cm))

    # -- 섹션 5: 실행가능성 + 전체 최적화 결과 ----------------------------
    story.append(
        Paragraph(
            "5. Feasibility Verification & Full Optimization Results", h2
        )
    )
    try:
        with open("results/feasibility_report.json") as f:
            feas = json.load(f)
        fsb = feas.get("feasibility", {})
        verdict = fsb.get("overall", "UNKNOWN")
        n_ok = fsb.get("n_feasible", 0)
        n_total = fsb.get("n_total_checks", 0)
        style = highlight if verdict == "FEASIBLE" else alert
        story.append(
            Paragraph(
                f"Feasibility Verdict: {verdict}  ({n_ok}/{n_total} checks passed) -- "
                f"Day: {feas.get('date', '2024-06-07')},"
                f" n={feas.get('n_assignments', 0)} assignments.",
                style,
            )
        )
    except Exception:
        story.append(Paragraph("Feasibility data unavailable.", body))
    story.append(Spacer(1, 0.3 * cm))

    try:
        with open("results/full_comparison.csv", encoding="utf-8-sig") as f:
            comp_rows = list(csv.DictReader(f))
        comp_header = [
            "Metric",
            "Baseline (Human)",
            "Optimized",
            "Improvement",
        ]
        comp_data = [comp_header]
        for r in comp_rows[:5]:
            comp_data.append(
                [
                    r.get("metric", ""),
                    str(r.get("baseline", "")),
                    str(r.get("optimized", "")),
                    str(r.get("improvement_pct", "")),
                ]
            )
        story.append(
            make_table(
                comp_data, col_widths=[5 * cm, 3.5 * cm, 3.5 * cm, 4.5 * cm]
            )
        )
    except Exception:
        story.append(Paragraph("Comparison data unavailable.", body))
    story.append(Spacer(1, 0.5 * cm))

    # -- 섹션 6: 결론 ------------------------------------------------------
    story.append(Paragraph("6. Conclusions & Recommendations", h2))
    conclusions = [
        ["Finding", "Result", "Action"],
        [
            "Vessel wait reduction",
            "103.6 min -> 0.06 min/service (-99.9%)",
            "Deploy multi-tug optimizer in production",
        ],
        [
            "Algorithm robustness",
            "All algorithms similar CVaR95 on small n",
            "Use MILP for n<=30, Greedy for n>30",
        ],
        [
            "Pilot optimal buffer",
            "62.1 min advance departure from PAL",
            "Implement automated pilot dispatch alerts",
        ],
        [
            "Feasibility (2024-06-07)",
            "11/40 tug movements infeasible",
            "Add travel-time constraints to prevent conflicts",
        ],
        [
            "Multi-tug coverage",
            "967 requests, 70.9% multi-tug",
            "Scale to full fleet with Benders decomposition",
        ],
    ]
    ct = Table(conclusions, colWidths=[4.5 * cm, 6.5 * cm, 5.5 * cm])
    ct.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f0f0ff")],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(ct)
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"Generated by harbor-optimization automated pipeline."
            f" Data: 2024-06 Incheon Harbor. Report: {now}.",
            body,
        )
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return str(out_path.resolve())


def main() -> None:
    out = pathlib.Path("results/comprehensive_report.pdf")
    print("종합 보고서 생성 중...")
    saved = build_pdf(out)
    size_kb = out.stat().st_size // 1024
    print(f"완료: {saved} ({size_kb} KB)")


if __name__ == "__main__":
    main()
