"""Compile bibliographic notes and asset hashes; payloads remain local-only."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

OWN=Path(__file__).resolve().parent; ROOT=OWN.parents[1]
RAW=ROOT/'data/raw/2026-10-06-sign-context-and-seals'

def source(id,title,authors,year,venue,url,access,locations,note,asset_id=None):
    return dict(id=id,title=title,authors=authors,year=year,venue=venue,url=url,
                access=access,locations=locations,relation_to_package=note,asset_id=asset_id,
                quotations_used=0)

def main():
    entries=[
      source('K1997','Early City-States in South Asia: Comparing the Harappan Phase and Early Historic Period',
        ['Jonathan Mark Kenoyer'],1997,'In Deborah L. Nichols and Thomas H. Charlton (eds.), The Archaeology of City-States, pp. 51–70, Smithsonian Institution Press',
        'https://www.columbia.edu/itc/anthropology/v3922/pdfs/kenoyer.pdf','opened_pdf_visual',
        ['PDF pp.1,3,4 inspected visually; printed p.54, Table 4.2'],
        'Urban site areas and an explicit warning about unknown occupied extent; the table gives Mohenjo-daro +250 while adjacent prose gives +200. Image-only extraction was empty.','kenoyer1997'),
      source('S2019',"What's cooking in the Indus Civilisation? Investigating Indus food through ceramic lipid residue analysis",
        ['Akshyeta Suryanarayan'],2019,'PhD dissertation, University of Cambridge',
        'https://api.repository.cam.ac.uk/server/api/core/bitstreams/515b5736-fa26-4c70-9ffb-7d5e9292221b/content','opened_pdf_text',
        ['printed p.87 / PDF p.121, Table 4.1','printed p.122 / PDF p.156, Kalibangan description'],
        'Site sizes and village/town/city classifications. Table footnotes state that Farmana and Rakhigarhi calculation criteria are uncertain.','kalibangan2020'),
      source('K2005',"L'archeologia del Subcontinente indiano. Dal Neolitico all'eta del Bronzo: la Civilta della valle dell'Indo",
        ['Jonathan M. Kenoyer','Stefano Pracchia','Massimo Vidale'],2005,'Il Mondo dell\'Archeologia, Treccani',
        "https://www.treccani.it/enciclopedia/l-archeologia-del-subcontinente-indiano-dal-neolitico-all-eta-del-bronzo-la-civilta-della-valle-dell-indo_(Il-Mondo-dell'Archeologia)/",'opened_fulltext',
        ['Kenoyer section: settlement hierarchy paragraph beginning I dati emersi','Vidale section: Chanhu Daro'],
        'Numerical settlement-area anchors, including Kalibangan 12.1; functional specialization at Chanhu Daro. Small-site tiers do not establish exclusive functions.','kenoyer2005'),
      source('U2014','Archaeological remains of a Harappa Port-Town, Lothal',
        ['Tentative-list nomination for India; authoring institution not established from this page'],2014,'UNESCO World Heritage Centre, tentative list, ref.5918, submitted 15 April 2014',
        'https://whc.unesco.org/en/tentativelists/5918/','opened_fulltext',
        ['Description, paragraphs 1–5'],
        'About 7 ha and port-town characterization. The displayed Submitted by field says Permanent Delegation of Turkey, an apparent page metadata anomaly; no authorship inferred from it.','lothal2014'),
      source('Y2013','Sensitivity of Indus Script to Site and Type of Object',
        ['Nisha Yadav'],2013,'Scripta 5, pp.67–103',
        'https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf','opened_fulltext_pdf',
        ['printed pp.67–71, data/methods','printed pp.75–76, field-symbol discussion','printed pp.100–103, conclusions/references'],
        'Direct predecessor for site, object and field-symbol frequencies. The present component-based references remeasure an established question on another observational export.','yadav2013'),
      source('O2019','Statistical Analysis of the Tables in Mahadevan’s Concordance of the Indus Valley Script',
        ['Michael Philip Oakes'],2019,'Journal of Quantitative Linguistics 26(1), pp.22–47; online publication 2017; DOI 10.1080/09296174.2017.1406294',
        'https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download','opened_fulltext_pdf',
        ['repository PDF p.1, bibliographic cover','Section 4, Tables 7–10 and Fig.6 discussion'],
        'Site/type/field-symbol tests, Bonferroni correction and correspondence analysis of sign–motif associations. Oakes 2017 and 2019 here name the online and issue dates of this same article.','oakes'),
      source('R2009','A Markov model of the Indus script',
        ['Rajesh P. N. Rao','Nisha Yadav','Mayank N. Vahia','Hrishikesh Joglekar','R. Adhikari','Iravatham Mahadevan'],2009,
        'Proceedings of the National Academy of Sciences 106(33), pp.13685–13690, DOI 10.1073/pnas.0904892106',
        'https://homes.cs.washington.edu/~rao/PNASIndus.pdf','opened_fulltext_pdf',
        ['PDF p.1, abstract/title; data preparation and Discussion'],
        'Sequence modelling and duplicate handling precedent. This located paper does not verify the specifically requested attribution of a motif–text association test to Rao et al.','rao2009'),
      source('R2018','The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor',
        ['Rajesh P. N. Rao'],2018,'In Walking with the Unicorn, Archaeopress, pp.518–525; arXiv 1812.00049v1',
        'https://arxiv.org/abs/1812.00049','opened_fulltext_pdf_and_abstract',
        ['PDF p.1 / printed p.518, tablet argument','arXiv abstract and publication comment'],
        'Provides an economic-function alternative for seals and tablets. It is a hypothesis about transaction media and is not a corporate-identity confirmation.','rao2018'),
      source('F2018','Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities',
        ['Dennys Frenez'],2018,'In D. Frenez, G. M. Jamison, R. W. Law, M. Vidale and R. H. Meadow (eds.), Walking with the Unicorn, Archaeopress',
        'https://www.researchgate.net/publication/347150488_Private_Person_or_Public_Persona_Use_and_Significance_of_Standard_Indus_Seals_as_Markers_of_Formal_Socio-Economic_Identities',
        'opened_web_fulltext_preview; direct download blocked',
        ['preview printed pp.186–187, Seals development as marketing strategy? and Private person or public persona?','preview printed p.167, size/style variability'],
        'Concentration and formal-role interpretation. Preview footers say 2017 and its pagination differs from current publisher contents; use section names and preserve the preview witness. The lecture itself was not reviewed.','frenez2018'),
      source('G2021','Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization',
        ['Adam Stuart Green'],2021,'Journal of Archaeological Research 29(2), pp.153–202; early online 16 September 2020; DOI 10.1007/s10814-020-09147-9',
        'https://link.springer.com/article/10.1007/s10814-020-09147-9','opened_fulltext_html_and_university_record',
        ['York record, Abstract/bibliography','article discussion of seals, reciprocity and corporate groups'],
        'Social-organization alternative; differences in seal use and technological organization cannot be resolved from pooled motif concentration alone.','green2021'),
      source('A2022','Mixed Methodologies: Collaborative Approaches to Indus Tiger Seals',
        ['Marta Ameri','Gregg Jamison'],2022,'South Asian Studies 38(1), pp.69–99; DOI 10.1080/02666030.2022.2051825',
        'https://www.tandfonline.com/doi/abs/10.1080/02666030.2022.2051825?role=tab&scroll=top&tab=permissions',
        'search_snippet_only; direct page blocked',
        ['publisher search result, title/author/pages/abstract'],
        'Stylistic and production comparisons are relevant to the workshop alternative. Detailed methods and results were not reviewed.','ameri2022'),
      source('Koverview','Indus Seals: An overview of Iconography and Style',
        ['Jonathan Mark Kenoyer'],'2006–2007 issue date; download filename says 2009','Ancient Sindh 9, pp.7–30',
        'https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals_0.pdf','opened_pdf_visual_and_host_summary',
        ['PDF p.1, cover; PDF p.4, contents; PDF p.5 / printed p.7, introduction'],
        'Production/iconographic survey predecessor. Only the stated pages were checked visually; no numerical size threshold from this article is used.','kenoyer2009'),
      source('KK2018','The Size of Indus Seals and its Significance',
        ['Ayumu Konasukawa','Manabu Koiso'],2018,'In Walking with the Unicorn, Archaeopress',
        'https://www.archaeopress.com/archaeopress/DMS/2F8027E3709041CC9F154907A5324022/9781784919177-sample.pdf',
        'contents_search_snippet_only; chapter unopened',
        ['sample contents starts at p.292; newer publisher contents gives The Size of the Indus Seals and its Significance at p.289'],
        'Direct size-study precedent located during this package. Its methods and distributions must be reviewed before any originality or disagreement claim.'),
      source('M2026v1','Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization: A Power Law Analysis of Harappan Seal Data',
        ['Mahesh T C'],2026,'arXiv 2604.23582v1, submitted 26 April 2026',
        'https://arxiv.org/html/2604.23582v1','opened_fulltext_html',
        ['Sections 1.1, 2, 3, 4 and 5.8; supplied HTML header also displays August 24, 2026'],
        'Offering-stand and site-count power-law interpretation. Bull1 suffixes are not an authenticated offering-stand typology, and motif concentration is not a network-degree or power-law test.','mahesh2026v1'),
      source('M2026current','Asynchronous Barter, Periodic Reconciliation: Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization',
        ['Mahesh T C'],2026,'arXiv 2604.23582, current abstract page, v3 dated 18 August 2026',
        'https://arxiv.org/abs/2604.23582','opened_abstract_and_submission_history',
        ['title and Submission history, v1/v2/v3'],
        'Title differs from v1. The title/version difference is preserved; current full text was not reviewed.','mahesh2026current'),
      source('B2019','Interrogating Indus inscriptions to unravel their mechanisms of meaning conveyance',
        ['Bahata Ansumali Mukhopadhyay'],2019,'Palgrave Communications 5, article 73; DOI 10.1057/s41599-019-0274-1',
        'https://www.nature.com/articles/s41599-019-0274-1','opened_fulltext_local_download; web open failed',
        ['Abstract; discussion of functional sign classes and commercial contexts'],
        'Structural segmentation and commercial interpretation precede this package. Statistical contextual differences do not authenticate the proposed semantic classes.','mukhopadhyay2019'),
      source('B2023','Semantic scope of Indus inscriptions comprising taxation, trade and craft licensing, commodity control and access control: archaeological and script-internal evidence',
        ['Bahata Ansumali Mukhopadhyay'],2023,'Humanities and Social Sciences Communications 10, article 972; DOI 10.1057/s41599-023-02320-7',
        'https://www.nature.com/articles/s41599-023-02320-7','opened_fulltext_html',
        ['Materials and methods; Semantic scopes of Indus-inscriptions; Diverse functionalities of ancient inscribed seals and tablets'],
        'Administrative-function proposals provide comparisons but require contextual and physical evidence beyond motif shares or dimension correlations.','mukhopadhyay2023'),
      source('J2017','Inscribed Unicorn Seals from Bagasra, Gujarat: A Comparative Analysis of Morphology, Carving Styles, and Distribution Patterns',
        ['Gregg M. Jamison','Bhanu Prakash Sharma','P. Ajithprasad','K. Krishnan','Kuldeep K. Bhan','V. H. Sonawane'],2017,
        'Heritage: Journal of Multidisciplinary Studies in Archaeology 5, pp.1–21',
        'https://www.heritageuniversityofkerala.com/JournalPDF/Volume5/1.pdf','search_snippet_only',
        ['publisher search result, title/author/abstract'],
        'Additional production/style precedent. Full paper not acquired; no workshop assignment is taken from it.'),
    ]
    manifests=[]
    for p in sorted(RAW.glob('source-downloads*/manifest.json')):
        for item in json.loads(p.read_text(encoding='utf-8')):
            manifests.append(dict(item,manifest_path=str(p.relative_to(ROOT)).replace('\\','/')))
    for e in entries:
        e['acquisitions']=[m for m in manifests if m['id']==e.get('asset_id')]
        e['rights_status']='rights-unverified; witnesses remain local-only'
    for e in entries:
        if e['id']=='O2019':
            e['rights_status']='explicit-license: repository cover states CC BY-NC-ND 4.0; local PDF and extracted text retained'
        if e['id']=='M2026v1':
            e['rights_status']='explicit-license: HTML links CC BY 4.0; local-only handling retained'
        if e['id']=='G2021':
            e['rights_status']='university record labels article CC BY; images require asset-level review'
    web=RAW/'source-downloads-2026-10-07-02/frenez-web-witness.txt'
    extra={'local_path':str(web.relative_to(ROOT)).replace('\\','/'),'bytes':web.stat().st_size,
           'sha256':hashlib.sha256(web.read_bytes()).hexdigest(),'route':'web tool fulltext preview excerpt; no copied excerpt in owned prose'}
    entries[8]['web_witness']=extra
    log=[
      {'queries':['Frenez 2018 Private person or public persona','Indus seals motif text association Rao Yadav 2013 Oakes 2017 2019','Green 2021 Indus seals social organization Kenoyer seal production standardization Ameri'],
       'outcome':'Located Yadav, Oakes, Frenez, Green, Ameri and Mahesh; opened available primary sources.'},
      {'queries':['Kenoyer Indus sites hectares Harappa Mohenjo Chanhudaro Kalibangan Lothal','Kalibangan hectares archaeology excavation','Banawali hectares Nausharo','Nausharo hectares Jarrige'],
       'outcome':'Located the Kenoyer chapter, Suryanarayan thesis and Treccani synthesis; did not acquire a numerical Banawali source.'},
      {'queries':['Rao Indus motif association','Rao Indus iconography statistical association','Rao field symbols Indus','Rao motif-text Indus'],
       'outcome':'Failed to identify the specifically requested Rao et al. motif–text test. Located Rao 2009/2018; Oakes supplies a verified direct association precedent.'},
      {'queries':['The Size of Indus Seals and its Significance','Mixed methodologies tiger seals Ameri Jamison 2022','Inscribed Unicorn Seals from Bagasra'],
       'outcome':'Located size chapter contents and two style precedents. Full size chapter and Ameri paper remain unreviewed.'},
      {'attempt':'Direct Smith2025 PDF download in an early ad hoc command',
       'url':'https://www.heritageuniversityofkerala.com/JournalPDF/Volume10/1.pdf','outcome':'Failed: remote connection reset. A second attempt is in the download manifest. This source was excluded from site inputs.'},
      {'attempt':'Web open of Mukhopadhyay 2019',
       'url':'https://www.nature.com/articles/s41599-019-0274-1','outcome':'Failed through inaccessible cookie authorization redirect; requests download later supplied full text.'},
      {'attempt':'Web open of Oakes repository PDF','outcome':'Web internal error; direct public repository download succeeded.'},
      {'attempt':'Dholavira nomination direct download and official Download File link',
       'url':'https://whc.unesco.org/en/documents/181028','outcome':'Direct download 403; web Download File internal error. No nomination area entered the model.'},
      {'attempt':'Recorded Frenez lecture','url':'https://youtu.be/1i9q17ld_jU',
       'outcome':'Lecture not independently viewed or transcribed. The research question came from the user; the published argument was located separately.'}
    ]
    result={'prepared_utc':datetime.now(timezone.utc).isoformat(),'sources':entries,'search_and_access_log':log,
            'all_download_attempts':manifests,'source_handling':'See repository knowledge/provenance/REDISTRIBUTION.md. No third-party rows, full texts or media in the owned directory.'}
    (OWN/'sources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(len(entries),'bibliographic records;',len(manifests),'download attempts')

if __name__=='__main__': main()
