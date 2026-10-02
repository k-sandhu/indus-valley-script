# Independent review of the Lothal evidence

The independent pixel reading agrees with all 465 compared cells in Table 1: 93 objects, five fields per object. The table contains 133 impressions, including 62 objects with one impression. The chapter's prose gives 130 impressions and 63 single-impression objects. Both readings are preserved. The [reviewed computation](main-refined/results.json) reproduces the source-frame coverage and inscription groups, with [14 checks passing](main-refined/verification.json).

The protocol was written before opening the root's row-level CSV. Aggregate targets were already known. The first independent transcription was saved locally before comparison; its SHA-256 is recorded in the result. Detailed table rows, corpus joins, inscription strings and source images remain under `data/six-hour/lothal/independent-review/`.

| Quantity | Table 1, independently read | Published prose | Prose location |
|---|---:|---:|---|
| Impressions | 133 | 130 | PDF 20, printed 82 |
| Objects with one impression | 62 | 63 | PDF 20, printed 82 |
| Context W | 35 | 35 | PDF 9, printed 71 |
| Context W1 | 18 | 18 | PDF 10, printed 72 |
| Context W2 | 11 | 11 | PDF 10, printed 72 |
| Context O | 10 | 11 | PDF 9, printed 71 |
| Context ? | 19 | 17 | PDF 10, printed 72 |

Two object descriptions also differ from their table counts. L174 has two impressions in the prose on PDF 18, printed 80, and one in Table 1 on PDF 32, printed 94. L179 has two badly preserved exterior impressions in the prose on PDF 12, printed 74, and one in the same table page. These differences leave the chapter's overall discrepancy unresolved. The [source assertions](source-assertions.json) retain the locations and each count separately.

The location for the prose totals is PDF 20, printed 82. The frozen root `join-refined` endpoint cited PDF 21, printed 83. This review records the correction without changing that endpoint.

The context labels also have different evidential bases. W records a documented warehouse association. W1 assigns 18 further objects to that area because they carry recurrent stamps already represented there. W2 records an area association without that stamp-based link. A future model using stamps to predict context can use W1 as the authors' inference or as a held-out claim to examine. Its label construction belongs in the model specification.

The corpus joins cover 68 objects and 86 observed faces. Twenty-nine objects provide a clean, complete, single-line inscription of at least three signs, one eligible face each. They form nine exact strings, with group sizes 11, 10, 2 and six singletons. The two largest groups contain 21 of the 29 eligible objects, or 72.4%. G01 spans seven source physical categories. G02 contains ten elephant-marked objects assigned to wooden boxes. The published elephant cohort contains twelve objects, L161–L172; L171 and L172 lack a joined corpus face. These group counts describe the preserved frame and its transcription coverage. The source's identification of a common stamp remains a separate assertion based on the complete seal image.

Figures 3–7 show 35 distinct labelled objects. A selected review of twelve objects and the unnumbered fingernail inset records visible geometry, surface marks, preservation and source interpretations in [trace observations](selected-trace-observations.json). L124 illustrates why useful annotation needs several dimensions: woven contact texture, curved geometry and a proposed vessel cover can describe the same object. L198's table category and its proposed locker use can also coexist as source assertions.

The next useful archaeological comparison is a matched block around a common stamp. Record contact texture, support geometry, cord route and breakage for G01's varied attachments and G02's elephant cohort. This would test how a stable inscription was used across physical tasks. The chapter already discusses the broad recurrence pattern; our contribution is the checked object frame, reproducible joins, source discrepancies and a field design that supports further image annotation.

The [field recommendations](TRACE-FIELDS.md) and [retrospective](RETROSPECTIVE.md) explain the work and its remaining gaps. [The protocol](PROTOCOL.md) and both computation endpoints are preserved. `main` records an initial counting bug; `main-refined` is the reviewed endpoint.
