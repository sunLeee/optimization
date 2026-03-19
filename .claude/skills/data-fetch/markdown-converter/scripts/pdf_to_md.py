#!/usr/bin/env python3
"""PDF를 마크다운으로 변환하는 스크립트.

Usage:
    python pdf_to_md.py <input.pdf> [output.md]

Requirements:
    pip install pdfplumber pymupdf
"""

import argparse
import re
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_text_pdfplumber(pdf_path: Path) -> str:
    """pdfplumber를 사용하여 텍스트 추출."""
    if pdfplumber is None:
        raise ImportError("pdfplumber가 설치되지 않음: pip install pdfplumber")

    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_parts.append(f"<!-- Page {i} -->\n\n{text}")

            # 표 추출
            tables = page.extract_tables()
            for table in tables:
                md_table = convert_table_to_markdown(table)
                text_parts.append(md_table)

    return "\n\n".join(text_parts)


def extract_text_pymupdf(pdf_path: Path) -> str:
    """PyMuPDF를 사용하여 텍스트 추출."""
    if fitz is None:
        raise ImportError("PyMuPDF가 설치되지 않음: pip install pymupdf")

    text_parts = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc, 1):
        text = page.get_text()
        if text:
            text_parts.append(f"<!-- Page {i} -->\n\n{text}")

    return "\n\n".join(text_parts)


def convert_table_to_markdown(table: list[list]) -> str:
    """테이블을 마크다운 형식으로 변환."""
    if not table or not table[0]:
        return ""

    # 헤더
    header = table[0]
    md_lines = ["| " + " | ".join(str(cell or "") for cell in header) + " |"]
    md_lines.append("| " + " | ".join("---" for _ in header) + " |")

    # 데이터 행
    for row in table[1:]:
        md_lines.append("| " + " | ".join(str(cell or "") for cell in row) + " |")

    return "\n".join(md_lines)


def clean_text(text: str) -> str:
    """텍스트 정리."""
    # 다중 공백 제거
    text = re.sub(r" +", " ", text)
    # 다중 줄바꿈 정리
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_pdf_to_markdown(
    input_path: Path,
    output_path: Path | None = None,
    engine: str = "auto",
) -> str:
    """PDF를 마크다운으로 변환.

    Args:
        input_path: 입력 PDF 경로.
        output_path: 출력 마크다운 경로 (선택).
        engine: 변환 엔진 (auto, pdfplumber, pymupdf).

    Returns:
        변환된 마크다운 텍스트.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없음: {input_path}")

    # 엔진 선택
    if engine == "auto":
        if pdfplumber is not None:
            text = extract_text_pdfplumber(input_path)
        elif fitz is not None:
            text = extract_text_pymupdf(input_path)
        else:
            raise ImportError(
                "PDF 라이브러리가 설치되지 않음: "
                "pip install pdfplumber 또는 pip install pymupdf"
            )
    elif engine == "pdfplumber":
        text = extract_text_pdfplumber(input_path)
    elif engine == "pymupdf":
        text = extract_text_pymupdf(input_path)
    else:
        raise ValueError(f"알 수 없는 엔진: {engine}")

    # 텍스트 정리
    markdown = clean_text(text)

    # 파일로 저장
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"저장됨: {output_path}")

    return markdown


def main():
    parser = argparse.ArgumentParser(description="PDF를 마크다운으로 변환")
    parser.add_argument("input", type=Path, help="입력 PDF 파일")
    parser.add_argument("output", type=Path, nargs="?", help="출력 마크다운 파일")
    parser.add_argument(
        "--engine",
        choices=["auto", "pdfplumber", "pymupdf"],
        default="auto",
        help="변환 엔진",
    )

    args = parser.parse_args()

    output = args.output
    if output is None:
        output = args.input.with_suffix(".md")

    convert_pdf_to_markdown(args.input, output, args.engine)


if __name__ == "__main__":
    main()
