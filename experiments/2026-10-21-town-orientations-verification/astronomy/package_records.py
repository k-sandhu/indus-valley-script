"""Verify and summarise our source witnesses and horizon coverage."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *

if __name__=='__main__':
    sources=[]
    attribution=(OUT/'COPERNICUS-ATTRIBUTION-v1.txt').read_text(encoding='utf-8').splitlines()[0]
    for meta in sorted(RAW.rglob('*.source.json')):
        source=meta.with_name(meta.name[:-len('.source.json')])
        item=json.loads(meta.read_text(encoding='utf-8'))
        assert source.stat().st_size==item['bytes'] and sha(source)==item['sha256'],source
        sources.append(dict(path=str(source.relative_to(ROOT)),url=item['url'],retrieved_utc=item['retrieved_utc'],
            bytes=item['bytes'],sha256=item['sha256'],rights=item['rights'],
            effective_dem_attribution=attribution if source.suffix=='.tif' else None))
    write_json(OUT/'SOURCE-MANIFEST-v1.json','source-manifest',
        dict(sources=sources,download_count=len(sources),download_bytes=sum(s['bytes'] for s in sources),
             handling='Raw witnesses local-only. No downloaded source code was executed.',
             coverage_change='Four star records, eleven horizon profiles and nine-target predictions for eleven coordinates; no inscribed-object metadata or corpus coverage changes.'),
        inputs=[RAW/'License-COPDEM-30.pdf',RAW/'intcal20.14c'],codes=[__file__,Path(__file__).with_name('records.py')])
    summaries=[]
    profiles=sorted((OUT/'horizon').glob('*.json'))
    for p in profiles:
        h=json.loads(p.read_text())
        summaries.append(dict(slug=p.stem,lat=h['lat'],lon=h['lon'],dem_surface_m=h['dem_surface_m'],
            observer_height_asl_m=h['observer_height_asl_m'],sea_level_dip_deg=h['sea_level_dip_deg'],
            min_apparent_altitude_deg=min(h['apparent_altitude_deg']),max_apparent_altitude_deg=max(h['apparent_altitude_deg']),
            azimuth_samples=len(h['azimuth_deg']),tile_count=len(h['dem_tiles'])))
    write_json(OUT/'horizon-summary-v1.json','horizon-summary',dict(towns=summaries),
        inputs=profiles,codes=[__file__,Path(__file__).with_name('horizon.py'),Path(__file__).parent/'history/horizon-v1.py'])
    print('sources',len(sources),'download bytes',sum(s['bytes'] for s in sources),'horizons',len(summaries))
