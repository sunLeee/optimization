---
name: ref-pdf-converter
triggers:
  - "ref pdf converter"
description: PDF 문서를 마크다운 형식으로 변환한다. 텍스트, 구조, 테이블을 추출하여 저장한다.
argument-hint: "[pdf-path] - PDF 파일 경로"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Bash
model: claude-sonnet-4-6[1m]
context: PDF 변환 스킬이다. markitdown 또는 유사 도구를 사용하여 PDF를 마크다운으로 변환한다.
agent: 당신은 문서 변환 전문가입니다. PDF 구조를 분석하고 마크다운으로 정확히 변환합니다.
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
# ref-pdf-converter

PDF 문서를 마크다운으로 변환하는 스킬.

## 목적

- PDF에서 텍스트 추출
- 문서 구조 보존 (제목, 단락)
- 테이블 마크다운 변환
- 프로젝트 레퍼런스로 활용

## 사용법

```
/ref-pdf-converter docs/external/api-spec.pdf
/ref-pdf-converter ~/Downloads/research-paper.pdf --output docs/references/
```

## 프로세스

```
/ref-pdf-converter [pdf-path]
    |
    v
[Step 1] PDF 파일 확인
    |-- 파일 존재 확인
    |-- 암호화 확인 (암호화된 경우 경고)
    |
    v
[Step 2] 텍스트 추출
    |-- markitdown 또는 pypdf 사용
    |-- 페이지별 텍스트 추출
    |
    v
[Step 3] 구조 정리
    |-- 헤딩 레벨 감지 및 조정
    |-- 테이블 마크다운 변환
    |-- 리스트 형식 변환
    |
    v
[Step 4] 메타데이터 추가
    |-- 원본 파일명
    |-- 변환 날짜
    |-- 페이지 수
    |
    v
[Step 5] 파일 저장
    |-- docs/references/{filename}.md
    |
    v
완료
```

## 출력 템플릿

```markdown
# {문서 제목}

> **원본**: {pdf-filename}
>
> **변환일**: {YYYY-MM-DD}
>
> **페이지 수**: {N}

---

## 문서 내용

{추출된 텍스트 - 구조 보존}

---

## 메타데이터

- 원본 파일: {path}
- 변환 도구: markitdown
```

## 예제

```
User: /ref-pdf-converter docs/external/oauth2-spec.pdf

Claude:
=== PDF 변환 시작 ===

파일: docs/external/oauth2-spec.pdf

[1/4] 파일 확인...
  - 크기: 2.3MB
  - 페이지: 45페이지
  - 암호화: 없음

[2/4] 텍스트 추출 중...
  - markitdown 실행
  - 45페이지 처리 완료

[3/4] 구조 정리 중...
  - 헤딩: 12개 감지
  - 테이블: 5개 변환
  - 코드 블록: 8개

[4/4] 파일 저장...

=== 완료 ===

파일: docs/references/oauth2-spec.md

### 문서 구조
1. Introduction
2. Protocol Flow
3. Obtaining Authorization
4. Access Token
5. ...

다음 단계: 문서 내용 검토 및 doc-prd 참조
```

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/markdown-converter/SKILL.md] | 유사 | 범용 마크다운 변환 |
| [@skills/prd-workflow/SKILL.md] | 부모 | 레퍼런스 수집 단계 |
| [@skills/ref-url-fetcher/SKILL.md] | 관련 | URL 기반 문서 수집 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |
