"""Write the review's proposed batch-row corrections without editing batches."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    target = (ROOT / args.output).resolve()
    if not target.is_relative_to(OWN) or target.exists():
        raise ValueError('Use a new output inside owned directory')
    records = []
    def prose_spacing(value):
        return re.sub(r'(?<=[a-z])(?=\d)|(?<=\d)(?=[A-Za-z])', ' ', value)
    def add(batch, site, fields, correction, locator, note='', checked=False):
        records.append({'id': 'B3-V6-' + str(len(records) + 1).zfill(3), 'batch': batch, 'site_or_source': site,
            'target': f'experiments/2026-10-06-evidence-census/sites-deep/{batch}/site-rows.json#site={site}' if not site.startswith('ledger:') else f'experiments/2026-10-06-evidence-census/sites-deep/{batch}/sources.json#{site[7:]}',
            'fields': fields, 'proposed_correction': prose_spacing(correction), 'primary_locator': locator,
            'review_evidence': f'review/site-check-{batch[0].upper()}.md', 'review_note': note,
            'B3_primary_rechecked': checked, 'status': 'Proposed for batch owner; original row unchanged'})
    a = 'a-pakistan-afghanistan'
    add(a, 'Chanhu-daro', ['post_cisi_assessment.latest_cisi_coverage_year', 'cisi.source_ids'],
        'Use1987 as latest verified catalogue year; CISI2 has no section. Later C51–94 edition remains unresolved, with CISI3.2 a bibliographic lead.', 'CISI1 C1–50 pp.327–343; CISI2 contents pp.iii–iv')
    add(a, 'Chanhu-daro', ['cisi.numbering_assumption'], 'Use CISI1 p.xxiv for side/inscription/view conventions; CISI2 p.434 governs another edition.', 'CISI1 pp.xxiv,365–366; C1–50 basic data pp.374–375')
    add(a, 'Chanhu-daro', ['excavation_campaigns[2]'], 'Didier2017 reports work2015–2018 and national Pakistan DOAM cooperation; separate this from the2015–17 report title.', 'Didier2017 p.969')
    add(a, 'Chanhu-daro', ['final_report.full_text_inspected'], 'Replace full-text inspection with title, preface and contents inspected; image-only body not established as read.', 'Mackay1943 PDF8,10–17; batch source scope')
    add(a, 'Chanhu-daro', ['coordinates'], 'Retain Mallah mound-A coordinates and add the reviewer-observed DOAM point as an unresolved alternative, about0.85km away.', 'Mallah2017 pp.1,5; review DOAM site6464')
    add(a, 'Chanhu-daro', ['publication_metadata.drawings'], 'Preface documents drawings, but does not establish their scale.', 'Mackay1943 pp.vi–vii')
    add(a, 'Chanhu-daro', ['name_location_evidence.location'], 'Remove Allahdino/CISI2 p.xv locator from Chanhu-daro evidence; use Mallah p.1.', 'Mallah2017 p.1; CISI2 p.xv')
    add(a, 'Chanhu-daro', ['source_ids', 'post_cisi_assessment.source_ids'], 'Include the cited RMA-CHANDIDIER in the row source list; retain no-witness access qualification.', 'review/site-check-A.md items18–19')
    add(a, 'Rappwala Ther', ['mahadevan_1977_count', 'cisi'], 'Record not listed in IM77 p.6 and CISI1/2 contents; later CISI3.x remains uninspected.', 'IM77 p.6; CISI1/2 contents', checked=True)
    add(a, 'Rappwala Ther', ['country', 'survey_candidate'], 'Qualify Pakistan/Cholistan placement: Fuls Inter-Riverine list crosses modern countries; survey number300 and Mughal p.113 unverified.', 'Fuls2022 p.26 saved capture; unopened Mughal survey lead')
    add(a, 'ledger:RAM-FULS2022', ['witnesses', 'access_scope'], 'Point to rwopen1 in web-opens.json for the35-page capture; distinguish capture from primary PDF and2022 from2023 edition.', 'review/site-check-A.md item12')
    add(a, 'ledger:RAM-FULS2023', ['opened', 'witnesses'], 'Qualify substantial-body-opened claim: no saved body witness; page498 count assertion unverified.', 'review/site-check-A.md items6,13')
    add(a, 'ledger:RAM-MUGHAL1989', ['opened', 'access_scope'], 'Mark the table snippet-only/blocked and the1989 container unverified; no opened-content witness.', 'review/site-check-A.md item14')
    add(a, 'ledger:RMA-CHANDIDIER2017;RMA-CHANDIDIER', ['opened', 'witnesses'], 'Distinguish reviewer-opened Persee page from the earlier retrieval that left no saved witness.', 'review/site-check-A.md item18')
    b = 'b-gujarat-kutch-maharashtra'
    add(b, 'Pabumath', ['holdings.observation'], 'KC is Department of Archaeology, Kuchchh Circle, Bhuj. KM denotes Kuchchh Museum.', 'CISI1 p.366 abbreviations; p.375 Pbm1')
    add(b, 'Pabumath', ['metadata_available.registration_numbers', 'metadata_available.*.scope'], 'Replace PBM034 with PBM024 and classify as excavation number; holder KC has no registration number on this row. Lipi spells the key PMB024.', 'CISI1 p.375 Pbm1', checked=True)
    add(b, 'Pabumath', ['reported_counts', 'metadata_available.material', 'excavation_campaigns'], 'Add1978–79 broken steatite inscribed seal report; do not assume identity with1980–81 seal or Pbm1.', 'IAR1978–79 p.68; IAR1980–81 p.14')
    add(b, 'Pabumath', ['local_corpus.faces_with_dimensions'], 'Declare the legacy dimension rule; positive millimetre-dimension presence gives1 face, with vertical31mm.', 'Lipi Pabumath metadata; review/site-check-B.md P7', checked=True)
    add(b, 'Pabumath', ['source_access_logs', 'province'], 'Only O26 carries Pabumath text among O03/O25/O26; add district Kutch using IAR.', 'IAR1977–78 p.21; O26')
    add(b, 'Daimabad', ['holdings.observation'], 'Replace ABD80/78 with ABD807A at Dmd6; retain ABD66,103,91,102 for other recorded entries.', 'CISI1 p.375 Dmd rows', checked=True)
    add(b, 'Daimabad', ['coordinates'], 'Retain the Uesugi point as an attributed alternative; flag14.3–14.7km displacement from other listings pending site-authority resolution.', 'Uesugi2018 Table1 row184 p.9; review gazetteer comparison')
    add(b, 'Daimabad', ['metadata_available.dimensions', 'metadata_available.registration_numbers'], 'Make availability partial on Sali-only pages; cite CISI1 p.375 for five ABD registrations and scale-bar versus measured dimensions separately.', 'Sali1986 pp.501–505,507–508; CISI1 p.375')
    add(b, 'Daimabad', ['reported_counts', 'open_problems'], 'Distinguish seven script-bearing objects from nine catalogue entries; absent Dmd2,3,6,7,9 are reported sign-bearing, while Dmd4/5 are comparative objects.', 'Sali1986 pp.504–505; CISI1 pp.352–354; review D14,D21')
    add(b, 'Daimabad', ['reported_counts locators', 'object_class', 'local_corpus.region'], 'Preserve sherd-E versus seal classification dispute; label South India as corpus region, not administrative geography; add uncounted Jorwe sign report as a lead.', 'Sali1986 pp.8,504–505; review D4,D6,D13,D21')
    add(b, 'Dholavira', ['reported_counts locators'], 'Recovered225 seals/60 sealings passage is p.233; graffiti discussion p.231, with photographs p.232. Other analysed populations retain their individual pages.', 'Mirror pagination; review/sample-recheck-AB.md finding3')
    add(b, 'ledger:DAIMABAD1986', ['witnesses'], 'Counting sentence is in O11/O23, sherd paragraphs O05; O08/O16 label is incomplete. Existing full ASI scan belongs to another package.', 'review/site-check-B.md source table')
    add(b, 'ledger:CISI32;FULS2022;CISI1;GAZETTEER2018', ['witnesses', 'access_scope', 'pages'], 'CISI32 logs O06/O13; FULS2022 CISI3.1 evidence snippet-only; actual CISI renders388–399,409–411,8; Uesugi chapter ends p.55.', 'review/site-check-B.md source table')
    c = 'c-north-india'
    add(c, 'Tarkhanewala Dera', ['mahadevan_1977_or_icit_count.main_corpus_objects'], 'Correct2 to1; saved batch sum118 becomes117 in synthesis, without changing batch aggregate.', 'IM77 p.6 / PDF17; REVIEW.md claim7', checked=True)
    add(c, 'Chandigarh', ['main_publication_metadata.dimensions'], 'Captions give unknown percentage (?%); no usable measured dimension or reliable photo scale established.', 'CISI1 p.351 Ch1–4')
    add(c, 'Chandigarh', ['reported_object_counts[0]', 'excavation_campaigns', 'main_publication_metadata.findspot', 'main_publication_metadata.stratum_or_phase', 'main_publication_metadata.registration_numbers', 'main_publication_metadata.drawings'], 'Use Pande pp.52,54 for excavation/context statements, not p.55; p.55 is PDF202 and outside listed inspected pages.', 'Pande pp.52–55; PDF197,198 unnumbered chart,200–202')
    add(c, 'Chandigarh', ['primary_and_final_publications'], 'Add IAR1970–71 as a cited but uninspected publication; later-literature absence remains untested.', 'Pande and CISI1 bibliography; review/site-check-C.md')
    add(c, 'Chandigarh and Rakhigarhi', ['mahadevan_1977_or_icit_count.limitation'], 'AppendixV pp.828–829 are present in the opened excerpt and list refs; object classes not supplied there.', 'review/site-check-C.md; IM77 AppendixV')
    add(c, 'Rakhigarhi', ['coordinates', 'coordinates.source_ids'], 'Add IAR1999–2000 p.30 third coordinate alternative; attach ASI Inventory entry33 to existing coordinate and correct ledger title/opening scope.', 'IAR1999–2000 p.30; ASI Inventory vol.I part2 entry33')
    add(c, 'Rakhigarhi', ['local_corpus.cisi_prefixes', 'local_corpus.faces_with_period_or_time'], 'Prefix counts count faces, not unique identifiers; period-or-time presence is1 face in Lipi, while inherited field counts time only.', 'Lipi site=Rakhigarhi; review/site-check-C.md', checked=True)
    add(c, 'Rakhigarhi', ['current_holding', 'reported_object_counts.lower_bound', 'main_publication_metadata.dimensions', 'alternative_spellings'], 'Retain DAH(?) uncertainty for Rgr1; catalogue entries are site minima; photo scale supports limited dimension inference; Rakhi Shahpur is a village/component name.', 'CISI1 pp.359–360,375; IAR location; review/site-check-C.md')
    add(c, 'Rakhigarhi', ['counts for pottery_graffiti, metal, other', 'post_1987_inscribed_find_documented'], 'Distinguish not examined from not located: draft Graffiti/Copper Objects chapters and later seasons were not inspected for counts.', 'Nath draft contents; review/site-check-C.md not checked')
    add(c, 'Kalibangan and Banawali', ['reported_object_counts source pages'], 'K1–65 ends p.311, not312; B1–22 ends p.346, not347. Banawali B26a addendum is p.364.', 'CISI1 plate headers; review/sample-recheck-CD.md')
    add(c, 'ledger:m77;web-2faeedf3e1e7;chandigarh_article', ['witnesses', 'title', 'opened', 'inspected'], 'IM77 table capture is live-open-04, not02; inventory entry33 supports Rakhigarhi, despite Banawali title/unopened flag; Chandigarh p.55 is PDF202.', 'review/site-check-C.md source table')
    d = 'd-finds-abroad'
    add(d, 'Susa', ['local_corpus.records[0].faces_with_period_or_time'], 'Correct period-or-time presence0 to2, or rename old0 as time-code presence.', 'Lipi Susa two faces; review/site-check-D.md S13', checked=True)
    add(d, 'Susa', ['publication_metadata.absolute_dates'], 'Record SuseIVB calendar attribution−2400 to−2100 separately from independent dating evidence.', 'Louvre record cl010176471; review S10')
    add(d, 'Susa', ['publication_metadata.photographs', 'publication_metadata.drawings'], 'Two image slots exist; media kind was not inspected, so photograph/drawing claims remain unmeasured.', 'Louvre saved record; review S11')
    add(d, 'Susa', ['source_ids', 'identity.coordinates', 'identity.province'], 'Add susa_unesco_maps to cited source lists; World Heritage coordinate is a property proxy. Khuzestan needs its own supporting source.', 'UNESCO witness call69; review S4,S6,S13')
    add(d, 'Ur', ['published_counts Gadd no.1 locator'], 'No.1 is reprint pp.5–6, not3–5.', 'Gadd1932 reprint pp.5–6; review U1')
    add(d, 'Ur', ['excavation_number U.7683'], 'Remove or mark unsupported U.7683; no source in the inspected batch contains it.', 'review/site-check-D.md U1; failed search in Gadd/witnesses')
    add(d, 'Ur', ['published_counts Gadd no.7 classification'], 'Gadd calls the sign certain; do not attribute a dispute to him. Treat cylinder inclusion consistently across Ur/Susa frames.', 'Gadd1932 reprint no.7; review U6–U7')
    add(d, 'Ur', ['local_corpus.records[0].faces_with_period_or_time'], 'Correct period-or-time presence0 to1; face3898.1 carries DynastyIII while time codes are absent.', 'Lipi Ur; review U14', checked=True)
    add(d, 'Ur', ['current_holdings', 'excavation_campaigns'], 'Gadd names Pennsylvania custody for nos.5,11,12,14,15; custody is1932 snapshot. Dated seasons in Gadd begin1925–26; start1923 not established by Gadd.', 'Gadd1932 reprint pp.4–14; review U8–U9')
    add(d, 'Ur', ['publication_metadata.drawings'], 'Gadd supplies photographs and says no inscription copies; partial drawings refer to Laursen Fig.9, so change source attribution.', 'Gadd p.18, platesI–III; Laursen p.111; review U17')
    add(d, 'Ur', ['counts_by_requested_class.inscribed_pottery_and_graffiti', 'minimum inclusion rule'], 'Add uncertain brick/pot mark candidates with Gadd qualifications; six Gulf-type specimens reproduce Laursen class list, with sign eligibility varying.', 'Gadd reprint pp.19–20; review U6–U7,U18')
    add(d, 'Ur and Dilmun', ['identity', 'count_comparison'], 'Ur face3898.1 U17649 and Dilmun face6000.1 BM123208 identify the same seal through Gadd no.16; preserve candidate physical merge and separate transcription variants.', 'Gadd reprint pp.13–14; local identifiers; review U15')
    add(d, 'Ur and Susa', ['local_corpus comparison independence'], 'Several local thickness strings reproduce Laursen Table1; record shared-source dependence as reviewer inference pending provenance confirmation.', 'review/site-check-D.md local export section')
    add(d, 'Shortughai and Gonur Depe', ['source locators'], 'CISI3.3 p.xv is PDF17, not16; Gonur Fig.115 is p.258, not259.', 'review/sample-recheck-CD.md; saved sources')
    add(d, 'Susa and Ur', ['cisi_coverage.reason'], 'Use CISI3.3 p.ix for planned3.4 scope; p.xi does not establish present publication status.', 'CISI3.3 p.ix; review/site-check-D.md S14')
    save_data = {'status': 'Proposed', 'date': '2026-10-07', 'scope': 'Corrections and qualifications from the four review/site-check files; no batch directory edited.',
                 'corrections_count': len(records), 'corrections': records,
                 'shared_coordinator_field': {'field': 'faces_with_period_or_time', 'actual_inherited_rule': 'time code only',
                    'affected_frame': 'all78 local-site-coverage labels', 'remedy': 'Rename time-only field or separately recompute period-or-time. Do not replace historical counts silently.'},
                 'manifest_note': 'Batch B/C/D file-hash manifests predate coordinator title edits; two D replay checks use stale hashes. Requires batch-owner amendment; B3 records current hashes in v6.'}
    target.write_text(json.dumps(save_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'corrections': len(records), 'output': target.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
