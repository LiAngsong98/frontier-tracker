# Output Templates

## Daily scan digest

```md
# Daily Literature Scan
Coverage: YYYY-MM-DD to YYYY-MM-DD
Profile: <profile-name>

## Must Read
| Priority | Class | Journal | Paper | Why it matters | Pool source | Rank basis | Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | A | Journal Name | Paper Title | Core-topic fit + method/data value | top-family seed | top-family seed; ranking pending | Add to queue |

## Should Read
| Priority | Class | Journal | Paper | Why it matters | Pool source | Rank basis | Action |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Watchlist
| Class | Journal | Paper | Signal | Pool source | Rank basis | Next step |
| --- | --- | --- | --- | --- | --- | --- |

## Carry-Over Reminders
- Paper title: pending for X days because it is high relevance and still unread.

## Boundary Review
- Boundary paper:
- Why it is not core ecosystem diversity:
- Whether it still informs proxy evaluation or concept differentiation:
```

## Weekly Monday report

```md
# Weekly Environment and Ecology Tracking Report
Coverage: YYYY-MM-DD to YYYY-MM-DD
Profile: <profile-name>

## Executive View
- New papers screened:
- Must read this week:
- Papers already noted:
- Overdue high-priority papers:

## Must Read
| Class | Priority | Journal | Paper | Why now | Pool source | Rank basis | Suggested note |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Should Read
| Class | Priority | Journal | Paper | Relevance signal | Action |
| --- | --- | --- | --- | --- | --- |

## Methods and Data Signals
- Method or dataset:
- Why it is reusable:

## Themes This Week
- Theme:
- Supporting papers:
- Why it matters to the profile:

## Boundary and Proxy Paths
- Concept:
- Representative paper:
- Why it is boundary rather than core:
- Whether it helps clarify ecosystem diversity measurement:

## Action List
- Read:
- Note:
- Archive or skip:
```

## Reading queue status

- `to-screen`: newly found and not yet triaged.
- `queued`: selected for reading soon.
- `reading`: currently in progress.
- `noted`: summarized into Zotero or Obsidian.
- `archived`: intentionally stored with no immediate action.
- `skip`: intentionally ignored.

## Obsidian note template

```md
---
title: "<paper-title>"
journal: "<journal-name>"
published: "YYYY-MM-DD"
doi: "<doi>"
rank_basis: "CAS 1 / JCR Q1"
pool_source: "top-family seed"
relevance: "high"
topics: ["topic-1", "topic-2"]
status: "noted"
A_F_class: "A"
P1_P3_priority: "P1"
directness: "core"
boundary_or_proxy: "none"
county_scale_relevance: "high"
concept_warning: ["none"]
---

# Citation
<full citation>

# Basic Metadata
- Study object:
- Scale:
- Data:
- Method:

# Why It Matters
- One-sentence relevance summary.

# Key Findings
- Finding 1
- Finding 2

# Limitations
- Limitation 1

# Methods or Data
- Method:
- Dataset:

# Concept Boundary Check
- Treats land-use types as ecosystem types:
- Treats landscape diversity as ecosystem diversity:
- Uses proxy indicators only:

# Use For My Work
- Reusable idea:
- Limitation:
- Follow-up:
```

## Zotero note template

```md
Summary: One-paragraph plain-language summary.

Classification:
- A-F class:
- P1-P3 priority:
- Directness to ecosystem diversity:
- Boundary or proxy status:
- County-scale relevance:

Basic metadata:
- Study object:
- Scale:
- Data:
- Method:

Why relevant:
- Core fit:
- Method fit:
- Geography or system fit:

Key extractable points:
- Point 1
- Point 2

Concept boundary check:
- Land-use types treated as ecosystem types:
- Landscape diversity treated as ecosystem diversity:
- Proxy indicators presented as direct ecosystem diversity:

Next action:
- Read in full / cite / archive / compare with <paper>.
```

## A-F classification scheme

- `A`: direct theory, definition, ontology, or conceptual boundary of ecosystem diversity.
- `B`: ecosystem classification systems, ecosystem units, ecosystem typology, or mapping foundations.
- `C`: direct measurement, index design, or assessment framework for ecosystem diversity.
- `D`: empirical spatial assessment or comparison where ecosystem diversity is the explicit target.
- `E`: applied conservation, management, or planning work with ecosystem diversity as the core object.
- `F`: boundary, proxy, surrogate, or adjacent-concept literature that informs differentiation but is not core ontology.

## P1-P3 priority scheme

- `P1`: core reading to keep up with immediately, because it directly affects the active tracking focus and should enter the reading queue first.
- `P2`: useful supporting reading, methods transfer, or boundary clarification.
- `P3`: background context, weakly related material, or low-value watchlist items.
