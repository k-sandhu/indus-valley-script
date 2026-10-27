"""Original schematic meshes from cited dimensions. Standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
MATERIALS = {
    'brick': '#b66d4c', 'brick-light': '#d19b6c', 'stone': '#b7ac8b',
    'earth': '#82735b', 'ground': '#cfc2a1', 'floor': '#d1b891',
    'water': '#438d9b', 'bitumen': '#373b39', 'roof': '#8a7263',
    'route': '#dccc9d', 'district': '#a29776', 'wood': '#79604e',
    'pit': '#72664f', 'marker': '#ede0bc',
}


class Scene:
    def __init__(self, sid, name, site, kind, summary, extent, orientation):
        self.d = dict(id=sid, name=name, site=site, kind=kind, summary=summary,
                      extent_m=extent, orientation=orientation,
                      phase='Architectural synthesis; components may belong to different building episodes.',
                      features=[], meshes=[], dimensions=[], labels=[])

    def feature(self, fid, name, description, sources, footprint, placement, vertical,
                assumptions, focus, span, detail=None):
        f = dict(id=fid, name=name, description=description, sources=sources,
                 footprint=footprint, placement=placement, vertical=vertical,
                 assumptions=assumptions, focus=focus, span=span)
        if detail:
            f['detail_model'] = detail
        self.d['features'].append(f)
        return fid

    def mesh(self, feature, vertices, faces, material, role='structure', variable=False,
             base=0, cut=False, evidence='schematic'):
        self.d['meshes'].append(dict(feature=feature, vertices=vertices, faces=faces,
                                    material=material, role=role, variable=variable,
                                    base=base, cut=cut, evidence=evidence))

    def box(self, f, x, y, z, w, l, h, mat='brick', **kw):
        v = [[x-w/2,y-l/2,z],[x+w/2,y-l/2,z],[x+w/2,y+l/2,z],[x-w/2,y+l/2,z],
             [x-w/2,y-l/2,z+h],[x+w/2,y-l/2,z+h],[x+w/2,y+l/2,z+h],[x-w/2,y+l/2,z+h]]
        self.mesh(f,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat,**kw)

    def quad(self, f, v, mat, **kw):
        self.mesh(f,v,[[0,1,2,3]],mat,**kw)

    def enclosure(self, f, x, y, z, w, l, thick, h, mat='brick', **kw):
        self.box(f,x,y-l/2+thick/2,z,w,thick,h,mat,cut=True,**kw)
        self.box(f,x,y+l/2-thick/2,z,w,thick,h,mat,**kw)
        self.box(f,x-w/2+thick/2,y,z,thick,l-2*thick,h,mat,**kw)
        self.box(f,x+w/2-thick/2,y,z,thick,l-2*thick,h,mat,cut=True,**kw)

    def ring(self, f, x,y,z,rx,ry,t,h, mat='brick', **kw):
        n=24
        for i in range(n):
            a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
            v=[]
            for zz in [z,z+h]:
                v += [[x+rx*math.cos(a),y+ry*math.sin(a),zz],
                      [x+rx*math.cos(b),y+ry*math.sin(b),zz],
                      [x+(rx-t)*math.cos(b),y+(ry-t)*math.sin(b),zz],
                      [x+(rx-t)*math.cos(a),y+(ry-t)*math.sin(a),zz]]
            self.mesh(f,v,[[4,5,6,7],[0,1,5,4],[2,3,7,6]],mat,**kw)

    def dimension(self, label, value, source, locator, start=None, end=None, interval=None):
        d=dict(label=label, value_m=value, source=source, locator=locator,
               status='published approximate dimension', start=start,end=end)
        if interval: d['published_range_m']=interval
        self.d['dimensions'].append(d)

    def label(self, text, p):
        self.d['labels'].append(dict(text=text, p=p))


def great_bath():
    s=Scene('great-bath','Great Bath','Mohenjo-daro','building',
            'A metric basin with opposed stairs, ledges and a visible waterproof lining. The surrounding rooms and colonnade are a spatial teaching diagram.',
            42,'North is +Y. The basin follows the published north–south direction.')
    s.feature('ground','Display ground','A neutral model plinth.', ['KENOYER-BATH'],
              'Display only','Display only','Display only', ['The plinth is not an excavated layer.'],[0,0,0],35)
    s.box('ground',0,0,-.35,33,36,.35,'ground',role='ground')
    s.feature('basin','Basin and brick lining','The published internal basin is approximately 12 m north–south by 7 m east–west, with a maximum depth of 2.4 m.',
              ['KENOYER-BATH'],'Published approximate 12 × 7 m interior','Centred for display','Published maximum depth 2.4 m',
              ['Wall thickness 1.1 m is illustrative; alternative display range 0.7–1.6 m.','The floor is drawn level. Joints show material, not individually surveyed bricks.'],[0,0,1.2],17)
    s.box('basin',0,0,-.18,9.2,14.2,.18,'brick',evidence='dimensioned')
    s.box('basin',0,0,.005,7,12,.025,'floor',role='floor',evidence='dimensioned')
    s.enclosure('basin',0,0,0,9.2,14.2,1.1,2.4,evidence='dimensioned')
    s.feature('waterproof','Waterproof layer','The caption describes gypsum mortar and bitumen beside the fitted brick lining.',
              ['KENOYER-BATH'],'Construction described; band thickness assumed','Illustrative lining','Same basin depth',
              ['Dark 0.07 m strips exaggerate the bitumen layer for legibility.'],[0,0,1],15)
    s.enclosure('waterproof',0,0,0,9.34,14.34,.07,2.35,'bitumen',evidence='described')
    s.feature('stairs','Opposed stairs and ledges','Two stairways enter the basin from the north and south; ledges cross the basin near their feet.',
              ['KENOYER-BATH'],'Described arrangement','Opposed ends; illustrative tread positions','Rise follows the fixed 2.4 m basin depth',
              ['Ten steps per flight, 2.5 m flight width and 0.3 m treads are display assumptions.','Ledge projection and height are illustrative.'],[0,0,1],16)
    for sign in [-1,1]:
        for i in range(10):
            s.box('stairs',0,sign*(3.15+.3*i),0,2.5,.3,.24*(i+1),'brick-light',evidence='described')
        s.box('stairs',0,sign*2.7,0,7,.6,.23,'brick-light',evidence='described')
    s.feature('colonnade','Colonnade and rooms','The source describes a colonnade on three sides, rooms to the east and a well in one room.',
              ['KENOYER-BATH'],'Arrangement described; envelope and room sizes assumed','Schematic, not a traced building plan','3 m walls and 3.5 m columns assumed; adjustable',
              ['Four rooms and twelve columns are explanatory choices, not excavated counts.','Optional roofs show one possible coverage; the basin remains open.','The well diameter is assumed. No supply pipe is drawn.'],[0,0,2.4],34)
    # Paving outside the basin leaves the pool open.
    for x in [-7.9,7.9]: s.box('colonnade',x,0,2.2,5.5,23,.2,'floor',evidence='schematic')
    for y in [-10,10]: s.box('colonnade',0,y,2.2,10.3,4,.2,'floor')
    for x in [-6.2,6.2]:
        for y in [-8,-4,0,4,8]:
            s.box('colonnade',x,y,2.4,.65,.65,3.5,'brick-light',variable=True,base=2.4)
    for y in [-10,10]:
        s.box('colonnade',0,y,2.4,.65,.65,3.5,'brick-light',variable=True,base=2.4)
    for y in [-8,-3,2,7]:
        s.enclosure('colonnade',12,y,2.4,4.2,4.5,.45,3,variable=True,base=2.4)
        s.box('colonnade',12,y,5.4,4.4,4.7,.25,'roof',role='roof',variable=True,base=2.4)
    s.ring('colonnade',12,7,2.4,1.1,1.1,.28,1,'brick-light',variable=True,base=2.4)
    for x in [-6.2,6.2]: s.box('colonnade',x,0,5.9,2.3,23,.25,'roof',role='roof',variable=True,base=2.4)
    for y in [-10,10]: s.box('colonnade',0,y,5.9,10.3,2.3,.25,'roof',role='roof',variable=True,base=2.4)
    s.feature('water','Display water','A reversible water plane helps show the basin. It is not a recovered ancient water level.', ['KENOYER-BATH'],
              'Display surface','Within basin','Illustrative 1.2 m above floor',['No water capacity estimate is derived from this model.'],[0,0,1.2],16)
    s.quad('water',[[-3.5,-6,1.2],[3.5,-6,1.2],[3.5,6,1.2],[-3.5,6,1.2]],'water',role='water')
    s.dimension('Basin length',12,'KENOYER-BATH','Caption paragraph 1',[-4.8,-6,2.5],[-4.8,6,2.5])
    s.dimension('Basin width',7,'KENOYER-BATH','Caption paragraph 1',[-3.5,-7.8,2.5],[3.5,-7.8,2.5])
    s.dimension('Maximum depth',2.4,'KENOYER-BATH','Caption paragraph 1',[4.9,-6,0],[4.9,-6,2.4])
    s.label('NORTH STAIRS',[0,5,2.8]); s.label('EAST ROOMS',[12,0,6])
    return s


def reservoir():
    s=Scene('dholavira-reservoir','Eastern reservoir','Dholavira','building',
            'The sloping basin follows the report’s top and bottom spans. A small northern probe shows the deeper cut; its unknown extent stays schematic.',
            94,'North is +Y. The long axis follows the published north–south direction.')
    s.feature('ground','Display ground','A plinth frames the basin.', ['BISHT-2015-PRELIM'],'Display only','Display only','Display only',['Ground surface is idealized.'],[0,0,6],88)
    # Top lip at 10.6, ordinary floor at 3.25: general depth 7.35 m.
    top=10.6;floor=3.25;w=29.3;l=73.45;bw=27.725;bl=70
    for x in [-20,20]:s.box('ground',x,0,top-1.3,9,82,1.3,'ground',role='ground')
    for y in [-39,39]:s.box('ground',0,y,top-1.3,31,5,1.3,'ground',role='ground')
    s.feature('basin','Sloping stone basin','The report gives a 73.40–73.50 m top length and 29.30 m top width. The ordinary bottom spans are about 70 m and 27.70–27.75 m.',
              ['BISHT-2015-PRELIM'],'Published top and bottom spans','Centred schematic basin; four sloping faces','General depth 7.20–7.50 m; model uses 7.35 m',
              ['The simple continuous slope interpolates published end dimensions.','Local irregular masonry and rock profiles are not surveyed here.'],[0,0,6],87)
    corners=[[-w/2,-l/2,top],[w/2,-l/2,top],[w/2,l/2,top],[-w/2,l/2,top]]
    bot=[[-bw/2,-bl/2,floor],[bw/2,-bl/2,floor],[bw/2,bl/2,floor],[-bw/2,bl/2,floor]]
    for i in range(4):
        j=(i+1)%4;s.quad('basin',[bot[i],bot[j],corners[j],corners[i]],'stone',cut=i in [0,1],evidence='dimensioned')
    # Divide the ordinary floor around an explicitly schematic deeper probe.
    s.box('basin',0,-6.5,floor-.2,bw,57,.2,'floor',evidence='dimensioned')
    for x in [-9.93,9.93]:s.box('basin',x,28.5,floor-.2,7.86,13,.2,'floor',evidence='dimensioned')
    s.box('basin',0,34,floor-.2,12,2,.2,'floor',evidence='dimensioned')
    s.enclosure('basin',0,0,top,w+2,l+2,1,1.1,'stone',evidence='dimensioned')
    s.feature('probe','Deep northern probe','The excavator reports a maximum cut of 10.60 m in a limited northern probe. The extent of an equally deep central zone remains open.',
              ['BISHT-2015-PRELIM'],'Probe extent unknown; display rectangle 12 × 11 m','Northern part as reported; exact rectangle assumed','10.60 m maximum cut from top datum shown',
              ['The 12 × 11 m outline is a display assumption, not an excavation boundary.','The deeper cut is not applied to the whole reservoir.'],[0,27.5,2],30)
    s.box('probe',0,27.5,-.2,12,11,.2,'pit',evidence='described')
    for x in [-6,6]: s.box('probe',x,27.5,0,.2,11,floor,'stone',evidence='described')
    for y in [22,33]:s.box('probe',0,y,0,12,.2,floor,'stone',evidence='described')
    s.feature('stairs','Three stair flights','The report identifies three flights of steps as components of the reservoir.', ['BISHT-2015-PRELIM'],
              'Flights described; tread dimensions assumed','Illustrative NW, NE and SW positions; exact placement is not registered','Illustrative 30 steps through the general basin depth',
              ['Each 1.6 m flight and its 0.5 m tread are schematic.','These steps do not reconstruct a single precisely dated phase.'],[0,0,7],83)
    for x,sgn in [(-12,1),(12,1),(-12,-1)]:
        for i in range(30):
            y=sgn*(20.65+.5*i)
            s.box('stairs',x,y,floor,1.6,.5,(i+1)*(7.35/30),'stone',evidence='described')
    s.feature('water','Display water','A switchable plane illustrates stored water.', ['BISHT-2015-PRELIM'],
              'Display surface','Inside basin','Illustrative elevation only',['No ancient operating water level or volume is inferred.'],[0,0,7],86)
    s.quad('water',[[-13.8,-35,7],[13.8,-35,7],[13.8,35,7],[-13.8,35,7]],'water',role='water')
    s.dimension('Top length',73.45,'BISHT-2015-PRELIM','p.149; PDF index 165',[-18,-l/2,top+1.5],[-18,l/2,top+1.5],[73.4,73.5])
    s.dimension('Top width',29.3,'BISHT-2015-PRELIM','p.149; PDF index 165',[-w/2,-40,top+1.5],[w/2,-40,top+1.5])
    s.dimension('General depth',7.35,'BISHT-2015-PRELIM','p.149; PDF index 165',interval=[7.2,7.5])
    s.dimension('Limited northern maximum cut',10.6,'BISHT-2015-PRELIM','pp.149–150; PDF indices 165–166')
    s.label('DEEP PROBE: EXTENT ASSUMED',[0,27,11.8])
    return s


def gateway():
    s=Scene('dholavira-gate','Castle west gateway','Dholavira','building',
            'A 9 m passage, 2.2 m wide, connects the castle and bailey. The model opens the passage to expose the room and limestone-slab steps.',
            24,'East is +X; the passage runs approximately east–west in this schematic. The exact survey azimuth is not asserted.')
    s.feature('ground','Display ground','Ground and two levels separate the bailey and castle sides.',['BISHT-2015-PRELIM'],'Display only','Display only','Level difference assumed',['No measured gateway elevation is available in this model.'],[0,0,0],24)
    s.box('ground',0,0,-.4,23,18,.4,'ground',role='ground')
    s.feature('passage','Passage and slab steps','The excavator gives a 9 m long, 2.2 m wide west passage, with a small room in the south wall and steps at the outer end.',
              ['BISHT-2015-PRELIM'],'Published passage 9 × 2.2 m','Plan arrangement described; exact wall faces simplified','Slope, slab steps and 3.2 m wall height assumed',
              ['The northern wall was washed to passage floor level; the north wall here shows a possible superstructure.','The model is a cutaway spatial explanation of the description.'],[0,0,1],15)
    s.box('passage',0,0,0,9,2.2,.2,'floor',evidence='dimensioned')
    s.box('passage',0,3.1,.2,9,4,3.2,'stone',variable=True,base=.2,evidence='dimensioned')
    # Leave a south chamber open to the passage, with two wings and a back wall.
    for x in [-2.8,2.8]:s.box('passage',x,-2.1,.2,3.4,2,3.2,'stone',variable=True,base=.2,cut=True,evidence='described')
    s.box('passage',0,-4.1,.2,9,2,3.2,'stone',variable=True,base=.2,cut=True,evidence='described')
    for i in range(4):s.box('passage',-6.25+i*.5,0,0,.5,2.2,(i+1)*.05,'stone',evidence='described')
    s.box('passage',0,0,3.4,9,2.6,.35,'roof',role='roof',variable=True,base=.2)
    s.feature('guard-room','South side room','A small guard room is reported in the southern wall.', ['BISHT-2015-PRELIM'],
              'Room existence described; 2.2 × 2 m display size assumed','South of passage; exact recess position assumed','Floor at passage datum; superstructure assumed',
              ['The chamber opens into the south side of the passage.','Its designation follows the excavator’s account.'],[0,-2.1,.2],9)
    s.box('guard-room',0,-2.1,.2,2.2,2,.1,'floor',evidence='described')
    s.dimension('Passage length',9,'BISHT-2015-PRELIM','p.114; PDF index 130',[-4.5,5.8,.5],[4.5,5.8,.5])
    s.dimension('Passage clear width',2.2,'BISHT-2015-PRELIM','p.114; PDF index 130',[5.2,-1.1,.6],[5.2,1.1,.6])
    s.label('BAILEY',[ -8,0,.5]);s.label('CASTLE',[8,0,.5])
    return s


def hall():
    s=Scene('pillared-hall','Pillared Hall','Mohenjo-daro','building',
            'A 27.5 m square envelope holds four rows of five pillars. Roofs, pillar heights and exact row spacing are adjustable assumptions.',
            37,'North is +Y for display. The published caption establishes the row count; exact plan bearings are not recovered here.')
    s.feature('ground','Display ground','A neutral plinth frames the hall.',['KENOYER-HALL'],'Display only','Display only','Display only',['The plinth is not a surveyed mound profile.'],[0,0,0],37)
    s.box('ground',0,0,-.4,33,33,.4,'ground',role='ground')
    s.feature('floor','Hall envelope','The caption reports an approximately 27.5 m square hall.', ['KENOYER-HALL'],
              'Published approximate 27.5 × 27.5 m envelope','Regularized square','Floor drawn level',
              ['Later partitions and slope are omitted to expose the pillar arrangement.'],[0,0,0],34)
    s.box('floor',0,0,0,27.5,27.5,.2,'floor',evidence='dimensioned')
    s.enclosure('floor',0,0,.2,27.5,27.5,.65,1.15,'brick',variable=True,base=.2,evidence='dimensioned')
    s.feature('pillars','Twenty pillar positions','The source describes twenty square brick pillars in four rows; only two rows remain preserved.', ['KENOYER-HALL'],
              'Published row and pillar count; exact spacing assumed','Regular four-by-five array for inspection','4 m pillars are illustrative; adjustable',
              ['Pillar width 1.25 m and equal spacing are display assumptions.','The full array combines preservation with the source’s reconstruction.'],[0,0,2],32)
    for y in [-8.5,-2.83,2.83,8.5]:
        for x in [-10,-5,0,5,10]:s.box('pillars',x,y,.2,1.25,1.25,4,'brick-light',variable=True,base=.2,evidence='described')
    s.feature('roof','Possible roof','An optional roof lets us inspect the relationship between supports and covered space.', ['KENOYER-HALL'],
              'Illustrative roof','Display only','4.2 m level assumed',
              ['No excavated roof profile or timber size is claimed.'],[0,0,4.5],34)
    for y in [-8.5,-2.83,2.83,8.5]:s.box('roof',0,y,4.2,27.5,.45,.4,'wood',role='roof',variable=True,base=.2)
    s.box('roof',0,0,4.6,28.5,28.5,.2,'roof',role='roof',variable=True,base=.2)
    s.dimension('Hall side',27.5,'KENOYER-HALL','Slide 35 caption',[-13.75,-15,.4],[13.75,-15,.4])
    return s


def lothal():
    s=Scene('lothal-basin','Large basin','Lothal','building',
            'The excavator’s mean wall spans and surviving height define the basin. The model leaves its dock or reservoir function open.',
            252,'North is +Y. A rectangular approximation replaces the reported trapezoid because exact corner coordinates are not used.')
    s.feature('ground','Display ground','A narrow neutral plinth frames the basin.',['RAO-1965'],'Display only','Display only','Display only',['The plinth is not the ancient shoreline.'],[0,0,0],246)
    s.box('ground',-8,0,-.5,80,241,.5,'ground',role='ground')
    s.feature('basin','Basin and embankments','Rao reports mean long-wall spans of 214.87 m, short-wall spans of 37.26 m, and an extant height of 3.30 m.', ['RAO-1965','LESHNIK-1968'],
              'Published mean wall spans; rectangular approximation','Centered; exact trapezoid omitted','Published extant height 3.30 m; original height unknown',
              ['Spans describe wall lengths; the model uses them as the wall-line envelope.','1.60 m foundation width is reported; taper to 1.30 m is simplified.','Rao interprets a dock; Leshnik and Junghans propose an irrigation tank. Geometry alone does not choose function.'],[0,0,1.5],235)
    w=37.26;l=214.87;t=1.6
    s.box('basin',0,0,-.1,w,l,.1,'floor',evidence='dimensioned')
    for x in [-w/2,w/2]:s.box('basin',x,0,0,t,l,3.3,'brick',cut=x>0,evidence='dimensioned')
    s.box('basin',0,-l/2,0,w,t,3.3,'brick',cut=True,evidence='dimensioned')
    # First-stage north inlet; we do not combine the later eastern inlet as a simultaneous opening.
    gap=12.21; wing=(w-gap)/2
    for sign in [-1,1]:s.box('basin',sign*(gap/2+wing/2),l/2,0,wing,t,3.3,'brick',evidence='dimensioned')
    s.feature('inlet','First-stage northern opening','The excavator gives an original northern inlet gap of 12.21 m; a 7.02 m eastern inlet belongs to a later phase.', ['RAO-1965'],
              'Published first-stage gap 12.21 m','North wall; exact channel geometry assumed','Channel floor assumed',
              ['The later eastern gap is omitted from this first-stage display.','No ship size or water-lock performance is reconstructed.'],[0,107,1.5],38)
    for x in [-6.9,6.9]:s.box('inlet',x,115,0,1.4,14,3.3,'brick',evidence='described')
    s.feature('wharf','West-side platform','Rao describes a mud-brick support beside the western embankment, 13–20 m wide.', ['RAO-1965'],
              'Published width range; 16.5 m display width','Along west side; extent simplified','3.3 m display height assumed',
              ['A continuous rectangular platform is schematic.'],[-28,0,1.5],230)
    s.box('wharf',-27.68,0,0,16.5,214.87,3.3,'earth',evidence='described')
    s.feature('water','Display water','A switchable water plane shows the enclosure.', ['RAO-1965'],
              'Display surface','Inside basin','Illustrative 1.65 m level',['This is not a tidal or hydraulic simulation.'],[0,0,1],230)
    s.quad('water',[[-17.8,-106,1.65],[17.8,-106,1.65],[17.8,106,1.65],[-17.8,106,1.65]],'water',role='water')
    s.dimension('Mean long wall span',214.87,'RAO-1965','Lothal: The Dock, paragraph 2',[-41,-l/2,4],[-41,l/2,4])
    s.dimension('Mean short wall span',37.26,'RAO-1965','Lothal: The Dock, paragraph 2',[-w/2,-114,4],[w/2,-114,4])
    s.dimension('Surviving wall height',3.3,'RAO-1965','Lothal: The Dock, paragraph 2')
    s.dimension('First-stage north opening',12.21,'RAO-1965','Lothal: The Dock, paragraph 3')
    s.label('FIRST-STAGE NORTH OPENING',[0,111,4]);s.label('WEST PLATFORM',[-28,0,4])
    return s


def embed(target, source, offset, prefix):
    """Reuse geometry at true metric scale; all placements are identified as approximate."""
    ox,oy,oz=offset
    for f in source.d['features']:
        if f['id'] in ['ground','water','roof']: continue
        f=json.loads(json.dumps(f));f['id']=prefix+f['id'];f['name']=source.d['name']+' · '+f['name']
        f['placement']='Approximate location in the city diagram; not georeferenced'
        f['focus']=[f['focus'][0]+ox,f['focus'][1]+oy,f['focus'][2]+oz]
        f['detail_model']=source.d['id'];target.d['features'].append(f)
    kept={x['id'] for x in target.d['features']}
    for m in source.d['meshes']:
        if prefix+m['feature'] not in kept or m['role']=='roof':continue
        m=json.loads(json.dumps(m));m['feature']=prefix+m['feature']
        m['vertices']=[[x+ox,y+oy,z+oz] for x,y,z in m['vertices']];m['base']+=oz
        target.d['meshes'].append(m)


def mohenjo(bath,phall):
    s=Scene('mohenjo-daro','Mohenjo-daro · city context','Mohenjo-daro','city',
            'Named excavation areas provide a city framework. Three monuments retain published dimensions; district extents, separations and ground levels are schematic.',
            850,'North is +Y in the diagram. District placement is approximate; this is not a registered excavation plan or a single phase.')
    s.feature('ground','Unmapped city ground','The plain is a blank context for named excavation areas.', ['UNESCO-MD','KENOYER-DISTRICTS'],
              'Display only; no city boundary inferred','Display only','Flat display plane',['Blank ground does not assert absence of remains.'],[50,20,0],850)
    s.box('ground',45,0,-3,810,720,3,'ground',role='ground')
    s.feature('western','Western mound · SD and L areas','The western mound carries the bath and other large structures. Its display rectangle is 200 × 400 m.', ['UNESCO-MD','KENOYER-DISTRICTS'],
              'Illustrative 200 × 400 m platform','West of lower town; proportions schematic','Illustrative 8 m platform',
              ['The rectangle is not a surveyed mound contour.','The model combines named monuments without selecting one building episode.'],[-180,0,5],480)
    s.box('western',-180,0,0,200,400,8,'earth')
    embed(s,bath,[-157,112,8],'md-bath-'); embed(s,phall,[-181,-110,8],'md-hall-')
    s.feature('platform','So-called granary · brick platform','The published envelope is 50 m east–west by 27 m north–south, divided into 27 blocks by passages.', ['KENOYER-PLATFORM'],
              'Published 50 × 27 m envelope; block count described','Approximate position west of Great Bath','2 m display foundation height; adjustable',
              ['Passage widths and equal block spacing are display assumptions.','The traditional granary label is retained as a name; storage function remains uncertain.'],[-225,112,10],68)
    s.box('platform',-225,112,8,50,27,1,'earth',evidence='dimensioned')
    for row in range(3):
        for col in range(9):s.box('platform',-247+col*5.5,103.4+row*8.6,9,4.8,7.6,2,'brick',variable=True,base=9,evidence='described')
    s.feature('court','College building · courtyard','The caption gives a 10 m square courtyard east of the Great Bath.', ['KENOYER-COURT'],
              'Published courtyard 10 × 10 m; surrounding complex omitted','Approximate location east of Great Bath','3 m display wall height; adjustable',
              ['Only a courtyard marker is built; no invented 78-room plan is supplied.','College is a traditional interpretation.'],[-120,112,10],25)
    s.box('court',-120,112,8,10,10,.2,'floor',evidence='dimensioned');s.enclosure('court',-120,112,8.2,11.2,11.2,.6,3,variable=True,base=8.2,evidence='dimensioned')
    for fid,name,x,y,w,l,desc in [
        ('vs','VS area',80,50,180,180,'VS is east of the western mound.'),
        ('hr','HR area',120,-170,210,180,'HR is southeast of the western mound.'),
        ('dk','DK-G area',180,240,230,140,'DK-G is in the northeastern sector.')]:
        s.feature(fid,name,desc,['KENOYER-DISTRICTS'],'District footprint unknown; diagram patch only','Published relative sector; rectangle and separations assumed','1 m display patch',
                  ['The tile identifies a district; its area is not archaeological coverage.','Internal streets and houses are left unmodelled until phase-keyed plans are registered.'],[x,y,1],max(w,l)*1.3)
        s.box(fid,x,y,0,w,l,1,'district')
        s.label(name,[x,y,5])
    s.label('SD AREA',[-210,170,12]);s.label('L AREA',[-210,-165,12]);s.label('WESTERN MOUND',[-180,15,14])
    s.dimension('Bath internal length',12,'KENOYER-BATH','Caption paragraph 1')
    s.dimension('Pillared Hall side',27.5,'KENOYER-HALL','Slide 35 caption')
    s.dimension('Brick platform east–west',50,'KENOYER-PLATFORM','Slide 40 caption')
    return s


def dholavira(res,gate):
    s=Scene('dholavira','Dholavira · city context','Dholavira','city',
            'The city envelope and named enclosures use published dimensions. Walls, districts, water structures and gates are simplified; locations remain approximate.',
            970,'North is +Y for display. Enclosures are squared to the display axes; source systems have different observed bearings. No new north measurement is made.')
    s.feature('ground','Display ground','A neutral plane encloses the model.', ['BISHT-2015-PRELIM'],
              'Display only','Display only','Display only',['The 13 m site gradient described by the report is not reconstructed.'],[0,0,0],970)
    s.box('ground',0,0,-4,875,720,4,'ground',role='ground')
    s.feature('city-wall','City envelope','Repeated prose gives 771.10 m east–west and 616.87 m north–south between identified inner corners.', ['BISHT-2015-PRELIM','UNESCO-DHO'],
              'Published corner spans; full rectangle inferred','Axis-aligned diagram; SE corner unconfirmed in cited report','4 m display wall height; adjustable',
              ['The source table prints 711.10 m; repeated prose gives 771.10 m.','South and east wall survival is incomplete; the full wall is a diagram.','Wall thickness 6 m and tower spacing in this model are illustrative.'],[0,0,2],930)
    # Inner corner spans define the envelope. Wall bodies extend outward.
    w=771.1;l=616.87;t=6
    s.enclosure('city-wall',0,0,0,w+2*t,l+2*t,t,4,'stone',variable=True,base=0,evidence='dimensioned')
    for x in [-w/2-3,w/2+3]:
        for y in [-l/2-3,l/2+3]:s.box('city-wall',x,y,0,16,16,5,'stone',variable=True,base=0)
    s.feature('castle','Castle','The report gives an external rectangle of 151 × 118 m and an inner top of 114 × 92 m.', ['BISHT-2015-PRELIM'],
              'Published external and internal spans','Approximate SW-sector location','6 m display walls above a 6 m platform; adjustable',
              ['Symmetric wall thickness interpolates external and internal rectangles.','The platform is schematic; the excavation contains several stages.'],[-130,-160,10],195)
    cx=-130;cy=-160
    s.box('castle',cx,cy,0,151,118,6,'earth')
    # Outer face 151 by118; inner114 by92, differences asymmetric in width/depth.
    for yy in [cy-52.5,cy+52.5]:s.box('castle',cx,yy,6,151,13,6,'stone',variable=True,base=6,evidence='dimensioned',cut=yy<cy)
    for xx in [cx-66.25,cx+66.25]:s.box('castle',xx,cy,6,18.5,92,6,'stone',variable=True,base=6,evidence='dimensioned',cut=xx>cx)
    s.feature('bailey','Bailey','The published internal bailey span is 120 × 120 m.', ['BISHT-2015-PRELIM'],
              'Published internal 120 × 120 m','West of castle; spacing assumed','3 m display platform and 4 m walls',
              ['The rectangular enclosure simplifies the published plan.'],[-272,-160,4],167)
    s.box('bailey',-272,-160,0,128,128,3,'earth');s.enclosure('bailey',-272,-160,3,128,128,4,4,'stone',variable=True,base=3,evidence='dimensioned')
    s.feature('middle','Middle town','The table gives 340.5 × 290.45 m for middle town plus stadium and 340.5 × 242 m excluding the stadium.', ['BISHT-2015-PRELIM'],
              'Published spans; outer rectangle simplified','North of citadel; placement approximate','2 m display terrace; 3 m walls assumed',
              ['The model uses the 340.5 × 242 m residential envelope and places the ground separately.','Internal street strips summarize the reported axial organization, not surveyed street widths.'],[-160,110,3],425)
    s.box('middle',-160,110,0,340.5,242,2,'district');s.enclosure('middle',-160,110,2,348.5,250,4,3,'stone',variable=True,base=2,evidence='dimensioned')
    s.box('middle',-160,110,2.03,335,8,.04,'route');s.box('middle',-160,110,2.03,7,236,.04,'route')
    s.feature('stadium','Ceremonial ground','The reported internal span is 283 × 47.5 m.', ['BISHT-2015-PRELIM'],
              'Published approximate 283 × 47.5 m','Between castle and middle town; placement approximate','Level display surface',
              ['The title describes a conventional archaeological feature name.','Spectator stands and event activities are not reconstructed.'],[-160,-48,1],327)
    s.box('stadium',-160,-48,0,283,47.5,1,'route',evidence='dimensioned');s.enclosure('stadium',-160,-48,1,287,51.5,2,1.2,'stone',evidence='described')
    s.feature('lower','Lower town','The table gives a 300 × 300 m built-up area; prose describes major crossing routes and subdivision.', ['BISHT-2015-PRELIM'],
              'Published built-up area approximation 300 × 300 m','Eastern half; position approximate','1 m display patch',
              ['The crossing strips are a spatial summary; no exact house plan or street width is asserted.'],[195,70,1],390)
    s.box('lower',195,70,0,300,300,1,'district',evidence='dimensioned')
    s.box('lower',195,70,1.02,300,9,.03,'route');s.box('lower',195,70,1.02,8,300,.03,'route')
    embed(s,res,[-25,-160,0],'dho-res-')
    # Use the described western passage as a metric inset at approximate gateway position.
    embed(s,gate,[-205.5,-160,6],'dho-gate-')
    s.feature('well','Castle well','The report records an internal opening of 4.00 m east–west by 4.25 m north–south, distorted by lateral thrust.', ['BISHT-2015-PRELIM'],
              'Published current opening 4.00 × 4.25 m','SW castle sector; exact centre assumed','Display rim 1 m above platform',
              ['The report’s 13.60 m evacuated shaft is not drawn to full depth in this city overview.'],[-165,-190,7],19)
    s.ring('well',-165,-190,6,2.5,2.625,.5,1,'stone',evidence='dimensioned')
    for text,p in [('CASTLE',[-130,-160,16]),('BAILEY',[-272,-160,10]),('MIDDLE TOWN',[-160,110,8]),('LOWER TOWN',[195,70,7]),('CEREMONIAL GROUND',[-160,-48,6])]:s.label(text,p)
    s.dimension('City E–W inner-corner span',771.1,'BISHT-2015-PRELIM','pp.93,107; PDF indices109,123',[-w/2,-339,7],[w/2,-339,7])
    s.dimension('City N–S inner-corner span',616.87,'BISHT-2015-PRELIM','pp.93,107; PDF indices109,123',[-416,-l/2,7],[-416,l/2,7])
    s.dimension('Castle external E–W',151,'BISHT-2015-PRELIM','p.107 table; PDF index123')
    s.dimension('Castle external N–S',118,'BISHT-2015-PRELIM','p.107 table; PDF index123')
    return s


def write_obj(scene, path):
    lines=['# Original schematic model; not a survey mesh.', '# Units: metres. Right-handed coordinates: X east, Y north, Z up.',
           '# See scenes.json and SOURCES.json for evidence and assumptions.', 'mtllib materials.mtl']
    offset=1
    for i,m in enumerate(scene['meshes']):
        if m['role'] in ['water','roof']:continue
        lines += ['o '+m['feature']+'_'+str(i),'usemtl '+m['material']]
        lines += ['v '+' '.join(f'{v:.6f}' for v in p) for p in m['vertices']]
        lines += ['f '+' '.join(str(v+offset) for v in f) for f in m['faces']]
        offset+=len(m['vertices'])
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def add_locators(scenes):
    """Attach exact source coordinates to every feature, including embedded copies."""
    dholavira={
        'city-wall':'pp.93 and107 prose; p.107 table carries the conflicting 711.10 value; PDF indices109,123',
        'castle':'p.107 table, rows2–3; PDF index123',
        'bailey':'p.107 table, row5; PDF index123',
        'middle':'p.107 table, rows6–7; layout pp.109–110; PDF indices123,125–126',
        'stadium':'p.107 table, row8; PDF index123',
        'lower':'p.107 table, row9; layout pp.109–110; PDF indices123,125–126',
        'well':'p.138, section6.6, first three paragraphs; PDF index154',
        'basin':'p.149, section6.7.2 eastern reservoir description; PDF index165',
        'probe':'pp.149–150, localized northern probing; PDF indices165–166',
        'stairs':'p.150, list of three flights; positions and tread geometry are display assumptions; PDF index166',
        'passage':'p.114, section6.2.2 west-gate description; PDF index130',
        'guard-room':'p.114, section6.2.2 west-gate description; PDF index130',
        'ground':'Display geometry only; archaeological setting described in chapter6',
        'water':'Display assumption only; water system described on pp.149–150',
    }
    bath={'basin':'Caption paragraph1: dimensions', 'waterproof':'Caption paragraph2: gypsum and bitumen',
          'stairs':'Caption paragraph1: opposing stairs and ledges', 'colonnade':'Caption paragraphs2–3: colonnade, rooms and well'}
    for s in scenes:
        s.d['sensitivity']=dict(assumed_superstructure_height_factor=[.6,1.6],
                               range_status='Display sensitivity, not an archaeological confidence interval',
                               position_error_m=None,position_error_reason='No registered survey coordinates or positional error budget supplied')
        for f in s.d['features']:
            key=f['id']
            for prefix in ['md-bath-','md-hall-','dho-res-','dho-gate-']:
                if key.startswith(prefix):key=key[len(prefix):]
            loc={}
            for source in f['sources']:
                if source=='BISHT-2015-PRELIM':loc[source]=dholavira.get(key,'Chapter6; component is a display assumption')
                elif source=='KENOYER-BATH':loc[source]=bath.get(key,'Caption; display-only component')
                elif source=='KENOYER-HALL':loc[source]='Slide35 of103, caption: square envelope and four rows of pillars'
                elif source=='KENOYER-PLATFORM':loc[source]='Slide40 of103, caption: 50 m by27 m and27 blocks'
                elif source=='KENOYER-COURT':loc[source]='Slide38 of103, caption: 10 m courtyard east of Great Bath'
                elif source=='KENOYER-DISTRICTS':loc[source]='Index captions9,11–12,23–40; relative district and monument locations'
                elif source=='RAO-1965':loc[source]='Section Lothal: The Dock; dimensions and northern inlet in paragraphs beginning This basin and The walls; west platform in paragraph beginning The wall was further supported'
                elif source=='LESHNIK-1968':loc[source]='Publisher abstract; alternative irrigation-tank interpretation'
                else:loc[source]='Brief synthesis; display context only'
            f['source_locators']=loc


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='run-v1');args=parser.parse_args()
    out=HERE/args.out
    if out.exists():raise FileExistsError(out)
    out.mkdir();(out/'exports').mkdir()
    bath=great_bath();res=reservoir();gate=gateway();phall=hall()
    scenes=[mohenjo(bath,phall),dholavira(res,gate),bath,res,gate,phall,lothal()]
    add_locators(scenes)
    sources=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    sources['witnesses'].append(dict(id='LESHNIK-1968',title='The Harappan “Port” at Lothal: Another View',
        authors='Lawrence S. Leshnik and K. H. Junghans',year=1968,
        url='https://doi.org/10.1525/aa.1968.70.5.02a00070',
        locator='American Anthropologist 70(5):911–922; publisher abstract',
        rights_status='rights-unverified',handling='Bibliographic pointer and own summary only; abstract inspected through browser 26 October 2026.',
        new_acquisition=False))
    data=dict(schema_version='1.0',units='metres',coordinates='right-handed X east, Y north, Z up',
              status='Schematic architectural models; not georeferenced or phase-pure surveys',
              materials=MATERIALS,scenes=[s.d for s in scenes],sources=sources['witnesses'])
    (out/'scenes.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    template=(HERE/'viewer.html').read_text(encoding='utf-8')
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    (out/'index.html').write_text(template.replace('/*MODEL_PAYLOAD*/',payload),encoding='utf-8')
    for s in scenes:write_obj(s.d,out/'exports'/(s.d['id']+'.obj'))
    mtl=[]
    for mat,color in MATERIALS.items():
        rgb=[int(color[i:i+2],16)/255 for i in [1,3,5]]
        mtl+=['newmtl '+mat,'Kd '+' '.join(f'{x:.5f}' for x in rgb),'Ka .15 .15 .15','d 1','']
    (out/'exports'/'materials.mtl').write_text('\n'.join(mtl),encoding='utf-8')
    manifest=[]
    for p in sorted(out.rglob('*')):
        if p.is_file():manifest.append(dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (out/'manifest.json').write_text(json.dumps(dict(files=manifest,builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         template_sha256=hashlib.sha256((HERE/'viewer.html').read_bytes()).hexdigest(),model_count=len(scenes)),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(out=out.as_posix(),models=len(scenes),features=sum(len(s.d['features']) for s in scenes),
                          meshes=sum(len(s.d['meshes']) for s in scenes),html_bytes=(out/'index.html').stat().st_size)))


if __name__=='__main__':main()
