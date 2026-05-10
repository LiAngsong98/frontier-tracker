#!/usr/bin/env python3
"""Enrich frontier scan results with abstracts from multiple APIs.

Three-way concurrent fallback (inspired by scansci-pdf):
  1. OpenAlex (abstract_inverted_index → reconstructed plain text)
  2. Crossref (abstract field, HTML tags stripped)
  3. Semantic Scholar (abstract field, direct plain text)

API results are merged by DOI: if OpenAlex lacks an abstract,
Crossref and Semantic Scholar are tried in parallel.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

USER_AGENT = "frontier-tracker/2.0 (abstract-enricher; multi-source)"


def request_json(url: str, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --------------- OpenAlex ---------------

def reconstruct_abstract(abstract_inverted_index: dict | None) -> str:
    """Reconstruct plain-text abstract from OpenAlex inverted index."""
    if not abstract_inverted_index:
        return ""
    word_positions = []
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


def fetch_openalex_abstract(doi: str) -> str | None:
    """Fetch abstract from OpenAlex by DOI."""
    q = urllib.parse.quote(doi, safe="")
    url = f"https://api.openalex.org/works/doi:{q}?select=abstract_inverted_index"
    try:
        data = request_json(url)
        abstract = reconstruct_abstract(data.get("abstract_inverted_index"))
        return abstract if abstract else None
    except Exception:
        return None


# --------------- Crossref ---------------

def fetch_crossref_abstract(doi: str) -> str | None:
    """Fetch abstract from Crossref API by DOI. Strips HTML tags."""
    q = urllib.parse.quote(doi, safe="")
    url = f"https://api.crossref.org/works/{q}"
    try:
        data = request_json(url)
        msg = data.get("message", {})
        abstract = (msg.get("abstract") or "").strip()
        if abstract:
            # Strip HTML tags (Crossref abstracts often contain <jats:p> etc.)
            abstract = re.sub(r"<[^>]+>", " ", abstract)
            abstract = re.sub(r"\s+", " ", abstract).strip()
        return abstract if abstract else None
    except Exception:
        return None


# --------------- Semantic Scholar ---------------

def fetch_s2_abstract(doi: str) -> str | None:
    """Fetch abstract from Semantic Scholar API by DOI.
    Returns abstract if available; falls back to tldr (AI-generated highlight).
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=abstract,tldr"
    try:
        data = request_json(url)
        abstract = (data.get("abstract") or "").strip()
        if abstract:
            return abstract
        # Fallback: use tldr (AI highlight/summary)
        tldr = (data.get("tldr") or {}).get("text", "").strip()
        if tldr:
            return f"[Highlight] {tldr}"
        return None
    except Exception:
        return None


# --------------- Three-way concurrent fallback ---------------

def _fetch_multi(doi: str) -> tuple[str, str]:
    """Try OpenAlex first, then Crossref+Semantic Scholar in parallel.
    Returns (abstract_text, source_name).
    """
    # 1. Try OpenAlex first (fastest, most structured)
    abstract = fetch_openalex_abstract(doi)
    if abstract:
        return abstract, "openalex"

    # 2. OpenAlex missed — try Crossref and Semantic Scholar in parallel
    sources = {
        "crossref": fetch_crossref_abstract,
        "semantic_scholar": fetch_s2_abstract,
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(fn, doi): name for name, fn in sources.items()}
        for future in as_completed(futures, timeout=15):
            name = futures[future]
            try:
                result = future.result()
                if result:
                    return result, name
            except Exception:
                pass
    return "", "unavailable"


def enrich_single(paper: dict) -> dict:
    """Enrich a single paper with abstract from multi-source fallback."""
    abstract = paper.get("abstract", "")
    if abstract:
        # Already has abstract (likely from scan phase)
        paper.setdefault("abstract_source", "openalex")
        return paper

    doi = paper.get("doi", "").strip()
    if not doi:
        paper = dict(paper)
        paper.setdefault("abstract", "")
        paper.setdefault("abstract_source", "unavailable")
        return paper

    enriched_abstract, source = _fetch_multi(doi)
    paper = dict(paper)
    paper["abstract"] = enriched_abstract
    paper["abstract_source"] = source
    return paper


def enrich_papers(papers: list[dict], sleep_seconds: float = 0.15, force: bool = False) -> list[dict]:
    """Add abstracts to papers using three-way fallback."""
    enriched = []
    total = len(papers)
    for i, p in enumerate(papers):
        if not force and p.get("abstract"):
            enriched.append(p)
        else:
            enriched.append(enrich_single(p))
        if (i + 1) % 20 == 0:
            print(f"  ... {i+1}/{total}", file=sys.stderr)
        time.sleep(sleep_seconds)
    # Summary stats
    has_abstract = sum(1 for p in enriched if p.get("abstract"))
    sources = {}
    for p in enriched:
        s = p.get("abstract_source", "unavailable")
        sources[s] = sources.get(s, 0) + 1
    print(f"  Abstracts: {has_abstract}/{total}  Sources: {dict(sources)}", file=sys.stderr)
    return enriched


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich scan results with abstracts (OpenAlex + Crossref + Semantic Scholar).")
    parser.add_argument("--input", type=Path, required=True, help="Scan JSON file to enrich.")
    parser.add_argument("--output", type=Path, help="Output enriched JSON file.")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between API requests.")
    parser.add_argument("--force", action="store_true", help="Re-fetch abstracts even if already present.")
    parser.add_argument("--field", default="already_seen", help="Which field to enrich (already_seen, new, or both).")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(f"Enriching from: {args.input.name}", file=sys.stderr)

    if args.field == "both":
        fields_to_enrich = ["already_seen", "new"]
    elif args.field in ("new", "already_seen"):
        fields_to_enrich = [args.field]
    else:
        print(f"Unknown field: {args.field}", file=sys.stderr)
        return 1

    total = 0
    for field in fields_to_enrich:
        papers = data.get(field, [])
        if papers:
            print(f"Enriching {field}: {len(papers)} papers...", file=sys.stderr)
            data[field] = enrich_papers(papers, args.sleep, force=args.force)
            total += len(papers)

    data["_enriched"] = True
    data["_enriched_fields"] = fields_to_enrich

    output_path = args.output or args.input
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved: {output_path} ({total} papers enriched)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
