---
name: markdown-converter
triggers:
  - "markdown converter"
description: 외부 문서(PDF, DOCX, HTML, 이미지)를 마크다운 형식으로 변환한다. 변환된 문서는 docs/references/에 저장하여 설계 문서 작성 시 참조한다. 사용자가 "문서 변환", "마크다운으로 변환", "PDF를 마크다운으로" 등을 요청할 때 사용한다. 호출 컨텍스트: - Composite: ref-* 스킬에서 내부 호출됨 - 단독 사용: 문서 변환만 필요할 때 직접 호출
argument-hint: "[file-path] [output-path] - 변환할 파일과 출력 경로"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: 외부 문서(PDF, DOCX, HTML, 이미지)를 마크다운으로 변환하여 docs/references/에 저장. 설계 문서 작성 시 참조 자료로 활용한다.
agent: 문서 변환 전문가. 다양한 형식의 문서를 마크다운으로 변환하고 구조를 유지한다. 표, 이미지, 코드 블록 등의 형식을 최대한 보존한다.
hooks:
  pre_execution: []
  post_execution: []
category: 변환
skill-type: Composite
references:
  - "@skills/ref-pdf-converter/SKILL.md"
  - "@skills/ref-image-ocr/SKILL.md"
referenced-by: []

---
# 마크다운 변환 스킬

외부 문서를 마크다운 형식으로 변환하고 `docs/references/`에 저장한다.

## 사용법

```
/convert <file-path> [output-path]
```

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| `file-path` | 변환할 파일 경로 | ./input/report.pdf |
| `output-path` | 출력 경로 (선택) | docs/references/report.md |

## 지원 형식

| 입력 형식 | 설명 | 변환 방법 |
|----------|------|----------|
| PDF | PDF 문서 | pdfplumber, PyMuPDF |
| DOCX | Word 문서 | python-docx |
| HTML | 웹 페이지 | beautifulsoup4 |
| 이미지 | PNG, JPG 등 | pytesseract (OCR) |

## 변환 워크플로우

### 1. 파일 분석

입력 파일의 형식과 구조를 분석한다:
- 파일 형식 감지
- 페이지/섹션 수 확인
- 표, 이미지 포함 여부 확인

### 2. 구조 추출

문서 구조를 추출한다:
- 제목/부제목 계층
- 단락/목록
- 표 데이터
- 이미지 참조

### 3. 마크다운 변환

추출된 구조를 마크다운으로 변환한다:

```markdown
# 문서 제목

## 섹션 1

본문 내용...

### 하위 섹션

- 목록 항목 1
- 목록 항목 2

| 헤더1 | 헤더2 |
|-------|-------|
| 값1   | 값2   |

![이미지 설명](./images/image1.png)
```

### 4. 후처리

변환 결과를 정리한다:
- 불필요한 공백 제거
- 링크 유효성 검사
- 이미지 경로 정리

## 출력 구조

```
docs/references/
├── {filename}.md           # 변환된 마크다운
└── {filename}_assets/      # 추출된 이미지
    ├── image1.png
    └── image2.png
```

## 예시

### PDF 변환

```bash
/convert ./input/technical_spec.pdf

# 출력:
# docs/references/technical_spec.md
# docs/references/technical_spec_assets/
```

### 웹 페이지 변환

```bash
/convert https://docs.example.com/api

# 출력:
# docs/references/api_docs.md
```

## 변환 품질 옵션

| 옵션 | 설명 |
|------|------|
| `--preserve-formatting` | 원본 서식 최대한 유지 |
| `--extract-images` | 이미지 추출 및 저장 |
| `--ocr` | OCR로 이미지 내 텍스트 추출 |
| `--clean` | 최소한의 마크다운만 생성 |

## 설계 문서 연동

변환된 문서를 설계 문서 작성에 활용한다:

1. 외부 스펙 문서 → `docs/references/spec.md`
2. CLAUDE.md에서 참조: `@docs/references/spec.md`
3. 설계 문서에서 인용

## 참고

변환 스크립트:
- `scripts/pdf_to_md.py`
- `scripts/docx_to_md.py`
