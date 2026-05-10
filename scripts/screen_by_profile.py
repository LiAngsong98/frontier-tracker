#!/usr/bin/env python3
"""Screen frontier scan results by research profile using keyword-based tiering.

Classification tiers:
  core    — directly on-topic (trade-off, synergy, Pareto, bundle, win-win...)
  proxy   — adjacent methods/themes (supply/demand, valuation, scenarios, InVEST...)
  eco     — broader ecological context (ecosystem service, biodiversity, restoration...)
  noise   — no match, excluded from digest

Usage:
  python -X utf8 scripts/screen_by_profile.py \
    --input outputs/data/frontier_enriched_<profile>_<date>.json \
    --profile references/default-profile-ecosystem-diversity.md \
    --output outputs/data/frontier_screened_<profile>_<date>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# --------------- Default ES trade-off profile ---------------
# These can be overridden via a profile markdown file or JSON.

DEFAULT_CORE = [
    "trade-off", "tradeoff", "trade off",
    "synergy", "synergistic", "synergies",
    "Pareto", "Pareto frontier", "Pareto optimal",
    "bundle", "bundles", "co-production", "coproduction",
    "win-win", "win-lose", "loss-win",
    "social-ecological fit", "mismatch",
    "threshold", "tipping point", "regime shift",
    "nonlinear", "non-linear",
]

DEFAULT_PROXY = [
    "ecosystem service supply", "ecosystem service demand",
    "ES supply", "ES demand",
    "ecosystem service valuation", "ecosystem service value",
    "natural capital", "natural capital accounting",
    "payment for ecosystem services", "PES",
    "InVEST", "ARIES", "SolVES", "SWAT",
    "integrated valuation",
    "scenario", "scenarios",
    "stakeholder", "stakeholders",
    "spatial trade-off", "spatial tradeoff",
]

DEFAULT_ECO = [
    "ecosystem service",
    "ecosystem function",
    "ecosystem process",
    "ecological function",
    "ecological process",
    "biodiversity",
    "conservation",
    "restoration",
    "land use change", "land-use change",
    "land cover change", "land-cover change",
    "degradation",
    "fragmentation",
    "habitat",
    "forest",
    "grassland",
    "wetland",
    "watershed",
    "catchment",
    "carbon sequestration",
    "carbon stock",
    "water yield",
    "water quality",
    "soil erosion",
    "nutrient retention",
    "pollination", "pollinator",
    "nature-based solution", "nature based solution", "NbS",
    "green infrastructure",
    "ecological restoration",
    "sustainable management",
    "nature contribution", "nature's contribution",
]


def load_profile_keywords(profile_path: Path | None) -> tuple[list[str], list[str], list[str]]:
    """Extract keyword lists from a profile markdown or JSON file.
    Falls back to DEFAULT_ lists if profile is missing or unparsable.
    """
    if not profile_path or not profile_path.exists():
        return DEFAULT_CORE, DEFAULT_PROXY, DEFAULT_ECO

    text = profile_path.read_text(encoding="utf-8").lower()

    def extract_section(heading: str) -> list[str]:
        """Extract keywords from a markdown section. Supports bullet lists,
        numbered lists, and plain-text lines (one keyword per line)."""
        import re
        pattern = rf"#+\s*{re.escape(heading)}.*?\n(.*?)(?=\n#+\s|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return []
        body = match.group(1)
        # Try bullet/num items first
        items = re.findall(r"(?:^|\n)\s*(?:[-*]|\d+[.)])\s+(.+?)(?=\n\s*(?:[-*]|\d+[.)])|\Z)", body, re.DOTALL)
        if items:
            return [item.strip().strip('"').strip("'").strip() for item in items if item.strip()]
        # Fallback: plain-text lines (strip blank lines)
        lines = [line.strip() for line in body.strip().split("\n") if line.strip()]
        return [line.strip('"').strip("'").strip() for line in lines if line.strip()]

    core = extract_section("core topics") or extract_section("core keywords") or extract_section("core") or DEFAULT_CORE
    proxy = extract_section("proxy topics") or extract_section("proxy keywords") or extract_section("proxy") or DEFAULT_PROXY
    eco = extract_section("secondary topics") or extract_section("eco keywords") or extract_section("eco-context") or extract_section("eco") or DEFAULT_ECO

    return core, proxy, eco


def classify_paper(title: str, abstract: str, core_kw: list[str], proxy_kw: list[str], eco_kw: list[str]) -> str:
    """Classify a paper into core / proxy / eco / noise."""
    text = (title + " " + abstract).lower()
    core_hits = sum(1 for kw in core_kw if kw in text)
    proxy_hits = sum(1 for kw in proxy_kw if kw in text)
    eco_hits = sum(1 for kw in eco_kw if kw in text)

    if core_hits:
        if core_hits >= 2 or proxy_hits or eco_hits:
            return "core"
        return "proxy"
    if proxy_hits:
        if proxy_hits >= 2 or eco_hits:
            return "proxy"
        return "eco"
    if eco_hits:
        return "eco"
    return "noise"


def screen_papers(papers: list[dict], core_kw: list[str], proxy_kw: list[str], eco_kw: list[str]) -> list[dict]:
    scored = []
    for p in papers:
        title = p.get("title", "") or ""
        abstract = p.get("abstract", "") or ""
        tier = classify_paper(title, abstract, core_kw, proxy_kw, eco_kw)
        p = dict(p)
        p["tier"] = tier
        scored.append(p)
    return scored


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Screen scan results by profile keywords.")
    parser.add_argument("--input", type=Path, required=True, help="Enriched scan JSON.")
    parser.add_argument("--profile", type=Path, help="Profile markdown or JSON with keyword sections.")
    parser.add_argument("--output", type=Path, help="Output screened JSON.")
    parser.add_argument("--field", default="new", help="Field to screen (new, already_seen, or both).")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    core_kw, proxy_kw, eco_kw = load_profile_keywords(args.profile)

    print(f"Profile: core={len(core_kw)} proxy={len(proxy_kw)} eco={len(eco_kw)} keywords", file=sys.stderr)

    if args.field == "both":
        fields = ["already_seen", "new"]
    else:
        fields = [args.field]

    stats = {"total": 0, "core": 0, "proxy": 0, "eco": 0, "noise": 0}
    for field in fields:
        papers = data.get(field, [])
        if not papers:
            continue
        scored = screen_papers(papers, core_kw, proxy_kw, eco_kw)
        data[field] = scored
        for p in scored:
            stats["total"] += 1
            stats[p["tier"]] = stats.get(p["tier"], 0) + 1

    data["_screened"] = True
    data["_profile_stats"] = stats

    print(f"Total: {stats['total']} | core={stats['core']} proxy={stats['proxy']} eco={stats['eco']} noise={stats['noise']}", file=sys.stderr)

    output_path = args.output or args.input
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved: {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
