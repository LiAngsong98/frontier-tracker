#!/usr/bin/env python3
"""Scan recent OpenAlex works for the frontier-tracker watchlist."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "state" / "reading_state.json"
DEFAULT_WATCHLIST_REFERENCE = ROOT / "references" / "top-journal-families.md"
BUILD_SCRIPT = ROOT / "scripts" / "build_top_family_watchlist.py"
DEFAULT_POOLS = (
    "flagship-general-full-track",
    "top-family-full-track",
    "top-family-relevant-only",
)
NON_RESEARCH_TITLE_PATTERNS = (
    r"^author correction:",
    r"^publisher correction:",
    r"^correction:",
    r"^retraction:",
    r"^briefing chat:",
    r"^daily briefing:",
)
NON_RESEARCH_DOI_PREFIXES = (
    "10.1038/d41586-",
)


def load_build_module():
    spec = importlib.util.spec_from_file_location("build_top_family_watchlist", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load helper script: {BUILD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WATCHLIST_HELPER = load_build_module()


def today_iso() -> str:
    return dt.date.today().isoformat()


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def normalize_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def paper_key(work: dict[str, Any]) -> str:
    doi = work.get("doi") or ""
    if doi:
        return "doi:" + normalize_key(doi).removeprefix("https://doi.org/")
    openalex_id = work.get("id") or ""
    if openalex_id:
        return "openalex:" + openalex_id.rsplit("/", 1)[-1]
    title = normalize_title(work.get("title") or "untitled")
    return f"title:{title}|date:{work.get('publication_date') or ''}"


def request_json(url: str, timeout: float = 30.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "frontier-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(fallback)
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_watchlist(path: Path | None, pools: set[str]) -> list[dict[str, Any]]:
    if path is None:
        rows = WATCHLIST_HELPER.parse_reference(DEFAULT_WATCHLIST_REFERENCE)
    elif path.suffix.lower() == ".json":
        rows = json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    else:
        rows = WATCHLIST_HELPER.parse_reference(path)
    return [row for row in rows if row.get("pool") in pools]


def source_cache_key(row: dict[str, Any]) -> str:
    return normalize_key(str(row.get("journal", "")))


def resolve_source(row: dict[str, Any], state: dict[str, Any], sleep_seconds: float) -> dict[str, Any]:
    if row.get("openalex_id"):
        return row
    cache = state.setdefault("source_cache", {})
    key = source_cache_key(row)
    if key in cache:
        merged = dict(row)
        merged.update(cache[key])
        return merged
    resolved = WATCHLIST_HELPER.resolve_openalex(str(row["journal"]))
    cache[key] = resolved
    merged = dict(row)
    merged.update(resolved)
    time.sleep(sleep_seconds)
    return merged


def source_id_for_filter(source_id: str) -> str:
    return source_id.strip()


def fetch_source_works(
    source: dict[str, Any],
    from_date: str,
    to_date: str,
    per_page: int,
    max_pages: int,
    sleep_seconds: float,
) -> list[dict[str, Any]]:
    source_id = source.get("openalex_id")
    if not source_id:
        return []
    filters = ",".join(
        [
            f"primary_location.source.id:{source_id_for_filter(str(source_id))}",
            f"from_publication_date:{from_date}",
            f"to_publication_date:{to_date}",
        ]
    )
    select = ",".join(
        [
            "id",
            "doi",
            "title",
            "publication_date",
            "publication_year",
            "type",
            "authorships",
            "primary_location",
            "open_access",
            "cited_by_count",
            "type_crossref",
            "topics",
            "keywords",
            "abstract_inverted_index",
        ]
    )
    works: list[dict[str, Any]] = []
    cursor = "*"
    for _ in range(max_pages):
        params = {
            "filter": filters,
            "sort": "publication_date:desc",
            "per-page": str(per_page),
            "cursor": cursor,
            "select": select,
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        data = request_json(url)
        batch = data.get("results") or []
        works.extend(batch)
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not cursor or not batch:
            break
        time.sleep(sleep_seconds)
    return works


def source_display_name(work: dict[str, Any], fallback: str) -> str:
    source = ((work.get("primary_location") or {}).get("source") or {})
    return source.get("display_name") or fallback


def doi_url(doi: str) -> str:
    if not doi:
        return ""
    if doi.startswith("https://doi.org/"):
        return doi
    return "https://doi.org/" + doi


def non_research_reason(work: dict[str, Any]) -> str:
    title = normalize_key(work.get("title") or "")
    doi = normalize_key((work.get("doi") or "").removeprefix("https://doi.org/"))
    for prefix in NON_RESEARCH_DOI_PREFIXES:
        if doi.startswith(prefix):
            return f"doi prefix {prefix}"
    for pattern in NON_RESEARCH_TITLE_PATTERNS:
        if re.search(pattern, title):
            return f"title pattern {pattern}"
    return ""


def authors(work: dict[str, Any], limit: int = 5) -> str:
    names = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            names.append(author["display_name"])
        if len(names) >= limit:
            break
    if not names:
        return ""
    suffix = " et al." if len(work.get("authorships") or []) > limit else ""
    return "; ".join(names) + suffix


def compact_topics(work: dict[str, Any], limit: int = 3) -> str:
    labels = []
    for topic in work.get("topics") or []:
        name = topic.get("display_name")
        if name:
            labels.append(name)
        if len(labels) >= limit:
            break
    return "; ".join(labels)


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


def scan(args: argparse.Namespace) -> dict[str, Any]:
    state_fallback = {
        "version": 1,
        "profile": "default-profile-ecosystem-diversity",
        "created": today_iso(),
        "last_scan": None,
        "source_cache": {},
        "seen": {},
        "reading_queue": {},
    }
    state = load_json(args.state, state_fallback)
    pools = set(args.pools)
    watchlist = load_watchlist(args.watchlist, pools)
    if args.max_journals:
        watchlist = watchlist[: args.max_journals]

    seen = state.setdefault("seen", {})
    reading_queue = state.setdefault("reading_queue", {})
    allowed_types = set(args.allowed_types)
    output: dict[str, Any] = {
        "coverage": {"from": args.from_date, "to": args.to_date},
        "watchlist_journals": len(watchlist),
        "pools": sorted(pools),
        "state_file": str(args.state),
        "state_updated": bool(args.update_state),
        "new": [],
        "already_seen": [],
        "needs_manual_verification": [],
        "excluded_non_research": [],
        "source_errors": [],
    }
    collected: dict[str, dict[str, Any]] = {}

    for row in watchlist:
        try:
            source = resolve_source(row, state, args.sleep)
            if source.get("openalex_status") not in {"matched", "candidate"}:
                output["source_errors"].append(
                    {
                        "journal": row.get("journal"),
                        "pool": row.get("pool"),
                        "status": source.get("openalex_status", "missing"),
                    }
                )
                continue
            works = fetch_source_works(
                source=source,
                from_date=args.from_date,
                to_date=args.to_date,
                per_page=args.per_page,
                max_pages=args.max_pages,
                sleep_seconds=args.sleep,
            )
        except Exception as exc:
            output["source_errors"].append(
                {
                    "journal": row.get("journal"),
                    "pool": row.get("pool"),
                    "status": "error",
                    "error": str(exc),
                }
            )
            continue
        for work in works:
            work_type = work.get("type") or ""
            if allowed_types and work_type not in allowed_types:
                continue
            reason = "" if args.include_non_research else non_research_reason(work)
            if reason:
                output["excluded_non_research"].append(
                    {
                        "title": work.get("title") or "",
                        "doi": normalize_key((work.get("doi") or "").removeprefix("https://doi.org/")),
                        "journal": source_display_name(work, str(row.get("journal", ""))),
                        "publication_date": work.get("publication_date") or "",
                        "reason": reason,
                    }
                )
                continue
            key = paper_key(work)
            if key in collected:
                continue
            doi = normalize_key((work.get("doi") or "").removeprefix("https://doi.org/"))
            record = {
                "key": key,
                "title": work.get("title") or "",
                "authors": authors(work),
                "journal": source_display_name(work, str(row.get("journal", ""))),
                "publication_date": work.get("publication_date") or "",
                "publication_year": work.get("publication_year") or "",
                "type": work_type,
                "type_crossref": work.get("type_crossref") or "",
                "doi": doi,
                "doi_url": doi_url(doi),
                "openalex_id": work.get("id") or "",
                "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
                "abstract_source": "openalex" if work.get("abstract_inverted_index") else "",
                "pool": row.get("pool"),
                "family": row.get("family"),
                "pool_source": "top-family seed",
                "rank_basis": "top-family seed; ranking pending",
                "cited_by_count": work.get("cited_by_count", 0),
                "topics": compact_topics(work),
                "relevance": "needs-profile-screening",
                "status": "to-screen",
            }
            collected[key] = record

    for key, record in sorted(collected.items(), key=lambda item: item[1].get("publication_date", ""), reverse=True):
        if key in seen:
            seen[key]["last_seen"] = today_iso()
            output["already_seen"].append(record)
        else:
            if not record.get("doi") and not record.get("openalex_id"):
                output["needs_manual_verification"].append(record)
            else:
                output["new"].append(record)
            if args.update_state:
                stored = dict(record)
                stored["first_seen"] = today_iso()
                stored["last_seen"] = today_iso()
                seen[key] = stored
                reading_queue.setdefault(key, {"status": "to-screen", "added": today_iso()})

    if args.update_state:
        state["last_scan"] = {
            "from": args.from_date,
            "to": args.to_date,
            "run_date": today_iso(),
            "new_count": len(output["new"]),
            "already_seen_count": len(output["already_seen"]),
            "source_error_count": len(output["source_errors"]),
            "excluded_non_research_count": len(output["excluded_non_research"]),
        }
        save_json(args.state, state)
    return output


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Recent Frontier Scan",
        f"Coverage: {result['coverage']['from']} to {result['coverage']['to']}",
        f"Watchlist journals: {result['watchlist_journals']}",
        f"State updated: {result['state_updated']}",
        f"Excluded non-research items: {len(result['excluded_non_research'])}",
        "",
        "## New",
        "| Date | Journal | Title | DOI | Pool | Topics |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in result["new"]:
        lines.append(
            f"| {record['publication_date']} | {record['journal']} | {record['title']} | {record['doi_url']} | {record['pool']} | {record['topics']} |"
        )
    lines.extend(
        [
            "",
            "## Already Seen",
            f"Count: {len(result['already_seen'])}",
            "",
            "## Needs Manual Verification",
            "| Date | Journal | Title | Reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for record in result["needs_manual_verification"]:
        lines.append(f"| {record['publication_date']} | {record['journal']} | {record['title']} | missing DOI/OpenAlex ID |")
    lines.extend(["", "## Source Errors", "| Journal | Pool | Status | Error |", "| --- | --- | --- | --- |"])
    for error in result["source_errors"]:
        lines.append(
            f"| {error.get('journal', '')} | {error.get('pool', '')} | {error.get('status', '')} | {error.get('error', '')} |"
        )
    lines.extend(["", "## Excluded Non-Research", f"Count: {len(result['excluded_non_research'])}"])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    today = dt.date.today()
    parser = argparse.ArgumentParser(description="Scan recent papers from the frontier-tracker top-family watchlist.")
    parser.add_argument("--watchlist", type=Path, help="JSON, CSV, or Markdown watchlist. Defaults to top-journal-families.md.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="Persistent state JSON for de-duplication.")
    parser.add_argument("--days", type=int, default=7, help="Look back this many days when --from-date is not set.")
    parser.add_argument("--from-date", help="Start date in YYYY-MM-DD.")
    parser.add_argument("--to-date", default=today.isoformat(), help="End date in YYYY-MM-DD.")
    parser.add_argument("--pools", nargs="+", default=list(DEFAULT_POOLS), help="Watchlist pools to scan.")
    parser.add_argument("--allowed-types", nargs="*", default=["article", "review"], help="OpenAlex work types to keep.")
    parser.add_argument("--include-non-research", action="store_true", help="Keep news, corrections, briefings, and other non-research items.")
    parser.add_argument("--per-page", type=int, default=200, help="OpenAlex page size.")
    parser.add_argument("--max-pages", type=int, default=2, help="Maximum OpenAlex pages per journal.")
    parser.add_argument("--max-journals", type=int, help="Limit journals for smoke tests.")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between API requests.")
    parser.add_argument("--update-state", action="store_true", help="Write new records and source cache to the state file.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.from_date is None:
        to_date = parse_date(args.to_date)
        args.from_date = (to_date - dt.timedelta(days=args.days)).isoformat()
    result = scan(args)
    if args.format == "json":
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = render_markdown(result) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
