# Package Q: Steven Bonta's partial decipherment and his 2025 lecture series

Owned directory: `experiments/2026-10-08-bonta-review/`. Local raw directory: `data/raw/2026-10-08-bonta-review/`. Python environments: the system Python and `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`.

## Request

The user asked the coordinator to look through Steven Bonta's recent work, including the YouTube lecture series he published about eleven months ago. Bonta holds a PhD in linguistics from Cornell. He argues that the Indus script records an early form of Indo-Aryan (Sanskrit) and proposes phonetic and logographic values for selected signs, reached from distributional analysis of "fields" within inscriptions, especially metrology fields ("M fields"). Your job is to describe what he claims and how he argues it, to test what can be tested against this project's corpora and controls, and to place the work among earlier proposals. You evaluate his proposals; you do not adopt, extend or endorse any reading.

Read first: `AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/INDEX.md`, `knowledge/experiments/registry.json` (search it for related packages), `research/corpus/CORPUS_REPORT.md`, `knowledge/provenance/REDISTRIBUTION.md`, and the reports of packages D2 (`experiments/2026-10-06-sign-context-and-seals/`), G (`experiments/2026-10-06-weight-metrology/`) and H (`experiments/2026-10-06-resemblance-baseline/`). Also read the program's earlier lecture check, `experiments/2026-10-06-research-program/frenez-talk-check.md`, for the expected form of a lecture review.

## Prior first pass (another contributor)

A separate session has already written a first-pass source review, `research/literature/2026-10-08-bonta-first-pass/` (`README.md`, `sources.json`, `RETROSPECTIVE.md`). Treat its directory as another contributor's files: read them, cite them, and do not edit them. Do not repeat its source identification and argument walk-through. Build on it.

It identifies the twelve lectures, the 2023 first edition (academia.edu 105163460), the 2024 second edition and an April 2024 Aror University presentation text (academia.edu 118880153). It traces the route from fields to values with timestamps. It records that the categorical claim in Lecture 5 that Dravidian lacks noun compounding conflicts with Krishnamurti's *The Dravidian Languages*. It leaves three tests proposed:
- a frozen replication of the field distributions;
- a chance baseline for the lexical matching, with the same search tolerances;
- an object-level audit of the ICIT "validation" set described in Lecture 7, 18:32–24:37, including its overlap with the Mahadevan concordance material used to develop the values.

Those three tests are the core of this package, alongside a complete claim ledger. Where your reading of a passage differs from the first pass, record both readings and the timestamp.

## Sources already acquired (local only)

- **Lectures.** `data/raw/2026-10-08-bonta-review/captions/01-…txt` to `12-…txt` hold the twelve lectures of the channel "Indus Script Decipherment by Steven Bonta" (@IVC_Decipherment_Steven_Bonta). They were published between 26 October and 13 December 2025 and run about 9.5 hours, roughly 101,000 words. Each file carries a header with title, video id, publish date and length, then YouTube's auto-generated English captions in 20-second blocks with `[h:mm:ss]` stamps. The captions are machine transcriptions. They garble names, Sanskrit and Dravidian words and sign descriptions ("Indis" for Indus, "Bont" for Bonta). When a claim depends on a garbled word, say so, and use the paper to resolve it where you can. The lecture titles are:
  1. Introduction to a partial decipherment
  2. Languages in South Asia
  3. The nature of the evidence and how the script works
  4. Segmentation of Indus texts
  5. Evidence for language typology
  6. Evidence from the "M fields" for a testable entering wedge
  7. Testing the "anchor values"
  8. Fuller decipherment of selected signs
  9. Terminal and juncture signs
  10. What do the Indus inscriptions tell us?
  11. More on the language of the Indus inscriptions
  12. How to evaluate decipherment claims
- **Paper.** `data/raw/2026-10-08-bonta-review/papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt` is the text of *A Partial Decipherment of the Indus Valley Script: Proposed Phonetic and Logographic Values for Selected Indus Signs and Readings of Indus Texts* (2nd ed., 2024, 259 pages; academia.edu 120435855), taken from the public page. The Indus sign glyphs and figures are missing from this text. Where it says "sign" with a blank, the sign identity must come from the PDF or from context (catalogue numbers, sign-list numbers, descriptions). The coordinator has asked the owner to download the PDF. If a PDF appears in `data/raw/2026-10-08-bonta-review/papers/`, use it to resolve sign identities and record which results used it.

## Other sources to locate and record

academia.edu pages block plain HTTP fetches, so record what you could open. Search for the following:
- the 1st edition of the partial decipherment (2023, academia.edu 105134798);
- "Decipherment of the Indus Valley Script: In Search of an 'Entering Wedge'" (academia.edu 12412747);
- "'Decipherment' of the Indus Valley script: Expectations and Outcomes" (academia.edu 12412722);
- "The Indus Valley Script: A New Interpretation" (academia.edu 8691385 and 8691466);
- his talks at the Discussion Meeting on New Scientific Approaches to Understanding the Indus Valley Phenomenon, Institute of Mathematical Sciences, Chennai, 4–5 May 2015;
- a three-hour 2023 presentation on YouTube (`rOZ21f3DKs4`) and a video in which he hosts Yajnadevam's decipherment (`A-M8IoAlaGI`);
- responses to his work, including S. Kalyanaraman's "Interpretation is not decipherment" (academia.edu 113408961), a comment on Language Log (post 68508) and a November 2023 post by Koenraad Elst on X;
- any review, citation or reply in the academic literature.

Do not download or track third-party PDFs into the owned directory. Witnesses go in the raw directory with their URL and access date.

## Tasks

Write `PROTOCOL.md` before computing any test result. List every planned test with its statistic, null model, decision rule and data, and add dated amendments for any later change.

1. **Claim ledger.** Build `claims.jsonl` (and a readable `claims.md`) with one record per substantive claim, from the lectures and the paper. Each record gives the source with lecture and timestamp or page and section, a paraphrase, a short quotation of at most 15 words where wording matters, and a type:
   - corpus-distributional;
   - segmentation or structure;
   - typology;
   - sign value (phonetic or logographic);
   - reading of a text;
   - historical, linguistic or archaeological;
   - method;
   - evaluation criterion.

   Also record the evidence he offers, whether the claim is testable with the data available here, and which task below tests it. Identify how his claims changed from 2010 and 2015 through the 2023 and 2024 editions to the 2025 lectures.
2. **Concordance.** Identify the sign list and inscription catalogue numbers he uses (for example Mahadevan 1977, Parpola's numbering or CISI numbers). Map them to this project's corpora: the pinned Lipi observational export (local, unlicensed, so aggregates only in tracked files), Mayig (MIT) and its Wells crosswalk, and the 1979 Helsinki codes. Record every mapping's basis and every unresolved sign.
3. **Distributional tests.** Test his corpus-level claims against the local corpora. Report counts with bases and intervals, and compare them with prior published results and package D2's results (for example sign 740 at 10.0–10.7% of tokens and 69.6% final). Cover these at least:
   - his field segmentation (initial or prefix, M, core and terminal fields);
   - the composition of M fields (fish signs, ovals, the "mortar and pestle" beside triple strokes, stroke numerals);
   - his terminal and juncture signs;
   - any distributional evidence he gives for typology, such as suffixing.

   State which claims reproduce, which depend on a corpus or edition choice, and which fail. Use `research/corpus/fish_strokes/` and related audits where they bear on stroke and fish-sign readings.
4. **Readings against a null model.** He reports that his proposed values yield readings that match names, titles and words in Vedic, Puranic or other Sanskrit sources. He also proposes "anchor values" and tests them in Lecture 7. Design a test in the spirit of package H. Under his own matching rule, how often would readings produced by random or permuted value assignments match an open Sanskrit lexicon or name list as well as his readings do? Keep the sign inventory, the text set and the matching tolerance fixed.
   - Use openly licensed lexical sources and record their licences. Cologne Digital Sanskrit Dictionaries data is one candidate; check its licence.
   - Define the match rule from his examples before scoring, and include his own consistency checks.
   - Compute it for the subset of readings whose sign values you can identify, and report the coverage.
   - If the sign identities need the PDF and it has not arrived, implement and document the harness, run it on what is identifiable, and state plainly what remains.

   This is a test of whether the reported matches exceed chance under stated assumptions. It says nothing about the true language.
4b. **Validation-set audit.** Reconstruct as far as the sources allow which inscriptions Bonta used to develop his values and which ICIT inscriptions he then read as a check. Determine object-level overlap through CISI and excavation numbers in the local corpora. Report how many of the "validation" readings concern objects or texts he had already seen, and how many attempted readings failed, if he reports them.
5. **Metrology.** He interprets M fields as numerals and measures. Compare this with package G's weight results and with Mukhopadhyay's (2019) analysis of numerical and metrological signs. Say whether anything here yields a test against physical weights or counts, and run it if the data allow.
6. **Evaluation.** Summarize the criteria he proposes in Lecture 12 for judging decipherment claims, and apply them to his own proposal and to the results of tasks 3–5. Note where he meets them and where not. Do the same with criteria from the literature, citing them.
7. **Context and precedence.** Say what in his method or results is new relative to Mahadevan, Parpola, Fairservis, Wells, Mukhopadhyay, Yajnadevam's cryptanalytic Sanskrit proposal and other recent claims, citing sources you opened. Say what this project could reuse, for example his field segmentation as a feature in the object ledger or in metrology work, and which of his distributional observations deserve a clean replication.

## Deliverables

Write `README.md`, `PROTOCOL.md`, `REPORT.md`, `RETROSPECTIVE.md`, `sources.json` and `registry-entry.json`, together with the claim ledger, the concordance, code and aggregate outputs. Keep captions, page text, PDFs and any Lipi record-level output in the raw directory. Tracked files carry only paraphrases, short quotations with timestamps or pages, identifiers, counts and the project's own analysis. `REPORT.md` should open with a plain summary, written for the owner, of what Bonta claims, how strong each part of the evidence is, and what the tests showed. Then it gives the details.

Do not write to `knowledge/INDEX.md` or `knowledge/experiments/registry.json`. Another contributor has uncommitted edits there, and the coordinator integrates registry entries. Do not claim or imply that the script is deciphered, and do not present any sound or meaning as established; his values are his proposals. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Report what you could not access.
