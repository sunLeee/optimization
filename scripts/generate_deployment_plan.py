"""
항구 예인선 스케줄링 최적화 시스템 — 운영 배치 계획서 (PDF) 생성.

실측 데이터 기반 KPI와 구현 로드맵, 운영 매뉴얼, 위험 평가,
비용편익 분석을 포함한 경영진/IT팀 제출용 공식 문서를 생성한다.

사용법:
    uv run python scripts/generate_deployment_plan.py [--lang ko|en]
"""

from __future__ import annotations

import argparse
import pathlib
import platform
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

# ── 언어 설정 (argparse로 덮어씀) ─────────────────────────────────────────────
lang: str = "en"


def t(ko_text: str, en_text: str) -> str:
    """언어 설정에 따라 한국어 또는 영어 텍스트를 반환한다."""
    return ko_text if lang == "ko" else en_text


SECTION_TITLES = {
    "ko": [
        "1. 경영진 요약",
        "2. 현황 분석",
        "3. 시스템 아키텍처",
        "4. 구현 로드맵 (4단계, 24개월)",
        "5. 디스패처 운영 매뉴얼",
        "6. 위험도 평가",
        "7. KPI 대시보드 설계",
        "8. 비용편익 분석",
        "9. 데이터 요구사항",
        "10. 부록: API 명세",
    ],
    "en": [
        "1. Executive Summary",
        "2. Current State Analysis",
        "3. System Architecture",
        "4. Implementation Roadmap (4 Phases, 24 Months)",
        "5. Operations Manual for Dispatchers",
        "6. Risk Assessment",
        "7. KPI Dashboard Design",
        "8. Cost-Benefit Analysis",
        "9. Data Requirements",
        "10. Appendix: API Specifications",
    ],
}

# ── 상수 ──────────────────────────────────────────────────────────────────────
NAVY = "#1a3a6b"
LIGHT_NAVY = "#2e5a9e"
LIGHT_BLUE = "#e8f0fb"
GREEN = "#1a6b2e"
LIGHT_GREEN = "#e8f8ec"
AMBER = "#b85c00"
LIGHT_AMBER = "#fff3e0"
RED_DARK = "#8b0000"
LIGHT_RED = "#fde8e8"
GREY_LIGHT = "#f5f5f5"
GREY_MID = "#dddddd"
WHITE = "#ffffff"

# 실측 KPI
BASELINE_AVG_DELAY_MIN = 103.6
OPTIMIZED_AVG_DELAY_MIN = 4.8
DELAY_REDUCTION_PCT = 95.4
TOTAL_WAIT_BASELINE_H = 580.0  # 총 580h / 336 서비스
TOTAL_SERVICES = 336
CVAR95_H = 37.3
PILOT_BUFFER_MIN = 62.1
FLEET_TUGS = 12
FLEET_PILOTS = 29
FLEET_BERTHS = 111
FLEET_ANCHORAGES = 4

OUT_PATH = pathlib.Path("results/deployment_plan_{lang}.pdf")


# ── 폰트 등록 ─────────────────────────────────────────────────────────────────

def _register_font() -> str:
    """시스템에 맞는 한글/기본 폰트를 등록하고 폰트 이름을 반환한다."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if platform.system() == "Darwin":
        candidates = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/NanumGothic.ttf",
        ]
        for fp in candidates:
            if pathlib.Path(fp).exists():
                try:
                    pdfmetrics.registerFont(TTFont("KorFont", fp))
                    return "KorFont"
                except Exception:
                    continue
    return "Helvetica"


# ── 스타일 팩토리 ─────────────────────────────────────────────────────────────

def _make_styles(font_name: str) -> dict:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    base = getSampleStyleSheet()

    def ps(name: str, **kwargs) -> ParagraphStyle:
        return ParagraphStyle(name, parent=base["Normal"], fontName=font_name, **kwargs)

    return {
        "cover_title": ps(
            "cover_title",
            fontSize=22,
            leading=28,
            spaceAfter=8,
            textColor=colors.HexColor(NAVY),
        ),
        "cover_sub": ps(
            "cover_sub",
            fontSize=13,
            leading=18,
            spaceAfter=6,
            textColor=colors.HexColor(LIGHT_NAVY),
        ),
        "cover_meta": ps(
            "cover_meta",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#555555"),
        ),
        "h1": ps(
            "h1",
            fontSize=13,
            leading=18,
            spaceBefore=16,
            spaceAfter=6,
            textColor=colors.HexColor(NAVY),
        ),
        "h2": ps(
            "h2",
            fontSize=10,
            leading=14,
            spaceBefore=10,
            spaceAfter=4,
            textColor=colors.HexColor(LIGHT_NAVY),
        ),
        "body": ps("body", fontSize=8.5, leading=13),
        "body_small": ps("body_small", fontSize=7.5, leading=11),
        "highlight": ps(
            "highlight",
            fontSize=8.5,
            leading=13,
            backColor=colors.HexColor(LIGHT_GREEN),
            leftIndent=6,
            rightIndent=6,
        ),
        "callout": ps(
            "callout",
            fontSize=8.5,
            leading=13,
            backColor=colors.HexColor(LIGHT_AMBER),
            leftIndent=6,
            rightIndent=6,
        ),
        "footer": ps(
            "footer",
            fontSize=7,
            leading=10,
            textColor=colors.HexColor("#888888"),
        ),
    }


# ── 공통 테이블 스타일 ────────────────────────────────────────────────────────

def _tbl_base(
    font_name: str,
    header_color: str = NAVY,
    alt_color: str = GREY_LIGHT,
    font_size: int = 8,
) -> list:
    from reportlab.lib import colors

    return [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(GREY_MID)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(alt_color)]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]


# ── 페이지 템플릿 (헤더/푸터) ──────────────────────────────────────────────────

def _make_doc(out_path: pathlib.Path, font_name: str):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate

    def _on_page(canvas, doc):
        canvas.saveState()
        w, _ = A4
        # 상단 헤더 라인
        canvas.setFillColor(colors.HexColor(NAVY))
        canvas.rect(0, A4[1] - 0.6 * cm, w, 0.6 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(font_name, 7)
        canvas.drawString(1.5 * cm, A4[1] - 0.42 * cm,
                          t("인천항 예선 스케줄링 최적화 — 배치 계획서",
                            "Harbor Tugboat Scheduling Optimization — Deployment Plan"))
        canvas.drawRightString(w - 1.5 * cm, A4[1] - 0.42 * cm,
                               "CONFIDENTIAL")
        # 하단 푸터 라인
        canvas.setFillColor(colors.HexColor(GREY_MID))
        canvas.rect(0, 0.5 * cm, w, 0.02 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.setFont(font_name, 7)
        canvas.drawString(1.5 * cm, 0.3 * cm,
                          f"Generated: {datetime.now().strftime('%Y-%m-%d')}  |  "
                          "Data: 2024-06 Busan/Incheon Harbor (N=336 services)")
        canvas.drawRightString(w - 1.5 * cm, 0.3 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.5 * cm,
        onFirstPage=_on_page,
        onLaterPages=_on_page,
    )
    return doc


# ── 섹션별 빌더 ───────────────────────────────────────────────────────────────

def _cover(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    fn = styles["body"].fontName

    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(
        t("인천항 예선 스케줄링 최적화<br/>실 운행 적용 계획서",
          "Harbor Tugboat Scheduling<br/>Optimization System"), styles["cover_title"]
    ))
    story.append(Paragraph(
        t("운영 배치 계획서", "Operational Deployment Plan"), styles["cover_sub"]
    ))
    story.append(HRFlowable(
        width="100%", thickness=2, color=colors.HexColor(NAVY), spaceAfter=10
    ))

    meta_data = [
        ["Document Type", "Operational Deployment Plan"],
        ["Version", "1.0 (2026-03-22)"],
        ["Classification", "Confidential — Management & IT Only"],
        ["Data Basis", "2024-06 Harbor Operations (N=336 services)"],
        ["Prepared By", "Harbor Optimization Project Team"],
        ["Target Audience", "Harbor Management, IT Operations, Dispatch Supervisors"],
    ]
    mt = Table(meta_data, colWidths=[4 * cm, 11 * cm])
    mt.setStyle(TableStyle(_tbl_base(fn, header_color=LIGHT_NAVY, font_size=8)))
    # override header back to data style for meta table
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(LIGHT_BLUE)),
        ("FONTNAME", (0, 0), (-1, -1), fn),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(GREY_MID)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "This document presents the full deployment plan for transitioning the harbor "
        "tugboat scheduling system from manual dispatch to AI-assisted optimization. "
        "It is structured for both management decision-making and IT implementation teams.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.4 * cm))


def _section_exec_summary(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][0], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "This system applies Mixed Integer Linear Programming (MILP), Adaptive Large "
        "Neighborhood Search (ALNS), and Benders Decomposition to optimize tug dispatch "
        "across 111 berths and 4 anchorages. Validated on 336 real service records from "
        "a major Korean harbor (2024-06), the system reduces average vessel wait time "
        "from 103.6 minutes to 4.8 minutes — a 95.4% improvement.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    kpi_data = [
        ["KPI", "Baseline (Historical)", "Optimized", "Change"],
        ["Avg vessel delay", "103.6 min/vessel", "4.8 min/vessel", "-95.4%"],
        ["Total fleet wait", "580 h (N=336)", "~26 h", "-95.5%"],
        ["Schedule feasibility", "Partial (manual)", "100%", "+100%"],
        ["Pilot buffer lead time", "Variable (uncontrolled)", "62.1 min (optimal)", "Defined"],
        ["CVaR95 (stochastic)", "Unmeasured", "37.3 h", "Quantified"],
        ["Fleet: Tugs / Pilots", "12 tugs, 29 pilots", "Same fleet — better use", "No capex"],
        ["Berths / Anchorages", "111 berths, 4 anchorages", "Same infrastructure", "No capex"],
    ]
    fn = styles["body"].fontName
    kt = Table(kpi_data, colWidths=[4.5 * cm, 4 * cm, 3.8 * cm, 2.7 * cm])
    kt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_GREEN)))
    kt.setStyle(TableStyle([
        ("BACKGROUND", (3, 1), (3, -1), colors.HexColor(LIGHT_GREEN)),
        ("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor(GREEN)),
    ]))
    story.append(kt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "ROI Snapshot: Conservative estimate of $67M/year in vessel demurrage savings "
        "(30% realization rate of 98.8 min/vessel × 15 vessels/day × 365 days × "
        "$5,000/hr). System development cost: $2-3M one-time. Payback period: < 1 year.",
        styles["highlight"],
    ))
    story.append(Spacer(1, 0.2 * cm))


def _section_current_state(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][1], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph("2.1 Operational Pain Points", styles["h2"]))
    story.append(Paragraph(
        "Current manual dispatch relies on dispatcher experience and radio communication. "
        "This results in suboptimal tug assignments, unpredictable pilot lead times, "
        "and no systematic handling of ETA uncertainty.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.2 * cm))

    pain_data = [
        ["Problem Area", "Current Situation", "Impact"],
        ["Tug assignment", "Manual radio dispatch per vessel", "103.6 min avg delay"],
        ["Pilot lead time", "Ad hoc, no standard buffer", "Unpredictable service start"],
        ["ETA uncertainty", "No stochastic model", "Cascading delays"],
        ["Fleet visibility", "Radio/paper-based tracking", "No real-time optimization"],
        ["Data integration", "Separate port mgmt / tug logs", "Manual reconciliation daily"],
        ["Scalability", "Dispatcher saturation at peak", "Service bottlenecks"],
    ]
    fn = styles["body"].fontName
    pt = Table(pain_data, colWidths=[3.5 * cm, 5.5 * cm, 6 * cm])
    pt.setStyle(TableStyle(_tbl_base(fn, header_color="#8b2000", alt_color=LIGHT_RED)))
    story.append(pt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("2.2 Fleet Inventory", styles["h2"]))
    fleet_data = [
        ["Resource", "Count", "Current Utilization", "Notes"],
        ["Tugboats", "12", "~65% (estimated)", "Mix of bow/stern tugs"],
        ["Pilots", "29", "~55% active hours", "Certified harbor pilots"],
        ["Berths", "111", "Varies by tide/season", "4 berth zones"],
        ["Anchorages", "4", "Peak: 3 active", "Waiting area before berth"],
        ["Dispatch controllers", "3 shifts", "Manual radio", "Experience-dependent"],
    ]
    ft = Table(fleet_data, colWidths=[3 * cm, 2 * cm, 4 * cm, 6 * cm])
    ft.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE)))
    story.append(ft)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("2.3 ETA Distribution (Empirical — 2024-06, N=336)", styles["h2"]))
    eta_data = [
        ["Parameter", "Value", "Interpretation"],
        ["Distribution", "Log-normal", "Right-skewed delay pattern"],
        ["mu_log", "4.015", "Log-scale delay mean"],
        ["sigma_log", "1.363", "High variability in delays"],
        ["Median delay", "55.4 min", "Typical vessel late arrival"],
        ["Delay probability", "71.4%", "Over 2/3 of vessels arrive late"],
        ["Early arrival", "28.6%", "Significant early-arrival minority"],
        ["Clip range", "[-6h, +6h]", "Covers 89.6% of actual variance"],
    ]
    et = Table(eta_data, colWidths=[3.5 * cm, 3 * cm, 8.5 * cm])
    et.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT)))
    story.append(et)
    story.append(Spacer(1, 0.2 * cm))


def _section_architecture(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][2], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "The system is built on a three-tier optimization stack, selected based on "
        "problem size (n = number of vessels in the scheduling window):",
        styles["body"],
    ))
    story.append(Spacer(1, 0.2 * cm))

    tier_data = [
        ["Tier", "Problem Size", "Algorithm", "Solver", "Typical Solve Time", "Use Case"],
        ["Tier 1", "n < 10", "Exact MILP", "HiGHS (free)", "< 5 sec", "Morning peak, short window"],
        ["Tier 2", "n = 10–50", "ALNS + eco-speed", "Pyomo/HiGHS", "< 60 sec", "Normal operations"],
        ["Tier 3", "n > 50", "Benders Decomp.", "HiGHS + IPOPT", "< 10 min", "Surge/holiday events"],
        ["Fallback", "Any", "Greedy heuristic", "Custom Python", "< 5 sec", "Real-time 15-min replan"],
    ]
    fn = styles["body"].fontName
    tt = Table(tier_data, colWidths=[1.5 * cm, 2.5 * cm, 3.5 * cm, 2.8 * cm, 3 * cm, 3.7 * cm])
    tt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE)))
    story.append(tt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("3.1 Module Dependency Map", styles["h2"]))
    story.append(Paragraph(
        "All dependency arrows are unidirectional (no circular imports). "
        "This ensures each layer can be tested and deployed independently.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.15 * cm))

    mod_data = [
        ["Layer", "Module", "Responsibility", "Key Classes"],
        ["Orchestration", "libs/stochastic/", "Rolling horizon + 2-stage SP", "RollingHorizonOrchestrator, PortState"],
        ["Scheduling", "libs/scheduling/", "BAP + TSP-T MILP formulation", "BerthAllocationModel, TugScheduleModel"],
        ["Routing", "libs/routing/", "VRPTW + ALNS", "VRPTWModel, ALNSWithSpeedOptimizer"],
        ["Fuel", "libs/fuel/", "F(v,d) = alpha * v^2.5 * d", "fuel_consumption, mccormick_linearize"],
        ["Utils", "libs/utils/", "Shared contracts & interfaces", "TimeWindowSpec, SchedulingToRoutingSpec"],
    ]
    mt = Table(mod_data, colWidths=[3 * cm, 3.5 * cm, 4.5 * cm, 4 * cm])
    mt.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT)))
    story.append(mt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("3.2 Data Flow", styles["h2"]))
    flow_data = [
        ["Step", "Data Source", "Destination", "Frequency"],
        ["1. Vessel schedule ingest", "Port Management System (PMS)", "Optimizer input queue", "Hourly + on arrival"],
        ["2. Day-ahead optimization", "Next 24h schedule", "Tug assignment plan", "06:00 daily"],
        ["3. AIS position feed", "AIS transponder network", "Real-time tug tracker", "Continuous (30-sec)"],
        ["4. Rolling replan", "Current tug positions + ETA", "Greedy reassignment", "Every 15 min"],
        ["5. Dispatch alert", "Assignment plan", "Tug captain mobile app", "Per vessel (auto)"],
        ["6. Pilot alert", "Assignment plan + 62.1 min buffer", "Pilot pager/app", "Per vessel (auto)"],
        ["7. KPI logging", "Actual vs planned times", "Operations DB", "Per service completion"],
    ]
    fl = Table(flow_data, colWidths=[3.5 * cm, 3.8 * cm, 3.8 * cm, 3.9 * cm])
    fl.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE)))
    story.append(fl)
    story.append(Spacer(1, 0.2 * cm))


def _section_roadmap(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][3], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "The rollout follows a four-phase approach over 12 months, starting with "
        "infrastructure and ending with full fleet integration and continuous improvement.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    phases = [
        {
            "phase": "Phase 1",
            "period": "Month 1–3",
            "name": "Infrastructure & Integration",
            "color": LIGHT_BLUE,
            "milestones": [
                "Deploy optimization server (Linux VM, 16-core, 64 GB RAM)",
                "Integrate AIS feed via NMEA 2000 / REST adapter",
                "Connect Port Management System API (read-only)",
                "Deploy PostgreSQL operations database schema",
                "Set up Docker-based optimizer service (HiGHS + Pyomo)",
                "Internal QA: validate MILP results against N=8 historical cases",
            ],
            "deliverable": "Live data pipeline — no dispatch changes yet",
        },
        {
            "phase": "Phase 2",
            "period": "Month 4–6",
            "name": "Shadow Mode & Dispatcher Training",
            "color": LIGHT_GREEN,
            "milestones": [
                "Run optimizer in parallel with manual dispatch (shadow mode)",
                "Dashboard live — dispatchers see optimizer suggestions vs actual",
                "Measure suggestion acceptance rate (target: > 70%)",
                "Conduct 3-day dispatcher training workshop",
                "Calibrate ETA model with live harbor data",
                "Phase 1 KPI review with operations management",
            ],
            "deliverable": "Dispatcher-reviewed optimization suggestions",
        },
        {
            "phase": "Phase 3",
            "period": "Month 7–9",
            "name": "Assisted Dispatch (Pilot Berths)",
            "color": LIGHT_AMBER,
            "milestones": [
                "Enable auto-dispatch alerts for 2 pilot berth zones (of 111)",
                "Dispatcher retains veto — all suggestions need 1-click approval",
                "Pilot notification system live (62.1 min buffer enforced)",
                "Rolling 15-min replan active (Greedy fallback verified < 5 sec)",
                "Incident logging: capture all manual overrides with reason codes",
                "Mid-project audit: compare Phase 3 KPI vs baseline",
            ],
            "deliverable": "Partial automation with dispatcher oversight",
        },
        {
            "phase": "Phase 4",
            "period": "Month 10–12",
            "name": "Full Fleet Automation & Optimization",
            "color": "#e8f8ec",
            "milestones": [
                "Extend to all 111 berths and 4 anchorages",
                "Day-ahead MILP + rolling Greedy fully automated",
                "Exception-only dispatcher review (auto-approve within bounds)",
                "Integrate Tier 3 (Benders) for surge events",
                "Full KPI comparison vs historical baseline (target: -90% delay)",
                "Handover documentation and operations runbook finalized",
            ],
            "deliverable": "Full production deployment",
        },
    ]

    fn = styles["body"].fontName

    for p in phases:
        # Phase header row
        phase_hdr = Table(
            [[f"{p['phase']}: {p['name']}  ({p['period']})", p["deliverable"]]],
            colWidths=[9.5 * cm, 5.5 * cm],
        )
        phase_hdr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(NAVY)),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), fn),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("RIGHTPADDING", (1, 0), (1, 0), 6),
        ]))
        story.append(phase_hdr)

        # Milestone rows
        ms_rows = [[f"  {i + 1}. {m}"] for i, m in enumerate(p["milestones"])]
        ms_t = Table(ms_rows, colWidths=[15 * cm])
        ms_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(p["color"])),
            ("FONTNAME", (0, 0), (-1, -1), fn),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor(GREY_MID)),
        ]))
        story.append(ms_t)
        story.append(Spacer(1, 0.25 * cm))

    # Gantt-style timeline summary
    story.append(Paragraph("4.1 Timeline Summary (Gantt View)", styles["h2"]))
    gantt_data = [
        ["Phase", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"],
        ["Phase 1: Infrastructure", "X", "X", "X", "", "", "", "", "", "", "", "", ""],
        ["Phase 2: Shadow Mode", "", "", "", "X", "X", "X", "", "", "", "", "", ""],
        ["Phase 3: Assisted Dispatch", "", "", "", "", "", "", "X", "X", "X", "", "", ""],
        ["Phase 4: Full Automation", "", "", "", "", "", "", "", "", "", "X", "X", "X"],
    ]
    col_w = [3.8 * cm] + [0.87 * cm] * 12
    gt = Table(gantt_data, colWidths=col_w)
    p1_col = colors.HexColor(LIGHT_BLUE)
    p2_col = colors.HexColor(LIGHT_GREEN)
    p3_col = colors.HexColor(LIGHT_AMBER)
    p4_col = colors.HexColor("#e8f8ec")
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), fn),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(GREY_MID)),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        # Phase 1 — cols 1-3
        ("BACKGROUND", (1, 1), (3, 1), p1_col),
        # Phase 2 — cols 4-6
        ("BACKGROUND", (4, 2), (6, 2), p2_col),
        # Phase 3 — cols 7-9
        ("BACKGROUND", (7, 3), (9, 3), p3_col),
        # Phase 4 — cols 10-12
        ("BACKGROUND", (10, 4), (12, 4), p4_col),
    ]))
    story.append(gt)
    story.append(Spacer(1, 0.2 * cm))


def _section_ops_manual(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][4], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "This section is written for dispatch supervisors and front-line operators. "
        "The system runs autonomously — dispatchers review exceptions and approve "
        "assignments outside the confidence threshold.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.25 * cm))

    story.append(Paragraph("5.1 Daily Workflow", styles["h2"]))
    workflow_data = [
        ["Time", "Actor", "Action", "System Response"],
        ["06:00", "System (auto)", "Load next 24h vessel schedule from PMS", "ETA list populated, AIS positions refreshed"],
        ["06:30", "System (auto)", "Run day-ahead MILP (Tier 1/2/3 based on n)", "Optimal tug assignment plan generated"],
        ["07:00", "Dispatcher", "Review plan on dashboard, approve or adjust", "Approved plan locked; alerts queued"],
        ["Every 15 min", "System (auto)", "Rolling horizon replan (Greedy fallback)", "Assignment adjustments for ETA changes"],
        ["Per vessel", "System (auto)", "Auto-dispatch alert to tug captain (32–175 min before service)", "Captain confirms via app or radio"],
        ["Per vessel", "System (auto)", "Auto-alert to pilot (62.1 min before scheduled start)", "Pilot confirmed ready"],
        ["Per incident", "Dispatcher", "Override assignment if needed (reason code required)", "Override logged; replan triggered"],
        ["18:00", "Dispatcher", "End-of-day KPI review on dashboard", "Daily summary report auto-generated"],
        ["23:00", "System (auto)", "Load next day schedule from PMS", "Tomorrow's plan seeded"],
    ]
    fn = styles["body"].fontName
    wt = Table(workflow_data, colWidths=[2.3 * cm, 2.7 * cm, 5.5 * cm, 4.5 * cm])
    wt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE, font_size=7)))
    story.append(wt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("5.2 Dispatcher Decision Rules", styles["h2"]))
    rules = [
        ["Rule", "Condition", "Required Action"],
        ["APPROVE", "Optimizer confidence > 85%, no conflict detected", "Single-click approve (default)"],
        ["REVIEW", "Confidence 60–85% or ETA change > 30 min", "Check alternatives panel, approve or pick alt"],
        ["OVERRIDE", "Tug breakdown, weather advisory, VIP vessel", "Select manual assignment; enter reason code"],
        ["ESCALATE", "Optimizer fails (timeout > 10 min)", "Greedy fallback auto-activates; notify supervisor"],
        ["HOLD", "Berth not ready (dredging, maintenance)", "Set berth hold flag; system removes from window"],
    ]
    rt = Table(rules, colWidths=[2.2 * cm, 6.3 * cm, 6.5 * cm])
    rt.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT, font_size=7)))
    story.append(rt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("5.3 Alert Lead Times by Route Zone", styles["h2"]))
    story.append(Paragraph(
        "Alert lead time (time before service start that tug is dispatched) depends on "
        "travel distance from tug standby location to berth. Zones are defined by the "
        "harbor AIS geo-fence grid.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.15 * cm))
    alert_data = [
        ["Zone", "Berth Range", "Typical Travel Time", "Auto-Dispatch Lead Time", "Pilot Alert"],
        ["Zone A (Inner)", "Berths 1–30", "15–25 min", "32 min before service", "62.1 min before service"],
        ["Zone B (Mid)", "Berths 31–70", "30–50 min", "65 min before service", "62.1 min before service"],
        ["Zone C (Outer)", "Berths 71–111", "60–90 min", "105 min before service", "62.1 min before service"],
        ["Anchorage (A1–A4)", "Open water wait", "90–150 min", "175 min before service", "62.1 min before service"],
    ]
    alt = Table(alert_data, colWidths=[2.5 * cm, 2.5 * cm, 3 * cm, 3.5 * cm, 3.5 * cm])
    alt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_AMBER, font_size=7)))
    story.append(alt)
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(
        "Pilot alert is always 62.1 minutes before scheduled service start, regardless "
        "of zone. This was empirically derived as the optimal buffer minimizing both "
        "idle pilot time and late-start incidents in the N=336 validation set.",
        styles["callout"],
    ))
    story.append(Spacer(1, 0.2 * cm))


def _section_risk(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][5], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "Risk matrix uses a 3×3 Likelihood × Impact scoring. "
        "Mitigation strategies are included for all Medium and High risks.",
        styles["body"],
    ))
    story.append(Spacer(1, 0.25 * cm))

    risk_data = [
        ["Risk", "Likelihood", "Impact", "Risk Level", "Mitigation Strategy"],
        [
            "AIS data interruption",
            "Medium", "High", "HIGH",
            "Fallback to manual radio + cached last-known positions (30-min stale allowed). "
            "Auto-alert to supervisor if AIS offline > 5 min.",
        ],
        [
            "MILP solver timeout on busy days",
            "High", "Low", "MEDIUM",
            "Greedy heuristic fallback activates automatically within 5 sec. "
            "Timeout threshold: 10 min for Tier 2/3. Tier 1 always < 5 sec.",
        ],
        [
            "Dispatcher non-adoption",
            "Medium", "High", "HIGH",
            "Phased rollout (shadow mode first). 3-day training workshop. "
            "Gamified KPI dashboard showing dispatcher vs optimizer outcomes. "
            "Management sponsorship required.",
        ],
        [
            "Tug breakdown during active assignment",
            "Low", "High", "MEDIUM",
            "Real-time reassignment via Greedy within 15-sec. Dispatcher override "
            "panel highlights affected vessels. Spare tug reservation policy enforced.",
        ],
        [
            "ETA prediction error (> 60 min)",
            "High", "Medium", "HIGH",
            "Rolling 15-min replan absorbs moderate errors. "
            "CVaR95 model trained on 2024-06 data quantifies worst-case at 37.3h. "
            "ETA model retrained quarterly with fresh AIS data.",
        ],
        [
            "Port Management System API downtime",
            "Low", "Medium", "MEDIUM",
            "Local cache of 24h schedule (refreshed at 06:00). "
            "Manual CSV upload fallback in dispatcher interface.",
        ],
        [
            "Regulatory/union constraints on automation",
            "Medium", "Medium", "MEDIUM",
            "Dispatcher veto authority preserved at all times. "
            "Automation advisory only until Phase 4. Union briefing in Phase 2.",
        ],
    ]
    fn = styles["body"].fontName

    # Color code risk level column
    risk_colors = {
        "HIGH": colors.HexColor("#ffe0e0"),
        "MEDIUM": colors.HexColor(LIGHT_AMBER),
        "LOW": colors.HexColor(LIGHT_GREEN),
    }
    rt = Table(risk_data, colWidths=[3.2 * cm, 1.8 * cm, 1.5 * cm, 1.8 * cm, 7.7 * cm])
    rt.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT, font_size=7)))
    # apply risk-level row colors
    for row_idx, row in enumerate(risk_data[1:], start=1):
        level = row[3]
        bg = risk_colors.get(level, colors.white)
        rt.setStyle(TableStyle([("BACKGROUND", (3, row_idx), (3, row_idx), bg)]))
    story.append(rt)
    story.append(Spacer(1, 0.3 * cm))

    # Risk matrix grid
    story.append(Paragraph("6.1 Risk Matrix (Likelihood × Impact)", styles["h2"]))
    matrix_data = [
        ["", "Low Impact", "Medium Impact", "High Impact"],
        ["High Likelihood", "LOW", "MEDIUM (MILP timeout)", "HIGH (ETA error)"],
        ["Medium Likelihood", "LOW", "MEDIUM (Reg./Union)", "HIGH (AIS down, Non-adoption)"],
        ["Low Likelihood", "LOW", "MEDIUM (PMS API)", "MEDIUM (Tug breakdown)"],
    ]
    mg = Table(matrix_data, colWidths=[3.5 * cm, 4 * cm, 4 * cm, 4 * cm])
    mg.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor(LIGHT_NAVY)),
        ("TEXTCOLOR", (0, 1), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), fn),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(GREY_MID)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # Low = green
        ("BACKGROUND", (1, 1), (1, -1), colors.HexColor(LIGHT_GREEN)),
        ("BACKGROUND", (1, -1), (1, -1), colors.HexColor(LIGHT_GREEN)),
        # Medium = amber
        ("BACKGROUND", (2, 1), (2, 1), colors.HexColor(LIGHT_AMBER)),
        ("BACKGROUND", (2, 2), (2, 2), colors.HexColor(LIGHT_AMBER)),
        ("BACKGROUND", (2, 3), (2, 3), colors.HexColor(LIGHT_AMBER)),
        ("BACKGROUND", (3, 3), (3, 3), colors.HexColor(LIGHT_AMBER)),
        # High = red
        ("BACKGROUND", (3, 1), (3, 2), colors.HexColor("#ffe0e0")),
    ]))
    story.append(mg)
    story.append(Spacer(1, 0.2 * cm))


def _section_kpi_dashboard(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][6], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "The operations dashboard provides real-time visibility for dispatchers, "
        "supervisors, and management. Three views are supported: Real-time (dispatcher), "
        "Daily Summary (supervisor), and Monthly Trend (management).",
        styles["body"],
    ))
    story.append(Spacer(1, 0.25 * cm))

    story.append(Paragraph("7.1 Real-Time Metrics (Dispatcher View)", styles["h2"]))
    rt_data = [
        ["Metric", "Target", "Alert Threshold", "Data Source", "Update Freq."],
        ["Avg vessel wait (current hour)", "< 10 min", "> 20 min (orange)", "Operations DB", "5 min"],
        ["Tug fleet utilization (%)", "70–85%", "< 50% or > 95%", "AIS tracker", "30 sec"],
        ["Pilot buffer compliance (%)", "> 95%", "< 85%", "Pilot alert log", "Per event"],
        ["Schedule adherence rate (%)", "> 90%", "< 80%", "Operations DB", "15 min"],
        ["Active conflicts detected", "0", "> 0 (immediate alert)", "Optimizer engine", "Real-time"],
        ["Greedy replan trigger count", "< 3/hour", "> 5/hour", "Optimizer log", "15 min"],
        ["Dispatcher overrides (today)", "< 5", "> 10 (review required)", "Override log", "Per event"],
    ]
    fn = styles["body"].fontName
    rtt = Table(rt_data, colWidths=[4 * cm, 2.5 * cm, 3 * cm, 2.8 * cm, 2.7 * cm])
    rtt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE, font_size=7)))
    story.append(rtt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("7.2 Daily Summary Metrics (Supervisor View)", styles["h2"]))
    daily_data = [
        ["Metric", "Formula", "Target"],
        ["Daily avg delay reduction", "(Baseline 103.6 - Actual avg delay) / 103.6 × 100%", "> 90%"],
        ["Total vessel-hours saved", "Sum(baseline delay - actual delay) / 60 for all vessels", "> 8 h/day"],
        ["Plan approval time (avg)", "Time from 07:00 display to dispatcher approve", "< 15 min"],
        ["Tug idle time (total)", "Sum of tug idle between service end and next dispatch", "< 30% of shift"],
        ["Pilot late starts", "Count(actual pilot arrival > scheduled service start)", "< 2/day"],
        ["AIS data quality score", "% of 30-sec AIS pings received vs expected", "> 98%"],
    ]
    dt = Table(daily_data, colWidths=[4 * cm, 7.5 * cm, 3.5 * cm])
    dt.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT, font_size=7)))
    story.append(dt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("7.3 Management KPI Summary (Monthly)", styles["h2"]))
    mgmt_data = [
        ["KPI", "Baseline (Pre-system)", "Target (Year 1)", "Target (Year 2+)"],
        ["Avg vessel delay", "103.6 min/vessel", "< 15 min", "< 8 min"],
        ["Total annual wait cost (est.)", "$225M theoretical", "< $30M", "< $15M"],
        ["Fleet utilization", "~65%", "> 75%", "> 80%"],
        ["Pilot compliance rate", "Unmeasured", "> 90%", "> 95%"],
        ["Dispatcher override rate", "100% (all manual)", "< 20%", "< 10%"],
        ["System uptime (optimizer)", "N/A", "> 99.5%", "> 99.9%"],
        ["Annual fuel savings (tugs)", "Baseline", "~5% via eco-speed", "~8%"],
    ]
    mgt = Table(mgmt_data, colWidths=[4 * cm, 3.5 * cm, 3.5 * cm, 4 * cm])
    mgt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_GREEN, font_size=7)))
    story.append(mgt)
    story.append(Spacer(1, 0.2 * cm))


def _section_cost_benefit(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][7], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph("8.1 Key Assumptions", styles["h2"]))
    assump_data = [
        ["Parameter", "Value", "Source"],
        ["Vessel demurrage cost", "$5,000 / hr", "Industry standard (large container vessel)"],
        ["Tug operational fuel cost", "~$200 / hr", "Estimated from harbor fuel logs"],
        ["Pilot idle cost", "~$100 / hr", "Pilot union rate × idle fraction"],
        ["Avg delay reduction", "98.8 min/vessel (103.6 → 4.8)", "N=336 validation results"],
        ["Daily vessel services", "15 vessels/day", "Harbor average (2024-06 data)"],
        ["Annual working days", "365 days", "24/7 harbor operations"],
        ["Realization rate (conservative)", "30%", "Accounting for partial adoption, peak days"],
    ]
    fn = styles["body"].fontName
    at = Table(assump_data, colWidths=[4.5 * cm, 4.5 * cm, 6 * cm])
    at.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT, font_size=8)))
    story.append(at)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("8.2 Annual Savings Calculation", styles["h2"]))
    savings_data = [
        ["Item", "Formula", "Amount"],
        [
            "Theoretical demurrage saved",
            "98.8 min × 15 vessels × 365 days × $5,000/hr ÷ 60 min/hr",
            "~$225M/year",
        ],
        [
            "Conservative (30% realization)",
            "$225M × 30%",
            "~$67M/year",
        ],
        [
            "Pilot idle savings",
            "29 pilots × 2 h/day × 250 days × $100/hr × 20% reduction",
            "~$290K/year",
        ],
        [
            "Tug fuel savings (eco-speed)",
            "12 tugs × 8 hr/day × 365 days × $200/hr × 5% saving",
            "~$350K/year",
        ],
        [
            "Total conservative annual savings",
            "$67M + $0.29M + $0.35M",
            "~$67.6M/year",
        ],
    ]
    st2 = Table(savings_data, colWidths=[4.5 * cm, 6.5 * cm, 4 * cm])
    st2.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_GREEN, font_size=8)))
    # Highlight total row
    st2.setStyle(TableStyle([
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor(LIGHT_GREEN)),
        ("FONTNAME", (0, -1), (-1, -1), fn),
    ]))
    story.append(st2)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("8.3 Investment & ROI", styles["h2"]))
    roi_data = [
        ["Cost Category", "One-Time Cost", "Annual Recurring", "Notes"],
        ["Software development", "$2–3M", "$300K maintenance", "Includes MILP model + dashboard"],
        ["Infrastructure (server + DB)", "$150K", "$60K cloud/ops", "16-core VM + PostgreSQL + AIS adapter"],
        ["Training & change management", "$200K", "$50K/year", "Dispatcher training, workshop, manuals"],
        ["AIS integration", "$100K", "$30K license", "NMEA adapter + vendor API"],
        ["Total investment", "~$2.5–3.5M", "~$440K/year", ""],
        ["Annual savings (conservative)", "", "~$67.6M/year", "30% realization rate"],
        ["Net annual benefit (Year 1)", "", "~$67.2M", "Savings minus recurring cost"],
        ["ROI / Payback period", "", "< 1 year", "Even at 5% realization: ~$11M vs $3.5M"],
    ]
    rt2 = Table(roi_data, colWidths=[4 * cm, 3 * cm, 4 * cm, 4 * cm])
    rt2.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE, font_size=8)))
    rt2.setStyle(TableStyle([
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor(LIGHT_GREEN)),
        ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor(LIGHT_GREEN)),
        ("BACKGROUND", (0, -3), (-1, -3), colors.HexColor(LIGHT_GREEN)),
    ]))
    story.append(rt2)
    story.append(Spacer(1, 0.25 * cm))

    story.append(Paragraph(
        "Even at a 5% realization rate ($11M/year), the system pays back its full "
        "development cost within the first year. The primary risk to ROI is dispatcher "
        "adoption rate, addressed in Phase 2 (shadow mode + training).",
        styles["highlight"],
    ))
    story.append(Spacer(1, 0.2 * cm))


def _section_data_requirements(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][8], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph("9.1 Input Data Streams", styles["h2"]))
    input_data = [
        ["Data Stream", "Format", "Frequency", "Provider", "Required Fields"],
        [
            "Vessel schedule (PMS)",
            "REST JSON / CSV",
            "Hourly + updates",
            "Port Management System",
            "vessel_id, berth_id, ETA, service_type, priority",
        ],
        [
            "Tug positions (AIS)",
            "NMEA 2000 / REST",
            "Every 30 sec",
            "AIS transponder network",
            "tug_id, lat, lon, speed, heading, timestamp",
        ],
        [
            "Pilot availability",
            "REST JSON",
            "On change",
            "Pilot dispatch system",
            "pilot_id, status, certified_vessels, shift_end",
        ],
        [
            "Berth occupancy",
            "REST JSON",
            "Every 5 min",
            "Berth monitoring sensors",
            "berth_id, status (free/occupied), vessel_id, expected_free",
        ],
        [
            "Tug status",
            "Mobile app / REST",
            "On change",
            "Tug captain app",
            "tug_id, status (idle/underway/service), fuel_pct, issues",
        ],
        [
            "Weather / sea state",
            "REST JSON",
            "Hourly",
            "Korea Meteorological Admin.",
            "wind_speed, wave_height, visibility, tidal_current",
        ],
    ]
    fn = styles["body"].fontName
    it = Table(input_data, colWidths=[3 * cm, 2.2 * cm, 2 * cm, 3 * cm, 4.8 * cm])
    it.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_BLUE, font_size=7)))
    story.append(it)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("9.2 Data Quality Requirements", styles["h2"]))
    quality_data = [
        ["Requirement", "Threshold", "If Violated"],
        ["AIS position freshness", "< 60 sec stale", "Fallback to last-known; alert dispatcher"],
        ["PMS schedule completeness", "> 95% of fields populated", "Use historical average for missing ETAs"],
        ["Berth occupancy accuracy", "> 98% match to actual", "Sensor calibration review triggered"],
        ["Pilot availability data lag", "< 2 min delay", "Assume last-known status; flag for confirmation"],
        ["Historical data for ETA model", "N >= 200 records / month", "Fall back to TruncatedNormal(-2h, +2h)"],
    ]
    qt = Table(quality_data, colWidths=[5 * cm, 3.5 * cm, 6.5 * cm])
    qt.setStyle(TableStyle(_tbl_base(fn, alt_color=GREY_LIGHT, font_size=7)))
    story.append(qt)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("9.3 Data Retention Policy", styles["h2"]))
    ret_data = [
        ["Data Type", "Retention Period", "Storage", "Access Control"],
        ["AIS position history", "90 days rolling", "PostgreSQL + S3 archive", "Operations team"],
        ["Optimizer decisions", "2 years", "PostgreSQL", "Management + IT"],
        ["Dispatcher overrides", "2 years", "PostgreSQL", "Management + IT"],
        ["KPI time series", "5 years", "PostgreSQL + BI tool", "Management"],
        ["ETA model training data", "Indefinite", "S3 + version control", "Data team"],
        ["Vessel service records", "7 years", "S3 archive", "Compliance"],
    ]
    rdt = Table(ret_data, colWidths=[3.5 * cm, 2.8 * cm, 4 * cm, 4.7 * cm])
    rdt.setStyle(TableStyle(_tbl_base(fn, alt_color=LIGHT_AMBER, font_size=7)))
    story.append(rdt)
    story.append(Spacer(1, 0.2 * cm))


def _section_appendix_api(story: list, styles: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    story.append(PageBreak())
    story.append(Paragraph(SECTION_TITLES[lang][9], styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor(NAVY), spaceAfter=6))

    story.append(Paragraph(
        "All APIs use JSON over HTTPS. Authentication: Bearer token (OAuth 2.0 client credentials). "
        "Base URL: https://harbor-optimizer.internal/api/v1/",
        styles["body"],
    ))
    story.append(Spacer(1, 0.25 * cm))

    fn = styles["body"].fontName

    endpoints = [
        {
            "title": "10.1 POST /optimize/day-ahead",
            "desc": "Trigger day-ahead optimization for a given date window. "
                    "Returns job_id for async polling.",
            "request": [
                ["Field", "Type", "Required", "Description"],
                ["date", "string (YYYY-MM-DD)", "Yes", "Target optimization date"],
                ["horizon_hours", "integer", "No (default: 24)", "Planning horizon in hours"],
                ["force_tier", "string (tier1|tier2|tier3)", "No", "Override automatic tier selection"],
                ["dry_run", "boolean", "No (default: false)", "Return plan without committing alerts"],
            ],
            "response": [
                ["Field", "Type", "Description"],
                ["job_id", "string (UUID)", "Async job reference"],
                ["estimated_solve_sec", "integer", "Solver ETA in seconds"],
                ["tier_selected", "string", "Tier chosen based on vessel count"],
                ["n_vessels", "integer", "Number of vessels in the window"],
            ],
        },
        {
            "title": "10.2 GET /optimize/status/{job_id}",
            "desc": "Poll optimization job status. Returns plan when status = 'completed'.",
            "request": [
                ["Field", "Type", "Required", "Description"],
                ["job_id (path)", "string (UUID)", "Yes", "Job ID from day-ahead trigger"],
            ],
            "response": [
                ["Field", "Type", "Description"],
                ["status", "string", "pending | running | completed | failed"],
                ["solve_time_sec", "float", "Actual solver time (when completed)"],
                ["optimality_gap", "float", "MILP gap (0.0 = optimal)"],
                ["assignments", "array[Assignment]", "List of tug-vessel assignments"],
                ["objective_value", "float", "Weighted wait-time objective"],
            ],
        },
        {
            "title": "10.3 POST /dispatch/override",
            "desc": "Submit a manual dispatcher override for a vessel assignment. "
                    "Triggers immediate Greedy replan for affected vessels.",
            "request": [
                ["Field", "Type", "Required", "Description"],
                ["vessel_id", "string", "Yes", "Vessel being overridden"],
                ["new_tug_id", "string", "Yes", "Replacement tug assignment"],
                ["reason_code", "string (enum)", "Yes", "BREAKDOWN | WEATHER | VIP | BERTH_HOLD | OTHER"],
                ["dispatcher_id", "string", "Yes", "Dispatcher user ID (audit trail)"],
                ["notes", "string", "No", "Free-text reason (max 500 chars)"],
            ],
            "response": [
                ["Field", "Type", "Description"],
                ["override_id", "string", "Audit reference for this override"],
                ["replan_triggered", "boolean", "Whether Greedy replan was triggered"],
                ["affected_vessels", "array[string]", "Other vessels impacted by replan"],
                ["new_alert_times", "object", "Updated dispatch/pilot alert times"],
            ],
        },
        {
            "title": "10.4 GET /kpi/realtime",
            "desc": "Retrieve current real-time KPI snapshot for dashboard display.",
            "request": [
                ["Field", "Type", "Required", "Description"],
                ["window_minutes", "integer", "No (default: 60)", "Look-back window for avg metrics"],
            ],
            "response": [
                ["Field", "Type", "Description"],
                ["avg_vessel_wait_min", "float", "Average wait in current window"],
                ["tug_utilization_pct", "float", "% of tugs active vs idle"],
                ["pilot_compliance_pct", "float", "% of pilots alerted within 62.1-min buffer"],
                ["schedule_adherence_pct", "float", "% of services starting within 5 min of plan"],
                ["active_conflicts", "integer", "Count of unresolved assignment conflicts"],
                ["greedy_replans_last_hour", "integer", "Count of rolling replans in last 60 min"],
            ],
        },
    ]

    for ep in endpoints:
        story.append(Paragraph(ep["title"], styles["h2"]))
        story.append(Paragraph(ep["desc"], styles["body"]))
        story.append(Spacer(1, 0.1 * cm))

        story.append(Paragraph("Request:", styles["body_small"]))
        req_t = Table(ep["request"], colWidths=[3 * cm, 3.5 * cm, 2 * cm, 6.5 * cm])
        req_t.setStyle(TableStyle(_tbl_base(fn, header_color=LIGHT_NAVY, font_size=7)))
        story.append(req_t)
        story.append(Spacer(1, 0.1 * cm))

        story.append(Paragraph("Response:", styles["body_small"]))
        resp_t = Table(ep["response"], colWidths=[3.5 * cm, 3.5 * cm, 8 * cm])
        resp_t.setStyle(TableStyle(_tbl_base(fn, header_color=GREEN, font_size=7)))
        story.append(resp_t)
        story.append(Spacer(1, 0.3 * cm))


# ── 메인 빌더 ─────────────────────────────────────────────────────────────────

def build_pdf(out_path: pathlib.Path) -> str:
    font_name = _register_font()
    styles = _make_styles(font_name)
    doc = _make_doc(out_path, font_name)

    story: list = []
    _cover(story, styles)
    _section_exec_summary(story, styles)
    _section_current_state(story, styles)
    _section_architecture(story, styles)
    _section_roadmap(story, styles)
    _section_ops_manual(story, styles)
    _section_risk(story, styles)
    _section_kpi_dashboard(story, styles)
    _section_cost_benefit(story, styles)
    _section_data_requirements(story, styles)
    _section_appendix_api(story, styles)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return str(out_path.resolve())


def main() -> None:
    global lang

    parser = argparse.ArgumentParser(
        description="항구 예인선 스케줄링 최적화 — 운영 배치 계획서 PDF 생성"
    )
    parser.add_argument(
        "--lang",
        choices=["ko", "en"],
        default="en",
        help="출력 언어 선택 (ko: 한국어, en: 영어, default: en)",
    )
    args = parser.parse_args()
    lang = args.lang

    out = pathlib.Path(str(OUT_PATH).format(lang=lang))
    print(t("배치 계획서 PDF 생성 중...", "Generating deployment plan PDF..."))
    saved = build_pdf(out)
    size_kb = out.stat().st_size // 1024
    print(f"완료: {saved}")
    print(f"파일 크기: {size_kb} KB")
    print(t("섹션: 10개 (경영진 요약 ~ 부록: API 명세)",
            "Sections: 10 (Executive Summary ~ API Specifications)"))


if __name__ == "__main__":
    main()
