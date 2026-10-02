"""Source-keyed observations and arithmetic for the recovered Susa packet."""
from pathlib import Path
import csv
import json

OUT = Path(__file__).resolve().parent
OLD = 'experiments/2026-10-02-connections-and-priority/regional-west'
SOURCES = {
    'A22': {'author': 'Enrico Ascalone', 'year': 2022,
            'title': 'Bronze Age Weights from Mesopotamia, Iran & Greater Indus Valley',
            'manifest': OLD+'/source-acquisition-v1.json',
            'pdf_sha256': '39e9c43c61eae694ff0d10cfb37f47b3ca7f12c42f25d2db12ec055a5d3e7efb'},
    'S11': {'author': 'Michel C. Soutzo', 'year': 1911,
            'title': 'Étude des monuments pondéraux de Suse',
            'url': 'https://archive.org/details/mmoires12franuoft',
            'pdf_sha256': '80321b8585bf064be9282eed44f7a877f2b7682ca6a10a19134af710c2bfc3f7'},
    'M03': {'author': 'Jonathan Mark Kenoyer (entry 292a,b)', 'year': 2003,
            'title': 'Art of the First Cities: The Third Millennium B.C. from the Mediterranean to the Indus',
            'url': 'https://www.metmuseum.org/met-publications/art-of-the-first-cities-the-third-millennium-bc-from-the-mediterranean-to-the-indus',
            'pdf_sha256': 'c7b019e084077b4988deced546881157b20306a5f30f9fb95096fb01808055bb'},
    'L13677': {'url': 'https://collections.louvre.fr/ark:/53355/cl010186254',
               'metadata_witness': 'data/raw/2026-10-02-connections-and-priority/regional-west/louvre-sb13677.json'},
    'L17774': {'url': 'https://collections.louvre.fr/ark:/53355/cl010188675',
               'metadata_sha256': '95c9c7ca9384749b428c854303b6bf9e14ae30a4679d77a9d9f5cd01cc374d0e'},
}

def record(key, cat, aliases, mass, graphic, a22page, plate, material, shape):
    return dict(id=key, a22_cat=cat, aliases=aliases,
                a22_mass_g=mass, a22_graphic=graphic, a22_page=a22page,
                a22_pdf_page=a22page+15, a22_plate=plate,
                a22_material=material, shape=shape,
                source_keys=['A22'], identity_join='A22 inventory assertion',
                creation_date_bce=None, deposition_date_bce=None,
                find_context=None, original_observations=[],
                missing_observation='Museum inventory concordance, dated find layer and marked-face photograph')

rows = [
    record('SB13677',224,['AS2615'],334.25,'four circles',49,5,'hematite','ovoid'),
    record('SB13323',694,['AS9546'],13.43,None,62,22,'stone','discoid'),
    record('SB17774',698,['AS5724'],27.25,None,63,22,'jasper','cuboid'),
    record('SB9342',598,['AS13821'],2459.50,'five strokes',59,16,'limestone','duck'),
    record('SB9340',603,['AS13820'],3067.00,'six strokes',59,17,'limestone','duck'),
    record('SB13748',608,['SH095373'],4940.00,'ten strokes',59,17,'limestone','duck'),
    record('SB13552',38,['AS9522'],4.00,'cross',44,1,'stone','ovoid'),
    record('SB13561',44,['AS9520'],4.17,'cross',44,1,'stone','ovoid'),
    record('SB13177',50,[],4.25,'cross',44,1,'stone','ovoid'),
    record('SB13564',669,[],3.81,'cross',62,21,'stone','pebble'),
    record('SB15535',670,[],4.15,'cross',62,21,'stone','pebble'),
]
byid={r['id']: r for r in rows}
byid['SB13677'].update(source_keys=['A22','S11','L13677'],
    identity_join='Louvre SB13677 / AS2615 and A22 cat224; S11 no2615 joined by alias',
    earliest_verified_graphic={'year':1911,'source':'S11','page':9,'pdf_page':19,'figure':8},
    image_observation='Museum photograph resolves four round cup-like depressions in one row',
    original_observations=[{'source':'S11','page':9,'pdf_page':19,'inventory':'2615',
                           'mass_g':345.0,'graphic':'four round marks',
                           'prior_interpretation':'four decashekel units; approximately 86.2 g per mark'}],
    missing_observation='Original weighing record, measurement date/method, conservation history and creation date')
byid['SB17774'].update(source_keys=['A22','L17774','M03'],
    identity_join='Louvre SB17774 / AS5724 and A22 cat698; Met292b gives SB17774',
    creation_date_bce={'museum':[2400,2100],'A22':[2500,2000],'M03':[2600,1900]},
    deposition_date_bce={'source':'M03','page':402,'pdf_page':427,'century':12},
    find_context={'museum':'Inshushinak temple funerary deposit; found in 1904',
                  'M03p401':'Acropole, foundation deposit at Inshushinak temple',
                  'M03p402':'princely funerary repository, twelfth century BCE'},
    dimensions_cm={'L17774':{'height':1.9,'length':2.8},
                   'M03p401':{'length':2.8,'width':1.9},
                   'A22':{'length':2.40,'height':2.39,'width':1.95}},
    image_observation='One published view shows banded jasper; no graphic inscription identified on the visible faces',
    missing_observation='Primary excavation deposit inventory and independently remeasured mass; full-face images')
for key,inv,mass,pages in [('SB9342','13821',2469.0,[13,41]),('SB9340','13820',2769.0,[13,49])]:
    byid[key].update(source_keys=['A22','S11'],
        identity_join='A22 links the SB inventory to the S11 numbered object; independent museum concordance missing',
        original_observations=[{'source':'S11','page':pages[0],'pdf_page':pages[0]+10,
                               'inventory':inv,'mass_g':mass,'material':'veined marble',
                               'graphic':'listed in unmarked section'},
                              {'source':'S11','page':pages[1],'pdf_page':pages[1]+10,
                               'inventory':inv,'graphic':'explicitly described as unmarked',
                               'prior_interpretation':'five mina units inferred by Soutzo'}],
        image_observation='A22 plate shows dorsal and profile views; the claimed stroke group cannot be counted from these acquired views',
        missing_observation='SB/AS concordance, all-face mark photographs, weighing logs, conservation/restoration record and creation date')
byid['SB13748']['image_observation']='A22 plate17 supplies a compressed single view; ten strokes remain unverified photographically'
byid['SB13177'].update(source_keys=['A22','S11'],
    identity_join='Unresolved: A22 cites S11 p. 11 no. 12295; original p. 11 gives 12995',
    original_observations=[{'source':'S11','page':11,'pdf_page':21,'figure':12,
                           'inventory':'12995','mass_g':4.40,'material':'blackish schist',
                           'graphic':'cross',
                           'prior_interpretation':'half-shekel inferred by Soutzo',
                           'join_to_target':'candidate only; original number differs from A22 citation'}],
    missing_observation='Museum concordance between SB 13177 and original 12995 / cited 12295; dated context and mark image')

historical_control = {'id':'S11-13855','inventory':'13855','source':'S11','page':9,'pdf_page':19,
    'mass_g':335.0,'graphic':'four strokes','material':'veined marble','shape':'ovoid',
    'creation_date_bce':None,
    'prior_interpretation':'Soutzo assigns the same four-decashekel value as 2615',
    'modern_join':'Not located by literal 13855 search in A22 extracted text',
    'missing_observation':'Modern inventory concordance and independent dated context'}

packet={'status':'source recovery; no new unit fit', 'sources':SOURCES,
        'targets':rows,'historical_control':historical_control}
(OUT/'observations.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'observations.csv').open('w',newline='',encoding='utf-8') as fh:
    fields=['id','a22_cat','aliases','a22_mass_g','a22_graphic','a22_page','a22_plate','a22_material','shape','identity_join','creation_date_bce','deposition_date_bce','missing_observation']
    writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader()
    for r in rows: writer.writerow({f:json.dumps(r[f],ensure_ascii=False) if isinstance(r[f],(dict,list)) else r[f] for f in fields})

changes=[]
for key in ['SB13677','SB9342','SB9340']:
    r=byid[key];before=r['original_observations'][0]['mass_g'];after=r['a22_mass_g']
    changes.append({'id':key,'earlier_source':'S11','later_source':'A22',
                    'earlier_mass_g':before,'later_mass_g':after,
                    'signed_change_g':after-before,
                    'percent_of_earlier_mass':100*(after-before)/before,
                    'identity_scope':r['identity_join']})
(OUT/'mass-source-audit.json').write_text(json.dumps({'method':'A22 minus S11, divided by S11 mass for percentage; catalogue measurement dates are unprovided','comparisons':changes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
