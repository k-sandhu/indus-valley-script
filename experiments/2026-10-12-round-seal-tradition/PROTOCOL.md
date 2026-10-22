# Round-seal follow-up protocol: joins, image checks, a shared-tradition test and the "twins"-initial count

Written 12 October 2026 before any sign of a round-seal text was compared with an image and before any statistic of the tests below was computed. Hashes are recorded in `FREEZE-2026-10-12.json`. Later changes go into dated `AMENDMENT-*.md` files. The parent study is Study B of the published-claim tests ([report](../2026-10-12-published-claim-tests/foreign-finds/REPORT.md), [protocol](../2026-10-12-published-claim-tests/foreign-finds/PROTOCOL.md)), whose files are read and not modified.

## Starting point

Study B found that 28 West Asian Indus-script texts are much less predictable under South Asian bigram statistics than matched South Asian texts (mean u 0.770), that round Gulf-type seals carry most of the excess (0.870), and that South Asian round seals are also atypical (0.704). Four of 22 West Asian texts with a known start begin with Wells sign 091, the sign of two persons standing side by side, against 0.08% of comparators; 3 of 22 end with the jar sign 740, against 34.9%. Study B did not join its records to Steffen Terp Laursen's 2010 catalogue of Gulf Type seals, did not check transcriptions against images, and measured round-seal coherence only by a count of shared transitions over seven texts.

Before this protocol was written, three kinds of information were read: record metadata and masked damage structures ([prefreeze-audit.json](prefreeze-audit.json), from [prefreeze_audit.py](prefreeze_audit.py)); Laursen's Table 1, his text on pp. 98–99, 109–112 and the captions of Figs. 8–10; and the page images of Laursen's Figs. 8 and 9 at page resolution, viewed to learn which seals they illustrate. Laursen states that his seal no. 11 carries a "relatively clear 'twin' sign" followed by pseudo-script strokes, that no. 56 uses two V signs as fill, and that a Kalba seal (Fig. 10i) carries a possible pseudo-"twins" sign. No Lipi code was compared with any image.

## Part 1. Joins to Laursen's Table 1 and to CISI

**Records joined.** All Lipi faces of type SEAL:C or SEAL:CY (43 faces), with priority on the West Asian round seals and the circular seals from Mohenjo-daro, Chanhu-daro, Dholavira and Daimabad.

**Targets.** Laursen (2010) Table 1 nos. 1–28 and 56, the inscribed seals he illustrates in Figs. 8 and 9; his Fig. 10 i–k (Kalba, Ra's al-Jinz, M-1370); Gadd (1932) catalogue numbers for the Ur and "Near East" seals; and CISI identifiers.

**Evidence classes.** Each join records every class that applies:

- *identifier*: an excavation, catalogue, plate, burial-mound or museum number in the Lipi metadata matches the number in Laursen's reference, BBM column or text;
- *citation*: Laursen or Gadd names the CISI or museum identifier of the illustrated seal;
- *image*: the object in a CISI-keyed Lipi photograph, Gadd's plate or another photograph matches Laursen's drawing in motif, outline, damage and the number and layout of signs;
- *site-unique*: the site has exactly one Lipi candidate and one Laursen seal of the type.

A join is **established** with an identifier or citation match, or an image match on at least two independent features (motif, outline or damage, and sign count or layout). It is **probable** with an image match on one feature or a site-unique match alone, and otherwise **unresolved**. Sign identities are used only to describe a join and never decide it. A CISI identifier is recorded when the Lipi `cisi` field holds a CISI siglum and the Lipi photograph filed under that siglum shows the same object; `BM-123208` in the `cisi` field is a museum number. CISI volume 3.3 (2022) defers the Gulf, West Asia and Dholavira to a final volume 3.4, which a search on 12 October 2026 did not find in print; these objects therefore receive no CISI identifier unless another published CISI number is found.

Output: `joins.csv` (tracked; identifiers and evidence only, no sign codes).

## Part 2. Transcription checks against images

**Witnesses.** Photographs take precedence over drawings, and every witness used is recorded. Available locally: CISI photographs and impressions filed by siglum in the Lipi repository (`data/lipi/public/seal_images`); Gadd (1932) Plates I–III (IGNCA scan); Laursen (2010) Figs. 8–10 impression drawings. Museum photographs (British Museum, Louvre, Penn Museum, Yale Babylonian Collection) are added where a public page serves the image for local inspection. All images stay local under `data/raw/2026-10-12-round-seal-tradition/`, with URL, date, byte count, SHA-256 and the observed rights notice. Photographs of seals are mirrored to impression orientation before comparison, and the mirroring is recorded.

**Objects checked.** All 43 round faces where a witness exists; all 22 West Asian texts with a known, legible start in Study B's frozen set (initial sign at minimum, all signs where possible); the 34 South Asian unique complete texts whose initial sign is one of the human-figure codes 090, 091, 093, 094, 095, 097, 104, 118 and 137 (initial sign only).

**Reader 1** (the coordinating session) renders each Lipi code string with Lipi's Wells-coded font in visual order and compares it with each witness sign by sign. Each position is recorded as *agree*; *differ*, with the alternative Wells code when the font chart identifies one and `000` otherwise; *not shown* (damaged, cropped or absent in the witness); or *extra* (a sign in the witness without a Lipi position). Each text also receives a status: *inscription*, *pseudo-inscription* (strokes or marks without standard sign forms, or so described by Laursen or Gadd), or *fill* (signs used as decoration, as Laursen describes no. 56), together with the evidence for its reading direction.

**Reader 2** is a subagent that sees the witness images without Lipi codes, sign numbers or Study B results. For every text in the 091 test it classifies the sign at each end of the inscription line in impression orientation as *two human figures side by side*, *one human figure*, *other* or *illegible*, and describes the form briefly.

**Checked transcription.** Lipi's code is kept unless a witness clearly shows a different sign, in which case Reader 1's alternative replaces it. An *extra* sign is inserted with its identified code or `000`. Edge flags change only when a witness shows breakage or completeness contrary to the Lipi code. A *not shown* position keeps the Lipi code, because the Lipi coder may have used a better image. Checked transcriptions and per-sign records stay local; tracked outputs give counts per object and the identification of each initial sign.

## Part 3a. Do round-seal texts form a shared sequence tradition?

**Population (T1).** Single-line texts of type SEAL:C found in West Asia, South Asia or without provenance, with the Dilmun face 6000.1 dropped as the duplicate witness of Ur 3898.1 (Study B rule) and the two-line faces 5230.1 and 5226.1 excluded: 16 West Asian, 9 South Asian (10 faces) and 4 unprovenanced objects. Faces of one object family are held out and scored together, and an object's value is the mean over its faces.

**Internal model.** For each held-out object i, an interpolated Kneser–Ney bigram is trained on every other population text, excluding any text with the same code string as i. The model is Study B's: discount D = n₁/(n₁ + 2n₂) from count-of-counts at each level (D = 0.5 if n₁ + 2n₂ = 0), lowest level interpolated with a uniform distribution over Study B's fixed vocabulary of 712 legible codes plus the end symbol, events and edge rules from `ffcore.py`.

**Matched South Asian model.** The matched pool holds the 1,382 unique complete single-line South Asian seal texts that are not round or cylinder seals. A matched training set replaces every population text j with a pool text of the same length L_j, drawn at random, carrying j's damage mask and edge flags as in Study B's comparator windows. Token and event counts therefore equal those of the internal training set. For held-out i, the partner of i is dropped. Each population is evaluated with D = 50 matched sets (seed 20261014).

**Statistic.** Δᵢ is the mean surprisal per scored event of object i under the internal model minus its mean over the 50 matched models, in bits. Δ̄ is the mean of Δᵢ over objects with at least one event. Negative values mean that other round seals predict a round seal better than the same amount of South Asian seal text does.

**Null distribution.** A pseudo-group replaces each population text with a random pool text of the same length, carrying its mask and edge flags. The whole procedure is repeated on the pseudo-group, with matched sets drawn from the pool after removing the pseudo-group's texts. Pseudo-group and matched sets come from one distribution, so the null Δ̄ centres near zero. 1,000 pseudo-groups (seed 20261015) give the one-sided p = (1 + #{Δ̄_null ≤ Δ̄_obs})/1,001. A 95% percentile bootstrap over objects (10,000 draws, seed 20261016) gives the interval for Δ̄.

**Decomposition.** Two further measures use the same held-out objects, matched sets and pseudo-groups:

- *Inventory:* Δ̄ computed with unigram models (absolute-discounted target counts interpolated with the uniform distribution), which use sign frequencies and ignore order.
- *Transitions:* for objects with at least one sign-to-sign event, the share of those events attested in the internal training set minus the mean share attested in the matched sets. Positive values mean shared transitions. The p-value counts null values at or above the observed one.

**Secondary tests**, with a Holm correction over their three p-values:

- *T2:* West Asian circular seals only (16 objects), internal leave-one-out as in T1.
- *T3a:* a model trained on all West Asian circular seals scores the South Asian circular seals, against matched models of the same West Asian training structure. The null replaces the West Asian training texts with pseudo-groups.
- *T3b:* a model trained on the South Asian circular seals scores the West Asian circular seals, with the converse construction.

**Decision rules.**

- *Shared tradition:* T1 shows a shared tradition when p < 0.05 and the bootstrap interval for Δ̄ lies below zero.
- *Sequence or inventory:* the tradition is a *sequence* tradition when the transition measure also has p < 0.05. When the bigram result holds and the transition measure does not, the shared element is reported as sign inventory.
- *Link between regions:* T3a and T3b test whether the West Asian and South Asian circular seals share a tradition. A positive decision in either requires Holm-adjusted p < 0.05 and an interval below zero.
- *No evidence:* if T1 fails, the corpus shows no shared round-seal tradition at this sample size. The null's 5% quantile and the positive controls state the effect the test could detect.

**Positive controls.** Two groups with known internal regularities are run with the same machinery: C1, the 67 unique complete Mohenjo-daro copper tablet texts (TAB:C), a set with recurring texts tied to images; C2, the 135 unique complete Gujarat/Kutch non-round seal texts, a regional set. For each, 100 random subsets of 29 texts are scored with internal leave-one-out against matched sets of their own lengths, with Gujarat/Kutch texts removed from the matched pool for C2. A 500-draw null is built for the first subset's structure. The report gives the median Δ̄ and the share of subsets below that null's 5% quantile.

**Sensitivities for T1.** Each has its own 1,000-draw null.

| Code | Change |
|---|---|
| S1 | Checked transcriptions from Part 2 replace Lipi codes |
| S2 | Texts with pseudo-inscription or fill status are removed |
| S3 | Only seals joined (established or probable) to Laursen's Indus-inscribed Gulf Type seals |
| S4 | Cylinder seals (SEAL:CY) added, including the Susa cylinder and the South Asian and unprovenanced cylinders |

A sensitivity that reverses a decision is reported beside the primary result and does not replace it.

## Part 3b. Do West Asian texts begin with the "twins" sign more often than South Asian texts?

**Texts.** The 22 West Asian texts in Study B's frozen set with a known, legible start, and the 2,122 unique complete South Asian texts.

**Identification.** A West Asian initial sign counts as *confirmed 091* when Reader 1 and Reader 2 both identify the reading-initial sign as two human figures side by side. Reading-initial is the right end of the impression for texts read right to left and the left end for texts read left to right, following Lipi's direction field unless a source states otherwise. A sign with only one reader's support, or with no usable witness, is *unconfirmed*. South Asian texts count as 091-initial when Reader 1 identifies two human figures side by side at the start of a text among the 34 checked; the remaining 2,088 texts begin with signs outside the human-figure codes and count as not 091-initial.

**Test.** One-sided Fisher exact test of confirmed 091-initial texts among the 22 West Asian texts, with unconfirmed counted as not 091, against image-checked 091-initial texts among 2,122 South Asian texts. The pattern holds with image-checked identifications when p < 0.05. Reported beside it: the count with unconfirmed Lipi readings included; the count after removing texts with pseudo-inscription or fill status; and Parpola's count, reported by Laursen, of four Near Eastern and three Indus Valley texts beginning with the "twins" sign.

## Scope

These tests measure graphic sequence regularities in transcriptions. Neither a shared tradition nor a "twins"-initial excess identifies a language, a reading, a name formula or the identity of the carvers; the report discusses which accounts each outcome favours.

## Outputs

Tracked: `joins.csv`, `transcription-checks.csv` (per object: witnesses, position counts by outcome, text status, initial-sign identification; no sign sequences), `run-*/summary.json`, `run-*/objects.csv` (per-object Δ without sequences), `verify-*.json`, `REPORT.md`, `SOURCES.md`, `RETROSPECTIVE.md`. Local only under `data/raw/2026-10-12-round-seal-tradition/`: source images and renders, per-sign check records, Reader 2's returned readings, checked transcriptions, and any file with sign sequences. A verification script recomputes T1 and the 091 test without importing the analysis module.
