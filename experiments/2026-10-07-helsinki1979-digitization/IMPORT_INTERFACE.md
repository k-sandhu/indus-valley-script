# Source-qualified occurrence import

Package L can ingest this package through `prepare_import.py`. The adapter preserves the Finnish 1979 edition, printed text number, occurrence coordinates, inventory, visual order, rank candidates, uncertainty, auxiliaries and source rights. It emits one transcription witness per printed occurrence. Repeated appearances in sorted sections stay separate.

An object relation requires a separate inspected crosswalk. Supply JSON with a `rows` array; each row requires `source_edition`, `text_number`, `target_scheme`, `target_identifier`, `concordance_source`, `concordance_page`, `surface_relation`, `rights_status` and `review_status`. The source edition string is `Koskenniemi-Parpola-1979`. The adapter uses exact source-qualified string numbers, including suffixes, and preserves multiple assertions. A null number, absent or multiple object relation, unconfirmed crosswalk, or flagged source occurrence enters quarantine.

The 1980 volume has an explicit Finnish-to-Mahadevan cross-reference table in §2.2.1, beginning at printed/PDF page 27. Its documentation discussion at page 24 explains the lookup into Mahadevan's sources. This provides a catalogue bridge worth extending; it supplies no direct verified CISI join in this package. A current Lipi family number, CISI base and Finnish 1979 number cannot be equated from their digits. The bounded crosswalk inspection is recorded in `concordance-search.json`; 1980 source crops and copied mappings remain local because that edition's reuse licence is unverified.

The import file is a review staging payload. Its confidence estimates concern compatibility with the chart's graphic candidate sets. Object identity, original line/side boundaries and ancient lost-sign counts require source review. Package L's protocol §source-qualified import already specifies an edition-qualified concordance and quarantine rule; this adapter implements that input boundary without editing its ledger or code.

The adapter also emits the concrete fields consumed by Package L's `import_helsinki1979.py`: `edition_id`, `segment_id`, `inventory_version`, `source_page`, `glyph_tokens`, `auxiliary_markers`, `order`, `boundary_status`, `rights`, `digitization_version` and `review_status`. `segment_id` is the occurrence key, so repeated sort witnesses do not collide. The rights object includes its required `CC-BY-4.0` spelling and attribution. Package L's current numeric-only validation quarantines letter suffixes; this package preserves their source strings. Its importer is exercised read-only through its pure `import_rows` function on a bounded sample, with summary output inside this package.

Run from the repository root after the full extraction finishes:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/prepare_import.py
```

Use `--out` for a new directory on repetition. A verified crosswalk can be passed with `--crosswalk`; preserve its source pages, rights and review decisions with the table.
