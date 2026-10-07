"""Bibliographic, attribution and audit corrections specified by the dated review."""
from pathlib import Path
import copy
from build_corrections import ROOT, RAW, OLD, read, digest, tidy

def witness(s, path):
    p=ROOT/path;s.update(local_witness=p.relative_to(ROOT).as_posix(),sha256=digest(p));return s

def correct_sources(sources):
    ss={s['id']:s for s in sources}
    ss['frenez2023-caption']['venue']='Oxford Research Encyclopedia of Asian History, Oxford University Press; online 18 October 2023; DOI 10.1093/acrefore/9780190277727.013.595'
    ss['durrani1995-intro'].update(title='Excavations in the Gomal Valley (Rehman Dheri Excavation Report No. 2): Introduction',venue='Ancient Pakistan X, indexed pp. 1–13; printed folios i–xiii')
    ss['audouze-jarrige1979'].update(authors=['Françoise Audouze (given name provisional)','Catherine Jarrige'],note='Original chapter unopened. Françoise replaces unsupported Francine; exact given name and page extent need title-page confirmation. Miller cites pp. 213–221 and p. 220; Quivron cites 213–231. Preserve page conflict.')
    ss['kenoyer-meadow1999']['venue']='Lahore Museum Bulletin XII(1), pp. 1–11; scan includes cover, text pp. 1–7 and four unnumbered plates'
    ss['winkelmann2004']['venue']='Il Punto Edizioni, for the Ligabue Study and Research Centre, 2004, 201 pp.; contributor roles unresolved; book not opened'
    ss['miller1997']['venue']='In P. M. Rice (volume editor), Prehistory and History of Ceramic Kilns, Ceramics and Civilization VII, pp. 41–71. W. D. Kingery, series editor. American Ceramic Society, Westerville, Ohio; chapter header says Columbus.'
    ss['jarrige1995-report']['editor_role']='The four persons in authors are editors, not chapter authors.'
    ss['jarrige1995-report']['venue']='Karachi: Department of Culture and Tourism, Government of Sindh, in collaboration with the Department of Archaeology and Museums, Government of Pakistan; French Ministry of Foreign Affairs'
    ss['quivron1997'].update(url=ss['coningham2002']['url'],opened=False,access_status='original chapter not opened; bibliography and observations cited through opened Coningham 2002',
        locations_reviewed=['Coningham 2002 pp. 93–94 and bibliography p. 102; cited Quivron pages 45, 53, 55, 61 not independently opened'],
        note='Former institutional URL lists 2000–2023 items and does not establish this chapter. Chapter title, editors and pp. 45–62 are second-hand through Coningham 2002.')
    witness(ss['quivron1997'],ss['coningham2002']['local_witness'])
    ss['harappa-hearth-gallery']['locations_reviewed']=['Gallery pages 46 and 47 of 90; legacy URL identifiers 136 and 137 are not current slide numbers']
    ss['harappa-hearth-gallery']['venue']='Around the Indus in 90 Slides 2, pages 46–47 of 90, Harappa.com excavation photographs and captions'
    ss['gadd1932']['venue']='Proceedings of the British Academy 18; opened separately paginated offprint pp. 3–22. Original journal page span unconfirmed.'
    witness(ss['changizi2006'],'data/raw/2026-10-06-backward-chronology/web-17.json')
    ss['changizi2006']['note']='Full-text web response witness; the local HTML acquisitions are error/challenge pages.'
    witness(ss['coningham1996'],'data/raw/2026-10-06-backward-chronology/web-02.json')
    ss['coningham1996']['note']='Opened abstract in the preserved web response. A new author-project PDF attempt returned HTTP 403 challenge HTML, not the paper; full text still unopened.'
    ss['lal1960'].update(year=1960,printed_year=1962,year_display='1960 [printed 1962]',note='One work: Ancient India no. 16 carries nominal year 1960 and printing imprint 1962; postscript p. 3 explains the two-year delay. Article received 20 October 1960, p. 24. Do not count 1962 as a second study.')
    ss['kenoyer2004']['locations_reviewed']=['English manuscript PDF p. 15, Early Jorwe ranges; PDF p. 38, Inamgaon cart caption']
    for sid,loc in [('rajan-sivanantham2026-I','Printed pp. 10–11, 15–27, 69–74, 101–109, 132, 143–144, 153, 167, 181–201, 224, 226, 295, 265, 301'),('rajan-sivanantham2026-II','Printed pp. 1155, 1162, 1165 and Table 10.1 pp. 1173–1175')]:
        ss[sid]['locations_reviewed'].append(loc)
    def add(sid,authors,year,title,venue,url,status,opened,loc,note,path=None):
        s=dict(id=sid,authors=authors,year=year,title=title,venue=venue,url=url,access_status=status,opened=opened,
               locations_reviewed=loc,note=note,rights_status='rights-unverified; payload local-only')
        if path:witness(s,path)
        sources.append(s)
    archive=read(ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/acquisition-archive.json')[0]
    add('cisi2-1991',['Sayid Ghulam Mustafa Shah (editor)','Asko Parpola (editor)'],1991,'Corpus of Indus Seals and Inscriptions 2: Collections in Pakistan',
        'Annales Academiae Scientiarum Fennicae, Series B 241. Helsinki: Suomalainen Tiedeakatemia',archive['url'],'opened primary catalogue sections',True,
        ['Pirak printed pp. 379–386, data p. 446; especially p. 381 Pk-15–17 and p. 385 IIIA'],'Reused a local copy acquired by the evidence-census package; no copy downloaded. Pk-15–17 belong to IB. No forced concordance to Kenoyer Fig. 3.',archive['path'].replace('\\','/'))
    ac=read(RAW/'petrie2012-pdf.acquisition.json')
    add('petrie-magee2012',['Cameron A. Petrie','Peter Magee'],2012,'The Achaemenid Expansion to the Indus and Alexander’s Invasion of North-West South Asia',
        'Iranian Journal of Archaeological Studies 2(1), pp. 1–25; DOI 10.22111/ijas.2012.1054',ac['url'],'opened full publisher PDF',True,
        ['pp. 2, 4, 11; bibliography p. 22'],'Authors summarize their 2010 recalibration: III start 1460–1150, end potentially 1300/1200–760 BCE. The recalibration table itself is not in this opened paper.',ac['local_witness'])
    add('magee-petrie2010',['Peter Magee','Cameron A. Petrie'],2010,'West of the Indus–East of the Empire: The Archaeology of the Pre-Achaemenid and Achaemenid Periods in Baluchistan and the North-West Frontier Province, Pakistan',
        'In J. Curtis and St J. Simpson (eds.), The World of Achaemenid Persia: History, Art and Society in Iran and the Ancient Near East, pp. 503–522. London: I.B. Tauris',
        'https://api.pageplace.de/preview/DT0400.9780857718013_A23726039/preview-9780857718013_A23726039.pdf','opened publisher preliminaries only; chapter not opened',False,
        ['Contents p. x, chapter starts p. 503; chronology cited through Petrie and Magee 2012'],'No primary recalibration table recovered. Full-text searches saved in web-04, web-06 and web-08.',(RAW/'magee2010-preview.pdf').relative_to(ROOT).as_posix())
    add('jarrige-santoni1979',['Jean-François Jarrige','Marielle Santoni'],1979,'Fouilles de Pirak, Volume I: Texte',
        'Fouilles du Pakistan 2. Paris: Diffusion de Boccard. Volume II, Étude architecturale et figures, by Jean-François Enault',
        'https://www.si.edu/object/siris_sil_147830','bibliographic search record only; original report not opened',False,
        ['Bibliographic record; reported chronology through Dumarçay 1980 and Petrie/Magee 2012'],'Do not authenticate period mean dates seen only in reviewer snippets.',(RAW/'web-01.json').relative_to(ROOT).as_posix())
    add('dumarcay1980',['Jacques Dumarçay'],1980,'Jean-François Jarrige, Marielie Santoni : Fouilles de Pirak',
        'Bulletin de l’École française d’Extrême-Orient 67, pp. 341–343',
        'https://www.persee.fr/doc/befeo_0336-1519_1980_num_67_1_3351','opened publisher page 341 of report review',True,
        ['p. 341'],'Period I spans the eighteenth to thirteenth centuries BCE in this report review; this is not the original excavation table.',(RAW/'web-05.json').relative_to(ROOT).as_posix())
    add('allchin-coningham1995',['R. A. E. Coningham','F. R. Allchin'],1995,'The rise of cities in Sri Lanka',
        'In F. R. Allchin (ed.), The Archaeology of Early Historic South Asia: The Emergence of Cities and States. Cambridge University Press; p. 176 relevant; chapter page extent unconfirmed here',
        'https://www.cambridge.org/core/books/archaeology-of-early-historic-south-asia/','original chapter not opened; indexed book text and reviewer reference',False,
        ['p. 176, second-hand; indexed text in web-07'],'Radiocarbon placement 450–350 BCE retained as an unselected alternative. Neither precise lab/sample joins nor the primary chapter were opened.',(RAW/'web-07.json').relative_to(ROOT).as_posix())
    return sources

def correct_claims(claims):
    cc={c['id']:c for c in claims}
    cc['bet-dwarka-relation']['authors']='Sundaresh and A. S. Gaur; integrity challenged by Alok Tripathi (Tripathi, A. 1996)'
    cc['brahmi-distribution']['claim']='The opened 1996 abstract proposes a tentative mechanism for Brahmi development and spread without identifying merchant carriers.'
    cc['brahmi-distribution']['assessment']='Merchant attribution in third-party summaries is unverified because the full 1996 paper remains unopened. Deraniyagala discusses migrations and Semitic trading scripts as possible stimuli.'
    cc['tn-morphology'].update(claim='Rajan and Sivanantham propose a close Indus/graffiti relation and possible evolution of graffiti into Tamiḻi; graffiti first appear, then coexist with Tamiḻi and later disappear.',
        locations='2025 brochure p. 5; Volume I pp. 11, 265, 301',intermediate_evidence='Illustrated graffiti and Tamil-Brahmi corpora and regional ceramic sequences. Volume I p. 265 explicitly contrasts left-to-right Iron Age graffiti with right-to-left Indus pot texts.',
        assessment='Their resemblance/evolution proposal requires dated specimen matrices and complexity/position controls; the direction difference must enter the model.')
    cc['harappa-development']['missing']='Specimen-level feature trajectories and frequencies within subphases; extension from the Ravi-to-initial-urban Kot Diji sequence to later South Asian scripts is unverified.'
    cc['harappa-development']['locations']='Kenoyer 2006 pp. 10–15, especially Table 1 p. 10 and counts p. 14; Kenoyer and Meadow 2010 Table 1'
    cc['mahadevan-pairs']['locations']='Mahadevan 2001 pp. 379, 381'
    cc['mahadevan-pairs']['claim']='Mahadevan considers the resemblances too close to dismiss as accidental: A/B identical, C compared with a variant, D probably a variant (p. 381).'
    cc['brahmi-origins']['assessment']='Salomon p. 20 describes Indus derivation as endorsed particularly by D. C. Sircar; Pandey also suggests an Indus link (n. 51). His phonological-adaptation proposal is hedged on p. 30. Aramaic/West Asian derivation, indigenous derivation and mixed adaptation remain attributed positions.'
    cc['kharosthi-aramaic']['locations']='Salomon 1998 pp. 51–54 (derivation); p. 46 (early attestations)'
    cc['lal-bridge'].update(authors='B. B. Lal, 1960 [printed 1962], one work',
        claim='Compares megalithic symbols with pooled Harappan seal/sealing and Chalcolithic pottery signs; 47 shared types out of 53 megalithic and 55 earlier pooled types.',
        intermediate_evidence='Discussion bridge sites: Lothal B, Rangpur IIC/III, Navdatoli, Maheswar, Gilund/Ahar, Bahal/Tekwada, Brahmagiri–Maski and Sonpur/Rajghat. Prakash is illustrated elsewhere but not named as a bridge on pp. 21–23.',
        assessment='The 1960 issue and 1962 imprint are one study. The earlier pool combines object classes and periods; reconstruct each type\'s dated witnesses before a continuity test.')
    cc['early-tamil-brahmi']['locations']+='; Volume II pp. 1165, 1175 (Porunthal calibration); Salomon p. 35 n. 103 (Mahadevan second–first century BCE versus Dani first century CE)'
    cc['early-tamil-brahmi']['assessment']='Separate method-specific assessments: Volume II Porunthal ranges 580–520 and 560–410 BCE have unstated calibration convention; Volume I p. 11 claims seventh–sixth-century Tamiḻi. Individual grave/deposit associations remain contested.'
    for c in claims:
        if c['id'].endswith('-followup'):
            c['locations'] += '; lecture time codes are through the coordinator caption note, not an independent video review'
    cc['oral-merchants-followup']['claim']='Frenez says priests preferred oral transmission and writing was reintroduced by Buddhist merchants in the fifth century; BCE is inferred from the lecture context, not explicit in the caption phrase.'
    cc['oral-merchants-followup']['assessment']='Attributable lecture account. Allchin/Coningham 450–350 BCE and Porunthal reported 580–410 BCE overlap the fifth-century comparison; dates do not identify merchant carriers. Ashoka is the A/high historical endpoint.'
    cc['preseal-repertoire-followup']['assessment']='Quivron p. 275 distinguishes pottery and seal repertoires; p. 279 compares incised marks with about twenty of 396 Harappan characters. Exact frequencies and a dated shared repertoire remain untested.'
    cc['rehman-continuity-followup']['missing']='Normalize the lettered catalogue entries and independently recount phases. The likely 14/41 transposition may permit a five-phase matrix, but the replacement count is not authenticated.'
    return claims

def correct_audits(data):
    for name in ['lecture-claim-audit.json','contact-items.json','dating-details.json','visual-checks.json']:
        data[name]=tidy(data[name])
    la=data['lecture-claim-audit.json']
    for c in la['claims']:
        c['caption_location']+=' (through coordinator note)'
        if c['id']=='oral-merchants':
            c['statement']='Frenez says writing was reintroduced by Buddhist merchants in the fifth century after priestly preference for oral transmission; BCE is inferred from context.'
            c['assessment']='Compare with unselected Allchin/Coningham 450–350 BCE, Volume II Porunthal 580–520 and 560–410 BCE, and the A/high Ashokan endpoint. No merchant carriers identified by those dates.'
        if c['id']=='contact-paper':c['statement']+=' He also says some legends encode Sumerian names and others names neither Sumerian nor Akkadian.'
        if c['id']=='site-correction':
            c['assessment']='Rehman Dheri is supported by Frenez 2018 p. 171 n. 5 and Kenoyer/Meadow 2010 p. liv, naming CISI 2 Rhd-1. Button seal is their terminology for the rectangular two-hole object; the caption geography is wrong. The primary phase alternatives are IA/IB, not Period II.'
        if c['id'] in ['preseal-repertoire','early-seals','rehman-seal']:
            c['assessment']+=' Frenez 2018 p. 171 n. 5 and Kenoyer/Meadow 2010 p. liv support the Rehman Dheri button-seal attribution; the caption geography remains wrong.'
    for c in data['contact-items.json']['cases']:
        if c['id']=='ur-bm120573':
            c['source_locations']=[s.replace('p. 6','p. 5').replace('p.6','p. 5')for s in c['source_locations']]
            for d in c['dating_assessments']:
                d['source_location']=d['source_location'].replace('p.6','p. 5').replace('p. 6','p. 5')
        if c['id']=='bnf-cuneiform-stamp':c['images_reviewed']=True
        if c['id']in ['bnf-cuneiform-stamp','bahrain-tokens2026']:
            for d in c['dating_assessments']:d['grade']='D'
    dd=data['dating-details.json']
    dd['count_audit'].update(transposition_arithmetic={'printed_II':14,'candidate_II':41,'difference':27,'candidate_phase_sum':190},
        assessment='A 14/41 transposition is plausible; catalogue recount remains required before replacing the printed count.',
        unit_warning='p. 208 gives 190 stratified signs/sherds; printed phase totals sum to 163. Do not authenticate a corrected allocation solely from arithmetic.')
    dd['rehman_object54']={'registration':'BIV/25 Layer 6 Level 19; catalogue 54, bone, 31×28×4.5 mm',
        'primary_assignments':'1995 Table 1/Introduction p. vii: IA; Durrani 1988 p. 28: IB; Plate XVIIIA about 3200 BCE',
        'removed_error':'Former Period II local-to-main trench correlation misread a different trench section.',
        'button_seal_usage':'Frenez 2018 p. 171 n. 5; Kenoyer and Meadow 2010 p. liv, CISI 2 Rhd-1',
        'selected_narrow_date':None}
    dd['specimen_units']={'earlier_additions':193,'inscribed_sherds_and_sealing':191,'motif_specimens_without_surviving_script':2,
        'ids_without_script':['harappa-ravi-bone1521','harappa-kot-diji-elephant1533']}
    dd['daimabad_PRL420_correction']='Sali Table 2 p. 209 lists PRL-420 with PRL-426 in the lower Phase II layer; former upper-layer assignment corrected.'
