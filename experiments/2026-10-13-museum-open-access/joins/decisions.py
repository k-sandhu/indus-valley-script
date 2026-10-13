"""Museum join decisions, with dated post-review corrections on 13 October 2026.

The original decisions are preserved locally under
data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/.
REVIEW-CHANGES.md records the corrections; PROTOCOL.md remains the original protocol.
Evidence for restricted sources uses project classifications and saved-record locators.
"""
D = []


def add(museum, accession, source, cls, method="", family="", cisi="", spec="", cands="", evidence="", conflicts="", addition=False):
    D.append(dict(museum=museum, accession=accession, source=source, cls=cls, method=method,
                  family=family, cisi=cisi, spec=spec, cands=cands, evidence=evidence,
                  conflicts=conflicts, addition=addition))

add('Metropolitan Museum of Art', '49.40.1', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|unicorn|38|38|4|1.5|1',
    evidence='Met API object 324062: Indus Valley, no number or findspot; unicorn and standard; 4 signs read on the CC0 photograph')

add('Metropolitan Museum of Art', '49.40.2', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|unicorn|38.1|38.1|5|1.5|1',
    evidence='Met API object 324063 (impression photographed): bull with harness and standard, 5 signs read; the Met title says buffalo, and no local buffalo seal of this size exists',
    conflicts="Met title 'buffalo'; the photograph shows a single-horned bull with standard")

add('Metropolitan Museum of Art', '49.40.3', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|unicorn|38.7|38.7|6|1.5|1',
    evidence='Met API object 324064: fragment, unicorn and standard, 6 signs read')

add('Metropolitan Museum of Art', '49.40.4', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:R|none|34.4|18.6|5|1.5|1',
    evidence='Met API object 324065: bar seal without animal, 5 signs read')

add('Metropolitan Museum of Art', '1984.482', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|short-horned bull|20|20|5|1.5|1',
    evidence="Met API object 38287: 'Seal with an Ox', 2 cm, culture Pakistan, no findspot; about 5 signs read")

add('Cleveland Museum of Art', '1964.104', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|unicorn|25|25|6|1.5|1',
    cands='61;62;63;83;85;99;100;101',
    evidence="CMA API: unicorn, 2.5 x 2.5 cm, upper corner broken; provenance 'Museum of Fine Arts, Boston ... by exchange', and the MFA's Indus seals come from the 1935-36 Chanhu-daro excavation; Chanhu-daro unicorn seals of 23-27 mm: C-64 (6 signs), C-62, C-13 (5), C-12 (7), C-11 (8), C-65 (7, the Penn seal L-141-176), C-66 (4), C-63 (2); Mackay 1943 pl. LII compared by eye, not decisive at the scan's contrast")

add('Cleveland Museum of Art', '1973.160', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|short-horned bull|32|32|5|1.5|1',
    evidence='CMA API: two-horned bull, 3.2 cm, bought from W. H. Wolff; no findspot')

add('Cleveland Museum of Art', '1973.161', 'harvest', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|unicorn|35|36|6|1.5|1',
    evidence='CMA API: unicorn, 3.5 x 3.6 cm, bought from W. H. Wolff; no findspot')

add('Penn Museum', 'L-141-92', 'harvest', 'confirmed',
    method='shared_field_number_and_plate',
    family='81',
    cisi='C-78',
    evidence="Penn object page 'Other Number' and bibliography: Field No 3493; Mackay 1943 pl. LI no. 12; Lipi idno CH 3493Pl. LI:12")

add('Penn Museum', 'L-141-159', 'harvest', 'confirmed',
    method='shared_field_number_and_plate',
    family='5270',
    cisi='C-73',
    evidence="Penn object page 'Other Number' and bibliography: Field No 3495; Mackay 1943 pl. LI no. 17; Lipi idno CH 3495Pl. LI:17")

add('Penn Museum', 'L-141-160', 'harvest', 'confirmed',
    method='shared_field_number_and_plate',
    family='60',
    cisi='C-80',
    evidence="Penn object page 'Other Number' and bibliography: Field No 2000; Mackay 1943 pl. LI no. 9; Lipi idno CH 2000Pl. LI:9")

add('Penn Museum', 'L-141-176', 'harvest', 'confirmed',
    method='shared_field_number_and_plate',
    family='62',
    cisi='C-65',
    evidence="Penn object page 'Other Number' and bibliography: Field No 2428; Mackay 1943 pl. LII no. 19; Lipi idno CH 2428Pl. LII:19")

add('Penn Museum', 'L-141-177', 'harvest', 'confirmed',
    method='shared_field_number_and_plate',
    family='71',
    cisi='C-53',
    evidence="Penn object page 'Other Number' and bibliography: Field Nos 3051 and 2558; Mackay 1943 pl. LI no. 24 (and pl. LII no. 12); Lipi idno CH 3051Pl. LI:24")

add('Penn Museum', 'L-141-75', 'harvest', 'uninscribed',
    method='record states no signs',
    evidence='unfinished seal, animal only (Field No 3052; Mackay pl. LI no. 2); no CH number in Lipi')

add('Penn Museum', 'L-141-157', 'harvest', 'uninscribed',
    method='record states no signs',
    evidence='terracotta seal-amulet with incised linear pattern (Field No 1993; pl. XLIX no. 15); no CH number in Lipi')

add('Penn Museum', 'L-141-158A', 'harvest', 'uninscribed',
    method='record states no signs',
    evidence='faience bead-seal fragment, geometric (Field No 4003; pl. L no. 10); no CH number in Lipi')

add('Penn Museum', 'L-141-209A', 'harvest', 'uninscribed',
    method='record states no signs',
    evidence='stone bead-seal, geometric (Field No 1594; pl. L no. 16); no CH number in Lipi')

add('Victoria and Albert Museum', 'IS.8:1-1951', 'harvest', 'exact',
    method='museum_cites_CISI',
    family='3984',
    cisi='M-1727',
    evidence='record=O25161; accession=IS.8:1-1951; saved=data/raw/2026-10-13-museum-open-access/vam/cache/7ccfe2ba780daec352bf1024.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Bibliography locator: CISI 3.1 (2010) pp. 34, 415, M-1727; family=3984; identifier resolves to one family.')

add('Victoria and Albert Museum', 'IS.8:2-1951', 'harvest', 'impression',
    method='modern_impression_of',
    family='3984',
    cisi='M-1727',
    evidence='record=O1307023; accession=IS.8:2-1951; saved=data/raw/2026-10-13-museum-open-access/vam/cache/23f62af756206172ae01a536.body; material=steatite; object_class=sealing-or-impression; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=modern-impression. impression_of=IS.8:1-1951; family=3984; excluded from original-object joins.')

add('Victoria and Albert Museum', 'IS.8A-1951', 'harvest', 'ambiguous',
    method='descriptive',
    spec='Mohenjo-daro|SEAL:R|none|0|0|3|2|0',
    evidence='record=O25177; accession=IS.8A-1951; saved=data/raw/2026-10-13-museum-open-access/vam/cache/b935807d6191cc149737f68f.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=none; inscription_status=inscribed; originality=original. Preservation classification: fragment; descriptive candidates remain unresolved.')

add('British Museum', '1947,0416.1', 'census', 'confirmed',
    method='museum_field_number_plus_Mackay_1938_table',
    family='2364',
    cisi='M-1893',
    evidence='record=1947,0416.1; accession=1947,0416.1; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=bull; inscription_status=inscribed; originality=original. Miscellaneous number=DK 7665; Mackay 1938 vol. I p. 390 row 686C; family=2364; columns paired by entry count.',
    conflicts='museum_width_cm=3.7; size_delta_mm=1.9; museum_sign_count=5; corpus_sign_count=4; motif_classification=bull; residual count conflict retained.')

add('British Museum', '1947,0416.2', 'harvest', 'confirmed',
    method='published_Marshall_composite',
    family='2526',
    cisi='M-1662',
    evidence='record=1947,0416.2; accession=1947,0416.2; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Miscellaneous number=VS 823; Marshall 1931 vol. II p. 402 row 3; census join reproduced.')

add('British Museum', '1947,0416.3', 'harvest', 'confirmed',
    method='published_Marshall_composite',
    family='2484',
    cisi='M-1720',
    evidence='record=1947,0416.3; accession=1947,0416.3; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Miscellaneous number=HR 629; Marshall 1931 vol. II p. 402 row 53; census join reproduced.')

add('British Museum', '1947,0416.4', 'harvest', 'confirmed',
    method='published_Marshall_composite',
    family='2478',
    cisi='M-1906',
    evidence='record=1947,0416.4; accession=1947,0416.4; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=rhinoceros; inscription_status=inscribed; originality=original. Miscellaneous number=HR 5635; Marshall 1931 vol. II p. 404 row 345; census join reproduced.')

add('British Museum', '1947,0416.7', 'harvest', 'confirmed',
    method='museum_field_number_plus_Mackay_1938_table',
    family='2398',
    cisi='M-1883',
    evidence='record=1947,0416.7; accession=1947,0416.7; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=short-horned-bull; inscription_status=inscribed; originality=original. Miscellaneous number=DK 8528; Mackay 1938 vol. I p. 387 row 581; family=2398; columns paired by entry count.')

add('British Museum', '1947,0416.5', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=1947,0416.5; accession=1947,0416.5; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '1947,0416.6', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=1947,0416.6; accession=1947,0416.6; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '1947,0416.8', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=1947,0416.8; accession=1947,0416.8; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '1892,1210.1', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|SEAL:S|unicorn|24|25|6|1.5|0',
    cands='3925',
    evidence='record=1892,1210.1; accession=1892,1210.1; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Cunningham 1875; candidate=H-1048; H-1671 excluded by acquisition chronology (HARP H90-1618).')

add('British Museum', '1912,0507.1', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|SEAL:S|unicorn|0|0|0|1.5|0',
    evidence='record=1912,0507.1; accession=1912,0507.1; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Fleet 1912 fig. C; descriptive candidates remain unresolved.')

add('British Museum', '1912,0629.1', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=1912,0629.1; accession=1912,0629.1; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '122946', 'harvest', 'ambiguous',
    method='site_only',
    spec='Ur|SEAL|any|0|0|0|2|0',
    evidence='record=122946; accession=122946; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '122188', 'harvest', 'ambiguous',
    method='site_only',
    spec='Ur|SEAL|any|0|0|0|2|0',
    evidence='record=122188; accession=122188; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '122187', 'harvest', 'ambiguous',
    method='site_only',
    spec='Ur|SEAL|any|0|0|0|2|0',
    evidence='record=122187; accession=122187; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '120228', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=120228; accession=120228; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '123059', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=123059; accession=123059; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.998', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.998; accession=2013,6001.998; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.999', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.999; accession=2013,6001.999; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1000', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1000; accession=2013,6001.1000; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1005', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1005; accession=2013,6001.1005; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1007', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1007; accession=2013,6001.1007; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1013', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1013; accession=2013,6001.1013; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1043', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1043; accession=2013,6001.1043; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1044', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1044; accession=2013,6001.1044; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1052', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1052; accession=2013,6001.1052; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.1054', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.1054; accession=2013,6001.1054; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '2013,6001.3663', 'harvest', 'unmatched',
    method='no_key_reachable',
    evidence='record=2013,6001.3663; accession=2013,6001.3663; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. Object page unavailable; no field identifier accessible; no confirmed join.')

add('British Museum', '123208', 'harvest', 'exact',
    method='local_record_cites_museum_number',
    family='6000',
    cisi='BM-123208',
    evidence='record=123208; accession=123208; saved=data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/bm-collection-search-indus-seal.html; material=not-stated; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=not-stated; originality=original. family=6000; corpus key=BM-123208; production_place=Dilmun; findspot=Ur; cultural_attribution=Ur-III.',
    conflicts='museum_cultural_attribution=Ur-III; accession join retained; Indus attribution excluded.')

add('Indian Museum, Kolkata', 'N.S.6045', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2553',
    cisi='M-25',
    evidence='record=im_kol-N-S-6045-42094; accession=N.S.6045; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-N-S-6045-42094.body; material=jasper; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. CISI 1 (Joshi and Parpola 1987) p. 366 (PDF 402), row M-25; accession aliases=N.S.6045 / IM S.6045; field_number=BJ 2.')

add('Indian Museum, Kolkata', '10377/A7252/C.2803', 'census', 'confirmed',
    method='independent_review_Marshall_composite',
    family='2194',
    cisi='M-1809',
    evidence='record=im_kol-10377-A7252-C-2803-26919; accession=10377/A7252/C.2803; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-10377-A7252-C-2803-26919.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. Marshall 1931 vol. II p. 403 (PDF 54) row 199; field_number=C 2803; family=2194; CISI=M-1809; material, motif, size and level agree. Independent check of 13 October 2026 recovered the join after the package exact-match search missed the DK- prefix; verification/independent-check.csv, accession 10377/A7252/C.2803.')

add('Indian Museum, Kolkata', '10379/A7253', 'census', 'ambiguous',
    method='descriptive',
    spec='Mohenjo-daro|SEAL:S|unicorn|21|21|0|1.5|0',
    evidence='record=im_kol-10379-A7253-26894; accession=10379/A7253; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-10379-A7253-26894.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 366-370.')

add('Indian Museum, Kolkata', '10384/A7255', 'census', 'ambiguous',
    method='descriptive',
    spec='Mohenjo-daro|any|any|10|18|0|1.5|0',
    evidence='record=im_kol-10384-A7255-26922; accession=10384/A7255; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-10384-A7255-26922.body; material=steatite; object_class=seal; inscribed_faces=2; motif=not-stated; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 366-370.')

add('Indian Museum, Kolkata', '11083/A6689', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|any|any|12.7|6.4|0|1.5|0',
    evidence='record=im_kol-11083-A6689-49879; accession=11083/A6689; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-11083-A6689-49879.body; material=steatite; object_class=seal; inscribed_faces=2; motif=not-stated; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 370-372.')

add('Indian Museum, Kolkata', '11085/ A6686', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|any|any|12|7|0|1.5|0',
    evidence='record=im_kol-11085--A6686-74638; accession=11085/ A6686; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-11085--A6686-74638.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=crocodilian; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 370-372.')

add('Indian Museum, Kolkata', '11087/A6679', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|any|any|0|0|0|1.5|0',
    evidence='record=im_kol-11087-A6679-49881; accession=11087/A6679; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-11087-A6679-49881.body; material=steatite; object_class=seal; inscribed_faces=2; motif=not-stated; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 370-372.')

add('Indian Museum, Kolkata', '11089/A6700', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|any|any|0|0|0|1.5|0',
    evidence='record=im_kol-11089-A6700-49568; accession=11089/A6700; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-11089-A6700-49568.body; material=faience; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 370-372.')

add('Indian Museum, Kolkata', '11095/A6721', 'census', 'ambiguous',
    method='descriptive',
    spec='Harappa|TAB|any|0|0|0|1.5|0',
    evidence='record=im_kol-11095-A6721-49491; accession=11095/A6721; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-im_kol-11095-A6721-49491.body; material=faience; object_class=prism; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching Indian Museum registration found in CISI 1 pp. 370-372.')

add('National Museum, New Delhi', '1217', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2098',
    cisi='L-166',
    evidence='record=nat_del-1217-13177; accession=1217; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-1217-13177.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 373 (PDF 409) row L-166; registration=LTH SRG 1217; family=2098.')

add('National Museum, New Delhi', '1273', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2019',
    cisi='L-48',
    evidence='record=nat_del-1273-13184; accession=1273; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-1273-13184.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=goat; inscription_status=inscribed; originality=original. CISI 1 p. 372 (PDF 408) row L-48; registration=LTH SRG 1273; family=2019.',
    conflicts='museum_sign_count=4; corpus_sign_count=6.')

add('National Museum, New Delhi', '12906-1296', 'census', 'unmatched',
    method='published_CISI_concordance_absent_locally',
    cisi='H-224',
    evidence='record=nat_del-2906-1296-38440; accession=12906-1296; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-2906-1296-38440.body; material=copper; object_class=tablet; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 371 (PDF 407) row H-224; registration=NMI 1296; no local family; candidate addition.',
    addition=True)

add('National Museum, New Delhi', '1368/74', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2816',
    cisi='M-296',
    evidence='record=nat_del-1368-74-4817; accession=1368/74; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-1368-74-4817.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=tree-and-unicorn-heads; inscription_status=inscribed; originality=original. CISI 1 p. 368 (PDF 404) row M-296; registration=NMI 74; Marshall 1931 vol. II p. 404 row 387; family=2816.',
    conflicts='accession component 1368 remains unexplained.')

add('National Museum, New Delhi', '1713 DHR', 'census', 'uninscribed',
    method='record states no visible signs',
    evidence='record=nat_del-1713-DHR-18543; accession=1713 DHR; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-1713-DHR-18543.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=uninscribed; originality=original. Excluded from inscription scope by the saved record; surface_visibility=obscured.')

add('National Museum, New Delhi', '1860/1239', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2101',
    cisi='L-169',
    evidence='record=nat_del-1860-1239-13175; accession=1860/1239; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-1860-1239-13175.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 373 row L-169; registration=LTH SRG 1239; painted-number locator=data/lipi/public/seal_images/L-169_A.jpg; family=2101.',
    conflicts='Museum excavation identifier=1860; one-digit conflict with CISI 1 p. 373 row L-169; registration 1239 secures identity.')

add('National Museum, New Delhi', '2845', 'census', 'confirmed',
    method='published_CISI_concordance_and_label',
    family='2067',
    cisi='L-122',
    evidence='record=nat_del-2845-13183; accession=2845; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-2845-13183.body; material=stone; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 373 row L-122; registration=LTH SRG 2845; painted-number locator=data/lipi/public/seal_images/L-122_B.jpg; family=2067.',
    conflicts='Family 2067 excavation identifier points to L-100 in CISI 1 p. 373; identifier-linked material and context fields need review. museum_sign_count=5; corpus_sign_count=6.')

add('National Museum, New Delhi', '2862', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='2088',
    cisi='L-146',
    evidence='record=nat_del-2862-14019; accession=2862; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-2862-14019.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 373 (PDF 409) row L-146; registration=LTH SRG 2862; family=2088.')

add('National Museum, New Delhi', '3697-54', 'census', 'confirmed',
    method='excavation_prefix_with_attributes',
    family='2284',
    cisi='M-2053',
    evidence='record=nat_del-5697-54-42692; accession=3697-54; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-5697-54-42692.body; material=copper; object_class=tablet; inscribed_faces=2; motif=not-stated; inscription_status=inscribed; originality=original. excavation_prefix=DK 3697; family=2284 is the only prefix match; material, face count and size agree.',
    conflicts='NMI 54 to M-2053 printed link unverified; CISI 3.1 unavailable.')

add('National Museum, New Delhi', '3714', 'census', 'unmatched',
    method='no_local_family',
    evidence='record=nat_del-BNL-3714-18393; accession=3714; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-BNL-3714-18393.body; material=terracotta; object_class=seal; inscribed_faces=not-stated; motif=elephant; inscription_status=inscribed; originality=original. Banawali candidate addition; no matching elephant seal in the local corpus; CISI 1 p. 375 rows B-1 to B-37 carry no matching identifier.',
    addition=True)

add('National Museum, New Delhi', '3904', 'census', 'ambiguous',
    method='descriptive',
    spec='Banawali|SEAL|any|30|18|0|3|0',
    cands='38',
    evidence='record=nat_del-BNL-3904-18398; accession=3904; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-BNL-3904-18398.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=unicorn; inscription_status=inscribed; originality=original. candidate=B-18, family=38; identifier and photograph confirmation pending.')

add('National Museum, New Delhi', '5032/1058', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='118',
    cisi='C-37',
    evidence='record=nat_del-5032-1058-18784; accession=5032/1058; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-5032-1058-18784.body; material=terracotta; object_class=pottery; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 375 (PDF 411) row C-37; field_number=CH 5032; registration=NMI 1058; family=118.',
    conflicts='museum_dimensions_cm=15.0x9.6; one recorded corpus axis differs.')

add('National Museum, New Delhi', '75 NM-1-240-88-2512', 'census', 'ambiguous',
    method='descriptive',
    cands='2368',
    evidence='record=nat_del-75-nm-1-240-88-2512---28666; accession=75 NM-1-240-88-2512; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-75-nm-1-240-88-2512---28666.body; material=copper; object_class=other; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. candidate family=2368; publication locator=CXXXI:37; identifier and photograph confirmation pending.')

add('National Museum, New Delhi', 'BNL-1-5473', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='29',
    cisi='B-4',
    evidence='record=nat_del-BNL-5473-18391; accession=BNL-1-5473; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-BNL-5473-18391.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=two-horned-animal; inscription_status=inscribed; originality=original. CISI 1 p. 375 row B-4; field_number=BNL 5473; family=29.')

add('National Museum, New Delhi', 'BNL-1-6230', 'census', 'ambiguous',
    method='descriptive',
    cands='40',
    evidence='record=nat_del-BNL-6230-18396; accession=BNL-1-6230; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-BNL-6230-18396.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching identifier in CISI 1 p. 375 or the local corpus; candidate=B-21, family=40, from size only.',
    conflicts='Identifier disagrees with the size-compatible candidate.')

add('National Museum, New Delhi', 'DHR-22198', 'census', 'unmatched',
    method='no_local_family',
    evidence='record=nat_del-DHR-22198-18645; accession=DHR-22198; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-DHR-22198-18645.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching local excavation identifier; candidate addition.',
    addition=True)

add('National Museum, New Delhi', 'DHR-6032', 'census', 'unmatched',
    method='no_local_family',
    evidence='record=nat_del-DHR-6032-18552; accession=DHR-6032; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-DHR-6032-18552.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching local excavation identifier; candidate addition.',
    addition=True)

add('National Museum, New Delhi', 'DHR-7860', 'census', 'unmatched',
    method='no_local_family',
    evidence='record=nat_del-DHR-7860-18546; accession=DHR-7860; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-DHR-7860-18546.body; material=terracotta; object_class=sealing; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. No matching local excavation identifier; candidate addition.',
    addition=True)

add('National Museum, New Delhi', 'DK12995', 'census', 'unmatched',
    method='candidate_rejected',
    evidence='record=nat_del-DK-4920; accession=DK12995; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-DK-4920.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=tiger-grappler; inscription_status=inscribed; originality=original. CISI 1 p. 370 row H-13, family=1074, rejected on site and motif; no matching Mohenjo-daro identifier.',
    conflicts='Published candidate differs on site and motif.')

add('National Museum, New Delhi', 'DK.369.a.49', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='3042',
    cisi='M-572',
    evidence='record=nat_del-dk-369-a-49-38408; accession=DK.369.a.49; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-dk-369-a-49-38408.body; material=copper; object_class=tablet; inscribed_faces=2; motif=composite-animal; inscription_status=inscribed; originality=original. CISI 1 p. 369 (PDF 405) row M-572; registration=NMI 49; family=3042; accession interpretation recorded by the independent reviewer.',
    conflicts='Letter-or-digit ambiguity in accession; see CISI 1 p. 369 row M-572 and independent-check.csv.')

add('National Museum, New Delhi', 'dk.7237', 'census', 'unmatched',
    method='no_local_family',
    evidence='record=nat_del-dk-7237-38406; accession=dk.7237; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-dk-7237-38406.body; material=copper; object_class=tablet; inscribed_faces=not-stated; motif=goat; inscription_status=inscribed; originality=original. No matching DK 7237 identifier in the local corpus or CISI 1 Mohenjo-daro rows.')

add('National Museum, New Delhi', 'dki', 'census', 'unmatched',
    method='no_key',
    evidence='record=nat_del-dki-42695; accession=dki; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-dki-42695.body; material=copper; object_class=tablet; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. The accession supplies no numeric identifier.')

add('National Museum, New Delhi', 'SRG-989/128', 'census', 'confirmed',
    method='published_CISI_concordance_and_label',
    family='2006',
    cisi='L-29',
    evidence='record=nat_del-SRG-989-128-13187; accession=SRG-989/128; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-SRG-989-128-13187.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=goat; inscription_status=inscribed; originality=original. CISI 1 p. 372 row L-29; painted-number locator=data/lipi/public/seal_images/L-29_B.jpg; family=2006.',
    conflicts='Registration component truncated; museum_motif=goat; image_motif=unicorn; museum_sign_count=4; corpus_sign_count=5; see independent-check.csv.')

add('National Museum, New Delhi', 'VS-1026-719', 'census', 'confirmed',
    method='published_CISI_concordance',
    family='3070',
    cisi='M-614',
    evidence='record=nat_del-VS-1026-718-18785; accession=VS-1026-719; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-VS-1026-718-18785.body; material=terracotta; object_class=pottery; inscribed_faces=not-stated; motif=not-stated; inscription_status=inscribed; originality=original. CISI 1 p. 370 (PDF 406) row M-614; field_number=VS 1026; family=3070.')

add('National Museum, New Delhi', 'vs.1574.144', 'census', 'confirmed',
    method='published_Marshall_composite',
    family='2508',
    cisi='M-1919',
    evidence='record=nat_del-vs-1574-144-38328; accession=vs.1574.144; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/object-nat_del-vs-1574-144-38328.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=human-tiger-tree; inscription_status=inscribed; originality=original. Marshall 1931 vol. II p. 404 row 357; field_number=VS 1574; family=2508.')

add('Louvre', 'AO 9036', 'census', 'ambiguous',
    method='descriptive',
    spec='any|SEAL:S|tiger|25|25|5|1.5|0',
    evidence='record=cl010169734; accession=AO 9036; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/louvre-md-json.body; material=stone; object_class=seal; inscribed_faces=not-stated; motif=lion; inscription_status=inscribed; originality=original. Descriptive candidates only; identifier or photograph confirmation pending.')

add('Louvre', 'SB 5614; AS 15374', 'census', 'ambiguous',
    method='descriptive',
    spec='Susa|SEAL|any|0|0|6|2|0',
    cands='3881',
    evidence='record=cl010179441; accession=SB 5614; AS 15374; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/louvre-sb5614.body; material=serpentine; object_class=seal; inscribed_faces=not-stated; motif=bull; inscription_status=inscribed; originality=original. candidate family=3881; descriptive agreement only; identifier or photograph confirmation pending.')

add('Louvre', 'AO 6064; CCO T. 24', 'census', 'ambiguous',
    method='descriptive',
    spec='Girsu|SEAL|any|0|0|0|2|0',
    cands='5222',
    evidence='record=cl010166753; accession=AO 6064; CCO T. 24; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/louvre-ao6064.body; material=stone; object_class=seal; inscribed_faces=not-stated; motif=bull; inscription_status=inscribed; originality=original. Delaporte 1920 T. 24; candidate family=5222; identifier or photograph confirmation pending.')

add('Louvre', 'SB 2425; AS 41; CCO S. 299', 'census', 'ambiguous',
    method='descriptive',
    spec='Susa|SEAL:CY|any|0|0|0|2|0',
    cands='3882',
    evidence='record=cl010176471; accession=SB 2425; AS 41; CCO S. 299; saved=data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/louvre-sb2425.body; material=steatite; object_class=seal; inscribed_faces=not-stated; motif=bull; inscription_status=inscribed; originality=original. Delaporte 1920 S. 299; candidate family=3882; identifier or photograph confirmation pending.')

