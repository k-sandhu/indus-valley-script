"""Recover declared source panels; preserve detailed catalogue rows locally."""
from pathlib import Path
import datetime
import hashlib
import json
import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / 'data/raw/2026-10-02-source-recovery/physical-views'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    payload = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        if path.read_text(encoding='utf8') == payload:
            return
        raise FileExistsError(path)
    path.write_text(payload, encoding='utf8')


def panel(source, page, key, bounds, observation, face, lower=None):
    path = RAW / f'{source}-pdf{page}-native.jpeg'
    if source == 'cisi1':
        pdf = ROOT / 'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
    elif source == 'private-person':
        pdf = RAW / 'frenez2018-private-person.pdf'
        path = RAW / 'private-person-figure6-native.jpg'
    else:
        pdf = RAW / 'frenez2020-mirrored-signs.pdf'
    doc = fitz.open(pdf)
    p = doc[page - 1]
    xref = p.get_images()[0][0]
    extracted = doc.extract_image(xref)
    if not path.exists():
        path.write_bytes(extracted['image'])
    original = Image.open(path)
    rgb = original.convert('RGB')
    crop = rgb.crop(bounds)
    out = RAW / f'{key}.png'
    if not out.exists():
        crop.save(out)
    return {
        'view_id': key, 'object_id': key.split('-')[0], 'source_id': source,
        'pdf_page': page,
        'printed_page': page - 36 if source == 'cisi1' else (173 if source == 'private-person' else 33),
        'figure': None if source == 'cisi1' else (6 if source == 'private-person' else 9),
        'source_face_label': face,
        'registration_basis': 'individual object caption in original publication',
        'pdf_path': pdf.relative_to(ROOT).as_posix(), 'pdf_sha256': sha(pdf),
        'xref': xref, 'parent_image_path': path.relative_to(ROOT).as_posix(),
        'parent_image_sha256': sha(path), 'parent_image_dimensions': list(original.size),
        'parent_mode': original.mode, 'source_page_bbox_points': list(p.get_image_rects(xref)[0]),
        'crop_bounds_xyxy': list(bounds), 'crop_path': out.relative_to(ROOT).as_posix(),
        'crop_sha256': sha(out), 'crop_dimensions': list(crop.size),
        'transformation': 'Pillow RGB conversion and integer crop; no resize, contrast adjustment or annotation',
        'observation': observation, 'separated_cut_lower_bound_in_selected_zone': lower,
        'complete_marked_surface': False, 'complete_object_cut_total': None,
        'same_die_match': 'not assessed', 'surface_interpretation': 'unresolved',
        'rights_status': 'pixels local-only; authored description selected'
    }


def main():
    specs = [
        (312,'L161-cisi1-A',(420,460,790,890),'A',
         'A rectangular stamp field lies below three broad curved depressions at the upper margin. The right edge and small marks remain coarse.',3),
        (312,'L162-cisi1-A',(45,760,365,1090),'A',
         'The upper margin exposes at least three curved depressions above the rectangular stamp field. The remaining edges are uneven.',3),
        (312,'L162-cisi1-B',(420,930,600,1100),'B',
         'A separate rear view exposes a mostly flat visible patch and painted registration marks. Small edge relief is poorly resolved.',None),
        (313,'L163-cisi1-A',(35,65,405,350),'A',
         'The stamp field and elephant image lie below curved depressions at the upper edge. This is an oblique front view.',3),
        (313,'L163-cisi1-C',(450,130,665,245),'C',
         'A labelled upper-side view exposes a narrow curved strip with short dark channels. It adds a side boundary and its relation to projecting ends.',None),
        (313,'L165-cisi1-A',(350,300,765,755),'A',
         'The stamp field, elephant and broad damaged upper margin are visible. The photograph supplies no secure count of short cuts.',None),
        (314,'L168-cisi1-A',(50,60,425,345),'A',
         'Two prominent curved depressions occur above the stamp field; an adjoining broken region interrupts the upper margin.',2),
        (314,'L168-cisi1-C',(465,95,665,250),'C',
         'The upper-side view exposes a narrow strip between a high left projection and a lower right end. Dark divisions remain coarse.',None),
        (318,'L190-cisi1-A123',(100,655,380,1095),'A 1–3',
         'The obverse carries three numbered impression regions separated by raised bands. A split projection remains at the lower end.',None),
        (318,'L190-cisi1-B',(510,610,685,855),'B',
         'The reverse view shows a long narrow depression beside a ridged strip. The oblique view leaves contact angles unresolved.',None),
        (318,'L190-cisi1-D',(430,845,560,1090),'D',
         'A side view follows a narrow elongated recessed strip with uneven projecting margins. A continuous pair of contact planes cannot be traced.',None),
        (318,'L190-cisi1-F',(610,850,730,1095),'F',
         'The opposite side shows parallel oblique relief and projecting margins. The scan does not expose a measurable junction angle.',None),
        (319,'L193-cisi1-A3',(30,525,365,1010),'A 3',
         'An oblique obverse panel exposes the third numbered impression and overlapping raised borders. The dark left region is poorly resolved.',None),
        (319,'L193-cisi1-A12',(360,750,765,1095),'A 1–2',
         'A second obverse panel exposes two numbered stamp regions and their overlap. Both panels are labelled A and add no labelled reverse surface.',None),
        (322,'L206-cisi1-A12',(180,530,780,1100),'A 1–2',
         'The large obverse panel exposes two numbered impressions and the margins of a broad open recess. It provides a stamp-side comparison.',None)
    ]
    views = [panel('cisi1', n, key, box, text, face, lower)
             for n,key,box,face,text,lower in specs]
    views.append(panel('private-person',14,'L190-private-person-front',(710,1030,1370,2030),
        'The labelled colour view exposes the three stamp regions, intervening ridges and split lower projection. The attachment surface is hidden.',
        'front; publication supplies no letter'))
    # These small colour panels provide archive locators, with their actual pixels retained.
    for key,box,text in [
        ('L190-mirrored-left-v2',(45,550,90,632),'A small colour oblique view exposes ridged contact relief.'),
        ('L190-mirrored-middle-v2',(90,550,145,632),'A small colour view shows broad transverse bands and the lower projection; the publication gives no face letter.'),
        ('L190-mirrored-right-v2',(145,550,200,632),'A small colour oblique view shows a narrow contact strip and projecting margins.')]:
        views.append(panel('mirrored-signs',13,key,box,text,'individual panel within labelled L190 group'))
    save(HERE/'observations-v2.json', {
        'scope': 'Newly consulted publication panels for eight fixed Lothal objects; related archive photographs may repeat earlier views.',
        'native_resolution_limit': 'CISI1 pages are about 810 × 1140 pixels; the 2020 complete montage is 481 × 681. Rendering larger adds no source detail.',
        'views': views,
        'harappa_new_registered_views': [],
        'harappa_result': 'No new individually registered target photograph acquired.'})
    # Detailed source-derived table remains local. FC is a concordance/archive key.
    rows = [
        ('L161',6013,'1830','LTH SRG 1195','HU 1261'),
        ('L162',6233,'1836','LTH SRG 1241','HU 1255'),
        ('L163',6159,'1861','LTH SRG 1207','HU 1265'),
        ('L165',6142,'1759','LTH SRG 1206','HU 1184'),
        ('L168',6165,'1868','LTH SRG 1187','HU 1250; C: ASI'),
        ('L190',6092,'1870','LTH SRG 1225','HU 1262'),
        ('L193',6178,'1888','LTH SRG 1166','HU 1216'),
        ('L206',6106,'2077','LTH SRG 1203','ASI')]
    save(RAW/'cisi1-target-basic-data.json', {'source': 'CISI1 printed 373 / PDF409',
        'column_key_source': 'printed 365–366 / PDF401–402',
        'holding_date': 1987,
        'rows': [dict(zip(['object_id','finnish_concordance','excavation_number','museum_registration','photograph_source'],row)) for row in rows],
        'key': {'LTH':'Archaeological Survey of India, Lothal Site Museum, Saragwala',
                'SRG':'Saragwala site-museum registration prefix',
                'HU':'Helsinki University, Department of Asian and African Studies, Erja Lahdenperä photograph for CISI',
                'ASI_photo':'Photograph taken by the ASI; no further source clarification'}})
    old = fitz.open(ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf')
    alt = fitz.open(RAW/'cisi1-rarebooks-scan.pdf')
    checks=[]
    for n in [312,313,314,318,319,322,409]:
        a=old.extract_image(old[n-1].get_images()[0][0])['image']
        b=alt.extract_image(alt[n-1].get_images()[0][0])['image']
        checks.append({'pdf_page':n,'printed_page':n-36,
                       'sha256_old':hashlib.sha256(a).hexdigest(),
                       'sha256_alternative':hashlib.sha256(b).hexdigest(),
                       'embedded_bytes_equal':a==b})
    save(HERE/'alternative-scan-check.json', {'old_pages':len(old),'alternative_pages':len(alt),
        'checked_pages':checks,'new_image_detail':False,
        'result':'All seven checked embedded images are identical despite different PDF hashes and page counts.'})
    print(json.dumps({'panels':len(views),'objects':len(set(v['object_id'] for v in views)),
                      'complete_marked_surfaces':sum(v['complete_marked_surface'] for v in views),
                      'alternative_image_checks':len(checks)}))


if __name__ == '__main__':
    main()
