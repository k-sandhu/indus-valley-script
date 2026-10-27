# Data readiness for reusable inscription units

We can begin independent layout adjudication and source acquisition now. A new confirmation test needs a reviewed object cohort, physical layout labels and exposure history. The executable audit reconstructs three work queues from held metadata: all 118 divided faces, 881 objects with unresolved assignments of multiple faces, and 358 post-catalogue inventory rows requiring identity and exposure review. The [readiness result](readiness-v1.json) records the counts and source hashes; the [release decision](release-decision.json) names each gate and its completion condition.

## The first work block

The 20 October audit contains 118 divided faces. Readers inspected 75 crops and confirmed a division on 65 faces; ten remain unclear. Forty-three faces lack a crop: 32 have CISI 3 numbers according to the earlier audit, and eleven lack a CISI identifier. Only 46 faces have an accepted physical-order label, and 33 of those satisfy the earlier clean-model eligibility rule. The remaining 29 imaged faces are the first adjudication queue. The current annotation set also needs a second reader and measured layout coordinates before a new study can rely on reader agreement or spacing.

The wider image queue contains 881 objects with multiple recorded faces for which at least one face lacks a verified side assignment. Linked images already exist for 378 of those objects; 503 require acquisition or a primary-source image join. The 797 faces attached to images with an unassigned side are a different denominator. The local queue records each provisional object and face ID, the available files and source locators. We can therefore start with accessible images while the missing plates are obtained.

These queues use the corrected 13 October image index and the later 20 October plate verdicts as separate observations. They preserve the earlier corrections and qualifications. A new reviewer must resolve any conflict between those records against the primary source before accepting an image identity. The register's provisional export families provide stable work IDs; confirmed physical identities require their own evidence.

With `--register-dir`, the amended audit adds each face's registered identity, image conflicts, accepted side-image count and an image-identity review task to the local queue. Historical image filenames remain available as source pointers. A quarantined register link is excluded from the accepted count and its face is prioritized for review. The first-run script is preserved as `audit-v1.py`; later integration outputs keep their own code and input hashes.

## What the labels can measure

The Indus labels record physical divisions and spatial order. They supply no complete word-boundary annotation. The next test can ask whether a frozen inventory predicts divisions and recurrence beyond layout and frequency controls. Its outputs must retain required-division recall and the rate of cuts at other positions. Precision and word-boundary F1 remain undefined on that reference.

Complete edited word divisions are already available in four readable-script rehearsal cohorts:

| Cohort | Previously used texts | Internal word boundaries |
|---|---:|---:|
| Sumerian seal legends | 309 | 1,187 |
| Sumerian lines matched to Indus lengths | 1,859 | 3,404 |
| Egyptian glyph sentences matched to Indus lengths | 940 | 914 |
| Akkadian letter lines matched to Indus lengths | 1,223 | 1,192 |

The audit rebuilds these memberships using the existing harness and runs no model on them. Their larger source pools retain document IDs, aliases and source word references. A document can be a composite or share its text with another object, so these IDs need a physical-source and dependence review before they define independent evaluation groups. These previously used cohorts support calibration and reproduction; a new prospective claim needs a declared exposure policy.

The [staged protocol](PROTOCOL.md) specifies complete-boundary F1 for readable controls and a separate physical-division endpoint for Indus. It requires source holdouts, grouping of aliases and repeated texts, comparisons with branching entropy and frequent fragments, and complete refitting under the declared randomization law. Discovery-only power work must justify the final sample and freeze. The protocol supplies pass and stopping rules, while the final cohort, exact exchangeability groups and frozen artifacts remain prerequisites.

## Exposure is the immediate shared blocker

The 20 October [spending proposal](../2026-10-20-seal-legend-units/spent-entry.json) calls broad prospective CISI 3 and post-catalogue pools fresh. The 21 October [retrospective](../2026-10-21-post-catalogue-finds/RETROSPECTIVE-CODEX.md) records accidental exposure to descriptive passages during extraction. Its combined source log has 892 entries. Every one of the 358 nonbaseline inventory rows cites a source with an access entry. The 301 definite post-catalogue rows are a subset of this review queue; eleven rows carry possible-duplicate markers.

Source access does not identify the exact objects or information each participant saw. A scripted page extraction, a displayed descriptive paragraph and a viewed seal image can affect eligibility differently. We therefore require a page-to-object and participant review, with the affected statistic or formula family recorded where known. This audit certifies no fresh object. Missing logs also leave exposure unresolved.

The same audit finds that `line_division_unit_boundary` and `seal_legend_closing_structure` appear in the historical proposal but are absent from the shared spending ledger. The earlier work remains historical exposure regardless of that bookkeeping gap. [ledger-update.json](ledger-update.json) proposes the two additions and replaces the broad prospective freshness declarations with an eligibility review, preserving the original endpoint and exact evidence hashes. It changes no shared file.

## Deliverables and checks

Run from the repository root:

```text
python -X utf8 -B experiments/2026-10-22-unit-readiness/audit.py --out experiments/2026-10-22-unit-readiness/readiness-NEW.json --local-out data/raw/2026-10-22-unit-readiness/run-NEW --register-dir data/raw/2026-10-22-object-register/run-v1
```

The script refuses existing output paths. The first completed run uses local `run-v2`; `run-v1` preserves partial queues from a path-normalization error described in the [retrospective](RETROSPECTIVE.md). It writes three CSV queues locally and records their hashes in the tracked aggregate. Input sequences, full inscriptions and source images are absent from those queues. Record-level derivatives remain local under the repository's redistribution rules.

Both the [synthetic segmentation test](segmentation-synthetic.json) and [synthetic shots test](shots-synthetic.json) pass. The scorer distinguishes complete boundaries from required divisions, and the generated shots exercise freeze, tamper, identity-closure and spending guards. No real confirmation split was created or read. [VALIDATION.md](VALIDATION.md) records the package and repository checks.

Our strongest supported claim is that the project has a defined, executable route from existing records to a test of reusable inscription units: the immediate work is 29 layout adjudications, 43 missing divided-face crops, and object-specific review of the candidate cohort. The decisive result will be a frozen inventory that predicts divisions and recurrent units on independently grouped, exposure-reviewed objects beyond the strongest prespecified layout and frequency controls.
