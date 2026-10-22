# Data records for maintainers

This package adds four of Asko Parpola's papers as source witnesses and one derived table of his sign identifications. None is an inscribed-object record, so the object coverage counts in `knowledge/DATA.md` section 2 do not change. Files, hashes, byte counts, retrieval times and rights notes are in [SOURCES.json](SOURCES.json).

## Proposed row for DATA.md, literature witnesses

| Kind | Source and size | Rights |
|---|---|---|
| Parpola's sign identifications | Parpola 1997, *Studia Orientalia* 82: 167–192 (journal.fi, 26 pages); 2005, *Transactions of the International Conference of Eastern Studies* 50: 28–66 (harappa.com, 39 pages); 2008, *Airāvati*, 111–131 (harappa.com, 23 pages); 2009, *Scripta* 1: 37–76 (harappa.com, 40 pages); the 2010 Chennai paper already held by FISH-CONTEXT-2026-10-20 | Open access without a stated licence (1997); rights unverified or publisher copyright (2005, 2008, 2009); all local-only |

Parpola's *Deciphering the Indus Script* (Cambridge University Press, 1994) is not held. The Internet Archive item `decipheringindus0000parp` is lending-only; buying or borrowing the book is a maintainer decision, and it would extend the identification table.

## New derived table

| Table | Built by | Fields |
|---|---|---|
| [identifications-v1.json](identifications-v1.json) (tracked) | hand compilation from the extraction records in `data/raw/2026-10-22-rebus-blind-templates/extraction-v1/` | sign key, label, ICIT codes, Tamil words, source and page, the cited objects that fix each code; signs left out with reasons; Parpola's published pairs |

The table is the first crosswalk in the project from Parpola's named signs to ICIT codes. It covers 16 signs and fixes each code by an object Parpola cites, except the 'bull's head' (ICIT 740, by the glyph printed in Parpola 1997) and the short-stroke numerals one and two.

## Spending ledger

`bench/spent.json` gained split `d1d1b92051cf…` (seed `2026-10-22-rebus-blind-templates`) with one confirmation read for the family `rebus_template_pairs`.
