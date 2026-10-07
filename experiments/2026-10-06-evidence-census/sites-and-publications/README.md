# Site and publication census

The search produced a reproducible register of **89 site and region labels** and identified excavation-report volumes for four sites: Lothal, Farmana, Kanmer and Dholavira. Four literal labels in the table denote an unresolved value, region or survey area rather than a confirmed individual site. This work did not produce a complete count of all excavated inscribed objects. Public sources do not expose a deduplicated total across excavation reports, CISI, ICIT and derivative datasets, and ICIT's full catalogue requires permission. The gap file therefore contains **zero confirmed omissions** and three source-to-index follow-up candidates.

The [site register](site-register.json) contains all **78 literal site-field values** in the pinned Lipi file plus eleven follow-up leads not represented there. The companion [CSV](site-register.csv) is a compact view. The local input count is **5,680 Lipi rows across 78 field values**, with no empty `site` fields, and **179 Mayig rows for Mohenjo-daro**, also with no empty `site` fields. These are source rows/faces, not unique-object counts; the corpora overlap and must not be added.

The [publication register](publication-register.json) identifies 17 corpus volumes, excavation reports, catalogues or source summaries. It gives exact titles and access status where verified. It records two approximate Lothal sealing counts (~100 and ~90) from different publications; they are not reconciled. The Harappa source frame adds a primary 2000 chapter count of 22 incised tablets depicted as 66 drawn faces. It also records three Kanmer clay sealings from Agrawal et al.'s 2010 article. Farmana's 2008 report describes two square steatite seals and two terracotta objects with seal impressions, including one seal found in the preceding season; this is not a count of four newly excavated inscribed objects. Each count basis is retained in the register.

The [gap register](unindexed-evidence.json) lists Farmana, Kanmer and Dholavira as follow-up candidates, not confirmed unindexed finds. Farmana and Kanmer appear in the 2023 ICIT-based site summary, while the exact object-level joins remain unchecked. Dholavira appears in the local corpus and ICIT-based summary, but this run did not establish which CISI volume records its finds or whether the 2015 excavation report added an object omitted from those indexes. Consequently, no accessible-index share of all reported evidence is estimable from the inspected public material.

## Reproduce the local counts

From the repository root run:

```powershell
python experiments/2026-10-06-evidence-census/sites-and-publications/build_registers.py
```

The script reads the repository's existing normalized files and writes only the two site-register files in this package. Web source findings and bibliographic records are captured in `sources.json` and `publication-register.json`. Search failures and inaccessible sources appear in `sources.json`.

## Reused work

The ICIT historical counts and access caveats come from `experiments/2026-10-02-dataset-landscape/landscape.json` and its cited conference-page audit. The CISI1 scan conventions reuse `knowledge/provenance/catalogue-caveats.md` and `research/literature/cisi1_counting_and_errata.md`. Kanmer source records reuse `experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md`; the prior Lothal and Harappa source frames informed the source identity and no-double-counting rules. No earlier run was overwritten.




