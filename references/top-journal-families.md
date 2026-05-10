# Top Journal Families

Use this reference to create a default watchlist before the user imports CAS/JCR tables. It is a seed pool, not a proprietary ranking table. Verify publisher status and ISSN metadata with official journal pages, Crossref, OpenAlex, or Web of Science Master Journal List when available.

Reviewed: 2026-05-10.

## Source priority

1. Official publisher journal pages and RSS/current-issue pages.
2. Crossref and OpenAlex source metadata for ISSN, publisher, and recent works.
3. CAS/JCR exports only for zone, quartile, and impact metadata.

Do not infer CAS zone or JCR quartile from journal prestige. If ranking data is missing, label `ranking pending`.

## Official source links

- Nature Portfolio Journals A-Z: https://www.nature.com/siteindex
- AAAS Science journals: https://www.science.org/journals
- Cell Press journals: https://www.cell.com/cell-press/journals
- PNAS: https://www.pnas.org/
- PNAS Nexus: https://academic.oup.com/pnasnexus

## Pool labels

- `flagship-general-full-track`: multidisciplinary flagship journals; track all new research, review, and perspective items, then filter by relevance.
- `top-family-full-track`: high-signal family journals that are directly relevant to ecology, environment, biodiversity, climate, remote sensing, sustainability, Earth systems, water, food systems, or human-nature governance.
- `top-family-relevant-only`: broad top-family journals; include only papers with high or medium fit to the user's profile.
- `field-core-candidate`: non-CNS field-leading journals to include when the task goes beyond CNS family monitoring.

## Flagship-general-full-track

| Journal | Family | Default reason |
| --- | --- | --- |
| Nature | Nature Portfolio | Flagship multidisciplinary science. |
| Science | AAAS | Flagship multidisciplinary science. |
| Cell | Cell Press | Flagship life science; include ecology/evolution/biodiversity-adjacent work when relevant. |
| Proceedings of the National Academy of Sciences | NAS | Broad high-impact multidisciplinary research. |
| PNAS Nexus | NAS | PNAS sibling journal; use relevant-only if volume is too high. |

## Nature Portfolio top-family-full-track

| Journal | Default scope note |
| --- | --- |
| Nature Climate Change | Climate impacts, adaptation, mitigation, carbon cycle, ecosystems. |
| Nature Ecology & Evolution | Ecology, biodiversity, evolution, conservation, ecosystem change. |
| Nature Sustainability | Sustainability science, social-ecological systems, governance, land systems. |
| Nature Geoscience | Earth system, climate, biogeochemistry, land-surface processes. |
| Nature Water | Water systems, watershed processes, water quality, water governance. |
| Nature Food | Food systems, agriculture, land use, biodiversity-food-climate links. |
| Nature Plants | Plant ecology, vegetation, productivity, stress response, biodiversity. |
| Nature Energy | Energy transition, climate mitigation, land-energy-environment interactions. |
| Nature Cities | Urban ecology, urban sustainability, nature-based solutions, urban land systems. |
| Nature Reviews Earth & Environment | Review and synthesis source for Earth and environmental science. |
| Nature Reviews Biodiversity | Review and synthesis source for biodiversity, conservation, ecology, and evolution. |
| Nature Communications | Broad family journal; use relevant-only by default. Full-track only when the user explicitly asks for exhaustive scanning and has sufficient weekly reading capacity. |
| Communications Earth & Environment | Earth, environmental, planetary, climate, ecology-interface research. |
| Communications Sustainability | Sustainability science, governance, land systems, biodiversity and climate solutions. |
| Communications Biology | Broad biology journal with ecology/evolution subset; use relevant-only. Exclude molecular/cellular/biomedical papers unless they directly address ecology, biodiversity, or environmental systems. |
| Scientific Data | High-value datasets for ecology, remote sensing, biodiversity, climate, and GIS. Use relevant-only. Exclude biomedical/clinical datasets unless directly tagged with ecology, environment, or Earth system keywords. |

## Nature Portfolio top-family-relevant-only

| Journal | Include when |
| --- | --- |
| Communications Materials | Remote sensing materials, sensors, environmental monitoring, or carbon/water applications. |
| Nature Sensors | Environmental sensing, Earth observation instruments, ecological monitoring technologies. |
| Nature Health | Environmental health, One Health, biodiversity-health or climate-health pathways. |
| npj Biodiversity | Biodiversity science, biogeography, ecology, conservation. |
| npj Climate Action | Climate mitigation/adaptation, governance, nature-based solutions. |
| npj Climate and Atmospheric Science | Climate, atmospheric drivers, ecological impacts, Earth observation. |
| npj Urban Sustainability | Urban ecology, urban-rural systems, planning, green infrastructure. |
| npj Ocean Sustainability | Marine biodiversity, ocean governance, conservation, blue economy. |
| npj Clean Water | Water quality, wastewater, watershed pollution, monitoring technologies. |
| npj Clean Air | Air pollution, atmospheric environment, exposure, ecosystem or human-health links. |
| npj Emerging Contaminants | Pollutants, water/soil contamination, environmental exposure and remediation. |
| npj Environmental Social Sciences | Environmental governance, policy, social-ecological systems, public behavior. |
| npj Palaeoecosystems | Long-term ecosystem change, palaeoecology, historical baselines. Note: may not yet be indexed in OpenAlex; verify source availability before using as a scan target. |
| npj Science of Food | Food systems, agricultural sustainability, food-environment interactions. |
| npj Science of Plants | Plant science with ecosystem function, vegetation, stress, and productivity relevance. |
| npj Soil Ecology | Soil biodiversity, soil carbon, belowground ecology, ecosystem function. Note: may not yet be indexed in OpenAlex; verify source availability before using as a scan target. |
| npj Sustainable Agriculture | Agroecology, agricultural biodiversity, soil, land use, food-system sustainability. |
| npj Natural Hazards | Climate hazards, landscape risk, coupled human-natural systems. |

## AAAS Science family

| Journal | Pool | Default scope note |
| --- | --- | --- |
| Science Advances | `top-family-full-track` | Broad open-access Science family journal; strong ecology/environment signal. |
| Science Robotics | `top-family-relevant-only` | Include for ecological monitoring, field robotics, sensing, autonomous sampling. |
| Science Immunology | `top-family-relevant-only` | Usually out of scope; include only for wildlife disease, eco-immunology, or conservation health. |
| Science Signaling | `top-family-relevant-only` | Usually out of scope; include only for plant/environment stress signaling with clear relevance. |
| Science Translational Medicine | `top-family-relevant-only` | Usually out of scope; include only for environment-health or biodiversity-health links. |

Science Partner Journals are not one journal. Add individual SPJ titles only after source verification and relevance screening.

## Cell Press family

| Journal | Pool | Default scope note |
| --- | --- | --- |
| One Earth | `top-family-full-track` | Cell Press sustainability flagship; environment, ecology, climate, governance. |
| Trends in Ecology & Evolution | `top-family-full-track` | High-value review and perspective source for ecology and evolution. |
| Current Biology | `top-family-relevant-only` | Include ecology, evolution, behavior, biodiversity, conservation biology. |
| Cell Reports Sustainability | `top-family-relevant-only` | Sustainability research across natural, applied, and social sciences. |
| iScience | `top-family-relevant-only` | Broad journal; include only high/medium profile matches. |
| Cell Reports | `top-family-relevant-only` | Usually out of scope; include ecology/evolution/microbiome/environmental biology matches. |
| Cell Reports Physical Science | `top-family-relevant-only` | Include for remote sensing, environmental data, carbon/water/energy materials only. |
| Trends in Plant Science | `top-family-relevant-only` | Vegetation, plant ecology, plant stress, productivity, ecosystem function. |
| Trends in Biotechnology | `top-family-relevant-only` | Environmental biotech, monitoring, restoration, carbon, water, or conservation applications. |

## Field-core candidates

Use these when the user asks for a broader top-journal watchlist beyond CNS/NAS families. CAS/JCR metadata should be added when available.

| Theme | Journals |
| --- | --- |
| Ecology and biodiversity | Ecology Letters; Global Ecology and Biogeography; Journal of Ecology; Ecological Monographs; Ecology; Methods in Ecology and Evolution; Journal of Biogeography; Ecography; Diversity and Distributions; Conservation Biology; Biological Conservation. |
| Global change and Earth systems | Global Change Biology; Earth System Science Data; Environmental Research Letters; Global Environmental Change; Earth-Science Reviews; Science of the Total Environment. |
| Remote sensing and spatial analysis | Remote Sensing of Environment; ISPRS Journal of Photogrammetry and Remote Sensing; IEEE Transactions on Geoscience and Remote Sensing; International Journal of Applied Earth Observation and Geoinformation. |
| Land systems, sustainability, governance | Landscape and Urban Planning; Land Use Policy; Journal of Environmental Management; Ecosystem Services; Conservation Letters. |

## Search strategy

For each journal, prefer direct source-limited queries:

- OpenAlex: filter by source display name or ISSN, publication date, and article type.
- Crossref: query by ISSN, from-pub-date, until-pub-date, and type.
- Publisher RSS/current issue pages when available.
- Semantic Scholar only as a secondary metadata enrichment source.

Always deduplicate by DOI first, then by normalized title and first author.

## Priority defaults

- `P1`: flagship-general or top-family-full-track paper with high profile fit.
- `P2`: top-family-full-track paper with medium fit, or relevant-only paper with high fit.
- `P3`: low-fit full-track paper retained for horizon scanning.
- `skip`: relevant-only paper with low fit, unless it introduces a reusable method or dataset.
