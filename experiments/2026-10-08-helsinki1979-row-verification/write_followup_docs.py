"""Regenerate living package documents from preserved pilot results."""
import json
from pathlib import Path
import workflow as W

FOLLOW='follow-up/2026-10-08-pilot2-v1'
PREP='pilot-2/2026-10-08-v1/preparation.json'


def save(name,text):
    W.owned(W.HERE/name).write_text(text,encoding='utf-8',newline='\n')


def main():
    save('README.md',f'''# Helsinki 1979 row verification: first pilot recorded, second prepared

Pilot 1 **failed the 95% all-fields control screen**: each initial role matched **16/18 controls**, and the final adjudicated readings matched **18/18**. Readers agreed on **185/216 targets**; **31** required adjudication. The final merge has **150 singleton-resolved rows and 66 candidate-only rows**, with zero ledger imports. [Frozen initial metrics](pilot/scored-initial-v1/metrics.json), `control_accuracy`, `target_agreement`, `screening`; [final control replay]({FOLLOW}/scored-final/metrics.json), `final_control_accuracy`; [frozen merge](pilot/merge-summary-v1.json), `dispositions`, `ledger_staging_rows`.

The seventeen Claude Sonnet 5.5 tasks used **6,218,955 measured combined tokens** and **23,373.822 summed seconds**. The coordinator's full-run projection has median **336.4 million tokens and 346.0 agent-hours**, with planning intervals **302.2–366.1 million** and **276.1–462.3 hours**. It assumes 328 column tasks per role, the observed disputed-column share and ideal concurrency. Billing remains unknown. [Measured aggregate]({FOLLOW}/pilot1-record.json), `measured_combined_tokens`, `measured_agent_seconds`; [original projection](pilot/coordinator-cost-projection-v1.json), `method`, `full_run`.

**Pilot 2 is prepared and unrun**: two blind readers, PDF pages **152 and 162**, **144 targets**, four column batches and **12 distinct hidden controls per role**. It uses v3 crop geometry and keys, clarified coincident-pair/hatched-unit conventions, and new cards labelled from P's v2.1 reference. The cards preserve all 687 glyph panels and identify 33 medium-confidence labels. [Preparation]({PREP}), `selected_pages`, `target_detected_rows`, `columns`, `controls_per_role`, `chart_cells`; [instructions](PILOT-2.md). Both pages are beginning-sorted and contain no proposed continuations; the pilot's coverage and cost inference have that limit.

## Run and review

The coordinator should use [PILOT-2.md](PILOT-2.md), which gives exact delivery, validation, usage-ledger, scoring, adjudication and merge commands. Its success criteria were added to [PROTOCOL.md](PROTOCOL.md) before page selection. Both initial roles need 12/12 exact controls, all source inventories must reconcile, final controls must match 12/12, and at most fourteen of 144 targets may enter adjudication. Candidate sets remain open values. L still requires reviewed object/surface concordance.

Run these checks from the repository root with fresh output paths:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/prepare_pilot2.py --out data/raw/2026-10-08-helsinki1979-row-verification/pilot2-reviewer-repeat-v1 --summary-out experiments/2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/reviewer-preparation-v1.json

& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/check_followup.py --raw-out data/raw/2026-10-08-helsinki1979-row-verification/pilot2-reviewer-check-v1 --out experiments/2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/reviewer-check-v1.json

python -B tools/review_prose.py --path experiments/2026-10-08-helsinki1979-row-verification --no-write
```

`score_pilot.py` and `merge.py` accept `--usage-ledger`. They join combined tokens by role/batch/run, preserve null input/output categories and retain returned timing alongside coordinator task duration. The first-pilot replays in [{FOLLOW}]({FOLLOW}/) reproduce its accuracy and merge without changing frozen outputs. [Ledger contract](INPUT_CONTRACT.md) defines validation and projection fields. The existing Python environment supplies PyMuPDF and Pillow; generation reads v3 proposals without inference. Temporary locations remain under N's local raw directory, and no dependency was installed.

The final follow-up checks pass **62/62**, including all frozen input pins, measured-ledger conservation, invalid-ledger rejection, eight blind packet checks and 687 unchanged glyph panels. The initial check's **59/61** result is preserved beside its correction. [Final checks]({FOLLOW}/checks-v3.json), `checks`, `passed`, `glyph_panels_compared`; [initial checks]({FOLLOW}/checks-v1.json). Actual source readings in these software checks: **0**. The original workflow regression also passes **123/123** with the amended code. [Regression]({FOLLOW}/regression-v4.json), `passed`, `total`.

## Evidence and files

[REPORT.md](REPORT.md) gives findings, dispute counts, timing comparisons and projection assumptions. [RETROSPECTIVE.md](RETROSPECTIVE.md) records preparation, the actual coordinator run and fixes. [sources.json](sources.json) pins source use; [registry-entry.json](registry-entry.json) proposes a Failed pilot entry for coordinator integration. [Follow-up path inventory]({FOLLOW}/changed-paths.json) lists every new or changed path. Earlier [PILOT.md](PILOT.md), packets, readings, scores and pending outputs remain historical witnesses.

The hidden-control references and chart labels come from AI readings with shared conventions and no expert check. Agreement measures workflow convergence on target rows; full-edition verification remains unfinished. All source-derived rows, images, proposals and synthetic fixtures remain under `data/raw/2026-10-08-helsinki1979-row-verification/`. Source: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, University of Helsinki, [handle](http://hdl.handle.net/10138/342677), CC BY 4.0. Crops, card arrangement and label strips are recorded modifications.
''')
    save('REPORT.md',f'''# First verification pilot and the prepared second pilot

The first pilot failed its initial-reader screen. Each role matched **16/18 all-fields controls (88.9%, Wilson 95% 67.2–96.9%)**, below the predeclared 95%. Adjudication produced **18/18 final controls (100%, 82.4–100%)**. Both roles had all eighteen numbers, classifications, counts and crop judgments correct; their strict sequences scored 17/18 and 16/18. No agreeing pair shared a wrong control. [Frozen initial metrics](pilot/scored-initial-v1/metrics.json), `control_accuracy`, `wrong_agreed_controls`, `screening`; [new final replay]({FOLLOW}/scored-final/metrics.json), `final_control_accuracy`. These references were previously adjudicated AI readings, with no expert check.

## What was read and what disagreed

Twelve fresh Claude Sonnet 5.5 sessions read six column batches on PDF53,83,170, one session per role and batch. Reader 1 corrected M v2 proposals; Reader 2 read blind. Five further fresh sessions adjudicated 31 target disagreements and four control disagreements, 35 items in total. All seventeen returns validated. Complete-column inventories reconciled for all six batches. [Coordinator account](pilot/PILOT-RESULTS.md), opening and Process notes; [measured replay]({FOLLOW}/scored-final/metrics.json), `progress`; [task aggregate]({FOLLOW}/pilot1-record.json), `tasks`.

The readers agreed on **185/216 targets (85.6%, Wilson 80.3–89.7%)**. The **31/216 adjudication queue (14.35%, Wilson 10.3–19.7%; page bootstrap 8.3–25.0%)** occupied five columns. Agreement included 144 singleton-resolved rows and 41 rows with matching candidate sets. The final merge added six singleton adjudications and kept 66 candidate-only rows. [Frozen scores](pilot/scored-final-v1/metrics.json), `target_agreement`, `adjudication_load`, `progress`; [frozen merge](pilot/merge-summary-v1.json), `dispositions`. The intervals summarize three sampled pages and shared chart/reference conventions.

The coordinator's dispute descriptions count control items alongside targets: seventeen coincident-pair disputes among eighteen items in page 83 column 1, seven hatched-kind cases, at least five U/comb label cases and six 597/598 cases. A reconstruction restricted to the **31 targets** gives the following overlapping row counts. Its rule compares the initial JSON fields and reads no source pixels. [Coordinator account](pilot/PILOT-RESULTS.md), Agreement and adjudication; [reconstruction]({FOLLOW}/pilot1-record.json), `dispute_patterns`, `pattern_method`, `target_disputes_by_column`.

| Target dispute pattern | Rows |
|---|---:|
| Coincident stroke pair | 16 |
| 596/454 unit-kind label | 6 |
| U/comb chart labels | 4 |
| 597/598 spacing | 5 |
| 235/593 bow-tie | 2 |
| 126/443 Y | 1 |
| 58/68 rectangle | 1 |
| Source y coordinate | 1 |

Thirty targets differed in units; one also differed in unresolved-field declarations, and another differed in source y. Target queues by column were 7, 0, 2, 16, 4 and 2 in page/column order. The four control misses were a wider 597/598 set, `sign` for hatched cells 454/596, a narrowed 543/769 pair, and a wider 465/485/486 set. Every one entered adjudication. [Reconstruction]({FOLLOW}/pilot1-record.json), `target_dispute_fields`, `target_disputes_by_column`; [coordinator control table](pilot/PILOT-RESULTS.md), Accuracy on the hidden controls.

All **66 unresolved merge rows have complete number, classification, count and crop-judgment fields; their only open values are code candidate sets**. The 72 multi-code unit sets comprise 34 {{9,765}}, 13 {{8,764}}, seven {{10,766}}, six {{543,769}}, three {{501,768}}, eight {{597,598}} and one {{58,68}}. Thus 63 sets concern coincident strokes. These sets remain preserved in the original vocabulary. The merge stages **150 resolved rows**, imports **zero**, and leaves reviewed object/surface concordance to L. [Reconstruction]({FOLLOW}/pilot1-record.json), `candidate_only_open_rows`, `candidate_sets_total`, `candidate_sets`; [frozen merge](pilot/merge-summary-v1.json), `ledger_staging_rows`, `real_ledger_imports`.

## Measured task cost and the full-run projection

Claude Code supplies a combined task total that includes context re-reads, with no input/cached/output split or bill. The coordinator ledger records **6,218,955 tokens**, **23,373.822 summed seconds (6.493 agent-hours)** and **28,791.458 tokens per target**, including controls and setup. Reader tasks used 349,502–462,740 tokens; adjudication used 1,308,140 for 35 items. The amended scorer and merge now compute these values directly from that ledger, retaining its hash and each matching task/run. The page 170 column 1 blind reader reported 1,566 seconds, while the coordinator recorded 4,503.897; projections use the latter and retain both. [Ledger](pilot/coordinator-task-ledger-v1.jsonl), `subagent_total_tokens`, `duration_ms`; [aggregate]({FOLLOW}/pilot1-record.json), `tasks`, `measured_combined_tokens`, `measured_agent_seconds`, `tokens_per_target`; [replay task ledger]({FOLLOW}/scored-final/cost-ledger.json), `tasks`.

| Role | Tokens | Summed seconds | Mean task seconds | Median task seconds |
|---|---:|---:|---:|---:|
| Assisted Reader 1 | 2,430,326 | 8,342.420 | 1,390.403 | 1,474.240 |
| Blind Reader 2 | 2,480,489 | 10,800.628 | 1,800.105 | 1,350.885 |
| Adjudicator | 1,308,140 | 4,230.774 | 846.155 | 919.501 |

Reader 1 had the slower median. Reader 2's long final task raises its mean, so the means favor Reader 1. Six paired columns without randomized exposure do not establish a proposal speed gain. The coordinator reported several useful proposal corrections, including numbers 3190 to 3199, 3166 to 3188 and 1100 to 1102; their existence does not establish a net time saving. [Aggregate]({FOLLOW}/pilot1-record.json), `tasks.*.mean_task_seconds`, `median_task_seconds`; [coordinator account](pilot/PILOT-RESULTS.md), Time and token use. Pilot 2 therefore uses two blind sessions per column.

The preserved coordinator projection uses M v3's **11,702 numbered occurrences, 67 continuations and 328 columns**, with **656 initial reader tasks** and one adjudication task for each column with any disagreement. Resampling the twelve measured reader tasks and five adjudicator tasks, with Jeffreys uncertainty for the observed five disputed columns out of six, gives median **336,377,793 combined tokens (95% planning interval 302,206,550–366,118,625)** and **346.046 agent-hours (276.073–462.331)**. Ideal wall time is **28.837 hours at twelve concurrent agents** or **14.419 at twenty-four**. [Original projection](pilot/coordinator-cost-projection-v1.json), `method`, `full_run`.

This projection includes observed chart/tool setup and hidden controls. It assumes sampled task costs and column lengths transfer to the edition, continued use of the same chart/context workflow, and sufficient concurrency. Continuation ownership/reading effort, rate limits, scheduling, human review and ledger concordance are not independently measured. Combined tokens supply no dollar price. The new scorer also offers a role-stratified column-task bootstrap, yielding median 336.513 million tokens and 347.022 agent-hours on the same measured ledger; its different seed and sampling rule leave the original projection unchanged. Its separate row/page projection scales per-target work and the target disagreement share. [New cost computation]({FOLLOW}/scored-final/metrics.json), `cost.column_task_projection`, `cost.full_run`, `cost.coordinator_ledger`.

## Prepared pilot 2

The dated amendment selects two pages uniformly without replacement from an ascending list using seed 2026100805. Excluding every recorded M evaluation/development/count/stress use, all v3 blind pages, and N's earlier target/control pages leaves ten eligible pages and excludes 149. The seed selects **152 and 162**, both beginning-sorted. Their v3 proposals contain **144 numbered targets, four columns and zero continuations**. There was no replacement after inspecting the proposals. [Preparation]({PREP}), `selected_pages`, `eligible_pages`, `excluded_pages`, `target_detected_rows`, `continuation_proposals`; raw `pilot2-2026-10-08-v1/coordinator/selection.json`, `excluded_pages`, `dependency_hashes`.

Both readers receive v3 geometry and complete source context, without proposed field values or codes. New cards carry v2.1 code, class and confidence labels by exact cell identity. All 687 original glyph panels are preserved, twenty code strips are revised, and 33 medium-confidence labels are marked. P's audit corrected eight primary codes and two classes; it combined one full AI reading, a second blind reading of 63 cells and a pixel sweep, with no expert review. [P guidance](../2026-10-08-chart-reference-audit/RECOMMENDED-USE.md); [preparation]({PREP}), `chart_cells`, `medium_confidence_labels`; [panel/label checks]({FOLLOW}/checks-v3.json), `checks`, `glyph_panels_compared`.

The revised instructions require the five coincident stroke pairs to remain complete sets and use `hatched_span` for cells 596 and 454. P's recommendation lists no additional mandatory stroke pair; other unresolved distinctions retain their compatible sets. Hidden controls come from v2, filtered conservatively to remove changed-code vocabulary, P-flagged rows, prior N controls and convention conflicts. The compatible pools contain five ambiguous and 24 singleton rows. Each column gets one ambiguous and two singleton controls without replacement, seed 2026100806. The twelve selected answers retain their original scored fields without a code remapping. Their accuracy measures unchanged vocabulary; the revised labels are supported by P's chart audit and remain exposed to fresh target comparison. [Protocol](PROTOCOL.md), post-pilot amendment; [preparation]({PREP}), `compatible_control_pool`; raw `coordinator/control-filter.json`, `rows`, `changed_cells`; [checks]({FOLLOW}/checks-v3.json), control preservation and distinctness entries.

The new screen requires at least 95% exact initial controls per role, all number/classification/count controls correct, no wrong agreeing control, complete source inventories, valid assigned returns, 100% final controls and a target queue of at most 10%. Here that means 12/12 initial controls per role and at most fourteen target disputes. Pilot 2 is **Proposed and unrun**. Its different target section, controls, chart, geometry and role exposure limit comparison with pilot 1; it measures the revised workflow as a whole. Neither prepared page tests continuation transcription. The coordinator instructions are [PILOT-2.md](PILOT-2.md).

## Verification and preservation

The first follow-up check passed 59/61. The adjudication copier initially carried only PNGs, omitting the new chart JSON and confidence notice; it now copies those chart assets and pins them. The other failed check compared instruction byte hashes across normalized line endings; the instruction text already matched, and the corrected check compares its content. The corrected run passed **61/61**, and a final synthetic-status check brings the final suite to **62/62** and verifies **1,098 frozen first-pilot files**, all 687 glyph panels, blind delivery, measured totals and malformed-ledger rejection. Constructed adjudication fixtures are labelled Synthetic and perform no source reading. [Initial and corrected checks]({FOLLOW}/checks-v1.json), [{FOLLOW}/checks-v3.json]({FOLLOW}/checks-v3.json). No frozen reading, score or chart was edited, and no full-edition inference or ledger import was run.
''')
    old=(W.HERE/FOLLOW/'prior-code-and-docs/RETROSPECTIVE.md').read_text(encoding='utf-8')
    old=old.replace('Prepared six column batches for each of two readers, covering 216 detected targets and 18 distinct reference controls per role. The final contract passes 123/123 checks. Actual readings remain unrun.', 'The initial preparation supplied six column batches for each of two readers, covering 216 detected targets and 18 distinct reference controls per role. Its contract passed 123/123 checks before the coordinator performed the readings. The follow-up below records those outcomes and prepares a second pilot.')
    save('RETROSPECTIVE.md',old+f'''

## Pilot recorded and second pilot prepared, 8 October 2026

The coordinator supplied twelve Sonnet 5.5 initial returns and five adjudications. Reused the frozen score/merge outputs, raw returns, task notifications and coordinator projection. Each initial role scored 16/18 all-fields controls, so the original 95% screen failed; final adjudication matched 18/18. The target queue was 31/216, and merge retained 66 candidate-only rows alongside 150 singleton-resolved rows. The new aggregate reconstructs 72 open sets, including 63 coincident-stroke sets. [Pilot record]({FOLLOW}/pilot1-record.json); [final control replay]({FOLLOW}/scored-final/metrics.json), `final_control_accuracy`.

The coordinator descriptions mix target and control disputes. Aggregating initial target fields separately gives sixteen coincident-pair, six hatched-kind, four U/comb-label and five 597/598 target cases, with overlap. These counts explain why the broader coordinator account reports seventeen, seven, at least five and six. Recorded both scopes beside their evidence. The earlier reference vocabulary stays preserved; no old numeric label was replaced.

Claude Code gave combined totals rather than token categories. Added a model-independent coordinator JSONL join to score and merge, with role/batch/run validation, optional identity/hash pins, coordinator-duration precedence and both original/measurement witnesses retained. The replay matches 6,218,955 combined tokens and 23,373.822 summed seconds. It reproduces the 216-row merge and 150-row ledger staging byte-for-byte. No bill was supplied, so monetary cost remains null. A new column-task bootstrap uses measured totals and states its own resampling rule; the coordinator's original projection remains unchanged. [Replay cost]({FOLLOW}/scored-final/metrics.json), `cost`; [merge replay]({FOLLOW}/merge-summary.json), `cost`, `merged_sha256`, `ledger_staging_sha256`.

Read M's completed v3 endpoint and interface and P's v2.1 chart audit. V3 is still quarantined after failing four frozen release criteria, so the second pilot uses its geometry and keys with independent page reading. P identifies twenty changed card code strips and two class corrections; new cards join labels by chart-cell identity and keep all 687 glyph panels unchanged. Confidence notice and medium labels remain visible. Reused the unchanged source PDF, source conventions, M evaluator functions, v3 proposals and v2 controls. No model inference, literature search, download or dependency installation was repeated.

Added the exploratory protocol amendment before selection and preparation. Chose two blind readers because assisted reading had the slower task median, while means were sensitive to one long blind task. Exclusion discovery left ten fresh pages; seed 2026100805 selected PDF152 and PDF162, both beginning-sorted. These supply 144 targets in four columns and no proposed continuation. Conservative vocabulary/convention filtering retained five ambiguous and 24 singleton control candidates; twelve distinct controls were selected without remapping their answers. Prepared eight 39-item packets in 29.267 seconds, with 29,250,943 local bytes at preparation. [Preparation]({PREP}), selection, pool, timing and byte fields. The page-section and continuation limits are explicit in the second-pilot protocol and guide.

The first new integrity run passed 59/61. Its adjudication test found that the old copier allowed PNGs only and omitted chart metadata/notice files. Extended the whitelist to JSON/Markdown under the chart directory, and included their hashes. The instruction comparison also failed because the copied text normalized line endings; content was identical, so changed that test to compare normalized text. Retained the failed output and fixtures, then ran a new check path: 61/61 passed. A final check that the revised screen retains Synthetic status for constructed returns passed as well, bringing the suite to 62/62. All constructed rows identify themselves as Synthetic. [Checks]({FOLLOW}/checks-v1.json), [{FOLLOW}/checks-v3.json]({FOLLOW}/checks-v3.json).

An exploratory PowerShell glob search passed literal wildcards to rg and failed; a directory search with rg's own file filters corrected it. One guessed retrospective filename did not exist; the relevant corpus retrospective and M's actual RETROSPECTIVE.md were read. Large combined inspection output was truncated, so exact fields were extracted in smaller reads. These inspection failures changed no research witness. The deprecated fitz import warning persisted while rendering completed successfully.

Current pilot 2 readings remain Proposed, with zero executed by this package. The coordinator must supply fresh isolated readings, actual task totals, adjudication and final scoring. Hidden controls share an AI reference and can be recognized as supplementary pages; chart labels have no expert check. Full-edition verification, dollar affordability, continuation effort and L's reviewed concordance remain unfinished. All edits stay inside N's owned/raw paths; first-pilot frozen files, other packages and repository history remain unchanged.
''')
    sources=W.read(W.HERE/FOLLOW/'prior-code-and-docs/sources.json')
    sources['follow_up_date']='2026-10-08'
    sources['sources'][0]['reading_scope']='N performs no row reading; the completed pilot comprises twelve coordinator-run reader tasks and five adjudications, recorded separately below.'
    sources['sources'][0]['source_locations'] += ['PDF152,162: pilot-2 source images rendered; no row readings performed by N']
    sources['sources'][0]['transformations'] += '; v3 geometry packet preparation; unchanged glyph panels with v2.1 code/class/confidence labels'
    for item in [
        dict(id='package-n-pilot1',title='Pilot results: two readers and an adjudicator on three pages',authors=['Research coordinator','Claude Sonnet 5.5 readers and adjudicators'],path='experiments/2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md',source_locations=['Accuracy on the hidden controls','Agreement and adjudication','Merged output','Time and token use','Process notes'],reuse='Frozen scores, merge, raw returns, task ledger and projection; no source re-reading'),
        dict(id='package-m-v3',title='Helsinki 1979: the completed v3 crop evaluation',authors=['Package M research agent','Research coordinator and Claude Sonnet 5.5 readers/adjudicator'],path='experiments/2026-10-07-helsinki1979-digitization/REPORT.md',source_locations=['Three frozen endpoints and their frames','Quarantine and row-verification workload','OPTION-B-INTERFACE.md: Physical-line records, Chart-label vocabulary'],reuse='Pinned full-v3 proposal geometry and occurrence/continuation keys; exclusions and evaluation functions'),
        dict(id='package-m-review-v3',title='Review of package M, v3 work (8 October 2026)',authors=['Claude Sonnet 5.5 reviewer'],path='experiments/2026-10-07-helsinki1979-digitization/REVIEW-V3.md',source_locations=['Verdict','Checked claims','M3. Reference provenance'],reuse='Read-only endpoint provenance and full-inventory review'),
        dict(id='package-p-v2.1',title='1979 chart-reference audit',authors=['Package P Codex audit agent','Claude independent chart reader and reviewer'],path='experiments/2026-10-08-chart-reference-audit/README.md',source_locations=['RECOMMENDED-USE.md: current v2.1 reference and N chart recommendation','chart-reference-v2.1.json: rows, limitations, audit','impact-v2.1.json: M_references.v2, M_templates, N_charts','amendment-decisions-v2.1.json: class 86 and contested 360 evidence'],reuse='Exact cell-joined chart labels, confidence notice and conservative control filtering')]:
        item.update(year=2026,venue='Private Indus research repository',url=None,opened=True,seen_only_search_snippet=False,quoted_words=0)
        sources['sources'].append(item)
    sources['reused_records'] += ['Package M v3 full-edition proposals and OPTION-B-INTERFACE.md','Package P chart-reference-v2.1.json and impact-v2.1.json','Package N pilot frozen scores and coordinator ledger/projection']
    sources['follow_up_search_scope']='Local records only; no new web search or download'
    save('sources.json',json.dumps(sources,indent=2,ensure_ascii=False)+'\n')
    registry=dict(id='HELSINKI1979-ROW-VERIFICATION-N-01',theme='Two-reader complete printed-row verification and cost pilot',status='Failed',
        question='Can two independent source readings and anonymous adjudication verify every printed occurrence affordably, with continuous controls and source-complete provenance?',
        outcome='Pilot 1: 216 targets, 185 agreements, 31 target disputes. Each initial role 16/18 all-fields controls, failing the 95% screen; final controls 18/18. Merge: 144 agreed singleton rows, 6 unique adjudications, 66 candidate-only rows carrying 72 sets; 150 staged, zero imported. Seventeen tasks measured 6,218,955 combined tokens and 23,373.822 seconds. Coordinator full-run median 336,377,793 tokens and 346.046 agent-hours. Pilot 2 prepared and Proposed: 144 targets on seeded PDF152/162, four columns, twelve distinct compatible v2 controls per role, eight packets, two blind roles, v3 geometry and v2.1 charts. Follow-up checks 62/62; no N source readings.',
        challenge='First-pilot shared conventions caused coincident-pair and hatched-kind disputes; chart labels changed after reading. Combined tokens have no category split or bill. Task medians showed no assisted speed gain; one blind outlier affects means. Two fresh beginning-sorted pages and no continuations limit the second pilot.',
        remedy='Preserved frozen endpoints; added measured coordinator-ledger joins and new replay paths. Preregistered post-outcome exploratory amendment, two blind roles, explicit candidate-pair/hatched-span rules, cell-joined v2.1 labels with confidence notice, all-use page exclusions and unmapped compatible controls. Full-run projection assumptions and AI-reference limits are adjacent to results.',
        evidence=[W.relative(W.HERE/p) for p in ['PROTOCOL.md','REPORT.md','PILOT-2.md','pilot/scored-initial-v1/metrics.json','pilot/scored-final-v1/metrics.json','pilot/merge-summary-v1.json','pilot/coordinator-cost-projection-v1.json',FOLLOW+'/pilot1-record.json',FOLLOW+'/scored-final/metrics.json',FOLLOW+'/checks-v3.json',PREP]],
        retry_when='Coordinator runs pilot 2 in fresh isolated sessions. Require >=95% exact initial controls per role, correct number/classification/count controls, no wrong agreed control, valid complete inventories, 100% final controls and <=10% target adjudication. Measure usage/bills and specialist/continuation workload before full expansion; L imports also require a reviewed occurrence/object/surface concordance.')
    save('registry-entry.json',json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    prep=W.read(W.HERE/PREP)
    for role in ('reader-1','reader-2'):
        path=W.HERE/'pilot-2/2026-10-08-v1'/role/'PACKETS.json'
        if path.exists():continue
        W.write(path,dict(status='Proposed',reader_mode='blind',packets=[b for b in prep['batches'] if b['role']==role]))
    print('Updated living reports, source register and registry proposal; wrote pilot-2 handoff manifests')


if __name__=='__main__':main()
