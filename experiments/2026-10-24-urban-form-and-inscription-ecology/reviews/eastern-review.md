# Semantic review of the merged register

Reviewer: GPT-6, Codex desktop collaboration harness, 24 October 2026. We reviewed coordinator `build_register.py`, `METHODS.md` and the three module registers and changed only this review file. The code references below describe the version inspected before a completed coordinator run was present.

The observation JSON merge preserves the original quantities, source locators, uncertainty and phase namespaces. The methods correctly distinguish rooms from households, construction from deposition, source assertions from independent archaeological events, and source chronological schemes from modeled boundaries. Five integration issues need repair before the domain matrix and duration output are used in figures. The most consequential are false feature-name matches and loss of an open chronological bound.

## 1. Review the domain index before treating it as recovered evidence

**Priority 1.** `build_register.py` lines 15–28 and 85–93 assign domains through unbounded substrings in `feature`. Several actual rows produce false hits or omit directly relevant observations:

| Case | Current behavior | Archaeological content |
|---|---|---|
| `EAST-FARMANA-005`, feature `early dwelling` | `well` matches `dwelling`, assigning water and sanitation and building inventory | A pit dwelling and its chronological attribution; it supplies no well observation. |
| `EAST-SURKOTADA-004`, feature `entrance relocation` | `location` matches `relocation`, assigning location and setting | A change of entrance, without geographic location evidence. |
| `EAST-KANMER-015`, feature `chronological extent` | `extent` assigns settlement extent | An urban date bracket, with no spatial extent measurement. |
| `EAST-KALIBANGAN-002`, `-008`, `-009` | Settlement extent is `not-recovered` | These give the early enclosure, citadel and lower-city dimensions. |
| `EAST-SURKOTADA-006`, `-016` | Settlement extent is `not-recovered` | These give the citadel and annexe dimensions. |
| `EAST-KANMER-012`, feature `open-space occupation` | No incremental-change hit | A named earlier open space becomes occupied while orientation remains unchanged. |
| `EAST-SURKOTADA-014`, feature `passage closure` | No access or alteration hit | A later partial blocking of a named intercommunicating passage. |

The existing `completeness` sentence and summary note disclose that this is an index. They do not make these false domain assignments useful. A reader of a heatmap is likely to interpret a colored cell as evidence relevant to that domain.

Use a reviewed mapping from observation IDs to domain tags. This is a bounded table of 12 towns and 13 domains, so checking the contributing IDs is feasible. Regex can propose candidate tags, but the reviewed mapping should determine the displayed index. Word boundaries would immediately fix `well`/`dwelling` and `location`/`relocation`; they would not recover omitted dimensions or resolve `chronological extent`. Keep unmatched assertions visible for review. Name the displayed result an **assertion index** and retain a separate `completeness: not-assessed` value.

## 2. Preserve mixed evidence states and specific missing fields

**Priority 1.** Lines 87–93 collapse an entire domain into one status. The heuristic recognizes only the words `gap`, `conflict` and `unresolved`, with case-sensitive tests after a case-insensitive feature match. It does not recognize `source numerical inconsistency`, `explicit within-report disagreement` or a named `missing` feature unless its record happens to contain a nonempty top-level `missing_reason`.

Farmana's `EAST-FARMANA-017` and `-018` explicitly disagree about the early chronology, but the chronology domain is assigned `reported-assertions`. Kalibangan drainage `EAST-KALIBANGAN-015` describes observed house drains and soakage jars while also preserving the limit on absence of a regular street system. It becomes `explicit-gap`, obscuring the positive evidence in the same assertion. Shikarpur's unreached fortification base (`EAST-SHIKARPUR-007`) provides a two-stage repair sequence, while the missing reason concerns the first construction date. It currently makes layout and replanning appear to have only a gap. Conversely, an observed row with one missing measurement can be excluded from the positive set even though it supplies the requested feature.

Store parallel lists such as `assertion_ids`, `explicit_gap_ids`, `conflict_ids` and `negative_observation_ids`. A domain can contain several states. Let specific fields carry missing reasons, including the existing inscription module's `field_missing_reasons`, rather than promoting one missing field into absence of all domain evidence. An asserted archaeological absence, a preservation-limited absence, and an unsearched field should have distinct states. Any compact display should show a mixed state when observations and limitations coexist.

## 3. Keep open chronological bounds and source conventions in derived outputs

**Priority 1.** Lines 100–106 export `start_bce`, `end_bce` and their difference. They omit the source operators, uncertainty and numerical chronology payloads. `W-HAR-003` says Ravi occupation begins **earlier than** 3900 BC and has `start_operator: ">"`. The current export turns it into `nominal_span_years: 1100` with no surviving operator. Under the source statement, the span to about 2800 BC is open at the earlier end. A general continuity disclaimer does not restore that bound.

Require a bounded, same-convention interval before computing an equality span. Preserve `start_operator`, `end_operator`, approximate status and any alternative boundary. For this Ravi row, either omit a scalar span or label the arithmetic as an approximate lower bound with the operator retained. Do not display it as an exact 1100-year bar. Retain both source-bound uncertainty and continuity uncertainty.

The eastern module stores source-convention intervals in `chronology_numeric`, including Kalibangan's uncorrected historical BC dates and the contested Farmana scheme. None enters `duration-spans.json`, while western top-level dates do. This is a schema difference, not a difference in chronological evidence availability. Export a unified chronology-assertion table retaining the original convention, phase, operators, alternative dates and reason no elapsed duration was calculated. If the present figure intentionally includes only one source's bounded estimates, state that selection in its caption. METHODs line 53 should say that interval overlap is compared only within an equivalent convention, then under separately documented models; “under the original dating convention” could otherwise be read as allowing overlap between uncorrected historical BC and calibrated BC.

## 4. Retain multi-site associations in town cards

**Priority 2.** Lines 41–43 and 81–83 expect one exact town slug. `INS-029` has town `Harappa and Lahoma Lal Tibba`. It remains in the merged observations as `harappa-and-lahoma-lal-tibba`, but contributes to none of the 12 town cards. No validation error identifies the omitted association. This is the reported shared-imprint comparison between Harappa and its hinterland, so its regional relation matters to the study's integration.

Preserve the source's place wording and add `towns: ["harappa", "lahoma-lal-tibba"]`, or another explicit multi-place relation. The Harappa card can reference the same assertion ID without duplicating it as a new observation. List out-of-frame places and unmatched rows in validation. Counts of town associations can exceed counts of unique assertions; label those quantities separately.

## 5. Accept documented unknown phases without inventing a phase

**Priority 2.** The mandatory-value check at lines 74–75 rejects null phases even when the original row provides `field_missing_reasons.phase`. Run-v2 has 13 such errors. `INS-001` records the Dholavira panel's recovery chamber but explicitly declines to transfer a phase from a neighboring structure. `INS-012` reports analyzed seal material with no independently joined construction phase. `INS-040` records a repeated-die relation without a qualified construction date. These are useful records with documented unknowns.

Require either a nonempty phase or an explicit field-level reason for the unknown. Preserve the original null and add a normalized `phase_status: unknown` if needed. Do not fix validation by assigning an adjacent building's phase or a general civilization-wide date. The same rule should apply to every required archaeological field that legitimately remains unknown.

## Denominators, units and outputs

The methodological treatment of independent units is appropriate for a descriptive source register. The code does not pool house counts, fit a city ranking or run a population test. Its summary explicitly states that assertions are dependent and source-use records are not publications. It retains the original JSON payloads, including observed versus estimated counts and the scope of quantities. These are strengths to preserve through figure generation.

The `count_and_denominator` domain currently marks the presence of a count-like feature name. It cannot certify a comparable denominator. For example, an eight-room partial exposure, eight inferred households and nine successive building phases are different units. Require an explicit `denominator_ready` state before calculating any rate; it should ordinarily be unknown or false in this first register. A town's surface mound area must not be paired with a count recovered from a few trenches. Repeated reports of one well or seal group should retain a shared evidence-family key before any future aggregation.

The CSV export at lines 130–132 drops `quantity`, `unit`, scope, count and denominator fields and chronology payloads through `extrasaction="ignore"`. The narrative assertion often still mentions the values, but a reader cannot obtain the machine-readable numeric table from that CSV. Add a separate normalized quantitative CSV or explicit JSON-string columns for structured quantities and chronology. Keep the original JSON as the full record.

METHODs line 41 defines incremental growth as any ordered change to an existing layout. A wall buttress can be a single repair within a coordinated project, and a closed door can be an access change with no growth. Code the observed operation first, such as addition, infill, subdivision, closure or repair. Give `process_mode` its own state, usually unknown until construction timing and scale distinguish gradual accretion from a coordinated rebuilding. The later rival-account discussion already supplies the right interpretation; an explicit field would carry it into tables and graphics.

The inherited Q-1032 pointer is valid in principle and retains the original source hash. For usable downstream joins, also expose the old row's `axes`, `horizon_records`, `dated_part_assertions`, `coordinate_value_status` and `coordinate` basis, rather than making consumers infer that those records are absent because only `north_readings` was copied. The pointer remains the authority, and no copied scalar should acquire a new measurement status.

## Checks and review limit

We read all three module observation arrays and inspected their field and status distributions, checked actual domain-match results for the seven eastern cases, and inspected top-level numeric date rows. There are 126 western, 118 eastern and 43 inscription assertions. One multi-site town string lies outside the exact 12-town frame. Run-v1 is recorded as a failed source-wrapper adapter with no scientific output. When run-v2 became available we inspected its summary, validation, Ravi span and the Farmana, Kalibangan and Kanmer domain entries. It reproduces the specific index and chronology defects above and reports the 13 documented-unknown phase errors. The summary gives 287 assertions and 42 source-use records; the complete source-use count remains separate from 36 distinct held file hashes and 38 checked source-file records. The findings concern integration semantics; source-copy hashes and the original excavation interpretations were not independently reverified in this pass. The review's prose scan has no flags.

The strongest comparison remains defensible after these repairs: large urban frameworks can persist through local additions, repairs and changed circulation. A reviewed phase-and-feature table can test which changes were coordinated. The deciding next step is to freeze the named features, their phase joins and their exposed denominators before computing a district comparison or associating inscriptions with an administrative use.

## Run-v3 disposition, appended 24 October 2026

**The five requested integration repairs pass this spot check.** We inspected the generated observations, town cards, chronology rows, readiness CSV, summary and validation. The earlier review remains above as the record of run-v2.

The seven feature-index examples now behave as intended. Farmana's early dwelling is excluded from water and sanitation, Surkotada's entrance relocation is excluded from geographic setting, and Kanmer's chronology is excluded from settlement extent. Kalibangan's enclosure, citadel and lower-city dimensions and Surkotada's citadel and annexe dimensions are indexed as extent. Kanmer's open-space occupation and Surkotada's passage closure are indexed as alterations; the passage also enters access. Eleven individual membership checks cover these seven cases. Every domain cell carries `completeness: not-assessed`.

Observations, explicit gaps and conflicts remain in parallel arrays. Farmana's competing chronology rows remain visible together with the disagreement entry, and Kalibangan's drainage row retains both its observed installation and its exposure limit under a mixed status. Negative archaeological observations remain explicitly unadjudicated by this index. The separate readiness table has five fields for each of 12 towns, giving 60 rows; these describe work still to assemble.

The Ravi row preserves its `>` start operator and suppresses a scalar elapsed span. All five eastern `chronology_numeric` payloads survive exactly in the chronology output, including their source conventions and reasons for leaving duration unknown. The 13 previously null inscription phases normalize to `unknown`, retain `phase_raw: null`, and preserve the original field-level missing reasons. INS-029 remains one assertion, associates both Harappa and Lahoma Lal Tibba, appears in the Harappa card, and identifies the hinterland place outside the core frame.

Run-v3 validation passes with no errors. The full JSON remains the authoritative record for structured quantities and chronological conventions; the earlier suggestion for a normalized quantitative CSV remains an output improvement. This disposition checks the specified integration semantics and does not independently verify every primary-source reading or establish a new archaeological result.
