"""
논문 PDF 다운로드 스크립트 (Sci-Hub / LibGen / Z-Library).

사용법:
    python scripts/download_papers_scihub.py --all
    python scripts/download_papers_scihub.py --doi 10.1016/j.ejor.2021.07.046

저장 위치: docs/research/papers/pdfs/
"""
from __future__ import annotations
import argparse
import re
import sys
import time
from pathlib import Path

import requests

PDFS_DIR = Path(__file__).parent.parent / "docs" / "research" / "papers" / "pdfs"
REFS_FILE = Path(__file__).parent.parent / "docs" / "research" / "papers" / "references.md"

SCIHUB_MIRRORS = [
    "https://sci-hub.kr",
    "https://sci-hub.se",
    "https://sci-hub.st",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def extract_dois(refs_path: Path) -> list[tuple[str, str]]:
    """references.md 에서 (label, DOI) 추출."""
    doi_pattern = re.compile(r"10\.\d{4,}/\S+")
    label_pattern = re.compile(r"### \[([^\]]+)\]")
    results = []
    current_label = "UNKNOWN"
    for line in refs_path.read_text().splitlines():
        m = label_pattern.search(line)
        if m:
            current_label = m.group(1)
        dois = doi_pattern.findall(line)
        for doi in dois:
            doi = doi.rstrip(".,)")
            results.append((current_label, doi))
    return list({doi: (lbl, doi) for lbl, doi in results}.values())  # dedup by DOI


def download_via_scihub(doi: str, output: Path) -> bool:
    """Sci-Hub에서 DOI로 PDF 다운로드 시도."""
    for mirror in SCIHUB_MIRRORS:
        try:
            url = f"{mirror}/{doi}"
            print(f"    [Sci-Hub] {mirror} 시도중...", end=" ", flush=True)
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}")
                continue
            # PDF 직접 링크 추출
            pdf_match = re.search(
                r'(https?://[^"\']+\.pdf(?:\?[^"\']*)?)',
                resp.text
            )
            if not pdf_match:
                # iframe src 추출
                iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', resp.text)
                if iframe_match:
                    pdf_url = iframe_match.group(1)
                    if not pdf_url.startswith("http"):
                        pdf_url = mirror + pdf_url
                else:
                    print("PDF 링크 없음")
                    continue
            else:
                pdf_url = pdf_match.group(1)

            pdf_resp = requests.get(pdf_url, headers=HEADERS, timeout=30)
            if pdf_resp.status_code == 200 and b"%PDF" in pdf_resp.content[:10]:
                output.write_bytes(pdf_resp.content)
                print(f"완료 ({len(pdf_resp.content)//1024}KB)")
                return True
            print("PDF 내용 없음")
        except Exception as e:
            print(f"오류: {e}")
        time.sleep(1)
    return False


def main() -> None:
    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="references.md 전체 다운로드")
    parser.add_argument("--doi", type=str, help="단일 DOI")
    args = parser.parse_args()

    if args.doi:
        pairs = [("MANUAL", args.doi)]
    elif args.all:
        pairs = extract_dois(REFS_FILE)
        print(f"{len(pairs)}개 DOI 발견")
    else:
        parser.print_help()
        return

    success, skip, fail = 0, 0, 0
    for label, doi in pairs:
        safe = doi.replace("/", "_").replace(".", "_")
        output = PDFS_DIR / f"{label}_{safe}.pdf"
        if output.exists():
            print(f"  [SKIP] {label}: {doi}")
            skip += 1
            continue
        print(f"  [{label}] {doi}")
        ok = download_via_scihub(doi, output)
        if ok:
            success += 1
        else:
            print(f"    [FAIL] 수동 다운로드 필요: {doi}")
            fail += 1
        time.sleep(2)

    print(f"\n완료: 성공={success}, 스킵={skip}, 실패={fail}")
    if fail > 0:
        print(f"실패 논문은 https://libgen.li 또는 https://z-library.sk 에서 수동 검색 권장")


if __name__ == "__main__":
    main()
