"""Render the frozen aggregate register into human-readable tables and sources."""
import argparse
import json
from pathlib import Path

P=Path(__file__).resolve().parent

NARRATIVE='''
## The source cases have different denominators

The architectural records are authored assessments of named sequences or source limitations. Repeated prose, plan and photograph views of one addition remain one source-event group where the module can establish that identity. They are not all independent rebuilding episodes. The 18 quantities below comprise 17 lengths and one angle, including a check of a source-labelled robber-trench width. They are readings of published drawings, not new excavation surveys.

The independent arithmetic review recomputes all 18 quantities, the alternative Mackay edge and both grid fits. A separate reader inspected the Mackay scale marks and street banks. The saved reading bounds allow uncertain endpoint and scale-bar selection. Original survey error, scan distortion, line generalisation and uncertain phase combination remain additional errors without quantified distributions.

### Farmana, Kanmer and Banawali

Farmana's eastern IIA plan and central IIB plan permit local dimensions with explicit source phase assignments. The two Lane 1 labels refer to different areas. Figures 5.69 and 5.70 are western and eastern halves of the same IIB plan, so treating them as successive occupations would create artificial retention. The northern cap of compound passage 4C cuts its link to central Lane 1; the source leaves the lane open in the mapped area. Structure 3I's eastern addition has conflicting reported lengths of 1.00 m and 2.10 m, retained within one event group. Its width reading uses an interpreted original face and therefore carries a larger endpoint radius.

Kanmer's northeastern fort corner gives an angle of 88.532 degrees with a reading bound 77.810–99.254 degrees. Its short exposed arms limit precision. The printed ratio 2 cm = 5 m lacks a usable graphic bar for scale after scan resizing, so no metric wall length is reported. Counts of partly exposed rooms and structural phases remain tied to their trenches and reports rather than being multiplied into town-wide buildings.

Banawali's composite plan and the reports of a changed interior inside an inherited outline remain useful qualitative evidence. The 1983–84 and 1987–88 publications update exposure, not successive ancient occupation plans. A proposed angle was withdrawn during visual review because one selected segment lay above a curving defence band. Its original clicks and withdrawal reason remain local; no corrected angle was substituted after seeing the outcome.

### Harappa, Dholavira and Lothal

Harappa Area C, Kenoyer 1991 Figures 4.12 and 4.16, is the one grid-registered descriptive pair. Six grid controls fit each drawing; two further points per drawing were held out. The fit errors and held-out errors appear below. The registration uses no archaeological walls as controls and no flexible warp. Its common geometric window does not certify common phase exposure: the early plan exposes a narrow strip of cart tracks and the upper drawing combines street levels and encroachment. The separate HARP Trench 39N image combines Period 3B drainage and Period 3C masonry. No internal-wall denominator is available in the lower window.

Harappa's Mound ET gateway and Drain 51 sequence retains the distinction between service, passage and entry. The robber-trench reading is a useful calibration check because the report labels its width 2.18 m; it is not a street or a preserved partition. In Trench 54, robbing and later disturbance remain visible limits on any comparison of surviving masonry.

Dholavira's east and north gates show later blocks in composite plans. Their local clearances cannot date those blocks. The original East Gate north arrow points right; its selected display crop rotates 90 degrees counterclockwise to put north upward. The North Gate and well-and-tank plans have north downward. Each transformation is recorded, and none establishes true versus magnetic north. The well's drawn horizontal diameter 3.797 m differs in scope and drawing precision from the prose dimensions 4.00 m east–west and 4.25 m north–south. Both records remain available.

Lothal Figure 17 was recovered inside the held text scan after the separately requested plate set proved incomplete. It gives a Phase IV plan of Block B with named houses, passage and entrance. That recovery changes local measurement coverage but does not recover the complete earlier street network. The warehouse-associated sealing deposit has its own discovery-area plan and competing interpretations involving discard or destruction, separately mapped in the atlas.

### Mohenjo-daro as an availability control

Mackay's Plates XVI–XX preserve five relative plan states, the last combining Late Ia and II. The first rendering pass misread the scan's alternating plan and blank-back sequence; its failed renders remain local. The corrected page indices are 45,47,49,51,53. Four local First Street chords can be read and one cannot. Plate XIX retains an alternative western edge, whose estimate and combined sensitivity bounds accompany the primary reading. Different frontages, source compilation and an unmeasurable fifth chord prevent a chronological widening claim.

The acquired Green, Alam and Petrie 2026 supplement contains summary statistics and code, but no street vectors or individual house polygons. It recovers published 80% intervals for five DK-GS residential-area Ginis. Their assigned centuries belong to a published model, not independent dates for street repairs. The atlas uses them only to show the distinction between an available summary and the missing feature-level comparison. Repeated houses across phases must not be summed as independent households. The source's DGN decimal conflict between prose and table remains preserved in the earlier package.

## Positive contexts and broken date chains

The context assessments retain object or cohort identity, material, formation, deposit, named feature, phase, dating evidence and source locator. A cohort and one of its individual members can both be assessed; 32 assessments therefore do not mean 32 objects or independent use events. The source records below distinguish manufacture, original operation, reuse and secondary deposition without assigning sign meanings.

| Context | Positive observation | Link still missing |
|---|---|---|
| Harappa Trench 54, workshop 601 | Registered tablet illustration units occur with production debris in a bounded courtyard setting | A dated sequence joining construction or repair to documentary use; subsequent recipients and function |
| Harappa Trench 10E seals | Named room floor and courtyard floor/fill associations | Event-specific stratigraphy and independent repair chronology |
| Harappa Trench 9 jar H95-2661/6640-501 | Inscribed vessel reused as an installed floor sump | Dates of its separate inscription, use and installation events |
| Harappa Wall 296 tablets | A mapped 22-tablet group, including a 16-item clump | Original manufacture and use locations; deposition is secondary and later than wall construction |
| Harappa Wall 15 | Actual hearth determinations below the wall | Tablet provenience conflict between prose and caption; no dated pair joining repair and use |
| Banawali sitting room | Horned-tiger seal reported in a mud-brick-paved room | Verified registration, house subphase and independently related sample |
| Farmana S1–S6 | Named phases, areas, object types and some fastening or suspension contacts | Explicitly qualified structural associations and event-specific dates |
| Kanmer three impressions | Repeated-stamp perforated objects with published functional proposals | Held full object-to-room register and dated use context |
| Dholavira gate inlays | Ten-sign material fallen in a named gate chamber | Original mounting and emplacement date |
| Lothal sealings | Physical fastening contacts and mapped concentration | Primary application-to-deposit history, independently coded custody change and event date |

Harappa's Table 1 reports Wall 15's underlying hearth samples A-8047/AA-16461,A-8048 and A-8049. The source's first-sigma calendar ranges remain source-specific; A-8049 is flagged aberrant. The text's construction-after-about 2470 BC inference does not date the two faience tablets whose Figure 11.4/.6 captions identify Trench 7/8, wash while the prose discusses Trench 22. A laboratory date, a sample and a wall association are distinct steps, all recorded separately.

Farmana's dating appendix provides 26 AMS entries, predominantly wood, including later Gupta and Medieval material. PLD-12422 is 1390±20 BP and AD 616–666 at the source's 95.4% coverage despite its Structure 3N label. Kanmer's genuine radiocarbon publications preserve 16 AMS and nine conventional results, with repeated lab IDs and source differences kept separate. The two intrusive-rice entries retain their source-reported fourth–fifth-century AD ages. A held file named kanmer2013.pdf proves to be publisher HTML and is excluded as an unavailable full-paper route.

Lothal's six charcoal determinations name trenches, loci, depths and deposits. TF-23 relates to a mud-wall posthole above Phase IV flood debris;TF-22 comes from an ashy layer sealing Phase IIIB flood debris and a wall. None dates the SRG3 warehouse sealing deposit. Parenthesized ages in the 1963 paper use another half-life convention rather than a modern calibrated confidence interval. Dholavira's reported TL ages are broad and lack the sample-to-target-feature relation needed here. No calibrated ages were recomputed or pooled.

## Coverage and source conflicts

Dholavira's 225 inherited context rows retain 225 unique accession strings, pending physical-object identity adjudication. The usable-label predicate finds 211 stratum labels, 201 depth labels and three explicit room labels. It excludes the literal marker Unst.; counting that marker produces 213/202 instead. The separate clarification preserves the frozen data and corrects an interim explanation. Stage, pit, room and disturbed flags can overlap; they are neither percentages of primary use nor a completeness score for excavation.

The Lothal recount independently reproduces all 93 literal provenance rows. W1 is inferred by stamp comparison and W2 supplies the broad SRG3 trench, while W records the reported warehouse association. Table W35/W1=18/W2=11/O10/?19 differs from prose W35/W1=18/W2=11/O11/?17. The table denominator 93, prose category sum 92, and older 65/69-of-90 populations remain separate. No count is silently reconciled into a new physical-object total.

## What the entry audit decides

The numerical persistence effect and documentary odds ratios remain null in the results register. The present source frame has zero fully qualified persistence episodes and zero matched documentary pairs under the frozen design. Single dimensions, multiple laboratory entries and many catalogue rows cannot replace those independent units. This is a completed evidence and measurement pilot; the institutional hypotheses await the new joined data specified in TEST-DESIGN.md.

The strongest reading is selective continuity: some connections were retained or renewed while local access and buildings changed. The deciding test is a preservation-controlled comparison of complete phase windows with independently dated operational documentary contexts. Loss of the route advantage under those controls, or a documentary association wholly explained by manufacture and discard, defeats the relevant extension.
'''

def main(run):
    for n in ('RESULTS.md','SOURCES.md'):
        if (P/n).exists():raise FileExistsError('Preserve rendered narrative.')
    d=json.loads(run.read_text(encoding='utf8'))
    c=d['counts']
    text=['# Measurements and context joins','',
          f"The frozen register contains {c['measured_quantities']} plan quantities, {c['architectural_source_cases']} architectural source cases, {c['context_assessments']} context assessments and {c['date_evidence_entries']} dating entries. The six primary towns remain in the frame; Mohenjo-daro is a supplementary availability control. The {c['source_use_records']} source-use records include repeated use of the same publications and {c['distinct_source_payload_hashes']} distinct recorded payload hashes. These are separate denominators.",'',
          '## Local plan readings','',
          'All ranges are conditional reading-sensitivity bounds. They cover the saved endpoint and scale choices; unknown original survey error is additional. The complete feature names, phase attribution, source locators and north references remain in run-v1.json and the module tables.','',
          '| Quantity ID | Town and feature | Estimate and reading bound |',
          '|---|---|---|']
    for r in d['measurements']:
        lo,hi=r['reading_bound'];unit=r['unit']
        text.append(f"| {r['id']} | {r['town']}: {r['feature']} | {r['value']:.3f} {unit}; {lo:.3f}–{hi:.3f} |")
    text += ['','## Independent-grid registration','',
             '| Panel | Grid-fit RMS error | Maximum held-out error |','|---|---|---|']
    for r in d['grid_registration']['fits']:
        text.append(f"| {r['panel']} | {r['grid_fit_rmse_metres']:.4f} m; six controls | {r['held_out_max_error_metres']:.4f} m; two held-out controls |")
    text += ['','The residuals quantify fit to the printed grid, not original survey accuracy or certification of comparable exposure. Both drawings retain unknown compilation and scan errors.','',
             '## Prediction entry results','',
             '| Prediction | Qualified units and effect | Result |','|---|---|---|']
    for r in d['decisions']:
        text.append(f"| {r['claim']} | {r['eligible']}; effect unknown | {r['status']}: {r['reason']} |")
    text += ['',''.join(NARRATIVE)]
    (P/'RESULTS.md').write_text('\n'.join(text)+'\n',encoding='utf8')
    sources=['# Sources and exact locators','',
             'Source IDs are qualified by module so that an alias in one module cannot silently replace another edition. The complete source-use register retains physical and logical paths, payload hashes, source-specific access failures and reuse lineage. The bibliography below preserves every source-use record; repeats are not independent archaeological evidence. All third-party source images and their detailed derivatives remain local-only.','']
    for r in d['source_use_records']:
        title=r.get('title','Untitled source record');auth=r.get('authors','Author unrecorded')
        if isinstance(auth,list):auth='; '.join(auth)
        loc=r.get('source_locators',r.get('read_locator',r.get('locators',r.get('locator',r.get('role','See module source guide and linked context records')))))
        if not isinstance(loc,str):loc=json.dumps(loc,ensure_ascii=False)
        sources += ['## '+r['source_ref'],'',f"{auth}. {r.get('year','Date unrecorded')}. *{title}*.",'',
                    f"Read scope: {loc}",'']
        if r.get('url'):sources += [f"Source route: {r['url']}",'']
        if r.get('physical_path'):sources += [f"Local input: `{r['physical_path']}`.",'']
        sources += ['SHA-256: '+r.get('sha256','No held payload; access limit retained')+'.','',
                    'Rights: '+str(r.get('rights',r.get('rights_status','Source-specific terms; local-only')))+'.','']
    sources += ['## Measurement and map references','',
                'QGIS Documentation Team. QGIS 3.44 User Guide, Georeferencer. https://docs.qgis.org/3.44/en/docs/user_manual/managing_data_source/georeferencer.html. We use independent grid controls, a stated transformation and residual checks. The documentation supplies method guidance, not excavation accuracy.','',
                'Historic England. The Bayesian Process, in Radiocarbon Dating and Chronological Modelling. https://historicengland.org.uk/images-books/publications/radiocarbon-dating-chronological-modelling/the-bayesian-process/. We distinguish the sample, dated event and stratigraphic relation; no new Bayesian chronology was fitted.','',
                'Natural Earth. 1:110 million land polygons and public-domain terms. https://www.naturalearthdata.com/about/terms-of-use/. The regional map uses a modern land outline, with no ancient shoreline or river reconstruction. The local GeoJSON payload and hash are in geography-sources-v1.json.','',
                'Town index points are inherited from the exposed Q-1032 table and pinned by the prior atlas manifest. They locate sites at regional scale; they are not survey controls for the excavation plans.','']
    (P/'SOURCES.md').write_text('\n'.join(sources),encoding='utf8')
    print(json.dumps({'results':str(P/'RESULTS.md'),'sources':str(P/'SOURCES.md')}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
    main(parser.parse_args().run)
