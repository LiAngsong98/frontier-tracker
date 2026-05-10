# Frontier Tracker

A personal literature surveillance pipeline for tracking new papers from top journals (Nature, Science, Cell, PNAS families and beyond) using OpenAlex, Crossref, and Semantic Scholar APIs.

## What it does

Frontier Tracker automates the weekly literature monitoring workflow:

1. **Scan** — Query OpenAlex for new papers from your configured journal watchlist
2. **Enrich** — Fill missing abstracts via three-way fallback (OpenAlex → Crossref → Semantic Scholar)
3. **Screen** — Classify papers into core / proxy / eco / noise tiers using your research profile keywords
4. **Render** — Output results as Excel dashboards, interactive HTML tables, Obsidian notes, or inline previews

No API keys required — uses public OpenAlex, Crossref, and Semantic Scholar endpoints.

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/yourusername/frontier-tracker.git
cd frontier-tracker
pip install openpyxl  # optional, for Excel output
```

### 2. Create your research profile

Copy the example profile and customize it:

```bash
cp references/example-profile.md references/my-profile.md
# Edit references/my-profile.md with your research keywords
```

See `references/research-profile-template.md` for the full template with all fields.

### 3. Build the journal watchlist

The default watchlist covers Nature, Science, Cell, PNAS families and related top journals:

```bash
python -X utf8 scripts/build_top_family_watchlist.py --format json --output state/watchlist.json
```

To also resolve OpenAlex source IDs (recommended for first run):

```bash
python -X utf8 scripts/build_top_family_watchlist.py --format json --resolve-openalex --output state/watchlist.json
```

### 4. Scan for new papers

```bash
python -X utf8 scripts/scan_recent_papers.py --days 7 --update-state --output outputs/data/frontier_scan_$(date +%Y-%m-%d).json
```

### 5. Enrich with abstracts

```bash
python -X utf8 scripts/enrich_abstracts.py \
  --input outputs/data/frontier_scan_$(date +%Y-%m-%d).json \
  --output outputs/data/frontier_enriched_$(date +%Y-%m-%d).json \
  --field new
```

### 6. Screen by your profile

```bash
python -X utf8 scripts/screen_by_profile.py \
  --input outputs/data/frontier_enriched_$(date +%Y-%m-%d).json \
  --profile references/my-profile.md \
  --output outputs/data/frontier_screened_$(date +%Y-%m-%d).json \
  --field both
```

### 7. Generate output

```bash
# Excel dashboard
python -X utf8 scripts/render_display_outputs.py --mode excel --scan-json outputs/data/frontier_screened_$(date +%Y-%m-%d).json

# Interactive HTML table
python -X utf8 scripts/render_display_outputs.py --mode app --scan-json outputs/data/frontier_screened_$(date +%Y-%m-%d).json

# Obsidian/Zotero notes
python -X utf8 scripts/render_display_outputs.py --mode notes --scan-json outputs/data/frontier_screened_$(date +%Y-%m-%d).json

# Quick inline preview
python -X utf8 scripts/render_display_outputs.py --mode codex --scan-json outputs/data/frontier_screened_$(date +%Y-%m-%d).json
```

### One-command weekly report

```bash
python -X utf8 scripts/auto_weekly_report.py \
  --input outputs/data/frontier_enriched_$(date +%Y-%m-%d).json \
  --profile references/my-profile.md
```

## Pipeline overview

```
┌─────────────────────────────────────────────────────────┐
│  references/top-journal-families.md                     │
│  (journal watchlist seed)                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  build_top_family_watchlist.py                          │
│  → state/watchlist.json                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  scan_recent_papers.py                                  │
│  → outputs/data/frontier_scan_<date>.json               │
│  → state/reading_state.json (de-duplication)            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  enrich_abstracts.py                                    │
│  → outputs/data/frontier_enriched_<date>.json           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  screen_by_profile.py                                   │
│  (uses references/<your-profile>.md)                    │
│  → outputs/data/frontier_screened_<date>.json           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  render_display_outputs.py / auto_weekly_report.py      │
│  → outputs/excel/, outputs/app/, outputs/notes/         │
│  → outputs/reports/                                     │
└─────────────────────────────────────────────────────────┘
```

## Project structure

```
frontier-tracker/
├── scripts/
│   ├── scan_recent_papers.py          # OpenAlex paper scanner
│   ├── enrich_abstracts.py            # Multi-source abstract enrichment
│   ├── screen_by_profile.py           # Keyword-based paper screening
│   ├── render_display_outputs.py      # Multi-format output renderer
│   ├── build_top_family_watchlist.py  # Watchlist builder from markdown
│   ├── auto_weekly_report.py          # One-command weekly HTML report
│   └── read_local_chinese_journal_pool.py  # Optional Chinese journal supplement
├── references/
│   ├── top-journal-families.md        # Default journal watchlist (Nature/Science/Cell/PNAS)
│   ├── example-profile.md             # Example research profile
│   ├── research-profile-template.md   # Full profile template
│   ├── source-and-selection-rules.md  # Journal selection rules
│   ├── output-templates.md            # Digest/report templates
│   └── display-output-options.md      # Output format guide
├── outputs/                           # Generated outputs (gitignored)
│   ├── data/
│   ├── reports/
│   └── .gitkeep
├── state/                             # Persistent state (gitignored)
│   └── .gitkeep
├── SKILL.md                           # Agent skill instructions
├── README.md
├── LICENSE
└── .gitignore
```

## Configuration

### Research profile

Your profile controls which papers are classified as core, proxy, or noise. Create it at `references/<name>.md` with these sections:

- **Core keywords** — Directly on-topic (classified as "core")
- **Proxy keywords** — Adjacent methods/themes (classified as "proxy")
- **Eco-context keywords** — Broader context (classified as "eco")

See `references/example-profile.md` for examples.

### Journal watchlist

Edit `references/top-journal-families.md` to customize which journals to track. The file uses markdown tables organized by pool:

- `flagship-general-full-track` — Nature, Science, Cell, PNAS
- `top-family-full-track` — High-signal family journals
- `top-family-relevant-only` — Broad journals (filtered by relevance)

### Adding CAS/JCR rankings

If you have CAS or JCR ranking data, you can enrich the watchlist:

1. Add ranking columns to your watchlist
2. Use `full-track` for CAS Zone 1-2 or JCR Q1
3. Use `relevant-only` for CAS Zone 3-4 or JCR Q2-Q4

### Chinese journal supplement

For Chinese-language journals, use the optional supplement:

```bash
python -X utf8 scripts/read_local_chinese_journal_pool.py --workbook path/to/journal_list.xlsx --format json
```

## Script reference

### scan_recent_papers.py

```bash
python -X utf8 scripts/scan_recent_papers.py \
  --days 7 \                    # Look-back window
  --update-state \              # Persist de-duplication state
  --output outputs/data/scan.json \  # Output file
  --pools flagship-general-full-track top-family-full-track  # Journal pools
```

### enrich_abstracts.py

```bash
python -X utf8 scripts/enrich_abstracts.py \
  --input scan.json \           # Input scan results
  --output enriched.json \      # Output with abstracts
  --field new \                 # Which field to enrich (new, already_seen, both)
  --force                       # Re-fetch even if abstract exists
```

### screen_by_profile.py

```bash
python -X utf8 scripts/screen_by_profile.py \
  --input enriched.json \       # Input enriched data
  --profile references/my-profile.md \  # Your research profile
  --output screened.json \      # Output with tier classifications
  --field both                  # Which field to screen
```

### render_display_outputs.py

```bash
python -X utf8 scripts/render_display_outputs.py \
  --mode excel \                # Output mode: excel, app, notes, codex
  --scan-json screened.json \   # Input data
  --output outputs/excel/       # Output path
```

### auto_weekly_report.py

```bash
python -X utf8 scripts/auto_weekly_report.py \
  --input enriched.json \       # Enriched data
  --profile references/my-profile.md \  # Profile for screening
  --output outputs/reports/weekly.html  # HTML report output
```

### build_top_family_watchlist.py

```bash
python -X utf8 scripts/build_top_family_watchlist.py \
  --reference references/top-journal-families.md \  # Source markdown
  --resolve-openalex \         # Also fetch OpenAlex source IDs
  --format json \              # Output format: json or csv
  --output state/watchlist.json
```

## Windows notes

Always use `python -X utf8` on Windows to avoid encoding errors with non-ASCII characters in journal names and paper titles.

## Dependencies

- Python 3.10+
- `openpyxl` (optional, for Excel output)

All API calls use Python's built-in `urllib` — no external HTTP libraries needed.

## License

MIT License — see [LICENSE](LICENSE).
