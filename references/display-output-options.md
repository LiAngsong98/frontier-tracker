# Display Output Options

Use this reference whenever the user asks how literature tracking results should be displayed, exported, or reviewed.

## Decision rule

The user decides the display form.

If the user has not chosen a form, ask:

`你想用哪种展示形式：Excel、本地交互式表格 App、Zotero+Obsidian，还是 Codex 页面输出？`

Do not silently default to Markdown or raw HTML.

## Supported forms

| Mode | Best for | Output |
| --- | --- | --- |
| `excel` | Daily/weekly triage, sorting, filtering, status updates | `.xlsx` dashboard with multiple sheets and colored priority/status columns |
| `app` | Interactive browsing without editing spreadsheet rows | Local table app folder with searchable/filterable paper list |
| `notes` | Long-term knowledge capture | Obsidian Markdown notes and Zotero-note-ready Markdown/CSV exports |
| `codex` | Quick in-thread preview or small scan result | Concise Codex response with top papers, counts, and action list |

## Script

Use:

```powershell
python scripts/render_display_outputs.py --mode excel --scan-json <scan.json>
python scripts/render_display_outputs.py --mode app --scan-json <scan.json>
python scripts/render_display_outputs.py --mode notes --scan-json <scan.json> --obsidian-dir <folder> --zotero-dir <folder>
python scripts/render_display_outputs.py --mode codex --scan-json <scan.json>
```

If no scan JSON exists, use `--state state/reading_state.json`.

## Practical guidance

- Use `excel` for the user's default daily and weekly working view when they want a file they can filter and annotate.
- Use `app` when the user wants an interactive dashboard but does not want to handle raw HTML.
- Use `notes` after screening, usually for `P1`, `P2`, `core`, `method`, or `dataset` papers.
- Use `codex` for quick previews, small result sets, or when the user explicitly asks to see results in the chat.

## Output directories

Default outputs go under:

```text
outputs/
  excel/
  app/
  obsidian_notes/
  zotero_notes/
  codex/
```

Keep generated outputs separate from `references/`, `scripts/`, and `state/`.
