import json
from pathlib import Path

ROOT=Path(r'C:\Users\sandh\OneDrive\Projects\indus_valley_script')
OWN=ROOT/'experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan'
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan'
queries=json.loads((OWN/'revision-afghan-minor-searches.json').read_text(encoding='utf-8'))
first=json.loads((OWN/'first-pass/site-rows.json').read_text(encoding='utf-8-sig'))
first=first['sites'] if isinstance(first,dict) else first
names=['Shortughai','Mundigak','Nuhato','Naru-Waro-dharo','Bakkar Buthi','Gharo Bhiro','Wattoowala','Rappwala Ther','Guddal A','Derawar Ther','Rajanpur']
sources=[]
def src(id,title,authors,year,venue,url,scope,locators,opened=True,reuse='No explicit reuse licence located; raw payload remains local.'):
 sources.append(dict(id='RAM-'+id,title=title,authors=authors,year=year,venue=venue,url=url,opened=opened,access_scope=scope,locators=locators,reuse=reuse,access_date='2026-10-07'))
src('CISI2','Corpus of Indus Seals and Inscriptions. 2: Collections in Pakistan',['Sayid Ghulam Mustafa Shah','Asko Parpola'],1991,'Annales Academiae Scientiarum Fennicae B 240, Helsinki','https://archive.org/download/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan/Corpus%20of%20Indus%20Seals%20and%20Inscriptions.%20Collections%20in%20Pakistan_text.pdf','Full 486-page PDF acquired by coordinator; assigned site plates and basic data visually inspected.',['p.iv/PDF7 TOC; p.xv/PDF18 Gharo Bhiro (Nuhato); pp.xvii–xviii/PDF20–21 Naru; p.392/PDF427 Grb1; p.406/PDF441 Nwd1–3; pp.434,447/PDF469,482 owner key and basic data'],'True'=='True','Copyright1991 Finnish Academy for volume and object owners for photographs, copyright leaf/PDF5; no open licence.')
src('CISI33','Corpus of Indus Seals and Inscriptions. Volume 3: New material, untraced objects, and collections outside India and Pakistan. Part 3: Indo-Iranian Borderlands (Eastern Iran, Turkmenistan, Tajikistan, Uzbekistan, Afghanistan)',['Asko Parpola (editor)','Petteri Koskikallio (editor)'],2022,'Humaniora 386, Finnish Academy of Science and Letters, Helsinki','https://www.vorderas-archaeologie.uni-muenchen.de/personen/wiss_mitarbeiter/kaniuth/publikationen/kaniuth-shaydullaev2022sapalli.pdf','71-page selected-pages PDF: prefatory matter and selected chapter. Shortughai object plates and basic data absent.',['TOC pp.vii–viii; preface pp.x,xii,xv; Shortughai chapter introduction listed lxxviii–lxxxi, plates509–523, basicdata676–683; Mundigak supplement528'],'True'=='True','Copyright2022 Finnish Academy for volume, photographers/object owners for images, p.iv. Selected excerpt is public; no open licence.')
src('FULS2023','A Catalog of Indus Signs',['Andreas Fuls'],2023,'Mathematica Epigraphica 4, Berlin, independently published; ISBN9798398422306','https://www.researchgate.net/publication/373522673_A_Catalog_of_Indus_Signs','Substantial catalogue body opened, including site list and definition of its bracketed numbers.',['p.498 section5.3 regional site list and legible-sign-occurrence unit'],'True'=='True','All rights preserved, copyright leaf; ResearchGate says uploaded author content may be subject to copyright.')
src('FULS2022','Corpus of Indus Inscriptions',['Andreas Fuls'],2022,'Mathematica Epigraphica 3, Berlin, independently published; ISBN9781671804869','https://www.researchgate.net/publication/373522666_Corpus_of_Indus_Inscriptions','35-page body preview and selected later indices. Bakkar Buthi body p.30 inspected; most assigned site bodies outside preview.',['p.30 section3.5 Bakkar Buthi, ICIT18; TOC pp.v–vi other site pages; pp.25–26 regional labels'],'True'=='True','All rights preserved, copyright leaf. No open licence.')
src('DAFA-S','Shortugaï',['Délégation Archéologique Française en Afghanistan'],None,'DAFA institutional site-history page','https://www.dafa-afgh.org/recherche/les-operations-de-terrain-entre-1922-et-1982/shortugai/','Full institutional page opened.',['section Recherches archéologiques; bibliography; web lines58–67'])
src('DAFA-M','Mundigak',['Délégation Archéologique Française en Afghanistan'],None,'DAFA institutional site-history page','https://www.dafa-afgh.org/mundigak/','Full institutional page opened.',['campaign history and location, web lines58–64; bibliography line69 gives conflicting volume number'])
src('GAZ-PK','インダス考古学の展望　インダス文明関連発掘遺跡集成: 第3章 パキスタンのインダス文明遺跡',['上杉彰紀 (Akinori Uesugi)'],2010,'Research Institute for Humanity and Nature, Indus Project; ISBN9784902325461','https://chikyu.repo.nii.ac.jp/record/378/files/IndusKoukogakunotenbouNo4804.pdf','Full Pakistan chapter pp.95–134 downloaded through requests; web fetch failed. Naru entry inspected.',['p.116/PDF22 Naru Waro Dharo; coordinates attributed Possehl1999:801–802'],True,'Repository permits internet viewing; no open reuse licence established. Images include individual copyright credits.')
src('GAZ-AF','インダス考古学の展望　インダス文明関連発掘遺跡集成: 第4章 アフガニスタンのインダス文明遺跡',['上杉彰紀 (Akinori Uesugi)'],2010,'Research Institute for Humanity and Nature, Indus Project; ISBN9784902325461','https://chikyu.repo.nii.ac.jp/record/379/files/IndusKoukogakunotenbouNo4805.pdf','Full four-page Afghanistan chapter downloaded and inspected; repository HTML429.',['p.136/PDF2 Mundigak; p.138/PDF4 Shortughai; NDL chapter record https://ndlsearch.ndl.go.jp/books/R000000025-I010410002278133'],True,'Repository permits internet viewing; photographs credited R.Besenval/DAFA; no open reuse licence established.')
src('FRANCFORT1989','Fouilles de Shortugaï. Recherches sur l’Asie centrale protohistorique',['Henri-Paul Francfort'],1989,'Mémoires de la Mission archéologique française en Asie centrale II, two volumes, Paris: de Boccard','https://catalogue.bnf.fr/ark:/12148/cb366410725','BnF bibliographic record opened; full report not obtained.',['BnF title/publication record; RAM-DAFA-S bibliography'])
src('CASAL1961','Fouilles de Mundigak',['Jean-Marie Casal'],1961,'Mémoires de la Délégation archéologique française en Afghanistan XVII, two volumes, Paris: C.Klincksieck','https://editions.efa.gr/?id=1081&r=publication','Official publisher bibliographic record opened; report body not obtained.',['publisher volume17 record; RAM-DAFA-M bibliography incorrectly saysXVI'])
src('CISI32','Corpus of Indus Seals and Inscriptions: 3.2 Shahr-i Sokhta; Mundigak; Mehrgarh, Nausharo, Sibri, Dauda-damb; Chanhudaro; Ahar, Balathal, Gilund; Kalibangan; Rojdi',['Asko Parpola (editor)','B.M. Pande (editor)','Petteri Koskikallio (editor)'],2019,'Humaniora383, Finnish Academy of Science and Letters, Helsinki','https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-32-shahr-i-sokhta-mundigak','Official bibliographic record reopened7October; exact title repaired. Mundigak catalogue body unavailable.',['title, year, editors; 432pages'])
src('MUGHAL1972','Explorations in Southern Sind',['M. Rafique Mughal'],1972,'Pakistan Archaeology8:133–137','https://rafiquemughal.com/wp-content/uploads/2022/01/MUGHAL_1972_In-Pakistan-PakArch8.pdf','Substantial primary report opened; Gharo Bhiro description and table inspected.',['p.133 survey leadership and Sept–Oct1972; p.134 site97 description; p.137 site table'])
src('SINDH2019','Sindh Antiquities – Bi-annual journal, Vol.5 – No.1, 2019',['Zahida Quadri (editorial)','Qasid Hussain Mallah (excavation investigator)'],2019,'Culture, Tourism and Antiquities Department, Government of Sindh','https://saj.sindhculture.gov.pk/index.php/archives/15-sindh-antiquities-bi-annual-journal-vol-5-no-1-2019','Issue landing page and editorial opened; report download failed404 viarequests and500 webredirect.',['editorial refers to2018 Nuhato excavation; Drive file1jUadiydHWZRnDqUQVmpGOrLWsIbWcFzM inaccessible'])
src('DAWN-NUHATO','HERITAGE: IN SEARCH OF MELUHHA',['Ali Bhutto'],2024,'Dawn, 8September2024','https://www.dawn.com/news/1857508','Substantial secondary feature opened; limited derived use.',['Nuhato fieldwork passage'],True,'No reuse licence located; web tool source budget25words; no quotation used.')
src('BALOCH1973','In search of the Indus culture sites in Sind',['N.A. Baloch'],1973,'Bulletin of the Institute of Sindhology, University of Sind3(2–3):11–19, map, sixplates','https://archive.org/download/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan/Corpus%20of%20Indus%20Seals%20and%20Inscriptions.%20Collections%20in%20Pakistan_text.pdf','Original not obtained; bibliographic citation and reproduced seal inspected in CISI2.',['CISI2 p.xv note14; p.447 credits plate3a'],False)
src('BALOCH2004','Sindh: Studies Cultural',['N.A. Baloch'],2004,'Publisher not established in inaccessible PDF','https://library-sindhi-sp-2020.s3.us-east-2.amazonaws.com/files/Sindh_Studies_Cultural-N_A_Baloch-2004-cs.pdf','Search snippet only; web and requests downloads403.',['snippet discussing Nuhato seal and plateIII'],False)
src('BIAGI2024','Exploitation, Transport, and Circulation of the Rohri Hills Chert (Sindh, Pakistan) during the Indus Period',['Paolo Biagi'],2024,'Heritage7:4249–4264; DOI10.3390/heritage7080200','https://iris.unive.it/retrieve/999adae2-39cb-44d2-8319-54561bc05328/heritage%20PB%202024.pdf','Full article PDF acquired and opened.',['p.4254/PDF6 Naru1955 excavations; p.4262 reference50'],True,'Creative Commons Attribution4.0, article footer.')
src('NARU1964','Excavations at Naru Waro Dharo',['Department of Archaeology (gazetteer attribution)','F.A. Khan (Biagi2024 attribution)'],1964,'Pakistan Archaeology1:43–44','https://iris.unive.it/retrieve/999adae2-39cb-44d2-8319-54561bc05328/heritage%20PB%202024.pdf','Bibliographic citation inspected; original two-page report not obtained.',['RAM-GAZ-PK p.116; RAM-BIAGI2024 reference50; CISI2 p.xviii note35 citesp44'],False)
src('HARAPPA-BB','Archaeology of Ancient Balochistan',['Ute Franke-Vogt'],None,'Harappa.com excavation slideshow','https://www.harappa.com/slideshows/archaeology-ancient-balochistan','Primary investigator slideshow introduction opened.',['Bakkar Buthi1998 excavations and building phases'])
src('HARAPPA-BB-POT','Red-slipped pedestal with inscription',['Ute Franke-Vogt (photograph/investigator)'],None,'Harappa.com slide','https://www.harappa.com/slide/red-slipped-pedestal-inscription','Primary excavation photograph and caption opened.',['caption Bakkar Buthi sectionA,l.1–4'],True,'Photograph copyright credit retained; no open licence located.')
src('PU2011','UNESCO-sponsored workshop on “Significance of Pottery in Archaeological Studies” begins at PU',['University of the Punjab'],2011,'Institutional news,19December2011','https://pu.edu.pk/home/section/workshops/1080','Primary institutional announcement opened.',['web lines80–84 project and Wattowala seal; planned teachingmuseum statement'])
src('DAWN-W','Rare Indus seal discovered in Cholistan',['Mansoor Malik'],2012,'Dawn,7February2012','https://www.dawn.com/news/693636','News article opened; limited derived use.',['2011survey and inscribed seal'],True,'No reuse licence located; web tool source budget25words; no quotation used.')
src('QASIM2001','Indus Civilization Sites Discovered in Sandal Bar',['Qasim Ali Qasim'],2001,'In M.A.Halim (editor), Abdul Ghafoor (co-editor), Indus Valley Civilization: Dialogue Among Civilizations, proceedings Islamabad6–8April2001, Government of Pakistan, pp.38–40','https://ignca.gov.in/Asi_data/85282.pdf','Full proceedings PDF downloaded; scanned article and title/editors/TOC visually inspected.',['printedp38/PDF74 Rajanpur Chak585 location and earlyHarappan surface pottery; articlepp38–40; nextarticlep41'])
src('MUGHAL1989','Recent Archaeological Research in the Cholistan Desert',['M. Rafique Mughal'],1989,'In S.P.Gupta (editor), An Archaeological Tour Along the Ghaggar-Hakra River, Meerut: Kusumanjali Prakashan, appendix; reprint of1982chapter','https://pahar.in/pahar/Books%20and%20Articles/Indian%20Subcontinent/1989%20Archaeological%20Tour%20along%20the%20Ghaggar-Hakra%20River%20by%20Stein%20s.pdf','Web full PDF opened; exact site table known from search snippets, not independently visually inspected. Requests download403.',['search snippets printedp111 DerawarTher209 vsFort208; p113 RappwalaTher300'],True,'Bookcopyright1989 publisher; no open licence.')
src('BALL2019','Archaeological Gazetteer of Afghanistan: Revised Edition',['Warwick Ball'],2019,'Oxford University Press','https://api.pageplace.de/preview/DT0400.9780192573346_A37880829/preview-9780192573346_A37880829.pdf','72-page preview opened; assigned site entries absent.',['preview does not contain Shortughai/Mundigak entries; nearby Arukh is a different site'],True,'All rights reserved, publisher copyright leaf.')
src('PLEIADES','Shortughai',['Pleiades contributors'],None,'Pleiades place717754049','https://pleiades.stoa.org/places/717754049','Bot challenge prevented gazetteer record inspection.',['blocked location record'],False)
src('ARCHATLAS','Remote Sensing in Inaccessible Lands',['Cameron A. Petrie'],2007,'ArchAtlas journal','https://www.archatlas.org/journal/cpetrie/inaccessiblelands/','Gazetteer table visible in search snippet only; pageopen403.',['Mundigak af/mundigak coordinate31.90601,65.49809 differs from Uesugi; snippet date not publisherverified'],False)
src('NDL','インダス考古学の展望 : インダス文明関連発掘遺跡集成',['上杉彰紀 (Akinori Uesugi)'],2010,'National Diet Library bibliography','https://ndlsearch.ndl.go.jp/books/R100000002-I000010761660','Bibliographic search snippet; separatechapter4NDLrecord opened.',['author,title,ISBN,year; chapter4 pp135–138 https://ndlsearch.ndl.go.jp/books/R000000025-I010410002278133'],False)
src('FRANCFORT1978','Sondage préliminaire sur l’établissement protohistorique harappéen et post-harappéen de Shortugaï (Afghanistan du N.-E.)',['Henri-Paul Francfort','Marie-Hélène Pottier'],1978,'Arts Asiatiques34:29–86; DOI10.3406/arasi.1978.1121','https://www.persee.fr/doc/arasi_0004-3958_1978_num_34_1_1121','Primary article opening page29 opened; later individual pages44/45 web fetch failed. PDF download requires captcha, so no download attempted.',['p.29 fieldwork dates and team; total articlepp29–86'])
src('UNIVERSALIS','SHORTUGAÏ',['Encyclopédie Universalis; article author not established in search snippet'],None,'Encyclopédie Universalis','https://www.universalis.fr/encyclopedie/shortugai/','Substantial search excerpt only; not used for numeric counts.',['site history and graffiti on locally made jars'],False)

def failure(site,detail,field=None):
 return {'status':'unresolved','value':None,'detail':detail,'search_ids':[q['id'] for q in queries if q['site']==site]}
def item(status,detail,source,locator):
 return {'status':status,'detail':detail,'source_ids':[source] if isinstance(source,str) else source,'locator':locator}
def count(n,unit,source,loc,year,detail):
 return {'count':n,'unit_or_basis':unit,'source_ids':[source],'source_location':loc,'date':year,'claim':detail}
rows=[]
for name in names:
 old=next(s for s in first if s['canonical_name']==name)
 row={k:old[k] for k in ['canonical_name','local_corpus']}
 row.update(status='Exploratory',revision_date='2026-10-07',site_entity_id='gharo-bhiro-nuhato' if name in ['Gharo Bhiro','Nuhato'] else name.lower().replace(' ','-'),alternative_spellings=[],country='Afghanistan' if name in ['Shortughai','Mundigak'] else 'Pakistan')
 row['search_ids']=[q['id'] for q in queries if q['site']==name]
 row['source_ids']=['RAM-FULS2022','RAM-FULS2023']
 row['province']=failure(name,'Country follows the package regional selection; administrative province and exact corpus locality could not be independently tied to a report.')
 row['coordinates']=failure(name,'Targeted coordinate/gazetteer searches did not identify a numeric position tied to this corpus label.')
 row['excavation_campaigns']=[failure(name,'No site-specific excavation campaign, director and institution established in opened sources.')]
 row['publications']=[]
 row['cisi']=failure(name,'No assigned-site plate range found in CISI2 contents or accessible CISI3 records; absence from an inspected volume is not an all-volume absence claim.')
 row['mahadevan_1977_count']=failure(name,'Targeted Mahadevan1977 searches returned no class-specific site count with a verifiable original page. Coordinator is independently inspecting the acquired full1977 volume.')
 row['icit_count']=failure(name,'Most assigned site bodies lie outside Fuls2022 public preview. TOC page identification alone does not verify object totals.')
 classes=['seals','sealings','tablets','inscribed_pottery_and_graffiti','metal','other_inscribed_objects']
 row['reported_counts_by_class']={c:[failure(name,'No class-specific inventory total found in the opened sources; source unit was checked before any numeric count was accepted.')] for c in classes}
 row['reported_object_counts']={'count_scope':'Separate class counts and sign occurrences; null means unresolved, not zero.','by_class':row['reported_counts_by_class']}
 fields=['findspot','stratum_or_phase','absolute_dates','dimensions','material','photographs','drawings','registration_numbers']
 row['publication_metadata']={f:{'status':'no','scope':'No verified object-level record in inspected publication portion. Full excavation report was not obtained.','search_ids':row['search_ids']} for f in fields}
 row['post_cisi_assessment']={'status':'unresolved','latest_cisi_coverage_year':None,'find_count_basis':None,'source_ids':row['source_ids'],'search_ids':row['search_ids'],'detail':'Searches included later seasons and Pakistan Archaeology; no dated additional inscribed find tied to a verified site-specific CISI cutoff was established.'}
 row['post_cisi_finds']=row['post_cisi_assessment']
 row['final_report']={'status':'unresolved','title':None,'source_id':None,'locator':None,'full_text_inspected':False,'search_ids':row['search_ids']}
 row['present_holding']=failure(name,'No present object custody established; an old catalogue owner is recorded separately when available.')
 row['digital_availability']={'sources':[{'source_id':'RAM-FULS2022','availability':'Public35-page preview plus selectedindices, not full assigned-site inventory.','reuse':'All rights preserved.'},{'source_id':'RAM-FULS2023','availability':'Substantial public digital catalogue.','reuse':'All rights preserved.'}]}
 row['open_problems']=['Original excavation inventory and current object custody remain unresolved where query records show no accessible source.','The local export counts faces and object families; neither alone establishes the number of excavated objects.']
 row['superseded_first_pass_claims']=['Fuls2023 bracketed site figures are legible sign occurrences (p.498 section5.3), not object records.','Fuls2022 TOC/sitepage references outside the35-page preview do not mean that the site body was inspected.']
 lc=row['local_corpus']
 row['local_coverage_judgment']=f"Local snapshot: {lc['faces']} faces, {lc['object_families']} object families and {lc['distinct_cisi_ids']} distinct CISI identifiers. Only published records in a matching unit can support completeness; no excavation-wide completeness claim is established." if lc else 'No local export row found in the starting selection.'
 rows.append(row)
R={r['canonical_name']:r for r in rows}
def addsrc(r,*ids):r['source_ids']+=list(ids)
def pub(r,title,authors,year,venue,id,loc):r['publications'].append(dict(title=title,authors=authors,year=year,venue=venue,source_id=id,locator=loc))
def met(r,field,status,detail,id,loc):r['publication_metadata'][field]=item(status,detail,id,loc)

r=R['Shortughai'];r['alternative_spellings']=['Shortugaï','Shortugai','Shortughaï'];r['province']=item('verified','Takhar in current DAFA account; Badakhshan in Uesugi2010 regional gazetteer.', ['RAM-DAFA-S','RAM-GAZ-AF'],'DAFA location section; Uesugi p.138')
r['coordinates']={'value':'37°18′00″N, 69°30′00″E','latitude':37.3,'longitude':69.5,'source_ids':['RAM-GAZ-AF'],'locator':'p.138/PDF4, citing Possehl1999:822','precision':'One arcminute published coordinates; no modern survey precision implied.'}
r['excavation_campaigns']=[{'years':'1975 survey; 1976 test trenches; 1977–1979 three campaigns','directors':'Jean-Claude Gardin (survey); Henri-Paul Francfort (excavation); Z.Païman, M.-H.Pottier and N.Rasouli listed as collaborators','institution':'DAFA and CNRS URA10','source_ids':['RAM-DAFA-S','RAM-GAZ-AF'],'locator':'DAFA field history; Uesugi p.138'}]
pub(r,'Fouilles de Shortugaï. Recherches sur l’Asie centrale protohistorique','Henri-Paul Francfort',1989,'Mémoires de la Mission archéologique française en Asie centrale II, two volumes, Paris:deBoccard','RAM-FRANCFORT1989','BnF record; DAFA bibliography')
pub(r,'Sondage préliminaire sur l’établissement protohistorique harappéen et post-harappéen de Shortugaï (Afghanistan du N.-E.)','H.-P.Francfort and M.-H.Pottier',1978,'Arts Asiatiques34:29–86','RAM-DAFA-S','bibliography')
r['final_report']={'status':'identified','title':r['publications'][0]['title'],'source_id':'RAM-FRANCFORT1989','locator':'BnF bibliographic record; DAFA bibliography','full_text_inspected':False}
r['cisi']={'volume':'CISI3.3','year':2022,'page_range':'509–523','catalogue_range':'Sh1–84','source_ids':['RAM-CISI33'],'locator':'TOC pp.vii–viii','count_basis':'84 numbered catalogue entries include seals, graffiti and other potmarks; not84 authenticated inscribed objects. Object plates and basicdata absent from selected PDF.'}
r['reported_counts_by_class']['seals']=[count(2,'seals, inscription status not individually audited','RAM-CISI33','preface p.xv/PDF16',2022,'Preface reports two Indus seals. Do not equate this to two independently verified inscribed seal faces.')]
r['reported_counts_by_class']['inscribed_pottery_and_graffiti']=[{'count':None,'unit_or_basis':'plentiful graffiti, no numeric inventory','source_ids':['RAM-CISI33'],'source_location':'preface p.xv/PDF16','date':2022,'claim':'Graffiti are explicitly described; their inscription status and count require the object catalogue.'}]
met(r,'findspot','partial','Site located; object-level trench/locus not inspected.','RAM-DAFA-S','field history')
met(r,'stratum_or_phase','partial','Four site periods I–IV described; no plate-to-period join inspected.','RAM-DAFA-S','chronology section')
met(r,'absolute_dates','no','No object-specific absolute date in opened DAFA overview or CISI excerpt.',['RAM-DAFA-S','RAM-CISI33'],'chronology; selected excerpt')
r['post_cisi_assessment'].update(status='no_dated_find_located',latest_cisi_coverage_year=2022,source_ids=['RAM-CISI33','RAM-DAFA-S'],detail='No excavation after1979 or additional inscribed find after2022 located in the recorded searches. The2022 publication is catalogue coverage.')
r['local_coverage_judgment']='One local face/family with CISI Sh69; maximum69 does not estimate completeness because CISI3.3 Sh1–84 includes mixed glyptic material and potmarks. Object-level inclusion must be checked before a denominator is formed.'
addsrc(r,'RAM-CISI33','RAM-DAFA-S','RAM-GAZ-AF','RAM-FRANCFORT1989','RAM-BALL2019','RAM-PLEIADES','RAM-FRANCFORT1978','RAM-UNIVERSALIS')

r=R['Mundigak'];r['alternative_spellings']=['Mundīgak','Mondigak'];r['province']=item('verified','Kandahar; Kishk-i-Nakhod valley in DAFA account.',['RAM-DAFA-M','RAM-GAZ-AF'],'DAFA location; Uesugi p.136')
r['coordinates']={'value':'31°55′00″N, 65°30′00″E','latitude':31.9166666667,'longitude':65.5,'source_ids':['RAM-GAZ-AF'],'locator':'p.136/PDF2 citing Possehl1999:799','disagreements':[{'value':'31.90601N65.49809E','source_id':'RAM-ARCHATLAS','scope':'Search snippet only; page403; not chosen as primary coordinate.'}]}
r['excavation_campaigns']=[{'years':'1951–1959, ten campaigns in DAFA account;1951–1958 listed by Uesugi and CISI3.3','directors':'Jean-Marie Casal; Daniel Schlumberger commissioned programme','institution':'DAFA; Musée Guimet attribution in Uesugi','source_ids':['RAM-DAFA-M','RAM-GAZ-AF','RAM-CISI33'],'locator':'DAFA field history; Uesugi p.136; CISI3.3 prefacep.x','disagreement':'Final season1959 versus1958 needs the original report.'}]
pub(r,'Fouilles de Mundigak','Jean-Marie Casal',1961,'Mémoires de la Délégation archéologique française en Afghanistan XVII, two volumes, Paris:C.Klincksieck','RAM-CASAL1961','official publisher record')
r['final_report']={'status':'identified','title':'Fouilles de Mundigak','source_id':'RAM-CASAL1961','locator':'Official publisher bibliographic record confirmsXVII; DAFA web bibliography saysXVI.','full_text_inspected':False}
r['cisi']={'volume':'CISI3.2 (2019) and supplement CISI3.3 (2022)','page_range':None,'supplement_page_range':'528','catalogue_range':'Supplement Mgk63–66','source_ids':['RAM-CISI32','RAM-CISI33'],'locator':'CISI3.2 title record; CISI3.3 TOCpp.vii–viii','count_basis':'Four supplement catalogue entries; inscription status unresolved. The2019 site range not recoverable from the opened bibliographic record.','search_ids':r['search_ids']}
met(r,'findspot','partial','Site geography verified; individual seal contexts not inspected.',['RAM-DAFA-M','RAM-GAZ-AF'],'DAFA overview; p.136')
met(r,'stratum_or_phase','partial','Seven site periods are described, without object-by-object association.','RAM-DAFA-M','chronology')
r['post_cisi_assessment'].update(status='no_dated_find_located',latest_cisi_coverage_year=2022,source_ids=['RAM-CISI33','RAM-DAFA-M'],detail='No dated inscribed find after2022 located. Four Mgk supplement entries do not establish newly excavated objects.')
r['local_coverage_judgment']='Mundigak has no local export row (zero local faces and families in the coordinator selection). The mixed CISI seal catalogue cannot supply an inscribed-object denominator until individual entries are inspected.'
addsrc(r,'RAM-CISI32','RAM-CISI33','RAM-DAFA-M','RAM-GAZ-AF','RAM-CASAL1961','RAM-ARCHATLAS','RAM-BALL2019')

for name in ['Gharo Bhiro','Nuhato']:
 r=R[name];r['alternative_spellings']=['Gharo Bhiro','Garho Bhiro','Nuhato'];r['province']=item('partial','Sindh. Mughal1972 calls it MithiTaluka, TharparkarDistrict; current Nuhato news refers to Umerkot. Administrative changes and catalogue identity need geographic reconciliation.',['RAM-MUGHAL1972','RAM-CISI2','RAM-DAWN-NUHATO'],'Mughalp.137 site97; CISI2p.xv; Nuhato feature')
 r['alias_cross_reference']={'site_entity_id':'gharo-bhiro-nuhato','claim':'CISI2 explicitly prints Gharo Bhiro (Nuhato). Both requested local-label rows retained.','source_id':'RAM-CISI2','locator':'p.xv and p.iv TOC','local_identity_warning':'The five Nuhato families and one Grb1 family are not established as six distinct archaeological objects; alias join unresolved.'}
 r['excavation_campaigns']=[{'years':'September–October1972 survey','directors':'Mohammad Sharif (field team); M.Rafique Mughal (report author)','institution':'Department of Archaeology, Pakistan','source_id':'RAM-MUGHAL1972','locator':'pp.133–134; site97 p.137'},{'years':'2018 excavation','directors':'Qasid Hussain Mallah','institution':'Culture, Tourism and Antiquities Department, Government of Sindh','source_id':'RAM-SINDH2019','locator':'issue editorial; full report download failed'}]
 pub(r,'Explorations in Southern Sind','M.Rafique Mughal',1972,'Pakistan Archaeology8:133–137','RAM-MUGHAL1972','p.134 and site97p.137')
 pub(r,'In search of the Indus culture sites in Sind','N.A.Baloch',1973,'Bulletin of the Institute of Sindhology, University of Sind3(2–3):11–19, map, sixplates','RAM-BALOCH1973','CISI2p.xv note14; plate3a reproduced asGrb1')
 r['cisi']={'volume':'CISI2','year':1991,'page_range':'392','catalogue_range':'Grb1','source_ids':['RAM-CISI2'],'locator':'p.iv TOC; p.392 plate; p.447 data','alias':'Gharo Bhiro (Nuhato)'}
 r['reported_counts_by_class']['seals']=[count(1,'surface-find seal; one catalogue object','RAM-CISI2','p.xv; p.392 Grb1; p.447 data',1991,'N.A.Baloch surface discovery reproduced from1973report. Shared by the alias rows, not additive.')]
 met(r,'findspot','partial','Surface of Gharo Bhiro (Nuhato), no trench or grid.','RAM-CISI2','p.xv; p.447 context???')
 met(r,'stratum_or_phase','partial','Seal attributed MatureHarappan; surface find lacks stratum.','RAM-CISI2','p.xv')
 met(r,'absolute_dates','no','No object-specific absolute dates given.','RAM-CISI2','p.xv; p.447')
 met(r,'dimensions','no','No numeric object dimensions in inspected Grb1 plate/basicdata.','RAM-CISI2','pp.392,447')
 met(r,'material','no','Grb1 material not specified in inspected basicdata; visual resemblance is insufficient.','RAM-CISI2','pp.392,447')
 met(r,'photographs','partial','One reproduced black-and-white seal illustration; original photographic medium not established.','RAM-CISI2','p.392, credited Baloch1973plate3a atp.447')
 met(r,'drawings','partial','Illustration reproduction present; cannot identify it securely as independent drawing or photograph.','RAM-CISI2','p.392')
 met(r,'registration_numbers','partial','Catalogue Grb1 and photographic corpus number8251; excavation registration absent.','RAM-CISI2','p.447')
 r['present_holding']=item('partial','CISI1991 ownercodePC*=privatecollection; current custody not established.','RAM-CISI2','p.447 Grb1; ownerkeyp.434')
 r['post_cisi_assessment'].update(status='unresolved',latest_cisi_coverage_year=1991,source_ids=['RAM-CISI2','RAM-SINDH2019'],detail='2018 excavation is independently announced, but its report could not be downloaded. No explicit post1991 inscribed find verified in the opened editorial or1972survey.')
 r['local_coverage_judgment']='CISI2 publishes one Grb1 seal. Local Gharo Bhiro has one Grb1 face/family; local Nuhato has five faces/families with noCISI IDs. The latter require object-level matching and cannot yet enlarge the Grb1 inventory.'
 r['superseded_first_pass_claims']+=['Mughal1972 title is Explorations in Southern Sind, not Recent Archaeological Research in the Cholistan Desert.']
 addsrc(r,'RAM-CISI2','RAM-MUGHAL1972','RAM-SINDH2019','RAM-BALOCH1973','RAM-BALOCH2004','RAM-DAWN-NUHATO')

r=R['Naru-Waro-dharo'];r['alternative_spellings']=['Naru Waro Dharo','Naru-Waro-Dharo'];r['province']=item('verified','Sindh, Khairpur District.','RAM-GAZ-PK','p.116/PDF22')
r['coordinates']={'value':'27°25′00″N, 68°41′00″E','latitude':27.4166666667,'longitude':68.6833333333,'source_ids':['RAM-GAZ-PK'],'locator':'p.116/PDF22 citingPossehl1999:801–802'}
r['excavation_campaigns']=[{'years':'1955','directors':'F.A.Khan attribution in Biagi2024 reference50; institutional excavation confirmed by gazetteer','institution':'Department of Archaeology, Pakistan','source_ids':['RAM-GAZ-PK','RAM-BIAGI2024'],'locator':'gazetteerp.116; Biagip.4254/reference50','limitation':'Original1955report not inspected; individual field-director role needs original verification.'}]
pub(r,'Excavations at Naru Waro Dharo','Department of Archaeology / F.A.Khan (attribution differs between gazetteer and Biagi)',1964,'Pakistan Archaeology1:43–44','RAM-NARU1964','gazetteerp.116; Biagi reference50; CISI2p.xviii note35p44')
r['final_report']={'status':'identified','title':'Excavations at Naru Waro Dharo','source_id':'RAM-NARU1964','locator':'Pakistan Archaeology1:43–44, citation only; whether this two-page account is the definitive excavation report is unresolved.','full_text_inspected':False}
r['cisi']={'volume':'CISI2','year':1991,'page_range':'406','catalogue_range':'Nwd1–3','source_ids':['RAM-CISI2'],'locator':'TOCp.iv; platep.406; data p.447'}
r['reported_counts_by_class']['inscribed_pottery_and_graffiti']=[count(3,'potsherd objects illustrated as Nwd1–3','RAM-CISI2','pp.xvii–xviii; p.406; p.447',1991,'Introduction explicitly says three such potsherds first published here; original1964report described inscribed potsherds without recovered total.')]
met(r,'findspot','partial','Site plus uninterpreted grid/context strings K.xvii/17(2), K.xviii/17(7), K.xvii/16.','RAM-CISI2','p.447 Nwd1–3')
met(r,'stratum_or_phase','partial','Site described MatureHarappan; object grid strings not translated into stratigraphic phases.','RAM-CISI2','pp.xvii–xviii; p.447')
met(r,'absolute_dates','no','No object-specific absolute date in basicdata.','RAM-CISI2','p.447')
met(r,'dimensions','partial','Published illustration scale50%,100%,100%, but no numeric dimensions verified.','RAM-CISI2','p.406')
met(r,'material','yes','Pottery sherds explicitly stated and photographed.','RAM-CISI2','pp.xvii–xviii and406')
met(r,'photographs','yes','Three sherd photographs AV108/107/106.','RAM-CISI2','pp.406,447')
met(r,'drawings','no','No independent object drawings on inspected plate.','RAM-CISI2','p.406')
met(r,'registration_numbers','yes','NWD1321, NWD1379, NWD626; photographic corpus8603/8602/8601.','RAM-CISI2','p.447 Nwd1–3')
r['present_holding']=item('partial','All three catalogued at EXB:Excavation Branch of Department of Archaeology and Museums, Government of Pakistan, Karachi in1991. Current custody unverified.','RAM-CISI2','p.447; keyp.434')
r['local_coverage_judgment']='Local3faces/3families/3distinctNwd IDs exactly match CISI2 Nwd1–3, with maximum3. This establishes coverage of that illustrated inventory, whose contiguous1–3 range is checked; it does not establish total excavated potsherds.'
r['post_cisi_assessment'].update(status='no_dated_find_located',latest_cisi_coverage_year=1991,source_ids=['RAM-CISI2','RAM-BIAGI2024'],detail='Biagi2024 revisits1955work; it does not report a later inscribed find. Recorded later-season searches located no dated additional inscribed object.')
addsrc(r,'RAM-CISI2','RAM-GAZ-PK','RAM-NARU1964','RAM-BIAGI2024')

r=R['Bakkar Buthi'];r['alternative_spellings']=['Bakkar Bhuti'];r['province']=item('partial','Balochistan, Lasbela region in excavation slideshow.','RAM-HARAPPA-BB','site overview')
r['coordinates']={'value':'25°45′N, 66°34′E','latitude':25.75,'longitude':66.5666666667,'source_ids':['RAM-FULS2022'],'locator':'p.30 section3.5','confidence':'Secondary epigraphic corpus coordinate; its underlying gazetteer reference not established. A report/gazetteer coordinate remains unresolved.','search_ids':r['search_ids']}
r['excavation_campaigns']=[{'years':'1998','directors':'Ute Franke-Vogt (investigator/photographer); field director attribution not explicit in caption','institution':'Institution not explicitly verified in inspected slide caption','source_ids':['RAM-HARAPPA-BB','RAM-HARAPPA-BB-POT'],'locator':'excavation slideshow BakkarButhi account'}]
r['icit_count']={'count':1,'unit_or_basis':'ICIT object entry, one pottery text','id':18,'date':2022,'source_ids':['RAM-FULS2022'],'locator':'p.30 section3.5'}
r['reported_counts_by_class']['inscribed_pottery_and_graffiti']=[count(1,'pictured pottery object, minimum, not site inventory','RAM-HARAPPA-BB-POT','caption sectionA,l.1–4',None,'Red-slipped pedestal with inscription.'),count(1,'ICIT object entry, one complete pottery text','RAM-FULS2022','p.30 section3.5 ID18',2022,'POT:T:g entry; noCISI ID. Matching depicted pedestal to databaseID18 needs a crosswalk.')]
met(r,'findspot','partial','SectionA,l.1–4 named; whetherlayers1–4 denote mixedcontext needs excavation report.','RAM-HARAPPA-BB-POT','caption')
met(r,'stratum_or_phase','partial','Caption has l.1–4, without individual phase assignment.','RAM-HARAPPA-BB-POT','caption')
met(r,'material','yes','Red-slipped pottery pedestal.','RAM-HARAPPA-BB-POT','caption')
met(r,'photographs','yes','Primary excavation photograph.','RAM-HARAPPA-BB-POT','slide')
r['local_coverage_judgment']='One localPOT face/family matches the oneICIT entry at the level of class and site. No objectID/photo join or excavation-wide pottery-mark inventory established.'
addsrc(r,'RAM-HARAPPA-BB','RAM-HARAPPA-BB-POT')

r=R['Wattoowala'];r['alternative_spellings']=['Wattowala','Watto Wala'];r['province']=item('verified','Punjab, Cholistan nearDerawarFort.','RAM-PU2011','institutional project report lines80–84')
r['excavation_campaigns']=[{'years':'2011 reconnaissance','directors':'Farzand Masih','institution':'Department of Archaeology, University of the Punjab; UNESCO-funded SuiVihar and SouthernPunjab reconnaissance project','source_id':'RAM-PU2011','locator':'lines80–84'}]
pub(r,'Rare Indus seal discovered in Cholistan','Mansoor Malik',2012,'Dawn,7February2012','RAM-DAWN-W','news article')
r['reported_counts_by_class']['seals']=[count(1,'reported survey-find seal','RAM-PU2011','webline83',2011,'Institution reports a first Indusperiod seal atWattowala.')]
r['post_cisi_assessment'].update(status='unresolved',latest_cisi_coverage_year=None,find_count_basis='One2011seal reported; latestsiteCISIcoverage unresolved.',source_ids=['RAM-PU2011','RAM-DAWN-W'],detail='Dawn identifies an inscribed steatite seal; exactCISI volume/page for localW1 not recovered, so cannot classify2011 as after latestsitecoverage.')
met(r,'findspot','partial','Site and reconnaissance programme identified; nogrid.','RAM-PU2011','line83')
met(r,'material','yes','Steatite seal with ibex and two signs.','RAM-DAWN-W','seal description')
r['present_holding']=failure('Wattoowala','PU announcement proposes a teachingmuseum; it does not establish that this seal was accessioned there.')
r['local_coverage_judgment']='One localseal face/family with W1 agrees with the reported one-seal discovery only at site/class level. The CISI volume and record identity require verification.'
addsrc(r,'RAM-PU2011','RAM-DAWN-W')

for name in ['Rappwala Ther','Guddal A','Derawar Ther']:
 r=R[name];r['alternative_spellings']=[name.replace(' ','-')]
 r['province']=item('partial','Inter-Riverine region in Fuls2022; CholistanPunjab is a report lead forRappwalaTher/DerawarTher, but the object-to-survey locality join remains unverified.','RAM-FULS2022','p.26 regional list')
 r['substantive_source_opened']={'source_id':'RAM-FULS2023','locator':'p.498 section5.3 site-specific list','observation':'One legible sign occurrence, not one excavated object.'}
 r['local_coverage_judgment']='One localpottery face/family, noCISI ID. Fuls2023 lists onelegiblesign; no matching publishedobjectdenominator was verified.'
 if name!='Guddal A':
  r['survey_candidate']={'source_id':'RAM-MUGHAL1989','locator':'p.113 site300' if name=='Rappwala Ther' else 'p.111 site209','access_scope':'Table searchsnippet; fulltable not independently rendered.','detail':'Named Cholistan survey locality; cannot yet join its archaeology to the local inscribed object.'};addsrc(r,'RAM-MUGHAL1989')

r=R['Rajanpur'];r['alternative_spellings']=['Rajanpur (corpus label)','Rajanpur Chak585 (candidate locality)'];r['site_entity_id']='rajanpur-corpus-unresolved'
r['province']=item('partial','Corpus label Inter-Riverine. Candidate Chak585 is historically JaranwalaTehsil, SheikhupuraDistrict,Punjab; identity with localtablet unresolved.',['RAM-FULS2022','RAM-QASIM2001'],'Fulsregional listp.26; Qasimp.38')
r['coordinates']={'value':None,'status':'unresolved','candidate':{'value':'31°09′30″N, 73°23′00″E','latitude':31.1583333333,'longitude':73.3833333333,'source_id':'RAM-QASIM2001','locator':'printedp.38/PDF74 RajanpurChak585'},'detail':'Do not assign candidatecoordinates to corpus tablet without an object/site crosswalk. ModernRajanpurDistrict is another homonym.','search_ids':r['search_ids']}
pub(r,'Indus Civilization Sites Discovered in Sandal Bar','Qasim Ali Qasim',2001,'In Indus Valley Civilization:Dialogue Among Civilizations, edM.A.Halim, coedAbdulGhafoor, GovernmentPakistan, pp.38–40','RAM-QASIM2001','printedp.38/PDF74')
r['excavation_campaigns']=[failure('Rajanpur','Qasim2001 gives surface earlyHarappan pottery and ornaments forChak585, without a field-season date or an inscribed-object discovery. This cannot supply the tablet campaign.')]
met(r,'findspot','partial','CandidateRajanpurChak585 described; localtablet provenance remains unresolved.','RAM-QASIM2001','p.38/PDF74')
met(r,'stratum_or_phase','partial','Candidate earlyHarappan surfaceceramics, not a stratifiedtabletphase.','RAM-QASIM2001','p.38/PDF74')
r['superseded_first_pass_claims']+=['The inspected RajanpurChak585 article is QasimAliQasim2001 pp.38–40, not Mughal1964.','Fuls2023 Rajanpur7 counts legiblesignoccurrences; local2TAB faces form oneobjectfamily.']
r['local_coverage_judgment']='LocaltwoTAB faces share onefamily, noCISI ID. Fuls2023 sevenlegiblesigns supply no physicalobjectcount; corpuslabel cannot be securely joined toChak585.'
addsrc(r,'RAM-QASIM2001')

for r in rows:
 r['reported_object_counts']['by_class']=r['reported_counts_by_class']
 r['post_cisi_finds']=r['post_cisi_assessment']
 r['source_ids']=list(dict.fromkeys(r['source_ids']))
 r['digital_availability']['sources'] += [{'source_id':sid,'availability':next(s['access_scope'] for s in sources if s['id']==sid),'reuse':next(s['reuse'] for s in sources if s['id']==sid)} for sid in r['source_ids'] if sid not in ['RAM-FULS2022','RAM-FULS2023']]

# Improve readability without changing identifiers, URLs or exact source titles.
replacements={
 'full1977':'full 1977','public35-page':'public 35-page','fulltable':'full table','searchsnippet':'search snippet',
 'basicdata':'basic data','legiblesignoccurrences':'legible sign occurrences','legiblesigns':'legible signs','legiblesign':'legible sign',
 'physicalobjectcount':'physical object count','objectdenominator':'object denominator','publishedobjectdenominator':'published object denominator',
 'objectID/photo':'object ID/photo','localtabletphase':'local tablet phase','localtablet':'local tablet','local2TAB':'local 2 TAB',
 'localpottery':'local pottery','localtwoTAB':'local two TAB','oneobjectfamily':'one object family','onefamily':'one family',
 'object/site':'object/site','toChak585':'to Chak 585','Chak585':'Chak 585','ModernRajanpurDistrict':'Modern Rajanpur District',
 'RajanpurChak':'Rajanpur Chak','MatureHarappan':'Mature Harappan','earlyHarappan':'early Harappan','surfaceceramics':'surface ceramics',
 'field-season':'field-season','first Indusperiod':'first Indus period','Indusperiod':'Indus period',
 'siteCISIcoverage':'site CISI coverage','exactCISI':'exact CISI','after2022':'after 2022','after1979':'after 1979',
 'after2022':'after 2022','post1991':'post 1991','threecampaigns':'three campaigns','site-specific':'site-specific',
 'Uesugi2010':'Uesugi 2010','Biagi2024':'Biagi 2024','Fuls2022':'Fuls 2022','Fuls2023':'Fuls 2023',
 'CISI1991':'CISI 1991','Mughal1972':'Mughal 1972','Baloch1973':'Baloch 1973','Possehl1999':'Possehl 1999',
 'Francfort1989':'Francfort 1989','Mughal1964':'Mughal 1964','Qasim2001':'Qasim 2001','QasimAliQasim2001':'Qasim Ali Qasim 2001',
 'original1964report':'original 1964 report','original1955report':'original 1955 report','2019Mundigak':'2019 Mundigak',
 '1998 excavations':'1998 excavations','BakkarButhi':'Bakkar Buthi','RappwalaTher':'Rappwala Ther','DerawarTher':'Derawar Ther',
 'CholistanPunjab':'Cholistan, Punjab','Wattowala':'Wattowala','SouthernPunjab':'Southern Punjab','SuiVihar':'Sui Vihar',
 'UniversityPunjab':'University Punjab','NationalMuseumofPakistan':'National Museum of Pakistan','ExcavationsBranch':'Excavations Branch',
 'privatecollection':'private collection','MithiTaluka':'Mithi Taluka','TharparkarDistrict':'Tharparkar District',
 'JaranwalaTehsil':'Jaranwala Tehsil','SheikhupuraDistrict':'Sheikhupura District','DerawarFort':'Derawar Fort',
 'inscribed-object':'inscribed-object','noCISI':'no CISI','site/class':'site/class','NWD1321':'NWD 1321','NWD1379':'NWD 1379','NWD626':'NWD 626',
 'K.xvii':'K. xvii','K.xviii':'K. xviii','ICIT18':'ICIT 18','ID18':'ID 18','noCISI':'no CISI','oneICIT':'one ICIT',
 'onePOT':'one POT','localPOT':'local POT','three Nwd':'three Nwd','one-seal':'one-seal','onelegible':'one legible',
 'TOCpp':'TOC pp','TOCp':'TOC p','prefacep.':'preface p.','gazetteerp.':'gazetteer p.','Biagip.':'Biagi p.',
 'reportp.':'report p.','p.xv':'p. xv','p.xviii':'p. xviii','p.xvii':'p. xvii','p.iv':'p. iv',
 'p.30':'p. 30','p.26':'p. 26','p.38':'p. 38','p.134':'p. 134','p.137':'p. 137','p.447':'p. 447',
 'pp.xvii':'pp. xvii','pp.vii':'pp. vii','pp.133':'pp. 133','pp.38':'pp. 38','site97':'site 97',
 'sealsfirst':'seals first','supplement528':'supplement 528','photo108':'photo 108','context???':'context ???',
 'siteplate':'site plate','field-director':'field-director','grid/context':'grid/context','fieldwork passage':'fieldwork passage',
 'Grb1':'Grb 1','Nwd1–3':'Nwd 1–3','Sh1–84':'Sh 1–84','Sh69':'Sh 69','Mgk63–66':'Mgk 63–66',
 'W1':'W 1','oneCISI':'one CISI','two seals':'two seals','Guddal-A':'Guddal-A',
 'newly excavated':'newly excavated','CISI2':'CISI 2','CISI3.3':'CISI 3.3','CISI3.2':'CISI 3.2',
 'Mahadevan1977':'Mahadevan 1977','Internetviewing':'Internet viewing','pp135–138':'pp.135–138',
 '30sources':'30 sources','35-page':'35-page','two-page1964':'two-page 1964',
}
skip={'id','source_id','source_ids','search_ids','url','site_entity_id','title','canonical_name','alternative_spellings','local_corpus'}
def readable(obj,key=''):
 if key in skip:return obj
 if isinstance(obj,dict):return {k:readable(v,k) for k,v in obj.items()}
 if isinstance(obj,list):return [readable(v,key) for v in obj]
 if isinstance(obj,str):
  for old,new in replacements.items():obj=obj.replace(old,new)
 return obj
rows=readable(rows);sources=readable(sources)

(OWN/'revision-afghan-minor.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OWN/'revision-afghan-minor-sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} rows; {len(sources)} sources; {len(queries)} queries')
