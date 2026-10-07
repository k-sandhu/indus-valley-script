"""Bibliographic/access corrections for the second follow-up; no acquisitions."""
import json
from pathlib import Path
from datetime import datetime, timezone
import analyze as main
from acquire_review_sources import URLS


def run():
    destination = main.OWN / 'sources-review-2026-10-07.json'
    if destination.exists():
        raise FileExistsError(destination)
    folder = main.RAW / 'sources-second-followup-2026-10-07'
    acquisitions = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    records = [
        {'id': 'JC2018', 'title': 'Understanding Indus Seal-Carving Traditions: A Stylistic and Metric Approach',
         'authors': ['Gregg M. Jamison'], 'year': 2018,
         'venue': 'In M. Ameri, S. K. Costello, G. Jamison and S. J. Scott (eds.), Seals and Sealing in the Ancient World: Case Studies from the Near East, Egypt, the Aegean, and South Asia, Cambridge University Press, pp.167-186',
         'url': URLS['jamison-cambridge'], 'doi': '10.1017/9781108160186.013',
         'access': 'opened publisher abstract and bibliographic metadata; full chapter unread',
         'locations': ['Summary; Information'],
         'relation': 'Style and metric assignment of producer groups directly precedes the workshop/standardization question. The present pooled CV and motif/text statistics do not assign producers.'},
        {'id': 'GC2018', 'title': 'Operational Sequences and Stamp Seals: A Preliminary Report on an Experimental and Microtopographic Framework for Identifying Groups of Seal Carvers in the Indus Civilization',
         'authors': ['Adam S. Green'], 'year': 2018,
         'venue': 'In M. Ameri, S. K. Costello, G. Jamison and S. J. Scott (eds.), Seals and Sealing in the Ancient World: Case Studies from the Near East, Egypt, the Aegean, and South Asia, Cambridge University Press, pp.187-203',
         'url': URLS['green-cambridge'], 'doi': '10.1017/9781108160186.014',
         'access': 'opened publisher abstract and bibliographic metadata; full chapter unread',
         'locations': ['Summary; Information'],
         'relation': 'Abstract describes 30 experimental seals and operational-sequence comparison of two Chanhu-daro seals. Such microtopographic assignments provide a production variable absent from this export.'},
        {'id': 'JW2018', 'title': 'The Organization of Indus Unicorn Seal Production. A Multi-faceted Investigation of Technology, Skill, and Style',
         'authors': ['Gregg M. Jamison'], 'year': 2018,
         'venue': 'In D. Frenez, G. M. Jamison, R. W. Law, M. Vidale and R. H. Meadow (eds.), Walking with the Unicorn: Social Organization and Material Culture in Ancient South Asia, Archaeopress, pp.272-291',
         'url': URLS['jamison-contents'],
         'access': 'opened publisher contents; full chapter unread; pagination corroborated by REVIEW.md',
         'locations': ['Contents, Jamison chapter; REVIEW.md Precedents'],
         'relation': 'A direct technology/skill/style precedent for unicorn production; pooled motif concentration and seal sizes alone do not replicate its producer assignments.'},
        {'id': 'A2013', 'title': 'Regional Diversity in the Harappan World: The Evidence of the Seals',
         'authors': ['Marta Ameri'], 'year': 2013,
         'venue': 'In S. A. Abraham, P. Gullapalli, T. P. Raczek and U. Z. Rizvi (eds.), Connections and Complexity: New Approaches to the Archaeology of South Asia, Left Coast Press, pp.355-374',
         'url': URLS['ameri2013'], 'access': 'opened primary chapter PDF and extracted full text',
         'locations': ['printed pp.359-360 discussion; p.361 Table 19.1 / PDF page13; pp.364-366 Eastern sites'],
         'relation': 'Six-site iconography/style study underlying the approximate multi-site average cited by Frenez. Regional exceptions at Banawali and Kalibangan directly precede the concentration comparison.',
         'edition_note': 'Saved draft has copyright 2012; bibliographic publication year 2013 retained.'},
    ]
    ids = {'JC2018': 'jamison-cambridge', 'GC2018': 'green-cambridge',
           'JW2018': 'jamison-contents', 'A2013': 'ameri2013'}
    for record in records:
        record['quotations_used'] = 0
        record['acquisitions'] = [v for v in acquisitions if v['id'] == ids[record['id']]]
        record['rights_status'] = 'rights-unverified; payload local-only'
    result = {'stage': 'post-review amendment', 'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'sources': records, 'download_attempts': acquisitions,
        'reused_sources': ['K2005 existing full Treccani witness', 'O2019 existing PDF/Table9',
                           'F2018 existing pp.186-188 web witness', 'Y2013 existing full PDF',
                           'FS2016 existing Salūt PDF, pp.116-117/Fig.9', 'CAP2026 coordinator caption check'],
        'search_log': [
            {'queries': ['site.cambridge.org Understanding Indus Seal-Carving Traditions',
                         'site.cambridge.org Operational Sequences and Stamp Seals',
                         'Jamison 2018 Walking with the Unicorn 272 291',
                         'Ameri 2013 65 seals unicorn', 'Ameri 2013 Regional diversity'],
             'outcome': 'Opened Cambridge abstracts, Archaeopress contents and the 2.56-MB Ameri chapter. Full Frenez PDF exceeded the 4-MiB cap; discarded its partial file and reused the earlier witness. DOI-only Green opening failed; Cambridge chapter link succeeded.'}],
        'caption_quote': {'source': 'experiments/2026-10-06-research-program/frenez-talk-check.md',
            'location': 'The oligopoly and its persistence (41:30-43:30)',
            'quote': 'the iconographies kept the same frequencies for almost a millennium',
            'words': 12, 'access': 'opened coordinator caption-based paraphrase; not a verbatim speech transcript'},
        'source_corrections': {'Banawali': 'Numerical extent was acquired in K2005, Vidale Banawali section; earlier search-log conclusion was incorrect.',
            'F2018': 'Approximate 65% is a multi-site average attributed to Ameri 2013, not a pooled corpus share. The earlier p.167 size/style attribution is unverified and withdrawn.'}}
    main.write(destination, result)
    source_path = main.OWN / 'sources.json'
    original = json.loads(source_path.read_text(encoding='utf-8'))
    for item in original['search_and_access_log']:
        if 'did not acquire a numerical Banawali source' in item.get('outcome', ''):
            item['original_outcome_archived_in'] = 'pre-second-followup-2026-10-07/sources.json'
            item['outcome'] = 'Located Kenoyer, Suryanarayan and Treccani. Correction of 7 October: the acquired Treccani Banawali section gives a 400-m side, a 16-ha bounding square; the original compilation omitted it.'
    for item in original['sources']:
        if item['id'] == 'K2005':
            item['locations'].append('Vidale site entries Harappa, Mohenjo daro, Rakhigarhi, Lothal, Nausharo, Banawali, Chanu daro, Kot diji and Surkotada; see supplemental source-anchor table.')
        if item['id'] == 'F2018':
            item['locations'] = ['preview printed pp.186-188, concentration, oligopoly and more-than-six-centuries discussion']
            item['relation_to_package'] = 'Frenez cites Ameri 2013 for an approximate 65% multi-site average and discusses oligopoly persistence for more than six centuries. Previous p.167 attribution withdrawn; full chapter still unread.'
    original['post_review_corrections'] = 'sources-review-2026-10-07.json; previous complete file archived byte for byte.'
    main.write(source_path, original)
    print('Four new source records and dated corrections recorded.')


if __name__ == '__main__':
    run()
