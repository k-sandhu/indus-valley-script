"""Keep newly acquired HTML witnesses local; preserve the previously held report."""
from pathlib import Path
import hashlib
import json
import urllib.request
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/reconstruction')
SOURCES = [
    ('KENOYER-BATH', 'The Great Bath of Mohenjo-daro C', 'Jonathan Mark Kenoyer / Harappa.com', None, 'https://www.harappa.com/content/great-bath-mohenjo-daro-c', 'Caption, paragraphs 1–4'),
    ('KENOYER-HALL', 'Pillared Hall, L Area', 'Jonathan Mark Kenoyer / Harappa.com', None, 'https://www.harappa.com/indus6/pillariedhallLarea35.html', 'Slide 35 of 103, caption'),
    ('KENOYER-PLATFORM', 'Granary, SD and REM area', 'Jonathan Mark Kenoyer / Harappa.com', None, 'https://www.harappa.com/indus6/granaryandwell40.html', 'Slide 40 of 103, caption'),
    ('KENOYER-COURT', 'College Building Courtyard, SD Area', 'Jonathan Mark Kenoyer / Harappa.com', None, 'https://www.harappa.com/indus6/collegebuilding38.html', 'Slide 38 of 103, caption'),
    ('KENOYER-DISTRICTS', 'Mohenjo-daro!', 'Jonathan Mark Kenoyer / Harappa.com', None, 'https://www.harappa.com/slideshows/mohenjo-daro', 'Index captions 9, 11–12, 23–40; relative locations'),
    ('UNESCO-DHO', 'Dholavira: a Harappan City', 'UNESCO World Heritage Centre', 2021, 'https://whc.unesco.org/en/list/1645/', 'Brief synthesis; map and plan links'),
    ('UNESCO-MD', 'Archaeological Ruins at Moenjodaro', 'UNESCO World Heritage Centre', None, 'https://whc.unesco.org/en/list/138/', 'Brief synthesis; citadel and lower-town description'),
    ('RAO-1965', 'Shipping and Maritime Trade of the Indus People', 'S. R. Rao', 1965, 'https://www.penn.museum/sites/expedition/shipping-and-maritime-trade-of-the-indus-people/', 'Section Lothal: The Dock, paragraphs 1–5; Expedition 7(3)'),
]


def main():
    if not RAW.parent.parent.parent.exists():
        raise RuntimeError('D: raw storage is unavailable')
    RAW.mkdir(parents=True, exist_ok=True)
    out = []
    for sid, title, author, year, url, locator in SOURCES:
        path = RAW / (sid.lower() + '.html')
        if not path.exists():
            req = urllib.request.Request(url, headers={'User-Agent': 'Indus-research-source-record/1.0'})
            with urllib.request.urlopen(req, timeout=40) as response:
                body = response.read()
            path.write_bytes(body)
        body = path.read_bytes()
        out.append(dict(id=sid, title=title, authors=author, year=year, url=url,
                        locator=locator, accessed_utc=datetime.now(timezone.utc).isoformat(),
                        physical_path=path.as_posix(), logical_path='data/raw/2026-10-26-indus-living-atlas/reconstruction/' + path.name,
                        bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                        format='text/html', rights_status='rights-unverified',
                        handling='Raw HTML local-only; no photographs or source prose embedded in models.',
                        observed_notice='Copyright notices retained in the local HTML; no explicit open licence confirmed.',
                        new_acquisition=True))
    held = Path('D:/projects/indus_valley_script/data/raw/2026-10-21-town-orientations-verification/dating/dholavira2015.pdf')
    body = held.read_bytes()
    assert hashlib.sha256(body).hexdigest() == 'f1c23210b95c17ea68650522ca2b7f7ecd7503078d9dede6fbfec6bfe4fad374'
    out.append(dict(id='BISHT-2015-PRELIM', title='Excavations at Dholavira (1989-90 to 2004-2005)',
                    authors='R. S. Bisht', year=2015, url='https://archive.org/details/dholavirareportpreliminaryjan2015_860_K',
                    locator='Printed pp. 93, 107–110, 114–116, 138, 149–151; zero-based PDF index = printed page + 16',
                    physical_path=held.as_posix(), logical_path='data/raw/2026-10-21-town-orientations-verification/dating/dholavira2015.pdf',
                    bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), format='application/pdf', pages=938,
                    rights_status='rights-unverified', handling='Existing preliminary scan local-only. No traced source plan embedded.',
                    edition_caution='January 2015 preliminary scan; identity with final published edition remains unresolved.',
                    conflicts=['Printed p.107 table gives city length 711.10; prose on pp.93 and 107 gives 771.10. We use the repeated prose value.',
                               'Eastern reservoir p.149 reports general depth 7.20–7.50 m; 10.60 m is a limited northern probe, not uniform basin depth.'],
                    new_acquisition=False))
    record = dict(schema_version='1.0', witnesses=out, previous_studies=[
        'experiments/2026-10-24-town-axis-visual-atlas/README.md',
        'experiments/2026-10-24-q1032-town-axis-register/REPORT.md',
        'experiments/2026-10-24-shared-infrastructure-plan-test/run-v1.json'])
    target = HERE / 'SOURCES.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'sources':len(out), 'new_html_witnesses':len(SOURCES), 'raw_root':RAW.as_posix()}))


if __name__ == '__main__':
    main()
