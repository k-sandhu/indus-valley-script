# Local object and face records

The local object ledger contains eight source-defined objects. Each record has a stable research ID, frame role and inclusion reason; excavation registration; source-relative specimen number or figure number; material; dimensions and mass; context and phase; perforation; front and reverse observations; and scanner-figure joins. Its shared assumptions identify the measurement source and the limits of the numbering joins.

An observation basis accompanies each source-derived field. Use `pixel-observed` for an inspected image feature, `author-reported` for a publication measurement or description, `published-interpretation` for an author's functional proposal, and `proposed-source-join` for an unresolved identification across publications. Numeric values use mm and g. Unknown values stay null. A group measurement stays labelled as group-level when applied for comparison across individual objects.

The first face records preserve source-image hashes, native pixel sizes, source-relative view IDs, displayed numbers and pixel bounds. They describe broad layout, openings, breakage and surface features. Later registration joins are separate from these first observations. The scanner record preserves literal camera labels and the short caption stems; it does not interpret software axes as writing direction.

Detailed input files are excluded by this folder's `.gitignore`: `object-ledger.json`, `antiquity-first-observations.json`, `primary2023-first-observations.json` and `gis-first-observations.json`. Their SHA-256 values are saved in the main endpoint or final verification. Raw source and derivative files are under `local-witness/`. The tracked report, source register, reviewed figure manifest, disagreement notes, code and aggregate results provide the durable public-facing record.

To repeat the audit, first acquire the listed witnesses and restore or independently reconstruct the local annotations. The audit helper refuses to overwrite an existing endpoint. Preserve a new reconstruction separately and compare its hashes, field coverage and source joins before combining results.
