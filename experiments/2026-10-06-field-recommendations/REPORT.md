# Published research priorities for Indus studies

Status: **Exploratory**. Source rebuild and final polish, 7 October 2026.

The catalogue contains **56 recommendations from 27 sources**, with **35 source records** covering recommendations, comparisons and background. Regional and chronological analysis, separation of artefact classes, and accessible collaborative data recur in the opened sample. The most feasible next work is to improve the object/context ledger and reuse site/type analyses. [summary.json](summary.json), [recommendations.json](recommendations.json), [action-ranking.json](action-ranking.json).

Each row admits an explicit prescription, future priority or stated project aim, with exact metadata, locator, required inputs, feasibility, short verbatim anchor and scoped comparisons. Six rows describe the authors' own project aims. Interpretations and findings appear in [positions.json](positions.json); excluded or inaccessible leads appear in [coverage.json](coverage.json). Selection frequencies describe this bounded opened sample. Rights and access limits remain attached to [sources.json](sources.json).

## Reading and comparison rules

Existing literature witnesses supplied much of the evidence. Additional pages and extracts remain in the local raw directory. Of the **59 original identifiers**, 56 remain recommendations, F04 and F53 are positions, and F55 is a coverage note. **57 anchors** match selected source text after whitespace normalization; **two** were read visually in original images. Each has fewer than 15 words. [validation.json](validation.json), [acquisition log](../../data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07/acquisition-log.json).

The fields `shared_or_disputed` and `n_independent_sources` describe each row's comparisons. Independence counts connected author groups across the row source and its scoped comparisons, including disputes about premises. This counts participation in the discussion; the relation field identifies agreement separately. Wells/Fuls form one group through their collaboration; Rao/Yadav/Vahia and overlapping coauthors form another. Frenez/Vidale also share a published abstract. The conservative grouping prevents overlapping papers from becoming independent endorsements. [author-groups.json](author-groups.json).

### Frenez's lecture and written parallels

The video is *Ongoing decipherments : Writing in the Indus Civilization - by Dennys Frenez*, ILARA's lecture 9, uploaded 3 October 2026; its description uses *Memorizing Meanings: Archaeological Perspectives on Writing in the Indus Civilisation*. The event date and physical venue remain unverified. The full transcript was not recovered. Paraphrases use the coordinator and second-review caption checks; this package independently read four short visible English auto-caption windows for anchors. Auto-caption wording can be garbled. This is the lecture evidence limit for the rows and positions below. [Video](https://youtu.be/1i9q17ld_jU), [coordinator check](../2026-10-06-research-program/frenez-talk-check.md), [second-review check](review-2/caption-check.csv), source FRENEZ-TALK-2026.

| Speaker's statement | Passage | Disposition |
|---|---|---|
| Proposes team effort with different expertise | 30:08-30:30 | Recommendation F01 |
| Proposes chronological and regional corpora | 24:36-25:12 | Recommendation F02 |
| Proposes investigating inventory differences with site size in context of use | 29:00-29:18 | Recommendation F03 |
| Reports non-canonical external sequences and alternative interpretations | 51:00-52:50 | Position F04 |

F03's `implementation_note` proposes assemblage counts, rarefaction and missingness checks as this package's analytical design. The speaker's frequency percentages belong to the descriptive portion. F04 records findings, so the external/core action below is a project choice supported by regional/context recommendations.

Frenez's *Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities* (2018), in *Walking with the Unicorn*, printed pp. 186-187, develops an unbalanced-oligopoly model of formal socio-economic identities. Footnote 11 on p. 186 requests testing of branding assumptions (F39). The model and its approximately 65% unicorn reference from Ameri's Table 19.1 are P01. [Opened chapter](../../research/literature/sources/frenez_2018_private_person.pdf).

The chapter's origin discussion on pp. 167, 170-171 and the 2021 Bologna abstract provide written parallels to local development (P02, P06). The lecture's administration/corporate-role, neighbouring-convention and origin arguments are P03-P05. They remain attributed interpretations with implications for dates, distributions and contexts. The 2025 programme's source record distinguishes its title/date from the opened 2021 abstract.

## Recommendations by theme

The headings follow the `theme` field. Every retained row is discussed under its assigned heading. [recommendations.json](recommendations.json).

| Theme | Rows | Required work |
|---|---:|---|
| Data and corpora | 8 | Text/image joins, sign definitions and production-stage records |
| Context and chronology | 21 | Regional samples, specimen dates and context |
| Linguistic approaches | 4 | Stated premises, context and language expertise |
| Computational method | 6 | Attested comparison systems and inference scope |
| Collaboration and access | 8 | Specialist participation, access and maintained data |
| New excavation and science | 9 | Fieldwork, samples or independent measurements |

### Data and corpora

Rao and coauthors request all known texts and newer sign lists (*A Markov model of the Indus script*, 2009, Discussion p. 13690; F16). Yadav requests stylistic-variant analysis across sites and object types (*Sensitivity of Indus Script to Site and Type of Object*, 2013, p. 98; F20). Vahia requests isolation of composite signs and additions (2025 slides, printed 43/PDF 40; F48). These address distinct parts of corpus/sign definition.

Kenoyer requires separating pre-firing producer marks from later graffiti (2020, p. 223; F11). Farmer, Sproat and Witzel emphasize rare signs (2004, p. 37 n. 23; F23). Possehl's author-page principle 1 requests form/orthography research and an authoritative sign list (F49). Vidale proposes standardized fonts, controlled additions and an accessible contextual archive (2007 Appendix proposal 2, p. 363; F33). Authoritative classifications require expert adjudication.

Sproat requests expansion of nonlinguistic taxonomies and corpora (2013 monograph, p. 86; F29). Rao and coauthors commend that resource contribution in their 2015 reply, p. e198. F29 records agreement on the resource; separate statistical comparisons identify disputed interpretations.

### Context and chronology

Five author groups prescribe overlapping chronological or regional work: Wells/Fuls (F05-F06, F10), Kenoyer (F13, F15), Rao/Yadav (F17, F19), Konasukawa (F56), and Frenez (F02-F03). Their prescriptions concern regional text structure, chronological development, site sequences, site/type fluctuations and contextual inventory differences. Locators are Wells Preface viii; Kenoyer 2020 p. 230 and 2006 p. 21; Rao 2009 p. 13690; Yadav 2013 pp. 96-98; Fuls 2023 p. 45; Konasukawa 2023 p. 50. The count follows these source IDs and [author-groups.json](author-groups.json).

Fuls's 2023 abstract compares sign frequencies with expectations based on unequal per-site artefact counts using a modified chi-square test. The paragraph begins "A special issue"; its final sentence requires heterogeneous artefact sets (F10). Artefact counts provide a corpus denominator. Excavated area, recovery practices and occupation duration need separate records. D1/D2 already analyse site/type composition and inventory sampling within their input frames.

Vidale requests coordinated palaeography on original objects through student theses (Appendix proposal 3, p. 363; F34) and separation by material, function, location and production stage before synthesis (proposal 4, pp. 363-364; F35). Kenoyer's chronological re-examination and production-stage distinction are specific parallels. Ameri requests regional studies of material classes, including architecture (2013, p. 371; F40). Vahia requests understanding modifications and other imagery within wider Harappan context (2025 printed 35, 47/PDF 34, 44; F47).

Farmer, Sproat and Witzel apply the Near Eastern second-hand seal problem to symbols and users of **Indus seals** (2004, p. 43 n. 28; F24). They propose sign-frequency changes as possible measures of historical development (p. 44; F25), and research on symbols' role in cultural cohesion and decline (p. 46; F26). These latter proposals depend on their nonlinguistic model. Parpola and Vidale's published replies dispute that premise; comparison entries specify its scope.

Frenez's branding-model test is F39. Green's *Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization* (2021, pp. 182-184) requests research on possible inequalities, comparative corporate-group organization, specialization and attachments (F57-F59). All three are marked **Limited**: present inscription/motif data cannot directly measure those social quantities. They are excluded from the ranking. [Green source](https://doi.org/10.1007/s10814-020-09147-9).

### Linguistic approaches

Wells assigns linguists the task of identifying or eliminating candidate languages using detailed structure (Preface x; F08). Ganesan, Subramanian, Suresh Babu and Mahadevan state a goal of extending textual/contextual segment analysis toward identifying the language (2010 section 8, reader pp. 5-6; F21). Parpola places iconic interpretation before rebus consideration (2008, p. 127; F22). Mukhopadhyay prescribes narrowing semantic scope before studying individual sign values (2023, p. 2; F36).

These routes require explicit linguistic/interpretive premises. The repository can examine graphic, structural and contextual predictions; its evidence supplies no authenticated language or semantic labels. Parpola's 2008 chapter and Vidale's 2007 reply contest Farmer-Sproat-Witzel's non-writing thesis at the passages recorded in the comparisons.

### Computational method

Rao and coauthors propose grammar induction (2009, p. 13690; F18). Sproat includes grammar induction among additional features and requests features less dependent on length (2013 monograph, pp. 85-86; F30). He asks for validation on known linguistic and nonlinguistic systems (2010, p. 592; F27). Rao and coauthors state a goal of better tests within an inductive framework (2010 reply, p. 803; F31). Possehl's author-page principle 3 recommends multiple lines of inference when testing decipherment claims (F51).

The published debate concerns inference scope and statistical arguments. Rao's 2010 reply, pp. 798-799, distinguishes similarity from proof and defends multiple lines of evidence. Sproat's counterreply, manuscript PDF 1 section 2, scopes criticism to the original papers. Rao's 2015 reply, pp. e198, e203-e204, disputes statistical interpretation and length-related classification. These opened replies appear in comparisons. Access to Sproat's 2014 main article remains unresolved in its source record.

Petrie and Lynam request further Cholistan mobility models linking sedentary and pastoral communities (accepted manuscript PDF 25, lines 675-678; F42). Credible landscape/settlement inputs require the work in F41.

### Collaboration and access

Frenez proposes teams (F01), Wells international/interdisciplinary cooperation (Preface ix; F07), Kenoyer continued collaboration and accessible publication (2020, p. 231; F14), Fuls worldwide database access and updates (2023, p. 45; F09), and Vidale an international sign/variant committee (Appendix proposal 1, p. 363; F32). Wells/Fuls, Kenoyer and Frenez/Vidale are three author groups within these overlapping priorities.

Sproat requests computational linguists in peer review (2010, p. 593; F28). Possehl's author-page principle 2 recommends many small research efforts (F50), which bounded repository packages can implement. Law states an international collaborative sourcing plan across large and small sites (2011, p. 503; F45). Access ledgers and review queues can be prepared now; object study and redistribution need owners and specialists.

### New excavation and science

Kenoyer requests Early Harappan excavation (2020, p. 230; F12). Law requests wider northern steatite sampling and question-oriented borderland excavation/re-excavation (2011, pp. 500-503; F43-F44). Petrie and Lynam request local subsistence, geomorphological and hydrological investigation (accepted manuscript PDF 25, lines 656-658; F41). These depend on field or material evidence.

Miller's biography describes a project launched in 2025 to identify possible bureaucracies/record-keeping centres through technological evidence (F46). Rao requests more analysis and archaeological evidence for economic-function proposals (2018, p. 525; F38). Mukhopadhyay proposes studying stamped pointed-base goblets for standardized commercial use (2023, p. 29; F37). Candidate/context inventories can be prepared; measurements and use evidence extend the available data.

Rajan and Sivanantham request documentation and material evidence about proposed cultural contact (2025 eight-page brochure, PDF 8; F52). Rao's 2026 interview says more texts are needed and hopes for longer or bilingual inscriptions from excavation (final attributed paragraph; F54). His numerical-reconstruction expectation is position F53. Ratnagar's general collection remark is coverage note F55.

## Ranked work with current data

Scores are this package's planning judgments. **Availability (A)**: 3 joined inputs, 2 partial joins, 1 major gaps, 0 absent inputs. **Autonomy (B)**: 3 local completion, 2 useful local preparation, 1 substantial specialist access, 0 new fieldwork. **Reuse (C)**: 3 foundational across themes, 2 several questions, 1 one question, 0 speculative contribution. Score is `2*A+B+C`; ties use availability, autonomy, then action ID. These weights prioritize usable inputs. [action-ranking.json](action-ranking.json).

| Rank | Bounded action | A/B/C; score | Rows and existing work | Reason and next requirement |
|---|---|---|---|---|
| 1 | Extend object/source/date/site/type ledger | 3/3/3; **12** | F02, F06, F11, F13, F15, F16, F35, F56; [Census](../2026-10-06-evidence-census/collections-and-datasets/README.md), [D1](../2026-10-06-chronology-region/README.md), [E](../2026-10-06-backward-chronology/README.md) | Foundational joins support several themes. Reuse registers and distinguish faces/components/specimens. |
| 2 | Interpret site/type inventories within sample frames | 3/3/2; **11** | F03, F05, F10, F17, F19; D1, [D2](../2026-10-06-sign-context-and-seals/README.md) | Existing counts and controls permit bounded interpretation. Document exposure before adding it. |
| 3 | Prepare image-linked sign-review queues | 3/2/2; **10** | F20, F23, F32-F33, F48-F49; [H](../2026-10-06-byproduct-inventory/README.md), D1, [G](../2026-10-06-resemblance-baseline/README.md) | Images/definitions support candidates. Adjudication needs specialists. |
| 4 | Prepare comparative feature/length audit | 2/3/3; **10** | F27, F29-F31, F51; [Controls](../../research/literature/nonlinguistic_controls/README.md), G, H | Disputes specify confounds. Failed totem/weather paths need new evidence before retry. |
| 5 | Document access, versions and review roles | 2/3/2; **9** | F01, F07, F09, F14, F28, F50; Census, H | Local ledgers/plans support continuing work. Permissions govern redistribution. |
| 6 | Specify dated motif-stability tests | 2/2/2; **8** | F25-F26, F39; D1, D2 | Existing concentration supports design. Matched dates/sites/selection and social evidence remain needed. |
| 7 | Audit external/core joins and seal reuse | 1/2/2; **6** | F05, F17, F19, F24; [Regional-west](../2026-10-02-connections-and-priority/regional-west/REPORT.md), D1, D2 | Small samples and incomplete joins lower feasibility. Regional/context priorities support this package design; F04 supplies descriptive motivation. |

D2 records **1,928 occurrences** of sign 740, **19,946 all positions** and **18,067 readable positions**: **9.67%** and **10.67%**. Its global square-seal record has **1,246 unicorns among 1,609 known motifs**, **77.44%**. These denominators and selections must accompany comparison with Frenez's approximately 65% reference. Exact fields are `top_sign_counts["740"]`, `all_positions`, `readable_positions`; motif selector `population=square_seals, level=global, group=all`, fields `unicorn_count`, `known_motif_objects`, `unicorn_share`. [Input summary](../2026-10-06-sign-context-and-seals/run-2026-10-07-01/input-summary.json), [motif concentration](../2026-10-06-sign-context-and-seals/run-2026-10-07-01/motif-concentration.json).

G supports preparation for graphic questions F22/F52 under its controls/uncertainty labels. E supplies early specimen/source registers. Goblet measurements, technological evidence, geological sampling and excavation remain additional-data work. Green's Limited rows F57-F59 require social/production-context evidence beyond motifs.

## Coverage and review

Recommendations cover **21 of 25 requested researchers**. Wright, Shinde and Bisht remain access/selection gaps; Ratnagar's opened remark falls outside the admitted agenda. [roster-coverage.json](roster-coverage.json), [coverage.json](coverage.json). Possehl's book and several full papers remain unavailable; substitute author pages, abstracts or replies are individually labelled. Every admitted row has an opened source record.

Repeat the exporter/prose checks, inspect all 59 anchors, and sample corrected F03/F04/F24/F53/F55 dispositions and F10's locator. Group counts and score arithmetic are mechanical checks; paraphrases and planning judgments remain Exploratory. [README.md](README.md), [validation.json](validation.json), [RETROSPECTIVE.md](RETROSPECTIVE.md).
