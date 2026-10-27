"""Reorganize navigation while retaining the original index's substantive blocks."""
import json
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
groups = json.loads((PACKAGE/'programmes.json').read_text(encoding='utf-8'))
for g in groups:
    if g['name'] == 'Contemporary civilisations':
        g['outcome'] = 'The comparison places the Mature Harappan civilisation beside 21 contemporary societies, retaining source-specific area, population and institution estimates.'

def main_report(name):
    d = ROOT/'experiments'/name
    order = ['REPORT-v2.md','REPORT.md','README.md','RETROSPECTIVE.md','COMMON.md']
    if name=='2026-10-13-data-round-1-verification': order=['README.md','REPORT.md']
    return next(d/n for n in order if (d/n).is_file())

def label(name):
    return name[11:].replace('-',' ')

def link(path, title, prefix='../'):
    return f'[{title}]({prefix}{path.relative_to(ROOT).as_posix()})'

def docs(g, prefix='../'):
    chunks=[]
    for name in g['packages']:
        d=ROOT/'experiments'/name
        parts=[link(main_report(name), label(name), prefix)]
        for n in ['REVIEW.md','VALIDATION.md','RETROSPECTIVE.md']:
            p=d/n
            if p.exists() and p!=main_report(name):parts.append(link(p,n.removesuffix('.md').lower(),prefix))
        # Keep checks embedded in reports discoverable when a package has no separate review.
        chunks.append(', '.join(parts))
    return '; '.join(chunks)+'.'

historical = [
('1–2 October','First investigation','archive/2026-10-01-investigation/README.md','The preserved corpus, source audits and prediction study establish the initial graphic and numerical results.'),
('2 October','Six-hour methods continuation','experiments/2026-10-02-six-hour/SESSION_LOG.md','Restoration, reference laws, mapping controls and physical-observation designs retain their measured outcomes and failed paths.'),
('2 October','Decipherment readiness','experiments/2026-10-02-decipherment-readiness/RETROSPECTIVE.md','The review separates held evidence from the independent physical observations needed for a restricted reading.'),
('2 October','Connections and publication priority','experiments/2026-10-02-connections-and-priority/README.md','Regional source frames and an independent precedent review qualify the numerical connections.'),
('2 October','Original source recovery','experiments/2026-10-02-source-recovery/README.md','Primary illustrations and early mass records expose disagreements in the Susa and other comparison sources.'),
('6–7 October','Fifteen-package research programme','experiments/2026-10-06-research-program/REPORT.md','Reviewed packages test restoration, evidence coverage, weights, seals and published recommendations.'),
('8–9 October','Bonta source review and exploratory extension','experiments/2026-10-08-bonta-extension/README.md','The source inventory and conditional map distinguish inherited proposals from new working assignments.'),
('11 October','Adversarial Bonta review and release','experiments/2026-10-11-bonta-adversarial/REPORT.md','Review narrows the interpretation to seven candidate semantic families and records source-sensitive changes.'),
('11 October','Grammar and whole-object functions','experiments/2026-10-11-two-approaches/REPORT.md','The frozen grammar comparison fails, while face-role controls qualify repeated tablet bundles.'),
('11 October','Settlement prospection','experiments/2026-10-11-settlement-prospection/README.md','A 72-record source register and 21 regions organize survey gaps without identifying a new site.'),
('11 October','Institutions and cultural memory','experiments/2026-10-11-early-indian-continuity/REPORT.md','Selective transmission and recombination remain source-qualified mechanisms with prospective tests.'),
('11 October','Societal persistence','experiments/2026-10-11-societal-persistence/REPORT.md','Finite models distinguish present service, replacement capacity and renewal under stated costs.'),
('12 October','Bronze Age documentary comparisons','experiments/2026-10-12-bronze-age-comparison/REPORT.md','Four readable traditions constrain method calibration while leaving the Indus language unselected.'),
('12 October','Published-claim tests','experiments/2026-10-12-published-claim-tests/README.md','Readability, rearranged keys and allograph tests establish controls for future phonetic proposals.'),
('12 October','Semantic-map calibration','experiments/2026-10-12-anchor-calibration/REPORT.md','Most fitted lexical and family patterns recur under rearrangements of the same values.'),
('12 October','Round seals','experiments/2026-10-12-round-seal-tradition/REPORT.md','Catalogue joins and two-reader image checks qualify unusual orders on Gulf-type seals.'),
('12 October','Structure before meaning','experiments/2026-10-12-structure-first/REPORT.md','Six steps measure sign families, image pairing, line breaks, strokes and structural comparison controls.'),
('12 October','Seal-text identity','experiments/2026-10-12-seal-text-identity/REPORT.md','Recurring short texts span sites, long texts remain distinct, and matching sealings often occur away from matching seals.'),
('12–13 October','First conjecture shots','experiments/2026-10-12-conjecture-shots/README.md','The 118-sign gloss map fails its test, while a size result depends on three large seals ending in 820.')]

original=(PACKAGE/'baseline/INDEX.md').read_text(encoding='utf-8-sig')
if original.startswith('````markdown\n'):original=original[len('````markdown\n'):].removesuffix('\n````\n')
sections={}
for block in re.split(r'(?m)(?=^## )',original):
    if block.startswith('## '):sections[block.splitlines()[0][3:]]=block.rstrip()

intro = '''# Knowledge index

Use this index to find a research programme by date and follow its results to reports, reviews and exact outputs. The [findings guide](findings/README.md) groups individual results by question; the dated summaries below preserve the longer research record. Attempts and findings use the [status vocabulary](registry/VOCABULARY.md).

We distinguish four levels of claim: observed graphics, statistical structure, possible function, and phonetic or lexical interpretation, that is, sounds and words. We have useful evidence for the first two. No authenticated phonetic or lexical interpretation has been established.

## Start here

- [Findings](findings/README.md): themed results, populations and exact evidence.
- [Working model](WORKING-MODEL.md): the integrated interpretation and links to every conjecture.
- [Conjectures](conjectures/README.md): claims, credences, predictions and kill conditions.
- [Open questions](questions/): the task cards and their prior attempts.
- [Data coverage](DATA.md): held sources, metadata gaps and acquisition priorities.
- [Repository map](MAP.md): the generated catalogue of cards and entry documents.
- [Experiment registry](experiments/registry.json): outcomes, challenges, remedies and retry conditions.
- [Retrospectives](retrospectives/README.md): approaches, repairs and unresolved problems.
- [Timeline](TIMELINE.md): the dated research record.

Read [LOCAL_STORAGE.md](../LOCAL_STORAGE.md) before acquiring or restoring local inputs.

## Programmes by date

Dates are in October 2026. Related passes share one row, with their separate reports linked in the programme name and the summaries below.

| Date | Programme | Outcome |
|---|---|---|
'''
for date,name,path,outcome in historical:
    # The conjecture package has an integrated report rather than a root README in some checkouts.
    p=ROOT/path
    if not p.exists() and name=='First conjecture shots': p=ROOT/'experiments/2026-10-12-conjecture-shots/REPORT.md'
    intro += f'| {date} | {link(p,name)} | {outcome} |\n'
for g in groups:
    paths=[main_report(n) for n in g['packages']]
    first=ROOT/'experiments/2026-10-13-data-round-1-verification/README.md' if g['packages'][0]=='2026-10-13-data-round-1' else paths[0]
    names=link(first,g['name'])
    if first!=paths[0]:names+=', '+link(paths[0],'shared instructions')
    names+=''.join(', '+link(p,label(n)) for n,p in zip(g['packages'][1:],paths[1:]))
    intro+=f"| {int(g['date'][-2:])} October | {names} | {g['outcome']} |\n"
intro+='| 27 October | [Findings organization](../experiments/2026-10-27-findings-organization/REPORT.md) | Nine new cards and ten themes make all 47 findings and 22 conjectures reachable through the navigation pages. |\n'

text=intro+'\n## Programme summaries\n\n### 1–10 October: evidence, methods and manuscripts\n\n'
# Preserve every original paragraph and link within these blocks.
early=sections['Manuscripts and reproducibility'].split('\n',1)[1].lstrip()
text+=early+'\n\n'
for title in ['October 11 review and publication','Two approaches beyond the Bonta work','Excavation and hidden settlement landscapes','Early Indian institutions and cultural memory','Societal persistence and renewal, October 11','Four Bronze Age records and known-category controls','Published-claim tests, 12 October','Calibration of the semantic assignments, 12 October','Round seals, 12 October','Structure before meaning, 12 October','Seal-text identity and the 12 October synthesis']:
    text+=re.sub(r'^## ', '### ',sections[title],count=1)+'\n\n'
# Preserve the later synopsis that was previously above the narrative.
synopsis=re.search(r'(?s)(The \[fish study\].*?versioned results\.)',original)
for day in sorted({g['date'] for g in groups}):
    text+=f'### {int(day[-2:])} October 2026\n\n'
    if day=='2026-10-20' and synopsis:text+=synopsis[1]+'\n\n'
    for g in [x for x in groups if x['date']==day]:
        text+=g['outcome']+' '+docs(g)+'\n\n'
    if day=='2026-10-26':
        d=ROOT/'experiments/2026-10-26-indus-living-atlas'
        text+='The atlas keeps separate records for '+', '.join(link(d/n,title) for n,title in [('mapping/REPORT.md','mapping'),('reconstruction/REPORT.md','seven reconstructions'),('continuity/REPORT.md','changing markers'),('living-towns/REPORT.md','living towns')])+'.\n\n'
text+='### 27 October 2026: findings organization\n\nThis editorial pass groups all 47 findings into ten themes, adds nine evidence-linked cards and makes all 22 conjecture cards reachable from the working model. [Report](../experiments/2026-10-27-findings-organization/REPORT.md), [retrospective](../experiments/2026-10-27-findings-organization/RETROSPECTIVE.md).\n\n'
for title in ['Research memory','New directions','Sources and reuse','Status vocabulary']:
    text+=sections[title]+'\n\n'
text+='Source review (`source-review`) records an audit, survey, census or literature review. Record (`record`) preserves coordination, release or research history. Contributor verification tiers are separate from these classes; see the [controlled vocabularies](registry/VOCABULARY.md).\n'
(ROOT/'knowledge/INDEX.md').write_text(text,encoding='utf-8')

# Preserve the historical timeline as a complete block below new, newest-first entries.
timeline=(PACKAGE/'baseline/TIMELINE.md').read_text(encoding='utf-8-sig')
if timeline.startswith('````markdown\n'):timeline=timeline[len('````markdown\n'):].removesuffix('\n````\n')
pos=timeline.index('# 2026-10-12')
front='# Research timeline\n\nThe dated entries run newest first. Entries from 13–27 October 2026 extend the preserved research narrative below; its Start here table remains the navigation snapshot of 12 October. The [index](INDEX.md) supplies an ascending programme table, and the [findings guide](findings/README.md) groups individual results.\n\n'
for day in sorted({g['date'] for g in groups},reverse=True):
    front+='# '+day+'\n\n'
    for g in [x for x in groups if x['date']==day]:front+='## '+g['name']+'\n\n'+g['outcome']+' '+docs(g)+'\n\n'
    if day=='2026-10-27':front+='## Findings organization\n\nThe [editorial report](../experiments/2026-10-27-findings-organization/REPORT.md) records nine new cards and ten themes covering all 47 findings, with the [retrospective](../experiments/2026-10-27-findings-organization/RETROSPECTIVE.md) and saved navigation checks.\n\n'
(ROOT/'knowledge/TIMELINE.md').write_text(front+timeline[pos:],encoding='utf-8')

retro=(PACKAGE/'baseline/retrospectives/README.md').read_text(encoding='utf-8-sig')
if retro.startswith('````markdown\n'):retro=retro[len('````markdown\n'):].removesuffix('\n````\n')
retro=retro.rstrip()+'\n'
for day in sorted({g['date'] for g in groups}):
    retro+=f'\n## {int(day[-2:])} October 2026: programme records\n\n'
    for g in [x for x in groups if x['date']==day]:
        links=[]
        for name in g['packages']:
            d=ROOT/'experiments'/name
            p=d/'RETROSPECTIVE.md'
            links.append(link(p if p.exists() else main_report(name),label(name)+(' (report; no separate retrospective)' if not p.exists() else ''),'../../'))
        retro+=g['outcome']+' '+ '; '.join(links)+'.\n\n'
    if day=='2026-10-26':
        d=ROOT/'experiments/2026-10-26-indus-living-atlas'
        retro+='The atlas also keeps module accounts for '+', '.join(link(d/n,title,'../../') for n,title in [('continuity/RETROSPECTIVE.md','continuity'),('living-towns/RETROSPECTIVE.md','living towns'),('reconstruction/RETROSPECTIVE.md','reconstruction')])+'.\n\n'
retro+='The [findings-organization retrospective](../../experiments/2026-10-27-findings-organization/RETROSPECTIVE.md) records the inventory, card selection, navigation structure and preservation checks for this editorial pass.\n'
(ROOT/'knowledge/retrospectives/README.md').write_text(retro,encoding='utf-8')

source=json.loads((PACKAGE/'source-files.json').read_text(encoding='utf-8'))
covered={n for g in groups for n in g['packages']}
expected={Path(p['package']).name for p in source['packages']}
assert covered==expected,(expected-covered,covered-expected)
(PACKAGE/'programme-coverage.json').write_text(json.dumps({'status':'pass','programmes':len(groups),'packages':len(covered),'uncovered':sorted(expected-covered)},indent=2)+'\n',encoding='utf-8')
print(len(groups),'programme groups cover',len(covered),'dated packages')
