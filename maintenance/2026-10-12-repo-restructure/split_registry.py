"""One-time, reviewed classification of the preserved 165-entry working registry."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/'data/raw/2026-10-12-repo-restructure'
RUN = ROOT/'experiments/2026-10-12-repo-restructure'

# Each row was chosen after reading the entry's status, question and outcome.
# Indices refer to the saved working-tree registry, never to a regenerated file.
DECISIONS = '''
0 exploratory meaning Working meanings and post-outcome lexical refinements.
1 source-review corpus Pinned corpus and observation-field audit.
2 verified-computation structure Grouped nested structural score and integrity checks.
3 superseded structure Alias loss invalidates the old restoration split.
4 verified-computation structure Known-slot recovery with checked outcomes.
5 exploratory structure Selected-site sensitivity rather than a new frozen endpoint.
6 verified-computation corpus Checked candidate-event calculation on shared-source annotations.
7 exploratory corpus Source exclusions selected after outcomes.
8 failed structure Matched gap-count estimator loses to constant one.
9 exploratory archaeology Broad metadata diagnostics lack an external response.
10 exploratory tablets Paired-face relationships audited without an external anchor.
11 exploratory structure Highlighted pair remains inconclusive after weighting checks.
12 synthetic methods Constructed office-routing counterexample.
13 verified-computation numerals Exact conditional equality enumeration.
14 synthetic numerals Explicit rescaled parameter counterexample.
15 source-review images Uncertainty-preserving chart transcription resource.
16 exploratory images Printed-row development pilot.
17 frozen-evaluation images Primary withheld-row endpoint stayed frozen and failed whole-row recovery.
18 exploratory images Geometric repair followed reference inspection.
19 source-review data Primary identity joins and unresolved historical aliases.
20 record methods Historical report and evidence-preservation checks.
21 synthetic methods Exact relabelling demonstration on invented symbols.
22 exploratory structure Post-pilot frequency-adjusted max sensitivity.
23 exploratory structure Larger-budget post-pilot max sensitivity.
24 exploratory structure Unique-text post-pilot max sensitivity.
25 exploratory structure Class-aware collapsed-corpus discovery and transfer.
26 exploratory structure Class-aware pilot discovery and transfer.
27 exploratory structure Class-aware primary discovery and transfer.
28 exploratory structure Class-aware unique-text discovery and transfer.
29 exploratory structure Class-aware alias-preserving sensitivity.
30 exploratory structure Collapsed-corpus model sensitivity from the result index.
31 verified-computation images Audit of the frozen fresh-20 predictions, rather than new acquisition.
32 exploratory images Source geometry changed after reference outcomes.
33 verified-computation images Audit of preserved pilot observations.
34 failed structure Matched gap-law sensitivity preserves the losing estimator.
35 exploratory structure Full-procedure primary null refinement after audit.
36 exploratory structure Larger-budget primary null refinement after audit.
37 exploratory structure Full-procedure unique-text null refinement after audit.
38 exploratory structure Uniqueness-conditioned nested reference added after pilot.
39 exploratory structure Collapsed transfer reference reruns discovery after audit.
40 exploratory structure Primary transfer reference reruns discovery after audit.
41 exploratory structure Unique transfer reference reruns discovery after audit.
42 exploratory structure Uniqueness-conditioned transfer refinement.
43 exploratory structure Collapsed nested selection and site-transfer sensitivity.
44 exploratory structure Short-text nested selection sensitivity.
45 exploratory structure Short-text alias-preserving nested sensitivity.
46 exploratory structure Nested pilot model selection.
47 exploratory structure Primary nested selection and site-transfer sensitivity.
48 exploratory structure Reversed-order nested sensitivity.
49 exploratory structure Unique-text nested selection sensitivity.
50 exploratory structure Alias-preserving unique-text nested sensitivity.
51 verified-computation numerals Exact numerical-equality audit.
52 exploratory structure Original method pilot endpoint.
53 exploratory structure Raw-corpus method sensitivity endpoint.
54 exploratory structure Extended latent-template robustness on observational strings.
55 exploratory structure Primary latent-template robustness on observational strings.
56 exploratory seals Metadata-conditioned motif null refinement after audit.
57 exploratory seals Motif-conditioned nested selection sensitivity.
58 exploratory seals Motif template robustness endpoint.
59 synthetic methods Workflow templates evaluated on constructed control records.
60 synthetic methods Generated reference and anchor recovery grid.
61 verified-computation structure Checked Markov outcomes on preserved known-slot queries.
62 exploratory structure Mechanism interventions selected after the comparator.
63 source-review data Source-cohort and metadata availability audit.
64 synthetic methods Generated integrated-reference uncertainty grid.
65 synthetic numerals Invented assemblies separate ratios and scale.
66 synthetic methods Generated measurement-selection stress grid.
67 source-review tablets Harappa primary object and context frame.
68 source-review seals Lothal table and population-coverage audit.
69 synthetic methods Generated identity-audit control and exact probability bound.
70 synthetic numerals Primary generated acquisition endpoint; later overlap policy is separately post-outcome.
71 source-review archaeology Tell Jokha source and report-locator recovery.
72 synthetic methods Copied-source and coupled-error mapping simulation.
73 verified-computation tablets Conditional arrangement enumeration on source-linked pairs.
74 verified-computation comparative Published khipu alignment is primary; generated controls are secondary.
75 synthetic images Curved-contact forward model with invented geometry.
76 synthetic methods Generated graph-mapping grid and exact optima.
77 verified-computation comparative Exact source-controlled partition enumeration.
78 verified-computation structure Independently checked second-order outcomes on saved masks.
79 exploratory structure Loss-selected comparison followed the second-order outcome.
80 synthetic numerals Generated maximum-consensus worlds with wrong memberships.
81 synthetic methods Fresh generated slot-versus-graph comparison after earlier outcomes.
82 source-review archaeology Kanmer specimen frame is primary; handling test remains prospective.
83 synthetic methods Exact constructed binary table space.
84 synthetic methods Exact literal-copy process control.
85 synthetic methods Constructed unequal-copy margin sampler.
86 synthetic methods Constructed deduplication support law.
87 synthetic methods Generated paired-error calibration populations.
88 synthetic methods Constructed undefined-fit witness and exact extensions.
89 synthetic methods Known-channel generated frequency-recovery control.
90 synthetic methods Generated reference-only mapping selector grid.
91 synthetic methods Known independent, unique and copy calibration populations.
92 verified-computation methods Conditional component-bound proof and saved allocation audit.
93 synthetic numerals Generated complete-pool conservation control.
94 source-review archaeology Kanmer bibliography and physical-volume source amendment.
95 exploratory numerals Acquisition policies evaluated on reused wrong-decoder worlds.
96 synthetic methods Fresh generated overlapping-form stress grid.
97 synthetic methods Generated shared-quality calibration control.
98 synthetic methods Fresh generated agreement diagnostic and exact tails.
99 failed structure All folds reject extra second-order shrinkage in favor of first order.
100 synthetic methods Frozen generated common-length mixture comparison.
101 verified-computation methods Exact rational population rank certificates.
102 source-review corpus Readiness audit of existing observations and input requirements.
103 source-review methods Primary precedent and publication-priority review.
104 source-review numerals Marked-weight census and source-linked compatibility audit.
105 source-review comparative Pinned South Indian web/print source comparison.
106 verified-computation tablets Source-linked module counts and object-pair enumeration.
107 exploratory seals Bounded source-informed contact-image interpretation.
108 source-review archaeology Original Gonur and Altyn Depe figure recovery.
109 source-review numerals Historical and modern mass/mark discrepancies.
110 source-review comparative Primary numeral-to-referent source joins.
111 source-review data Registered views and archive-target recovery.
112 source-review data Dataset landscape and local coverage audit.
113 exploratory structure Modern models reuse the previously measured restoration masks.
114 superseded data Site census replaced by regional batches.
115 source-review data Pakistan and Afghanistan bounded source census.
116 source-review data Gujarat and neighboring-region bounded source census.
117 source-review data North India bounded source census.
118 source-review data Foreign-site bounded source census.
119 source-review data Museum catalogue and corpus-join audit.
120 source-review data Reviewed census synthesis records source coverage and missingness.
121 source-review methods Publication byproduct inventory and precedent assessment.
122 frozen-evaluation archaeology Primary chronology endpoint frozen; later amendments remain exploratory.
123 frozen-evaluation seals Primary sign/context endpoints frozen; amended area laws remain exploratory.
124 source-review comparative Dated source inventory; transmission tests are proposed.
125 source-review methods Attributed recommendation survey.
126 exploratory numerals Reviewed metrology refinements preserve the original endpoint.
127 exploratory comparative Small shape-descriptor pilot and reviewer correction.
128 record methods Coordination record for fifteen work packages.
129 exploratory data Object-ledger pilot and amended selections.
130 failed images Four frozen digitization release criteria fail; proposals quarantined.
131 failed images Primary reader screen failed; second pilot does not replace that screen.
132 source-review images Chart-reference source audit and corrected numeric record.
133 record data Private release-preview packaging awaits owner decisions.
134 source-review meaning Lecture and manuscript first-pass source review.
135 source-review images Public-image and literature-access audit.
136 exploratory meaning Adversarial review of post-outcome semantic candidates.
137 record data Public-release preservation and distribution record.
138 exploratory structure Standalone grammar failure with post-outcome class-mixture repair.
139 exploratory tablets Conditional bundle structure with post-outcome face-role control.
140 exploratory meaning Integration of exploratory grammar and carrier-function proposals.
141 exploratory archaeology Reviewed settlement synthesis; no fieldwork endpoint.
142 exploratory comparative Selective-survival source synthesis and prospective historical tests.
143 source-review comparative Documentary audit is primary; invented erasure construction is secondary.
144 exploratory comparative Integrated historical synthesis with invented retention controls.
145 source-review comparative Purposive primary theoretical literature survey.
146 synthetic methods Exact invented renewal and shared-repair worlds.
147 source-review archaeology Source-qualified Harappan service/renewal application.
148 exploratory comparative Conditional theory integrated with prospective empirical tests.
149 exploratory comparative Documentary comparison with preserved source repairs.
150 frozen-evaluation comparative Primary source-tagged held-out control; sign extension remains exploratory.
151 exploratory language Per-face lexical compatibility construction permits independent correspondences.
152 frozen-evaluation language Primary readability decision rules frozen; review corrections preserved.
153 frozen-evaluation language Primary key-likelihood decision rules frozen; exploratory fits remain separate.
154 synthetic language Exploratory key-calibration power on generated Indus-shaped corpora.
155 frozen-evaluation structure Primary foreign-sequence tests frozen; subgroup checks exploratory.
156 frozen-evaluation structure Primary substitution tests frozen; ordering diagnostics post-outcome.
157 frozen-evaluation structure Six primary steps frozen; amendments and exploratory checks documented.
158 frozen-evaluation structure Primary family/modifier prediction endpoint frozen; contiguous-cut checks post-outcome.
159 frozen-evaluation tablets Primary image/text endpoint frozen; corrected copper population retained.
160 frozen-evaluation structure Primary line-division and alternation endpoints frozen with amendments.
161 frozen-evaluation numerals Primary numeral/item endpoint frozen; directional sensitivities post-outcome.
162 frozen-evaluation methods Readable-corpus segmentation rehearsal frozen.
163 frozen-evaluation language Descriptive typology rule amended before computation; all languages tied.
164 frozen-evaluation seals Primary duplicate-locality test frozen; review site breakdown exploratory.
'''


def main():
    registry = json.loads((RAW/'registry-before.json').read_text(encoding='utf-8'))
    entries = registry['experiments']
    decisions = {}
    for line in DECISIONS.strip().splitlines():
        index, status, area, reason = line.split(' ', 3)
        decisions[int(index)] = (status, area, reason)
    assert len(entries) == len(decisions) == 165
    base = ROOT/'knowledge/registry'
    (base/'attempts').mkdir(parents=True, exist_ok=True)
    metadata = {k: v for k, v in registry.items() if k != 'experiments'}
    (base/'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    grouped = {}
    rows = []
    for i, original in enumerate(entries):
        status, area, reason = decisions[i]
        augmented = {**original, 'status_class': status, 'area': area, 'registry_order': i}
        path = base/'attempts'/f"{original['id']}.json"
        if path.exists():
            assert json.loads(path.read_text(encoding='utf-8')) == augmented, 'Existing attempt differs'
        else:
            path.write_text(json.dumps(augmented, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        grouped.setdefault(original['status'], []).append((original['id'], status, area, reason))
        rows.append(dict(id=original['id'], registry_order=i, original_status=original['status'],
                         status_class=status, area=area, reason=reason))
    lines = ['# Original statuses and their classifications', '',
             'Classification uses each entry’s question, status and outcome. The original fields remain unchanged.',
             'For mixed studies the reason identifies the primary endpoint; later checks retain their original description.',
             f'The saved working registry has {len(entries)} entries and {len(grouped)} distinct status strings.', '',
             'The area names describe the primary subject. Status class describes the primary endpoint, including its observation or simulation basis.', '']
    for original_status, group in sorted(grouped.items()):
        lines += ['## `'+original_status+'`', '', '| Entry | Status class | Area | Reason |', '|---|---|---|---|']
        for identifier, status, area, reason in group:
            lines.append(f'| [{identifier}](attempts/{identifier}.json) | {status} | {area} | {reason} |')
        lines.append('')
    (base/'STATUS-MAPPING.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (RUN/'classification-decisions.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    print('Split and classified', len(entries), 'entries; original SHA-256', hashlib.sha256((RAW/'registry-before.json').read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
