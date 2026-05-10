# Source and Selection Rules

## Official sources

- Use the official Chinese Academy of Sciences journal ranking platform at [fenqubiao.com](https://www.fenqubiao.com/).
- Treat `2025` as the latest official CAS edition unless a newer official notice says otherwise. As of `March 30, 2026`, the official platform states that it will not continue updating or publishing the ranking from `2026` onward.
- Use the official Clarivate `Journal Citation Reports` release for JCR quartiles.
- Treat the `2025` JCR edition as the latest released JCR unless Clarivate publishes a newer release. As of `March 30, 2026`, Clarivate states that the `2025` edition was released on `June 18, 2025`.
- Use the Clarivate `Master Journal List` to verify category placement when JCR category mapping is unclear.
- Use official publisher journal pages for top-family membership, including Nature Portfolio, AAAS Science journals, Cell Press, and the National Academy of Sciences publications.
- Use Crossref and OpenAlex for source metadata, ISSNs, DOIs, publication dates, and recent-work discovery. Treat them as indexing sources, not ranking authorities.
- Do not rely on third-party reposts when an official or institutionally licensed source is available.
- Respect data-usage restrictions. Do not redistribute full proprietary ranking tables when access is subscription-based or institution-scoped.

## Top journal family seed pool

- Load `top-journal-families.md` before asking the user for a ranking export when the request mentions `top journals`, `CNS`, `Nature`, `Science`, `Cell`, `PNAS`, `顶刊`, or `子刊`.
- The seed pool exists so monitoring can start without a manually imported CAS/JCR workbook.
- Treat `flagship-general-full-track` and `top-family-full-track` as trackable even when CAS/JCR metadata is unavailable.
- Treat `top-family-relevant-only` as a screened pool: keep only papers with `high` or `medium` relevance unless the user asks for exhaustive monitoring.
- Label seed-pool papers with `pool source = top-family seed`.
- If CAS/JCR metadata is unavailable, write `rank basis = top-family seed; ranking pending`.
- Do not label a paper as `Nature paper`, `Science paper`, or `Cell paper` unless the actual journal title is exactly `Nature`, `Science`, or `Cell`. Use `Nature Portfolio`, `AAAS Science family`, or `Cell Press family` for subjournals.

## Local Chinese supplement

- Use the user-maintained local workbook configured in `scripts/read_local_chinese_journal_pool.py` when the user asks to expand the journal pool with Chinese-core or high-quality Chinese journals.
- Treat the workbook as a curated local source, not as an official CAS or JCR source.
- Preserve its source label in outputs so the user can tell whether a journal entered the pool via `CAS/JCR` or via the `local Chinese supplement`.
- If the local workbook changes, prefer the live workbook over any older summary cached in the conversation.

## Scope rule

- Default scope: journals in the CAS major field `Environmental Sciences and Ecology`.
- Default JCR side of the same scope: journals classified under `Environmental Sciences` or `Ecology`.
- Add adjacent categories only if the user explicitly asks or the journal is clearly central to the user's topic.
- Default no-import fallback: top-family seed pool from `top-journal-families.md`.
- Default broad tracking order:
  1. `flagship-general-full-track`
  2. `top-family-full-track`
  3. CAS/JCR `full-track`
  4. `top-family-relevant-only`
  5. CAS/JCR `relevant-only`
  6. local Chinese supplement

## Tracking rule

- `flagship-general-full-track`: Nature, Science, Cell, PNAS, and PNAS Nexus; screen all new items but prioritize by profile relevance.
- `top-family-full-track`: high-signal top-family journals in `top-journal-families.md`; track all new items and keep low-relevance items as horizon scanning.
- `top-family-relevant-only`: broad or adjacent top-family journals; keep only `high` and `medium` relevance unless exhaustive output is requested.
- `full-track`: CAS 2025 Zone 1 or 2, or JCR Q1.
- `relevant-only`: CAS 2025 Zone 3 or 4, or JCR Q2, Q3, or Q4.
- `full-track-cn`: local tier 1 or 2 from the Chinese supplement.
- `relevant-only-cn`: local tier 3 from the Chinese supplement.
- If a journal hits `full-track` in either system, treat it as `full-track`.
- If a journal hits `top-family-full-track` but lacks CAS/JCR metadata, keep it and mark ranking as pending.
- If a journal appears in both `top-family-relevant-only` and CAS/JCR `full-track`, promote it to `full-track`.
- If a journal appears only in `relevant-only`, include it only when the paper's relevance score is `high` or `medium`.
- If a journal appears only in `full-track-cn`, keep it in the watchlist by default.
- If a journal appears only in `relevant-only-cn`, include it when the paper's relevance score is `high` or `medium`.
- If CAS/JCR are unavailable and the journal is not in the top-family seed pool, exclude the journal by default and mark it for manual review.

## Relevance rule

- Score relevance by `topic fit`, `methods fit`, `study system fit`, `geography fit`, and `novelty signal`.
- Promote to `high` when a paper matches a core topic and also contributes a useful method, dataset, or conceptual advance.
- Mark as `medium` when the topic or method is adjacent but potentially useful.
- Mark as `low` when only broad keywords match.
- Exclude when exclusion topics dominate the paper.

## Data access rule

- If official quartile data cannot be accessed directly, ask the user for a JCR export, a CAS screenshot or export, a saved watchlist, or a manually curated journal list.
- Do not stop top-family tracking while waiting for a ranking export.
- Never fabricate a journal's zone or quartile.

## Repeatable scan state

- Use `scripts/scan_recent_papers.py` for top-family seed scans that need durable de-duplication.
- Default state file: `state/reading_state.json`.
- Key papers by normalized DOI first, then OpenAlex work ID, then normalized title and publication date.
- Treat records missing DOI and OpenAlex ID as `needs manual verification`.
- For recurring automations, run with `--update-state` so the next scan can separate `new` from `already_seen`.
- For exploratory scans, omit `--update-state` and report that the state file was not changed.
- Keep the default non-research filter on for literature monitoring. Use `--include-non-research` only for publisher-wide horizon scans that intentionally include news, briefings, corrections, and notices.
- Do not delete old state records automatically. Mark paper status as `archived` or `skip` when the user decides it is no longer active.
