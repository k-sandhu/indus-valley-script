"""Write source-qualified component comparisons once, without evidential scoring."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREFIX='experiments/2026-10-12-transmission-hypothesis/'


def obs(file,*ids):return {'file':PREFIX+file,'ids':list(ids)}


def rival(prediction,actual,relation,observations,missing,assumption=None):
    value={'prediction':prediction,'actual_observation':actual,'relation':relation,
           'observations':observations,'missing_discriminator':missing}
    if assumption:value['assumption']=assumption
    return value


def edge(feature,origin,destination,type,state,observations=(),premises=None):
    return {'feature':feature,'from':origin,'to':destination,'type':type,'state':state,
            'observations':list(observations),'feature_specific':state!='unresolved',
            'premises':premises}


def case(id,family,feature,proposition,observations,chronology,dependencies,transitions,rivals,decision,conclusion,refinement=None):
    return {'id':id,'family':family,'feature':feature,'proposition':proposition,
            'observations':observations,'chronology':chronology,'dependencies':dependencies,
            'transitions':transitions,'rivals':rivals,'decision':decision,'conclusion':conclusion,
            'claims_traced_local_literary_descent':False,'rival_discrimination_basis':None,
            'post_reading_refinement':refinement,
            'scope':'Manual source-based judgment in a purposive frame; routes may combine and unknown is not absence.'}


def main():
    out=HERE/'comparisons-v1.json'
    if out.exists():raise SystemExit('Comparison endpoint exists; no overwrite.')
    mat='material/observations.json';txt='texts/OBSERVATIONS.json';rev='review/observations-v2.json';ctl='coordinator/observations-v2.json'
    comparisons=[]
    comparisons.append(case('TC01','agriculture and water-related operations','Cultivation, crop use and represented sowing/water lifting',
      'Do intermediate crop specimens and the selected agricultural hymn identify locally transmitted practice?',
      [obs(mat,'MO07','MO08','MO09','MO10','MO17','MO22','MO23','MO24','MO25'),obs(txt,'TX-RV10.101.3','TX-RV10.101.4','TX-RV10.101.5','TX-RV10.101.7','TX-RV10.101.11','TX-V3-CULTIVATION')],
      'Jognakhera has three directly dated crop specimens with separate ranges; individual layer joins are absent in the inspected date table. Hulas has conflicting broad chronology. A hymn stratum is not a specimen date.',
      'Hulas botanical observations share one excavation/sample lineage; Jognakhera dates and residue observations share one study. Sanskrit, translation and stanza coding are one textual passage lineage.',
      [edge('Distinctive farming operation','Harappan working contexts','second-millennium practitioners','material_operation','unresolved'),
       edge('Same distinctive operation','second-millennium practitioners','RV 10.101 representation','learning_relation','unresolved'),
       edge('Represented sowing and well acts','RV 10.101.3–7','received selected hymn','textual_operation','observed',[obs(txt,'TX-RV10.101.3','TX-RV10.101.5','TX-RV10.101.7')])],
      {'R1':rival('Distinctive local operations continue through intermediate practice and enter the hymn.','Direct grain dates and processing candidates improve intermediate endpoints; no linked local-to-hymn operation is observed.','compatible_only',[obs(mat,'MO23','MO24')],'Dated operation bundle, not crop presence alone.'),
       'R2':rival('Some agricultural vocabulary, ritual frame or role relationships have a comparative ancestral explanation.','Younger Avestan cultivation and Haoma controls represent agriculture/ritual relations, but not the selected well mechanism.','compatible_only',[obs(txt,'TX-V3-CULTIVATION','TX-Y9-PRESS')],'A feature-specific formal or operational comparison with chronology.'),
       'R3':rival('Practitioners, crops or operations arrive through wider regional contacts.','Plant occurrence and proposed migration are distinct; the study does not identify the carriers.','compatible_only',[obs(mat,'MO11','MO25')],'Discriminating provenance and dated contact/operation distribution.'),
       'R4':rival('Similar tasks and inputs can generate similar cultivation and water-handling choices.','The selected actions have practical purposes; no reinvention experiment or rare-bundle distribution identifies this route.','compatible_only',[obs(txt,'TX-RV10.101.3','TX-RV10.101.5'),obs(ctl,'C-O05','C-O07')],'Matched task/material controls and alternative workable operations.'),
       'R5':rival('A text relates practical acts to a ritual and ethical repertoire.','The full hymn places the acts within ritual imagery, including the well without digging; the Iranian control also joins cultivation to religious value.','positive_observation',[obs(txt,'TX-RV10.101.11','TX-V3-REGISTER')],'Earlier component/variant evidence for a particular later reorganization.')},
      'unresolved_join','Intermediate plant use and represented agricultural acts are supported at different endpoints. Their operation-level descent is unresolved; the full hymn supplies conceptual/ritual organization rather than a technical manual.'))
    comparisons.append(case('TC02','hard-stone manufacture','Working-stage beads and a proposed later workshop lineage',
      'Do unfinished beads establish a dated local teaching chain that shaped the selected literary craft imagery?',
      [obs(mat,'MO01','MO02','MO03','MO04','MO12','MO13','MO14','MO19','MO26'),obs(txt,'TX-RV9.112.2','TX-RV10.101.10')],
      'The Harappa pot is a mixed-phase collection. Bhagwanpura accessions have source-assigned IB subphases and broad dating uncertainty; neither is a teacher date.',
      'Two Harappa captions describe the same pot. BPR-208 is one accession with two material descriptions. The early Ravi workshop is a control, not an intermediate replicate.',
      [edge('Bead operations','Harappan production','Bhagwanpura working-stage objects','material_operation','unresolved'),
       edge('Bead technical knowledge','later practitioners','selected literary craft image','learning_relation','unresolved'),
       edge('Unfinished bead forms','Bhagwanpura catalogue','intermediate object record','material_operation','observed',[obs(mat,'MO12','MO13')])],
      {'R1':rival('Local practitioners continue a distinctive manufacturing sequence.','Unfinished beads/raw material support an attributed local-working hypothesis; the sequence and learning relation are not observed.','compatible_only',[obs(mat,'MO12','MO14')],'Associated waste/tools, operation signature and dated succession.'),
       'R2':rival('The literary image can belong to an inherited specialist repertoire.','The selected craft imagery specifies no bead drilling; inherited role comparisons cannot supply that missing technique.','unresolved',[obs(txt,'TX-RV9.112.2'),obs(rev,'O-R01-1')],'A bead-specific textual or comparative operation.'),
       'R3':rival('Moving craftspeople or traded working-stage objects produce the observed assemblage.','Unfinished objects and raw material are compatible with regional transfer or imported roughouts.','compatible_only',[obs(mat,'MO12','MO14')],'Provenance and technological distribution capable of separating these routes.'),
       'R4':rival('Available material and tool constraints allow reconstruction of a technique.','No linked technique or measured alternatives establish reinvention; color alone does not identify stone source or supply loss.','unresolved',[obs(mat,'MO02'),obs(ctl,'C-O05')],'Experimental/microscopic alternatives and a matched distribution.'),
       'R5':rival('A later literary repertoire uses general craft imagery.','The hymns represent artisans and materials but omit the proposed bead sequence.','compatible_only',[obs(txt,'TX-RV9.112.2','TX-RV10.101.10')],'A bead-specific incorporation or transformation locus.')},
      'supported_intermediate','Bhagwanpura supplies source-qualified working-stage objects. The mixed pot weakens a narrow deposition-to-manufacture argument, and neither assemblage establishes a bead-to-text lineage.'))
    comparisons.append(case('TC03','ceramic production','Forming, joining, finishing and firing choices',
      'Do intermediate pottery observations identify the continuation of a distinctive recipe and its literary incorporation?',
      [obs(mat,'MO06','MO10','MO14','MO15','MO16','MO18','MO19','MO20','MO21'),obs(txt,'TX-RV10.101.10')],
      'Hulas and Bhagwanpura preserve different phase schemes and coarse/qualified date arguments. Sanghol later factory claims concern Kushana contexts, not an intermediate workshop.',
      'Morphology, bulk composition and authors\' interaction claims are related observations from the same Bhagwanpura programme; they are not independent teaching records.',
      [edge('Distinctive pottery sequence','Harappan practitioners','intermediate ceramic makers','material_operation','unresolved'),
       edge('Same sequence','ceramic makers','selected literary representation','learning_relation','unresolved'),
       edge('Forming/joining/trimming traces','Hulas sherds','reported technological reconstruction','material_operation','attributed_inference',[obs(mat,'MO06')],'Striations and joins are interpreted as forming and finishing traces; finished vessels can travel.')],
      {'R1':rival('A distinctive local manufacture tradition continues and teaches recipients.','The report gives operational traces and an explicit author-attributed learning hypothesis, with no documented teachers.','compatible_only',[obs(mat,'MO06','MO15','MO18')],'Dated recipe succession and production/correction choices with controls.'),
       'R2':rival('A comparative inherited repertoire supplies the relevant technique or its representation.','The inspected Iranian/verbal controls do not specify the ceramic sequence.','unresolved',[obs(rev,'O-R02-3'),obs(txt,'TX-RV10.101.10')],'A ceramic-specific comparative operation, rather than a generic role.'),
       'R3':rival('Vessels or skilled producers move between interacting communities.',"Associated wares and forms permit contact; the author's learning interpretation is not a measured movement of potters.",'compatible_only',[obs(mat,'MO15','MO18')],'Geological provenance, workshop context and operation distribution.'),
       'R4':rival('Shared functions and physical constraints produce similar choices.','Wheel manufacture and similar forms leave alternative working solutions and their frequencies unresolved.','compatible_only',[obs(mat,'MO16'),obs(ctl,'C-O05','C-O06')],'Controls for clay, vessel use, forming and firing constraints.'),
       'R5':rival('A literary tradition reorganizes a specific pottery operation.','The selected passages do not supply that sequence.','unresolved',[obs(txt,'TX-RV10.101.10')],'An independently selected ceramic operation in a textual locus.')},
      'unresolved_join','There is a stronger material comparison to undertake at the operation level. Existing authors already proposed learning between neighboring makers; the present data do not trace the literary transition.'))
    comparisons.append(case('TC04','specialist occupations','Different occupations, clients and household tasks',
      'Is the selected occupational picture diagnostic of a uniquely local urban-derived institutional order?',
      [obs(txt,'TX-RV9.112.1','TX-RV9.112.2','TX-RV9.112.3','TX-RV9.112.4','TX-OD17-ROLES'),obs(rev,'O-R01-1')],
      'The received hymns and Greek passage have distinct compositional/collection histories; neither locates a Harappan occupation.',
      'A complete four-stanza hymn is one textual frame. Its translation and Sanskrit edition are witnesses, not separate household samples.',
      [edge('Occupation organization','Harappan working communities','later represented household/client relations','learning_relation','unresolved'),
       edge('Represented roles','RV 9.112.1–3','selected hymn','textual_operation','observed',[obs(txt,'TX-RV9.112.1','TX-RV9.112.3')])],
      {'R1':rival('A narrow uniqueness claim predicts this role picture cannot be supplied by other repertoires.','The Greek passage lists overlapping specialist kinds and the comparative scholarship supplies an inherited poet-patron account.','counter_observation_under_stated_assumption',[obs(txt,'TX-OD17-ROLES'),obs(rev,'O-R01-1')],'A distinctive local bundle and independently dated carrier.','Only the claim of uniqueness/necessity is challenged; a possible local contribution is not excluded.'),
       'R2':rival('Poet/support relations or specific vocabulary have an inherited comparative explanation.','The scholarly introduction argues inherited poet-patron relations; the Greek role list is a further comparison, not proof of the whole bundle.','positive_observation',[obs(rev,'O-R01-1'),obs(txt,'TX-OD17-ROLES')],'Feature-specific formal comparison for any proposed whole occupational bundle.'),
       'R3':rival('Regional contacts contribute skills or social arrangements to the portrayed repertoire.','The poem does not identify donors or activity-specific contacts.','unresolved',[obs(txt,'TX-RV9.112.1')],'A carrier relationship and geographically discriminating feature.'),
       'R4':rival('Ordinary recurring tasks permit occupational differentiation and clients.','The practical roles and different desires fit this possibility; the selected poem supplies no reinvention history.','compatible_only',[obs(txt,'TX-RV9.112.1','TX-RV9.112.4')],'A control distinguishing ordinary task differentiation from a transmitted rare arrangement.'),
       'R5':rival('A poem organizes work as part of its own literary purpose.','The household, clients and animal/human desires participate in a complete Soma-refrain comparison.','positive_observation',[obs(txt,'TX-RV9.112.3','TX-RV9.112.4')],'Earlier variants for a claim of particular redaction or institutional chronology.')},
      'rival_comparison','The hymn depicts differentiated work and household tasks. The observations challenge a uniqueness claim, while leaving contributions to specific occupations open. They do not establish a hereditary caste, market census or manufacturing lineage.'))
    comparisons.append(case('TC05','poetic or ritual learning','Competence, companionship, collective performance and specialist contributions',
      'Does the learned-speech picture require a post-Harappan institutional origin?',
      [obs(txt,'TX-RV10.71.4','TX-RV10.71.6','TX-RV10.71.8','TX-RV10.71.10','TX-RV10.71.11'),obs(rev,'O-R01-1','O-R01-3','O-R02-1','O-R02-2','O-R02-4','O-R05-1','O-R05-2','O-R07-1','O-R07-2')],
      'The Rigvedic and Old Avestan represented settings, comparative reconstruction and later canon history retain separate strata. An audience or named patron is not an independently dated school.',
      'The two Jamison–Brereton excerpts are one work; Skjærvø editions and role article have interpretive overlap. Canon reconstruction remains an attributed argument.',
      [edge('Learning institution','Harappan social relationships','Rigvedic specialist companionship','learning_relation','unresolved'),
       edge('Represented competence and roles','RV 10.71','selected learned-speech picture','textual_operation','observed',[obs(txt,'TX-RV10.71.6','TX-RV10.71.8','TX-RV10.71.11')]),
       edge('Poet/ritual comparisons','Indo-Iranian repertoire','Rigvedic and Iranian roles','comparative_reconstruction','attributed_inference',[obs(rev,'O-R01-1','O-R07-1')],'Comparative verbal/role premises of the cited scholars; not a directly observed teacher chain.')],
      {'R1':rival('Local working/learning relationships supply some distinctive component.','The hymn depicts competence and affiliation but the local-to-verbal transfer is untraced.','compatible_only',[obs(txt,'TX-RV10.71.6','TX-RV10.71.10')],'A feature specific to a dated local carrier and its recipient.'),
       'R2':rival('Professional verbal and ritual relations have an inherited Indo-Iranian explanation.','The scholarly reconstruction and edited Old Avestan controls supply specific patronage, role and addressed-speech comparisons.','positive_observation',[obs(rev,'O-R01-1','O-R02-1','O-R02-2','O-R02-4','O-R07-1')],'More specific operations must be assessed separately; no whole-text exclusion follows.'),
       'R3':rival('Regional networks modify an inherited specialist repertoire.','School history argues regional differentiation and interaction, without a Harappan feature-specific donor.','compatible_only',[obs(rev,'O-R05-1')],'A dated contact and transferred component.'),
       'R4':rival('Recurring performance and cooperation generate competence norms.','The represented distinction between hearing, understanding and successful collective work fits the mechanism.','compatible_only',[obs(txt,'TX-RV10.71.4','TX-RV10.71.8')],'A comparison separating ordinary competence evaluation from an inherited distinctive form.'),
       'R5':rival('Collection and teaching institutions combine repertoires and change their evaluation.','The scholars reconstruct canon consolidation; the Iranian comparison argues changed evaluations of related role terms.','positive_observation',[obs(rev,'O-R05-1','O-R05-2','O-R07-2')],'A case-specific earlier/later textual trajectory for any proposed exact reorganization.')},
      'rival_comparison','The text supports a specific learned-speech picture and a prospective peer-qualification mechanism. Indo-Iranian inheritance is an independently motivated account for part of it; local practical inputs and later combinations remain component-level questions.'))
    comparisons.append(case('TC06','poetic or ritual learning','Sifting meal used to depict the shaping of speech',
      'Is practical-to-conceptual incorporation directly represented, and does it identify a Harappan source?',
      [obs(txt,'TX-RV10.71.2','TX-RV10.71.3','TX-RV10.71.10','TX-RV10.71.11'),obs(mat,'MO17'),obs(rev,'O-R01-3')],
      'The analogy is present at the selected textual stage. The age of sifting and the origin of the particular verbal image are not dated by the poem.',
      'The motivating verse is discovery evidence; independent later validation needs a new fixed comparison. A quern is a grinding tool and cannot be substituted for a sifting observation.',
      [edge('Sifting operation/image','proposed earlier local practice','particular poetic analogy','learning_relation','unresolved'),
       edge('Represented comparison','RV 10.71.2','speech-fashioning and affiliation picture','textual_operation','observed',[obs(txt,'TX-RV10.71.2')])],
      {'R1':rival('A locally transmitted operation contributes the image.','A sifting comparison is explicit; no Harappan sieve sequence or worker-to-poet transfer is observed.','compatible_only',[obs(txt,'TX-RV10.71.2')],'A distinctive operation/image with local intermediates and transmission evidence.'),
       'R2':rival('The image or verbal construction belongs to an inherited poetic repertoire.','Comparative scholarship supports inherited formulaic resources generally, but this exact image has no matched control in the selected evidence.','compatible_only',[obs(rev,'O-R01-3')],'An exact inherited metaphor or formal comparison and its premises.'),
       'R3':rival('A practical or verbal image arrives through regional contact.','The selected passage does not name a donor.','unresolved',[obs(txt,'TX-RV10.71.2')],'Geographical and chronological distribution of the distinctive image/operation.'),
       'R4':rival('A familiar separation/refinement action independently supplies a model for speech.','The represented relation fits this possibility; no experiment or historical independence establishes it.','compatible_only',[obs(txt,'TX-RV10.71.2'),obs(ctl,'C-O05','C-O07')],'Independent comparison controlling common practical constraints.'),
       'R5':rival('Practical material is conceptually organized in specialist speech.','The explicit meal/sieve comparison directly relates a practical action to fashioning speech in the learned-speech context.','positive_observation',[obs(txt,'TX-RV10.71.2','TX-RV10.71.3','TX-RV10.71.11')],'Earlier variants or independently dated components for a specific later-redaction claim.')},
      'supported_endpoint','The poem directly represents practical-to-conceptual reuse. Incorporation at this endpoint is a positive finding; its donor and earlier route remain unresolved.','coordinator/REFINEMENT-analogy.md'))
    comparisons.append(case('TC07','specialist occupations','Normative classification of livelihood arts',
      'Does a later organized repertoire establish an old Harappan institutional package?',
      [obs(txt,'TX-DN1-NORM','TX-DN1-MARKS','TX-DN1-CALC','TX-DN1-TREAT'),obs(rev,'O-R01-2','O-R05-3')],
      'DN 1 is a later non-Vedic textual comparison. Its classification does not date its component arts to the Rigveda or Harappan cities.',
      'Pali and translation segmentation witness one discourse; lists within it are not independent occupation censuses.',
      [edge('Practical repertoire','Harappan occupations','DN 1 classified arts','learning_relation','unresolved'),
       edge('Ethical grouping','DN 1.1.21–27','received normative classification','later_reorganization','observed',[obs(txt,'TX-DN1-NORM','TX-DN1-CALC')])],
      {'R1':rival('Locally retained practices contribute components to the later list.','The list names arts but provides no intermediate local carrier.','compatible_only',[obs(txt,'TX-DN1-TREAT')],'A component-specific practice and dated transfer route.'),
       'R2':rival('Some verbal, ritual or specialist components have inherited comparative histories.','The selected comparative source does not reconstruct the entire DN 1 list.','unresolved',[obs(rev,'O-R01-1')],'Exact component comparisons rather than transfer of a whole package.'),
       'R3':rival('Regional contacts contribute diverse components.','The normative list does not identify the activities\' donors.','compatible_only',[obs(txt,'TX-DN1-NORM')],'Dated regional distribution and a specific transfer.'),
       'R4':rival('Practical and ethical reasoning reconstructs a classification.','A classification is represented, but its invention history is unobserved.','compatible_only',[obs(txt,'TX-DN1-NORM')],'Independent contemporary repertoires or variant history.'),
       'R5':rival('A tradition organizes varied arts through its own livelihood norm.','DN 1 places calculation, prediction, treatment and ritual in an abstention-from-livelihood framework.','positive_observation',[obs(txt,'TX-DN1-NORM','TX-DN1-CALC','TX-DN1-TREAT')],'A surviving predecessor or variant sequence for a demonstrated redaction.')},
      'supported_endpoint','The classification shows mature organization at its own textual stage. It is neither an occupational census nor a traced Harappan package; individual older components and new grouping can coexist.'))
    with out.open('x',encoding='utf-8') as stream:
        json.dump({'scope':'Seven manually assessed component comparisons. Semantic judgments are independently reviewed; declaration checks do not adjudicate them.',
                   'comparisons':comparisons},stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'comparisons':len(comparisons),'rival_records':sum(len(row['rivals']) for row in comparisons)}))


if __name__=='__main__':main()
