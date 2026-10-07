# Inventory of research outside decipherment

This package assesses 23 research candidates, mapping all 112 entries in the experiment registry. They cover source and catalogue checks, archaeological record completeness, object frames, metrology, digitization, physical experiments, khipu replication, statistical methods, and research preservation. A public-source coverage census adds 35 institution rows, 15 dataset/archive rows, 87 site-name rows, and zero validated pairs among 30 planned museum-to-corpus joins. The registry-to-candidate map is recorded entry by entry in [inventory.json](inventory.json).

The strongest near-term publication is a short correction on the conditional arithmetic behind the 10/8/6 proposal: the saved enumeration has four positive-integer solutions, while the reported range selects one. A source note on Susa weights is next: its census includes 69 coded entries and 57 mass/mark ratios, and the original and modern catalogues disagree on the mass of AS 13820 by 298 g. Catalogue cross-checks also identify Lothal totals of 133 impressions in the table and 130 in the prose, a six-versus-five component difference for Tamil Nadu form 4.19C, and a 26-versus-23 Gonur token count. The [ranked report](REPORT.md) explains publication form and remaining validation.

The rankings combine plausible novelty from a bounded live precedent search, source/output readiness, likely usefulness to a field, and remaining validation work. `inventory.json` records each candidate's numbers, exact evidence paths and fields, repository status, precedent-check status, review needs, smallest publication form, existing venue options, effort estimate, and registry IDs. `sources.json` records full bibliographic details where available and marks whether each source was opened or only seen in search results. A bounded search does not establish exhaustive priority.

No prior analysis was rerun or changed. A few numbers could only be confirmed from saved reports rather than raw source rows; those limits remain beside the claims. Source assets with unresolved rights stay local under `data/raw/2026-10-06-byproduct-inventory/`; the repository's [redistribution guidance](../../knowledge/provenance/REDISTRIBUTION.md) governs any later release.

From the repository root, run the package coverage checker with:

```powershell
python experiments/2026-10-06-byproduct-inventory/audit_coverage.py
```

The checker verifies that the inventory maps every current registry ID exactly once and that each candidate has its required assessment fields. It does not rerun any analysis or verify third-party source contents.
