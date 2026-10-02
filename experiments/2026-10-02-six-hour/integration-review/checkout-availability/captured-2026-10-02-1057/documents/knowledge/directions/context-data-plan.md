# Archaeological context data plan

The present exports contain site, object-type, material, shape and some excavation fields, but completeness and source identity need a field-by-field audit. The next useful corpus is a table of observations with primary witnesses and known missingness. It should support a blinded test of whether inscriptions predict independently coded object use or context after accounting for site, date, manufacture and repeated objects/texts.

The October investigation measured a seal/tablet association in derivative metadata and inspected a small set of primary objects. It left the excavation-context join and the availability of useful independent response labels open. This plan specifies what to collect before choosing the next context endpoint. See the [corpus retrospective](../retrospectives/corpus-and-transcription.md), [source inventory](../provenance/SOURCES.md) and [original next tests](../../research/NEXT_TESTS.md).

## Observation model

Use separate tables for objects, contexts, witnesses, surfaces, graphic annotations and identity links. Each assertion carries its source, coordinates, observer, annotation version and confidence. Keep raw values beside normalized values. A minimal source record has `source_id`, author/title/year, access URL/date, file SHA256, rights status, printed/PDF page, figure/table/caption and exact object label.

| Table | Key and fields | Coding basis |
|---|---|---|
| `objects` | `object_id`; raw catalogue references; excavation year/item IDs; lot ID; museum/accession ID; site; material; colour; dimensions/units; shape; boss/perforation; carving/impression/relief/manufacture; preservation; object-type label | Publication tables and physical photographs. Separate catalogued identification from direct observation. |
| `contexts` | `context_id`; excavation source; site/area/block/room/trench/grid; stratum/layer/locus/lot; depth with datum and units; phase; date interval and dating basis; primary/secondary deposit; disturbance; associated assemblage | Excavators' context records. Keep a lot's identity distinct from its artifacts. |
| `object_context` | Object/context pair; asserted relation; confidence; source coordinates; alternatives | Join through item identifiers and primary records. Record uncertain association as a relation rather than forcing one context. |
| `witnesses` | `witness_id`; parent object/surface; photograph/drawing/impression; side caption; polarity/mirroring; scale/resolution; source hash; crop bounds and coordinate system; duplicate-photo suffix | Source image and caption. A witness may show multiple sides or objects. |
| `surfaces` | `surface_id`; parent object; raw A/B/C label; line count; line arrangement; direction evidence; inscribed/iconographic/plain status; relation to other sides | Source plate/caption and direct layout coding. Keep uncertain side assignments explicit. |
| `graphic_annotations` | Witness/surface/line/unit IDs; displayed order; bounding polygon; observed strokes/components; height/width ratios; damage; visible partial carving; auxiliary status; inventory/code candidates and namespace; reading-order transform | Blind descriptive annotation before catalogue/model candidates. A component can belong to a compound glyph. |
| `motifs` | Surface; motif description; component count; animal/body posture; horn/foot/tail features; associated apparatus; style attributes; uncertainty | Image observations. Assign catalogue animal names separately from descriptive features. |
| `use_assertions` | Object; proposed use category; source author; evidence type; direct wear/residue/sealing evidence; reconstruction; confidence; alternatives | Physical/archaeological evidence, with interpretive attribution. Seal, tag or tablet manufacture alone can be coded without choosing its historical purpose. |
| `identity_links` | Two identifiers; relation `same-object`, `same-side`, `extra-photo`, `impression-of`, `possible-match`, `repeated-text`; source/side evidence; confidence; adjudication history | Physical provenance first, then compatible graphics as additional evidence. |

For every field add `value_status`: `observed`, `catalogued`, `inferred`, `unknown`, `conflicting`, or `not-applicable`. Unknown values need a reason such as `not-reported`, `source-not-acquired`, `illegible`, `lost-context`, `ambiguous-join`, or `outside-scope`. Store competing assertions without discarding one. This allows completeness statistics to distinguish lack of publication from failed acquisition or unreadable material.

## Chronology and identity

Preserve the source's chronological terminology and stated range. A local “Stratum I” needs its own excavation sequence and datum; equal names at different sites are separate labels. A phase-to-calendar conversion should cite the dating model and retain interval uncertainty. Keep intrusion, residuality and secondary dumping visible. The H2218–H2239 cohort in the acquired Kenoyer/Meadow excerpt has a secondary-dump qualification, so its findspot and period support a different inference from an object sealed in a dated occupation surface.

Use archaeological item and accession identifiers to resolve physical objects. Lot identifiers belong to contexts. CISI bases, side captions, bis/ter/quater image suffixes and normalized export IDs stay in their source namespaces. Missing or compound references can produce candidate joins; only confirmed same-object links enter the physical identity graph. Sequence identity forms a separate dependence graph for prediction. P→W candidate arrays remain local graphic compatibility sets.

Objects with different inscriptions on several sides are represented once in `objects` and several times in `surfaces`. Store the original surface boundaries. Printed 1979 rows can combine sides/lines, so font digitization enters through witness units until its physical-boundary linkage is verified. Existing derivative sequence fields remain intact for comparisons.

## First completeness audit

Inventory the actual normalized metadata keys and raw values across all 5,680 Lipi rows, then collapse to physical families with conflict flags. For each field report row-level and object-level availability, unique values, placeholder frequencies, conflicts across faces and site/object-type concentration. Separate `None` as an asserted absent motif from `-`/empty/`Unknown` placeholders. Case/spelling normalization belongs in a versioned mapping table.

Report coverage for material, dimensions, manufacturing type, site, area, room/grid, excavation item, depth, stratum, phase, time/period and motif. List feasible response labels and their class counts within supported site/period strata. Trace a bounded random sample plus every uncommon label to primary tables/images. Publish an exclusion ledger for failed joins. This audit determines whether a context experiment has adequate data; labels should follow the available evidence rather than a desired result.

The Mayig subset can support graphic/stylistic annotation, but it is restricted to Mohenjo-daro unicorn seals and shares source photographs with Lipi. Its default uncertainty values and subjective unicorn subclasses need observer/source attribution. Compare independent annotations on a frozen block rather than selecting only catalogue agreement.

## Source acquisition order

| Source block | Intended fields | Completion criterion |
|---|---|---|
| CISI1 plates, catalogue and corrigenda already acquired | Object type, material/dimensions when reported, caption identities, motifs, side/layout, photo errata | Resolve source coordinates and a representative identity/metadata sample, retaining duplicate-photo structure. |
| Kenoyer/Meadow HARP introduction and item/context tables | Item/lot identifiers, excavation context, chronology and formal/informal media | Acquire exact edition and code a bounded object block with primary joins. The [17-page HARP link](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf) differs from the preserved 15-page excerpt. |
| CISI2/3 or primary Harappa reports | Missing H697A, H1897, H2139, H2200, H1100 and later Mohenjo objects | Acquire the requested physical plate/caption, not merely a numerical export match. |
| Jamison/Uesugi/Yamaguchi 2023, DOI `10.1016/j.ara.2023.100486` | Unicorn attribute/style coding and sampling design | Read primary definitions, distinguish measured graphic attributes from social/style interpretation, then assess transfer to selected witnesses. |
| Vats H904 and Vidale/M1383 records | Physical identity, paired-side counts, manufacturing context and vessel-content reconstruction | Establish the historical figure/object join and the independent numerical unit/count witness before adopting a metrological response. |
| SAHI2017 Tell Jokha lead | External-object identity, plate, layer, material and associated context | Inspect TJ17-PRO-S56/Fig 6.61 and primary caption/report. Current status is an acquisition lead. |

Retain URL, access outcome, file hash and observed reuse terms. Acquired images/text remain local according to [redistribution policy](../provenance/REDISTRIBUTION.md). No source-contact or external publication action is proposed by this plan.

## Blinded context test

Choose the target label and sample frame after the completeness audit, then freeze the protocol before scoring. A context coder sees primary object/context witnesses with inscription content masked where practical. A graphic coder sees inscription crops without response labels. Record disagreements and adjudicate them using a prespecified source rule. Freeze all eligible objects, including unknown or conflicting cases, before model output is available.

Use the simplest response that has independently observed evidence and sufficient variation within site/period/manufacture strata. For example, a physically evidenced sealing/attachment use category may be testable if wear, residue or associated closure evidence is documented. A broad seal/tablet type classifier is an available preliminary endpoint but mixes manufacture, layout, preservation and site; report those covariates explicitly.

Split by confirmed physical-object components and repeated whole-text components, preserving aliases before selecting unique texts. Discover grouping links from the full observational register, including faces excluded from scoring. Hold out source blocks or sites when enough groups remain. Report coverage and unsupported labels for every split. If dependence connects a comparator into one component, record that split as infeasible; the weather archive already produced this outcome under station-plus-identical-string closure.

Compare inscription features with a reference using site, date/phase, material, dimensions, object manufacture, length, preservation, source/resolution and motif where appropriate. Avoid a response or covariate derived from the sign sequence, such as Wells text class. Include a template-only comparator. Permute response labels within prespecified matched strata or components, rerunning tuning and fitting for each null. A label that varies only between sites cannot support a within-site effect estimate.

Report held-out log score, uncertainty grouped by physical/dependence component, per-class performance, coverage and missingness. Keep an object-weighted primary endpoint and declare any surface/token weighting separately. Audit sensitivity to unknown contexts, disputed identities and catalogue revisions without replacing the frozen score.

## Success and failure criteria

| Test | Evidence needed for success | Failure or stopping result | What it establishes |
|---|---|---|---|
| Metadata feasibility | Enough primary-joined objects and label variation for the frozen split/strata | Sparse or confounded labels, unverifiable joins, one dependence component | Whether a context endpoint can be estimated from this source block. |
| Blinded graphic-to-context prediction | Prespecified gain over context/manufacture/length/template references on a held-out source block, with declared null and coverage | Gain disappears under controls, source-block transfer or identity correction | A measurable inscription/context association within the sampled objects. |
| Physical numerical anchor | Confirmed figure/object join, reliable mark counts and independently evidenced unit/content relation | Ambiguous figure correspondence, damaged counts or unsupported reconstruction range | Constraints on the published numerical proposal's premises. |
| Prospective one-slot restoration | Photo establishes exactly one glyph span and visible constraints; frozen predictions calibrated on rare codes; subsequent independent evidence resolves it | Broad/unbounded loss or no independent resolution | Graphic candidate performance on an archaeological case. |
| Proposed semantic/phonetic reading | Prespecified external prediction with alternatives and a decisive source outcome | Flexible relabelling, incompatible held-out evidence or no discriminating prediction | Support or rejection for the particular proposed reading. |

A successful context association guides the next source test. Meaning and sound values require their own external predictions, such as a quantity/unit join, independently dated name or an authenticated cross-script correspondence. Record those premises and competing explanations once in the protocol, then evaluate the proposed prediction directly.
