"""Register the second-coding comparison before computing its endpoints."""
from pathlib import Path
import shutil
from pdf_followup import ROOT, OWN, RAW, read, write, sha

AMENDMENT='''

## Independent second coding amendment, 9 October 2026

The coordinator supplied coder2-merged.json for all 96 targets, assembled unchanged from two fresh Claude Sonnet 5.5 sessions coding separate halves. Their returns and notes stay preserved locally. The first frozen 96-target mapping and all earlier outcomes remain unchanged. New outputs use two-coder-2026-10-09-v1/ in the owned and local raw trees. This registration precedes agreement and sensitivity calculations. These are two AI coding rounds without specialist review; the second round has two nonoverlapping reader assignments.

| ID | Statistic/data | Comparison or null | Decision and negative result |
|---|---|---|---|
| S2-A | Match the 96 IDs in template order. Normalize Wells W prefixes and chart identities. In Mayig, Wells and Helsinki-cell domains count exact singleton matches, equal nonempty candidate sets, overlap (including exact matches), disjoint nonempty sets and missing sets. Compute Cohen's kappa only on paired singleton rows with at least two represented labels and a nonzero chance denominator. Split by each coder's confidence, joint confidence and target type (65 Table drawings, 17 caption forms, 14 field/anchor targets). | Chance agreement for kappa uses the paired singleton marginals. Candidate-overlap counts are descriptive; no kappa is defined for ambiguous sets. Helsinki identity is cell_id, with code/rank payload consistency checked separately. | List every nonidentical candidate set or component sequence with both codings and a source-image note. Missing first-coder mappings are separate from disjoint nonempty sets. No agreement cutoff establishes correctness. |
| S2-R | Check the Mayig-to-chart class relation by joining direct Parpola codes to chart-reference-v2.1.json. Tabulate Mayig number minus printed rank, exceptions and code 369 membership. Check returned class/code metadata and part hashes. | Exact comparison with local pinned reference data; class means printed chart rank. | Report supported ranges and exceptions; never replace explicit code/cell joins with a numeric offset rule. Preserve original instructions and add a clarification with a new filename. |
| S2-M | Freeze three operational mappings: the first mapping, the normalized second return, and agreed-only. Agreed-only retains targets with nonempty Mayig-set intersection and uses that intersection; Wells/cell intersections are retained. Drop other targets, including empty/empty compounds, while reporting component agreement separately. | Fixed source sign IDs, source assignments and reference pins. Candidate ambiguity is retained, with no choice based on outcomes. | A dropped field target becomes unavailable rather than acquiring a new identity. No disputed target is adjudicated. |
| S2-F | Rerun canonical fields and fish units on the fixed 2469-object, 10835-token population under each mapping. Source targets are basic fish B031; fish variants B070-B073; compound fish B074/B075; ovals B066-B069; MA B006 plus TRA B039; short junctures B079/B077 and bent pair B078; terminals B055/B056. Repetition and span rules stay as in P-F. Use direct Wells sets and RTL component sequences; a code with incompatible categories is indeterminate. A source-omitted target cannot label a corpus sign. | Within-text shuffles, 1999 draws, seed 20261009, preserving token counts and lengths; report observed clean count and fish adjacency, null mean/range and add-one tail. Also rerun the 100 clear Mayig lines using direct Wells sets only when grammar categories agree. | Report all three clean/conflict/indeterminate populations. Clustering survives only if each mapping's tail is <= .05 and its observed count exceeds its shuffle mean. Canonical conflict counts never certify the full wider grammar. The first mapping must reproduce the earlier endpoint where its operational code recipe is unchanged. |
| S2-L | Rerun full and explicit-caption lexical panels, clear-origin subsets and any source-qualified held-out subset. Reuse the frozen 640-occurrence selection, Table variants, dictionary pin, normalization and provenance classifications. First/second reference codings leave manuscript glyph IDs and proposed value bundles fixed: these source-reading lexical scores do not depend on an external graphic class. Agreed-only removes occurrences containing any dropped target; it keeps the manuscript's assignments for the remainder. Report coverage and affected types. | Same bundle permutations as P-L: exhaustive up to 40320, otherwise 1999 seeded draws; exact primary, normalized secondary. Keep one-sign counts separate from deduplicated multi-role scores. Held-out membership needs an explicit source assertion, as before. | State when an unchanged result follows from this dependency structure. A tail <= .05 measures conditional fit; a change in the clear-origin conclusion must be listed for later adjudication. The agreed-only restriction is a source-coverage sensitivity, rather than a new meaning assignment. |
| S2-J | Recount explicit CISI reading joins for all 859 source attempt rows under each mapping; separately count fully/partially reference-mapped figures and their joined objects. Corpus object identity and join aliases remain fixed independently of glyph mapping. | Fixed manuscript aliases and pinned Lipi export; no same-number ICIT joins. No new statistical null. | Alias-join counts should be identical under all three; mapping coverage can change. Agreement filtering does not erase an identified object. Source-qualified joins stay flagged. |

Record every affected target, output and ledger test link. Conclusions that survive all mappings can lose the single-coder qualifier, with the two-AI-coder and specialist-review limits kept beside them. Confidence has no measured calibration. New source/score rows and predictions remain raw-only. Registered inputs, operational mapping hashes and code hashes precede reruns; fresh output paths refuse overwrites.
'''

if __name__=='__main__':
    out=OWN/'two-coder-2026-10-09-v1';raw=RAW/'two-coder-2026-10-09-v1'
    if out.exists() or raw.exists():raise SystemExit('Registration already exists')
    history=OWN/'history/2026-10-09-before-second-coder';history.mkdir()
    for name in ['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','sources.json','registry-entry.json',
                 'claims.jsonl','claims.md','ledger-coverage.json','COMPLETION.md','FILES.json']:
        if (OWN/name).exists():shutil.copyfile(OWN/name,history/name)
    files=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for directory in [OWN,RAW]
           for p in sorted(directory.rglob('*')) if p.is_file() and not p.is_relative_to(history) and '__pycache__' not in p.parts]
    write(history/'baseline-files.json',files)
    with (OWN/'PROTOCOL.md').open('a',encoding='utf-8') as f:f.write(AMENDMENT)
    out.mkdir();raw.mkdir();shutil.copyfile(OWN/'PROTOCOL.md',out/'PROTOCOL-registered.md')
    write(out/'registration.json',{'date':'2026-10-09','protocol_sha256':sha(out/'PROTOCOL-registered.md'),
        'first_mapping_sha256':sha(OWN/'pdf-2026-10-09-v1/mapping-v2-frozen.json'),
        'second_return_sha256':sha(RAW/'second-coder-v1/returns/coder2-merged.json'),
        'protected_baseline_files':len(files)})
    print('Registered agreement and sensitivities; prior state preserved')
