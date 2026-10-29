"""Seed actionable questions from the retained roadmap, retry fields and conjectures."""
from pathlib import Path
import json
import os
import re

ROOT=Path(__file__).resolve().parents[2]
ROAD='knowledge/directions/research-roadmap.md'
CONTEXT='knowledge/directions/context-data-plan.md'
READY='knowledge/directions/decipherment-readiness-2026-10-02.md'
NEXT='experiments/2026-10-12-structure-first/REPORT.md'
EST='knowledge/directions/what-12-october-established.md'
C3='knowledge/conjectures/C-0003-unicorn-affiliation.md'
C4='knowledge/conjectures/C-0004-m895-office-text.md'
C5='knowledge/conjectures/C-0005-tablet-tiers.md'
ROWS=[]


def add(title,area,kind,priority,access,compute,difficulty,prior,related,sources,question,why,needs,decide):
    ROWS.append((title,area,kind,priority,access,compute,difficulty,prior,related,sources,question,why,needs,decide))


def main():
    add('Review a 30-object identity block','data','metadata',1,'local-only','hours','starter',['ROOT-19','OBJECT-LEDGER-PILOT-01'],[],[ROAD,CONTEXT],
        'Can a 30-object block from the held source collection be joined across catalogue, excavation and museum identifiers without forcing uncertain matches?',
        'Physical identity determines which faces belong together and which observations are independent.',
        'Use the roadmap’s observation block and held images/registers. Retain source namespaces, all aliases, locators, competing matches and a disagreement ledger in a new package.',
        'Stop after the fixed 30 objects. Every asserted same-object edge must have an accession, excavation or plate witness; retain unsupported edges as possible matches. Report resolved, conflicting and unresolved counts.')
    add('Audit completeness of object faces','data','metadata',1,'local-only','hours','starter',['CONTEXT-01','ARCH-01'],['F-0009'],[CONTEXT,READY],
        'Which objects in a fixed held-source block have all recorded faces represented, including plain and iconographic surfaces?',
        'A complete text-bearing export can still omit faces needed to test an object’s operation.',
        'Compare object records with source plate captions and face drawings. Keep surface IDs, missingness reasons, orientation and line layout separate from normalized text rows.',
        'Finish a frozen block and account for every source-captioned face. Mark completeness unknown where the publication does not enumerate sides. Do not infer a missing face from a missing text row alone.')
    add('Recount metadata availability by object','data','metadata',1,'local-only','hours','starter',['CONTEXT-01','DATASET-LANDSCAPE-01'],['F-0009'],[CONTEXT],
        'How do field availability and conflicts change when the held export’s face rows are collapsed to provisional object families?',
        'Repeated face metadata can overstate coverage, and placeholder strings previously inflated depth availability.',
        'Inventory the actual fields and raw placeholder values; preserve observed, catalogued, inferred, unknown, conflicting and not-applicable states. Report row and object denominators.',
        'Account for every row and provisional family in the pinned input. A field is present only under a declared rule; independently replay the counts and inspect every uncommon placeholder.')
    add('Normalize dimensions with retained units','data','metadata',1,'local-only','hours','starter',['OBJECT-LEDGER-PILOT-01','SIGN-CONTEXT-SEALS-01'],[],[CONTEXT,ROAD],
        'Can the dimension strings in an existing reviewed object block be normalized without losing units, axes, approximations or conflicting measurements?',
        'Seal-area tests require comparable measurements and a source for each conversion.',
        'Use held source tables and pilot assertions. Record raw text locally, normalized values, axis meanings, units, source coordinates and conversion rules; publish aggregate checks and permitted metadata.',
        'Stop at the chosen block. Every conversion must be reversible from its recorded rule; keep uncertain axes and unitless values outside the area endpoint. Report the coverage change.')
    add('Review museum field disagreements','data','verification',1,'local-only','hours','starter',['EVIDENCE-CENSUS-COLLECTIONS-01','EVIDENCE-CENSUS-SYNTHESIS-01'],['F-0008'],[CONTEXT,'experiments/2026-10-06-evidence-census/synthesis/join-summary.json'],
        'Which flagged site, material, dimension and sign-count disagreements in the held museum joins reflect aliases, terminology or conflicting source observations?',
        'A confirmed identifier join does not guarantee that the two catalogues describe an object consistently.',
        'Read the saved paired-field comparisons and source witnesses. Keep museum and corpus assertions with independent locators and classify the reason for each disagreement.',
        'Review all flagged disagreements in the chosen comparison block. Accept a correction only with a source witness; retain unresolved conflicts and separate incomparable measurements.')
    add('Check source coordinates in an object block','data','verification',1,'local-only','hours','starter',['ARCH-01','ARCH-02'],[],[CONTEXT,ROAD],
        'Do the saved page, plate, figure and caption locators lead to the stated objects in one held source block?',
        'Reliable coordinates let another contributor inspect the same observation without repeating source discovery.',
        'Use the original held edition and its hash. Distinguish printed pages from PDF pages and photograph identifiers from object identifiers.',
        'Check every locator in a fixed block and record edition-specific corrections in a new ledger. Stop when each resolves or has a recorded access or identity failure.')
    add('Trace chronology labels to dating evidence','archaeology','metadata',1,'local-only','days','expert',['CHRONOLOGY-REGION-01','CONTEXT-01'],[],[CONTEXT,ROAD],
        'Which period and stratum labels in the held Harappa block can be traced to an excavation sequence and an independent dating basis?',
        'Chronological transfer tests depend on residuality, secondary deposition and the relation between a lot and an object.',
        'Retain raw phase terminology, source-defined date intervals, dating basis, disturbance and object-context links. Use held item and context tables before designing a time test.',
        'Stop at the fixed source cohort. An object-level calendar assertion requires a cited conversion model and context relation; otherwise retain the source phase and mark calendar age unresolved.')
    add('Detect duplicated photographs','images','tooling',1,'local-only','hours','starter',['ROOT-19','HARP-LOTHAL-SOURCE-02'],[],[CONTEXT,'research/literature/cisi1_counting_and_errata.md'],
        'Which held photographs or scan panels are repeated witnesses of the same image rather than additional object observations?',
        'Duplicate images can inflate apparent photographic coverage and independent annotation counts.',
        'Hash the held files and compare candidate crops with source captions. Keep full-file and crop matches separate and publish hashes, identifiers and aggregate counts under the rights rules.',
        'Exact hashes establish identical files; near matches require visible crop and caption confirmation. Stop after the declared source block and retain doubtful pairs as candidates.')
    add('Distinguish missing motif from no motif','data','metadata',1,'local-only','hours','starter',['SIGN-CONTEXT-SEALS-01','OBJECT-LEDGER-PILOT-01'],['F-0029'],[CONTEXT],
        'Can the held motif fields distinguish a catalogued absent motif from an unknown, damaged, unreported or unacquired motif?',
        'Text-only seals and missing animal observations have different roles in motif comparisons.',
        'Inspect each placeholder type in the export and a fixed source sample. Retain the source’s label and a versioned mapping to value status and missingness reason.',
        'Stop after all placeholder categories and the fixed sample have been reviewed. Kill any normalization that merges asserted absence with unknown observation.')
    add('Rebuild dependence from all recorded faces','corpus','verification',2,'local-only','hours','standard',['ROOT-03','CONTEXT-01'],[],[CONTEXT,ROAD],
        'Do existing analysis splits preserve aliases and repeated whole texts when grouping uses the full observational register, including excluded faces?',
        'An excluded short or damaged face can connect an otherwise eligible object to a training object.',
        'Use confirmed physical identity separately from repeated-text dependence. Reconstruct group closure before eligibility filtering and compare it with a chosen saved split.',
        'Pass only if no declared dependence component crosses its evaluation boundary. Report every changed group and preserve the old endpoint; any leakage requires a separately dated rerun.')
    add('Audit the held H904 historical join','data','verification',1,'local-only','hours','expert',['ROOT-19','READINESS-01'],['F-0006'],[READY,'research/literature/metrology/numerical_source_audit.md'],
        'Do the held Vats records, plates and author references establish the proposed ICIT 3786 to H904 identity?',
        'The conditional numeral equations depend on the physical object and both faces.',
        'Review the held plate, J213 excavation registration and Vats number 477 against the historical identifier. List the specific missing witness through DATA if it cannot be resolved locally.',
        'Accept only an explicit historical crosswalk or matching registration plus both face witnesses. Stop when the held evidence is exhausted; leave the join conditional if the author figure or register is missing.')
    add('Audit the M-1383 numerical referent','data','verification',1,'local-only','hours','expert',['ROOT-19','READINESS-01'],['F-0006'],[READY,'research/literature/metrology/numerical_source_audit.md'],
        'Does any held witness connect the numerical proposal’s M-1383 to the reconstructed bangle assembly and its count?',
        'The additional range selects one arithmetic solution and therefore needs an independent physical basis.',
        'Compare source-captioned identity, material, figure and refit/count accounts. Keep the normalized export overlap separate from the proposed bangle referent.',
        'Pass only with an inscription-specific object join and documented count/reconstruction uncertainty. Stop at the held witnesses; record the absent source in DATA if no join is supported.')
    add('Verify the Lothal and M-895 text match','seals','verification',1,'local-only','hours','expert',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['C-0004','F-0030'],[C4,EST],
        'Do the held CISI plates confirm the same four signs in the same order on L-161 to L-170 and M-895?',
        'This is the cheapest direct kill test for the office-text conjecture.',
        'Record all photographed impressions, damage, orientation, fine-form alternatives and source coordinates. Have an independent reader inspect the same images without the proposed reading.',
        'Use C-0004 P1: all four signs agree. A confirmed mismatch kills that prediction; an unreadable sign leaves it unresolved. Do not fill a damaged sign from the catalogue match.')
    add('Verify the animals on the matched sealings','images','verification',1,'local-only','hours','expert',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['C-0004','F-0030'],[C4,'experiments/2026-10-12-seal-text-identity/REPORT.md'],
        'Do the held views independently establish the elephant on L-161 to L-170 and the catalogue’s unicorn label on the M-895 fragment?',
        'Different animal observations are a premise of the office-versus-travelling-seal test.',
        'Inspect the complete retained views and captions. Record which features are visible and which are inferred from the fragment or catalogue.',
        'Use C-0004 P2 and its credence rule. Pass requires both animals to be visibly or independently source-confirmed; an unidentifiable fragment remains unresolved.')
    add('Compare M-895 with the impressed seal','seals','analysis',2,'local-only','hours','expert',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['C-0004'],[C4,CONTEXT],
        'Can measured impression dimensions or carving features distinguish the seal that made the Lothal group from M-895?',
        'A different die carrying the same legend would change the competing movement explanations.',
        'Use held scaled views, impression distortion bounds and a feature protocol frozen before comparison. Retain missing scale and damaged-edge uncertainty.',
        'Use C-0004 P3: width differs by more than 10% or carved forms differ. If scale or contact distortion makes that test impossible, stop with an observation-gap record.')
    add('Resolve the Dholavira duplicate seal','data','verification',1,'local-only','hours','standard',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['F-0028'],['experiments/2026-10-12-seal-text-identity/REPORT.md',CONTEXT],
        'Are Dholavira 128.1 and 4225.1 two physical seals or two catalogue records of one seal?',
        'The smaller-site duplicate count is sensitive to this identity edge.',
        'Compare held registrations, dimensions, photographs and publication crosswalks. Keep text identity as supporting evidence separate from physical identity.',
        'Accept one-object status only with a registration or image-based identity witness. Report locality sensitivity under both interpretations if the join stays unresolved.')
    add('Review circular-seal transcriptions','images','verification',1,'local-only','hours','standard',['FOREIGN-FINDS-SEQUENCE-STATISTICS-2026-10-12'],[],[EST,CONTEXT],
        'Do held Gulf-type and South Asian circular-seal images support the fine codes and reading order used in the foreign-sequence test?',
        'The reported unusual ordering depends on a small object cohort.',
        'Review every eligible held circular seal, including direction evidence, mirroring and damaged alternatives, before opening its model score.',
        'Stop at the saved cohort. Retain every disagreement and recompute sensitivity only in a new endpoint after freezing revised annotations. Unresolved orientation remains a candidate set.')
    add('Join Banawali duplicate contexts','data','metadata',1,'local-only','hours','expert',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['F-0028'],['experiments/2026-10-12-seal-text-identity/REPORT.md',CONTEXT],
        'Which excavation contexts and dates can the held witnesses assign to the Banawali seals sharing texts?',
        'Same-site duplicates could be one holder’s seals, one institutional deposit or separated periods.',
        'Trace item identifiers to find units, stratum, phase and deposit status. Record unavailable fields in the data gap ledger.',
        'Finish the complete saved duplicate group. Accept contemporaneity only at the source-supported interval; leave context-free pairs unclassified.')
    add('Recheck Lothal attachment geometry','seals','verification',2,'local-only','hours','expert',['LOTHAL-TRACE-01','ARCH-02'],[],[READY,'experiments/2026-10-02-six-hour/lothal-physical-use/README.md'],
        'Can an independent reading of the held L206 views reproduce the contact observation used to reject a sole angular board-edge explanation for G01?',
        'The repeated inscription’s physical attachment scope should rest on observable features.',
        'Code curvature, texture, cord path, coverage and stamp identity with the inscription masked where practical. Preserve alternate readings and incomplete-object limits.',
        'Pass the narrow contrast only if independently joined images show the incompatible geometry. Stop if contact topology is not visible; report the unresolved feature rather than a category label.')
    add('Review complete Harappa short modules','tablets','verification',1,'local-only','hours','standard',['HARP-SHORT-01','ARCH-01'],[],[READY,'experiments/2026-10-02-six-hour/harappa-object-frame/README.md'],
        'Which stroke counts and face arrangements in H2218–H2239 can be independently confirmed from the held original views?',
        'The short-record cohort is excluded from the main restoration length filter but retains complete-object structure.',
        'Keep all objects and faces, source order, visible stroke height, candidate counts and engraver groups. Review unresolved pairs before testing numerical relations.',
        'Finish the complete 22-object source frame. Accept a count contrast only with two resolved physical faces; alternate transcriptions remain repeated observations of those objects.')
    add('Test W700 tier stability by period','tablets','analysis',2,'local-only','hours','standard',['NUMERAL-BEHAVIOUR-2026-10-12','ADMINISTRATIVE-BUNDLES-2026-10-11'],['C-0005','F-0024'],[C5,CONTEXT],
        'Are the two-, three- and four-tall-stroke proportions before W700 stable across source-supported Harappa periods?',
        'This is C-0005’s stated standard-tier prediction.',
        'Audit period labels and whole-object dependence first. Use the conjecture’s two-stage design, freeze exclusions, power and period comparison before confirmation.',
        'Use C-0005 P1’s rule and report power for detecting the prespecified shift. A strong period trend lowers credence; sparse labels or wide uncertainty leave stability undecided.')
    add('Test same-tier find-context clustering','tablets','analysis',2,'local-only','hours','standard',['ADMINISTRATIVE-BUNDLES-2026-10-11'],['C-0005'],[C5,CONTEXT],
        'Within a fixed descriptor class, do Harappa tablets of the same tier share find contexts more than tablets of different tiers?',
        'The comparison can distinguish issued series from arbitrary stroke assignments.',
        'Use primary-joined find units, retain secondary deposits and unknown contexts, and freeze the comparison on the discovery half under the conjecture design.',
        'Use C-0005 P2’s one-sided permutation p below 0.05. Stop if context variation is absent or one dependence component exhausts the population.')
    add('Test rare-animal site concentration','seals','analysis',2,'local-only','hours','standard',['SIGN-CONTEXT-SEALS-01','SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['C-0003','F-0029'],[C3],
        'Do rarer field animals concentrate at fewer sites than their counts and site totals predict, while unicorns follow site totals?',
        'This is the affiliation conjecture’s P1 and combined kill test.',
        'Use square seals with known animal at sites meeting the card’s sample threshold, source-audit motifs and follow the two-stage design. Freeze HHI and the permutation strata.',
        'Apply C-0003 P1’s 95th-percentile and central-95% rules. Failure of both parts activates its kill condition; insufficient rare-animal counts stop the shot as underpowered.')
    add('Test different-animal cross-site pairs','seals','analysis',2,'local-only','hours','standard',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12'],['C-0003','F-0029'],[C3],
        'Do identical texts on different non-unicorn animals cross sites more often than identical texts on the same animal?',
        'C-0003 P2 tests whether a legend transfers across affiliations.',
        'Keep exact and variant-merged text definitions separate, use the held object registry and freeze a pair-weighting rule on discovery before confirmation.',
        'Apply C-0003 P2’s one-sided permutation p below 0.05. Report every eligible pair and stop if there is no supported same-animal comparator.')
    add('Prepare prospective conjecture observation rules','methods','tooling',2,'none-needed','hours','starter',[],['C-0003','C-0004','C-0005'],[C3,C4,C5],
        'Can a contributor write reproducible eligibility and recording rules for the prospective predictions on the three existing conjecture cards?',
        'A future assemblage should be evaluated under rules recorded before its outcomes are inspected.',
        'Write a protocol in a new dated package defining publication cutoff, duplicate handling, complete faces, required fields and the existing pass rules. Leave the cards unchanged until maintainer review.',
        'The deliverable is a protocol and mock empty ledger, using synthetic fixtures only. Stop before acquiring or scoring new evidence; every ambiguity must have a prespecified resolution rule.')
    add('Recode sign families without catalogue order','images','verification',2,'local-only','days','expert',['SIGN-FAMILIES-2026-10-12'],['F-0010','F-0011'],[NEXT],
        'Does an independent human coding of shuffled glyph sheets retain the family prediction gain?',
        'Both original coders saw the Wells order, which already groups graphics.',
        'Prepare shuffled sheets without codes or counts, retain a keyed local crosswalk and specify adjudication before the human coding. Check low-agreement families and the twelve-stroke grid against held photographs.',
        'Freeze the grouping before rerunning the recorded prediction assay. Compare it with both random groups and contiguous-order cuts. Stop interpretation where the feature cannot be seen reliably.')
    add('Audit catalogue line-division locators','data','metadata',1,'local-only','hours','starter',['LINE-BREAKS-SEGMENTATION-2026-10-12'],['F-0018'],[NEXT,CONTEXT],
        'Which saved line divisions have source plate coordinates and reliable line-order evidence?',
        'A boundary training set needs independently inspectable layout labels.',
        'Review held multi-line faces, source captions and orientation; keep numeral-only lines, wrapped text and spatially separate groups distinguishable.',
        'Finish a fixed source block with all exclusions accounted for. Retain both line orders when unresolved and exclude them from a one-order gold set.')
    add('Train segmentation on observed divisions','structure','analysis',2,'local-only','hours','standard',['LINE-BREAKS-SEGMENTATION-2026-10-12','REHEARSAL-SEGMENTATION-2026-10-12'],['F-0018','F-0020'],[NEXT],
        'Does a segmenter trained on catalogue divisions improve boundary prediction on a reserved physical-family block?',
        'Unsupervised rehearsal gives limited average accuracy; recorded divisions provide positive boundary evidence.',
        'Use reviewed line layouts and spacing measurements already held. Keep positive boundaries distinct from positions without boundary labels and split complete object families.',
        'Freeze a held-out boundary-recall endpoint and any independently justified precision labels. Pass requires improvement over the saved segmenter with stated coverage; stop if only positive labels permit no claimed precision estimate.')
    add('Compare numerals in both directions','numerals','analysis',2,'local-only','hours','standard',['NUMERAL-BEHAVIOUR-2026-10-12'],['F-0024','F-0025'],[NEXT],
        'Does stroke-value fixity survive site and period stratification when both preceding and following signs are treated as items?',
        'Direction changes which combinations appear near-fixed.',
        'Retain short/tall stroke distinctions, multi-face objects, site and period uncertainty. Freeze strata and comparators before confirmation; preserve the original following-item endpoint.',
        'Report both directions under the same sample-size and unit controls. Stop strata with inadequate support; any interpretation must predict a new object relation beyond these conditional counts.')
    add('Check chronology transfer after context audit','archaeology','analysis',2,'local-only','days','expert',['CHRONOLOGY-REGION-01'],[],[ROAD,CONTEXT],
        'Can a source-joined dated cohort support a held-out sign-use comparison after genre, material and recovery-method controls?',
        'Existing period differences vary with label-source and mound composition.',
        'Use only audited dates and object-context joins. Freeze residuality, secondary deposits, grouping and a source/site holdout rule before examining its outcome.',
        'Pass requires the declared effect on a supported reserved cohort and sensitivity to dating uncertainty. Stop if date labels are confounded with source or manufacture beyond the available controls.')
    add('Separate manufacture from graphic variation','images','analysis',2,'local-only','days','expert',['ROOT-11','SIGN-FAMILIES-2026-10-12'],[],[ROAD,CONTEXT],
        'Do fine modifiers track a production group or an independently observed category across production groups?',
        'A recurring carved feature can arise from manufacture as well as the inscription’s function.',
        'Use held high-resolution views, tool marks, material and independently coded production groups. Keep the feature coder blind to the category comparison.',
        'Freeze the feature and held-out production-group prediction before scoring. Pass requires transfer beyond production baselines; stop any feature with inadequate observer agreement.')
    add('Test gap geometry on held damaged cases','images','analysis',2,'local-only','days','expert',['ROOT-08','ROOT-17'],['F-0005'],[ROAD,READY],
        'Can measured gap width and surviving traces improve missing-count prediction on a newly reserved block of held images?',
        'The statistical count estimator lost to constant one without physical geometry.',
        'Freeze source-only crop, scale, segmentation and physical span rules before independent count references are opened. Keep acquisition and count outcomes separate.',
        'Pass requires the declared improvement over a sampling-matched constant control on reference-withheld cases. Stop when gap boundaries are unbounded or a count cannot be independently resolved.')
    add('Independently reproduce a reference calibration','methods','verification',3,'none-needed','hours','starter',['NULL-08','NULL-05'],['F-0031','F-0032'],['papers/002-conditional-reference-laws/methods.md'],
        'Can a new contributor independently reproduce a selected exact or generated reference-law calculation from tracked inputs?',
        'Verification by someone other than the author can raise a submitted result to reproduced.',
        'Choose the bounded calculation from Paper 002’s methods, record environment and helper hashes, use a fresh endpoint and implement the statistic or finite enumeration independently where feasible.',
        'Match the recorded exact counts or declared stochastic replay under its seeds. Preserve discrepancies and investigate them without replacing the old result; report the independence and reused code.')
    add('Repair retained mixture search misses','methods','analysis',3,'none-needed','hours','standard',['CRYPTO-10','CRYPTO-11'],[],[ROAD,'papers/004-reference-model-selection/methods.md'],
        'Can a different optimizer close the retained mixture-map score gaps without changing the declared objective or supplied component count?',
        'Population identification and finite-sample search success are distinct measurements.',
        'Use tracked generated worlds or their lossless package, the exact truth scores and failed-map diagnostics. Freeze the optimizer and budget before a fresh generated comparison.',
        'Pass requires the declared search improvement on the frozen objective plus a fresh control grid. Stop if gains come only from tuning on the saved misses; retain tied objectives and wrong optima.')
    add('Audit completeness for a quantity inventory','data','metadata',1,'local-only','hours','expert',['REGIONNUM-01','KHI-04'],['F-0006'],[ROAD,READY],
        'Can a held physical inventory establish whether an associated count or pool is complete, with units and commodity scope?',
        'The numerical controls show that a partial pool called complete can accept wrong values.',
        'Choose one held source-defined inventory and trace membership, missing fragments, measurement uncertainty and publication selection. List the absent independent count through DATA.',
        'Pass requires source-supported completeness and an independently recorded quantity. Stop with a partial or unknown-completeness ledger when the publication cannot establish membership.')
    add('Specify a known-script seal-locality comparator','comparative','analysis',3,'local-only','hours','standard',['SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12','BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12'],['F-0026','F-0028'],[EST,'experiments/2026-10-12-seal-text-identity/REPORT.md'],
        'Can the known-script editions already held support an object-level duplicate-locality comparator with the same eligibility rules?',
        'Impression records and edited texts supply different object denominators.',
        'Audit object IDs, source groups, find sites, complete legends and aliases in the held comparison editions. Record acquisition gaps through DATA rather than filling them with text counts.',
        'The first endpoint is feasibility: every comparison record must join to an object and site. Freeze a matched test only if the object-level denominator and dependence graph are supported.')
    add('Design a head-direction seal comparison','language','analysis',3,'none-needed','hours','standard',['STRUCTURAL-TYPOLOGY-2026-10-12'],['F-0022','F-0023'],[NEXT,EST],
        'What matched seal-legend protocol would compare at least two head-initial and two head-final traditions at both sign and word level?',
        'The observed edge statistic changes sign with unit and genre.',
        'Write the protocol from the held rehearsal and typology records. Define object identity, genre, sampling, gold word units and required metadata; route any external acquisition gaps to DATA and the data contributor.',
        'Stop at the protocol and feasibility ledger. Do not rank Indus language candidates until the matched controls pass their predeclared discrimination test.')
    add('Reproduce one manuscript claim from tracked aggregates','methods','verification',2,'none-needed','hours','starter',['MARKOV-03'],['F-0002','F-0003'],['papers/001-artifact-aware-prediction/claim-evidence-map.md','papers/001-artifact-aware-prediction/methods.md'],
        'Can a contributor independently recover one Paper 001 headline comparison from its tracked aggregate outputs and recorded definitions?',
        'A short verification contribution can check the human entry page’s claims without requiring local corpus access.',
        'Choose one aggregate claim, record the input hashes and recompute the displayed quantity. If a paired replay needs local audits, document that boundary and use the aggregate endpoint only.',
        'Match the source’s displayed value and denominator. Stop after the selected claim and report exactly which inputs and calculations were independently inspected.')
    assert 30<=len(ROWS)<=45 and sum(r[6]=='starter' for r in ROWS)>=8
    for i,row in enumerate(ROWS,1):
        title,area,kind,priority,access,compute,difficulty,prior,related,sources,question,why,needs,decide=row
        identifier=f'Q-{i:04d}'; slug=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
        path=ROOT/f'knowledge/questions/{identifier}-{slug}.md';path.parent.mkdir(parents=True,exist_ok=True)
        fields=dict(id=identifier,title=title,status='open',area=area,kind=kind,priority=priority,data_access=access,
                    compute=compute,difficulty=difficulty,claimed_by='',claim_expires='',prior_attempts=prior,related=related,
                    sources=sources,authors=['Codex (GPT-6; API harness)'])
        front='\n'.join(f'{k}: {json.dumps(v,ensure_ascii=False)}' for k,v in fields.items())
        source_links='; '.join(f'[{p}]({os.path.relpath(ROOT/p,path.parent).replace(chr(92),"/")})' for p in sources)
        prior_links='; '.join(f'[{p}](../registry/attempts/{p}.json)' for p in prior)
        prior_text=(prior_links+'. Read their outcomes and `retry_when` before running this task.' if prior else 'No registered run is required for this protocol-writing task; inspect the linked predictions before proposing changes.')
        text=f'---\n{front}\n---\n\n# Question\n\n{question}\n\n# Why it matters\n\n{why}\n\n# What is needed\n\n{needs} Read [DATA.md](../DATA.md) for the gaps this task depends on.\n\nSources: {source_links}.\n\n# How to decide\n\n{decide}\n\n# Prior attempts\n\n{prior_text}\n'
        path.write_text(text,encoding='utf-8',newline='\n')
    print('Wrote',len(ROWS),'questions;',sum(r[6]=='starter' for r in ROWS),'starter tasks')


if __name__=='__main__':main()
