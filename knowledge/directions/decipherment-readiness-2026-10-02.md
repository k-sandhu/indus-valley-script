# Evidence needed for an Indus decipherment

We reviewed the project on 2 October 2026. We have usable sign transcriptions, groups of objects linked to their sources, and methods for comparing candidate explanations. The next step toward a reading is to connect a particular inscription or sign group to an independently observed quantity, object or activity, and then test the proposed connection on other objects.

The review covers the 101 entries in the experiment registry at the start of the audit, the four papers, and their relevant source and failure records. The [dated review](../../experiments/2026-10-02-decipherment-readiness/README.md) records its coverage and the hashes of its inputs. We assessed computational results from their preserved methods and outputs; the new calculations check only source coverage and descriptive compatibility. Comparisons on the objects now in hand are exploratory; a confirming study needs a block of observations reserved in advance and kept out of the exploration.

## What the existing work supplies

| Resource | What we can use it for | Evidence still needed for a reading |
|---|---|---|
| Pinned transcriptions, original-source images, catalogue joins and graphic uncertainty | Locate repeated inscriptions and inspect particular marks on their original objects | Reliable fine sign identity, orientation and segmentation for each proposed reading |
| Restoration and substitution studies | Test sign order, identify recurring frames and rank a deliberately hidden graphic | An outside observation that distinguishes possible meanings of the frame or sign |
| Mapping and latent-form code | Compare candidate correspondences when a reference and its record process are justified | A historically supported reference, or observed functional/quantitative constraints tied to the Indus objects |
| Exact numerical solvers and acquisition studies | Enumerate possible quantities, identify unresolved ratios or scale, and choose discriminating measurements | Independently recorded counts, contents or complete inventories, with their units and relation to the inscription |
| Harappa, Lothal and Kanmer source frames | Study face relationships, production groups and physical operations | Independently coded function, contents, ownership or wear observations for the proposed interpretation |
| Dependence and calibration studies | Keep copied texts, shared stamps and recording quality in the test design | An evaluation block whose relationship to the discovery objects is known |

The table uses several of the project's working terms. A pinned transcription is one fixed at a recorded version, and a catalogue join links entries for the same object across catalogues. A frame is a recurring context into which different signs are substituted, while a source frame is a set of objects defined from the original publications. Mapping code assigns unknown symbols to the symbols of a reference system, given a model of how that system's records were produced.

The missing connection can take several forms. A counted collection with an associated label can constrain a numeral. A known material or an independently identified operation can constrain a label's function. An archive that links an Indus seal to a named person could constrain a name. Corresponding texts in a known script could constrain both sounds and meanings. Several independent connections may be needed to distinguish the surviving interpretations.

Our existing outputs supply different parts of an inference procedure. Our best restoration score measures how well a model guesses which sign occupies a known, deliberately hidden position. The mapping successes use generated reference records whose symbol identities are known. Our exact rank calculation shows that population probabilities determine the parameters of a specified mixture model. The [computational review](../../experiments/2026-10-02-decipherment-readiness/computational/REPORT.md) lists what each output needs as input.

## Relevant observations outside the main benchmark

The main restoration population required a complete, right-to-left, single-line inscription with at least three signs. That choice served its prediction question. A partial-decipherment study needs its own set of objects defined from the sources, including short records and the arrangement of their faces.

All 66 recorded faces of the 22 Harappa tablets H2218–H2239 have two signs and fall outside that length filter. Their source drawings, registrations and deposition keys are already joined. Seven face observations support direct counts of three or four short strokes; specimens 8 and 16 display the readable face pattern 3, 4, 3. This source-defined group is therefore useful for investigating how a changing stroke group relates to the other form and to the adjacent faces. [Harappa source frame](../../experiments/2026-10-02-six-hour/harappa-object-frame/README.md).

The earlier context audit found that only two of 69 source-defined Harappa tablets, sealings and stamped vessels entered the main prediction population. Much of the material relevant to physical use therefore lies elsewhere in the project. A new study should keep whole objects, their separate faces, visible stroke height and side relationships. [Context coverage](../../experiments/2026-10-02-six-hour/context-audit/README.md).

A new filter check followed the catalogue's class of quantity-like texts through the same selection. Of 355 rows from 354 numeric families (groups of Lipi face records sharing the number before the decimal point, our provisional objects), 336 have two signs, 17 have one and two have three. Only two enter the main population. This modern class supplies a candidate set to search; its proposed numerical function is a hypothesis to test against the objects. [Corpus review](../../experiments/2026-10-02-decipherment-readiness/corpus/REPORT.md).

## Tests we can prepare from current sources

### A repeated Lothal inscription across different attachments

The Lothal source frame has 93 sealings, 68 of them joined to the corpus. Twenty-nine objects have eligible complete strings, comprising nine distinct inscriptions. One eight-sign group, G01, occurs on eleven objects that fall in seven of the source table's physical categories, its classes of container, contact material and fastening. The source already discusses repeated stamps on varied fastenings. The existing image review records the shape of the contact surface for L124, L126, L193 and L206. [Existing frame and recurrence results](../../experiments/2026-10-02-six-hour/lothal-physical-use/README.md).

A bounded test can ask whether the repeated inscription is restricted to one physical attachment geometry. Curvature, contact texture and cord path would be coded from the source images, with inscription identity kept separate. A confirmed contrast on two correctly joined objects would rule out that restriction for this inscription. The inscription could still identify a person, institution, class of commodity or operation spanning those attachments; the next observation must distinguish those hypotheses.

The variation in the table's categories is enough to define the test; confirming the images and reviewing whether the stamps are identical determine its archaeological outcome. The context label W1, the authors' warehouse inference, needs particular care because the authors assigned it partly from recurring stamps. The corpus contains only nine complete strings in this frame, so a broad classifier needs a larger collection defined from the sources.

The physical review also computes a descriptive bound on how well the recorded categories fit one category per inscription. Assigning each complete inscription one diagnostic category can fit at most 20 of 26 objects, leaving at least six exceptions in G01. The [source-category check](../../experiments/2026-10-02-decipherment-readiness/physical/current-checks.json) keeps the groups, ties and treatment of undiagnostic entries. The categories mix contact texture, support and fastening; a test on individual specimens should code those observations separately.

### Short modules on the Harappa tablets

Each face of these tablets carries a short module, a group of strokes beside one other form. Use the complete group of 22 objects to compare stroke counts, form identity, position on the left or right, face order and the published groups of engravers. Keep unresolved marks as sets of candidates and retain the three-dimensional arrangement. The first outcome would establish which graphic relations repeat across separate objects and which follow production or display orientation.

This can sharpen a hypothesis about quantities or units. A numerical value then needs a count or measured amount tied independently to the relevant module. A different photographic transcription of the same tablet improves observation without adding another known quantity.

## The numerical route and its missing evidence

Fuls's published 10/8/6 proposal is our most explicit existing numerical candidate. The project has enumerated four positive-integer solutions to the equalities it assumes. An additional reconstructed range for a bangle count selects the published values. The source audit leaves specific questions about objects and physical counts to resolve. [Numerical source audit](../../research/literature/metrology/numerical_source_audit.md), [exact solutions](../../research/methods/results/numerical_equalities/numerical_equalities_audit.json).

| Candidate | Existing evidence | Required observation |
|---|---|---|
| H904, Vats no. 477, excavation J213 | Original plates and table join a two-sided tablet; coarse long-stroke counts are visible | Author figure or historical register confirming the proposed ICIT 3786 join, readable remaining marks, and an independently supported relation between the quantities on its faces |
| M331 | Original photographs support coarse marks and grouped surfaces | Evidence for the proposed total/addition, common units and treatment of the separator |
| M-1383 | A current catalogue entry shares the identifier and proposed sign pair with the reported example | Original figure, artifact/material join and the count/refit record behind the alleged bangle range |
| H370–H372 capacity examples | Published fitted capacities and inspected coarse graphic features | Resolved measurement-to-object identities, raw measurement/reconstruction uncertainty and a new comparable object with an independent target |

The acquired Vidale chapter describes a reconstructed manufacturing assembly. It supplies no join specific to the M-1383 inscription and no independently confirmed count for the disputed range. Fits to vessel capacities also leave two things adjustable together: the value of a mark and the physical size of a unit. The next numerical test should name its target: a ratio, an absolute number or a measured amount in a fixed unit.

A useful quantity dossier would contain the original object registration, all relevant faces, an independently recorded count or amount, the measurement method, completeness, units and the scope of commodities. Write competing numerical rules before disclosing a reserved target, and report every candidate value still compatible with the measurements. Agreement on more than one independently observed object would support a restricted numerical reading; each further module needs its own evidence.

## Requirements for sounds and full readings

The objects we inspected from contexts of external contact provide evidence of historical contact and cuneiform inscriptions with names. The project's [external-anchor audit](../../research/literature/external_phonetic_anchor_audit.md) found no inspected pair of corresponding Indus and legible cuneiform texts. Shu-ilishu's seal identifies an interpreting role but supplies no Indus spelling of that name. Tell Jokha remains a useful target for object history and transcription, with the original report's specimen fields still sought.

A phonetic investigation can proceed through an identified name, a historically supported comparison of languages or systematic correspondences with another script. It needs fixed reading rules, a justified treatment of sign variants and segmentation, and predictions that differ from those of competing language or semantic models. Existing neural decipherment methods provide precedents for using related languages and phonetic constraints; their assumption of a known reference language must be tested in an Indus application. [Luo, Cao and Barzilay 2019](https://aclanthology.org/P19-1303/), [Luo and colleagues 2021](https://aclanthology.org/2021.tacl-1.5/).

The raw corpus also contains Sanskrit assignments and proposed translations from its upstream source. The analytical schemas keep those interpretive columns separate from observations. Their rules can become candidate readings for an independent comparison once their exceptions, segmentation and allowed values are fully specified. [Schema and interpretation-field audit](../../experiments/2026-10-02-decipherment-readiness/corpus/REPORT.md).

For the first restricted reading, reserve independently observed objects before tuning its interpretation. For an extended reading, require the same rules to handle additional sign combinations, contexts and exceptions, with their uncertainty recorded. No complete sign-to-sound proposal has passed such an archaeological evaluation in this project.

## Pictorial and historical routes

The archaeological memo supplies candidates from graphic shape, motifs, human handling and comparisons with other societies. These can be developed into predictions about the objects: a sign that looks like a container might follow a known container or class of commodity; a modifier might follow production technique, quantity or status. Record the visible features before selecting a word or a sound. The [archaeological review](../../experiments/2026-10-02-decipherment-readiness/physical/REPORT.md) identifies the source observations available for such comparisons.

Historical transmission offers another route when dated intermediate examples preserve a distinctive compound, position or practice. The project has comparative suggestions and experimental designs; the intermediate observations are still to be collected. Studies of how people interpret symbols, and controls using unfamiliar artifacts, can help choose observations and measure mistaken interpretations. Their predictions belong in the same tests defined from the sources. [Archaeology and iconography](archaeology-and-iconography.md), [cross-disciplinary designs](cross-disciplinary-and-alien.md), [community leads](community-proposals.md).

## Recommended next research cycle

Start with the Lothal attachment comparison and a source-preserving table of the Harappa short records. Both use material we already hold and can narrow the next question. In parallel, resolve the H904 and M-1383 joins and seek a separately counted or measured object within a specified module. The first decipherment target should be one quantitative value or one independently supported function of a label.

Each task should produce a table of observations linked to their sources, competing predictions and a separate evaluation record. Keep work on recognition and statistical controls proportional to the needs of that test. The existing restoration benchmark, mapping simulations and solver audits can be reused when a new input changes the question.
