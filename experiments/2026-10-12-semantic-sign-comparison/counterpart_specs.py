"""Authored semantic selections. Source values are resolved and checked by the builder.

The selections are descriptive after source inspection, not a registered benchmark.
Tuple fields: id, concept, lemma, guideword, sense, displayed source reading,
canonical sign names. Multi-sign sequences retain their components.
"""
SUMERIAN = [
 ('S-carry','carry','il','raise','to raise, carry','il₂',['IL₂']),
 ('S-comb-mush','comb','muš','comb','a comb','muš',['MUŠ']),
 ('S-comb-garig','comb','garig','comb','comb','ga-rig₂',['GA','ZUM']),
 ('S-harrow','harrow','ganur','harrow','harrow','gan₂-ur₃',['GAN₂','|GA₂×NUN&NUN|']),
 ('S-plough','plough','apin','plow','(seed) plow','apin',['APIN']),
 ('S-staff','staff','ŋidru','scepter','scepter, stick','ŋidru',['PA']),
 ('S-person','person','lu','person','person','lu₂',['LU₂']),
 ('S-female-worker','person','geme','worker','female worker','geme₂',['|SAL.KUR|']),
 ('S-pot','vessel','dug','pot','(clay) pot','dug',['DUG']),
 ('S-house','house','e','house','house','e₂',['E₂']),
 ('S-storehouse','storehouse','ŋanun','storehouse','storehouse','ŋa₂-nun',['GA₂','NUN']),
 ('S-door','door','ig','door','door','ig',['IG']),
 ('S-field','field','gana','field','field','gana₂',['GAN₂']),
 ('S-fish','fish','kud','fish','fish','ku₆',['HA']),
 ('S-bird','bird','mušen','bird','bird','mušen',['HU']),
 ('S-sheep','animal','udu','sheep','sheep','udu',['LU']),
 ('S-goat','animal','maš','goat','goat','maš',['MAŠ']),
 ('S-ox','animal','gud','ox','bull, ox','gud',['GUD']),
 ('S-horn','horn','si','horn','horn','si',['SI']),
 ('S-grain','grain','še','barley','barley','še',['ŠE']),
 ('S-reed','plant','gi','reed','reed, cane','gi',['GI']),
 ('S-tree','plant','ŋeš','tree','tree','ŋeš',['GIŠ']),
 ('S-branch','branch','pa','branch','branch, frond','pa',['PA']),
 ('S-bundle','bundle','sa','bundle','reed-bundle','sa',['SA']),
 ('S-water','water','a','water','water','a',['A']),
 ('S-textile','textile','tug','textile','textile, garment','tug₂',['TUG₂']),
 ('S-rope','rope','eš','rope','rope, thong, string','eš₂',['EŠ₂']),
 ('S-net','net','sabar','net','a net','sa-bar',['SA','BAR']),
 ('S-bow','bow','pana','bow','bow','pana',['PAN']),
 ('S-arrow','arrow','gagsisa','arrow','arrow','gag-si-sa₂',['KAK','SI','DI']),
 ('S-wheel','wheel','umbin','wheel','wheel','umbin',['UMBIN']),
 ('S-total','total','šuniŋin','total','total, sum','šu-niŋin₂',['ŠU','LAGAB']),
]

# Exact source token IDs, including a deliberately retained damaged comparison.
AKKADIAN = [
 ('A-milk-carrier','carry','P372798.9.2','milk-carrier'),
 ('A-chair-carrier','carry','P405378.12.3','chair-carrier'),
 ('A-carry-verb','carry','P405385.10.1','bring'),
 ('A-staff','staff','P405340.9.2','sceptre'),
 ('A-plough','plough','P405361.9.4','(seed) plough'),
 ('A-person','person','P405432.4.1','man'),
 ('A-house','house','P405432.7.2','house'),
 ('A-sheep','animal','P405121.4.2','sheep'),
 ('A-ox','animal','P372788.4.2','ox'),
 ('A-water','water','P405236.6.4','water'),
 ('A-comb','comb','P405176.3.4','comb'),
]

# AES OK & FIP tokens. Selector codes are whole word spellings, not an assignment
# of the word meaning to every individual component.
EGYPTIAN_WORDS = [
 ('E-carry-A119','carry','63460','A119','carry'),
 ('E-carry-A9','carry','63460','I9-A9','carry'),
 ('E-pot','vessel','183020','W22','clay jar'),
 ('E-house','house','60220','O1','house'),
 ('E-enclosure','house','100010','O6-X1-D29','Ka-house / funerary chapel'),
 ('E-water','water','69000','N35-N35-N35','water'),
 ('E-grain','grain','32830','M33','barley'),
 ('E-fish','fish','73880','K1-K2-K3','fish'),
 ('E-plough','plough','98010','O4-D58-U13','plough'),
 ('E-textile','textile','71170','S28','clothing'),
]

# Supplementary sign-list uses. Its inventory is principally Middle Egyptian;
# explicit Old Kingdom examples are recorded separately in evidence notes.
EGYPTIAN_LIST = [
 ('E-person','person','A1',442,5,'person','logogram or classifier'),
 ('E-official','staff','A21',444,7,'official / noble','logogram or classifier'),
 ('E-old-man','staff','A19',444,7,'old / eldest','logogram or classifier'),
 ('E-door','door','O31',496,60,'door','logogram or classifier'),
 ('E-cup','vessel','W10',528,92,'cup','classifier; other sound uses'),
 ('E-relation-bowl','relation','W24',531,94,'nw; plural genitive','phonetic sign'),
 ('E-arrow','arrow','T11',512,76,'arrow','classifier; other sound uses'),
 ('E-cord','rope','V6',522,86,'cord / rope','word sign or classifier; other sound uses'),
]

# Sign, source chart id, zero-based chart column and row, source abbreviation,
# concept, own English interpretation. These labels are supplied in the charts.
LINEAR_B = [
 ('B100','liber-logograms-100-v1',0,0,'VIR','person','man'),
 ('B102','liber-logograms-100-v1',0,1,'MULier','person','woman'),
 ('B106','liber-logograms-100-v1',0,6,'OVIS','animal','sheep'),
 ('B107','liber-logograms-100-v1',0,10,'CAPer','animal','goat'),
 ('B109','liber-logograms-100-v1',1,5,'BOS','animal','bovine'),
 ('B120','liber-logograms-100-v1',2,4,'GRAnum','grain','grain'),
 ('B121','liber-logograms-100-v1',2,7,'HORDeum','grain','barley'),
 ('B145','liber-logograms-100-v1',3,7,'LANA','textile','wool'),
 ('B151','liber-logograms-100-v1',4,11,'CORNu','horn','horn'),
 ('B159','liber-logograms-100-v1',5,7,'TELA','textile','cloth'),
 ('B176','liber-logograms-168-v1',0,8,'ARB','plant','tree'),
 ('B200','liber-logograms-168-v1',1,8,'VAS','vessel','vessel'),
 ('B202','liber-logograms-168-v1',1,10,'VAS','vessel','vessel'),
 ('B231','liber-logograms-168-v1',4,0,'SAGitta','arrow','arrow'),
 ('B243','liber-logograms-168-v1',4,8,'ROTA','wheel','wheel'),
]

# These are retrieval links to possible semantic alternatives, never matches to
# every qualified member of a family. Unlisted families receive an explicit gap.
FAMILY_CONCEPTS = {
 'quantity_strokes':['quantity'], 'bounded_tallies':['quantity','total'],
 'forked_stem':['branch','staff'], 'headed_shaft':['staff'],
 'human_agent':['person'], 'paired_agents':['person'], 'enclosed_human':['person','house'],
 'object_handling_person':['person','carry'], 'animal_or_hide_bearer':['person','animal'],
 'fish_bearer':['person','fish'], 'bow_bearer':['person','bow'],
 'paired_work_party':['carry','person'], 'creature_bearer':['person','animal'],
 'toothed_tool_bearer':['harrow','plough','person'], 'crossed_body_equipment':['carry','person'],
 'staff_bearer':['staff','person'], 'carrier_yoke':['carry'],
 'looped_cover':['rope'], 'paired_suspended_ovals':['carry','vessel'],
 'multi_appendage_creature':['animal'], 'loop_chain':['rope','total'],
 'fish_shapes':['fish'], 'bird_shapes':['bird'], 'rooted_oval':['plant'],
 'bent_parallel_rows':['bundle'], 'many_legged_outline':['person','bundle'],
 'compartmented_frame':['storehouse','house'], 'forked_leaf_vessel':['plant','vessel'],
 'horned_animal':['animal','horn'], 'dangling_loop':['rope','carry'],
 'rail_tally':['bundle','quantity'], 'gate_frame':['door'],
 'flag_panel':['house','door','textile'], 'circled_stem':['plant','staff'],
 'leaf_cluster':['plant','branch'], 'plant_branch':['plant','branch'],
 'toothed_closer':['comb','total'], 'toothed_implements':['comb','harrow','plough'],
 'bound_stalks':['bundle','grain','plant'], 'wave_zigzag':['water'],
 'angular_support':['carry','plough'], 'peaked_band':['house','textile'],
 'triangular_leaf':['plant','arrow'], 'handled_rectangle':['vessel','storehouse'],
 'binding_bowtie':['rope','relation'], 'gateway_compound':['door','storehouse'],
 'arrow_shaft':['arrow'], 'plain_divided_enclosure':['house','field'],
 'toothed_border_box':['storehouse','house'], 'grid_compartments':['storehouse','net','textile'],
 'cup_vessels':['vessel'], 'sprouting_vessel':['plant','vessel'],
 'rooted_cup':['plant','vessel'], 'rim_marked_vessel':['vessel','relation'],
 'terminal_qualified_vessel':['vessel','grain','plant'],
 'enclosed_emblem':['field','house'], 'wheel_spokes':['wheel'],
 'woven_mesh':['textile','net'], 'paired_oval_join':['rope','relation'],
 'diamond_enclosure':['field','house'], 'bow_or_curved_blade':['bow'],
 'arch_canopy':['house','storehouse'], 'enclosed_fish_group':['fish'],
}

REVIEWED_CODES = ['151','154','156','158','161','400','527','142','130']
