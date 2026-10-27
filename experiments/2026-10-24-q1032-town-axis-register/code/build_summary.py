"""Write a readable index and acquisition manifests from the final register."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'experiments/2026-10-24-q1032-town-axis-register'
RUN=P/'run-v5'
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-q1032-town-axis-register')

def save(name,x):
    with (P/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    table=json.loads((RUN/'town-axis-table.json').read_text(encoding='utf-8'))['towns']
    ms=[json.loads(l) for l in (RUN/'measurements.jsonl').read_text(encoding='utf-8').splitlines()]
    hs=[json.loads(l) for l in (RUN/'horizons.jsonl').read_text(encoding='utf-8').splitlines()]
    parts=[json.loads(l) for l in (RUN/'chronology-parts.jsonl').read_text(encoding='utf-8').splitlines()]
    headings={'mohenjo-daro':'Mohenjo-daro','harappa':'Harappa','lothal':'Lothal','dholavira':'Dholavira','surkotada':'Surkotada'}
    text=['# Town-axis table, current endpoint run-v5',
          '', 'This is an index to source-backed observations. Bearings below are examples from individual systems, not pooled town values. Positive deviation is clockwise. Errors in the detailed tables remain reported, partial or unknown. A plan value of unspecified north is not a true-north bearing. The report explains the cross-source conflicts and the status of registration results.',
          '', '[All line and system measurements](run-v5/measurements.csv), [source joins](run-v5/sources.jsonl), [dated parts](run-v5/chronology-parts.jsonl), [radiocarbon](run-v5/radiocarbon.jsonl), [horizons](run-v5/horizons.jsonl), [field gaps](run-v5/missing-fields.csv).',
          '', '| Town | Image deviation example, degrees | Plan north references present | Modern horizon maxima W / E, degrees | Dated-part assertions | Radiocarbon assertions |',
          '|---|---|---|---|---:|---:|']
    for t in table:
        town=t['town']; mm=[m for m in ms if m['town']==town and m.get('is_current_input')]
        if town=='surkotada':image='Western IC face -11.83; southern IC face -11.60; digitizing errors about 5 degrees, total error unknown'
        elif town=='lothal':image='Dock: Esri about -1.9; Sentinel-2 about +0.2; discordant reported errors'
        elif town=='dholavira':image='Castle about -5.5 on Esri; middle-town system about -3.5 on Sentinel-2; different parts'
        else:
            candidates=[m for m in mm if m['source_kind']=='imagery' and m['level']=='system' and 'measure-img-A' in m['record']['path']]
            selected=None
            for m in candidates:
                origin=json.loads((ROOT/m['record']['path']).read_text(encoding='utf-8-sig'))
                r=origin['systems'][int(m['record']['json_pointer'].split('/')[-1])]
                if origin.get('main_system')==r.get('id'):selected=m;break
            if selected:image=f"{selected['part']}: {selected['deviation_deg']:+.2f} (one historical observer)"
            elif any(m['source_kind']=='imagery' for m in mm):image='See individual image lines; no pooled value'
            else:image='Missing; source-specific reasons retained'
        ns=sorted({str(m['north_reference']) for m in mm if m['source_kind']=='plan'})
        valid=[h for h in hs if h['town']==town and h['usable_at_corrected_site']]
        h=valid[-1] if valid else None
        horizon=f"{h['max_west_deg']:+.3f} / {h['max_east_deg']:+.3f}" if h else 'Missing or wrong-location profile excluded'
        name=headings.get(town,town.replace('-',' ').title())+(' *' if t['required'] else '')
        text.append(f"| {name} | {image} | {', '.join(ns) if ns else 'No measured plan'} | {horizon} | {len(t['dated_part_assertions'])} | {t['radiocarbon_assertions']} |")
    text+=['','An asterisk marks a required town. Horizon sectors cover azimuths 225-315 degrees west and 45-135 degrees east. These are modern DSM results with unquantified palaeohorizon errors. Counts include repeated assertions. Candidate site coordinates and their quality labels are in the CSV and JSON index; measured line endpoints remain separately referenced.']
    with (P/'TABLE.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(text)+'\n')
    h=json.loads((P/'horizon-repair-v1/horizons.json').read_text(encoding='utf-8'))
    coverage=json.loads((RUN/'coverage.json').read_text(encoding='utf-8'))
    save('manifest-additions.json',dict(schema_version='1.0',date='2026-10-24',question='Q-1032',
        proposed_sources=[dict(id='q1032-town-axis-register-2026-10-24',status='project-output',location='tracked',
            version='run-v5',path='experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json',
            sha256=hashlib.sha256((RUN/'town-axis-table.json').read_bytes()).hexdigest(),rights_status='own-work',
            fields=['town and aliases','architectural part','source and record locator','north reference','bearing and deviation','reported and partial uncertainty','coordinates with quality','horizon profiles','layout phase','radiocarbon evidence','missing-field reason'],coverage=coverage),
            dict(id='copernicus-corrected-town-horizons-2026-10-24',status='held',location='local-only',version='AWS Copernicus DEM GLO-30 and GLO-90',
                acquisition_route='Public S3 HTTPS, URLs and retrieval times retained per tile',
                rights_status='explicit-license',licence='Source-specific Copernicus DEM licence; not assigned a project licence',licence_url=h['licence_source'],
                attribution=h['attribution'],files=len(h['dem_tiles']),bytes=sum(r.get('bytes',0) for r in h['dem_tiles']),
                local_root=str(RAW/'dem'),acquisitions=h['dem_tiles'])],
        reused_sources=['Wanzke 1987 pp. 33-44','Joshi 1990 Fig. 8','Agrawal and Kusumgar 1973 pp. 574 and 579-580','three prior town studies; all input paths and hashes in run-v5/input-manifest.json'],
        additions=dict(image_lines=2,entered_published_rows=35,repaired_horizon_locations=2,new_radiocarbon_determinations=0,new_inscribed_objects=0),
        maintainers='Integrate source and coverage records after review; generated registry and MAP remain untouched.'))
    records=[]
    for p in sorted(RAW.rglob('*')):
        if not p.is_file():continue
        records.append(dict(physical_path=str(p),logical_path='data/raw/2026-10-24-q1032-town-axis-register/'+p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),handling='local-only',
                            transformation='Acquired DEM tile' if p.suffix=='.tif' else 'Local PDF render, visual-review crop or diagnostic; parents identified in source-checks.json and new-observations.json'))
    save('local-artifacts.json',dict(files=records,source_parents=['source-checks.json','new-observations.json','horizon-repair-v1/horizons.json'],
                                    note='Manifest only. No image, plan, OCR or DEM payload is distributed in the experiment.'))
    print(json.dumps(dict(table_towns=len(table),local_files=len(records),new_tiles=len(h['dem_tiles']))))

if __name__=='__main__':main()
