#!/usr/bin/env python3
"""Auto weekly report — screen + render from existing enriched data.

Usage:
  python -X utf8 scripts/auto_weekly_report.py \
    --input outputs/data/frontier_enriched_<profile>_<date>.json \
    --profile references/<profile>.md \
    --output outputs/reports/frontier_weekly_<profile>_<date>.html
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

today = date.today().isoformat()


def run(cmd: str, desc: str) -> None:
    print(f"\n{'=' * 50}")
    print(f">>> {desc}")
    print(f">>> {cmd[:140]}")
    sys.stdout.flush()
    r = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**__import__("os").environ, "PYTHONUNBUFFERED": "1"},
    )
    print(r.stdout)
    if r.returncode != 0:
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a weekly HTML report from enriched scan data."
    )
    parser.add_argument(
        "--input", type=Path, required=True,
        help="Enriched JSON file (output of enrich_abstracts.py).",
    )
    parser.add_argument(
        "--profile", type=Path, required=True,
        help="Profile markdown for screening.",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Output HTML report path. Defaults to outputs/reports/frontier_weekly_<date>.html.",
    )
    parser.add_argument(
        "--screened-output", type=Path,
        help="Intermediate screened JSON path. Defaults to outputs/data/frontier_screened_<date>.json.",
    )
    parser.add_argument(
        "--title", default=None,
        help="Report title. Defaults to 'Frontier Weekly Report · <date>'.",
    )
    parser.add_argument(
        "--field", default="both",
        help="Fields to screen: new, already_seen, or both (default).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    screened_path = args.screened_output or (ROOT / "outputs" / "data" / f"frontier_screened_{today}.json")
    html_path = args.output or (ROOT / "outputs" / "reports" / f"frontier_weekly_{today}.html")
    title = args.title or f"Frontier Weekly Report · {today}"

    # Step 1: Screen
    screen_cmd = (
        f'python -X utf8 "{SCRIPTS / "screen_by_profile.py"}"'
        f' --input "{args.input}"'
        f' --output "{screened_path}"'
        f' --profile "{args.profile}"'
        f' --field {args.field}'
    )
    run(screen_cmd, "Step 1: Screen by profile")

    # Step 2: Render HTML
    print(f"\n{'=' * 50}")
    print(">>> Step 2: Render HTML")
    data = json.loads(screened_path.read_text(encoding="utf-8"))
    stats = data.get("_profile_stats", {})

    lines = [
        f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body {{ font-family: -apple-system, system-ui, sans-serif; max-width:1100px; margin:0 auto; padding:20px; background:#f8f9fa; }}
h1 {{ color:#1a5276; border-bottom:3px solid #2980b9; padding-bottom:8px; }}
h2 {{ color:#2c3e50; margin-top:30px; }}
.stats {{ background:#eaf2f8; padding:15px; border-radius:8px; margin-bottom:20px; }}
.stats span {{ margin-right:20px; font-weight:bold; }}
.tier-core {{ background:#e8f8f5; border-left:4px solid #27ae60; padding:12px; margin:8px 0; border-radius:4px; }}
.tier-proxy {{ background:#fef9e7; border-left:4px solid #f39c12; padding:12px; margin:8px 0; border-radius:4px; }}
.tier-eco {{ background:#ebf5fb; border-left:4px solid #2980b9; padding:12px; margin:8px 0; border-radius:4px; }}
.paper-title {{ font-weight:bold; font-size:1.05em; margin-bottom:4px; }}
.paper-meta {{ color:#666; font-size:0.9em; margin-bottom:4px; }}
.paper-abstract {{ color:#333; font-size:0.92em; margin-top:6px; line-height:1.5; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.8em; margin-right:5px; }}
.badge-core {{ background:#27ae60; color:white; }}
.badge-proxy {{ background:#f39c12; color:white; }}
.badge-eco {{ background:#2980b9; color:white; }}
a {{ color:#2980b9; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
</style></head><body>
<h1>{html.escape(title)}</h1>
<div class="stats">
<span>Total scanned: {stats.get('total', '?')}</span>
<span>Core: {stats.get('core', '?')}</span>
<span>Proxy: {stats.get('proxy', '?')}</span>
<span>Eco: {stats.get('eco', '?')}</span>
</div>"""
    ]

    def render_paper(p: dict) -> str:
        t = html.escape(p.get("title", "Untitled"))
        journal = html.escape(p.get("journal", ""))
        authors = html.escape(p.get("authors", ""))
        d = html.escape(p.get("publication_date", ""))
        doi = p.get("doi_url", "") or f"https://doi.org/{p.get('doi', '')}"
        abstract = html.escape(p.get("abstract", "") or "")
        tier = p.get("tier", "eco")
        label = {"core": "Core", "proxy": "Proxy", "eco": "Eco"}.get(tier, tier)
        bc = f"badge-{tier}"
        if not abstract:
            abstract = '<em style="color:#999">No abstract</em>'
        return (
            f'<div class="tier-{tier}">'
            f'<div class="paper-title"><a href="{html.escape(doi)}" target="_blank">{t}</a> '
            f'<span class="badge {bc}">{label}</span></div>'
            f'<div class="paper-meta">{journal} · {d} · {authors}</div>'
            f'<div class="paper-abstract">{abstract}</div>'
            f'</div>'
        )

    all_p = data.get("new", []) + data.get("already_seen", [])
    core_p = [p for p in all_p if p.get("tier") == "core"]
    proxy_p = [p for p in all_p if p.get("tier") == "proxy"]
    eco_p = [p for p in all_p if p.get("tier") == "eco"]

    show_core = min(30, len(core_p))
    show_proxy = min(20, len(proxy_p))
    show_eco = min(15, len(eco_p))

    lines.append(f"<h2>Core (top {show_core}/{len(core_p)})</h2>")
    for p in core_p[:show_core]:
        lines.append(render_paper(p))
    if len(core_p) > show_core:
        lines.append(f"<p style='color:#999'>...and {len(core_p) - show_core} more</p>")

    lines.append(f"<h2>Proxy (top {show_proxy}/{len(proxy_p)})</h2>")
    for p in proxy_p[:show_proxy]:
        lines.append(render_paper(p))

    lines.append(f"<h2>Eco context (top {show_eco}/{len(eco_p)})</h2>")
    for p in eco_p[:show_eco]:
        lines.append(render_paper(p))

    lines.append(
        f"<p style='color:#888;margin-top:40px;font-size:0.85em'>"
        f"Generated: {today} | Profile: {html.escape(args.profile.stem)}"
        f"</p></body></html>"
    )

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "date": today,
        "total": stats.get("total", 0),
        "core": stats.get("core", 0),
        "proxy": stats.get("proxy", 0),
        "eco": stats.get("eco", 0),
        "noise": stats.get("noise", 0),
    }
    print(f"\n>>> Done! Report: {html_path}")
    print(f"    {json.dumps(summary, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
