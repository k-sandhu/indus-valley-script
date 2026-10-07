"""Curated census observations. Numeric claims preserve the source's unit and scope."""
SOURCES={}
def s(key,title,authors,year,venue,url,access="opened_text",locator="",rights="Reuse terms unresolved; witness stays local-only"):
 SOURCES[key]=dict(id=key,title=title,authors=authors,year=year,venue=venue,url=url,access=access,locator=locator,reuse_terms=rights,quoted_words=0)
s("gadd1932","Seals of ancient Indian style found at Ur",["C. J. Gadd"],1932,"Proceedings of the British Academy 18: 191–210","https://ignca.gov.in/Asi_data/33779.pdf","opened_local_text","Reprint pp. 3–22, plates I–III; reused OCR in research/literature/sources/gadd1932_ocr.txt")
s("laursen2010","The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC",["Steffen Terp Laursen"],2010,"Arabian Archaeology and Epigraphy 21: 96–134","https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf",locator="Table 1; Figs. 10, 14–16",rights="Wiley copyright; PDF available to read, urllib download returned 403")
s("parpola2018","Indus Seals and Glyptic Studies: An Overview",["Asko Parpola"],2018,"In Marta Ameri, Sarah Kielt Costello, Gregg Jamison and Sarah Jarmer Scott, eds., Seals and Sealing in the Ancient World: Case Studies from the Near East, Egypt, the Aegean, and South Asia. Cambridge University Press, pp. 127–143 and plate IX","https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf","opened_local_text","Final proof June 2016; PDF pp. 5–6, 12 and bibliography")
s("cisi33","Corpus of Indus Seals and Inscriptions, Volume 3: New material, untraced objects, and collections outside India and Pakistan. Part 3: Indo-Iranian Borderlands (Eastern Iran, Turkmenistan, Tajikistan, Uzbekistan, Afghanistan)",["Asko Parpola (editor)","Petteri Koskikallio (editor)"],2022,"Annales Academiae Scientiarum Fennicae, Humaniora 386. Helsinki: Suomalainen Tiedeakatemia","https://orbi.uliege.be/bitstream/2268/333796/1/Desset%20F%202022%20in%20CISI%203.3%201763.pdf","opened_local_text","40-page author excerpt: contents v–vii, preface ix–xviii, François Desset essay xix–xxvi, bibliography. Catalogue plates themselves absent.")
s("cisi32","Corpus of Indus Seals and Inscriptions: 3.2 Shahr-i Sokhta; Mundigak; Mehrgarh, Nausharo, Sibri, Dauda-damb; Chanhudaro; Ahar, Balathal, Gilund; Kalibangan; Rojdi",["Asko Parpola (editor)","B. M. Pande (editor)","Petteri Koskikallio (editor)"],2019,"Annales Academiae Scientiarum Fennicae, Humaniora 383. Helsinki: Suomalainen Tiedeakatemia, 432 pp.","https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-32-shahr-i-sokhta-mundigak/","opened_metadata","Publication metadata; no whole-volume inspection")
s("nippur1993","Nippur III: Kassite Buildings in Area WC-1",["Richard L. Zettler"],1993,"Oriental Institute Publications 111. Chicago: Oriental Institute, University of Chicago","https://isac.uchicago.edu/publications/nippur-iii-kassite-buildings-area-wc-1","opened_local_text","pp. 81–82; catalogue 13 N 506, IM 78230; plate 89a–d",rights="Current ISAC landing page states CC BY-NC-ND 4.0; payload retained locally")
s("frankfort1933","Tell Asmar, Khafaje and Khorsabad: Second Preliminary Report of the Iraq Expedition",["Henri Frankfort"],1933,"Oriental Institute Communications 16. Chicago: University of Chicago Press","https://isac.uchicago.edu/publications/tell-asmar-khafaje-and-khorsabad-second-preliminary-report-iraq-expedition","opened_local_text","pp. 50–53, Figs. 32–33; As. 31-22")
s("salut2016","Bronze Age Salūt (ST1) and the Indus Civilization: new insights on regional interaction",["Dennys Frenez","Michele Degli Esposti","Sophie Méry","Jonathan Mark Kenoyer"],2016,"Proceedings of the Seminar for Arabian Studies 46: 107–124","https://www.harappa.com/sites/default/files/pdf/Bronze-Age-Indus-Connections.pdf","opened_local_text","pp. 110, 116–118; Figs. 9–10",rights="© Archaeopress 2016; all rights reserved; local-only PDF")
s("gonur2005","Gonur-Depe: City of Kings and Gods",["Viktor I. Sarianidi"],2005,"Ashgabat: Miras","https://margiana.su/publication/book/Gonur-Depe_City_of_Kings_and_Gods_2005.pdf","opened_local_text","pp. 258–259, Figs. 114–115; PDF spread 130")
s("gonur_project","Archäologische Forschungen in Gonur Depe",["Institute of Archaeological Sciences, University of Bern"],None,"Institutional project report","https://www.iaw.unibe.ch/research/ancient_near_eastern_archaeology/archaeologische_forschungen_in_gonur_depe/index_eng.html",locator="Excavation history and Partner/Projektteam sections")
s("kircho2008","Технико-технологический потенциал энеолитического населения Алтын-депе как основа становления раннегородской цивилизации",["L. B. Kircho","G. F. Korobkova","V. M. Masson"],2008,"Труды ИИМК РАН XXVIII. St Petersburg: European House, 370 pp.","https://www.old.archeo.ru/izdaniya-1/vagnejshije-izdanija/pdf/Altyn_technical_2008.pdf/view","opened_local_text","Plate 94.2; reused OXUS-SOURCE-02 acquisition; proposed impression class remains tentative")
s("konar2015","Indus Components in the Iconography of a White Marble Cylinder Seal from Konar Sandal South (Kerman, Iran)",["Massimo Vidale","Dennys Frenez"],2015,"South Asian Studies 31(1): 144–154. DOI 10.1080/02666030.2015.1008820","https://www.harappa.com/sites/default/files/pdf/Vidale%20%26%20Frenez%20_%20Konar%20Sandal%20seal.pdf",locator="Seal 2006IX001 and illustrations",rights="Taylor & Francis copyright; urllib download returned 403; web PDF opened")
s("hissar_iranica","TEPE HISSAR",["Robert H. Dyson, Jr."],2009,"Encyclopaedia Iranica; updated 4 January 2014","https://www.iranicaonline.org/articles/tepe-hissar/",locator="Excavation history; tablet paragraph; bibliography")
s("yahya_iranica","TEPE YAHYA",["C. C. Lamberg-Karlovsky"],2011,"Encyclopaedia Iranica","https://www.iranicaonline.org/articles/tepe-yahya/",locator="Excavations 1967–1975 and bibliography; author/year should be sampled against article header")
s("susa_iranica","SUSA i. EXCAVATIONS",["Jean Perrot"],None,"Encyclopaedia Iranica; header year unresolved in saved excerpt","https://www.iranicaonline.org/articles/susa-i-excavations/",locator="Campaign history and bibliography")
s("louvre2425","sceau cylindre: SB 2425; AS 41; CCO S. 299",["Musée du Louvre"],2026,"Collections database, updated 27 March 2026","https://collections.louvre.fr/en/ark%3A/53355/cl010176471",locator="Inventory; Inscriptions; Physical characteristics; Places and dates; Current location",rights="Images require acceptance of Louvre terms; open record is not an image reuse licence")
s("bm123208","stamp-seal: museum number 123208",["British Museum"],None,"Collection database","https://www.britishmuseum.org/collection/object/W_1932-1008-178","search_snippet","Museum number, production place Dilmun, findspot Ur; opening returned 403")
s("umma2021","“In the field”: The Project SAHI-Tell Jokha",["Drahoslav Hulínek"],2021,"International Association for Assyriology, Mar Shiprim, 22 January 2021 (posted by Stefania Ermidoro)","https://iaassyriology.com/in-the-field-the-project-sahi-tell-jokha/",locator="Seasons 2016, 2017, 2019, 2020; report of Harappan seal impressions during topographic survey")
s("umma_tosi","The Indus Civilization beyond the Indian Subcontinent",["Maurizio Tosi"],2022,"Reprinted in Madad Ali Sindhi, comp., Save Mohenjo Daro!, Government of Sindh, pp. 56–57; original date unresolved","https://www.harappa.com/blog/indus-seal-impression-umma-mesopotamia",locator="Historical sealing and 1931 Louvre-to-Ashmolean transfer")
s("frankfort_blog","Indus Cylinder Seals",["Harappa.com (editorial author not named)"],None,"Scholarly source excerpt","https://www.harappa.com/blog/indus-cylinder-seals",locator="Frankfort discussion of Tell Asmar cylinder")
s("kish_review","P. R. S. Moorey : Kish Excavations, 1923-1933.",["André Parrot"],1980,"Syria 57(2): 493–494","https://www.persee.fr/doc/syria_0039-7946_1980_num_57_2_6706_t1_0493_0000_2",locator="p. 493, Oxford/Field Museum expedition and final book")
s("miri_project","The site of Miri Qalat and the Kech-Makran (Balochistan, Pakistan) during the second half of the 3rd millennium BC",["Shelby White and Leon Levy Program for Archaeological Publications"],None,"Harvard University project page","https://whitelevy.fas.harvard.edu/site-miri-qalat-and-kech-makran-balochistan-pakistan-during-second-half-3rd-millennium-bc-0",locator="1990–1996 French mission under Roland Besenval; Aurore Didier publication project")
s("besenval1997","Entre le Sud-Est iranien et la plaine de l'Indus : le Kech-Makran. Recherches archéologiques sur le peuplement ancien d'une marche des confins indo-iraniens",["Roland Besenval"],1997,"Arts Asiatiques 52: 5–36. DOI 10.3406/arasi.1997.1399","https://www.persee.fr/doc/arasi_0004-3958_1997_num_52_1_1399",locator="Opened p. 5 only; do not use as a witness to Murda Sang")
s("murda_primary","5: The Third Millenium BCE: 3000 - 2500 BCE",["Ute Franke-Vogt"],None,"Archaeology of Southeastern Balochistan, Harappa.com","https://www.harappa.com/baluch/e5.html",locator="Murda Sang paragraphs, slides 53–62; discovered 1997, trial trenches 1998")
s("ornach_primary","Prehistoric Balochistan: Cultural Developments in an Arid Region",["Ute Franke"],None,"Harappa.com scholarly article introduction; original bibliographic date unresolved","https://www.harappa.com/content/prehistoric-balochistan-cultural-developments-arid-region",locator="Image 3 caption: Kinneru, Ornach valley; source article preview")
s("nindowari_parpola","The Harappan Unicorn in Eurasian and South Asian perspectives",["Asko Parpola"],2011,"In Toshiki Osada and Hitoshi Endo, eds., Linguistics, Archaeology and the Human Past, Occasional Paper 12. Kyoto: RIHN, pp. 125–188","https://www.harappa.com/content/harappan-unicorn-eurasian-and-south-asian-perspectives",locator="Nd-1 illustration caption, CISI 2 p. 419")
s("hajar1987","A Copper-Bronze Animal in Harappan Style from Bahrain: Evidence of Mercantile Interaction",["E. C. L. During Caspers"],1987,"Journal of the Economic and Social History of the Orient 30(1): 30–46","https://www.scribd.com/document/672690085/A-Copper-Bronze-Animal-in-Harappan-Style-From-Bahrain-Evidence-of-Mercantile-Interaction-E-C-L-During-Caspers-Journal-of-the-Economic-and-So",locator="p. 37 and note 23; al-Hajjar prism with Indus characters",rights="Third-party mirror of JSTOR text; rights unresolved; local-only witness")
s("sarazm1987","Découvertes récentes à Sarazm (R.S.S. du Tadjikistan) : attestation des relations au IIIe millénaire entre l'Asie centrale, l'Iran du Nord-Est et le Baluchistan",["Roland Besenval"],1987,"Comptes rendus des séances de l'Académie des Inscriptions et Belles-Lettres 131(2): page range unresolved","https://www.persee.fr/doc/crai_0065-0536_1987_num_131_2_14510",locator="First article page; research history")
s("shortughai_bnf","Fouilles de Shortughaï : recherches sur l'Asie centrale protohistorique",["Henri-Paul Francfort"],1989,"Mémoires de la Mission archéologique française en Asie centrale 2, I–II. Paris: Diffusion de Boccard","https://catalogue.bnf.fr/ark%3A/12148/cb366410725","opened_metadata","Bibliographic record")
s("bat_project","The Site of Bat",["ArchaeOman project"],None,"German archaeological project website","https://www.archaeoman.de/en/der-fundort-bat/",locator="Project/site history")
s("failaka_intro","Failaka/Dilmun: The Second Millennium Settlements. 5: The Beads (Introduction)",["Author not resolved in excerpt"],2023,"Aarhus University Press; year inferred from catalogue and requires header verification","https://unipress.dk/media/19153/failaka-vol-5_the-beads_introduction.pdf",locator="p. 7: Danish 1958–1963, Johns Hopkins 1973–1974, French 1984–1985, Kuwaiti-Danish 2008–2017; Højlund")
s("failaka_cuneiform","Inscriptions cunéiformes de Failaka / Cuneiform inscriptions from Failaka",["Jean-Jacques Glassner"],1984,"In Failaka. Fouilles françaises 1983. Travaux de la Maison de l'Orient 9. Lyon: MOM, pp. 31–50","https://www.persee.fr/doc/mom_0766-0510_1984_rpm_9_1_2040?pageId=T1_32",locator="p. 32; independent cuneiform catalogue")
s("ummnar1995","The Island of Umm-an-Nar. 2. The Third Millennium Settlement",["Karen Frifelt"],1995,"Jutland Archaeological Society Publications 26:2. Højbjerg: Jysk Arkæologisk Selskab, 260 pp.","https://en.unipress.dk/udgivelser/i/the-island-of-umm-an-nar-2-the-third-millennium-settlement/","opened_metadata","Publisher record")
s("jas2022","Jutland Archaeological Society: Catalogue 2022",["Jutland Archaeological Society"],2022,"Publisher catalogue","https://jyskarkaeologiskselskab.dk/wp-content/uploads/2022/01/JAS_catalogue_2022.pdf","search_snippet","Umm an-Nar volumes; Qala'at al-Bahrain I–II; open failed")
s("sokhta2019","Seals and Seal Impressions from Shahr-i Sokhta (Sistan, Iran), 3rd Millennium BC",["Massimo Vidale","Alessandra Lazzari"],2019,"In CISI 3.2; pages unresolved","https://iris.cnr.it/handle/20.500.14243/408755","opened_metadata","CNR repository record; PDF restricted to authorised users")
for key,num,title in [("susa_unesco","1455","Susa"),("sokhta_unesco","1456","Shahr-i Sokhta"),("qalat_unesco","1192","Qal’at al-Bahrain – Ancient Harbour and Capital of Dilmun"),("hili_unesco","1343","Cultural Sites of Al Ain (Hafit, Hili, Bidaa Bint Saud and Oases Areas)"),("bat_unesco","434","Archaeological Sites of Bat, Al-Khutm and Al-Ayn"),("sarazm_unesco","1141","Proto-urban Site of Sarazm")]:
 s(key,title,["UNESCO World Heritage Centre; State Party nomination"],None,"World Heritage property record","https://whc.unesco.org/en/list/"+num+"/",locator="Description and Outstanding Universal Value",rights="Description CC BY-SA IGO 3.0; individual image credits vary")
 s(key+"_maps",title+" — Maps",["UNESCO World Heritage Centre; State Party nomination"],None,"Geographical data","https://whc.unesco.org/en/list/"+num+"/maps/",locator="Geographical data table",rights="Coordinate attribution retained; image/map rights not assumed")
s("failaka_unesco","Failaka Island: A Palimpsest of Human Civilizations",["National Council for Culture, Art and Letters, Kuwait"],2025,"UNESCO Tentative List 6800, submitted 29 January 2025","https://whc.unesco.org/en/tentativelists/6800/",locator="Coordinates; excavation history")
s("ummnar_unesco","Settlement and Cemetery of Umm an-Nar Island",["National Council of Tourism and Antiquities, UAE"],2012,"UNESCO Tentative List 5660","https://whc.unesco.org/en/tentativelists/5660/",locator="Province, coordinates and description")
s("hissar_tgn","Tepe Hisar (deserted settlement), TGN 6005886",["Getty Research Institute"],None,"Thesaurus of Geographic Names","https://www.getty.edu/vow/TGNFullDisplay?english=N&find=7005100&nation=&place=&subjectid=6005886",locator="Coordinates and hierarchical position")
s("janabiyah_tgn","Janabiyah (ancient site), TGN 7503923",["Getty Research Institute"],None,"Thesaurus of Geographic Names","https://www.getty.edu/vow/TGNFullDisplay?english=Y&find=Helsinki&nation=Finland&place=&subjectid=7503923",locator="Coordinates and hierarchical position")
# The next entries were located through citations, not read in full.
s("moorey1978","Kish Excavations, 1923–1933. With a microfiche catalogue of the objects in Oxford. Excavated by the Oxford-Field Museum, Chicago Expedition to Iraq, 1923–1933",["P. R. S. Moorey"],1978,"Oxford: Clarendon Press","https://www.persee.fr/doc/syria_0039-7946_1980_num_57_2_6706_t1_0493_0000_2","cited_in_opened_source","Parrot review p. 493; Zettler 1993 pp. 81–82, note 4 refers pp. 26–27 and fiche 2 C03")
s("nindowari2011","Nindowari, Pakistan : La culture de Kulli, ses origines et ses relations avec la civilisation de l’Indus",["Jean-François Jarrige","Gonzague Quivron","Catherine Jarrige"],2011,"Paris: Ginkgo Éditeur","https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf","cited_in_opened_source","Parpola bibliography, PDF p. 27; CISI 3.3 preface p. x")
s("potts2001","Excavations at Tepe Yahya, Iran, 1967–1975: The Third Millennium",["D. T. Potts"],2001,"Bulletin of the American School of Prehistoric Research 45. Cambridge, MA: Peabody Museum, Harvard University","https://www.iranicaonline.org/articles/tepe-yahya/","cited_in_opened_source","Bibliography; Pittman chapter pp. 231–268 in CISI 3.3 bibliography")
s("schmidt1937","Excavations at Tepe Hissar, Damghan",["Erich F. Schmidt"],1937,"Philadelphia: University of Pennsylvania Press","https://www.iranicaonline.org/articles/tepe-hissar/","cited_in_opened_source","Bibliography")
s("masson1988","Altyn-Depe",["V. M. Masson"],1988,"Translated by Henry N. Michael. Philadelphia: University Museum, University of Pennsylvania","https://commons.library.stonybrook.edu/amar/147/","search_snippet","Final monograph located; not acquired")
s("kjaerum1983","Failaka/Dilmun: The Second Millennium Settlements. 1.1: The Stamp and Cylinder Seals: Plates and Catalogue Descriptions",["Poul Kjærum"],1983,"Jutland Archaeological Society, Aarhus","https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf","cited_in_opened_source","Laursen table 1 nos. 12–13; original catalogue nos. 319, 279")
s("qalat1994","Qala’at al-Bahrain. 1. The Northern City Wall and the Islamic Fortress",["Flemming Højlund","H. Hellmuth Andersen"],1994,"Jutland Archaeological Society, 511 pp.","https://jyskarkaeologiskselskab.dk/wp-content/uploads/2022/01/JAS_catalogue_2022.pdf","search_snippet","Publisher catalogue; original pages uninspected")
s("qalat1997","Qala’at al-Bahrain. 2. The Central Monumental Buildings",["Flemming Højlund","H. Hellmuth Andersen"],1997,"Jutland Archaeological Society, 288 pp.","https://jyskarkaeologiskselskab.dk/wp-content/uploads/2022/01/JAS_catalogue_2022.pdf","search_snippet","Publisher catalogue")
s("saar2005","The Early Dilmun Settlement at Saar",["Robert Killick","Jane Moon"],2005,"London-Bahrain Archaeological Expedition; publisher details unresolved","https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf","cited_in_opened_source","Laursen bibliography; settlement report is distinct from cemetery")
s("saar2001","Early Dilmun Seals from Saar: Art and Commerce in Bronze Age Bahrain",["Harriet Crawford"],2001,"London: London-Bahrain Archaeological Expedition / Archaeology International; imprint requires verification","https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf","cited_in_opened_source","Laursen table 1 and references")
s("tello1948","Tello : vingt campagnes de fouilles (1877–1933)",["André Parrot"],1948,"Paris: Albin Michel","https://commons.library.stonybrook.edu/amar/66/","search_snippet","Final excavation synthesis")
s("woolley1934","Ur Excavations. Volume II: The Royal Cemetery",["C. Leonard Woolley"],1934,"London and Philadelphia: British Museum and University Museum","https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/oip37.pdf","search_snippet","Bibliographic citation in Brett seals catalogue; seal plates 192–216")
s("hajar1983","Triangular Stamp Seals from the Arabian Gulf and Their Indus Valley Connection",["E. C. L. During Caspers"],1983,"Annali dell’Istituto Universitario Orientale di Napoli 43: 661–670","https://www.scribd.com/document/672690085/A-Copper-Bronze-Animal-in-Harappan-Style-From-Bahrain-Evidence-of-Mercantile-Interaction-E-C-L-During-Caspers-Journal-of-the-Economic-and-So","cited_in_opened_source","1987 article p. 37 note 23")

def e(value,source,loc): return dict(value=value,source=source,location=loc)
def count(n,cls,source,loc,year,basis="objects",scope="minimum documented specimens",note="",include=True):
 return dict(count=n,object_class=cls,source=source,location=loc,count_date=year,basis=basis,scope=scope,note=note,include_in_indus_minimum=include)
ROWS=[]
def row(name,region,country,aliases,sources,local=None,province=None):
 r=dict(site=name,region=region,country=country,aliases=aliases,sources=sources,local_labels=local or [],province=province,counts=[],publications=[],campaigns=[],problems=[],metadata={},later=[],coordinates=None,final_report_identified=False,coverage="No reviewed object-to-object join; coverage fraction undefined.",cisi=None,holdings=None,scope="named_batch_site")
 ROWS.append(r);return r
# Mesopotamia
r=row("Ur","Mesopotamia","Iraq",["Tell el-Muqayyar","Ur(i)"],["gadd1932","laursen2010"],["Ur"])
r["campaigns"]=[e("Gadd's objects derive from Woolley's campaigns 1923–1932; joint British Museum/University Museum expedition. Whole campaign register still needs the final reports.","gadd1932","Reprint catalogue nos. 1–16")]
r["publications"]=["gadd1932","woolley1934"];r["final_report_identified"]=True
r["counts"]=[count(16,"Indus-style seals, mixed inscribed and uninscribed","gadd1932","Reprint p. 14: nos. 1–16",1932,scope="catalogue subtotal",include=False),count(6,"Gulf-type seals with Indus or uncertain signs","laursen2010","Fig. 15, p. 126; Gadd nos. 2–5, 15–16",2010,note="Includes questioned writing; retain class as reported."),count(1,"Indus-style stamp seal with cuneiform","gadd1932","No. 1, BM 120573/U.7683, reprint pp. 3–5",1932,include=False),count(1,"cylinder seal with Indus-like signs","gadd1932","No. 7, U.11958",1932,note="Sign identification disputed; excluded from strict minimum.",include=False)]
r["holdings"]=e("British Museum numbers supplied for part of the catalogue, including BM 123208; other entries have Ur excavation numbers only.","gadd1932","Nos. 1–18")
r["problems"]=["Reconcile 16 mixed catalogue seals with 6 Gulf inscribed specimens and the 5 local families; do not call all 16 inscriptions."]
r["metadata"]=dict(findspot="partial",stratum_or_phase="partial",absolute_dates="partial",dimensions="yes",material="yes",photographs="yes",drawings="partial",registration_numbers="yes",source="gadd1932",location="Nos. 1–16; plates I–III")
r=row("Kish","Mesopotamia","Iraq",["Tell al-Uhaymir","Kiš"],["nippur1993","kish_review"],["Kish"])
r["counts"]=[count(2,"canonical square Indus stamp seals","nippur1993","p. 82; note 4, Moorey pp. 26–27 and fiche 2 C03",1993)]
r["campaigns"]=[e("Oxford–Field Museum expedition, 1923–1933; reviewed book records campaigns under Langdon, Mackay and Watelin. Season-by-season director attribution remains incomplete.","kish_review","p. 493")]
r["publications"]=["moorey1978"];r["final_report_identified"]=True;r["holdings"]=e("Oxford objects are catalogued on microfiche; excavated material was divided among Oxford, Baghdad and Chicago. Holdings of the two inscribed seals require accession-level checking.","kish_review","p. 493")
r["problems"]=["Two local families and two published seals agree numerically; accession match remains unverified."]
r=row("Nippur","Mesopotamia","Iraq",["Nuffar","Niffer"],["nippur1993"],["Nippur"])
r["counts"]=[count(1,"canonical square Indus stamp seal","nippur1993","pp. 81–82; 13 N 506, IM 78230; plate 89a–d",1993)]
r["publications"]=["nippur1993"];r["final_report_identified"]=True
r["campaigns"]=[e("Area WC-1 investigations in the 13th and 14th seasons, 1975–1976, Oriental Institute expedition directed by McGuire Gibson; exact discovery day unresolved.","nippur1993","Introduction and object register 13 N 506")]
r["holdings"]=e("Iraq Museum IM 78230, as registered in the 1993 report; present physical location not independently checked.","nippur1993","Catalogue 13 N 506")
r["metadata"]=dict(findspot="yes",stratum_or_phase="yes",absolute_dates="partial",dimensions="yes",material="yes",photographs="yes",drawings="yes",registration_numbers="yes",source="nippur1993",location="pp. 81–82, catalogue: Level III, Locus 6, Floor 3; 2.0 × 2.0 × 1.0 cm; plate 89a–d")
r["problems"]=["Seal is residual in a later building; the find layer cannot date its manufacture directly."]
r=row("Tell Asmar","Mesopotamia","Iraq",["Eshnunna","Ashnunnak"],["frankfort1933","frankfort_blog"])
r["counts"]=[count(1,"uninscribed Indus-related cylinder seal","frankfort1933","pp. 50–52, Fig. 32; As. 31-22",1933,include=False)]
r["campaigns"]=[e("1930–1932 Iraq Expedition, Henri Frankfort, Oriental Institute of Chicago; this report covers the second campaign.","frankfort1933","Title and introduction")]
r["publications"]=["frankfort1933"];r["problems"]=["No authenticated Indus-script specimen recovered by this search; a final glyptic catalogue still needs inspection."]
r["metadata"]=dict(findspot="yes",stratum_or_phase="yes",absolute_dates="partial",dimensions="partial",material="partial",photographs="yes",drawings="partial",registration_numbers="yes",source="frankfort1933",location="pp. 50–53, Fig. 32; Akkadian houses; material tentatively glazed steatite")
r=row("Girsu/Tello","Mesopotamia","Iraq",["Girsu","Tello","Telloh"],["laursen2010","nippur1993"],["Girsu","Tello"])
r["counts"]=[count(2,"classic square Indus seals","laursen2010","Fig. 14, p. 125; Thureau-Dangin 1925 p. 99 and Amiet 1988 p. 195 no. 1",2010),count(1,"Gulf-type seal with signs","laursen2010","Fig. 15, p. 126; Sarzec/Heuzey pp. 321–322, pl. 30.3a–b",2010)]
r["publications"]=["tello1948"];r["final_report_identified"]=True
r["campaigns"]=[e("Twenty campaigns 1877–1933 are the stated scope of Parrot's final synthesis; de Sarzec's early excavation publication underlies the Gulf seal.","tello1948","Title; Laursen Fig. 15 reference")]
r["problems"]=["Local Girsu and Tello labels each contain one family; overlap is unreviewed. Zettler p. 82 note 4 describes Tello provenances as supposed."]
r=row("Umma","Mesopotamia","Iraq",["Tell Jokha","Tell Djokha","Tell Umma","Jokha","Jhoka"],["umma_tosi","umma2021","nippur1993"],["Tell Umma"])
r["counts"]=[count(1,"clay sealing impressed by inscribed Indus seal","umma_tosi","Historical sealing paragraphs; reprint pp. 56–57",2022,note="Dealer-reported provenance; not an excavated Umma context.")]
r["campaigns"]=[e("SAHI project began 2016 under Drahoslav Hulínek with Iraqi partners; seasons 2016, 2017, 2019 and 2020; Geneva/Bern Sumerologists joined the 2017 survey.","umma2021","Project and season paragraphs")]
r["publications"]=["umma2021","umma_tosi"];r["holdings"]=e("Historical sealing transferred from Louvre to Ashmolean in 1931.","umma_tosi","Transfer paragraph")
r["later"]=[e("Harappan seal impressions reported in the post-2016 topographic survey; no itemised count. Coordinator's Frenez 2023 witness associates a seal image with 2017, but original p. 59 fig. 6.61 remains unrecovered.","umma2021","Survey finds paragraph")]
r["problems"]=["Historical market sealing and new survey finds require separate provenance records; no final inventory recovered."]
r=row("Babylon","Mesopotamia","Iraq",["Bābil"],["laursen2010","gadd1932"])
r["scope"]="added_from_literature";r["counts"]=[count(1,"Gulf-type seal with signs","laursen2010","Fig. 15, p. 126; Collon 1994 p. 216 correction of Gadd no. 17",2010)]
r["problems"]=["Added through Laursen's corrected provenance list. Gadd 1932 treated no. 17 as unprovenanced; independently inspect Collon's correction and accession."]
# Iran
r=row("Susa","Iranian Plateau","Iran",["Suse","Shush"],["louvre2425","laursen2010","susa_iranica","susa_unesco"],["Susa"],"Khuzestan")
r["counts"]=[count(1,"Indus-inscribed cylinder seal","louvre2425","SB 2425; script field Indus",2026),count(1,"Gulf-type seal with signs","laursen2010","Fig. 15, p. 126; Amiet 1972 pl. 153/1643",2010)]
r["campaigns"]=[e("de Morgan 1897–1912; de Mecquenem 1913–1939 with wartime interruption; Ghirshman 1946–1967; Steve 1967–1968; Perrot 1968–1979, French delegation/mission.","susa_iranica","Excavation history")]
r["holdings"]=e("Louvre SB 2425, currently displayed in Richelieu room 231, case 4.","louvre2425","Current location; updated 27 March 2026")
r["metadata"]=dict(findspot="partial",stratum_or_phase="partial",absolute_dates="yes",dimensions="yes",material="yes",photographs="yes",drawings="no",registration_numbers="yes",source="louvre2425",location="SB 2425: site Suse; discovery 1898–1906; attributed Suse IV B; 2.3 cm height, 1.6 cm diameter; two images")
r["problems"]=["Two published classes are a selected minimum; square seals including SB 5614 remain to be reconciled. No complete Indus inventory obtained."]
r=row("Tepe Yahya","Iranian Plateau","Iran",["Tappeh Yahya"],["cisi33","yahya_iranica","salut2016"],["Tepe Yahya"],"Kerman")
r["counts"]=[count(1,"Indus-related seal-impressed pottery sherd","cisi33","Preface p. xi; TY-106",2022,note="CISI calls this Indus; Harvard 2004 presentation questions sign matches. Reviewed photograph needed."),count(112,"mixed catalogue entries, multiple scripts and glyptics","cisi33","Contents p. vi; TY-1 to 112, pp. 1–40",2022,basis="catalogue entries",scope="numbered sequence",include=False),count(27,"Proto-Elamite tablet catalogue entries","cisi33","Desset pp. xx–xxi; TY-8 to TY-34; text gives 26 or 27 tablets",2022,basis="catalogue entries",include=False)]
r["cisi"]=e("CISI 3.3 (2022), pp. 1–40, TY-1 to 112; TY-106 explicitly identified as seal impression. Four earlier assignment volumes do not supply this site's complete range.","cisi33","Contents p. vi and preface p. xi")
r["campaigns"]=[e("Harvard excavations 1967–1975 directed by C. C. Lamberg-Karlovsky.","yahya_iranica","Excavation history")]
r["publications"]=["potts2001"];r["final_report_identified"]=True
r["problems"]=["Catalogue includes Proto-Elamite tablets and non-Indus seals. Local 1/maximum 106 measures neither catalogue completeness nor Indus coverage."]
r=row("Shahr-i Sokhta","Iranian Plateau","Iran",["Shahr-e Sokhteh","Shahr-i-Sokhta","Shahri Sokhta"],["cisi33","cisi32","sokhta2019","sokhta_unesco"],province="Sistan and Baluchestan")
r["counts"]=[count(444,"mixed seals and impressions added to catalogue","cisi33","Contents p. vi: SiS-185 to 628, pp. 197–284",2022,basis="catalogue entries",scope="inclusive endpoint arithmetic",include=False),count(1,"Proto-Elamite tablet","cisi33","Desset p. xx; SiS-1, CISI 3.2 p. 1",2022,include=False)]
r["cisi"]=e("CISI 3.2 (2019), SiS-1 to 184 inferred from continuation beginning 185; whole earlier page range unrecovered. CISI 3.3 pp. 197–284 continues SiS-185 to 628.","cisi33","Contents p. vi; Desset p. xx")
r["campaigns"]=[e("Italian mission from 1967 under Maurizio Tosi; early reports cover 1967 and 1968. Catalogue preface describes later Iranian work and Italian archive material.","cisi33","Preface p. x; bibliography Tosi 1968 and 1969")]
r["later"]=[e("2021 phase-10 accounting-tablet claim reported in Tehran Times 23 January 2022; Desset awaits full publication. No authenticated Indus inscription established.","cisi33","Desset p. xx")]
r["holdings"]=e("Italian mission documents, photographs and drawings are archived in Museo delle Civiltà, Rome; this does not establish custody of every physical object.","cisi33","Bibliography abbreviation MAI, PDF p. 36")
r["problems"]=["628 is a mixed catalogue endpoint, not an Indus inscription count. Restricted 2019 chapter and absent plates prevent a class-by-class tally."]
r=row("Konar Sandal/Jiroft","Iranian Plateau","Iran",["Konar Sandal South","KSS","Konar Sandal North","KSN","Jiroft"],["konar2015","cisi33"],province="Kerman")
r["counts"]=[count(1,"uninscribed Indus-related marble cylinder seal","konar2015","2006IX001",2015,include=False),count(4,"Linear Elamite documents","cisi33","Desset p. xxii; KSS-380 to 383",2022,include=False),count(383,"mixed South catalogue entries","cisi33","Contents p. vi; pp. 42–133",2022,basis="catalogue entries",include=False),count(11,"mixed North catalogue entries","cisi33","Contents p. vi; pp. 134–136",2022,basis="catalogue entries",include=False)]
r["cisi"]=e("CISI 3.3, KSS-1 to 383 pp. 42–133; KSN-1 to 11 pp. 134–136. Pittman introductory essay xxxiv–xlii.","cisi33","Contents pp. v–vi")
r["campaigns"]=[e("2002–2008 excavations directed by Yousef Majidzadeh; Holly Pittman supplied the complete glyptic packet for CISI 3.3.","cisi33","Preface p. xiv")]
r["publications"]=["konar2015","cisi33"];r["problems"]=["Cylinder iconography and four Linear Elamite texts provide separate evidence classes; no authenticated Indus inscription enumerated."]
r=row("Tepe Hissar","Iranian Plateau","Iran",["Tepe Hisar","Tappeh Hesār","Tappa Ḥiṣār"],["hissar_iranica","cisi33","hissar_tgn"],province="Semnan")
r["counts"]=[count(109,"seals and seal impressions in Schmidt's publications","cisi33","Preface p. xv",2022,basis="published catalogue items",include=False),count(280,"mixed seals and impressions in revised corpus","cisi33","Preface p. xv; TH-1 to 280 pp. 296–358",2022,basis="catalogue entries",include=False)]
r["cisi"]=e("CISI 3.3 pp. 296–358, TH-1 to 280; Pittman essay lvii–lix.","cisi33","Contents pp. v–vi")
r["campaigns"]=[e("Schmidt, University of Pennsylvania, 1931–1932; 1972 surface survey; 1976 Pennsylvania/Turin/ICAR restudy; 1995 Iranian salvage excavation.","hissar_iranica","Excavation history")]
r["publications"]=["schmidt1937"];r["final_report_identified"]=True
r["later"]=[e("1995 unpublished tablets reported by Dyson; CISI 3.3 p. xvi questions whether H76-122/TH-132 is writing at all.","cisi33","Preface p. xvi")]
r["holdings"]=e("Schmidt's finds divided between Pennsylvania Museum and Iran; archive plates annotate UPM accessions or Persia. Object-specific custody remains unresolved.","cisi33","Preface p. xv")
r["problems"]=["The change 109 to 280 incorporates older archive photographs; it is not 171 new excavated Indus inscriptions."]
# Gulf and Oman
r=row("Failaka","Persian Gulf","Kuwait",["Faylaka","Tell F3","Tell F6"],["laursen2010","failaka_intro","failaka_cuneiform","failaka_unesco"],["Failaka"])
r["counts"]=[count(2,"Gulf/Dilmun seals with signs including pseudo-script","laursen2010","Fig. 15; Kjærum nos. 279 and 319",2010,note="No. 279 is technically Dilmun type; pseudo-script requires separate review.")]
r["campaigns"]=[e("Danish mission 1958–1963; Johns Hopkins 1973–1974; French 1984–1985; renewed Kuwaiti-Danish 2008–2017 under Flemming Højlund.","failaka_intro","p. 7")]
r["publications"]=["kjaerum1983","failaka_cuneiform"];r["final_report_identified"]=True
r["problems"]=["Local 2 agrees with the inclusive 2010 count; classification and two accession joins remain unverified. Cuneiform catalogue kept separate."]
r=row("Qala'at al-Bahrain","Persian Gulf","Bahrain",["Qal’at al-Bahrain","Qalat al Bahrain","Qalaat al-Bahrain"],["laursen2010","qalat_unesco","jas2022"],["Qala'at al-Bahrain"])
r["counts"]=[count(2,"Gulf-type seals with signs","laursen2010","Table 1 nos. 6–7; Fig. 15",2010)]
r["publications"]=["qalat1994","qalat1997"];r["final_report_identified"]=True
r["problems"]=["Published 2 versus local 1 flags a join target. Whole catalogue and later-season Indus totals unrecovered."]
r=row("Saar","Persian Gulf","Bahrain",["Sar","Saar Cemetery","Sār"],["laursen2010","saar2001"],["Saar"])
r["counts"]=[count(1,"Gulf-type seal with signs, cemetery","laursen2010","Table 1 no. 9, Al-Sindi 1999 no. 182",2010)]
r["publications"]=["saar2001","saar2005"];r["final_report_identified"]=True
r["problems"]=["Cemetery object must be kept distinct from settlement catalogue. Exact local accession not established."]
r=row("Tell Abraq","Persian Gulf","United Arab Emirates",["Tall Abraq"],["laursen2010"])
r["counts"]=[count(1,"uninscribed ivory Gulf-type imitation","laursen2010","Table 1 no. 121; Fig. 16; Potts 2000 p. 122",2010,include=False)]
r["problems"]=["A complete final-report witness and authenticated Indus-script inventory were not recovered; foreign pottery and uninscribed seal cannot supply that count."]
r=row("Hili","Persian Gulf","United Arab Emirates",["Hili 8","Hili N"],["salut2016","hili_unesco"],province="Abu Dhabi (Al Ain)")
r["campaigns"]=[e("Hili 8 investigations in the late 1970s recognised Indus pottery; Serge Cleuziou and Philippe Gouin are named in the paper's acknowledgements.","salut2016","p. 119")]
r["problems"]=["Published contact pottery and twin relief on tomb Hili 1059 do not establish an Indus inscription. ENHG excavation talk pages timed out."]
r=row("Ras al-Jinz","Persian Gulf","Oman",["Ra's al-Junayz","Ra’s al-Jinz","RJ-2"],["salut2016","laursen2010"],["Ra's al-Junayz"])
r["counts"]=[count(1,"copper stamp seal with Indus signs","salut2016","p. 117; RJ-2; Cleuziou/Tosi 2000 pp. 59–60 fig. 7a",2016),count(1,"seal with uncertain pseudo-twins motif","laursen2010","Fig. 10j, p. 112; RJ-2.1",2010,include=False)]
r["campaigns"]=[e("Joint Hadd Project of Serge Cleuziou and Maurizio Tosi; RJ-2 reports cited in 1988, 1990 and 2000. Full season register unresolved.","laursen2010","Fig. 14, p. 125")]
r["problems"]=["Local 3 pottery faces require primary specimen reconciliation; two pottery illustrations in later syntheses do not prove a total of three. Ras al-Hadd and Ras al-Jinz must remain geographically distinct."]
r=row("Salut","Persian Gulf","Oman",["Salūt","ST1","Salut ST1"],["salut2016"],["Salut"])
r["counts"]=[count(1,"Indus-style chlorite stamp seal with Indus signs","salut2016","pp. 116–117, Fig. 9",2016,note="Western manufacture is the authors' inference from chlorite and technique."),count(2,"seal-impressed pottery fragments","salut2016","pp. 117–118, Fig. 10 and 2015–2016 rim sherd",2016,basis="fragments",scope="reported fragments, possibly same vessel",include=False),count(1,"seal-impressed pottery vessel","salut2016","pp. 117–118",2016,scope="minimum vessels",note="Two fragments may derive from one jar.")]
r["campaigns"]=[e("Italian Mission, University of Pisa, with Sultan's cultural-affairs office, began tower ST1 excavation in 2010; publication includes the ongoing 2015–2016 season.","salut2016","pp. 110, 118")]
r["later"]=[e("Second identically impressed rim fragment found in the 2015–2016 season; authors allow that both fragments belong to one jar.","salut2016","p. 118")]
r["metadata"]=dict(findspot="partial",stratum_or_phase="partial",absolute_dates="yes",dimensions="partial",material="yes",photographs="yes",drawings="yes",registration_numbers="partial",source="salut2016",location="ST1 context pp. 110–111; seal and sherd pp. 116–118, Figs. 9–10")
r["problems"]=["Local TAG is a seal-impressed jar fragment. Two impressions do not establish two vessels or an excavated tablet."]
r=row("Bat","Persian Gulf","Oman",["Bāt"],["bat_project","salut2016","bat_unesco"])
r["campaigns"]=[e("ArchaeOman describes Danish work from 1972 and later German projects; complete director/campaign register remains unresolved.","bat_project","Site history")]
r["problems"]=["Indus pottery and square Dilmun-type seals are contact evidence; no authenticated Indus text count recovered."]
r=row("Umm an-Nar","Persian Gulf","United Arab Emirates",["Umm al-Nar","Umm en-Nar","Umm an-Nār Island"],["ummnar_unesco","ummnar1995","jas2022"],province="Abu Dhabi")
r["campaigns"]=[e("Danish Aarhus Museum settlement excavations 1959–1965; burial documentation 1959–1961.","jas2022","Publisher synopsis")]
r["publications"]=["ummnar1995"];r["final_report_identified"]=True
r["problems"]=["Island and cultural-period label must be separated. Final monograph located but unread; inscription count unresolved."]
# Central Asia
r=row("Altyn Depe","Central Asia","Turkmenistan",["Altyn-depe","Altin Depe"],["cisi33","parpola2018","kircho2008"],["Altyn Depe"])
r["counts"]=[count(1,"square seal with two Indus signs","cisi33","Preface p. xi: Alt-90; Parpola 2018 PDF pp. 5–6",2022),count(1,"uninscribed swastika seal","cisi33","Preface p. xi: Alt-49",2022,include=False),count(142,"mixed catalogue entries","cisi33","Contents p. vii: Alt-1 to 142, pp. 370–404",2022,basis="catalogue entries",include=False)]
r["campaigns"]=[e("Systematic Russian excavation from 1965; Masson and Kircho's publications underpin the corpus.","cisi33","Preface p. xvi")]
r["cisi"]=e("CISI 3.3 pp. 370–404, Alt-1 to 142; Alt-90 is the inscribed seal.","cisi33","Contents p. vii and preface p. xi")
r["publications"]=["masson1988"];r["final_report_identified"]=True;r["problems"]=["Local maximum 90 is valid CISI numbering, but most catalogue entries are different classes. Kircho Plate 94.2 clay object is a tentative impression, without authenticated Indus text."]
r=row("Gonur Depe","Central Asia","Turkmenistan",["Gonur-depe","Goňur depe","Gonur North"],["gonur2005","gonur_project","cisi33"],["Gonur Depe"])
r["counts"]=[count(1,"elephant stamp seal with Indus signs","gonur2005","pp. 258–259, Fig. 114",2005),count(1,"cuneiform-inscribed cylinder seal","gonur2005","p. 259, Fig. 115",2005,include=False)]
r["campaigns"]=[e("Sarianidi test trenches 1972 and 1974; broad excavation from 1988; north palace 1991–1995 and 2002–2004; excavation led by Sarianidi until 2013 and later Nadezhda Dubova, with Turkmen partners and Bern project.","gonur_project","Excavation history, Partner and Projektteam")]
r["publications"]=["gonur2005"];r["final_report_identified"]=True
r["cisi"]=e("CISI 3.3 preface says roughly 400 Gonur seals were promised but unavailable for publication. No Gonur catalogue range in contents.","cisi33","Preface p. xi")
r["problems"]=["Indus seal found autumn 2004 in room 19, Area 9, Water Temple. General corpus of about 400 seals is not an Indus count; earlier token group excluded."]
r["metadata"]=dict(findspot="yes",stratum_or_phase="partial",absolute_dates="partial",dimensions="no",material="yes",photographs="yes",drawings="no",registration_numbers="partial",source="gonur2005",location="pp. 258–259, Fig. 114; room 19, Area 9; no object accession or dimensions in these pages")
r=row("Sarazm","Central Asia","Tajikistan",["Sarazm"],["cisi33","sarazm1987","sarazm_unesco"])
r["counts"]=[count(5,"one cylinder and four possible stamp seals, mixed corpus","cisi33","Contents pp. v, vii: Sz-1 to 5, pp. 496–498; Mutin/Razzokov/Razzokov essay lx–lxx",2022,basis="catalogue entries",include=False)]
r["cisi"]=e("CISI 3.3 pp. 496–498, Sz-1 to 5; no Indus-script identification supplied by inspected preface.","cisi33","Contents pp. v, vii")
r["campaigns"]=[e("Isakov's Tajik archaeological project and French collaboration are documented in the 1987 report; full season history requires the nomination dossier.","sarazm1987","Opening article page")]
r["problems"]=["Five glyptic entries include uncertain stamp-seal attribution; no Indus inscription count verified."]
# Extra local labels: retain their literal membership and correct geography explicitly.
r=row("Karzakan","Persian Gulf","Bahrain",["Karzakkan","Karzakkān","Hamad Town burial field"],["laursen2010"],["Karzakan"])
r["scope"]="local_region_extra";r["counts"]=[count(3,"Gulf-type seals with signs or pseudo-signs","laursen2010","Table 1 nos. 8, 11, 56; Fig. 15",2010,note="Inclusive classification: no. 11 pseudo-script; no. 56 two V-shaped marks. Not three established Indus texts.")]
r["holdings"]=e("Bahrain National Museum; catalogue and new acquisitions examined by Laursen.","laursen2010","pp. 99, 104")
r["problems"]=["Match museum/field numbers before interpreting local 3 versus inclusive published 3."]
r=row("Hajar","Persian Gulf","Bahrain",["al-Hajjar","Al Hajar"],["hajar1987"],["Hajar"])
r["scope"]="local_region_extra";r["counts"]=[count(1,"locally made triangular prism seal with Indus characters","hajar1987","p. 37, note 23; Weisgerber 1981 fig. 54",1987)]
r["publications"]=["hajar1983"];r["problems"]=["Hajar-to-al-Hajjar identification is provisional without registration-number join. Local class TAB differs from published prism seal."]
r=row("Luristan","Iranian Plateau","Iran",["Lorestān","Lorestan"],["laursen2010"],["Luristan"])
r["scope"]="regional_provenance_label";r["counts"]=[count(1,"Gulf-type seal with signs","laursen2010","Fig. 15; Amiet 1973 pl. 23a–b",2010)]
r["problems"]=["Regional attribution does not identify excavation site or coordinates. Separate the unprovenanced Western Iranian Linear Elamite seal, table 1 no. 28."]
r=row("Janabiyah","Persian Gulf","Bahrain",["Janabiya","Janabivah"],["laursen2010","janabiyah_tgn"],["Janabiyah"],"Northern / Ash Shamālīyah")
r["scope"]="local_region_extra";r["counts"]=[count(1,"Gulf-type seal with signs","laursen2010","Table 1 no. 10; Fig. 15",2010)]
r["holdings"]=e("Bahrain National Museum, acquisition discussed with Karzakan specimens.","laursen2010","p. 99")
r["problems"]=["1999/2005 museum acquisition dates are not securely assigned to each specimen; do not infer excavation year."]
r=row("Kalba","Persian Gulf","United Arab Emirates",["Kalbā","K4"],["laursen2010"],["Kalba"])
r["scope"]="local_region_extra";r["counts"]=[count(1,"bifacial seal with possible pseudo-twins motif","laursen2010","Fig. 10i, p. 112",2010,include=False)]
r["problems"]=["One uncertain motif does not provide an authenticated Indus inscription count. Context described as supposedly early second millennium."]
r=row("Dilmun","Persian Gulf","Bahrain / regional label",["Dilmun (production place)"],["gadd1932","bm123208"],["Dilmun"])
r["scope"]="regional_provenance_label";r["counts"]=[count(1,"Gulf-type seal excavated at Ur, BM 123208","gadd1932","No. 16, reprint pp. 13–14",1932,scope="provenance correction; counted under Ur",include=False)]
r["holdings"]=e("British Museum BM 123208.","gadd1932","No. 16")
r["problems"]=["Local Dilmun production-region label masks Ur findspot. Keep local row; do not add this object to archaeological totals twice."]
r=row("Shortughai","Central Asia","Afghanistan",["Shortughaï","Shortugai","Shortugaï"],["cisi33","parpola2018","shortughai_bnf"],["Shortughai"])
r["scope"]="local_region_extra";r["counts"]=[count(1,"canonical Indus stamp seal","parpola2018","PDF p. 6",2018),count(84,"mixed seals and graffiti catalogue entries","cisi33","Contents p. vii, Sh-1 to 84 pp. 509–523",2022,basis="catalogue entries",include=False),count(2,"seals, only one verified here as inscribed","cisi33","Preface p. xv",2022,include=False)]
r["cisi"]=e("CISI 3.3 pp. 509–523, Sh-1 to 84. Local Sh-69 falls within a sequence including many graffiti.","cisi33","Contents p. vii; preface p. xv")
r["publications"]=["shortughai_bnf"];r["final_report_identified"]=True
r["campaigns"]=[e("French archaeological mission, Henri-Paul Francfort, 1976–1979; final report 1989.","shortughai_bnf","Bibliographic record; seasons require checking against report introduction")]
r["problems"]=["Local 1/69 is not inscription coverage. Full graffiti classification and exact Sh-69 plate absent from excerpt."]
r=row("Nindowari-damb","Iranian Plateau (local assignment)","Pakistan",["Nindowari","Nindōwari"],["cisi33","nindowari_parpola","parpola2018"],["Nindowari-damb"],"Balochistan")
r["scope"]="south_asian_cross_reference";r["counts"]=[count(1,"inscribed seal Nd-1, explicitly illustrated","nindowari_parpola","Image caption: CISI 2 p. 419",2011)]
r["campaigns"]=[e("Jean-Marie Casal, 1962–1965, French archaeological mission.","cisi33","Preface p. x")]
r["publications"]=["nindowari2011"];r["final_report_identified"]=True
r["cisi"]=e("CISI 2 p. 419 verified by Nd-1 citation; full site range unresolved. CISI 3.3 preface says Nindowari material also included in 3.2.","nindowari_parpola","Image caption; CISI 3.3 preface p. x")
r["problems"]=["Pakistan site retained because coordinator assigned its rows to Iranian Plateau; avoid duplicate work with regional batch. Two local families, Nd-1 and Nd-2, exceed the one specimen independently located here."]
r=row("Miri Qalat","Iranian Plateau (local assignment)","Pakistan",["Miri Kalat","Mīrī Qalāt"],["miri_project","besenval1997","cisi33"],["Miri Qalat"],"Balochistan (Kech-Makran)")
r["scope"]="south_asian_cross_reference";r["campaigns"]=[e("French Archaeological Mission in Makran, Roland Besenval with Pakistan Department of Archaeology and Museums, 1990–1996.","miri_project","Project description")]
r["problems"]=["Local MQ-11 and MQ-12 are two seals; no opened publication supplies a matched total. Publication project identified; final Indus-period report unrecovered."]
r["cisi"]=e("CISI 3.3 preface transfers Kech-Makran material to planned 3.4. Local MQ identifiers alone cannot establish the volume/page range.","cisi33","Preface p. xi")
r=row("Sibri","Iranian Plateau (local assignment)","Pakistan",["Sibrī"],["cisi33","cisi32","parpola2018"],["Sibri"],"Balochistan")
r["scope"]="south_asian_cross_reference";r["cisi"]=e("CISI 2 pp. 411–413 cover BMAC-type seals, as cited by Parpola; CISI 3.2 includes remaining Sibri material, but exact range unrecovered.","parpola2018","PDF p. 12; CISI 3.3 preface p. x")
r["campaigns"]=[e("Jarrige's French mission sequence at Mehrgarh, Nausharo and Sibri, 1975–2002; Sibri-only season breakdown unresolved.","cisi33","Preface p. x")]
r["problems"]=["Local Sb-4 must be checked against an actual photograph; cited BMAC cylinders do not establish Indus inscription count."]
r=row("Ornach area","Iranian Plateau (local assignment)","Pakistan",["Kinneru (candidate identification)","Ornach valley"],["ornach_primary"],["Ornach area"],"Balochistan")
r["scope"]="south_asian_cross_reference";r["counts"]=[count(1,"Indus seal from Kinneru, Ornach valley","ornach_primary","Image 3 caption",None,note="Caption identifies find locality; local family match not established.")]
r["problems"]=["Kinneru provides a more specific published candidate findspot; exact match to local Ornach fragment, campaign, coordinates and custody unverified."]
r=row("Murda Sang","Iranian Plateau (local assignment)","Pakistan",["Murda-Sang"],["murda_primary"],["Murda Sang"],"Balochistan (Kanrach valley)")
r["scope"]="south_asian_cross_reference";r["campaigns"]=[e("Discovered 1997 and trial trenched 1998; Ute Franke-Vogt's project account documents the work. Precise director/institution allocation unresolved.","murda_primary","Murda Sang paragraphs, slides 53–62")]
r["problems"]=["Local pottery face is damaged and illegible; opened excavation narrative supplies no inscription inventory. Earlier assumption of Makran provenance was corrected to Kanrach valley."]
# Coordinates are copied at source precision; most sites need a dedicated georeference witness.
coords={
"Susa":("N32 11 22.05 E48 15 22.94","susa_unesco_maps","1455-001, archaeological complex"),
"Shahr-i Sokhta":("N30 35 38 E61 19 40","sokhta_unesco_maps","1456"),
"Qala'at al-Bahrain":("N26 14 3.99 E50 31 5.99","qalat_unesco_maps","1192ter-001, Core zone 1"),
"Hili":("N24 17 34.38 E55 47 23.69","hili_unesco_maps","1343-007, archaeological park; not every Hili subsite"),
"Sarazm":("N39 30 28.4 E67 27 31.4","sarazm_unesco_maps","1141rev"),
"Failaka":("N29 26 E48 20","failaka_unesco","Tentative List 6800, island-scale coordinate; not Tell F3/F6"),
"Umm an-Nar":("N24.43969 E54.51425","ummnar_unesco","Tentative List 5660"),
"Tepe Hissar":("N36.1500 E54.3500","hissar_tgn","TGN 6005886; minute precision"),
"Janabiyah":("N26.1800 E50.4730","janabiyah_tgn","TGN 7503923; published decimal rounding")}
for r in ROWS:
 if r["site"] in coords:
  v,k,loc=coords[r["site"]];r["coordinates"]=e(v,k,loc)

# Header corrections made by inspecting the saved live responses before aggregation.
SOURCES['yahya_iranica'].update(authors=['Daniel Thomas Potts'],year=2004,venue='Encyclopaedia Iranica; updated 13 April 2016',locator='Excavation history and bibliography')
SOURCES['susa_iranica'].update(authors=['Hermann Gasche'],year=2009,venue='Encyclopaedia Iranica; updated 9 October 2015')
SOURCES['sarazm1987']['venue']='Comptes rendus des séances de l’Académie des Inscriptions et Belles-Lettres 131(2): 441–456'
SOURCES['failaka_intro'].update(year=None,venue='Aarhus University Press; excerpt does not resolve year or author')
SOURCES['gonur2005']['venue']='Ashgabat, 2005; publisher imprint requires title-page verification'
