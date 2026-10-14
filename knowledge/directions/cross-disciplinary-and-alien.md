# Human symbols and unfamiliar artifacts

Reviewed 2 October 2026. The experiments on how objects were physically operated now have results from controlled simulations; the designs with human participants and the comparative designs below remain proposals. We draw on other symbol systems whose function, production or physical organisation is documented, as sources of new Indus tests.

## Function can shape a symbol system

A mark system used to distinguish owners faces different pressures from one used to count goods or reproduce speech. An owner badge must remain recognizable across copies. An account must preserve quantities and distinguish categories. A portable message must survive separation from its maker. These pressures give us measurable hypotheses about repetition, the reuse of components, errors and the relation between a mark and the object that carries it.

Recent research on human symbols supplies experimental designs. Bentz and Dutkiewicz's 2026 study reports conventional patterning on Aurignacian objects, similarities to early proto-cuneiform in selected statistics, and differences in information density by object type. Its authors supply data and computational analyses. [Bentz and Dutkiewicz 2026, PNAS 123(9), e2520385123, author text](https://www.researchgate.net/publication/401125892_Humans_40000_y_ago_developed_a_system_of_conventional_signs).

A September 2026 transmission-chain study compared decoration, group identity and denotational communication. It reports that marks became more regular across conditions and that some cognitive measures responded differently. [Pagnotta et al., DOI 10.1016/j.evolhumbehav.2026.106902](https://pure.au.dk/portal/en/publications/the-evolution-of-symbolic-artefacts-how-function-shapes-form-2/). A separate April 2026 study, first online in December 2025, found that delayed copying produced more regular and memorable marks, while social and functional context was still needed to explain the archaeological patterns it examined. [Simulating Symbolic Evolution in the Lab](https://pubmed.ncbi.nlm.nih.gov/41406238/). Graphical simplification through repeated communication also has an experimental precedent. [Caldwell and Smith 2012](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0043807).

We can use those tasks to build controls whose purpose is known and compare them with the actual constraints of making and using an Indus object.

## Comparisons by the property they expose

| System | Useful observation or resource | Experiment it supports |
|---|---|---|
| Proto-Elamite, earlier western Asia | Tablet editions preserve headers, entries, totals and seal associations. [Hawkins's primary edition](https://cdli.earth/articles/cdlj/2015-1) | Test recovery of administrative structure while withholding known readings; keep the tablet layout. |
| Central Asian seal traditions, broadly contemporary | Regional studies cover seal forms, compartmented designs and Indus-related material. [Kaniuth and Shaydullaev 2022 volume](https://www.vorderas-archaeologie.uni-muenchen.de/personen/wiss_mitarbeiter/kaniuth/publikationen/kaniuth-shaydullaev2022sapalli.pdf) | Compare manufacture, attachment and motif conventions along independently documented contact routes. |
| Gulf seals and sealings | Records based on museum accessions separate image conventions, cuneiform and Indus-related marks. [Existing object audit](../../research/literature/external_phonetic_anchor_audit.md) | Search for a joined object carrying independently readable information relevant to an Indus label. |
| Later Indian punchmarked coins | Museum records distinguish obverse punches from reverse countermarks. [British Museum specimen](https://www.britishmuseum.org/collection/object/C_1922-0424-4463) | Measure whether successive authorities and reuse create recurring combinations that resemble the recurring sign groups of Indus texts. |
| Andean khipu (knotted-cord records), much later | Urton compares numerical matches in records with shared provenance. [Urton, author manuscript at Harvard](https://dash.harvard.edu/bitstreams/7312037e-6b09-6bd4-e053-0100007fdf3b/download) | Test searches for duplicate accounts and for totals and their parts while keeping the cord hierarchy and archive identity. |
| Rongorongo, much later | A 2024 study combines wood dating with 3D documentation of four tablets. [Ferrara et al. (2024), Scientific Reports](https://www.nature.com/articles/s41598-024-53063-7) | Test transcription from curved surfaces and distinguish the age of the wood from the age of the engraving. |
| Constructed modern systems | Office routes, assembly labels, game states and annotated parts can have concealed, known rules. | Measure how well function is recovered from short inscriptions, damage and unfamiliar graphic codes. |

For each comparison, keep both the record as the source presents it and the version transformed for analysis. A knot hierarchy or a two-dimensional arrangement of countermarks can lose information when flattened into a string. Where the order of reading is uncertain, compare the documented order with alternative linearisations.

## The alien-artifact experiment

Treat an unfamiliar artifact as if its users and conventions were unavailable. Its material, geometry, operation, repeated parts and inscriptions become the available evidence. This can be tested with an answer key.

The first part we implemented is [physical-membership recovery](../../experiments/2026-10-02-six-hour/physical-information/README.md). It hides six quantities and gives the solver only object membership, meaning which objects contain which, and one count. The answer key is saved apart from the solver's input. Complete membership relations recover the relative values, and an independent count fixes their scale; incomplete collections keep the alternative solutions explicitly. The subsequent [measurement-choice experiment](../../experiments/2026-10-02-six-hour/physical-acquisition/PROTOCOL.md) compares the cost of acquiring relations and counts known only within an interval. These controls run by computer; a study with participants would add independent human observers.

The [known khipu control](../../experiments/2026-10-02-six-hour/khipu-control/README.md) now tests directly how representation affects what can be recovered. Flattening the cords into an ordered list in which each value keeps its known position preserves the published relation between accounts; removing that correspondence loses it. In generated records, knowing which cords hang from which constrains concealed positional values. A [whole-collection inventory](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/REPORT.md) corrects many errors in local membership, and independent counts expose a wrong decoder that eight redundant account checks had accepted. For an unfamiliar artifact this raises a practical question: which observable operation or quantity separates the candidate models that survive?

A [curved-clay contact model](../../experiments/2026-10-02-six-hour/stamp-geometry/README.md) also tests an explanation of graphic frequencies specific to the medium. Contact and damage change which of the invented graphics remain visible enough to be counted. When opposite pressing directions are paired, the graphics in the first and last positions have exactly the same distribution under the declared geometry. The planned physical experiment can replace those assumptions with measured grooves and impressions.

The Voyager Golden Record is a useful design example. NASA describes its cover's playback diagrams, a time reference based on a hydrogen transition, and instructions for reconstructing images. The cover ties the diagram physically to the recorded signal. [NASA, Golden Record Cover](https://science.nasa.gov/mission/voyager/golden-record-cover/).

Construct twelve small artifacts with concealed functions: authentication, counting, routing, assembly and a phonetic message. Match inscription length and the number of distinct signs across selected functions. Replace familiar letter shapes and remove identifying filenames. Give separate teams progressively more evidence:

1. Images of the object and its marks.
2. Dimensions, material and wear.
3. Access to the object's operation.
4. A few paired objects and observed outputs.

At each stage, require a fixed model that predicts the operation or output of a withheld artifact. Score successful predictions, confident wrong assignments and the number of adjustable conventions. Keep a separate withheld set for each stage so that later evidence leaves the earlier score intact. Include tool marks, rotated photographs and objects with identical marks but different capacities.

The experiment can show which physical observations resolve ambiguity and which analytical tools recover a known operation. A useful result might show that an attachment pattern lets teams distinguish an ownership badge from a counter, or that paired outputs identify a numerical relation. That result would guide the acquisition of corresponding archaeological observations.

## Production and perception experiments

### Copying on constrained media

Randomly assign participants to produce short messages, institutional badges or inventory labels within the same stamp area. Cross the assigned task with the production method, such as carving, drawing and impressing. Measure the reuse of components, the placement of modifiers, the number of signs, copying errors and successful use. Fit the analysis on some groups of participants and test it on new groups, with unconstrained drawing as a control condition.

The experiment separates effects of the task from effects of production. If the same feature at the end of an inscription arises across functions only when carving constrains it, it becomes a candidate production explanation. If a feature instead follows counting or identification across methods, we gain a more specific functional prediction to test on source-reviewed objects.

### Blind judgements of disputed features

Prepare permitted crops of fish modifiers, short and tall bars and compounds, with dates, sites and catalogue codes hidden. Ask annotators to record the visible components and their uncertainty. Vary lighting, scale and photographic source for the same object. Experimental carvings with known tool marks provide a control for damage.

The resulting confusion table can show which distinctions need new photography and which survive changes in how the object is observed. The uncertainty then feeds into alternative transcriptions, whose predictive consequences we compare without choosing a preferred encoding from the outcome.

### Component grammar and compression

Fit a grammar of reusable strokes and components to training images and predict the geometry of withheld glyphs. Compare it with a model of independent shapes and a model conditioned on material. Hold out physical objects and carving families. Repeat with invented marks and unrelated symbols matched for stroke count.

A component model that predicts new drawings provides evidence that the graphics are built economically from shared parts. The next experiment would test whether those same components predict an independently observed function or context. This makes the form of the signs useful even while the components' lexical roles remain unresolved.

## Assumptions and available evidence

| Issue | Treatment |
|---|---|
| Alien framing | A blind inference experiment using human-designed objects with a concealed answer key. |
| Unknown comparison meanings | Paleolithic signs, Proto-Elamite and Rongorongo carry different degrees of interpretive uncertainty. Use each for the property its source documents. |
| Historical connection | Contact or descent is a separate archaeological hypothesis. The distant comparisons above are chosen for task, medium or representation. |
| Chronology | The wood can be older than the engraving; mixed find contexts need separate intervals for manufacture, use and deposition. |
| Existing control results | In the first investigation, a simulation of documents routed between offices showed that the declared sequential statistic is compatible with a nonphonetic process. The totem-pole archive was sparse. In the weather-icon archive, grouping records by station and identical string joined every record into one dependence group. [Control audit](../../research/literature/nonlinguistic_controls/README.md), [methods findings](../../research/methods/FINDINGS.md). |
| Access in this update | We reviewed institutional abstracts, primary author text and catalogue records. The Central Asian volume and the comparison editions were located; their full image inventories were not transcribed here. |

Start with the twelve-artifact design and the blind feature task. They are small enough to debug the rules for observation and scoring before a larger study. The [cryptography memo](cryptography.md) and [roadmap](research-roadmap.md) record complementary work on anchors and acquisition.
