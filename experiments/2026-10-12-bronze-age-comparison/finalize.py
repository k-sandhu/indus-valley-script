"""Append the completed research record while preserving current shared entries."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
LOCAL=ROOT/'data/raw/2026-10-12-bronze-age-comparison/integration-v1'
LOCAL.mkdir(parents=True,exist_ok=False)
prefix='experiments/2026-10-12-bronze-age-comparison/'
entries=[
 {'id':'BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12','theme':'source-observed short-record comparison','status':'completed-exploratory-with-preserved-source-repairs',
  'question':'How do Sumerian, Akkadian, Egyptian and Mycenaean Greek short edited records compare with IVS under stated source units and allocation controls?',
  'outcome':'Primary institutional editions supply a fixed Ur III sample, Akkadian letter/account cohorts, source-linked Egyptian vessel texts and a site-stratified Linear B sample. IVS has 1593 complete distinct faces of length 3-12 and 7970 codes. All eleven testable position cohorts depart from within-record references after adjustment; their encoding and genre populations remain distinct. One tiny seal cohort lacks a statistic.',
  'challenge':'Edition units, damage, glyph readings, natural subdivisions and language/period labels differ. ORACC blank/ruling and seal markers, AES numeric glyph entities, missing IDs and LiBER normalized search-link certainty required repairs. The final Greek cohort is smaller. Related rows can connect into large components.',
  'remedy':'Preserved failed normalization, successive datasets, run-v1/sign-control-v1 and exact code snapshots. Corrected Greek display/query eligibility in new endpoints without replacement source selection. Every non-Greek numeric cohort outcome is unchanged. Separate arithmetic, analytic shuffle expectations, source byte checks and category replay accompany the manuscript.',
  'evidence':[prefix+p for p in ['MANUSCRIPT.md','REPORT.md','TABLES.md','SOURCES.md','observations.json','CLAIM-EVIDENCE.json','run-v2/structural-results.json','run-v2/verification.json','source-correction-comparison.json','RETROSPECTIVE.md']],
  'retry_when':'A source-reviewed physical-glyph correspondence, new independently grouped short complete record cohort, or independent Indus functional/quantity block changes the observation problem. Preserve current endpoints; do not select a language from unmatched structural scores.'},
 {'id':'BRONZE-AGE-KNOWN-CATEGORY-CONTROLS-2026-10-12','theme':'known-category calibration and observation uncertainty','status':'completed-source-tagged-held-out-controls-with-exploratory-sign-extension',
  'question':'Can anonymous identities, context and position predict source tags on held-out source groups, with or without supplied word boundaries?',
  'outcome':'Whole-word context/identity-only accuracy is 90.41/81.79% for Sumerian, 97.00/95.09% for Egyptian, 83.92/69.23% for Greek written-unit types and 50/50% for 50 Akkadian targets. The sign-boundary-concealed control retains positive and negative baseline comparisons and insufficient four-group complete Akkadian coverage. Greek uses SYLLABIC/LOGOGRAM/NUMBER, not a personal-name key.',
  'challenge':'Source word divisions and training tags are stronger observations than available for IVS. Rare categories, repeated identities and giant extension components constrain generalization. Word/sign length filters select different objects.',
  'remedy':'Training meanings are available but test meanings, readable identities and glosses are hidden from prediction. Physical/text/exact-sequence closure precedes folds. Report majority, position, identity, context, shuffled-label, balanced and unseen-ID outcomes. A separate Counter implementation replays 3320 decisions. The post-outcome sign amendment and source correction retain their original counterparts.',
  'evidence':[prefix+p for p in ['COHORT-SPEC.md','AMENDMENT-SIGN-CONTROL.md','run-v2/category-results.json','sign-control-v2/results.json','sign-control-v2/verification.json','category-replay-verification-v2.json','METHODS.md','NEXT-TESTS.md']],
  'retry_when':'The same source objects support a paired boundary-information assay; more complete Akkadian records, assessed Greek semantic tags, physical glyph identities or a new held-out functional context supplies a changed input. Do not treat supervised source-category prediction as recovered IVS meanings.'},
 {'id':'BRONZE-AGE-LEXICAL-PATTERN-AMBIGUITY-2026-10-12','theme':'lexical compatibility, dictionary size and shared-key constraints','status':'completed-restrictive-per-face-compatibility-construction',
  'question':'How selective are equality-pattern word matches when several known documentary spelling inventories receive the same per-face correspondence freedom?',
  'outcome':'1522 distinct IVS faces of length 3-8 have 47 equality patterns. Repeated 200-entry spelling samples give mean compatible fractions 92.02%, 97.13%, 96.93% and 91.16% for the Sumerian, Akkadian-document, Egyptian and Greek cohorts, generally with multiple candidates. Per-face correspondences do not form a shared key. A separate observed-inventory injection bound is necessary only and selects no historical language.',
  'challenge':'The one-face/one-word assumption, distinct script representations, mixed source languages, incomplete lexica and independently chosen maps limit interpretation. Sanskrit dictionary-letter windows have different units and premises.',
  'remedy':'Preserved natural lexicon counts, size-matched draws, subset intervals, ambiguity counts and exact cardinality constraints. Raw spellings/maps remain local. The manuscript keeps hypothetical mapping rules separate from source-observed records.',
  'evidence':[prefix+p for p in ['run-v2/lexical-ambiguity.json','COHORT-SPEC.md','METHODS.md','TABLES.md','CLAIM-EVIDENCE.json','NEXT-TESTS.md']],
  'retry_when':'A fixed shared mapping model, dated and matched reference units, verified word boundaries or independent phonetic/semantic anchors support a new withheld test. Additional flexible dictionary fits alone do not resolve this construction.'}
]

saved=[]
def guarded_write(relative,transform):
    file=ROOT/relative
    before=file.read_bytes();after=transform(before)
    target=LOCAL/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    if file.read_bytes()!=before:raise RuntimeError('Shared file changed during integration: '+relative)
    temporary=file.with_name(file.name+'.bronze-age-write-part')
    temporary.write_bytes(after)
    if file.read_bytes()!=before:raise RuntimeError('Shared file changed before replacement: '+relative)
    os.replace(temporary,file)
    saved.append({'path':relative,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest()})

def registry_transform(before):
    value=json.loads(before);old=value['experiments'][:];existing={x['id']:x for x in old}
    for entry in entries:
        if entry['id'] in existing:
            if entry!=existing[entry['id']]:raise RuntimeError('Registry ID already has different contents')
        else:value['experiments'].append(entry)
    assert value['experiments'][:len(old)]==old
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
guarded_write('knowledge/experiments/registry.json',registry_transform)

def append(relative,block):
    def change(before):
        text=before.decode('utf-8')
        if '2026-10-12-bronze-age-comparison' in text:return before
        newline='\r\n' if b'\r\n' in before else '\n'
        return (text.rstrip()+newline+newline+block.replace('\n',newline)+newline).encode('utf-8')
    guarded_write(relative,change)
append('README.md','## Four Bronze Age documentary comparisons\n\nThe [October 12 manuscript](experiments/2026-10-12-bronze-age-comparison/MANUSCRIPT.md) and [findings](experiments/2026-10-12-bronze-age-comparison/REPORT.md) compare source-observed Sumerian, Akkadian, Egyptian and Mycenaean Greek records with IVS. Known-category controls, preserved source repairs and per-face lexical ambiguity are linked to [exact tables](experiments/2026-10-12-bronze-age-comparison/TABLES.md). The work selects no historical Indus language.')
append('knowledge/INDEX.md','## Four Bronze Age records and known-category controls\n\nThe [October 12 comparison](../experiments/2026-10-12-bronze-age-comparison/README.md) supplies primary source frames, a [manuscript](../experiments/2026-10-12-bronze-age-comparison/MANUSCRIPT.md), [methods](../experiments/2026-10-12-bronze-age-comparison/METHODS.md) and [exact outcomes](../experiments/2026-10-12-bronze-age-comparison/TABLES.md). Complete edited objects and natural subdivisions retain different units. Known-category success partly follows repeated identities; equal-entry spelling inventories all match most IVS equality patterns under independently chosen per-face keys. Source repairs and every earlier endpoint remain preserved. [Retrospective](retrospectives/2026-10-12-bronze-age-comparison.md).')
append('knowledge/retrospectives/README.md','## 12 October: four Bronze Age documentary comparisons\n\n[Source acquisition, category controls and lexical ambiguity](2026-10-12-bronze-age-comparison.md) records the new Sumerian, Akkadian, Egyptian and Greek study, its source-format repairs, unchanged non-Greek successor outcomes and frozen next-data tests. [Detailed program retrospective](../../experiments/2026-10-12-bronze-age-comparison/RETROSPECTIVE.md).')
summary=ROOT/'knowledge/retrospectives/2026-10-12-bronze-age-comparison.md'
with summary.open('x',encoding='utf-8') as handle:
    handle.write('# Four Bronze Age documentary comparisons\n\nThe [program retrospective](../../experiments/2026-10-12-bronze-age-comparison/RETROSPECTIVE.md) records source selection, acquisition, format repairs, category recovery, source-markup correction and preservation. Read the [manuscript](../../experiments/2026-10-12-bronze-age-comparison/MANUSCRIPT.md), [methods](../../experiments/2026-10-12-bronze-age-comparison/METHODS.md) and [next tests](../../experiments/2026-10-12-bronze-age-comparison/NEXT-TESTS.md) before repeating this path.\n\nPrimary institutional editions changed the input problem from invented laws to source-observed records with annotation keys. The original word control, the post-outcome boundary-concealed control and the later Greek markup repair have separate endpoints. Dictionary-pattern compatibility remains ambiguous across all four source inventories. No historical language or IVS meaning was authenticated, and no CI/CD, recurring automation or publication action was added.\n')
record={'integrated_utc':datetime.now(timezone.utc).isoformat(),'new_registry_ids':[e['id'] for e in entries],
        'shared_files':saved,'previous_registry_entries_preserved':True,
        'scope':'Loaded latest navigation and registry; guarded byte comparison before each replacement. Unrelated working files left intact.'}
with (P/'integration-v1.json').open('x',encoding='utf-8') as handle:json.dump(record,handle,indent=2);handle.write('\n')
print(json.dumps({'new_registry_entries':len(entries),'navigation_files':len(saved),'preserved_existing_entries':True}))
