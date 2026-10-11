"""Authored readings for 215 codes inspected in five local font contact sheets.

Groups are our visual comparisons, not additions to the upstream graphic crosswalk.
"""
from semantic_hypotheses import sense
ROWS={}

def group(codes, meaning, words, role, alternatives, shape, anchors=()):
    for code in codes.split():
        assert code not in ROWS,code
        ROWS[code]={**sense(meaning,words,role,alternatives,shape),
                    'new_anchor_connections':list(anchors),'visual_witness':'unmapped-glyph-sheet'}

group('036 037 039','tall-stroke quantity or counted class',['saṃkhyā','aṅka'],'quantity',
 ['a numerical name component'],'Several tall parallel strokes form a tally; precise base/unit remains open.')
group('041 042 043','mixed tall/short units or a qualified count',['aṅka','māna'],'quantity',
 ['a name abbreviation','a delimited account field'],'Tall strokes combine with shorter ticks at several positions.')
group('047 050','delimited quantity or institution-qualified count',['saṃkhyā','māna'],'quantity',
 ['registered people or lots'],'Parallel strokes stand inside curved boundaries.')
group('056 059','grouped total or multiple batches',['rāśi','gaṇa'],'quantity',
 ['separate accounting fields'],'Ticks occur in several rows or diagonally grouped pairs.',('N07',))
group('067 068','count-plus-juncture or a linked allotment',['aṅka','sambandha'],'grammar',
 ['a numeral sound abbreviation'],'A diagonal stroke joins one or two short upright strokes.')
group('069','paired persons or shared labour unit',['yugala','gaṇa'],'person',
 ['two arrow-like issuer marks'],'Two upright forked forms stand side by side.')
group('074 075','plant-staff or crop-related personal name',['śasya','bīja'],'commodity',
 ['a spear or flag name'],'A long stem carries a curved or peaked head.',('N14',))
group('082 084 085','supervised or registered office-holder',['adhikārin','daṇḍin'],'title',
 ['a star/weapon personal name'],'A staff/person-like stem bears a star and an arch or enclosing strokes.',('N08',))
group('092','vessel worker or headed household representative',['kumbhakāra','jana'],'labour',
 ['a ranked person or issuer'],'An inverted triangle sits above a branching human-like stem.')
group('096 099','person, labour unit or name element',['jana','nara'],'person',
 ['an arrow or branching plant'],'A vertical trunk has arms and split legs.')
group('102','registered worker or enclosed household',['jana','kula'],'person',
 ['a syllabic person-name ligature'],'A person with raised hands stands inside curved boundaries.')
group('115 116','vessel handler, goods protector or specialized worker',['kumbhakāra','rakṣaka'],'labour',
 ['a shield-bearing guard','a compound personal name'],'A person holds an oval, vessel or elaborate bent implement.')
group('128 129','cattle keeper or livestock-related work party',['gopāla','paśu'],'labour',
 ['a cattle-named person','an animal product allotment'],'A person is joined to one or two animal-head-like outlines.',('N10',))
group('132','cultivator or fork-tool worker',['kṛṣaka','hala'],'labour',
 ['an agricultural name element'],'A person holds a forked implement.',('N09',))
group('135 136','qualified labour or ranked worker',['karmakara','jana'],'labour',
 ['a multi-element personal name'],'The person carries multiple short lateral strokes or arm-like branches.')
group('138','cart worker, wagoner or mobile service',['vāhana','śakaṭa'],'labour',
 ['a ranked household emblem'],'Two circles appear at the feet of a human-like figure.',('N01',))
group('139','craft worker or implement-related name',['śilpin','karman'],'labour',
 ['a small personal-name ligature'],'A person has an attached angular tool near the leg.')
group('141','registered vessel-worker or named recipient',['kumbhakāra','kula'],'labour',
 ['a vessel receipt classifier'],'A person/vessel outline is enclosed by parentheses.')
group('147','cloth/standard bearer or supervised consignment',['vastra','vāha'],'labour',
 ['a flag-bearing official'],'A person is joined to a hatched triangular panel and staff.',('N06','N01'))
group('148','holding-associated official or estate recipient',['kṣetra','pati'],'title',
 ['a diamond-name compound'],'A diamond-like outline lies across a person.',('N04',))
group('150 152','potter, vessel worker or container household',['kumbhakāra','kumbha'],'labour',
 ['a capacity or vessel-name component'],'A person has a cup-shaped upper component.')
group('157 172 173','framed transport, carried loads or delivery service',['bhāra','vāha'],'labour',
 ['a paired vessel allocation','a transport-household name'],'Two pendants/ovals hang from a raised frame.',('N01',))
group('180','animal product, hide or processed material',['carma','paśu'],'commodity',
 ['a phonetic animal name'],'A long oval has multiple projecting strokes at one end.',('N10',))
group('191 195','fibre work, crop processing or plant-product lot',['vastra','śasya'],'commodity',
 ['a pincer-name compound'],'Oval bodies have radiating side branches, sometimes paired.',('N06',))
group('219','paired asset units or joint fish-related account',['māna','yugala'],'measure',
 ['two fish or a fish-name ligature'],'Two fish-like forms stand side by side.')
group('221 223 224 225','registered asset denomination or qualified fish unit',['māna','tulā'],'measure',
 ['enclosed fishery produce','a phonetic fish-name variant'],'A fish-like form is surrounded by curved or vertical boundaries.')
group('229 230 237 250 251 252 253 257','qualified asset/weight class or fish-related name',['māna','matsya'],'measure',
 ['fish produce','a personal-name syllable'],'The fish-like body has extra head, foot, hatching or attached strokes.')
group('261 263 276 277 278 279','bird-related service, messenger or bird-named party',['pakṣin','dūta'],'person',
 ['poultry/feather goods','a phonetic bird-name sign'],'Bird/neck shapes appear singly, paired, filled or with additional strokes.',('N11',))
group('298','shared access, joined premises or paired frame',['setu','sopāna'],'institution',
 ['a doubled sound sign'],'Three bent bars form a repeated frame-like outline.',('N05',))
group('310 311','water/vessel delivery or multi-unit container account',['udaka','kumbha'],'commodity',
 ['a many-legged person or issuer emblem'],'Round or cellular upper bodies stand above several descending strokes.',('N03',))
group('316 320 326 327 328 330','divided store, tiered premises or storage section',['koṣṭha','sopāna'],'institution',
 ['a metrological frame','a joined phonetic sign'],'H-shaped or rectangular frames carry rows, internal divisions or extra legs.',('N05','N04'))
group('351','botanical holding, fruit crop or plant-name element',['phala','bīja'],'commodity',
 ['a paired-crescent name'],'An oval body rises to two outward stems.',('N14',))
group('376','bounded stem/crop holding or protected seed lot',['bīja','kṣetra'],'commodity',
 ['a phonetic field marker'],'A circular-headed stem stands between two curves.',('N14','N04'))
group('381 383','leaf/fruit produce or botanical estate',['phala','śasya'],'commodity',
 ['a leaf-shaped account denomination'],'A heart/leaf outline stands alone or with a short downward stem.',('N14',))
group('386 387','graded produce, grain lot or accounted crop',['dhānya','śasya'],'commodity',
 ['a scale or quantity emblem'],'A leaf/round body contains repeated parallel strokes.',('N02',))
group('389','four-part crop grouping or orchard/seed allocation',['śasya','bīja'],'commodity',
 ['four named parties or a composite numeral'],'Four branching plant-like stems stand side by side.',('N14',))
group('401','paired count records or joint inventory',['gaṇanā','gaṇa'],'operation',
 ['two comb/plant-name signs'],'Two stems have short horizontal strokes on one side.',('N07',))
group('403','grain group or joined crop allotment',['dhānya','yava'],'commodity',
 ['a shared vessel or work-party emblem'],'Several looped/crop-like outlines share a horizontal base.',('N02',))
group('404','crop-processing tool or agricultural service',['kṛṣi','hala'],'operation',
 ['a phonetic rake name'],'An inclined forked head stands on a four-legged base.',('N09',))
group('409 410','qualified tally or account total',['gaṇanā','gaṇa'],'operation',
 ['grain stem or textile tool'],'Short side strokes run along a vertical staff; their direction differs.',('N07',))
group('418 424','registered/divided crop or workshop account',['koṣṭha','dhānya'],'institution',
 ['a counted implement name'],'Forked or multiple strokes are enclosed in a rectangular frame.',('N02','N04'))
group('441 442 444 445','premises, doorway or qualified institutional space',['agāra','śālā'],'institution',
 ['a measured length or phonetic arch'],'One or two open-bottom arches carry internal or outline modifications.',('N16',))
group('453','paired water/channel allocation',['udaka','jala'],'commodity',
 ['a doubled phonetic zigzag'],'Two parallel waves are drawn together.',('N03',))
group('458','joint gift, paired wealth or divided portion',['dhana','bhāga'],'measure',
 ['a double-bow personal-name element'],'Two opposing triangles/bows share a central staff.',('N12',))
group('462','crop held by a grouped institution or three-part allocation',['śasya','rāśi'],'institution',
 ['a botanical name or heraldic device'],'A leaf/tree stands above three triangular outlines.',('N02',))
group('463 479','multiple hills/places or grouped allotments',['adri','rāśi'],'institution',
 ['a numerical classifier'],'Two or three angular peaks stand side by side.')
group('481','counted/qualified hill, store or place',['adri','koṣṭha'],'institution',
 ['a graded triangular quantity unit'],'A tall triangular frame has two short inner ticks.')
group('491 492 493 494 495 501','subdivided container, measured share or graded amount',['māna','bhāga'],'measure',
 ['a storage unit or phonetic panel'],'A triangular/tapered body is partitioned by horizontal strokes.',('N12',))
group('506','registered measured lot or bounded store',['māna','koṣṭha'],'measure',
 ['a name enclosed by field marks'],'A divided central body is framed by several short boundary strokes.')
group('514','ranked official, record board or accounted obligation',['gaṇanā','adhikārin'],'title',
 ['a phonetic boxed-staff compound'],'A long staff carries a small rectangular panel with horizontal ticks.',('N07','N08'))
group('515 516 519','acceptance/valuation class or arrow-named party',['īśa','māna'],'grammar',
 ['a counted issuer emblem'],'One or two arrow-like forms have additional tips; comparison extends Bonta’s arrow.')
group('525','allotment ledger or joined holding',['bhāga','kṣetra'],'institution',
 ['a phonetic side-box sign'],'A small square joins a long vertical staff.',('N04','N12'))
group('534 535 541 543 544 546 547 552 563','qualified shared portion, exchange or contribution',['bhāga','saṃyoga'],'measure',
 ['a commodity/office ligature','a sound compound'],'Crossed or opposed triangular panels carry extra sides, hatching, curves or ticks.',('N12','N13'))
group('576 577 585 586','protected premises, raised store or supervised worksite',['śālā','koṣṭha'],'institution',
 ['a phonetic arch/roof name'],'An arch/frame is topped or combined with a peaked interior and boundary strokes.',('N16','N05'))
group('591 596 597','container account, storage record or qualified household',['koṣṭha','lekha'],'institution',
 ['a phonetic name/sign formed with ka'],'A square hanging from a staff carries bands or ticks.',('N04','N07'))
group('599','three stores, grouped holdings or three account units',['koṣṭha','rāśi'],'institution',
 ['a triple quantity sign'],'Three plain rectangles stand together.',('N04',))
group('601 606 617 620 627 629','divided holding, store compartments or registered batches',['koṣṭha','kṣetra'],'institution',
 ['metrological lot classes','a rectangular phonetic sign'],'Rectangles contain grids, short inner ticks or paired compartments.',('N04','N05'))
group('641 643','institution-qualified exchange or joined account',['saṃyoga','koṣṭha'],'institution',
 ['a framed personal-name element'],'A rectangle carries internal/corner marks, once with a crossed central element.',('N13','N04'))
group('646 647','qualified joint contribution or partnership',['saha','saṃyoga'],'grammar',
 ['a multiplied issuer mark'],'An X carries extra upper or lower strokes.',('N13',))
group('681 682 687','corporate issuer, joined authority or registered group',['gaṇa','adhikārin'],'title',
 ['an asterisk-name or commodity emblem'],'Multiple rays meet centrally, sometimes under a rectangular roof.',('N13','N08'))
group('697 698 699','multiple rations, paired containers or grouped capacity',['kumbha','rāśi'],'measure',
 ['a plural sound compound'],'Two or three cup outlines stand together, sometimes with inner staffs.')
group('702 713 714 715 718 720 722 723','specified capacity, processed contents or qualified vessel lot',['kumbha','māna'],'measure',
 ['a container-name element'],'Cup/rectangular vessel forms contain ticks, wedges, hatching or an attached panel.')
group('725 727 728 729 733','issued/received vessel unit or qualified recipient',['kumbha','vāha'],'operation',
 ['a phonetic cup-staff compound'],'A cup merges with an extended stem, fork or oblique lower stroke.')
group('759 762 763','issuer-linked vessel account or designated institutional ration',['kumbha','śālā'],'institution',
 ['a capacity name with a phonetic modifier'],'A vessel encloses a wheel, person-like figure or elongated pendant.',('N15','N16'))
group('766 775 780 781','paired/qualified allocation or registered recipient',['bhāga','gaṇa'],'measure',
 ['a linked pair of phonetic signs'],'Cup arms bear leaves, arrows or an additional fish-like body.',('N12',))
group('791 792 793 794 795 799 801','paired or qualified estate/large lot',['kṣetra','bhāga'],'institution',
 ['large denomination classes','plant-name phonetic signs'],'Oval/leaf forms are paired, dotted, enclosed or joined to lateral strokes.',('N04','N12'))
group('811','authority-affiliated holding or arrow-qualified lot',['kṣetra','īśa'],'institution',
 ['a valued asset denomination'],'A single arrow stands inside an oval.',('N04',))
group('821 822','paired/registered divine or corporate issuer',['deva','gaṇa'],'title',
 ['wheel-related workshops','a counted emblem'],'Two six-spoke wheels stand together, or one stands within vertical boundaries.',('N15',))
group('824','joined institutional holdings or woven commodity lot',['saṃyoga','vastra'],'institution',
 ['a wheel/estate graphic variant'],'An oval is filled by several crossing lines.',('N13','N06'))
group('826 827 828 829 830 835 836 837 838 839','graded holding, subdivision or large account unit',['kṣetra','bhāga'],'institution',
 ['metrological denomination grades','a botanical name element'],'An oval contains one or more ticks/dividers, or small outer strokes.',('N04','N12'))
group('842 843 844','joint lordship, shared holding or paired office',['pati','saha'],'title',
 ['a double estate denomination'],'Overlapping pointed ovals are enclosed, bounded or marked with inner dots.',('N13',))
group('849 852 854 855 856 857 862 866 872 874 875 876','qualified office, affiliated holding or responsible recipient',['pati','adhikārin'],'title',
 ['an estate grade or personal-name compound'],'A diamond form carries ticks, enclosing strokes, an inner diamond, rays or other attachments.',('N08',))
group('893 897 898','paired/qualified wealth, gift or donation account',['dhana','dāna'],'measure',
 ['a bow-name element'],'Bow/D-shaped outlines are doubled, hatched or crossed by an additional stroke.')
group('899 907 910 911 912 914 918 919','recipient/source affiliation, linked parties or grammatical qualification',['sambandha','saha'],'grammar',
 ['a crescent-name sound','a commodity-shaped curved sign'],'Curved brackets occur singly, paired or in multiples with internal or surrounding ticks.',('N13',))
group('913','house, premises or institutional affiliation',['agāra','śālā'],'institution',
 ['a phonetic arch shape'],'A broad arch stands alone.',('N16',))
group('925','paired connection or qualified joining marker',['saṃyoga','saha'],'grammar',
 ['a channel or zigzag name'],'Two bent/zigzag bars run side by side.',('N13',))
group('933','institutional store or supervised worksite',['koṣṭha','śālā'],'institution',
 ['a phonetic peak/roof compound'],'A peaked frame with projecting ends stands on multiple legs.',('N05','N16'))
group('945','registered divine issuer or accounted corporate authority',['deva','gaṇa'],'title',
 ['a measured wheel denomination'],'A six-spoke wheel is flanked by long and short strokes.',('N15',))
group('947 951','joined produce/holding or paired recipient account',['bhāga','kṣetra'],'institution',
 ['a bird/person-name ligature'],'Oval, leaf or curved forms are joined across a central frame.',('N04','N12'))
group('953','field/store overseer or holding-associated worker',['kṣetra','adhikārin'],'title',
 ['a box-name compound'],'A person is joined to a small square on the upper body.',('N04','N08'))
group('957','crop/tally-related official or qualified account category',['gaṇanā','kṛṣi'],'operation',
 ['a staff-name compound'],'A curved long staff bears several short lateral strokes.',('N07','N09'))
group('958','supervised crop-work or premises obligation',['kṛṣi','śālā'],'operation',
 ['a combined personal name'],'A peaked structure is joined to a forked branch and an extended base.',('N09','N16'))
