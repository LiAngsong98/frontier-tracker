#!/usr/bin/env python3
"""Build a machine-readable watchlist from top-journal-families.md."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "references" / "top-journal-families.md"


def clean_cell(value: str) -> str:
    value = value.strip()
    value = value.strip("`")
    return re.sub(r"\s+", " ", value)


def split_table_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", line.strip()))


def normalize_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return re.sub(r"^the\s+", "", normalized)


def section_pool(section: str) -> tuple[str | None, str | None]:
    s = section.lower()
    if s == "flagship-general-full-track":
        return "flagship-general-full-track", None
    if s == "nature portfolio top-family-full-track":
        return "top-family-full-track", "Nature Portfolio"
    if s == "nature portfolio top-family-relevant-only":
        return "top-family-relevant-only", "Nature Portfolio"
    if s == "aaas science family":
        return None, "AAAS"
    if s == "cell press family":
        return None, "Cell Press"
    return None, None


def parse_reference(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, str]] = []
    section = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            section = line[3:].strip()
            i += 1
            continue
        if line.strip().startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            headers = split_table_row(line)
            i += 2
            table: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table.append(split_table_row(lines[i]))
                i += 1
            default_pool, default_family = section_pool(section)
            if section == "Field-core candidates":
                for cells in table:
                    if len(cells) < 2:
                        continue
                    theme, journals = cells[0], cells[1]
                    for journal in [j.strip().rstrip(".") for j in journals.split(";") if j.strip()]:
                        rows.append(
                            {
                                "journal": journal,
                                "family": theme,
                                "pool": "field-core-candidate",
                                "scope_note": "Field-core candidate; add CAS/JCR metadata when available.",
                                "source": "top-journal-families.md",
                            }
                        )
                continue
            for cells in table:
                item = dict(zip(headers, cells))
                journal = item.get("Journal", "").strip()
                if not journal:
                    continue
                pool = item.get("Pool", default_pool or "").strip()
                family = item.get("Family", default_family or "").strip()
                note = item.get("Default scope note") or item.get("Default reason") or item.get("Include when") or ""
                if not pool:
                    pool = "top-family-relevant-only"
                rows.append(
                    {
                        "journal": journal,
                        "family": family,
                        "pool": pool,
                        "scope_note": note,
                        "source": "top-journal-families.md",
                    }
                )
            continue
        i += 1
    return rows


def resolve_openalex(journal: str, timeout: float = 20.0) -> dict[str, object]:
    params = urllib.parse.urlencode({"search": journal, "per-page": 5})
    url = f"https://api.openalex.org/sources?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "frontier-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    target = normalize_title(journal)
    best = None
    for candidate in data.get("results", []):
        name = candidate.get("display_name", "")
        if normalize_title(name) == target:
            best = candidate
            break
    if best is None and data.get("results"):
        best = data["results"][0]
    if best is None:
        return {"openalex_status": "not-found"}
    return {
        "openalex_status": "matched" if normalize_title(best.get("display_name", "")) == target else "candidate",
        "openalex_id": best.get("id", ""),
        "openalex_display_name": best.get("display_name", ""),
        "issn_l": best.get("issn_l", ""),
        "issn": ";".join(best.get("issn") or []),
        "publisher": best.get("host_organization_name", ""),
        "works_count": best.get("works_count", ""),
    }


def write_csv(rows: list[dict[str, object]], stream) -> None:
    fields = sorted({key for row in rows for key in row})
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--resolve-openalex", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.15, help="Delay between OpenAlex requests.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows: list[dict[str, object]] = parse_reference(args.reference)
    if args.resolve_openalex:
        for row in rows:
            try:
                row.update(resolve_openalex(str(row["journal"])))
            except Exception as exc:  # Keep watchlist generation robust.
                row["openalex_status"] = "error"
                row["openalex_error"] = str(exc)
            time.sleep(args.sleep)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as fh:
            if args.format == "json":
                json.dump(rows, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            else:
                write_csv(rows, fh)
    else:
        if args.format == "json":
            json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            write_csv(rows, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
