"""Dated, bounded corrections to the existing 59-row coding, 7 October 2026.

The initial source coding remains in curation.py. This layer records the second
review's dispositions, exact anchors, comparisons and project ranking explicitly.
It acquires no sources and changes no historical or reviewer witness.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = 'data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07/'

# These excerpts were read in the named local extracts or original images.
# Page numbers select PDF pages, not printed pagination; row locators retain both.
ANCHORS = {
 'F01': ('caption-anchors-2026-10-07.json', 'F01', 'with different expertise'),
 'F02': ('caption-anchors-2026-10-07.json', 'F02', 'the entire corpus was treated'),
 'F03': ('caption-anchors-2026-10-07.json', 'F03', 'based on the context.'),
 'F04': ('caption-anchors-2026-10-07.json', 'F04', 'position of the signs'),
 'F05': ('wells_2015_sample.pages.json', 12, 'regional differences in text structure'),
 'F06': ('wells_2015_sample.pages.json', 12, 'without chronological control'),
 'F07': ('wells_2015_sample.pages.json', 13, 'international and interdisciplinary cooperation'),
 'F08': ('wells_2015_sample.pages.json', 14, 'This work falls to linguists.'),
 'F09': ('iitgn_2023_abstracts.pages.json', 45, 'accessible to scholars worldwide'),
 'F10': ('iitgn_2023_abstracts.pages.json', 45, 'one homogeneous set'),
 'F11': ('kenoyer2020_origin.pages.json', 7, 'conflation needs to be avoided'),
 'F12': ('kenoyer2020_origin.pages.json', 14, 'excavations of Early Harappan sites'),
 'F13': ('kenoyer2020_origin.pages.json', 14, 'More detailed recording and quantification'),
 'F14': ('kenoyer2020_origin.pages.json', 15, 'continued collaborations'),
 'F15': ('kenoyer2006_pdf8.png', 'visual', 'sorting them out chronologically'),
 'F16': ('rao_2009_markov.pages.json', 6, 'all known texts'),
 'F17': ('rao_2009_markov.pages.json', 6, 'site-by-site analysis'),
 'F18': ('rao_2009_markov.pages.json', 6, 'infer a grammar'),
 'F19': ('yadav_2013_site_type.pages.json', 32, 'potential sources of fluctuations.'),
 'F20': ('yadav_2013_site_type.pages.json', 32, 'stylistic variations of'),
 'F21': ('research/literature/sources/rmrl/mahadevan_2010_context/page_06.png', 'visual', 'ascertain the language'),
 'F22': ('airavati_2008.pages.json', 127, 'their iconic meaning.'),
 'F23': ('farmer_sproat_witzel_2004_author.pages.json', 19, 'critical to future Indus studies'),
 'F24': ('farmer_sproat_witzel_2004_author.pages.json', 25, 'second-hand seals in the Near East'),
 'F25': ('farmer_sproat_witzel_2004_author.pages.json', 26, 'may provide sensitive measures'),
 'F26': ('farmer_sproat_witzel_2004_author.pages.json', 28, 'maintaining that cohesion'),
 'F27': ('sproat_2010_last_words.pages.json', 8, 'with very high accuracy'),
 'F28': ('sproat_2010_last_words.pages.json', 9, 'among the peer reviewers'),
 'F29': ('sproat_2014_monograph.pages.json', 86, 'extend the taxonomy'),
 'F30': ('sproat_2014_monograph.pages.json', 85, 'not correlated with length.'),
 'F31': ('rao_2010_reply.pages.json', 9, 'develop better statistical tests'),
 'F32': ('vidale_web_excerpt.json', 'text', 'committee of no more'),
 'F33': ('vidale_web_excerpt.json', 'text', 'freely exchanged'),
 'F34': ('vidale_web_excerpt.json', 'text', 'international research on palaeography'),
 'F35': ('vidale_web_excerpt.json', 'text', 'material, functional and spatial variability'),
 'F36': ('mukhopadhyay_2023.pages.json', 2, 'narrow down the semantic scopes'),
 'F37': ('mukhopadhyay_2023.pages.json', 29, 'should be researched in future studies.'),
 'F38': ('rao_2018_economics.pages.json', 8, 'Additional analysis and archaeological evidence'),
 'F39': ('frenez_2018_private_person.pages.json', 27, 'further tested and'),
 'F40': ('ameri_2013.pages.json', 23, 'More detailed studies'),
 'F41': ('petrie_lynam_accepted.pages.json', 25, 'future investigation of local subsistence'),
 'F42': ('petrie_lynam_accepted.pages.json', 25, 'explore further models'),
 'F43': ('law_ch14.pages.json', 2, 'more extensive sampling'),
 'F44': ('law_ch14.pages.json', 4, 'excavation (or re-excavation)'),
 'F45': ('law_ch14.pages.json', 4, 'long-term program'),
 'F46': ('miller_projects.html', 'html', 'identify possible ancient bureaucracies'),
 'F47': ('vahia_2025_slides.pages.json', 34, 'context of sign modifications.'),
 'F48': ('vahia_2025_slides.pages.json', 40, 'These need to be isolated'),
 'F49': ('possehL_proxy.txt', 'text', 'an authoritative sign-list'),
 'F50': ('possehL_proxy.txt', 'text', 'many small scale research efforts'),
 'F51': ('possehL_proxy.txt', 'text', 'use multiple lines of inference'),
 'F52': ('morphological-study-2025.pages.json', 8, 'more material evidences and tangible data'),
 'F53': ('rao_2026_interview.html', 'html', 'We may be able to reconstruct'),
 'F54': ('rao_2026_interview.html', 'html', 'archaeologists will need to uncover'),
 'F55': ('ratnagar_2018_interview.html', 'html', 'archeology must consider seriously.'),
 'F56': ('iitgn_2023_abstracts.pages.json', 50, 'must be taken into'),
 'F57': ('green_2021_priest_king.pages.json', 30, 'deserve further research'),
 'F58': ('green_2021_priest_king.pages.json', 31, 'heterarchical corporate groups were more numerous'),
 'F59': ('green_2021_priest_king.pages.json', 32, 'important topic for'),
}

def normalize_prose(value, key=''):
    """Separate fused prose/locators, preserving identifiers, URLs and paths."""
    if isinstance(value, dict):
        return {k: normalize_prose(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_prose(v, key) for v in value]
    if isinstance(value, tuple):
        return tuple(normalize_prose(v, key) for v in value)
    if not isinstance(value, str) or key in {
        'id', 'source_id', 'source_ids', 'url', 'witness_path', 'repository_links',
        'sha256', 'witness_sha256', 'extraction_path', 'path', 'text'}:
        return value
    # Mask inline filenames, URLs and machine identifiers inside prose.
    pieces = re.split(r'(https?://\S+|[\w./%-]+\.(?:pdf|json|html|py|png|txt|md|csv)|\b[A-Z][A-Z0-9-]+\b)', value)
    for i in range(0, len(pieces), 2):
        s = re.sub(r'([A-Za-z]*[a-z]{2,})(?=\d)', r'\1 ', pieces[i])
        s = re.sub(r'(\d)(?!(?:st|nd|rd|th)\b)(?=[A-Za-z]{2,}\b)', r'\1 ', s)
        # Compact all-capital page locators are readable with the same spacing.
        s = re.sub(r'\bPDF(?=\d)', 'PDF ', s)
        pieces[i] = s
    return re.sub(r'\bPDF(?=\d)', 'PDF ', ''.join(pieces))

def comparison(sid, locator, statement):
    return dict(source_id=sid, locator=locator, relation='shared_priority', statement=statement)

def apply(coded):
    for key in ['sources', 'recommendations', 'positions', 'coverage', 'corrections']:
        coded[key] = normalize_prose(coded[key])
    rows = coded['recommendations']
    by = {r['id']: r for r in rows}
    by['F01']['source_locator']='30:08-30:30; second-review caption check; selected visible anchor at 30:27'
    by['F02']['source_locator']='24:36-25:12; second-review caption check; selected visible anchor at 25:04'
    by['F03'].update(
        recommendation='Investigate how sign inventories vary with site size in their context of use.',
        source_locator='29:00-29:18; second-review caption check and selected visible captions',
        limitation='The reported frequency percentages are descriptive findings.',
        implementation_note='Package proposal: use assemblage counts, rarefaction and missingness checks to interpret inventory differences. These controls are not attributed to the speaker.',
        comparisons=[])
    by['F10']['source_locator'] = 'printed/PDF 45, paragraph beginning A special issue, final sentence'
    by['F13']['recommendation'] = 'Record and quantify pottery marks and other inscribed objects in more detail across regions.'
    by['F24']['recommendation'] = 'Account for the Near Eastern second-hand seal problem before linking symbols on Indus seals to their users.'
    by['F24']['limitation'] = 'The footnote applies the comparative problem to Indus seal-user interpretation; it does not document a specific reused Indus seal.'
    coded['positions'].extend([
        dict(id='F04', source_id='FRENEZ-TALK-2026', locator='51:00-52:50; second-review caption check; anchor at 51:30',
             status='Exploratory', theme='data and corpora', position='Reports that inscriptions outside the valley have non-canonical sequences and unusual affixes, sign positions or sign types.',
             observation='The speaker describes earlier analyses and alternative interpretations of frequent signs.',
             scope='Reported finding; the passage contains no request to study these inscriptions.',
             implementation_note='A matched external/core comparison is a package proposal considered in action A07.',
             repository_links=by['F04']['repository_links']),
        dict(id='F53', source_id='RAO-INTERVIEW-2026', locator=by['F53']['source_locator'],
             status='Exploratory', theme='computational method', position='Rao says partial reconstruction of the number system may be possible.',
             observation='The reporter discusses tally marks and standardized weight ratios as possible aids.',
             scope='Expectation and reporter explanation; no direct research prescription admitted.',
             repository_links=by['F53']['repository_links'])])
    old = by['F55']
    if not any(x['researcher']=='Shereen Ratnagar' for x in coded['coverage']):
        coded['coverage'].append(dict(researcher='Shereen Ratnagar',source_ids=[old['source_id']]))
    for item in coded['coverage']:
        if item['researcher'] == 'Shereen Ratnagar':
            item.update(disposition='Opened interview; general archaeological remark outside this survey agenda',
                        status='Exploratory',
                        reason='The plant/bone passage endorses taking collection questions seriously while recounting a Turkish professor\'s concern about repetitive samples; no Indus-script prescription admitted.',
                        legacy_row_id='F55', source_id=old['source_id'], locator=old['source_locator'])
    rows[:] = [r for r in rows if r['id'] not in {'F04', 'F53', 'F55'}]
    # Use the appropriate distinct prescription, rather than one generic pair.
    replacements = {
      'F02': [comparison('WELLS-2015','Preface viii, PDF 12','Calls for regional text-structure research and chronological control.'),
              comparison('KONASUKAWA-2023','printed/PDF 50, paragraph 2','Requires chronology when discussing the script.')],
      'F06': [comparison('KENOYER-2006','printed 21, scan PDF 8 right column','Requests chronological sorting of earlier-excavated objects.'),
              comparison('KONASUKAWA-2023','printed/PDF 50, paragraph 2','Requires seal chronology in discussion of the script.')],
      'F09': [comparison('VIDALE-2007','Appendix proposal 2, printed 363','Proposes a central standardized archive with accessible contextual information.')],
      'F10': [comparison('VIDALE-2007','Appendix proposal 4, printed 363-364','Requires material, functional and spatial separation before synthesis.'),
              comparison('YADAV-2013','Conclusions printed 98, PDF 32','Requires site and object-type fluctuations in interpretation models.')],
      'F13': [comparison('VIDALE-2007','Appendix proposal 4, printed 364','Requests pottery inscription comparisons within production stage and position before broader synthesis.')],
      'F17': [comparison('WELLS-2015','Preface viii, PDF 12','Calls for defining regional differences in text structure.')],
      'F20': [],  # Vahia's composites are a different graphic question.
      'F28': [],  # Rao replies to assessment, not specialist-review advice.
      'F33': [comparison('FULS-2023','printed/PDF 45, final paragraph','Aims to provide worldwide access to all inscriptions with continuing updates.')],
      'F35': [comparison('KENOYER-2020','printed 223, PDF 7','Requires distinguishing pre-firing producer marks from later graffiti.'),
              comparison('FULS-2023','printed/PDF 45, A special issue paragraph','Requires treating inscribed artefacts as heterogeneous sets.')],
      'F40': [],  # Text regionality is narrower than regional material classes.
      'F45': [],  # General collaboration does not prescribe geological sourcing.
      'F47': [],  # Regional distribution is narrower than wider cultural context.
      'F48': [],  # Yadav's stylistic variants are not explicitly composites.
      'F50': [],  # Vidale's theses are coordinated palaeography, not small efforts generally.
    }
    for rid, comparisons in replacements.items():
        by[rid]['comparisons'] = comparisons
    for r in rows:
        r.setdefault('implementation_note','')
        r['kind'] = 'stated project aim' if r['id'] in {'F09','F21','F31','F43','F45','F46'} else 'recommendation or stated priority'
        r['comparison_scope'] = 'Relations apply to each specified proposition; a disputed premise does not imply opposition to data collection.' if r['comparisons'] else 'No matching independent recommendation or direct dispute located in the opened sample.'
    for s in coded['sources']:
        if s['id'] == 'FRENEZ-TALK-2026':
            s['read_scope'] = 'Coordinator and second-review caption checks; independently read four short visible English auto-caption windows at 25:04, 29:16, 30:27 and 51:30. Full transcript not recovered.'
            s['access'] = 'opened_selected_captions_and_caption_checks'
        # Short per-row anchors replace the earlier single longer quotation.
        s['quotations'] = []
    assign_author_groups(coded)
    attach_anchors(coded)
    coded['action_ranking'] = ranking(coded)
    return coded

def assign_author_groups(coded):
    sources = coded['sources']
    parent = {s['id']: s['id'] for s in sources}
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    def union(a, b):
        parent[find(b)] = find(a)
    aliases = {'Mayank Vahia':'Mayank N. Vahia'}
    voices = {}
    for s in sources:
        names = ['Rajesh P. N. Rao'] if s['id'] == 'RAO-INTERVIEW-2026' else s['authors']
        voices[s['id']] = {aliases.get(n, n) for n in names}
    for a in sources:
        for b in sources:
            if voices[a['id']] & voices[b['id']]:
                union(a['id'], b['id'])
    union('WELLS-2015','FULS-2023')  # Technical appendices / collaboration.
    clusters = {}
    for s in sources:
        clusters.setdefault(find(s['id']), []).append(s['id'])
    groups = []
    sid_group = {}
    for i, ids in enumerate(sorted(clusters.values(), key=lambda v: sorted(v)[0]), 1):
        gid = f'AG{i:02d}'
        groups.append(dict(id=gid, source_ids=sorted(ids), researchers=sorted(set().union(*(voices[x] for x in ids)))))
        sid_group.update({sid:gid for sid in ids})
    coded['author_groups'] = dict(
        method='Connected components of overlapping credited authors across the opened catalogue; Wells/Fuls also joined for their collaboration. Interview evidence groups the attributed speaker. Transitive overlap is conservative.',
        count_scope='n_independent_sources counts author components across the row source and all scoped comparisons, including disputes about premises. It is not a count of sources endorsing the recommendation.',
        groups=groups)
    for s in sources:
        s['author_group_id'] = sid_group[s['id']]
    for r in coded['recommendations']:
        compared = [r['source_id']] + [c['source_id'] for c in r['comparisons']]
        r['independent_author_groups'] = sorted({sid_group[s] for s in compared})
        r['n_independent_sources'] = len(r['independent_author_groups'])
        for c in r['comparisons']:
            c['author_group_id'] = sid_group[c['source_id']]
            c['independent_of_row_author_group'] = sid_group[c['source_id']] != sid_group[r['source_id']]
        relations = {c['relation'] for c in r['comparisons']}
        if 'disputes_underlying_thesis' in relations:
            r['shared_or_disputed'] = 'Disputed premise; research request not directly disputed'
        elif relations & {'direct_dispute_on_inference','direct_counterreply','direct_dispute_on_assessment'}:
            r['shared_or_disputed'] = 'Disputed inference scope'
        elif 'different_stated_sequence' in relations:
            r['shared_or_disputed'] = 'Different proposed research sequences'
        elif 'shared_method_with_different_inference' in relations:
            r['shared_or_disputed'] = 'Shared method; different inference claims'
        elif any(c['independent_of_row_author_group'] and c['relation'] in {'shared_priority','explicit_agreement_on_resource'} for c in r['comparisons']):
            r['shared_or_disputed'] = 'Shared priority across independent author groups'
        else:
            r['shared_or_disputed'] = 'Single author group in this opened sample'

def attach_anchors(coded):
    all_rows = {r['id']:r for r in coded['recommendations'] + coded['positions']}
    all_rows['F55'] = next(x for x in coded['coverage'] if x.get('legacy_row_id') == 'F55')
    for rid, (name, selector, text) in ANCHORS.items():
        path = name if name.startswith('research/') else RAW + name
        row = all_rows[rid]
        row['anchor'] = dict(text=text, locator=row.get('source_locator', row.get('locator')),
                             witness_path=path, selector=selector,
                             sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                             verification='Visually read original image' if selector=='visual' else 'Exact match after whitespace normalization in selected source text')
        if rid in {'F01','F02','F03','F04'}:
            row['anchor']['caption_time'] = {'F01':'30:27','F02':'25:04','F03':'29:16','F04':'51:30'}[rid]

def ranking(coded):
    # Availability A: 3 joined inputs, 2 partial joins, 1 major gaps, 0 no inputs.
    # Autonomy B: 3 local completion, 2 useful local preparation, 1 substantial
    # specialist access, 0 new fieldwork. Reuse C: 3 foundational many themes,
    # 2 several questions, 1 one bounded question, 0 speculative contribution.
    # Score = 2*A+B+C. Ties: A descending, B descending, then action ID.
    d = {name:coded[name] for name in ['D1','D2','E','G','H','CENSUS','WEST','CONTROLS']}
    specs = [
      ('A01','Extend the object/source/date/site/type ledger and expose missing fields.',3,3,3,['F02','F06','F11','F13','F15','F16','F35','F56'],['CENSUS','D1','E'],'Reuse existing registers; define face, component and specimen joins.'),
      ('A02','Interpret site/type inventories and frequencies within their sampling frame.',3,3,2,['F03','F05','F10','F17','F19'],['D1','D2'],'Reuse composition and rarefaction results; add exposure only where documented.'),
      ('A03','Prepare image-linked review queues for variants, composites and rare signs.',3,2,2,['F20','F23','F32','F33','F48','F49'],['H','D1','G'],'Rank prepares candidates; final adjudication needs specialists.'),
      ('A04','Prepare a bounded comparison-system feature and length-control audit.',2,3,3,['F27','F29','F30','F31','F51'],['CONTROLS','G','H'],'Reuse existing controls; failed totem/weather paths need new evidence before retry.'),
      ('A05','Document access, versioning and specialist-review responsibilities.',2,3,2,['F01','F07','F09','F14','F28','F50'],['CENSUS','H'],'Prepare private metadata and review plans; permissions govern redistribution.'),
      ('A06','Specify dated motif-stability tests of the branding/cohesion models.',2,2,2,['F25','F26','F39'],['D1','D2'],'Matched dates, sites and object selection required; motifs do not count corporate groups.'),
      ('A07','Audit joins for a bounded external/core comparison and seal reuse.',1,2,2,['F05','F17','F19','F24'],['WEST','D1','D2'],'Package design choice from regional/context priorities; F04 motivates it as an observation. External samples are small and context joins incomplete.'),
    ]
    actions=[]
    for aid, action, a, b, c, ids, links, reason in specs:
        actions.append(dict(id=aid,status='Exploratory',action=action,availability=a,autonomy=b,reuse=c,
                            score=2*a+b+c,recommendation_ids=ids,repository_links=[d[k] for k in links],scope_and_reason=reason))
    actions.sort(key=lambda x:(-x['score'],-x['availability'],-x['autonomy'],x['id']))
    for i, row in enumerate(actions,1):
        row['rank']=i
    return dict(status='Exploratory',scoring_rule='Score = 2*availability + autonomy + reuse; descending score, availability, autonomy, then action ID.',
                criteria=dict(availability='3 joined inputs; 2 partial joins; 1 major gaps; 0 absent.',autonomy='3 local completion; 2 useful local preparation; 1 substantial specialist access; 0 new fieldwork.',reuse='3 foundational across themes; 2 several questions; 1 one question; 0 speculative.'),
                selection='Ranks bounded additional work with current holdings. Rows marked Limited are excluded. Preparing evidence is distinguished from completing the entire recommendation.',
                excluded_limited_rows=['F57','F58','F59'],actions=actions)
