"""Replay the small v6 source/locator amendments into a new owned directory."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
ORIGINAL = OWN / 'pre-v6-2026-10-07'
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/synthesis/review-fixes-2026-10-07-v1'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(p, data):
    if p.exists():
        raise ValueError('Refusing overwrite')
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    out = (ROOT / args.output_dir).resolve()
    if not out.is_relative_to(OWN) or out.exists():
        raise ValueError('Use a new owned amendment directory')
    out.mkdir(parents=True)
    sources = load(ORIGINAL / 'sources.json')
    byid = {r['id']: r for r in sources['sources']}
    byid['CISI1']['venue'] += '; Helsinki: Suomalainen Tiedeakatemia'
    byid['CISI2']['venue'] += '; Helsinki: Suomalainen Tiedeakatemia'
    byid['SALUT2016']['title'] = 'Bronze Age Salūt (ST1) and the Indus Civilization: recent discoveries and new insights on regional interaction'
    byid['IAR2013'].update(title='Indian Archaeology 2013-14 – A Review',
                         authors=['Rakesh Tewari (chief editor)', 'D. N. Dimri (editor)', 'Archaeological Survey of India'])
    byid['IAR1987'].update(authors=['M. C. Joshi (editor)', 'Archaeological Survey of India'],
                         publication_date_note='Title page 1993; copyright page 1992. Date note removed from authors field.')
    byid['CISI33'].update(access_in_B3='saved_40_page_excerpt_without_catalogue_plates',
                         url_scope='Desset author postprint/excerpt: contents, preface, essay and bibliography; full volume catalogue not opened')
    byid['GONUR2005'].update(authors=['Victor Sarianidi (English title page)'], venue='Aşgabat: Miras, 2005')
    byid['DHOLAVIRA2015'].update(title='Excavations at Dholavira', reported_excavation_seasons='1989–90 to 2004–05',
         access_in_B3='saved_user_upload_mirror_transcription', title_scope='Printed ASI title page not opened; date range is recorded separately from the uploader title',
         reviewer_scan='https://archive.org/details/dholavirareportpreliminaryjan2015_860_K',
         reviewer_scan_scope='Reviewer opened nine page scans; 938-page preliminary upload with no title page. B3 has not opened this upload.',
         original_page_rasters_opened_in_B3=False)
    byid['LOTHAL2005']['venue'] += '; Studi egei e vicinorientali 1'
    byid['LOTHAL2005']['rights'] = 'Reviewer reports Zenodo API CC BY 4.0/open-access field; not re-fetched by B3. Depositor metadata and applicable image rights require asset-specific review.'
    byid['LOTHAL2005']['title_note'] = 'Printed article title retained; Zenodo metadata uses networks in place of Circuits.'
    for sid in ['CISI1', 'CISI2', 'IAR1987', 'CISI33', 'DHOLAVIRA2015', 'LOTHAL2005']:
        byid[sid]['bibliographic_amendment_evidence'] = 'review/sample-recheck-AB.md#2-bibliographic-entries; review/sample-recheck-CD.md#2-bibliographic-entries'
    # The new extraction manifests are small pointers; source bytes stay raw.
    all_witnesses = load(RAW / 'manifest.json') + load(RAW / 'bibliographic-manifest.json')
    mapping = {'CISI1': 'CISI1', 'IM77': 'IM77', 'CISI2': 'CISI2', 'Salut': 'SALUT2016', 'IAR2013': 'IAR2013', 'Gonur': 'GONUR2005'}
    for w in all_witnesses:
        stem = w.get('render') or w.get('text')
        key = stem.split('-pdf')[0] if stem else ''
        sid = mapping.get(key)
        if sid:
            byid[sid]['inspected_witnesses'].append({'source': w['source'], 'source_sha256': w['sha256'],
                'pdf_page_1_based': w['pdf_page_1_based'], 'review_date': '2026-10-07',
                'local_witness_directory': RAW.relative_to(ROOT).as_posix(), 'render_file': w.get('render'), 'text_file': w.get('text')})
    for sid, rel, pages in [
        ('LOTHAL2005', 'data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/LOTHAL2005.pdf', [8, 9]),
        ('NIPPUR1993', 'data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/nippur1993-s3.pdf', [119, 151])]:
        # These are reviewer-inspected pages; do not imply B3 re-opened them.
        byid[sid]['additional_review_locators'] = {'source': rel, 'pdf_pages_1_based': pages,
            'reviewer': 'Sonnet review/sample-recheck-AB.md or sample-recheck-CD.md', 'B3_reopened': False}
    sources['sources'].append({'id': 'RAO1985', 'title': 'Lothal: A Harappan Port Town (1955–62), Volume II',
        'authors': ['S. R. Rao'], 'year': 1985, 'venue': 'Memoirs of the Archaeological Survey of India 78; New Delhi: Archaeological Survey of India',
        'url': 'https://archive.org/details/masi78lothalaharappanporttownraos.r.part2_531_D/page/n55/mode/2up',
        'opened_in_B3': False, 'opened_by_reviewer': True, 'search_snippet_only_in_B3': False,
        'access_in_B3': 'Not opened; reviewer reports primary scan p.305 / leaf n55; earlier batch copy was a challenge response',
        'inspected_witnesses': [], 'rights': 'Rights unverified; no source payload copied', 'quoted_words_in_B3': 0,
        'evidence': 'review/sample-recheck-AB.md#3-findings; REVIEW.md#4-bibliography'} )
    marshall = 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/marshall-alt-pdf.body'
    sources['sources'].append({'id': 'MARSHALL1931', 'title': 'Mohenjo-daro and the Indus Civilization',
        'authors': ['John Marshall (editor)'], 'year': 1931, 'venue': 'Volume II; London: Arthur Probsthain; Tabulation of Seals p.402',
        'url': 'https://archive.org/download/in.ernet.dli.2015.62023/2015.62023.Mohenjo-daro-And-The-Indus-Civilization-1931.pdf',
        'opened_in_B3': True, 'search_snippet_only_in_B3': False, 'access_in_B3': 'saved_primary_PDF_p402',
        'inspected_witnesses': [{'source': marshall, 'source_sha256': sha256((ROOT / marshall).read_bytes()).hexdigest(),
          'pdf_page_1_based': 53, 'printed_page': 402, 'local_witness_directory': RAW.relative_to(ROOT).as_posix(), 'render_file': 'Marshall-pdf53.png'}],
        'rights': 'Source and museum image terms unresolved; raw witness remains local', 'quoted_words_in_B3': 0})
    sources['amendment'] = 'Post-review v6: bibliography and opening scope corrected; previously opened witnesses retained. Rao1985 unseen by B3.'
    save(out / 'sources.json', sources)
    audit = load(ORIGINAL / 'source-sample-audit.json')
    locators = {'Dholavira': 'saved mirror pp.233,242,308; page numerals follow the preceding text',
                'Nagwada': 'pp.19–20 / PDF27–28',
                'Karanpura': 'graffiti p.120 / PDF125; seals pp.114,117 / PDF119,122; plates pp.118–119',
                'Banawali': 'pp.344–349,364; endpoint p.349 / PDF385',
                'Nippur': 'catalogue p.113 / PDF151; discussion pp.81–82 / PDF119–120',
                'Tepe Yahya': 'pp.vi,xi,xii,xv,xx–xxi / PDF8,13,14,17,22–23; catalogue plates unavailable',
                'Gonur Depe': 'p.258 / PDF130, figs.114–115; narrative continues p.259'}
    for r in audit['rows']:
        r['original_B3_outcome'] = r['outcome']
        r['review_outcome'] = 'qualified' if r['site'] in ['Lothal', 'Dholavira'] else 'supported'
        r['review_evidence'] = 'review/sample-recheck-AB.md' if r['batch'][0] in ['a', 'b'] else 'review/sample-recheck-CD.md'
        if r['site'] in locators:
            r['original_locator'] = r['locator']
            r['locator'] = locators[r['site']]
        if r['site'] == 'Lothal':
            r['tested_assertion'] = 'Frenez and Tosi report 93 sealings and attribute the total to Rao\'s finds, pp.67–68,70–71'
            r['B3_observation'] = '93 occurs in the saved article. The review checked its attribution to Rao; it is not a new recount. Rao1985 p.305 reports91 and remains unseen by B3.'
        if r['site'] == 'Bhagwanpura':
            r['B3_observation'] = 'P.139 lists two tablets and nineteen marked sherds. Fig.39 draws A-1 in three views; A-2 is described in the text and listed by the review in Pl.XLIII B.'
        if r['site'] == 'Nippur':
            r['B3_observation'] = 'Catalogue p.113 supplies registrations13 N506/IM78230, dimensions2×2×1cm and Floor3. The deliberate-fill heading below belongs to other objects; pp.81–82 discuss secondary context.'
    audit['review_re_adjudication'] = {'supported': 18, 'qualified': 2, 'evidence': 'REVIEW.md#3-row-join-and-sample-checks'}
    audit['scope'] = 'Original B3 endpoint-bound verdicts14/6 retained; corrected locators/observations and source-wide reviewer verdicts18/2 recorded separately; purposive sample.'
    save(out / 'source-sample-audit.json', audit)
    conflicts = load(ORIGINAL / 'conflicts.json')
    for r in conflicts['conflicts']:
        if r['id'] == 'Lothal-counts':
            r.update(observation='Rao1985 p.305 gives91; Frenez and Tosi2005 pp.67–68,70–71 attribute93 to Rao\'s finds; CISI1 L124–216 has93 sealing entries; IM77 selects75.',
                resolution='Separate attributed inventory statements; no new recount established. Resolve difference through excavation-number inventory, with Rao p.305 unseen by B3 and opened by reviewer.', sources=['RAO1985', 'LOTHAL2005', 'CISI1', 'IM77'])
        if r['id'] == 'Dholavira-counts':
            r.update(observation='Report mirror p.233:225 seals/60 sealings; p.242:194 inscription-analysis seals/139 positive; p.308:61 sealings, four undated, remaining59. Reviewer scan chart sums58; motif table136 versus prose130; locality204 and period185 are other analysed populations.',
                resolution='Keep each population and source locator. 61−4=57, so remaining59 and chart58 disagree. Missing inscription23/194=11.9%, with prose23% erroneous. B3 uses mirror; original upload pages were opened by reviewer only.',
                review_evidence='review/sample-recheck-AB.md#3-findings')
    conflicts['amendment'] = 'v6 locators and count attribution; original seven conflict IDs retained'
    save(out / 'conflicts.json', conflicts)
    gaps = load(ORIGINAL / 'priority-gaps.json')
    museum = next(r for r in gaps['gaps'] if r['id'] == 'museum-unjoined')
    museum.update(pool='46 museum original records lacking a checked local identifier join',
                  scale={'inspected_originals': 114, 'confirmed_join_lower_bound': 68, 'previous_lower_bound': 61, 'unjoined': 46,
                         'failed_string_match': 13, 'untried_usable_key': 2, 'no_usable_key_in_original_pass': 31},
                  evidence=['join-summary.json', 'data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/candidate-object-joins.json', 'review/museum-join-check.md'])
    museum['route'][0] = 'Original53 raw candidate records;46 remain unresolved after seven checked additions'
    next(r for r in gaps['gaps'] if r['id'] == 'lothal')['scale']['reported_sealings_range'] = [91, 93]
    gaps['amendment'] = 'v6 museum lower bound and query dispositions; pools remain overlapping'
    save(out / 'priority-gaps.json', gaps)
    print(json.dumps({'sources': len(sources['sources']), 'sample_rows': len(audit['rows']), 'output': out.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
