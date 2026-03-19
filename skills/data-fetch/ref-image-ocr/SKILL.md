---
name: ref-image-ocr
triggers:
  - "ref image ocr"
description: 이미지에서 텍스트를 추출(OCR)하여 마크다운으로 저장한다. 스크린샷, 다이어그램, 문서 이미지를 텍스트화한다.
argument-hint: "[image-path] - 이미지 파일 경로"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: 이미지 OCR 스킬이다. 이미지에서 텍스트를 추출하여 레퍼런스로 저장한다.
agent: 당신은 OCR 전문가입니다. 이미지에서 텍스트를 정확히 추출하고 구조화합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 레퍼런스/시나리오
skill-type: Atomic
references: []
referenced-by:
  - "@skills/markdown-converter/SKILL.md"
  - "@skills/ref-workflow/SKILL.md"

---
# ref-image-ocr

이미지에서 텍스트를 추출(OCR)하는 스킬.

## 목적

- 이미지에서 텍스트 추출
- 스크린샷, 다이어그램 텍스트화
- 문서 이미지 레퍼런스화

## 사용법

```
/ref-image-ocr docs/images/architecture-diagram.png
/ref-image-ocr ~/Screenshots/error-message.png
```

## 프로세스

```
/ref-image-ocr [image-path]
    |
    v
[Step 1] 이미지 확인
    |-- 파일 존재 확인
    |-- 이미지 형식 확인 (PNG, JPG, etc.)
    |
    v
[Step 2] OCR 실행
    |-- Claude Vision API 활용
    |-- 또는 tesseract-ocr 사용
    |
    v
[Step 3] 텍스트 정리
    |-- 구조화 (테이블, 리스트 감지)
    |-- 오타 교정 (필요 시)
    |
    v
[Step 4] 마크다운 변환
    |-- 적절한 형식 적용
    |
    v
[Step 5] 파일 저장
    |-- docs/references/ocr/{filename}.md
    |
    v
완료
```

## 출력 템플릿

```markdown
# {이미지 파일명} - OCR 결과

> **원본**: {image-path}
>
> **추출일**: {YYYY-MM-DD}
>
> **이미지 크기**: {width}x{height}

---

## 추출된 텍스트

{OCR로 추출된 텍스트 - 구조 보존}

---

## 메타데이터

- 원본 이미지: {path}
- OCR 방식: Claude Vision / tesseract
```

## 예제

```
User: /ref-image-ocr docs/images/api-flow-diagram.png

Claude:
=== 이미지 OCR 시작 ===

파일: docs/images/api-flow-diagram.png

[1/3] 이미지 분석 중...
  - 크기: 1200x800
  - 형식: PNG
  - 내용: 플로우 다이어그램

[2/3] 텍스트 추출 중...
  - Claude Vision 사용
  - 텍스트 박스: 15개 감지

[3/3] 구조화 중...
  - 플로우 단계: 5개
  - 연결 관계 감지

=== 완료 ===

파일: docs/references/ocr/api-flow-diagram.md

### 추출된 플로우
1. Client → API Gateway
2. API Gateway → Auth Service
3. Auth Service → Database
4. Database → Auth Service (Response)
5. API Gateway → Client (Token)
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/ref-pdf-converter/SKILL.md] | 관련 | 스캔 PDF OCR에도 활용 |
| [@skills/diagram-generator/SKILL.md] | 역방향 | OCR 결과로 다이어그램 재생성 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |
