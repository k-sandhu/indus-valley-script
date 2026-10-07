# Recommendations for moving Indus research forward

Status: Exploratory. Source rebuild dated 7 October 2026.

The rebuilt catalogue admits **59 recommendations drawn from 28 sources**, with **35 source records** including comparisons and background and covers **22 of the 25 requested researchers** with at least one recommendation. Regional and chronological analysis, attention to object context, and collaboration recur in the opened sample. These priorities support work already undertaken in the October 6 packages. The counts describe this bounded survey, whose source selection followed the review; they do not measure a vote across the field. [summary.json](summary.json), [roster-coverage.json](roster-coverage.json).

## Evidence and selection

Each row records an author's explicit recommendation, future priority or stated project aim, with a page, manuscript line, named web paragraph or timestamp. Descriptions of a method and findings were excluded when no prescription was located. Interpretations needed to check the lecture are in [positions.json](positions.json); sources that yielded no recommendation are in [coverage.json](coverage.json). Exact titles, authors, years, venues, URLs, read scopes and witness hashes are in [sources.json](sources.json). The row identifiers below locate the recommendation and its comparison passages in [recommendations.json](recommendations.json).

The 33 original rows were reviewed individually: 28 have replacements read from sources, and five were dropped without replacement. A replacement can use a different source and does not endorse the original wording. The 14 source-record corrections and 16 missing-item dispositions have separate ledgers. The nonexistent Miller 2013 citation was removed; her actual institutional page supplies a stated project aim. The 2024 Frenez Lothal title was corrected from the opened Crossref DOI record, with no recommendation admitted from the inaccessible article. [row-rebuild.json](row-rebuild.json), [source-corrections.json](source-corrections.json), [missing-item-disposition.json](missing-item-disposition.json).

Local witnesses in `research/literature/sources/` were reused before downloads. New pages, PDFs, extracts and failed responses remain under the local raw directory. The acquisition log records timestamps, paths and hashes; HTTP success alone was insufficient, since one publisher response contained an unrelated sponsor page. A source's `opened` flag means the stated `read_scope` was inspected: an abstract, author extract or web-page rendering does not become a full paper. [Acquisition log](../../data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07/acquisition-log.json).

### Frenez's lecture and written parallels

The video is *Ongoing decipherments : Writing in the Indus Civilization - by Dennys Frenez*, ILARA's lecture 9, uploaded 3 October 2026. Its description uses *Memorizing Meanings: Archaeological Perspectives on Writing in the Indus Civilisation*. The recording date and physical venue remain unverified. This package read the coordinator's caption-check note, which reports 1,166 English auto-caption lines; it did not retrieve or independently read the full transcript. The four lecture recommendations now use that checked record. [Video](https://youtu.be/1i9q17ld_jU), [coordinator check](../2026-10-06-research-program/frenez-talk-check.md), source FRENEZ-TALK-2026.

| Recommendation | Timestamp | Row |
|---|---|---|
| Work in teams with different kinds of expertise | 30:05-30:25 | F01 |
| Separate chronological and regional corpora | 24:45-25:40 | F02 |
| Contextualize frequencies and inventories against assemblage size, site and context | 28:45-30:40 | F03 |
| Study non-canonical external inscriptions and their unusual sign use | 51:00-53:00 | F04 |

Frenez's *Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities* (2018), in *Walking with the Unicorn*, printed pp. 186-187, explicitly develops an unbalanced-oligopoly model. His argument uses an approximately 65% unicorn share from Ameri's Table 19.1 and motif persistence to propose a limited set of formal socio-economic identities. Footnote 11 on p. 186 requests further testing of the branding assumptions; that prescription is F39. The social model itself is P01. [Opened local chapter](../../research/literature/sources/frenez_2018_private_person.pdf).

The same chapter places development within indigenous traditions on p. 167 and discusses script and standard seals at Harappa around 2800-2600 BCE on pp. 170-171. Frenez's opened 2021 Bologna workshop abstract also proposes local development around 3200-2600 BCE and stresses synchronic corpora and discovery contexts (P02, P06). The 2025 Sorbonne programme supplies a date and title but no abstract; the 2021 text was not transferred to it. Identification, property control and administration, deliberate rejection of neighbouring conventions, and the lecture's corporate-role interpretation are attributed positions, with caption locators in P03-P05. No opened written source here establishes the deliberate-rejection claim as archaeological fact.

## Recommendations by theme

The table counts each admitted recommendation once. Shared priorities below mean that named opened sources prescribe overlapping work. A dispute is recorded only for the passage and proposition the opposing source addresses.

| Theme | Rows | Main practical requirement |
|---|---:|---|
| Data and corpora | 9 | Object-linked text, images, sign definitions and production-stage records |
| Context and chronology | 21 | Comparable regional samples and specimen-level dates |
| Linguistic approaches | 4 | Explicit assumptions, sign/context evidence and language expertise |
| Computational method | 7 | Attested comparison systems and tests with defined inference scope |
| Collaboration and access | 8 | Specialist review, maintained data and permission records |
| New excavation and science | 10 | Fieldwork, sampling or independent archaeological measurements |

### Data and corpora

Rao and coauthors ask for analysis using all known texts and newer sign lists (2009, *A Markov model of the Indus script*, Discussion p. 13690; F16). Possehl's institutional author page sets out an authoritative sign list and more research on form and orthography (F49). Yadav calls for detailed study of stylistic variants by site and object type (2013, Conclusions p. 98; F20). Vahia's 2025 slides prescribe isolating composite signs and add-on elements (printed slide 43, PDF 40; F48). These overlap on corpus definition and graphic analysis, although their aims differ. Possehl's book itself was not opened; his three principles are attributed to his author page, obtained through an identified text proxy.

Kenoyer requires separating pre-firing producer marks from later graffiti (2020, p. 223; F11). Vidale's Appendix independently requires that separation and direct object access (2007, p. 364; F35). Farmer, Sproat and Witzel emphasize rare signs (2004, p. 37 n. 23; F23), while Frenez's lecture emphasizes external inscriptions (F04). Existing corpus files permit counts and candidate lists, but expert image and object checks are needed to settle variant and production-stage decisions.

### Context and chronology

Six named researchers or author groups explicitly prescribe chronological, regional or site/type control: Wells (2015 Preface viii; F05-F06), Kenoyer (2006 p. 21; 2020 pp. 230-231; F13, F15), Rao and coauthors (2009 p. 13690; F17), Yadav (2013 pp. 96-98; F19), Fuls (2023 abstract p. 45; F10) and Konasukawa (2023 abstract p. 50; F56). The caption-mediated Frenez lecture adds a seventh voice (F02-F03). Wells's opened Preface supports regional work, chronology and cooperation; it does not prescribe maintaining an updated comprehensive corpus. The update prescription belongs to Fuls (F09).

Fuls's abstract already uses a modified chi-square comparison of sign frequencies against expectations based on unequal per-site artefact counts. It also says the inscribed sets should not be treated as homogeneous. This corrects the first pass's claim that no available source supplies a denominator approach. Artefact counts define a corpus denominator; excavated area, recovery practices and occupation duration require additional records. D1 and D2 address site/type composition and inventory sampling within their stated data frames.

Ameri requests more regional studies of material classes, including architecture (2013, p. 371; F40). Petrie and Lynam prescribe finer local geomorphological, hydrological and subsistence information and further models of mobility in Cholistan (accepted manuscript, lines 656-658 and 675-678; F41-F42). Their settlement work makes contemporaneity relevant when comparing site scale. Farmer, Sproat and Witzel's proposed use of sign-frequency fluctuations to study social change is conditional on their nonlinguistic model (2004, p. 44; F25); it is not shared assent to that model.

Green's *Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization* (2021, printed pp. 182-184) requests research on potential inequalities, comparison of heterarchical corporate groups, and exploration of specialization and group attachments (F57-F59). His egalitarian interpretation supplies the framing; the rows do not map seal motifs to corporate groups. The paper was located during the final gap search and read separately from the excluded 2016 method paper. [Published PDF in author repository](https://api.repository.cam.ac.uk/server/api/core/bitstreams/1d70aa4e-82ca-4950-96cf-0ea200717ca0/content).

### Linguistic approaches

Wells asks linguists to identify or eliminate language candidates using detailed structure (Preface x; F08). Ganesan, Subramanian, Suresh Babu and Mahadevan state a goal of extending textual and contextual segment analysis toward identifying the language (2010, section 8, original reader pp. 5-6; F21). Parpola requires establishing iconic meanings before considering rebus uses (2008, p. 127; F22). Mukhopadhyay prescribes narrowing the semantic domain before studying individual signs (2023, p. 2; F36). These are distinct research routes with substantial unresolved premises. The repository can test graphic and contextual predictions, while authenticated language and semantic readings remain unavailable.

The writing/non-writing debate is explicit. Parpola's 2008 chapter (pp. 111, 113-115) and Vidale's 2007 reply (pp. 361-362) contest Farmer-Sproat-Witzel's claimed demonstration of a non-writing system. The comparison entries scope those disputes to the underlying thesis and arguments about repetition and rarity; they do not turn disagreement over interpretation into opposition to collecting rare-sign data.

### Computational method

Rao and coauthors propose grammar induction (2009, p. 13690; F18). Sproat's 2013 author monograph includes grammar induction and asks for features less dependent on text length, wider taxonomies and more nonlinguistic corpora (pp. 84-86; F29-F30). Sproat's 2010 article requires validating techniques on known linguistic and nonlinguistic systems (p. 592; F27). Rao and coauthors' 2010 reply calls for better tests within an inductive evidence framework (p. 803; F31). These prescriptions share an interest in comparative tests, with differing claims about what their results can establish.

Sproat's 2010 critique, Rao and coauthors' 2010 reply, Sproat's counterreply, and Rao and coauthors' 2015 reply are now opened comparison sources. Rao's 2010 reply (pp. 798-799) distinguishes entropy similarity from proof and argues for multiple lines of evidence. Sproat's counterreply (author manuscript PDF 1, section 2) limits his original criticism to the original papers. Rao's 2015 reply (e198, e203-e204) disputes Sproat's statistical interpretation and length-related classification, while commending collection of nonlinguistic corpora. Sproat's 2014 abstract was opened, but its main article remains unread here; the catalogue does not infer a future recommendation from its method or describe Sproat as rejecting statistical inference generally.

### Collaboration and access

Wells (2015, ix; F07), Kenoyer (2020, p. 231; F14), Vidale (2007 Appendix, pp. 363-364; F32-F34), Fuls (2023, p. 45; F09) and the Frenez lecture (F01) explicitly seek cooperation, access or shared infrastructure. These are five sources with overlapping priorities. Vidale gives concrete proposals: an expert sign-list committee, a freely available font and digital archive, and internationally organized palaeographic theses based on original objects. Fuls asks for worldwide database access and updates after new inscriptions are published. Sproat separately calls for specialist computational review (2010, p. 593; F28).

Metadata and review queues can be prepared with current holdings. Image redistribution, original-object study and institutional database access require the relevant owners and specialists. The evidence census and H provide inputs for that preparation.

### New excavation and science

Kenoyer calls for more extensive Early Harappan excavation (2020, p. 230; F12). Law proposes northern steatite sampling, question-led investigation of northern borderlands, and long-term collaborative sourcing across large and small sites (2011, pp. 500-503; F43-F45). Miller's undated institutional research page describes a project launched in 2025 to identify possible Indus bureaucracies or record-keeping centres through technological data (F46). These require independent field or material evidence.

Rao's 2018 economic-function chapter explicitly requests more analysis and archaeological evidence (p. 525; F38). Mukhopadhyay proposes study of stamped pointed-base goblets to test standardized commercial use (2023, p. 29; F37). Rao's 2026 interview proposes partial reconstruction of numerical practices and continued excavation for longer or bilingual texts (F53-F54). Gokhale's 2023 abstract criticizes how the emphasis on reading and bilingual discovery leaves typology and purpose understudied; it provides a contextual critique, with no separate future-study row admitted from that abstract. Ratnagar's 2018 interview asks archaeology to reconsider repetitive plant/bone collection seriously (figurine discussion; F55). This narrow concern supports explicit sampling questions and does not prescribe abandoning collection.

## Priorities with current project data

These priorities rank additional work by available inputs, value of resolving an uncertainty and dependence on specialist or field access. They reuse completed analyses before proposing new calculations.

| Rank | Action and reason | Recommendations | Existing work and next boundary |
|---|---|---|---|
| 1 | Extend the object/source/date/site/type ledger and expose missing fields. Most contextual tests depend on these joins. | F02, F06, F11, F13, F15, F16, F35, F56 | [Census](../2026-10-06-evidence-census/collections-and-datasets/README.md), [D1](../2026-10-06-chronology-region/README.md), [E](../2026-10-06-backward-chronology/README.md). Reuse their registers; distinguish a face, physical component and documented specimen. |
| 2 | Interpret site/type frequencies and inventories within their sampling frame. Denominator and type composition directly affect comparisons. | F03, F05, F10, F17, F19 | [D1](../2026-10-06-chronology-region/README.md), [D2](../2026-10-06-sign-context-and-seals/README.md). Reuse existing rarefaction and composition controls; add exposure information only where documented. |
| 3 | Test dated motif stability and social-model predictions against explicit source frames. This connects the oligopoly argument to measurable distributions. | F25, F39, F40, F58-F59; P01, P03 | [D1](../2026-10-06-chronology-region/README.md), [D2](../2026-10-06-sign-context-and-seals/README.md). D2 supplies concentration and motif-conditioned analyses. Comparisons need matched dates, sites and object selection. |
| 4 | Assemble expert review queues for variants, composites and rare signs, with object images and competing classifications. Existing definitions can otherwise drive apparent differences. | F20, F23, F32-F34, F48-F49 | [H](../2026-10-06-byproduct-inventory/README.md), [D1](../2026-10-06-chronology-region/README.md), [G](../2026-10-06-resemblance-baseline/README.md). H supplies candidate work; adjudication needs specialists. |
| 5 | Build comparable external/core samples, recording reuse and deposition separately. External irregularities can be evaluated only against an appropriate core sample. | F04, F24 | [Regional-west report](../2026-10-02-connections-and-priority/regional-west/REPORT.md), [D1](../2026-10-06-chronology-region/README.md), [D2](../2026-10-06-sign-context-and-seals/README.md). Current external samples are small and their context joins incomplete. |
| 6 | Audit computational features on attested comparison systems with object grouping and length controls. Published disputes identify concrete confounds. | F27, F29-F31, F51 | [Nonlinguistic controls](../../research/literature/nonlinguistic_controls/README.md), [G](../2026-10-06-resemblance-baseline/README.md), [H](../2026-10-06-byproduct-inventory/README.md). Existing totem and weather limitations require new evidence or a changed input before retrying. |
| 7 | Inventory evidence for bounded numerical or economic predictions before modelling. An independent object measure could distinguish otherwise compatible interpretations. | F37-F38, F46, F53 | [D2](../2026-10-06-sign-context-and-seals/README.md), [H](../2026-10-06-byproduct-inventory/README.md), [Census](../2026-10-06-evidence-census/collections-and-datasets/README.md). Weight, capacity and function associations require new source joins. |

D2 reports sign 740 at **9.67% of all positions** and **10.67% of readable positions**, illustrating why a reported percentage needs its denominator. The input summary records `top_sign_counts["740"] = 1928`, `all_positions = 19946` and `readable_positions = 18067`. Its known square-seal motif subset has **1,246 unicorns among 1,609 motifs, 77.44%**, in the motif record with `population = square_seals`, `level = global`, `group = all`, fields `unicorn_count`, `known_motif_objects` and `unicorn_share`. That subset differs from Frenez's approximately 65% reference from Ameri; the values cannot be pooled without reconciling object selection. These are existing D2 results. [D2 input summary](../2026-10-06-sign-context-and-seals/run-2026-10-07-01/input-summary.json), [D2 motif concentration](../2026-10-06-sign-context-and-seals/run-2026-10-07-01/motif-concentration.json).

G supplies an existing resemblance baseline relevant to Parpola's graphic stage and Rajan-Sivanantham's request for additional material evidence (F22, F52). Its controls and uncertainty labels constrain resemblance claims. The opened Rajan-Sivanantham source is an eight-page brochure, and its own recommendation concerns further documentation and material evidence; a blinded comparison was not attributed to the authors. E registers early specimens and sources, while new Early Harappan excavation remains outside this repository's present capabilities.

## Coverage and review limits

No recommendation is admitted for **Rita Wright, Vasant Shinde or R. S. Bisht**. Green's 2016 method extracts yielded no recommendation; a separate 2021 review supplied explicit agendas (F57-F59). Wright's excerpt download timed out, Shinde's inspected routes failed, and no inspectable Bisht agenda passage was found. Ratnagar, Possehl, Vidale and Miller now have sourced recommendations. [coverage.json](coverage.json), [roster-coverage.json](roster-coverage.json).

The remaining access limits are attached to source records: the full lecture transcript, Possehl's 1996 book, Sproat's 2014 main article, and several full papers were not recovered. No recommendation rests only on a search snippet. The mediated lecture and author-page rows should receive particular attention in review. Mechanical checks establish encoding, hashes, link resolution and export agreement; the reading and paraphrases remain Exploratory. The disk interruption and continuation checks are documented in [RETROSPECTIVE.md](RETROSPECTIVE.md) and [interruption-check.json](interruption-check.json).
