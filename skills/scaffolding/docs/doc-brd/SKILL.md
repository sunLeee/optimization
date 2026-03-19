---
name: doc-brd
triggers:
  - "doc brd"
description: "비즈니스 요구사항 문서(BRD)를 생성한다. 비즈니스 목표, ROI, 이해관계자, 리스크를 문서화한다."
argument-hint: "[output-path] - 출력 경로 (기본: docs/brd/)"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: 비즈니스 요구사항 문서화 스킬이다. 사용자 대화에서 비즈니스 정보를 수집하여 BRD를 생성한다.
agent: 당신은 비즈니스 분석가입니다. 비즈니스 가치와 ROI를 명확히 분석하고 문서화합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 문서 생성
skill-type: Atomic
references:
  - "@skills/doc-prd/SKILL.md"
referenced-by:
  - "@skills/doc-prd/SKILL.md"
  - "@skills/doc-workflow/SKILL.md"

---
# doc-brd

비즈니스 요구사항 문서(BRD)를 생성하는 스킬.

## 목적

- 비즈니스 목표 문서화
- 이해관계자 분석
- ROI/비용 분석
- 리스크 식별
- 프로젝트 정당성 입증

## 사용법

```
/doc-brd                                 # 대화형으로 BRD 생성
/doc-brd tasks/payment-brd.md         # 지정 경로에 생성
```

## 프로세스

```
/doc-brd [output-path]
    |
    v
[Step 1] 비즈니스 정보 수집
    |-- 비즈니스 목표 질문
    |-- 문제 정의 질문
    |-- 이해관계자 식별
    |
    v
[Step 2] 분석
    |-- ROI 추정
    |-- 리스크 식별
    |-- 성공 지표 정의
    |
    v
[Step 3] 문서 생성
    |-- BRD 템플릿 적용
    |-- 마크다운 파일 저장
    |
    v
완료
```

## BRD 템플릿

```markdown
# {프로젝트명} 비즈니스 요구사항 문서

> **버전**: 1.0
> **작성일**: {날짜}
> **상태**: Draft | Review | Approved

---

## 1. Executive Summary

{프로젝트 요약 - 2-3문장}

## 2. Business Objectives

### 2.1 Problem Statement

{해결할 비즈니스 문제}

### 2.2 Goals

| 목표 | 측정 지표 | 목표값 |
|------|----------|--------|
| {목표1} | {지표} | {값} |

## 3. Stakeholders

| 이해관계자 | 역할 | 관심사 | 영향력 |
|------------|------|--------|--------|
| {이름/그룹} | {역할} | {관심사} | 높음/중간/낮음 |

## 4. Business Case

### 4.1 Cost Analysis

| 항목 | 비용 | 비고 |
|------|------|------|
| 개발 인건비 | ₩{금액} | |
| 인프라 | ₩{금액} | |

### 4.2 Expected Benefits

| 이점 | 정량적 가치 | 정성적 가치 |
|------|-------------|-------------|
| {이점1} | ₩{금액}/년 | {설명} |

### 4.3 ROI

```
ROI = (Benefits - Costs) / Costs × 100%
예상 ROI: {X}%
투자 회수 기간: {Y}개월
```

## 5. Success Metrics

| KPI | 현재값 | 목표값 | 측정 주기 |
|-----|--------|--------|----------|
| {KPI1} | {현재} | {목표} | 월간 |

## 6. Risks

| 리스크 | 확률 | 영향 | 완화 방안 |
|--------|------|------|----------|
| {리스크1} | 높음 | 높음 | {방안} |

## 7. Timeline

| 단계 | 기간 | 산출물 |
|------|------|--------|
| Phase 1 | {기간} | {산출물} |

## 8. Approval

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| Sponsor | | | |
| PM | | | |

---

## Traceability

- **Downstream**: tasks/{project}-prd.md
```

## 예제

### 기본 사용

```
User: /doc-brd

Claude:
=== 비즈니스 요구사항 문서 생성 ===

[AskUserQuestion 호출]
question: "프로젝트/제품명은 무엇인가요?"
header: "프로젝트명"
options:
  - "직접 입력"

User: 실시간 주문 추적 시스템

Claude:
[AskUserQuestion 호출]
question: "해결하려는 핵심 비즈니스 문제는?"
header: "문제 정의"
options:
  - "고객 만족도 저하" - 현재 주문 상태 확인 어려움
  - "운영 비효율" - 수동 문의 응대 과다
  - "경쟁력 약화" - 경쟁사 대비 서비스 부족

User: 고객 만족도 저하

Claude:
[... 추가 질문 후 ...]

=== BRD 생성 완료 ===

파일: tasks/order-tracking-brd.md

### 요약
- 비즈니스 목표: 고객 만족도 15% 향상
- 예상 ROI: 250%
- 주요 리스크: 3개 식별

다음 단계: /doc-prd로 제품 요구사항 작성
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/doc-prd/SKILL.md] | 후행 | BRD 승인 후 PRD 작성 |
| [@skills/brainstorming/SKILL.md] | 선행 | 아이디어 정리 후 BRD 작성 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-02-12 | 저장 경로 통일: docs/brd/ → tasks/ |
| 2026-01-21 | 초기 스킬 생성 |
