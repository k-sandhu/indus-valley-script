"""Write new source and region registers after the frozen-draft reviews.

Authored revisions are versioned. Source observations retain acquisition depth.
No satellite scene, polygon clipping, site-discovery model or field access is inferred.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent

def write_new(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def prose_spacing(text):
    """Repair authored compressed spacing; leave source titles and IDs alone."""
    held=[]
    def keep(match):
        held.append(match.group())
        return chr(0xE000+len(held)-1)
    text=re.sub(r'\b[PRME]\d{2}\b|https?://\S+|`[^`]+`',keep,str(text))
    text=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',text)
    for i,value in enumerate(held):
        text=text.replace(chr(0xE000+i),value)
    return text

def source_from(row, sid, alias):
    authors = row.get('authors', row.get('author', row.get('institution', 'Institutional account')))
    if isinstance(authors, list):
        authors = ', '.join(authors)
    year = row.get('year')
    if year is None:
        value = row.get('online_publication_date', row.get('event_date', row.get('date', row.get('publication_date', row.get('published_date', row.get('issue_date', ''))))))
        if value:
            year = int(str(value)[:4])
        elif '2024' in alias:
            year = 2024
    witness = row.get('raw_witness')
    if witness is None and row.get('local_witness'):
        witness = dict(local_path=row['local_witness'], sha256=row['sha256'], bytes=row['bytes'])
    if witness is None and row.get('witness_record'):
        record = json.loads((ROOT / row['witness_record']).read_text(encoding='utf-8'))
        local = record.get('local_path', record.get('path'))
        if local is None:
            # Acquisition records differ; locate their saved source by prefix.
            stem = Path(row['witness_record']).name.removesuffix('.acquisition.json')
            options = [p for p in (ROOT / Path(row['witness_record']).parent).glob(stem + '.*')
                       if p.suffix in {'.html', '.pdf', '.xml'}]
            if len(options) == 1:
                local = options[0].relative_to(ROOT).as_posix()
        if local:
            p = ROOT / local
            if p.exists():
                witness = dict(local_path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
    access = row.get('access_depth', row.get('access', 'See companion source note'))
    observation = row.get('observation', row.get('finding', row.get('limitations', 'See authored companion observation.')))
    return dict(id=sid, authors=authors, year=year, title=row['title'], url=row['url'],
                access_depth=access, observation_id=sid+'-O1', locator=row.get('locator', 'See companion register'),
                observation=observation, limits=row.get('limits', row.get('limitation')),
                as_of='2026-10-11', raw_witness=witness, upstream_source_id=alias)

DESIGNS = {
 'P01': ('Classifier cluster and matched 1 km² landform cell', 'Size-stratified proposals plus random classifier-negative cells within the published footprint', 'Demote an excess-candidate hypothesis if adequately precise, equal-effort checks show no excess of phase-supported archaeology; reclassify individual natural/later targets', 'High: resolve identity and dates of published proposals', 'Uncertain: dunes, agricultural change and remote-only evidence', 'Conditional field follow-up; data concordance first'),
 'P02': ('Mound-margin transect and adjacent eligible cell', 'Known-context margins, map-negative landforms and size-matched regional proposals', 'Demote an expanded occupation-footprint prediction where adequate margin tests establish natural or different-period deposits', 'High: reconcile area definitions and buried margins', 'Documented surface archaeology; subsurface extent uncertain', 'Coordinate with existing Ganweriwala project'),
 'P03': ('Historical feature plus eligible 1 km² cell', 'Map-positive and map-negative fields matched by size/landform/prior effort', 'Demote the mapped-concentration prediction if precise blind checks show no phase-supported excess', 'High: published historical-map follow-up', 'Leveling and surface visibility vary', 'Conditional survey with local partner'),
 'P04': ('Historical feature plus eligible 1 km² cell', 'Map symbols and natural/transformed-feature controls under equal effort', 'Reject a tested archaeological-feature interpretation when adequate observation supports a natural pond/dune; demote only the Indus attribution if archaeology belongs to another period', 'High: symbol identity and survival', 'Mixed surviving and transformed features', 'Conditional survey with local partner'),
 'P05': ('Map/image-history feature and matched cell', 'Known embankments, map-positive features and equivalent map-negative fields', 'Demote a mound-history prediction if dated feature sequences support recent earthworks or adequately precise checks show no candidate excess', 'High: historical mound versus later earthwork', 'Agricultural modification uncertain by parcel', 'Archive concordance before intervention'),
 'P06': ('Flank-to-channel coring transect within an eligible 1 km² cell', 'Stable flanks, covered margins and young channel interiors; include low-prior-effort blocks after archive review', 'Demote survival of the predicted horizon only where adequate logs demonstrate scour or age-incompatible terrestrial conditions; unreached horizons remain unresolved', 'High: compare burial and erosion near dated river studies', 'Landform-dependent burial and truncation', 'Conditional paired-landform pilot'),
 'P07': ('Phase-mapped mound unit and off-mound transect', 'Size-stratified small sites and equal-effort rural transects outside mapped mounds', 'Demote a contemporaneous catchment-link prediction if independent dates show different periods or comparable off-mound effort finds no concentration at adequate sensitivity', 'High: small-site economy and unit reconciliation', 'Thin scatters and mixed phases', 'Coordinate with published rural project records'),
 'P08': ('Eligible 1 km² landform cell containing a sediment transect', 'Four preservation strata and recorded low-prior-effort subset; proposed pilot has 24 blocks, six per stratum', 'Demote a sampled preservation premise where adequate profiles show loss of the predicted target-age surface; deep/inaccessible surfaces remain unresolved', 'High: directly test survival versus poor visibility', 'Uncertain depth and survival; preserve negative cores', 'Proposed paired-landform pilot; no partner or permit secured'),
 'P09': ('Dated channel cross-section and adjoining paleosol transect', 'Historic canal controls and older/younger surfaces within a frame shared with P08', 'Demote a Bronze Age channel/settlement link if adequately constrained channel-activity and occupation intervals do not overlap; a later fill date alone can postdate channel use', 'Medium: channel-age ambiguity in an existing survey landscape', 'Relict networks may be later; target surfaces uncertain', 'Combine with P08 frame; no independent rectangle sample'),
 'P10': ('Permitted section/context and surrounding cadastral parcel', 'Surviving lower contexts, truncated sections and modern-fill process controls', 'Demote a parcel-specific intact-horizon prediction if sufficiently deep sections demonstrate complete truncation; retain inaccessible parcels as unresolved', 'High: known threatened urban archaeology', 'Upper damage documented; lower survival varies', 'Existing heritage/rescue coordination first'),
 'P11': ('Floodplain levee/backswamp sediment transect', 'Locally dated levees, young belts and scour zones separated from P18 fans', 'Demote survival in a sampled sediment unit if adequate stratigraphy documents loss of the predicted horizon or incompatible environmental history', 'Medium: broad floodplain preservation question', 'Broad regional mechanism; local chronology absent', 'Desk chronology and sediment mapping first'),
 'P12': ('Catchment cell and independently dated cemetery/habitation unit', 'Known burial catchments and comparable catchments without recorded burials', 'Demote a contemporaneous habitation-burial link when independent contexts have incompatible dates; unlocated habitation remains unresolved', 'High: existing project addresses habitation links', 'Low-relief habitation may differ from cemetery survival', 'Existing project; coordinate and avoid duplicate claims'),
 'P13': ('Fort/exterior transect and phase-specific feature', 'Later stone structures and tributary reaches without the proposed phase signal', 'Demote alias-independent discovery or extent claim when records join to Kotada, or dates separate fort and exterior phases', 'High: published alias/extent and mixed-period issue', 'Known features; full phase footprint uncertain', 'Coordinate with known Kotada investigators'),
 'P14': ('Dune/interdune landform cell sampled across seasons', 'Dry dune shoulders, wet natural depressions and low-prior-effort comparable blocks', 'Demote an ancient occupation interpretation if dated deposits support recent wetness/natural sediments or a different cultural period', 'Medium: seasonal detection and small-site mechanism', 'Ecological precedent; local ancient surfaces uncertain', 'Chronology and pilot survey first'),
 'P15': ('Estuary-margin core transect and dated terrestrial surface', 'Modern estuary deposits, natural shell beds and preserved landward margins', 'Demote a tested shoreline/occupation association if adequate dates and indicative environments do not overlap the proposed occupation', 'Medium: known local coastal environmental sequences', 'Local infill and preservation need updated chronology', 'Local chronology first; Lothal is not a local sea-level proxy'),
 'P16': ('Tributary fan/terrace cross-section and occupation context', 'Active young fans, stable interfan surfaces and local non-Indus positive controls', 'Demote Indus affiliation if dated occupation supports another tradition; demote burial at a tested profile only if adequate stratigraphy excludes the predicted surface', 'Medium: known regional sequence with burial mechanism', 'Storm flood/erosion process known; fan ages unresolved', 'Local collaboration, access and border-related feasibility unverified'),
 'P17': ('Bolan fan/interfan transect and known sequence comparator', 'Stable terraces and dated pre-Indus/local/later deposits', 'Demote an occupation attribution if its context dates to another period; demote surface survival only where adequate stratigraphy excludes its availability or shows its loss. Older substrate or younger cap alone is insufficient.', 'Medium: direct burial analogue and local-to-Indus sequence', 'Pre-Indus analogue does not date target surfaces', 'Local sequence and archive coordination first'),
 'P18': ('Piedmont fan/interfluve or spring-corridor transect; cave inventory item separately', 'Natural chert outcrops, stable map-negative interfluves and local cultural controls', 'Demote a tested Indus attribution if dated context supports local/other-period occupation; cave component requires identity, intact deposits and dates before a field target', 'High for piedmont inventory; low for cave attribution', 'Known settlement and workshops; cavity chronology unresolved', 'Existing regional missions; cave component remains Class C'),
 'P19': ('Former lagoon-margin core transect and shell context', 'Natural shell beds and comparably preserved shoreline segments', 'Demote a proposed occupation/shoreline association if calibrated, reservoir-aware contexts support different periods or geological shell deposition', 'Medium: published Las Bela evidence', 'Dunes, lagoon change and industrial loss; local age control needed', 'Chronology first; Lower Sindh is an external analogue'),
 'P20': ('Dated local sea-level indicator and paleochannel/core transect', 'Modern estuary analogues and age-incompatible sediment/surface controls', 'Demote a local habitable-shore prediction where dated elevations/environments contradict it; ambiguous limiting points remain unresolved', 'Medium: explicit recent sea-level and route research', 'Indicative meaning, tidal range and infill limit reconstruction', 'Desk chronology and existing-project concordance first'),
 'P21': ('Raised/inland coastal terrace or buried-lagoon transect; offshore surface only after age control', 'Raised terraces, modern channels, geological sonar forms and date-incompatible marine deposits', 'Demote submergence at a tested locality if dated land motion and deposits place the target surface inland/raised; unsupported acoustic identity remains unresolved', 'Medium: known coastal anchors; speculative missing surfaces', 'Uplift/progradation favor inland/raised alternatives locally; erosion and burial also matter', 'Local chronology first; border, access and marine permits unverified'),
}

def main():
    sources = json.loads((BASE/'sources-v2.json').read_text(encoding='utf-8'))
    byid = {r['id']: r for r in sources['sources']}
    byid['R01']['observation'] = 'Teaching chapter p.41 reports 1022 Mature Harappan locations and approximately 96 excavated, citing 2002 sources; 406+616 and 41+55 subtotals. Underlying inventory not traced to a common compilation with R38.'
    byid['R02']['observation'] += ' The 142 count extends Uesugi’s compilation through 2024; publisher-indexed count passage p.156.'
    byid['R08']['observation'] += ' Discussion “Villages and Towns: Mound Size Estimates” and Fig.9A identify six mounds >20 ha. These remain the source’s mound/settlement interpretations, not new field dates here.'
    byid['R10']['observation'] = '779 historical-map features were checked; 199 archaeological positives of several periods; 169 not securely linked to earlier reports; 64 additional off-map encounters. Table1 rounded percentages uniquely recover the positive integers. In 2017 smallest-feature checks stopped after ten negatives per regional grid unit; in 2018 rechecking Survey of India historical maps excluded apparent ponds/dunes before visits. These selection rules restrict transfer of checked rates.'
    byid['R10']['locator'] = 'Table1 / PDF p.15; PDF p.10 stopping rule and map review, p.11 site definition, pp.7–14 encounters'
    byid['R32']['access_depth'] = 'Full primary publisher text including Methods, Table1 and Discussion read through web tool; no valid local full-text witness'
    byid['R32']['locator'] = '§3, Table1 and §4–5; trench4km downstream; Marine20 calibration, ΔR −106±51; Table1 intervals'
    byid['R32']['observation'] = 'Local marine-to-estuarine transition around calibrated4150±230 to3625±200 BP. Table1 gives3918–4385calBP and3424–3825calBP for the relevant AMS samples, respectively. Calibration uses Marine20 and regional ΔR−106±51; approximate RSL reconstruction has tidal-elevation limitations.'
    byid['R38']['observation'] = 'Primary2002 Introduction extract reports1056 Mature locations and96excavated, citing Possehl1999AppendixA. A different historical1022total appears in R01; a common underlying compilation was not traced. Online2009 publication does not update field counts.'
    for row in sources['sources']:
        row['access_depth'] = row['access_depth'].replace('independent Codex source auditor','separate author-commissioned Codex source-check pass')

    aliases = {}
    raw = ROOT/'data/raw/2026-10-11-settlement-prospection/SUTKAGEN2026.html'
    sid = 'R48'
    sources['sources'].append(dict(id=sid, authors='Pakistan Department of Archaeology and Museums', year=None,
       title='Sutkagen-Dor', url='https://doam.gov.pk/public/sites/8639', access_depth='Full government inventory page; coordinate and topographic description inspected',
       observation_id=sid+'-O1', locator='Coordinates and location description',
       observation='Known settlement inventory at25.516666667N61.966666667E, leftbankDasht on sandstone outcrop; coordinate lies in P21. Broadinventory period label is not an independently dated ancient shoreline.',
       as_of='2026-10-11', raw_witness=dict(local_path=raw.relative_to(ROOT).as_posix(), bytes=raw.stat().st_size, sha256=hashlib.sha256(raw.read_bytes()).hexdigest())))
    aliases['SUTKAGEN'] = sid
    sid = 'R49'
    sources['sources'].append(dict(id=sid, authors='Government of Sindh, Directorate of Culture and Antiquities', year=2015,
       title='Introduction: Inventory of Cultural Property in the Province of Sindh',
       url='https://rio-heritage.org/wp-content/uploads/2016/10/introduction-inventory-of-cultural-property-in-the-province-of-sindh.pdf',
       access_depth='Primary indexed coordinate-table text read; direct PDF unavailable', observation_id=sid+'-O1',
       locator='Register by Locality, printedp.14; KaiCaves row, VolumeI/382',
       observation='KaiCaves26°18′20.1″N67°33′37.7″E, approximately26.305583N67.560472E. This locates an inventory item, not an authenticated Indus cave deposit.',
       as_of='2026-10-11', raw_witness=None))
    aliases['KAI_COORD'] = sid
    mountains = json.loads((BASE/'research/mountain-sources.json').read_text(encoding='utf-8'))
    row = next(r for r in mountains['sources'] if r['id']=='M06')
    sid = 'R50'
    sources['sources'].append(source_from(row, sid, 'M06'))
    aliases['BESENVAL'] = sid

    groups = [
      ('research/recent-update-sources.json', {'RECENT_UW2025':'MOHENJO_UW','RECENT_GREEN2026':'MOHENJO_ARCHIVE','RECENT_GUPTA2024_JAS':'LOTHAL_JAS','RECENT_GUPTA2024_JMA':'LOTHAL_MARITIME','RECENT_PARTICIPANT2026':'MOHENJO_PARTICIPANT'}),
      ('research/estimation-framework-sources.json', {'E01':'CAPTURE','E02':'MULTILIST','E03':'HETEROGENEITY','E04':'ACCUMULATION','E05':'COVERAGE'}),
      ('research/additional-anchor-sources.json', {'AP01':'MOHENJO_DALES','AP02':'RAKHI_VILLAGES','AP03':'HARAPPA_BRICKS','AP04':'MAKRAN_UPLIFT','AP05':'MAKRAN_TERRACES','AP06':'MAKRAN_DALES','AP07':'MANDA','AP08':'ROPAR','AP09':'SHORTUGAI','AP10':'KALIBANGAN_COORD','AP11':'KHAMBHAT_OFFSHORE'}),
    ]
    next_id = 51
    for path, mapping in groups:
        data = json.loads((BASE/path).read_text(encoding='utf-8'))
        for row in data['sources']:
            if not row.get('url') or not row.get('title'):
                continue  # Unretrieved preliminary report is a lead, not a read source.
            if path.endswith('recent-update-sources.json') and row['id'] not in mapping:
                continue
            alias = mapping.get(row['id'], row.get('manuscript_key', row['id']))
            sid = 'R'+str(next_id).zfill(2); next_id += 1
            sources['sources'].append(source_from(row, sid, row['id']))
            aliases[alias] = sid
    sources.update(version='v3', authored_utc=datetime.now(timezone.utc).isoformat(),
       preceding_version='sources-v2.json', revision_basis='Frozen-draft author-commissioned Codex and Claude Opus-5.5 reviews',
       review_aliases=aliases, local_witness_count=sum(bool(r.get('raw_witness')) for r in sources['sources']))
    for row in sources['sources']:
        for key in ('observation','access_depth','locator','limits'):
            if isinstance(row.get(key),str):
                row[key]=prose_spacing(row[key])
    write_new(BASE/'sources-v3.json', sources)
    write_new(BASE/'source-aliases-v3.json', aliases)

    candidates = json.loads((BASE/'candidates-v2.json').read_text(encoding='utf-8'))
    candidates['evidence_classes'] = candidates.pop('priority_classes')
    candidates.update(version='v3', preceding_version='candidates-v2.json',
      geometry_scope='Overlapping editorial regions of interest; not sampling frames, site boundaries, measured survey footprints or suitability predictions.',
      common_comparison='Fix effort and intervention limits after local method calibration and before outcome inspection. Record prior effort, size, inaccessible/undatable/negative units. Blind observers and phase assessors where practical. A negative demotes a premise only for inspected units with adequate effort, visibility, spatial coverage, depth and chronology. Unreached or inadequately dated/covered units remain unresolved; a nonsignificant difference alone does not reject concentration.',
      common_access='Current parcel access, project-data access, partner agreement and permits have not been secured. Border and marine requirements are local feasibility questions.',
      pilot_scope='Only P08/P09 has a proposed24block workload, with no statistical power claim; other efforts require local design.',
      review_basis=['Codex F1–F8','Claude F1–F18 plus §3/§7 checks'])
    for t in candidates['targets']:
        t['evidence_class'] = t.pop('priority_class')
        t['bbox_definition'] = 'Hand-drawn editorial region, rounded to0.1degrees; overlaps are partitioned by landform in any future sampling frame'
        unit, comp, demote, info, preservation, action = DESIGNS[t['id']]
        t.update(sampling_unit=unit, minimum_comparison=comp,
                 comparison_stratum=comp, falsification_test=demote,
                 effort='Equal predeclared time/area or core-depth effort within matched strata; locally calibrated and locked before outcomes',
                 blinding='Candidate/map labels concealed from observers and sample assessors where practical; access/landform cannot always be blinded',
                 demotion_rule=demote, information_value=info, preservation_assessment=preservation,
                 next_action=action, prior_effort='See source survey/project years; spatial effort register not yet acquired',
                 predicted_site_count=None, predicted_area_ha=None, predicted_artifact_total=None,
                 geographic_validation='Partial anchor containment only; exact feature coordinates/landforms/access remain unverified')
        if t['id']=='P01':
            t['name']='Cholistan study-region comparison'
            t['target']='Published Khundowala/Mulhiawala proposal cohort and matched desert landforms inside the actual classifier footprint'
            t['geographic_validation']='Editorial box extends beyond studied desert and can cross an international border; exact proposal points not verified. Clip to the source footprint before sampling.'
        if t['id']=='P08':
            t['source_ids']=['R11','R17']
            t['falsification_test']='Use the proposed paired-landform pilot; distinguish dating of substrate, cap and occupation horizon'
        if t['id']=='P06' and 'KALIBANGAN_COORD' in aliases:
            t['source_ids'].append(aliases['KALIBANGAN_COORD'])
            t['anchor_points']=[dict(name='Kalibangan published coarse point',lon=74.133333,lat=29.483333,source_id=aliases['KALIBANGAN_COORD'])]
        if t['id']=='P09':
            t['origin']='Chronology comparison within a sampling frame shared with P08'
        if t['id']=='P11':
            t['name']='Lower Indus ridge and backswamp margins'
            t['target']='Locally dated abandoned levees and backswamp margins within the editorial region'
        if t['id']=='P12':
            t['origin']='Existing field projects; coordination and catchment comparisons, not a newly identified project locality'
        if t['id']=='P14':
            t['evidence_class']='C'
            t['origin']='Published seasonal ecology precedent; ancient surfaces and attribution need local chronology'
        if t['id']=='P15':
            t['source_ids']=['R25']
            t['origin']='Known local coastal sequences; Lothal chronology is a method comparison outside this region'
        if t['id']=='P16':
            t['source_ids']=['R26','R50']
            t['missingness_mechanism']='Alluvial/tributary flood burial and erosion; fan chronology remains unestablished'
        if t['id']=='P17':
            t['target']='Fan/interfan contacts and known-sequence comparisons in the Bolan outlet'
            t['missingness_mechanism']='Alluvial burial of valley margins; regional process analogue is pre-Indus'
            t['competing_explanation']='Pre-Indus, local or later occupation, or loss of the sought horizon'
            t['comparison_stratum']='Stable terraces and dated local/pre-Indus/later deposits'
        if t['id']=='P18':
            t['name']='Kirthar piedmont, Jamshoro-western Dadu'
            t['bbox_lonlat']=[67.0,25.0,68.1,26.6]
            t['source_ids']=[s for s in t['source_ids'] if s!='R44']+['R49']
            t['target']='Piedmont fan/interfluve and spring-corridor comparisons; Kai cave inventory/chronology is a separate Class C question'
            t['component_classes']={'piedmont':'B','cave_identity_and_chronology':'C'}
            t['anchor_points']=[dict(name='Ghazi Shah',lon=67.464134722,lat=26.454762389,source_id='R41'),dict(name='Kai Caves inventory',lon=67.560472,lat=26.305583,source_id='R49')]
        if t['id']=='P20':
            t['source_ids'] += [aliases['LOTHAL_JAS'],aliases['LOTHAL_MARITIME']]
        if t['id']=='P21':
            t['source_ids']=['R48']+[aliases[k] for k in ['MAKRAN_DALES','MAKRAN_UPLIFT'] if k in aliases]
            t['name']='Makran Dasht-Sutkagen Dor to Pasni coast'
            t['origin']='Known coastal settlement anchor and local uplift evidence; Kech/Las Bela are external regional analogues'
            t['missingness_mechanism']='Coast advance through uplift/progradation, erosion and sediment cover; local submergence remains a rival needing evidence'
            t['target']='Dated raised/inland terrace and buried-lagoon margins; offshore only if a preserved target-age surface is established'
            t['anchor_points']=[dict(name='Sutkagen-Dor',lon=61.966666667,lat=25.516666667,source_id='R48')]
        for key,value in list(t.items()):
            if isinstance(value,str):
                t[key]=prose_spacing(value)
    write_new(BASE/'candidates-v3.json', candidates)
    print(json.dumps(dict(sources=len(sources['sources']), local_witnesses=sources['local_witness_count'], regions=len(candidates['targets']), aliases=aliases)))

if __name__=='__main__':
    main()
