"""Build a source ledger from declared readings and preserved acquisition records.

The declared scopes are human inspection records, not inferred from downloads.
All third-party witnesses and text derivatives remain local-only.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-11-societal-persistence/literature'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(relative, role='primary_witness', dependency=False):
    path = ROOT / relative
    return dict(path=relative, sha256=sha(path), bytes=path.stat().st_size,
                role=role, reused_collaborator_witness=dependency,
                redistribution='local-only')


sources = []
observations = []


def source(ident, title, authors, year, citation, url, kind, scope,
           loci, mechanism, recommendation, caveat, doi=None, selected=True,
           rights='rights-unverified; local-only', edition=None):
    sources.append(dict(
        source_id=ident, title=title, authors=authors, publication_year=year,
        citation=citation, primary_url=url, doi=doi, work_type=kind,
        selected_primary_work=selected, access_depth='selected primary passages' if selected else 'limited lead or publisher description',
        inspected_scope=scope, supporting_loci=loci,
        mechanism_summary=mechanism, author_recommendation=recommendation,
        interpretive_limit=caveat, rights_observation=rights,
        redistribution='local-only', edition_note=edition,
        acquisition_attempts=[], witnesses=[], derivatives=[]))


def obs(ident, number, locator, statement, category='author argument', supports=None):
    observations.append(dict(observation_id=f'O-{ident}-{number}', source_id=ident,
        locator=locator, statement=statement, category=category,
        interpretation_scope=supports or 'This observation supports the stated mechanism or scope; it supplies no Harappan parameter estimate.'))


source('L01', 'The Urban Revolution', ['V. Gordon Childe'], 1950,
       'The Town Planning Review 21(1):3–17',
       'https://faculty.washington.edu/plape/citiesaut11/readings/Childe-urban%20revolution%201950.pdf',
       'original archaeological synthesis',
       'Title and opening p3; selected printed pp11–12 and16–17, PDF14–15 and19–20. Article occupies pp3–17; intervening plates cause the PDF offset.',
       ['printed pp11–12', 'printed pp16–17'],
       'Specialists depend on surplus and exchange; metalworking cities can depend on distant raw materials and complementary producers.',
       'No distinct future-research prescription extracted from the selected passages.',
       'The historical typology assumes centralized surplus and other institutions. Its dated claims about Harappan palaces/granaries are not adopted as excavation evidence.')
obs('L01', 1, 'printed pp11–12', 'The proposed urban division of labor requires food transfers to non-food-producing specialists.')
obs('L01', 2, 'printed pp16–17', 'The argument connects long-distance raw-material exchange, industrial specialization and interdependence; later societies can inherit accumulated material and cultural resources.')

source('L02', 'Social complexity and sustainability', ['Joseph A. Tainter'], 2006,
       'Ecological Complexity 3:91–103; online13 February2006',
       'https://research.fs.usda.gov/download/treesearch/61158.pdf',
       'author theoretical synthesis and viewpoint',
       'Title/abstract and introductory pp91–92; selected conclusions and strategic responses pp99–101, PDF9–11. No complete reanalysis of the historical cases.',
       ['printed pp99–101'],
       'Problem solving can accumulate costs; subsidies, deferred expenditure and information arrangements change how those costs are borne.',
       'Become aware of accumulated costs, examine subsidies and deferred costs, connect costs with benefits through effective information, and reconsider expensive problem-solving arrangements.',
       'The selected argument supplies conditional cost mechanisms, not an inevitable collapse trajectory or a fitted ancient cost curve.',
       doi='10.1016/j.ecocom.2005.07.004')
obs('L02', 1, 'printed pp99–100', 'The strategic responses include paying costs, obtaining subsidies, shifting/defering costs and improving links between costs and benefits.', 'explicit author prescription')

source('L03', 'Resilience and Stability of Ecological Systems', ['C. S. Holling'], 1973,
       'Annual Review of Ecology and Systematics 4:1–23; IIASA reprint RP-73-003',
       'https://pure.iiasa.ac.at/id/eprint/26/7/RP-73-003.pdf',
       'original ecological theory and case synthesis',
       'Introduction printed pp1–2/PDF5–6 and synthesis pp17–20/PDF21–24; complete report acquired but remaining pages not claimed read.',
       ['printed pp1–2', 'printed pp17–20'],
       'Persistence of relationships can coexist with variation; stability around one equilibrium and survival through disturbance are separate properties.',
       'Management should preserve options, heterogeneity and capacity to accommodate change, with attention to regional dispersal and uncertain system structure.',
       'The ecological cases do not establish a universal urban cycle or an archaeological survival probability.',
       doi='10.1146/annurev.es.04.110173.000245')
obs('L03', 1, 'printed pp1–2 and17–20', 'The argument distinguishes return to equilibrium from persistence of relationships and recognizes open-system dispersal and alternative stability domains.')

source('L04', 'Understanding the Complexity of Economic, Ecological, and Social Systems', ['C. S. Holling'], 2001,
       'Ecosystems 4:390–405',
       'https://alnap.cdn.ngo/media/documents/holling-complexity-econecol-socialsys-2001.pdf',
       'original cross-system theoretical synthesis',
       'Title/abstract; selected printed p394 and pp398–400, PDF5 and9–11. Primary article reproduced on an NGO host; host is not the publisher.',
       ['printed p394', 'printed pp398–400'],
       'Potential, connectedness and adaptive capacity interact across scales; accumulated skills, trust and networks affect reorganization.',
       'Use cross-scale relationships and opportunities for experiment and reorganization in understanding adaptive change.',
       'The adaptive cycle is a heuristic; the selected material does not justify assigning every society a fixed four-stage chronology.',
       doi='10.1007/s10021-001-0101-5')
obs('L04', 1, 'printed pp398–400', 'Cross-scale remember/revolt relationships, poverty and rigidity traps, and accumulated skills and trust are parts of the proposed framework.')

source('L05', 'Resilience, Adaptability and Transformability in Social–ecological Systems',
       ['Brian Walker', 'C. S. Holling', 'Stephen R. Carpenter', 'Ann Kinzig'], 2004,
       'Ecology and Society 9(2):5', 'https://ecologyandsociety.org/vol9/iss2/art5/inline.html',
       'original conceptual framework',
       'Publisher HTML introduction and definitions of resilience, adaptability and transformability; retained text lines72–97. Later explanatory cases are outside the declared reading.',
       ['Introduction; definitions before Explanation'],
       'Actors can adjust within a regime or form a different system when the existing arrangement becomes untenable.',
       'Define the system, its state variables and desired outcome before assessing resilience and transformation.',
       'A change that preserves residents or livelihoods can end a particular institutional or urban configuration.',
       doi='10.5751/ES-00650-090205')
obs('L05', 1, 'Introduction; definitions of adaptability and transformability', 'Adaptability concerns adjustment within the present system; transformability concerns creating a different system when the present one is untenable.')

source('L06', 'Resilience Thinking: Integrating Resilience, Adaptability and Transformability',
       ['Carl Folke', 'Stephen R. Carpenter', 'Brian Walker', 'Marten Scheffer', 'Terry Chapin', 'Johan Rockström'], 2010,
       'Ecology and Society 15(4):20', 'https://research.fs.usda.gov/download/treesearch/42598.pdf',
       'author conceptual synthesis',
       'Glossary/table on PDF3 and selected text on PDF4–7: specified/general resilience, transformation across scales and conclusion.',
       ['PDF3 glossary', 'PDF4–7, specified/general resilience and transformation'],
       'Small-scale transformation can support larger-scale persistence; experiments, learning and alternatives can alter what continues.',
       'Attend to general resilience and to learning and transformation across scales, beyond responses to one specified shock.',
       'The retained PDF has article pagination rather than ordinary journal page numbers; its case summaries were not independently reanalyzed.',
       doi='10.5751/ES-03610-150420')
obs('L06', 1, 'PDF4–7', 'The synthesis permits transformation at one scale to maintain resilience at another and connects this to learning and experimentation.')

source('L07', 'A Framework to Analyze the Robustness of Social-ecological Systems from an Institutional Perspective',
       ['John M. Anderies', 'Marco A. Janssen', 'Elinor Ostrom'], 2004,
       'Ecology and Society 9(1):18', 'https://ecologyandsociety.org/vol9/iss1/art18/inline.html',
       'original institutional robustness framework',
       'Selected publisher introduction/framework and interactions at operational/collective-choice levels; retained text lines215–256 for the latter.',
       ['Framework: four components and links', 'Interactions at operational and collective-choice levels'],
       'Resources, users, infrastructure and infrastructure providers form linked relationships; provider-user feedback affects contributions and maintenance.',
       'Examine links and incentives connecting users with public infrastructure providers and specify boundary and time scale.',
       'A focal resource can decline while users substitute another resource; robustness is relative to the chosen outcome and boundary.',
       doi='10.5751/ES-00610-090118')
obs('L07', 1, 'Framework and operational/collective-choice interactions', 'The framework explicitly includes infrastructure providers and user-provider contribution/benefit links alongside resources and resource users.')
obs('L07', 2, 'Operational/collective-choice interactions, retained text lines215–256', 'Users can withhold contributions when providers fail to supply useful infrastructure; substitution and chosen boundaries change what counts as failure.')

source('L08', 'A General Framework for Analyzing Sustainability of Social-Ecological Systems', ['Elinor Ostrom'], 2009,
       'Science 325:419–422;24 July2009', 'https://www.dpi.inpe.br/gilberto/cursos/cst-317/papers/ostrom_sustainability.pdf',
       'original diagnostic framework and synthesis',
       'Article title/abstract p419 and selected leading text on pp420–422; PDF2–5 contains the article, with the end of a preceding article above its title on PDF2.',
       ['printed pp419–422, selected passages'],
       'Resource systems, units, users and governance interact; group size has different effects depending on transaction costs and management work.',
       'Build comparable quantitative and qualitative databases with nested variables, heterogeneous costs/benefits and explicit spatial and temporal scales.',
       'The framework supports diagnosis and comparison; the selected cross-case summaries do not identify an ancient governance form.',
       doi='10.1126/science.1172133')
obs('L08', 1, 'printed pp420–421', 'The proposed nested framework includes resource, user and governance variables; the effect of user numbers depends on the work and other variables.')
obs('L08', 2, 'printed p422', 'The author calls for comparable qualitative/quantitative data and models of heterogeneous costs and benefits among governments, communities and individuals.', 'explicit author prescription')

source('L09', 'The persistence of ancient settlements and urban sustainability',
       ['Michael E. Smith', 'José Lobo', 'Matthew A. Peeples', 'Abigail M. York', 'Benjamin W. Stanley', 'Katherine A. Crawford', 'Nicolas Gauthier', 'Angela C. Huster'], 2021,
       'Proceedings of the National Academy of Sciences 118:e2018155118', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8157985/',
       'archaeological conceptual synthesis and illustrative comparisons',
       'JATS body paragraphs7–30 and31–34: outcome types, duration/data problems and research agenda. Europe PMC XML replaces a failed PMC challenge; no supporting dataset reanalysis.',
       ['JATS s1, paragraphs7–14', 'JATS s3, paragraphs26–30', 'JATS s4, paragraphs31–34'],
       'Occupation, population scale, institutions and culture can persist differently; geography, demography and collective action are candidate explanations.',
       'Standardize archaeological data, assemble interdisciplinary comparisons and develop theory connecting settlement duration with institutional, demographic and geographic features.',
       'Illustrative duration figures are not a complete random settlement sample. Selected main text supplies no quantified initial stocks, import limits or repair schedules.',
       doi='10.1073/pnas.2018155118', rights='Observed CC BY-NC-ND4.0 notice in primary JATS; raw/derivatives kept local-only')
obs('L09', 1, 'JATS s1, body paragraphs7–14', 'The paper distinguishes occupation, demographic scale, institutions and culture as four persistence outcomes.')
obs('L09', 2, 'JATS s4, body paragraphs31–34', 'The proposed agenda links standardized archaeological databases with theory and tests of geography, demography and collective action.', 'explicit author prescription')
obs('L09', 3, 'Inspected main-text scope, paragraphs7–34', 'These selected passages discuss duration and possible explanations without quantifying the joint initial-output/import/renewal inputs required by the proposed conservation bound.', 'bounded scope assessment', 'This is a statement about inspected passages, not proof that the entire field omits maintenance or that supplementary data lack every such quantity.')

source('L10', 'Housing inequality and settlement persistence are associated across the archaeological record',
       ['Dan Lawrence', 'Amy Bogaard', 'Gabriela Cervantes Quequezana', 'Francesca Chelazzi', 'Gary M. Feinman', 'Adam S. Green', 'Helena Hamerow', 'Jessica Munson', 'Scott G. Ortman', 'Amy E. Thompson'], 2025,
       'Proceedings of the National Academy of Sciences 122:e2400696122', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12036995/',
       'comparative archaeological observational study',
       'Primary main-text web rendering and JATS Methods paragraphs22–24, Results paragraph6, Discussion selected paragraphs16–18 and Outlook paragraphs20–21. No dataset/model rerun.',
       ['JATS s8, paragraphs23–24, Settlement Persistence', 'Results paragraph6', 'Outlook paragraphs20–21'],
       'Housing area disparity, settlement scale and occupation duration are compared; the associations do not establish a universal inequality threshold.',
       'Use complete settlement systems to distinguish network-wide gains from extraction benefiting some settlements at others expense.',
       'Duration can miss contractions or short gaps. The study does not estimate the service demand, stock/output ceiling and import ceiling needed for our proposed bound.',
       doi='10.1073/pnas.2400696122', rights='Observed CC BY4.0 notice in primary JATS; raw/derivatives kept local-only')
obs('L10', 1, 'Materials and Methods > Settlement Persistence; JATS s8, paragraphs23–24', 'Persistence is an episode of substantial permanent occupation ending at total abandonment; changes in size/importance can lie inside an episode, while reoccupation begins another episode and squatter occupation is excluded.')
obs('L10', 2, 'Results paragraph6; Methods > Settlement Persistence', 'Dating resolution differs across regions and can conceal short abandonment; regional experts supplied duration estimates from varied evidence.')
obs('L10', 3, 'Outlook paragraphs20–21', 'The authors call for data on complete settlement systems because a large settlement advantage can coexist with costs imposed on smaller settlements.', 'explicit author prescription')

source('L11', 'Integrating adaptation pathways and Ostrom’s framework for sustainable governance of social-ecological systems in a changing world',
       ['Jean-Baptiste Pichancourt', 'Antoine Brias', 'Anne Bonis'], 2025,
       'PeerJ 13:e18938', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11867035/',
       'original integrated formal framework and modeled application',
       'Primary introduction and Table1; JATS selected paragraphs14,31–38,85–87,91–95,99–101. Coupled pathways and concluding limitations inspected; full numerical experiment not reproduced.',
       ['Table1', 'JATS paragraphs31–38', 'JATS paragraphs91–95'],
       'Nested collective/constitutional actions alter viable pathways in coupled systems, with providers, institutions, infrastructure, knowledge and external assistance represented.',
       'Include incremental costs of moving between constitutional/collective arrangements; distinguish service preferences, changing environment and institutions in practical applications.',
       'This is a close direct predecessor. The authors report insufficient transition-cost data; a feasible modeled pathway does not authenticate an ancient sequence.',
       doi='10.7717/peerj.18938', rights='Observed primary JATS Creative Commons Attribution notice; raw/derivatives kept local-only')
obs('L11', 1, 'Table1; JATS paragraphs31–38', 'The coupled framework includes capital/infrastructure replacement, storage, facilities, knowledge and institutional interventions supporting viable pathways.')
obs('L11', 2, 'JATS paragraphs92–93', 'The authors state that data were insufficient for costs of transitions between collective/constitutional arrangements and recommend incorporating incremental transition costs.', 'explicit author prescription')

source('L12', 'Demography and Cultural Evolution: How Adaptive Cultural Processes Can Produce Maladaptive Losses—The Tasmanian Case', ['Joseph Henrich'], 2004,
       'American Antiquity 69(2):197–214', 'https://coevolution.fas.harvard.edu/sites/g/files/omnuum5841/files/culture_cognition_coevol_lab/files/henrich_2004-2.pdf',
       'original cultural-learning model and historical application',
       'Abstract printed p197/PDF2 and selected model pp200–202/PDF5–7; model assumptions and effective interacting population read. Historical archaeological claims not independently audited.',
       ['printed pp200–202'],
       'Under the declared biased/noisy social-learning law, access to a larger interacting skill pool can offset transmission loss.',
       'The selected abstract speculates about applying the model to variability in adaptive cultural evolution; no separately inspected research-design prescription extracted.',
       'Model-specific thresholds do not identify a universal minimum population. The historical Tasmanian interpretation remains an author application, not a new result here.')
obs('L12', 1, 'printed pp200–202', 'The formal mechanism concerns the effective pool of interacting social learners and skill transmission under stipulated imitation errors, rather than census population alone.')

source('L13', 'Partial connectivity increases cultural accumulation within groups', ['Maxime Derex', 'Robert Boyd'], 2016,
       'Proceedings of the National Academy of Sciences 113(11):2982–2987', 'https://maximederex.github.io/assets/pdf/derex2016.pdf',
       'original controlled behavioral experiment',
       'Abstract/design printed pp2982–2983, results pp2984–2985 and discussion/Methods opening p2986, PDF1–5. Remaining detailed methods not claimed read.',
       ['printed pp2984–2986'],
       'In a path-dependent computer task, partial connectivity preserved diverse solution branches that could later recombine; complete connection fostered early convergence.',
       'Investigate learning structure, fitness landscapes and contacts among partially separated groups when explaining cultural accumulation.',
       'The experiment demonstrates a conditional mechanism, not that fragmentation always helps or that all ancient skills have this task structure.',
       doi='10.1073/pnas.1518798113')
obs('L13', 1, 'printed pp2984–2985', 'Equal-sized partially connected groups retained alternative productive branches in the declared task; payoff-biased copying in fully connected groups led to convergence.')
obs('L13', 2, 'printed p2986, discussion and Methods opening', 'The authors propose future theoretical comparison of task landscapes, population structure and cultural-learning biases; participants were university students in a controlled computer experiment.', 'explicit author prescription')

source('L14', 'The Distributional Approach: A New Way to Identify Marketplace Exchange in the Archaeological Record', ['Kenneth G. Hirth'], 1998,
       'Current Anthropology 39(4):451–476', 'https://www.journals.uchicago.edu/doi/10.1086/204759',
       'unavailable article; primary publisher abstract lead',
       'Publisher search-rendered abstract/metadata only. Direct acquisition403 returned a challenge; no article body read.',
       ['publisher abstract'], 'Domestic assemblage distributions are proposed as evidence of marketplace exchange.',
       'No prescription beyond the abstract-level proposed method is used.',
       'Excluded from the primary selected census and from detailed trade-mechanism claims.', doi='10.1086/204759', selected=False)

source('L15', 'Bad Year Economics: Cultural Responses to Risk and Uncertainty', ['Paul Halstead (editor)', 'John O’Shea (editor)'], 1989,
       'Cambridge University Press; print29 September1989; online26 October2009', 'https://www.cambridge.org/core/books/bad-year-economics/2249365CCA983DAC9E902E08D7990E48',
       'publisher description of edited research volume',
       'Primary publisher book description and bibliographic information only; excerpt retrieval timed out twice. No chapter or whole-book reading.',
       ['publisher book description'],
       'The description identifies mobility, economic diversification, storage and exchange as responses to spatially/temporally variable food shortage.',
       'No chapter-specific prescription extracted.',
       'Contextual lead outside the 25-primary-work census; its description does not supply quantitative provisioning or trade results.',
       doi='10.1017/CBO9780511521218', selected=False)

source('L16', 'A Model of General Economic Equilibrium', ['John von Neumann'], 1945,
       'The Review of Economic Studies 13(1):1–9', 'https://www.erlinger.name/Tekster/VonNeumann1945.pdf',
       'original mathematical model; English translation',
       'Printed pp1–2/PDF1–2: model setup, goods producing goods, wear stages and timing; remaining equilibrium proof not read.',
       ['printed pp1–2, sections1–2'],
       'Circular production, joint products and stages of capital wear enter a simultaneous goods-and-process model.',
       'The opening identifies interpretation questions; no practical governance prescription extracted.',
       'The model assumes constant returns and unlimited expansion of natural factors including labor, with income above necessities reinvested. It does not resolve finite archaeological work capacities.',
       doi='10.2307/2296111', edition='English article footnote reports original German publication1938 and a1932 presentation; original German witness not inspected.')
obs('L16', 1, 'printed pp1–2, sections1–2', 'Goods produce other goods; capital wear can be represented by different wear-stage goods and longer processes by unit-time steps.')
obs('L16', 2, 'printed p2, assumptions(b)–(d)', 'Constant returns, unlimited expansion of labor/natural factors and reinvestment above necessities define the selected formal scope.')

source('L17', 'Production of Commodities by Means of Commodities: Prelude to a Critique of Economic Theory', ['Piero Sraffa'], 1960,
       'Original work1960; inspected Indian edition1963, Vora & Co. Publishers, Bombay', 'https://www.nuevatribuna.es/media/nuevatribuna/files/2013/04/15/production_of_commodities_by_means_of_commodities.pdf',
       'original economic reproduction framework; later edition witness',
       'Title/copyright PDF1–2 and ChapterI printed pp3–5/PDF15–17 visually inspected; selected OCR aids inspection. Printed p6 acquired/OCR only, not used for a substantive ChapterII claim. No complete book reading.',
       ['ChapterI, printed pp3–5'],
       'A self-replacing economy must recreate material inputs and redistribute them among mutually dependent production processes.',
       'No separate future-research prescription in inspected ChapterI.',
       'The illustrated self-replacing system is an assumed case, not a claim that every city is self-sufficient or that finite labor, access and institutions are already modeled.',
       edition='Image-only scan: title page identifies Vora & Co., Bombay; copyright page says Indian edition1963 and copyright1960. File stem retains first-work year.')
obs('L17', 1, 'ChapterI, printed pp3–5/PDF15–17', 'The examples jointly replace agricultural and industrial inputs and redistribute products by exchange; a third commodity can require triangular rather than pairwise exchange.')

source('L18', 'Note: Some Conditions of Macroeconomic Stability', ['David Hawkins', 'Herbert A. Simon'], 1949,
       'Econometrica 17(3/4):245–248', 'https://iiif.library.cmu.edu/file/Simon_box00029_fld02213_bdl0001_doc0001/Simon_box00029_fld02213_bdl0001_doc0001.pdf',
       'original mathematical note',
       'All four pages of the note, printed pp245–248/PDF1–4, inspected through institutional scan and extracted text. No modern generalization or empirical coefficient estimate attempted.',
       ['printed pp245–248'],
       'A linear production system must meet intermediate demands and final consumption together; the note provides a positivity criterion under its sign assumptions.',
       'The note corrects an earlier sufficient-condition error and gives a method for checking its production equations.',
       'The interpretation assumes enough fixed factors. It does not establish workforce availability, deadlines, storage or governance for a historical city.',
       doi='10.2307/1905526')
obs('L18', 1, 'printed pp245–248, economic interpretation on248', 'The condition is interpreted as requiring each group of industries to supply more than its own group-product needs so final consumption and other industries can be supplied.')

source('L19', 'Resilience as pathway diversity: linking systems, individual, and temporal perspectives on resilience',
       ['Steven J. Lade', 'Brian Walker', 'L. Jamila Haider'], 2020,
       'Ecology and Society 25(3):19', 'https://ecologyandsociety.org/vol25/iss3/art19/',
       'original conceptual model and illustrative formal examples',
       'Publisher sections Resilience as Pathway Diversity, Feedbacks from Actions, agricultural planning illustration/limitations, causal entropy and poverty trap example, selected discussion and conclusion.',
       ['Resilience as Pathway Diversity; Feedbacks from Actions', 'Agricultural Planning: guiding decision-making and limitations', 'Conclusion'],
       'Choices change future access to choices; livelihood pathways have a defined horizon and are constrained by assets, relationships and feedback.',
       'Refine with realistic dynamics and uncertainty, probabilistic drivers and participatory assessment, and report whose options are being counted.',
       'The agricultural example is intentionally invented; maximizing a powerful actor’s options may harm others. Pathway diversity is not a universal welfare measure.',
       doi='10.5751/ES-11760-250319')
obs('L19', 1, 'Feedbacks from Actions', 'A present action that runs down capital can remove later actions; pathway diversity concerns sequences and feedback rather than only an initial count of options.')
obs('L19', 2, 'Agricultural Planning > guiding decision-making and limitations', 'The illustrative analysis assumes a two-year fully known horizon and explicitly requests realistic switching costs, uncertain drivers and multiscale/participatory refinement.', 'explicit author prescription')

source('L20', 'Operationalizing pathway diversity in a mosaic landscape',
       ['My M. Sellberg', 'Steven J. Lade', 'Jan J. Kuiper', 'Katja Malmborg', 'Tobias Plieninger', 'Erik Andersson'], 2024,
       'Ecology and Society 29(3):26', 'https://ecologyandsociety.org/vol29/iss3/art26/',
       'original exploratory empirical-model application',
       'Publisher abstract, single-strategy results, discussion subsections on switching/abandonment/scale, reflections and conclusions. No independent model rerun or whole supplementary-data audit.',
       ['Results > Pathway Diversity: single strategies', 'Lessons from a Pathway Diversity Approach', 'Reflections on the Pathway Diversity Approach'],
       'Accessibility matrices, collective strategies and supporting pairs can alter livelihood options, while individual gains can erode a landscape outcome.',
       'Test uncertainty in matrix entries, social/environmental feedbacks, contested power contexts, co-production and trade-offs across actors and scales.',
       'One Swedish landscape and exploratory assumptions do not supply universal rankings. Short versus long horizons can reverse comparisons.',
       doi='10.5751/ES-15255-290326')
obs('L20', 1, 'Results > Pathway Diversity: single strategies', 'Modeled strategy comparisons vary with horizon and abandonment assumptions; similar initial options can diverge later.')
obs('L20', 2, 'Lessons > Managing Trade-offs across Scales; Reflections', 'Individual moves toward forestry can improve livelihood options while threatening the mosaic landscape; authors request parameter/structural uncertainty and explicit feedback analysis.', 'explicit author prescription')

source('L21', 'Mesoamerican urbanism revisited: Environmental change, adaptation, resilience, persistence, and collapse',
       ['Diane Z. Chase', 'José Lobo', 'Gary M. Feinman', 'David M. Carballo', 'Arlen F. Chase', 'Adrian S. Z. Chase', 'Scott R. Hutson', 'Alanna Ossa', 'Marcello Canuto', 'Travis W. Stanton', 'LJ Gorenflo', 'Christopher A. Pool', 'Barbara Arroyo', 'Rodrigo Liendo Stuardo', 'Deborah L. Nichols'], 2023,
       'Proceedings of the National Academy of Sciences 120(31):e2211558120; online24 July2023', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10400939/',
       'author archaeological synthesis and research agenda',
       'Primary abstract and first two paragraphs each of Risk/Adaptation/Resilience, Sustainability and Adaptation, and Ongoing Research/New Research Dialogue. Full case reports and supplements not independently inspected.',
       ['Sustainability and Adaptation, paragraphs1–2', 'Ongoing Research and a New Research Dialogue, paragraphs1–2'],
       'Comparative examples include dispersed reservoirs, food imports and local intensive farming, with governance and settlement layouts affecting adaptation.',
       'Build cross-cultural and cross-temporal comparisons using diverse cases and material/social infrastructure, with collaboration across disciplines.',
       'These are the authors’ synthesis of other case reports. The survey does not adopt every causal attribution to autocracy or authenticate service quantities from the synthesis alone.',
       doi='10.1073/pnas.2211558120')
obs('L21', 1, 'Sustainability and Adaptation, paragraph2', 'The authors contrast localized reservoirs and intensive farming at Caracol, food imports at Chunchucmil and nearby cropping at Tikal.', 'author case synthesis')
obs('L21', 2, 'Ongoing Research and a New Research Dialogue, paragraphs1–2', 'The proposed comparison treats hard, green and social infrastructure as sources for testing urban adaptation across diverse past cases.', 'explicit author prescription')

source('L22', 'Out of Order: Understanding Repair and Maintenance', ['Stephen Graham', 'Nigel Thrift'], 2007,
       'Theory, Culture & Society 24(3):1–25', 'https://raley.english.ucsb.edu/wp-content/Engl800/Graham-Thrift-repair.pdf',
       'original urban maintenance argument and synthesis',
       'Selected printed pp4–6/PDF5–7 independently read from the review agent’s retained primary-paper witness; broader urban claims on later pages depend on reviewer reading and are not included as new inspection here.',
       ['printed pp4–6'],
       'Repair uses skilled apprenticeship and improvisation; maintaining service can change materials and methods and generate innovation.',
       'Treat repair, maintenance and their practical knowledge as objects of social/urban inquiry.',
       'The selected qualitative argument already connects repair to innovation and practical learning. It supplies no ancient repair cadence or measured input requirement.')
obs('L22', 1, 'printed pp4–6/PDF5–7', 'Repair can entail apprenticeship, improvisation, cannibalization and new material combinations; restored function need not mean exact replication.')

source('L23', 'Beyond Markets and States: Polycentric Governance of Complex Economic Systems', ['Elinor Ostrom'], 2009,
       'Nobel lecture8 December2009; Les Prix Nobel printed pp408 onward',
       'https://www.nobelprize.org/uploads/2018/06/ostrom_lecture.pdf',
       'author lecture with empirical/theoretical synthesis',
       'Printed pp411–412/PDF4–5 and p420/PDF13 independently read from reviewer’s official lecture witness. The related2010 American Economic Review article is not an independently inspected work.',
       ['printed pp411–412', 'printed p420'],
       'Local direct providers and shared indirect services can complement one another; information, choice, aggregation and payoff rules affect action.',
       'Investigate polycentric arrangements empirically and distinguish institutional rules, rather than assuming one organizing level.',
       'Modern water/police examples support alternative mechanisms; they are not evidence of ancient institutions or technical feasibility alone.',
       edition='The official lecture heading uses Complex Economic Systems; citation to the later AER version sometimes uses a different title. This record is the2009 lecture witness.')
obs('L23', 1, 'printed pp411–412/PDF4–5', 'Water and policing research illustrates complementary local production and larger-scale indirect provision under polycentric arrangements.')
obs('L23', 2, 'printed p420/PDF13', 'Rules governing choices, information, aggregation and payoffs influence which available actions actors can undertake.')

source('L24', 'The Cost of Restoration as a Way of Defining Resilience: a Viability Approach Applied to a Model of Lake Eutrophication', ['Sophie Martin'], 2004,
       'Ecology and Society 9(2):8;15 October2004', 'https://ecologyandsociety.org/vol9/iss2/art8/inline.html',
       'original viability model and operational resilience definition',
       'Primary abstract, Methods opening through objectives/time horizon, cost-function subsection and selected discussion; reused coordinator HTML. Numerical lake experiment and proof appendices not independently reproduced.',
       ['Methods > Mathematical Formulation > dynamics and controls', 'Methods > cost function, disturbance and resilience'],
       'The viable subset contains states admitting at least one control trajectory that meets the chosen property through the horizon; restoration costs depend on the property and disturbance.',
       'Specify property, controls, disturbance, horizon and cost when making resilience operational.',
       'The selected law assumes the controlling institution can bear control changes and treats those provider costs as external to its chosen resilience cost. A broader boundary requires additional resource accounting.')
obs('L24', 1, 'Methods > Mathematical Formulation > The Dynamics and the Controls', 'The institution can choose admissible controls, switch among them and is assumed to have enough resources to bear those changes.', 'declared model assumption')
obs('L24', 2, 'Methods > The Cost Function, the Disturbance, and the Resilience; paragraph beginning Maintaining this property', 'Costs of control changes are excluded from the selected resilience cost because they are borne by the acting institution externally.', 'declared model assumption')
obs('L24', 3, 'Methods > A Viability Analysis > The Viability Kernel', 'A state can satisfy the present property while no admissible trajectory sustains it through the chosen horizon; permanent external control may support some viable trajectories.', 'declared model construction')

source('L25', 'The Collapse of Complex Societies', ['Joseph A. Tainter'], 1988,
       'Cambridge University Press', 'https://assets.cambridge.org/97805213/86739/excerpt/9780521386739_excerpt.pdf',
       'unavailable book/excerpt lead',
       'Primary publisher search metadata/snippet only. Two excerpt attempts timed out; a guessed book URL returned500. No chapter or full-book reading.',
       ['publisher search metadata'], 'No independent detailed book argument is extracted here; L02 provides the author’s later inspected synthesis.',
       'No book-specific prescription claimed.', 'Excluded from primary census; no unsupported substitution of a later summary for full-book inspection.', selected=False)

source('L26', 'Thinking Through Change: Combining the Adaptive Cycle and Assemblage Theory to Assess Urban Change in Later Medieval Northern England', ['Ben Jervis'], 2026,
       'Journal of Archaeological Method and Theory; DOI10.1007/s10816-026-09803-2', 'https://link.springer.com/article/10.1007/s10816-026-09803-2',
       'original archaeological theoretical/case interpretation',
       'Primary publisher web-rendered selected lines146–191,296–310,368–376 and397–404 independently read through coordinator captures. Direct HTML was a challenge; no full PDF or complete article read.',
       ['publisher web lines176–180, yard', 'web lines296–310, boundaries/temporality', 'web lines397–404, conclusion'],
       'Yards and boundaries persist through repeated maintenance, changing relations and materials; archaeological phases can conceal overlapping temporal processes.',
       'Compare material relations and consider integration with empirical network analysis, including Priß et al.2026.',
       'Invisible maintenance and temporal/boundary complexity are explicit prior arguments. Interpretation of a persistent yard does not itself measure total work, service output or the unique mechanism.',
       doi='10.1007/s10816-026-09803-2', rights='Coordinator observed CC BY4.0; final license witness retained by coordinator; this survey keeps all raw local-only')
obs('L26', 1, 'publisher-rendered lines176–180', 'The Carlisle yard example describes repair, sweeping and relaying; some activities leave traces and others are inferred from the surface’s persistence.', 'author archaeological interpretation')
obs('L26', 2, 'publisher-rendered lines296–310 and368–376', 'Boundary and building continuity can involve altered materials, uses and relations rather than exact replication; phase divisions can flatten this history.')
obs('L26', 3, 'publisher-rendered lines397–404', 'The conclusion explicitly suggests joining comparative adaptive-cycle analysis, network connectivity metrics and material context.', 'explicit author prescription')

source('L27', 'Integrating Restoration and Scheduling Decisions for Disrupted Interdependent Infrastructure Systems',
       ['Burak Cavdaroglu', 'Erik Hammel', 'John E. Mitchell', 'Thomas C. Sharkey', 'William A. Wallace'], 2013,
       'Annals of Operations Research 203:279–294; author page reports online-first5 September2011', 'https://mitchjrpi.github.io/papers/integrated.html',
       'original mathematical optimization model and computational application',
       'Author manuscript selected abstract and pp3–4,7 independently read from reviewer witness. Publication chronology is from retained author-page capture; no whole model/computational results rerun.',
       ['author manuscript pp3–4', 'author manuscript p7'],
       'Restoration task selection, work-group assignment, scheduling and infrastructure dependencies are solved together with service performance over time.',
       'Integrate planning and scheduling rather than sequentially optimizing installation cost and task completion; offer usable heuristic methods.',
       'This is a direct predecessor for shared repair resources and joint plans. Modern task durations and management assumptions do not identify ancient ones.')
obs('L27', 1, 'author manuscript pp3–4', 'The model integrates which components to restore, allocation to work groups and timing, assessing services throughout the horizon.')
obs('L27', 2, 'author manuscript p7', 'Network-flow, input-dependency, scheduling and availability constraints are coupled; the stated modern planning horizon is30–60days.', 'declared model construction')

source('L28', 'Urban resilience in Ancient Mesopotamia: insights into the socioeconomic system of the Bronze and Iron Age Khabur Valley',
       ['Deborah Priß', 'Dan Lawrence', 'John Wainwright', 'Christina Prell', 'Laura Turnbull'], 2026,
       'Antiquity100(410):340–354; online28 January2026; issueApril2026',
       'https://www.cambridge.org/core/journals/antiquity/article/urban-resilience-in-ancient-mesopotamia-insights-into-the-socioeconomic-system-of-the-bronze-and-iron-age-khabur-valley/9F0354FCAB61E534295AB049C430F6F0',
       'original archaeological network analysis',
       'Publisher PDF title/abstract/intro p340, route reconstruction p342 and metric assumptions p345/PDF1,3,6. References on p352 viewed but not used as inspected evidence. No complete article/code or result reanalysis.',
       ['printed p342', 'printed p345'],
       'Reconstructed settlement/route graphs provide period-specific connectivity and potential proxies for adaptive-cycle comparisons.',
       'Operationalize the cycle with testable network expectations; include settlement diversity/specialization when data permit.',
       'Hollow ways are hard to date; missing sites/routes are reconstructed and size can be held constant. The selected metrics are proxies, not measured imports, repair capacity or a unique causal history.',
       doi='10.15184/aqy.2025.10272', rights='Observed CC BY-NC4.0 notice on publisher PDF p340; raw/derivatives local-only')
obs('L28', 1, 'printed p342', 'Fragments of hollow ways are joined to reconstruct routes and an algorithm predicts missing settlements; period-specific graphs connect dated settlements through these inferred routes.', 'declared analytical construction')
obs('L28', 2, 'printed p345', 'Density/centralization are connectivity proxies and site count is a potential proxy; the authors identify unavailable settlement specialization/diversity and some undifferentiated size histories.', 'declared analytical construction')


def main():
    index={x['source_id']:x for x in sources}
    explicit={'L02','L03','L08','L09','L10','L11','L13','L19','L20','L21','L26','L28'}
    none={'L01','L12','L15','L17','L25'}
    for item in sources:
        item['recommendation_status']='explicit prescription in inspected text' if item['source_id'] in explicit else 'none separately extracted' if item['source_id'] in none else 'methodological framing or stated objective, not a separate future-research prescription'
    for manifest in sorted(RAW.glob('capture-v*.json')):
        data=json.loads(manifest.read_text('utf-8'))
        for row in data.get('attempts',[]):
            key=row['id'].split('-')[0]
            if key not in index: continue
            enriched=dict(row, acquisition_manifest=manifest.relative_to(ROOT).as_posix(),
                          acquisition_manifest_sha256=sha(manifest))
            index[key]['acquisition_attempts'].append(enriched)
            if row.get('path'):
                usable=(row.get('status_code')==200 and row.get('format')=='pdf') or row.get('path','').endswith('.bin')
                if key in ['L05','L07','L19','L20','L21'] and row.get('status_code')==200: usable=True
                if key=='L15' and 'capture-v3' in row.get('path','') and row.get('status_code')==200:usable=True
                role='primary_witness' if usable else 'failed_or_challenge_witness'
                index[key]['witnesses'].append(artifact(row['path'],role))
            if row.get('extraction'):
                index[key]['derivatives'].append(artifact(row['extraction']['path'],'mechanical_derivative'))
    for key in ['L09','L10','L11']:
        for path in sorted(RAW.glob(key+'-*-xml-extraction-v*.json')):
            index[key]['derivatives'].append(artifact(path.relative_to(ROOT).as_posix(),'mechanical_derivative'))
    for path in sorted(RAW.glob('L17-*-ocr-v1*')):
        index['L17']['derivatives'].append(artifact(path.relative_to(ROOT).as_posix(),'mechanical_derivative'))
    for key,paths in {
        'L22':['data/raw/2026-10-11-societal-persistence/review/graham-thrift2007.pdf','data/raw/2026-10-11-societal-persistence/review/graham-thrift2007.pdf.pages.json'],
        'L23':['data/raw/2026-10-11-societal-persistence/review/ostrom2009-lecture.pdf','data/raw/2026-10-11-societal-persistence/review/ostrom2009-lecture.pdf.pages.json'],
        'L24':['data/raw/2026-10-11-societal-persistence/coordinator/sources-v1/martin2004.html'],
        'L26':['data/raw/2026-10-11-societal-persistence/coordinator/sources-v1/jervis2026-web-v3.json','data/raw/2026-10-11-societal-persistence/coordinator/sources-v1/jervis2026-web-v4.json'],
        'L27':['data/raw/2026-10-11-societal-persistence/review/cavdaroglu2013.pdf','data/raw/2026-10-11-societal-persistence/review/cavdaroglu2013.pdf.pages.json'],
    }.items():
        for relative in paths:
            role='mechanical_derivative' if relative.endswith('.pages.json') else 'mediated_primary_rendering' if relative.endswith('.json') else 'primary_witness'
            index[key]['witnesses'].append(artifact(relative,role,True))
        for relative in paths:
            acquisition=ROOT/(relative+'.acquisition.json')
            if acquisition.exists():
                index[key]['acquisition_attempts'].append(dict(reused_from_collaborator=True,
                    acquisition_manifest=acquisition.relative_to(ROOT).as_posix(),
                    acquisition_manifest_sha256=sha(acquisition),
                    record=json.loads(acquisition.read_text('utf-8'))))
    for key in ['L24','L26']:
        manifest=ROOT/'data/raw/2026-10-11-societal-persistence/coordinator/sources-v1/manifest.json'
        index[key]['acquisition_attempts'].append(dict(reused_from_collaborator=True,
            acquisition_manifest=manifest.relative_to(ROOT).as_posix(),
            acquisition_manifest_sha256=sha(manifest),
            note='Coordinator manifest and source ledger retain acquisition context. Web-rendered Jervis passages are mediated captures, not downloaded article bytes.'))
    for row in observations:
        row['supporting_witness_paths']=[x['path'] for x in index[row['source_id']]['witnesses'] if x['role']!='failed_or_challenge_witness']
    scope=dict(date='2026-10-11', design='purposive exploratory survey; not field prevalence estimate',
        source_records=len(sources), selected_primary_works=sum(s['selected_primary_work'] for s in sources),
        excluded_or_context_leads=[s['source_id'] for s in sources if not s['selected_primary_work']],
        raw_policy='All source publications, tool renderings, OCR and mechanical extracts remain local-only. Original summaries/code/metadata are authored artifacts.',
        access_rule='A complete acquired file does not mean complete reading. Inspected scope is explicitly declared for every work.',
        followup='L28 added after the initial census because L26 explicitly names it as a direct integration predecessor.',
        inherited_sources='L22/L23/L27 reuse review-agent witnesses; L24/L26 reuse coordinator witnesses. Independent selected reading is declared; no duplicate acquisition.',
        generated_by='build_ledger.py', script_sha256=sha(Path(__file__)))
    (HERE/'SOURCES.json').write_text(json.dumps(dict(scope=scope,sources=sources),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'OBSERVATIONS.json').write_text(json.dumps(dict(scope='Source statements, author constructions and bounded scope assessments; proposed extensions live separately in COMPARISONS.json',observations=observations),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(records=len(sources),selected=sum(s['selected_primary_work'] for s in sources),observations=len(observations)),indent=2))


if __name__=='__main__': main()
