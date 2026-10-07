# What this package contains

This exploratory survey records 31 recommendations from 29 source records, covering the named researchers and six research themes. The strongest shared agenda is corpus improvement tied to chronology and archaeological context. The five current-data priorities and their limits are in [REPORT.md](REPORT.md); the sortable source-by-source records are in [recommendations.csv](recommendations.csv) and [recommendations.json](recommendations.json).

The Frenez YouTube page yielded the title “Ongoing decipherments : Writing in the Indus Civilization.” Its transcript, event date, venue details and timestamps remain unavailable after YouTube throttled page and timed-text retrieval. The talk-specific rows therefore record the user’s notes without fabricated timestamps. Written Frenez sources support the contextual study of seals, sealings and external finds, with access states in [sources.json](sources.json).

To reproduce the machine-readable exports from the repository root, run:

```powershell
python experiments/2026-10-06-field-recommendations/build_tables.py
```

The builder converts curated source/recommendation records embedded in its script into JSON and CSV. It performs no web acquisition or interpretive coding. Source pages, transcripts and third-party payloads were not copied into the owned directory.

The dataset landscape audit already counted 5,680 source records, 4,695 provisional families and 19,946 token positions; those figures describe an existing derivative, not an independently verified object census. The repository has schemas and context analyses but no fully populated regional/chronological register. Consult `PROTOCOL.md` for the exploratory selection rules and `RETROSPECTIVE.md` for access problems and fixes.
