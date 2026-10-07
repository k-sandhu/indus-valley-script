import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'experiments/2026-10-06-evidence-census/sites-deep/c-north-india'
COVERAGE = ROOT / 'experiments/2026-10-06-research-program/local-site-coverage.json'

# [canonical, aliases, province, region, CISI prefix, evidence note, publication lead]
SITES = [
['Kalibangan',['Kali Bangan'],'Rajasthan','Inter-Riverine','K','Mahadevan 1977 count 99 objects; ICIT-based 2025 source says about 24 fish-sign texts.','Excavations at Kalibangan: The Early Harappans, 1960–1969 (B. B. Lal et al., 2003); vol. II, 2020.'],
['Banawali',[],'Haryana','Eastern Headwaters','B','Mahadevan 1977 count 7 objects; CISI B-1 to B-37; B-17 / ASI BNL-9201 reported from merchant house.','Excavations at Banawali (R. S. Bisht; 1974–77; publications 1982/1984).'],
['Rakhigarhi',['Rakigarhi','Rakhigari'],'Haryana','Eastern Headwaters','Rgr','Later report reports inscribed seals, sealings, clay tablets and a lead ingot; site CISI I contents lists Rgr-1 to 3.','Excavations at Rakigarhi [1997-98 to 1999-2000] (Amarendra Nath; catalogue 2012); later IAR seasons.'],
['Farmana',[],'Haryana','Eastern Headwaters','F','2008 report: two square steatite seals and two terracotta impression objects; one seal from preceding season, so not four new finds.','A Report on Excavations at Farmana 2007–08; Excavations at Farmana 2006–2008 (Shinde, Kumar, Osada, 2008/2011).'],
['Bhirrana',['Bhirdana'],'Haryana','Eastern Headwaters','Bhr','Three ASI field seasons 2003–06; sources mention seals, including a quarter-foil shell seal; object totals not reconciled.','New Light on the Excavation of Harappan Settlement at Bhirrana (L. S. Rao et al., 2011).'],
['Kunal',[],'Haryana','Eastern Headwaters','Ku','Haryana government page reports seal assemblage of 13 (8 steatite, 2 terracotta, 2 shell, 1 terracotta; wording overlaps categories); not all are inscribed.','Indian Archaeology – A Review 1991–92, “Excavation at Kunal”; J-STAGE article on Kunal seals (2012).'],
['Mitathal',[],'Haryana','Eastern Headwaters','Mth','1968 excavation reported one seal in later account; later excavations and surface surveys disagree on whether an inscribed seal was recovered.','Excavation at Mitathal (1968) and Other Explorations in the Sutlej-Yamuna Divide (Suraj Bhan, 1975).'],
['Sanauli',['Sinauli'],'Uttar Pradesh','Uttar Pradesh','Snl','Graffiti on pottery is reported in secondary search results; Indus-script attribution and object count not verified.','ASI 2005–06 excavation report / IAR; later excavations directed by Sanjay Manjul.'],
['Alamgirpur',[],'Uttar Pradesh','Eastern Headwaters','Agr','IAR 1958–59 plate LXV identifies Harappan script on pottery; local identifiers Agr-1 to Agr-3.','“Recent Excavations at Alamgirpur, Meerut District: A Preliminary Report”; later IAR reports.'],
['Hulas',[],'Uttar Pradesh','Eastern Headwaters','Hls','One terracotta sealing with three Harappan signs, registration 990, from unstratified deposit; dimensions 56.69 × 39.17 × 22.64 mm.','Excavations at Hulas; appendix “Indus Sealing from Hulas” (ASI PDF search result).'],
['Ropar (Rupar)',['Rupnagar','Rupar'],'Punjab','Punjab','Rpr','Local export has Rpr-1; historic report summaries note inscribed material, but object and phase counts not joined.','Excavations at Rupar (1953–55; Y. D. Sharma); 1955–56 report.'],
['Chandigarh',[],'Chandigarh','Chandigarh','Ch','Mahadevan 1977 count 4 objects; local export has 3 unique CISI IDs, maximum Ch-4.','CISI I site catalogue; no site-specific excavation report found.'],
['Kotla Nihang Khan',[],'Punjab','Punjab','KNK','Mentioned in an early exploration/report; no verified Indus-script object count or inscription-bearing status.','Exploration—Harappa / early ASI report; bibliography requires full check.'],
['Sanghol',[],'Punjab','Punjab','Sgh','NMMA search result lists a sealing (ASM-888-PB-183075); Indus script/date not verified.','Excavation of Sanghol, A Vedic Culture Site (ASI, 1986–90); Coins, Seals and Sealings from Sanghol.'],
['Karanpura',[],'Rajasthan','Inter-Riverine','Kp','IAR 2013–14 reports a seal with a two-letter inscription; 2021 presentation describes other inscribed material and 130 distinct ceramic signs.','Preliminary Results of Excavation at Karanpura (V. N. Prabhakar et al.); Indian Archaeology 2013–14.'],
['Binjor (4MSR)',['Binjore','4MSR'],'Rajasthan','Rajasthan','Bjn','No inscribed object count independently verified in sources searched.','ASI 4MSR excavation reporting; 2020 archaeometallurgy article distinguishes Binjor 1–4.'],
['Baror',[],'Rajasthan','Inter-Riverine','Br','ASI report describes 65 trenches in 2003–04 and 2004–05; inscription count not verified.','Baror – A New Harappan Site in Ghaggar Valley – A Preliminary Report (Urmila Sant et al.).'],
['Tarkhanewala Dera',['Tarkhanewala-dera'],'Rajasthan','Inter-Riverine','Tkwd','IAR report: terracotta seal impression with unicorn and typical Harappan letters, plate 2; Tkwd-1 to 3 locally indexed.','Tarkhanewala Dera and Chak 86 (2003–2004), Indian Archaeology – A Review.'],
['Manda',[],'Jammu and Kashmir','Jammu and Kashmir','M','IAR 1976–77 reports pottery with incised Harappan script and an unfinished seal; no total.','Indian Archaeology 1976–77, “Excavation at Manda”.'],
['Lohari Ragho',[],'Haryana','Eastern Headwaters','Lr','Local/regional listing retained; no independently verified inscribed object report found in this search set.','Regional survey and Rakhigarhi hinterland reports; final site report not located.'],
['Masudpur',[],'Haryana','Eastern Headwaters','Mas','Modern survey/excavation sources located; no inscribed object independently verified.','Living in the Hinterland: Survey and Excavations at Masudpur 2018–2019.'],
['Bhagwanpura',[],'Haryana','Eastern Headwaters','Bhg','Source search did not verify an Indus-script object; some summaries explicitly note no seal/sealing.','Excavations at Bhagwanpura (J. P. Joshi, 1975–76).'],
['Siswal',[],'Haryana','Eastern Headwaters','Sis','Secondary teaching PDF mentions early script on pottery and a square seal but does not securely assign specimens to this site.','Excavations at Siswal, District Hissar (Suraj Bhan; 1970; report 1972).'],
['Tigrana',[],'Haryana','Inter-Riverine','Tig','Added from local Inter-Riverine coverage: one TAG-class face; local database entry is not independent excavation confirmation.','No final excavation report located.'],
]

coverage=json.loads(COVERAGE.read_text(encoding='utf-8'))['sites']
by_name={x['site'].casefold():x for x in coverage}
aliases={'Ropar (Rupar)':'rupar','Tarkhanewala Dera':'tarkhanewala-dera'}
rows=[]
for name, spellings, state, region, prefix, note, publication in SITES:
    local=next((by_name[k.casefold()] for k in [name,*spellings] if k.casefold() in by_name),None)
    if local is None and name in aliases: local=by_name.get(aliases[name])
    count={'counts_by_class':{'seals':None,'sealings':None,'tablets':None,'inscribed_pottery_and_graffiti':None,'metal_and_other':None},'published_statement':note,'count_unit_date_and_page':'See cited source/search record; several totals are snippets or legacy counts and are not page-audited.'}
    coords={'Farmana':{'value':'29°02′22″N, 76°18′21″E','source':'Preliminary Findings on Human Skeletal Remains from Harappan Site of Farmana, 2012, search result; ResearchGate record','search_status':'published coordinates; source page not opened'}}
    row={'canonical_name':name,'alternative_spellings':spellings,'country':'India','province_or_union_territory':state,'coordinates':coords.get(name,{'value':None,'source':None,'search_status':'not located in inspected primary sources; see searches.json'}),'excavation_campaigns':{'summary':publication,'years_directors_institutions':'partial; exact campaign tables require publication-page audit'},'primary_and_final_publications':{'title_authors_year':publication,'cisi_volume':'CISI 1 (1987, India) where catalogue identifiers are present; otherwise later CISI coverage not page-verified','cisi_page_range':'Only following ranges verified: Kalibangan K-1–122, pp.298–326; Banawali B-1–37, pp.344–349 and 364. Other ranges not located.','mahad evan_1977_or_icit_count':note},'reported_inscribed_object_counts':count,'local_corpus':local or {'status':'No matching site row in local-site-coverage.json'},'local_coverage_judgment':note,'main_publication_metadata':{'findspot':'partial; see note/source-specific plate or report','stratum_or_phase':'partial/not located per site in this search set','absolute_dates':'not located per site in this search set','dimensions':'not located except Hulas sealing dimensions above','material':'partial for named finds in note','photographs':'CISI photos available where catalogue entry is identified; individual figures not checked','drawings':'not audited per object','registration_numbers':'partial: Hulas 990; Banawali BNL-9201; others not joined'},'post_cisi_finds':{'summary':note,'certainty':'varies; see source records and search failures'},'current_holding':'No object-level current repository/collection located in reviewed sources.','digital_availability_and_reuse':{'availability':'CISI scans, IAR PDFs and some reports are online; full text not consistently opened.','reuse_terms':'Reuse terms not verified for most scans; downloaded third-party files remain in local raw directory.'},'open_problems':[note,'Object-level joins, coordinates, exact CISI ranges and publication metadata require page-level checking.'],'evidence_status':'Exploratory; source-level gaps are explicit.'}
    # Keep keys ASCII-friendly while preserving field meaning.
    row['primary_and_final_publications']['mahadevan_1977_or_icit_count']=row['primary_and_final_publications'].pop('mahad evan_1977_or_icit_count')
    rows.append(row)

(OUT/'site-rows.json').write_text(json.dumps({'status':'Exploratory','generated':'2026-10-07','rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'site-rows.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=list(rows[0]); w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for row in rows: w.writerow({k:json.dumps(v,ensure_ascii=False) for k,v in row.items()})
