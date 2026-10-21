# Harappa sealing and vessel settings

Written 20 October 2026 before new object-source acquisition or outcome coding. Authors: GPT-6.1-sol, Codex collaboration subagent `archaeological_setting`. Harness: Codex tools, Python 3.13, the repository source workflow and shared bench. Main endpoint: `source-review`.

We will recover the physical operations and excavation settings represented by Harappa sealings H-1719–H-1725 and stamped vessels H-1727–H-1766. All 47 targets remain in the disposition table. The object-source gap is documented by ARCH-01, whose 2 October frame identified no primary figure for these 47 targets. Its retry requires previously unavailable source plates or identified physical views. This run searches original HARP publications and their author-hosted photographs for those views and explicit registration joins. We will preserve failures and uncertain matches.

## Inputs and scope

We have read AGENTS.md, the orient, add-data and start-study skills, README, knowledge/INDEX.md, knowledge/DATA.md, the experiment registry, ARCH-01 and ARCH-02 and their linked reports and access records, the context-data plan, bench/README.md, the shots and meaning-map guides, CONTRIBUTING.md, the experiment template, the writing rules, redistribution rules, REUSE.md and LICENSE. Read-only PDF inspection follows the PDF skill. Active Mohenjo-daro stratigraphy, findspot-map and seal-legend segmentation packages are outside this run.

Starting sources are Kenoyer and Meadow's *Inscribed Objects from Harappa Excavations 1986–2007*, the existing 81-target frame, the pinned Lipi face export, and earlier original HARP excavation publications. Acquired PDF, HTML, images, OCR and record-level export derivatives remain local under `data/raw/2026-10-20-archaeological-setting/`. We track our code, source pointers, own observations, aggregate results and hashes. Exact sign strings are excluded from tracked outputs.

Each target receives its CISI identifier, derivative family and face count where present, every source registration and excavation lot/item found, source coordinates, witness kind, acquisition status and a reason for any unresolved identity. A registration or an explicit catalogue cross-reference can establish identity. A matching-looking image without such a key remains a candidate. We preserve publication descriptions, visible observations and interpretations as separate assertions.

## Protocol before outcomes

1. Build the 47-target source-disposition frame and hash its starting inputs.
2. Locate relevant passages in the held HARP introduction, then search its original cited excavation publications and public author-hosted pages. Stop after six relevant primary publications or twenty targeted web searches, whichever comes first. No source-holder contact is authorized.
3. Acquire and hash new source files. Render complete relevant pages, inspect the object and caption, and record source coordinates. Where useful, make a crop with its parent hash and bounds. OCR supplies locators; pixels establish figures and small identifiers.
4. Record each supported operation: impression in clay sealing, impression in a vessel wall before firing, closure against a container or cord, incised addition after firing, or unresolved. Record whether the evidence is directly visible, a caption assertion, the excavators' interpretation, or a conjecture. A deposit description applies only to the objects explicitly identified by the source. Broad site associations do not become object contexts.
5. Summarize changes in primary-image availability, sourced registration/lot/item availability, manufacture/use evidence, deposition evidence and potential functional labels across all 47 targets. Compare only source-qualified operations and available matched objects. We will not fit a classifier if there are fewer than ten independent object/text groups in each of two operation classes, or if the class is reconstructed from the inscription being predicted.

This is a complete bounded source audit with descriptive comparisons. A new meaning or sign reading requires a dated amendment, a frozen candidate and competing prediction, and the appropriate versioned `python -m bench` output. The shared corpus has been widely inspected in earlier work; any re-split of it is exploratory. We will copy the spending ledger locally and propose additions rather than modify the shared ledger. Bench synthetic mode will test the selected protocol before a real run. With insufficient independent use labels we stop at the source result and freeze a prospective test whose next required observation is explicit.

## Candidate explanations and decisive evidence

The functional rivals are an owner's or issuer's identity, a commodity class, a production-stage authorization and a ritual designation. A physical closure can constrain when a mark was applied and what it contacted. A pre-firing vessel-wall impression locates the act in the vessel's manufacture, while a separate clay sealing locates it in a closure or attachment operation. Neither observation alone authenticates a word or identifies vessel contents.

A useful functional comparison asks whether the same independently identified stamp or complete legend crosses those operations. The source must establish both identities and physical operations. Exact repeated legend and identical physical stamp are distinct relations. If a source supplies no matched labels, we retain that missingness and give the next discriminating measurement.

## Checks and reporting

The result builder refuses existing outputs. Verification will check all 47 targets, input/source hashes, join uniqueness, assertion provenance, missingness accounting, and aggregate counts. Run `python tools/kb.py check`, the prose scan and repository integrity check into owned dated paths. We own this directory, our local raw directory and `knowledge/registry/attempts/ARCHAEOLOGICAL-SETTING-2026-10-20.json`; shared-document proposals stay here. No CI, website build, publication, commits or pushes are included.

The report will state the new source observations, all failed paths, exact outputs, strongest functional reading justified by the evidence, credence and kill condition where a conjecture is proposed, and the prospective observation that would decide it.
