"""Record additional integrated-source readings separately from the control frame."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from acquire_controls import REPO

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    p = REPO / path
    return {'path': path, 'bytes': p.stat().st_size, 'sha256': sha(p)}


if __name__ == '__main__':
    path = HERE / 'additional-anchor-review.json'
    if path.exists():
        raise SystemExit('Refusing existing anchor-review endpoint')
    records = [
        {'branch': 'material', 'source_ids': ['MS04'], 'observation_ids': ['MO12', 'MO13', 'MO14', 'MO18'],
         'witness': pin('data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v1/bhagwanpura-full.pdf'),
         'inspected': 'Printed pp.30,118,120,122; PDF pp.55,154,156,158. All four contributor renders independently viewed; original report identifies their catalogue and society loci.',
         'renders': [pin(f'data/raw/2026-10-12-transmission-hypothesis/material/ocr-bhagwanpura-v5/pdf{n}.png') for n in [154,156,158]] +
                    [pin('data/raw/2026-10-12-transmission-hypothesis/material/ocr-bhagwanpura-v3/pdf55.png')],
         'finding': 'BPR-36 is an unfinished roughly faceted black-jasper bead in late IB. BPR-208 is one mid-IB accession described as quartz and banded agate in separate lists. Production from unfinished objects/raw material and learning from neighboring Late Harappans are author-attributed inferences.',
         'limit': 'No direct object date, demonstrated teacher, named language or route into a particular literary passage is supplied by these loci.'},
        {'branch': 'material', 'source_ids': ['MS02'], 'observation_ids': ['MO03'],
         'witness': pin('data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v2/harappa-bead-collection.html'),
         'inspected': 'Actual HTML prose and final substantive image-alt caption, parsed independently; no photograph acquired.',
         'finding': 'The page describes133objects in a later collection with contents from all occupation phases. Duplicate image-alt occurrences are the same caption.',
         'limit': 'The collection deposition cannot date each object’s manufacture.'},
        {'branch': 'material', 'source_ids': ['MS03'], 'observation_ids': ['MO08'],
         'witness': pin('data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v1/hulas-full.pdf'),
         'inspected': 'Printed p.232/PDF p.244; full contributor render independently viewed.',
         'render': pin('data/raw/2026-10-12-transmission-hypothesis/material/hulas-inspection-v1/pdf244.png'),
         'finding': 'The appendix discusses uncertain wild/cultivated rice identification and rice-bearing marsh clay as an alternative while discussing comparative Gujarat impressions.',
         'limit': 'Its application to Hulas is a prospective formation control, not a demonstrated Hulas marsh-clay procurement event.'},
        {'branch': 'material', 'source_ids': ['MS06'], 'observation_ids': ['MO23'],
         'witness': pin('data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v3/jognakhera2026-supplement.docx'),
         'inspected': 'Original publisher supplementary Word XML: all TableS2 rows, its95.4% heading, and comparison with TableS1 context fields. Main PDF not independently inspected in this additional pass.',
         'finding': 'The three newly dated specimen rows give2471–2298,1880–1691 and1517–1428calBCE for barley,Vigna andrice. Their TableS2 contexts say Jognakhera rather than assigning individual layers.',
         'limit': 'No recalibration, rotation inference, same-field inference or crop-teaching route reconstructed.'},
        {'branch': 'texts', 'source_ids': ['T-RVSANS', 'T-GRIFFITH'], 'observation_ids': ['TX-RV10.71.2'],
         'witnesses': [pin('data/raw/2026-10-12-transmission-hypothesis/texts/rv10-sanskrit-v1.html'),
                       pin('data/raw/2026-10-12-transmission-hypothesis/texts/rv10071-griffith-v1.html')],
         'paired_derivative': pin('data/raw/2026-10-12-transmission-hypothesis/texts/paired-passages-v2.json'),
         'inspected': 'All11RV10.71paired stanzas; Sanskrit10.71.2 and its Griffith translation also checked in actual parent HTML.',
         'finding': 'The comparison particle iva marks a meal-sifting relation used for shaping speech. Ritual, affiliation and differentiated performance frame the hymn; practical water, thread and food imagery also occurs.',
         'limit': 'Directly represented analogy at its textual stage; no independently established Harappan operation ancestry or processor-to-poet apprenticeship.'},
    ]
    result = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Additional selected primary anchor readings in integrated branches, separate from the seven-record/six-work control frame. No whole-report or manuscript-collation claim.',
              'code_sha256': sha(Path(__file__)),
              'branch_observation_pins': {name: sha(BASE / name) for name in ['material/observations.json', 'texts/OBSERVATIONS.json']},
              'records': records,
              'independent_material_anchor_works': 4,
              'independently_viewed_material_pdf_pages': 5,
              'additional_textual_anchor': 'One complete11-stanza hymn in two editions; one lineage, not two ancient observations'}
    with path.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({'records': len(records), 'material_works': 4, 'material_pdf_pages': 5,
                      'textual_hymn_stanzas': 11}))
