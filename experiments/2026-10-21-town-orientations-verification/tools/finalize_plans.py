"""Freeze the visually inspected plan locators; retain no page renders."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,sha256,utc
from resume_storage import records
import argparse,copy
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();raw=Path(a.raw);infra=Path(a.infra)
    acquired={};aliases={}
    for p in list(infra.glob('*acquisition*.json'))+[infra/'additional-sources-v1.json']:
        for r in records(read_json(p)):acquired[str(Path(r['path']).resolve())]=r
    for p in infra.glob('duplicate-cleanup-v*.json'):
        for r in read_json(p)['deletions']:aliases[r['path']]=r.get('retained_path')
    def source(path):
        p=Path(path);key=str(p.resolve());old=acquired.get(key,{})
        target=Path(aliases.get(p.resolve().as_posix()) or path)
        r=copy.deepcopy(old);r.update(path=target.as_posix(),bytes=target.stat().st_size,sha256=sha256(target),format=target.suffix.lstrip('.'))
        if not old:raise ValueError('Missing acquisition provenance '+path)
        if target.resolve()!=p.resolve():r['retired_duplicate_path']=p.as_posix()
        return r
    def p(slug,sub):return (raw/'plans'/slug/sub/'source.pdf').as_posix()
    sources={
      'kenoyer':(p('mohenjo-daro','kenoyer-columbia'),dict(authors=['Jonathan Mark Kenoyer'],year=1997,title='Early City-States in South Asia: Comparing the Harappan Phase and Early Historic Period',container='The Archaeology of City-States: Cross-Cultural Approaches',editors=['Deborah L. Nichols','Thomas H. Charlton'],pages='51–70',publisher='Smithsonian Institution Press, Washington, D.C.',bibliographic_evidence_url='https://www.harappa.com/sites/default/files/pdf/kenoyer1997Trade%20and%20Technology%20of%20The%20Indus%20Valley.pdf')),
      'vats':(next(x['file']['path'] for x in read_json(infra/'source-acquisition-v1.json')['sources'] if '/harappa/' in x['destination']),dict(authors=['Madho Sarup Vats'],year=1940,title='Excavations at Harappa',volume='II: Plates',publisher='Manager of Publications, Delhi')),
      'mackay':(next(x['file']['path'] for x in read_json(infra/'source-acquisition-v1.json')['sources'] if '/chanhu-daro/' in x['destination']),dict(authors=['Ernest J. H. Mackay'],year=1943,title='Chanhu-daro Excavations 1935–36',series='American Oriental Series 20',publisher='American Oriental Society, New Haven')),
      'chapter':(p('surkotada','university-chapter'),dict(authors=None,year=None,title='HARAPPAN CIVILIZATION',container='Unattributed Chapter III, printed pages 39–75',publisher='University of Lucknow (web host)',identity_status='partial: author, book title and publication year are not present in the held excerpt; ASI is credited under the selected figures')),
      'surkotada':(p('surkotada','masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t'),dict(authors=['Jagat Pati Joshi'],year=1990,title='Excavations at Surkotada 1971–72 and Exploration in Kutch',series='Memoirs of the Archaeological Survey of India 87',publisher='Archaeological Survey of India, New Delhi',identity_status='1990 copyright/reprint notice on PDF page 5; title supplied by report and archive identity')),
      'bisht':(p('banawali','bisht-volume'),dict(authors=['R. S. Bisht'],year='1998–99',title='Dholavira and Banawali: Two different paradigms of the Harappan Urbis forma',container='Puratattva 29',pages='14–37',publisher='Indian Archaeological Society, New Delhi')),
      'kanmer':(p('kanmer','kharakwal'),dict(authors=['J. S. Kharakwal','Y. S. Rawat','T. Osada','L. C. Patel','Hanmukh Seth','Rajesh Meena','S. Meena','K. P. Singh','A. Hussain'],year=2011,title='Kanmer: A Multicultural Site in Kachchh, Gujarat, India',container='Changing Perceptions of Japan in South Asia in the New Asian Era: The State of Japanese Studies in India and other SAARC Countries',editor='Takao Uno',pages='355–376',publisher='International Research Center for Japanese Studies, Kyoto',identity_status='Title and authors checked on PDF page 1; container/year from bibliographic search; institutional record returned HTTP 429')),
      'fish':(p('shikarpur','deshpande2025'),dict(authors=['G. S. Abhayan','Pramod P. Joglekar','P. Ajithprasad','S. V. Rajesh','Pankaj Goyal','Brad Chase','Jeevan Kharakwal','Prabodh Shirvalkar'],year=2025,title='Ichthyoarchaeological perspectives on roles of fish and red meat during Indus Civilization in Gujarat, India',container='Frontiers in Environmental Archaeology 4:1517351',publisher='Frontiers',doi='10.3389/fearc.2025.1517351')),
      'juni':(p('juni-kuran','report2004'),dict(authors=['Shubhra Pramanik'],year='2003–2004',title='Excavation at Juni Kuran 2003-04: A Preliminary Report',container='Puratattva 34',pages='45–67',publisher='Indian Archaeological Society, New Delhi')),
      'farmana':(p('farmana','preliminary2008'),dict(authors=['Vasant Shinde','Toshiki Osada','Akinori Uesugi','Manmohan Kumar'],year=2008,title='A Report on Excavations at Farmana 2007-08',container='Linguistics, Archaeology and the Human Past, Occasional Paper 6',editors=['Toshiki Osada','Akinori Uesugi'],publisher='Indus Project, Research Institute for Humanity and Nature, Kyoto')),
      'karanpura':(p('karanpura','prabhakar2017'),dict(authors=['V. N. Prabhakar','Ravi Korisettar'],year=2017,title='Ground survey to aerial survey: methods and best practices in systematic archaeological explorations and excavations',container='Current Science 113(10)',pages='1873–1890',publisher='Current Science Association')),
      'rangpur':(p('rangpur','rao1963'),dict(authors=['S. R. Rao'],year='1962–63',title='Excavation at Rangpur and Other Explorations in Gujarat',container='Ancient India 18 & 19',pages='5–207',publisher='Archaeological Survey of India')),
    }
    plans=[]
    def add(slug,key,page,printed,fig,caption,shows,north_location,scale=True,north_class='unspecified',north_words='N',survey_year=None,notes='',region=None):
        path,citation=sources[key];f=source(path)
        plans.append(dict(id=f'{slug}-{len([x for x in plans if x["town_slug"]==slug])+1:02d}',town_slug=slug,citation=citation,source=f,local_source_path=f['path'],pdf_page=page,printed_page=printed,figure_or_plate=fig,caption_exact=caption,caption_location='Below figure' if key not in ['vats','mackay'] else 'Plate heading or internal plan title',shows=shows,north_arrow=True,scale_bar=scale,north_class=north_class,north_words_exact=north_words,north_evidence_location=north_location,north_meaning_stated=north_class in ['true','magnetic','grid'],survey_year=survey_year,survey_year_evidence='MAG. NORTH / NOV: 2ND 1935.' if survey_year else None,render_path=None,render_status='Render on demand with tools/render_plan.py; review PNGs were temporary and deleted',render_region=region,inspection_dpi=65,notes=notes))
    add('mohenjo-daro','kenoyer',7,'57','Figure 4.3','Figure 4.3. Mohenjo-daro site plan. After Jansen (1984b:figure 4.2).','Whole town, excavated areas','Arrow marked N, lower left of upper plan')
    add('harappa','vats',14,'Plate I','Plate I','THE PREHISTORIC SITE OF HARAPPA','Whole site with excavation areas','N arrow inside plan at lower left')
    add('harappa','vats',18,'Plate III','Plate III','HARAPPA MOUND F PLAN OF THE GREAT GRANARY AREA AND SECTION ON A.B.','Granary area and section','N arrow below plan, beside scale')
    add('kalibangan','chapter',11,'49','Fig. 3.7','Fig. 3.7 The site plan of Kalibangan (courtesy ASI)','Harappan settlement and entrances','Needle-like arrow at upper right, no magnetic or true label',notes='Reproduction has unresolved book and author identity. The arrow symbol alone does not resolve its reference.')
    add('lothal','chapter',8,'46','Fig. 3.1','Fig. 3.1 The site plan of Lothal (courtesy ASI)','Whole settlement','N arrow on right side of upper plan',notes='Reproduction has unresolved book and author identity.')
    add('dholavira','kenoyer',7,'57','Figure 4.4','Figure 4.4. Dholavira site plan. After Bisht (1989).','Whole town divisions','N arrow at upper right of lower plan',notes='The held preliminary report lacks a title page, and its inspected plans on PDF pages 51 and 111 have no visible north arrow.')
    add('surkotada','surkotada',41,'22','Fig. 4','Fig. 4. Sketch Plan of structures.','Citadel and residential area','N arrow at upper left in the page frame; plan is printed sideways',survey_year=None,notes='Internal title states SURKOTADA:1971-72; this dates the excavation season, not an explicit north survey.')
    add('banawali','bisht',47,'33','Fig. 1','Fig.1 Banawali Excavations','Whole settlement and fortification','N compass at upper right')
    for page,plate,caption,shows in [(364,'II','CHANHU-DARO: MOUND I','Mound I'),(366,'III','CHANHU-DARO: MOUNDS II AND III','Mounds II and III')]:
        add('chanhu-daro','mackay',page,'Plate '+plate,'Plate '+plate,caption,shows,'Compass below the plan',north_class='magnetic',north_words='MAG. NORTH\nNOV: 2ND 1935.' if page==364 else 'MAG. NORTH\nNOV 2ND 1935',survey_year=1935,notes='Compass inscription checked in a 150 dpi temporary crop. Survey date is 1935-11-02; keep raw and corrected bearings.')
    add('kanmer','kanmer',6,'360','Fig. 5','Fig. 5  Plan of Kanmer fort of Harappans','Fort walls and exposed structures','N arrow near upper left',scale=False,notes='A scale statement reads SCALE = 2CM=5M; there is no separate conventional scale bar. Calibrate two known grid marks after checking the source scale.')
    fish_caption='Plans of selected sites showing fortifications, and sampled excavation trenches. (A) Bagasra (Image Courtesy: MSU Baroda), (B) Shikarpur (Image Courtesy: MSU Baroda), (C) Kanmer (After Kharakwal et al., 2012a), (D) Kotada Bhadli (Image composed by Abhayan G.S.), and (E) Navinal (Image composed by Abhayan G.S.).'
    add('shikarpur','fish',5,'05','Figure 2B',fish_caption,'Fortification, structures and trenches','N arrow at upper right of panel B',notes='Use panel B only. Panels D and E contain commercial basemap imagery and are excluded.')
    add('gola-dhoro','fish',5,'05','Figure 2A',fish_caption,'Bagasra fortification, structures and trenches','N arrow at upper right of panel A',notes='Use panel A only. Panels D and E are excluded.')
    add('juni-kuran','juni',69,'59','Fig. 2','Fig. 2. Kuran : Drawing showing the mound & the excavated area at Kuran-2004.','Whole site, mound and excavation','Compass at upper right',notes='Printed caption checked visually; PDF page 74 has a gateway plan but no resolved north arrow and is not selected.')
    for page,printed,fig,caption in [(28,'16','11','Figures 11    Farmana    Plan of excavated features in Trench 3X (1:60)'),(31,'19','14','Figure 14    Farmana    Plan of excavated features in Trench 3A3 (1:60)'),(34,'22','17','Figure 17    Farmana    Plan of St. no. 1 in Trench 2'),(37,'25','19','Figure 19    Farmana    Plan of Structure Complex nos. 2-4 in Trench 3')]:
        add('farmana','farmana',page,printed,'Figure '+fig,caption,'Excavated architectural features','North symbol at lower or upper right of plan',north_words='N')
    add('karanpura','karanpura',10,'1882','Figure 10','Figure 10. Site layout of Karanpura showing details of different areas of excavation.','Contour and trench layout','N compass at upper right',scale=True,notes='The plan locates trenches; it does not supply resolved wall faces. Use the line art in Figure 10 only; photographic panels are excluded.')
    for page,printed,fig,cut in [(46,'33','7','RGP 3'),(58,'35','8','RGP 4'),(62,'39','10','RGP 7')]:
        add('rangpur','rangpur',page,printed,'Fig. '+fig,'FIG. '+fig,'Plan and section of '+cut,'N compass beside plan',notes='There is no descriptive caption beyond the figure number. Internal title identifies RANGPUR 1953-56 and the cutting. Separate the horizontal plan from the section.')
    towns=[]
    for s in read_json(infra/'sites-located-v1.json')['sites']:
        found=[p for p in plans if p['town_slug']==s['slug']]
        reason=None if found else ('No qualifying plan with north arrow found in the inspected report, Puratattva article and held inventory; the inventory is a monuments list' if s['slug']=='rakhigarhi' else 'No qualifying plan recovered in the held and first-run time-boxed source search; see optional-plan-search-v1.json and source notes')
        towns.append(dict(slug=s['slug'],plans=found,plan_count=len(found),north_meaning_stated_count=sum(p['north_meaning_stated'] for p in found),status='indexed' if found else 'no-plan-found',missing_reason=reason))
    write_json(infra/'plan-library-v1.json',dict(schema_version=1,created_utc=utc(),task='town-plan-library',page_number_convention='One-based PDF page; printed page recorded independently',towns=towns,source_identity_corrections=['The file named kenoyer_1998_ancient_cities.pdf contains Decipherment of the Indus script and is excluded','The file under shikarpur/deshpande2025 is Abhayan et al. 2025','The file under kuntasi/dhavalikar is the complete Recent Advances in Marine Archaeology (1991), containing a one-page Kuntasi abstract on PDF page 52, printed page 37','The held Rakhigarhi inventory is Inventory of Monuments and Sites of National Importance, a monuments list','The kalibangan/report-part2 scan is the 2020 Part II report, beginning with Chapter XI; its inspected contents do not supply a settlement plan'],render_policy='No stored plan renders; use render_plan.py on listed page, then choose the indicated panel'))
    print('plans',len(plans),'towns',sum(bool(x['plans']) for x in towns))
if __name__=='__main__':main()
