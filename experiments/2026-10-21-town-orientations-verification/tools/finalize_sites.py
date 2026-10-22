"""Reconcile cached coordinate responses and explicitly sourced conflicts."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
from common import read_json,write_json,record,GEOD,utc
from locate_sites import TOWNS
OVERRIDES={
 'kanmer':([23+25/60+4/3600,70+51/60+48/3600],'https://www.sciencedirect.com/science/article/pii/S2352409X20303382','An ichthyoarchaeological investigation into the Harappan settlement at Kanmer in Gujarat, India (2020), site description; 23°25′04″ N, 70°51′48″ E. Wikidata point is over 10 km away.'),
 'khirsara':([23.45,69.05],'https://www.heritageuniversityofkerala.com/JournalPDF/Volume2/658-673.pdf','Nath, Kumaran and Chandra (2014), p. 658, 23°27′ N; 69°03′ E. Wikidata point conflicts with the excavators by about 38 km. Arcminute precision.'),
 'farmana':([29+2/60+22/3600,76+18/60+21/3600],'https://www.scribd.com/document/213664074/A-Report-on-Excavations-at-Farmana-2007-08','Excavators’ report, Chapter II, printed p. 4: 29°02′22″ N, 76°18′21″ E. Wikidata point conflicts with the report.'),
 'allahdino':([24.85,67.3],'https://www.scribd.com/document/1043984685/Fuls2022-Corpus-of-Indus-Inscriptions-View-Inside','Andreas Fuls, Corpus of Indus Inscriptions, sample section 3.2: longitude 67°18′, latitude 24°51′. Arcminute precision. OSM search returned an unrelated railway station and was rejected.'),
 'lakhanjo-daro':([27+43/60+27/3600,68+50/60+51/3600],'https://southasia.wisc.edu/lecture-series-archive-fall-2010-spring-2015/2011-fall-lecture-series/qasid-mallah/','Qasid Mallah, 2011 lecture abstract: 27°43′27″ N; 68°50′51″ E.'),
 'karanpura':([29+6/60+29/3600,75+5/60+50/3600],'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202013%20-%202014%20%20A%20Review.pdf','ASI, Indian Archaeology 2013–14 – A Review, Excavation at Karanpura: 29°6′29″ N; 75°5′50″ E. Alternative 2025 proceedings differ by about 300 m; remains a starting point.')
}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('raw');p.add_argument('output');a=p.parse_args();d=read_json(a.input)
    for row,spec in zip(d['sites'],TOWNS):
        slug=spec[0];dest=Path(a.raw)/'coordinates'/slug
        if row.get('wikidata') is None and (dest/'entities.json').exists():
            entities=read_json(dest/'entities.json')['entities'];q=spec[4]
            if q in entities:
                e=entities[q];cs=[c['mainsnak']['datavalue']['value'] for c in e.get('claims',{}).get('P625',[]) if c.get('rank')!='deprecated' and 'datavalue' in c['mainsnak']]
                row['wikidata']=dict(qid=q,label=e.get('labels',{}).get('en',{}).get('value',spec[1]),P625=cs,url='https://www.wikidata.org/wiki/'+q,found_by_search=True)
                if cs:row.update(coordinate_used=[cs[0]['latitude'],cs[0]['longitude']],coordinate_source='https://www.wikidata.org/wiki/'+q+'#P625',flags=[])
        if slug in OVERRIDES:
            c,url,note=OVERRIDES[slug];row['secondary_check']=dict(coordinate=c,url=url,observation=note,checked_utc=utc());row.update(coordinate_used=c,coordinate_source=url)
            if not row['flags']:row['flags'].append('Wikidata coordinate conflicts with excavator or published site coordinate')
        if row['guess'] and row['coordinate_used']:
            c=row['coordinate_used'];g=row['guess'];row['distance_from_guess_m']=GEOD.inv(g[1],g[0],c[1],c[0])[2]
            wd=row['wikidata']['P625'][0] if row['wikidata'] and row['wikidata']['P625'] else None
            row['wikidata_distance_from_guess_m']=GEOD.inv(g[1],g[0],wd['longitude'],wd['latitude'])[2] if wd else None
        row['located']=row['coordinate_used'] is not None
    d['created_utc']=utc();d['reconciled_from']=a.input
    paths={r['path'] for r in d['files']}
    # Include the cached first successful search and entity responses omitted by the interrupted attempt.
    for pth in sorted((Path(a.raw)/'coordinates').glob('*/*.json')):
        if pth.as_posix() in paths:continue
        slug=pth.parent.name
        url='https://www.wikidata.org/w/api.php' if 'osm-' not in pth.name else 'https://nominatim.openstreetmap.org/search'
        d['files'].append(record(pth,url,'explicit-license','Wikidata CC0 1.0' if 'wikidata' in url else 'OpenStreetMap ODbL 1.0',retrieved_utc=__import__('datetime').datetime.fromtimestamp(pth.stat().st_mtime,__import__('datetime').timezone.utc).isoformat(),note='Request parameters preserved in cached response and locate_sites.py'))
    d['counts']=dict(total=len(d['sites']),located=sum(r['located'] for r in d['sites']),flagged=sum(bool(r['flags']) for r in d['sites']))
    write_json(a.output,d);print(d['counts'])
if __name__=='__main__':main()
