"""
DOI/arXiv 기반 논문 PDF 다운로드 스크립트.

사용법:
    python scripts/download_papers.py --references docs/research/papers/references.md
    python scripts/download_papers.py --doi 10.1016/j.ejor.2011.01.002

의존: requests, arxiv (pip install requests arxiv)
저장 위치: docs/research/papers/pdfs/
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


PDFS_DIR = Path(__file__).parent.parent / "docs" / "research" / "papers" / "pdfs"


def try_arxiv_download(arxiv_id: str, output_path: Path) -> bool:
    """arXiv 논문 PDF 다운로드 시도."""
    try:
        import arxiv
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(search.results())
        result.download_pdf(dirpath=str(output_path.parent), filename=output_path.name)
        return True
    except Exception as e:
        print(f"  [arXiv] 실패: {e}", file=sys.stderr)
        return False


def try_unpaywall_download(doi: str, email: str, output_path: Path) -> bool:
    """Unpaywall API를 통한 오픈 액세스 PDF 다운로드 시도."""
    try:
        import requests
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        oa_url = data.get("best_oa_location", {}).get("url_for_pdf")
        if not oa_url:
            print(f"  [Unpaywall] OA PDF 없음 (DOI: {doi})", file=sys.stderr)
            return False
        pdf_resp = requests.get(oa_url, timeout=30)
        output_path.write_bytes(pdf_resp.content)
        return True
    except Exception as e:
        print(f"  [Unpaywall] 실패: {e}", file=sys.stderr)
        return False


def extract_dois_from_references(references_path: Path) -> list[str]:
    """references.md에서 DOI 목록 추출."""
    pattern = re.compile(r"10\.\d{4,}/\S+")
    dois = []
    for line in references_path.read_text().splitlines():
        matches = pattern.findall(line)
        dois.extend(m.rstrip(".,)") for m in matches)
    return list(dict.fromkeys(dois))  # 중복 제거


def main() -> None:
    parser = argparse.ArgumentParser(description="논문 PDF 다운로드")
    parser.add_argument("--references", type=Path, help="references.md 경로")
    parser.add_argument("--doi", type=str, help="단일 DOI")
    parser.add_argument("--email", type=str, default="research@example.com",
                        help="Unpaywall API 이메일 (필수)")
    args = parser.parse_args()

    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    dois = []
    if args.references:
        dois = extract_dois_from_references(args.references)
        print(f"{len(dois)}개 DOI 발견")
    elif args.doi:
        dois = [args.doi]

    for doi in dois:
        safe_name = doi.replace("/", "_").replace(".", "_")
        output = PDFS_DIR / f"{safe_name}.pdf"
        if output.exists():
            print(f"  [SKIP] 이미 존재: {output.name}")
            continue
        print(f"  [다운로드] {doi}")
        ok = try_unpaywall_download(doi, args.email, output)
        if not ok:
            print(f"  [수동 필요] {doi} — 저널 접근 필요")


if __name__ == "__main__":
    main()
