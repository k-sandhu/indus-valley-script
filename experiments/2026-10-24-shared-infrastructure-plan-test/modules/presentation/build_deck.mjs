import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const SKILL='C:/Users/sandh/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11348/skills/presentations';
const LOCAL='D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/presentation';
const PY='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';
process.env.RUNTIME_PYTHON=PY;
process.env.RUNTIME_BIN_DIR='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override';
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const FONT=resolvePresentationFont({fontFamily:'Arial'});
const RUN=process.argv[2]||'v1';
const BUILD=path.join(LOCAL,'build',RUN);await fs.mkdir(BUILD);
const D=JSON.parse(await fs.readFile(path.join(LOCAL,'build',`evidence-${RUN}.json`),'utf8'));
const C={bg:'#F7F4ED',ink:'#182C30',muted:'#56676A',teal:'#207D80',rust:'#BA573B',line:'#D9DCD5',pale:'#E5ECE7'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
const nativeCharts=[],nativeTables=[],slideIndex=[];
const AX={fontSize:23,fill:C.muted},GRID={fill:C.line,width:1,style:'solid'};

function text(s,v,x,y,w,h,size=27,{color=C.ink,bold=false,name=null,align='left'}={}){
 const t=s.shapes.add({geometry:'textbox',name:name||v.slice(0,60),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=v;t.text.style={typeface:FONT,fontSize:size,color,bold,alignment:align,verticalAlignment:'top',lineSpacing:1.08,autoFit:'none',insets:0};return t;
}
function slide(title,notes='',dark=false){
 const s=p.slides.add();s.background.fill=dark?C.ink:C.bg;
 if(title)text(s,title,55,34,1170,85,43,{bold:true,color:dark?C.bg:C.ink,name:'slide-title'});
 s.speakerNotes.text=notes+'\n\nStudy status: exploratory with declared prior exposure. Root run-v1 SHA-256 '+D.root_run_sha256+'. Quantities are source-scoped. Conditional plan-reading bounds do not include unknown original survey or reconstruction error. Source pixels and this illustrated deck remain local-only on D.';
 slideIndex.push({slide:p.slides.items.length,title,asset_ids:[],measurement_ids:[],context_ids:[],notes});return s;
}
function foot(s,v,dark=false){text(s,v,56,660,1168,43,18,{color:dark?'#CFE2DC':C.muted,name:'source-footnote'});}
function asset(id){const a=D.assets[id];if(!a)throw Error('Missing asset '+id);return a;}
function assetNote(ids){return ids.map(id=>{const a=asset(id);return `${id}: ${a.caption}\n${a.citation}\nImage physical path: ${a.physical_path}\nImage SHA-256: ${a.sha256}\nDisplay crop: ${JSON.stringify(a.display_crop)}. Original image: ${a.source_image_path}, SHA-256 ${a.source_image_sha256}.`}).join('\n\n');}
async function image(s,id,x,y,w,h){
 const a=asset(id);const b=await fs.readFile(a.physical_path);const ratio=Math.min(w/a.pixels[0],h/a.pixels[1]);const iw=a.pixels[0]*ratio,ih=a.pixels[1]*ratio;
 s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:a.caption||id,fit:'contain',position:{left:x+(w-iw)/2,top:y+(h-ih)/2,width:iw,height:ih}});
 slideIndex.at(-1).asset_ids.push(id);
}
function measurementNote(ids){return ids.map(id=>{const m=D.measurement_by_id[id];if(!m)throw Error(id);const source=D.root.source_use_records.find(s=>s.source_ref===m.source_ref);return `${id}: ${JSON.stringify(m,null,2)}\nSource: ${JSON.stringify(source,null,2)}`}).join('\n\n');}
function contextNote(ids){return ids.map(id=>{const c=D.context_by_id[id];if(!c)throw Error(id);const src=c.source_locators.map(q=>D.root.source_use_records.find(s=>s.module==='contexts'&&s.id===q.source_id));return `${id}: ${JSON.stringify(c,null,2)}\nBibliography: ${JSON.stringify(src,null,2)}`}).join('\n\n');}
function caseNote(module,ids){return ids.map(id=>{const a=D.root.architectural_source_cases.find(s=>s.module===module&&s.source_record.id===id);if(!a)throw Error(id);const r=a.source_record;const ids=r.source_ids||[r.source_id];const sources=ids.map(id=>D.root.source_use_records.find(s=>s.module===module&&s.id===id));return `${module} ${id}: ${JSON.stringify(r,null,2)}\nBibliography: ${JSON.stringify(sources,null,2)}`}).join('\n\n');}
function table(s,values,{x=55,y=165,w=1170,h=390,widths=null,size=25}={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths||Array(values[0].length).fill(w/values[0].length),values});
 t.styleOptions={headerRow:false,bandedRows:false};t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{top:8,bottom:8,left:10,right:10}});t.borders.assign({fill:C.line,width:.6,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const a=t.getCell(r,c);a.fill=r===0?C.ink:C.bg;a.text.style={typeface:FONT,fontSize:size,color:r===0?C.bg:C.ink,bold:r===0,verticalAlignment:'middle',insets:9};}
 nativeTables.push(p.slides.items.length);return t;
}
function chart(s,type,cfg){
 const config={...cfg,series:cfg.series.map(r=>({smooth:false,fill:r.fill??r.marker?.fill??r.line?.fill??C.teal,...r,...Object.fromEntries(['values','xValues'].filter(k=>r[k]).map(k=>[k,r[k].map(v=>v===null?null:Number(v.toPrecision(12)))]))}))};
 const ch=s.charts.add(type,{hasLegend:false,chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config});applyPresentationChartFont(ch,{fontFamily:FONT});nativeCharts.push(p.slides.items.length);return ch;
}
function node(s,label,x,y,w,h,{color=C.teal,size=27}={}){const n=s.shapes.add({geometry:'rect',name:label,position:{left:x,top:y,width:w,height:h},fill:C.bg,line:{fill:color,width:2}});n.text=label;n.text.style={typeface:FONT,fontSize:size,color:C.ink,alignment:'center',verticalAlignment:'middle',insets:10};return n;}
function sequence(s,steps,y,{x=55,w=1170,h=115,size=27}={}){const gap=32,bw=(w-gap*(steps.length-1))/steps.length;steps.forEach((v,i)=>{node(s,v,x+i*(bw+gap),y,bw,h,{size});if(i<steps.length-1)s.shapes.add({geometry:'rightArrow',name:'evidence relation',position:{left:x+bw+i*(bw+gap)+4,top:y+h/2-9,width:24,height:18},fill:C.teal,line:{fill:'none',width:0}});});}
function tag(s,v,x,y,w=360){text(s,v,x,y,w,55,29,{color:C.rust,bold:true});}

// 1. A source photograph establishes the archaeological setting.
{
 const s=slide('',assetNote(['PW-P19']),true);
 await image(s,'PW-P19',770,50,440,600);
 text(s,'Shared infrastructure\nthrough rebuilding',60,155,680,180,62,{bold:true,color:C.bg});
 text(s,'Excavation plans, access changes\nand the contexts of writing',64,388,650,95,33,{color:'#CEE1DD'});
 text(s,'Exploratory source study\n24 October 2026',65,567,620,65,25,{color:C.bg});
 foot(s,'Illustrated local research edition. Dholavira source photograph, Bisht Fig.6.26.',true);
}
// 2. Regional map, with counts that describe the audit.
{
 const s=slide('The fixed source frame',assetNote(['ATLAS-01-DETAIL'])+'\nAudit counts: '+JSON.stringify(D.root.counts));
 await image(s,'ATLAS-01-DETAIL',45,125,830,510);
 text(s,'6 towns',905,165,300,65,49,{bold:true,color:C.teal});
 text(s,'in the primary audit',908,235,300,55,25);
 text(s,'18 quantities',905,328,310,60,43,{bold:true,color:C.teal});
 text(s,'17 lengths and 1 angle',908,394,300,67,25);
 text(s,'Mohenjo-daro is a\nsupplementary source control.',907,520,300,88,26);
 foot(s,'Modern land outline and inherited source points. No ancient river-access reconstruction.');
}
// 3. Native evidence-chain diagram.
{
 const s=slide('What the comparison must join',D.test_design+'\nRoot decisions: '+JSON.stringify(D.root.decisions));
 sequence(s,['Registered\nobject','Operating\ndeposit','Named wall,\nfloor or drain','Rebuilding\nepisode','Independent\nevent date'],215,{h:117,size:26});
 text(s,'Geometry',56,395,300,48,31,{bold:true,color:C.teal});
 text(s,'A line gives a local width or direction.',56,455,345,108,27);
 text(s,'Connectivity',458,395,350,48,31,{bold:true,color:C.teal});
 text(s,'A connection needs evidence that access or flow remained possible.',458,455,345,135,27);
 text(s,'Persistence',864,395,350,48,31,{bold:true,color:C.teal});
 text(s,'A comparison needs both feature classes in the same complete phase window.',864,455,345,135,27);
 foot(s,'All three are useful observations. Each answers a different archaeological question.');
}
// 4. Banawali records source retention and a withdrawn geometric target.
{
 const s=slide('Banawali combines several building periods',assetNote(['PE-P04'])+caseNote('plans-east',['PE-E012','PE-E013','PE-E014']));
 await image(s,'PE-P04',45,130,690,515);
 text(s,'The source distinguishes earlier and Harappan defences.',775,154,435,100,31,{bold:true});
 text(s,'The excavator describes retaining and widening defences while domestic layouts changed.',775,288,435,130,28);
 text(s,'The curving corner does not supply a unique straight angle. That measurement was withdrawn after overlay review.',775,454,435,155,27,{color:C.rust});
 foot(s,'Bisht 1999, p.33, Fig.1. Publication versions and excavation seasons remain separate from ancient periods.');
}
// 5. Two lanes in the same eastern IIA plan.
{
 const ids=['plans-east::PE-M001','plans-east::PE-M002'];
 const s=slide('Farmana’s eastern lanes retain local differences',assetNote(['PE-P01'])+measurementNote(ids)+caseNote('plans-east',['PE-E001','PE-E002']));
 await image(s,'PE-P01',45,129,680,515);
 table(s,[['Local section','Metres','Reading bound'],['Lane 1','1.91','1.78–2.05'],['Lane 2','1.95','1.82–2.09']],{x:755,y:164,w:470,h:203,widths:[215,95,160],size:23});
 text(s,'Period IIA drawing, with later features ordered in the report.',756,400,460,80,28,{bold:true});
 text(s,'A bathing platform occupies one exposed end. The author infers earlier disuse. A complete route closure remains unresolved.',756,501,460,125,26);
 foot(s,'Shinde, Osada and Kumar 2011, Fig.5.18, p.57. Local transects and published averages have different scopes.');
 slideIndex.at(-1).measurement_ids=ids;
}
// 6. Passage closure is distinct from closure of the adjoining lane.
{
 const ids=['plans-east::PE-M003','plans-east::PE-M004','plans-east::PE-M006'];
 const s=slide('Farmana’s 4C connection was capped',assetNote(['PE-P02'])+measurementNote(ids)+caseNote('plans-east',['PE-E003','PE-E004','PE-E005']));
 await image(s,'PE-P02',35,132,760,510);
 table(s,[['Drawn feature','m','Reading bound'],['Main Street','3.96','3.70–4.23'],['3I projection','0.59','0.25–0.95'],['4C clearance','1.79','1.55–2.02']],{x:820,y:157,w:405,h:265,widths:[175,80,150],size:22});
 text(s,'The northern cap closes the compound passage’s link with central Lane 1.',823,449,390,92,28,{bold:true});
 text(s,'Lane 1 itself remains a separate connection.',823,565,390,65,27,{color:C.rust});
 foot(s,'Period IIB, Fig.5.70, p.99. Individual additions and the cap lack independent repair dates.');
 slideIndex.at(-1).measurement_ids=ids;
}
// 7. Retained orientation with infill, and a newly located floor lead.
{
 const s=slide('Kanmer’s alignment coexists with infill',assetNote(['PE-P03'])+caseNote('plans-east',['PE-E008','PE-E009','PE-E010','PE-E011'])+'\nPost-freeze source lead, separate from run-v1 assessments: '+JSON.stringify(D.postjoin_lead));
 await image(s,'PE-P03',45,137,660,500);
 text(s,'Earlier open space received rooms in successive residential stages.',755,156,455,115,31,{bold:true});
 text(s,'The report also describes retained alignment with the fort. This overview does not separate IIa from IIb.',755,295,455,140,28);
 text(s,'A later source check locates a terracotta sealing on a Z28 SW floor. Its identity and dated repair join remain open.',755,474,455,138,26,{color:C.rust});
 foot(s,'Kharakwal and colleagues 2011, Fig.5; OP10 pp.85–86. The floor lead is a labelled post-freeze addition.');
}
// 8. Register on controls independent of the tested feature.
{
 const s=slide('Harappa’s older route lies within the later corridor',assetNote(['PW-V01'])+caseNote('plans-west',['PW-E01'])+'\nGrid fits: '+JSON.stringify(D.root.grid_registration));
 await image(s,'PW-V01',40,134,830,505);
 text(s,'Rust traces transfer the Period 2 cart tracks using the excavation grid.',907,164,300,130,29,{bold:true});
 text(s,'Six controls and two held-out crosses per drawing support the location transfer.',907,334,300,125,26);
 text(s,'The early window has no comparable internal-wall inventory.',907,504,300,100,28,{color:C.rust});
 foot(s,'Kenoyer 1991, Figs.4.12 and 4.16. The upper plan combines exposed street levels. No survival fraction.');
}
// 9. The Mound ET gateway is separate from the measured Area C gateway.
{
 const s=slide('Harappa rebuilt drainage while gate access changed',assetNote(['PW-V02'])+caseNote('plans-west',['PW-E05']));
 await image(s,'PW-V02',35,139,830,501);
 text(s,'1  Earlier western drains',905,157,305,72,28,{bold:true,color:C.rust});
 text(s,'The last clogged with silty refuse.',905,240,305,70,26);
 text(s,'2  Later central culvert',905,337,305,70,28,{bold:true,color:C.rust});
 text(s,'It partly blocked the older gateway. An east-west street crossed above it.',905,422,305,140,27);
 foot(s,'Meadow and Kenoyer 1997, Fig.3, pp.143–146. Relative building sequence, without an independent late repair date.');
}
// 10. A dated wall does not resolve a conflicting object context.
{
 const ids=['HAR-TR22-CAPTION-CONFLICT'];
 const s=slide('Wall 15 has dates and a disputed tablet context',assetNote(['ATLAS-10-DETAIL'])+contextNote(ids)+caseNote('plans-west',['PW-E04']));
 await image(s,'ATLAS-10-DETAIL',45,125,750,520);
 text(s,'Hearths beneath the wall give an earlier bound for enclosure.',830,160,380,115,30,{bold:true});
 text(s,'The tablet prose says street deposits inside the wall.',830,325,380,105,28);
 text(s,'The figure caption assigns them to Trench 7/8, wash. The field records must decide that conflict.',830,481,380,140,28,{color:C.rust});
 foot(s,'The reported after-ca.2470 BC inference concerns initial enclosure. It does not date later tablet use or Drain 51.');
 slideIndex.at(-1).context_ids=ids;
}
// 11. Production is positive evidence.
{
 const ids=['HAR-TR54-MANUFACTURE'];
 const s=slide('Harappa’s workshop locates tablet manufacture',assetNote(['HAR-WORKSHOP-PLAN'])+contextNote(ids));
 await image(s,'HAR-WORKSHOP-PLAN',45,127,740,515);
 text(s,'Workshop 601 and a bounded courtyard',820,160,390,100,32,{bold:true});
 text(s,'Broken and unfinished tablets, blanks, sawn steatite and faience waste support manufacture.',820,301,390,135,28);
 text(s,'The illustrated set contains 15 units. Their individual use points and a dated repair are unresolved.',820,482,390,132,26,{color:C.rust});
 foot(s,'Kenoyer 2005, context pp.2–4, Fig.2. Production debris in fill has a different history from operating documents.');
 slideIndex.at(-1).context_ids=ids;
}
// 12. Concentration can result from discard.
{
 const ids=['HAR-W296-22'];
 const s=slide('The Wall 296 clump is a secondary deposit',assetNote(['HAR-SECONDARY-CLUMP'])+contextNote(ids));
 await image(s,'HAR-SECONDARY-CLUMP',45,128,740,513);
 table(s,[['Reported grouping','Tablets'],['Reconstructed clump','16'],['Nearby','2'],['Scattered','4'],['Total source cohort','22']],{x:825,y:159,w:390,h:291,widths:[285,105],size:24});
 text(s,'The source places the dump after wall construction. Its map locates discard, with the original use setting still open.',825,487,390,133,28,{bold:true});
 foot(s,'Meadow and Kenoyer 2000, Fig.2 and p.13. Approximate finds and one source cohort.');
 slideIndex.at(-1).context_ids=ids;
}
// 13. A measurable interior can have blocked ends.
{
 const ids=['plans-west::PW-M03'];
 const s=slide('Dholavira’s East Gate has later blockings',assetNote(['PW-V04'])+measurementNote(ids)+caseNote('plans-west',['PW-E09']));
 await image(s,'PW-V04',40,128,745,513);
 text(s,'2.52 m',830,158,380,80,57,{bold:true,color:C.rust});
 text(s,'Interior section\nReading bound 2.27–2.79 m',832,245,380,96,27);
 text(s,'Both ends carry a later-blocking label. The plan does not assign each blocking to an exact stage.',832,395,380,143,29,{bold:true});
 text(s,'Display rotated to north-up.',832,577,380,45,25,{color:C.muted});
 foot(s,'Bisht, p.116, Fig.6.9. Local clearance and access through the gate are separate observations.');
 slideIndex.at(-1).measurement_ids=ids;
}
// 14. Public architecture is a bounded anchor, original mounting remains reconstructed.
{
 const ids=['DHO-GATE10'];
 const s=slide('Dholavira’s gate anchors a fallen sign panel',assetNote(['ATLAS-18-DETAIL'])+contextNote(ids)+caseNote('plans-west',['PW-E10']));
 await image(s,'ATLAS-18-DETAIL',45,125,755,520);
 text(s,'Ten-sign inlays fell into the western chamber.',836,158,374,115,31,{bold:true});
 text(s,'The source reconstructs an original wooden mounting above the gate.',836,333,374,105,28);
 text(s,'Its installation date remains unresolved.',836,515,374,90,30,{color:C.rust});
 foot(s,'Bisht pp.228–230. Gate use and later narrowing do not independently date the panel’s emplacement.');
 slideIndex.at(-1).context_ids=ids;
}
// 15. Two actual drawings with different temporal resolution.
{
 const s=slide('Dholavira’s defence and water system',assetNote(['PW-P15','PW-V08'])+caseNote('plans-west',['PW-E08','PW-E12'])+measurementNote(['plans-west::PW-M05']));
 await image(s,'PW-P15',40,158,760,365);
 await image(s,'PW-V08',838,130,380,510);
 text(s,'Stage I base 11 m. Additions: 2.8 m in II and 4.5 m in III.',52,546,735,73,29,{bold:true});
 text(s,'The well-and-tank plan combines channels and unassigned repairs.',50,616,740,37,24,{color:C.rust});
 foot(s,'Bisht Fig.5.1 is schematic. Fig.6.32 points north down. Published wall dimensions and a composite water plan.');
}
// 16. Recovered text figure retains the unavailable comparison.
{
 const ids=['plans-west::PW-M06','plans-west::PW-M07'];
 const s=slide('Lothal’s Phase IV openings can be measured',assetNote(['PW-V09'])+measurementNote(ids)+caseNote('plans-west',['PW-E13','PW-E14']));
 await image(s,'PW-V09',45,129,730,514);
 table(s,[['Opening','m','Reading bound'],['Passage','1.12','0.99–1.26'],['House 172 entrance','2.21','2.06–2.36']],{x:812,y:160,w:405,h:230,widths:[190,75,140],size:22});
 text(s,'The earlier matched block plan and whole street plate are absent from the held volume.',814,433,390,122,29,{bold:true});
 text(s,'Missing plates do not erase this usable figure.',814,580,390,60,25,{color:C.rust});
 foot(s,'Rao 1979, p.109, Fig.17. No phase-pair narrowing fraction is inferred.');
 slideIndex.at(-1).measurement_ids=ids;
}
// 17. Contacts and deposition have separate functions.
{
 const ids=['LOT-WAREHOUSE-COHORT','LOT-L164','LOT-L206'];
 const s=slide('Lothal joins fastening evidence to a later deposit',assetNote(['LOT-DEPOSIT-PLAN','LOT-CLOSURE-RECONSTRUCTION'])+contextNote(ids));
 await image(s,'LOT-DEPOSIT-PLAN',40,136,750,500);
 await image(s,'LOT-CLOSURE-RECONSTRUCTION',835,135,380,300);
 text(s,'Source closure models interpret reverse contacts.',838,449,373,72,26,{bold:true});
 text(s,'Application point, handover and final discard require separate evidence.',838,542,373,88,27,{color:C.rust});
 foot(s,'Frenez and Tosi 2005, Figs.2–3. Cord and container contacts do not independently identify a custody change.');
 slideIndex.at(-1).context_ids=ids;
}
// 18. Native chart of an independently recounted publication table.
{
 const vals=D.root.Lothal_independent_recount.counts;
 const s=slide('Lothal’s table and prose have different counts',contextNote(['LOT-WAREHOUSE-COHORT','LOT-W1-INFERRED'])+'\nIndependent recount: '+JSON.stringify(D.root.Lothal_independent_recount)+'\nDenominators: '+JSON.stringify(D.root.Lothal_denominators));
 chart(s,'bar',{position:{left:48,top:146,width:760,height:440},categories:['W','W1','W2','O','?'],series:[{name:'Table 1 rows',values:['W','W1','W2','O','?'].map(k=>vals[k]),fill:C.teal}],barOptions:{direction:'column',grouping:'clustered',gapWidth:80},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0',textStyle:{fontSize:28,fill:C.ink,bold:true}},xAxis:{textStyle:AX,majorGridlines:null},yAxis:{min:0,max:40,majorUnit:10,textStyle:AX,majorGridlines:GRID,title:{text:'Publication rows',textStyle:AX}}});
 text(s,'93 table rows',852,161,360,70,43,{bold:true,color:C.teal});
 text(s,'The prose gives O = 11 and ? = 17. Its categories sum to 92.',853,259,360,115,28);
 text(s,'W1 follows stamp similarity. W2 identifies a broad trench. They cannot become precise warehouse findspots in the same stamp test.',853,417,360,190,27,{color:C.rust});
 foot(s,'Frenez and Tosi 2005, Table 1 pp.93–94. Two readers reproduced W 35, W1 18, W2 11, O 10, ? 19.');
}
// 19. Source field coverage, not ancient context frequency.
{
 const g=D.root.Dholavira_coverage.gate_counts;
 const cats=['Accession','Grid','Stratum','Depth','Area','Unqualified stage','Literal room'];
 const values=[g.accession_string,g.grid_label,g.stratum_label,g.depth_label,g.area_label,g.unqualified_stage,g.explicit_room_label];
 const s=slide('Dholavira’s table gives three literal room leads',contextNote(['DHO-225TABLE','DHO-ROOM-83','DHO-ROOM-140','DHO-ROOM-211'])+'\nSource-field gate counts: '+JSON.stringify(D.root.Dholavira_coverage));
 chart(s,'bar',{position:{left:48,top:153,width:800,height:434},categories:cats,series:[{name:'Rows with usable field',values,fill:C.teal}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:65},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0',textStyle:{fontSize:25,fill:C.ink,bold:true}},xAxis:{textStyle:AX,majorGridlines:null},yAxis:{min:0,max:250,majorUnit:50,textStyle:AX,majorGridlines:GRID}});
 text(s,'225 rows',887,165,330,75,49,{bold:true,color:C.teal});
 text(s,'A room label is a lead to recover its floor and construction history.',888,293,328,125,29,{bold:true});
 text(s,'No row establishes the complete original-use-to-repair chain in this table audit.',888,472,328,135,27,{color:C.rust});
 foot(s,'Bisht pp.247–259. Counts describe recorded fields and join criteria, not ancient absence of primary contexts.');
}
// 20. Intrusive dates as positive evidence of formation.
{
 const s=slide('Direct dates can overturn a cultural assignment',assetNote(['KAN-RICE-COUNTEREXAMPLE'])+contextNote(['FAR-ST3N-DATE','KAN-RICE-INTRUSION'])+'\nSource-specific dating entries retained separately: '+JSON.stringify(D.root.counts));
 await image(s,'KAN-RICE-COUNTEREXAMPLE',45,128,655,505);
 table(s,[['Reported association','Direct date as reported'],['Farmana Structure 3N\nPLD-12422','AD 616–666\n95.4% coverage'],['Kanmer Mature/Late layers\nPLD-16351/16353 rice','Fourth–fifth centuries AD\nRaw BP absent from paragraph']],{x:735,y:161,w:482,h:325,widths:[240,242],size:22});
 text(s,'A nearby structure or phase label cannot supply the age of a seal’s original use.',739,511,470,115,29,{bold:true});
 foot(s,'The source discusses intrusion, reworking or percolation. Calendar conventions remain source-specific.');
}
// 21. Original source scales and alternative bank readings.
{
 const s=slide('Mackay’s First Street plans permit local readings',assetNote(['ATLAS-22','ATLAS-23','MD-SCALE-45','MD-SCALE-51'])+measurementNote(['mohenjo-control::MD-WIDTH-45','mohenjo-control::MD-WIDTH-51']));
 await image(s,'ATLAS-22',40,130,585,365);
 await image(s,'ATLAS-23',655,130,585,365);
 await image(s,'MD-SCALE-45',85,525,495,75);
 await image(s,'MD-SCALE-51',700,525,495,75);
 text(s,'The source bars run from 0 to 50 feet. Plate XIX retains two plausible western edges.',55,612,1160,41,27,{bold:true});
 foot(s,'Mackay Volume II, plates XVI and XIX. Targeted independent visual audit after values were known.');
}
// 22. Independent chord positions retain source phases without a trend claim.
{
 const ms=D.root.measurements.filter(r=>r.module==='mohenjo-control');
 const notes=measurementNote(ms.map(m=>m.id))+'\nThe four readings are beside different local frontages, not repeated registered ground transects. The fifth frozen reading lacks a continuous western bank. The range is a conditional source-reading bound, not a confidence interval. No street-widening trend is estimated.';
 const s=slide('Four street chords and one missing bank',notes);
 const series=[];ms.forEach((m,i)=>{const r=m.source_record;const bound=[r.reading_lower_m,r.reading_upper_m];series.push({name:m.phase+' reading range',xValues:bound,values:[4-i,4-i],line:{fill:C.teal,width:5},marker:{symbol:'none'}});series.push({name:m.phase+' point reading',xValues:[m.value],values:[4-i],line:{fill:'none',width:0},marker:{symbol:'circle',size:12,fill:C.teal}});});
 const alternative=ms.at(-1).source_record.alternative_edge;
 series.push({name:'Plate XIX alternative edge range',xValues:[alternative.reading_lower_m,alternative.reading_upper_m],values:[.85,.85],line:{fill:C.rust,width:4},marker:{symbol:'none'}});
 series.push({name:'Plate XIX alternative edge',xValues:[alternative.estimate_m],values:[.85],line:{fill:'none',width:0},marker:{symbol:'square',size:11,fill:C.rust}});
 chart(s,'scatter',{position:{left:300,top:151,width:920,height:420},scatterOptions:{style:'lineWithMarkers'},series,xAxis:{min:4,max:14,majorUnit:2,title:{text:'Local drawn clearance, metres',textStyle:AX},textStyle:AX,majorGridlines:GRID},yAxis:{min:.5,max:4.5,majorUnit:1,visible:false,majorGridlines:null}});
 ['Intermediate III','Intermediate II','Intermediate I','Late III'].forEach((v,i)=>text(s,v,55,184+i*83,244,54,28,{bold:true}));
 text(s,'Plate XIX retains the rust alternative edge. The fifth frozen section has no identifiable western bank.',55,586,1160,60,27,{color:C.rust});
 foot(s,'Categorical source phases and different local frontages. The graph makes no temporal widening estimate.');
 slideIndex.at(-1).measurement_ids=ms.map(m=>m.id);
}
// 23. The entry requirements remain visible beside the actual denominator.
{
 const s=slide('No candidate meets the full comparison requirements',JSON.stringify(D.root.decisions,null,2)+'\n'+D.decision);
 table(s,[['Prediction','Required comparison','Qualified units'],['C-0017 P1','Complete phase windows for routes and partitions','0 episodes'],['C-0017 P2','Joined repairs and different local components','0 qualified sets'],['C-0017 P3','Repair dates against engineering and distance','0 comparisons'],['C-0018','Operational custody contexts and matched recovery','0 matched pairs'],['C-0019','Work evidence beyond ordinary goods allocation','0 matched pairs']],{x:55,y:151,w:1170,h:390,widths:[190,755,225],size:23});
 text(s,'The audit supplies positive cases and unestimated effects. It supplies no institutional confirmation.',57,579,1150,66,30,{bold:true});
 foot(s,'29 source-defined architectural cases, 32 context assessments and 78 date entries describe overlapping evidence.');
}
// 24. Rival mechanisms and subjective working judgments.
{
 const s=slide('Several causes can preserve a shared system',D.test_design+'\nExploratory subjective credences remain C-0017 .55, C-0018 .35, C-0019 .10; unchanged by this source reuse. All are untested judgments.');
 table(s,[['Proposed cause','New observation that could distinguish it'],['Common rules for connected services','Preferential route continuity with locally different components and usable joins'],['Settlement-wide supervision','Repair timing and component choices coordinate beyond connected groups'],['Engineering constraints','Slope, flow, foundations and flood exposure explain retention'],['Household decisions in inherited streets','Local closures and additions follow inherited constraints without additional repair coordination']],{x:55,y:162,w:1170,h:356,widths:[390,780],size:26});
 text(s,'Architectural persistence alone leaves the governing arrangement open.',57,551,1150,53,32,{bold:true});
 foot(s,'C-0017 0.55, C-0018 0.35, C-0019 0.10. Existing subjective exploratory judgments, with no new update.');
}
// 25. A native prospective design, with minima separated from power.
{
 const s=slide('The deciding comparison needs new complete evidence',D.test_design+'\n'+D.decision);
 sequence(s,['New complete\nphase windows','Independent\narchitecture and\ncontext coding','Population and\npower audit','One frozen\nconfirmation read'],180,{h:124,size:27});
 table(s,[['Target','Inherited entry minimum','Deciding contrast'],['Architecture','12 independent episodes\nin 4 towns, plus adequate power','Route retention at least 0.25\nabove matched partitions'],['Documentary settings','20 matched pairs\nin 4 towns, plus adequate power','Odds ratio at least 2 under\nprimary-use and recovery controls']],{x:55,y:365,w:1170,h:228,widths:[220,440,510],size:25});
 foot(s,'Previously exposed plans stay discovery material. Work obligations require a physical distinction from goods allocation.');
}
// 26. Strongest reading with an explicit failure condition.
{
 const s=slide('The strongest reading and the deciding test',D.decision,true);
 text(s,'People retained or renewed connections\nwhile local access changed.',60,163,1150,146,52,{bold:true,color:C.bg});
 text(s,'A complete, dated comparison must show whether shared routes\noutlasted internal divisions under matched preservation.',62,365,1140,105,33,{color:'#CEE1DD'});
 text(s,'If that preference disappears, or manufacture and secondary disposal\nexplain the documentary pattern, the corresponding claim fails.',62,538,1140,93,30,{color:C.bg});
 foot(s,'Selective continuity is the supported reading. Its institutional cause remains a testable proposal.',true);
}

if(p.slides.items.length!==26)throw Error('Slide count differs');
await fs.writeFile(path.join(BUILD,'deck.json'),JSON.stringify(p.toProto()));
await fs.writeFile(path.join(BUILD,'slide-index.json'),JSON.stringify(slideIndex,null,2));
await fs.writeFile(path.join(BUILD,'build_deck.mjs'),await fs.readFile(new URL(import.meta.url)));
const candidate=path.join(BUILD,'candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);console.log('Draft exported');
const final=path.join(LOCAL,'output',`shared-infrastructure-plan-test-2026-10-24-${RUN}.pptx`);
const result=await finalizePresentation({workspaceDir:LOCAL,candidatePath:candidate,finalPath:final,pythonExecutable:PY,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...nativeTables.flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:26,requiredNativeTableOwnerSlides:nativeTables,requiredNativeChartOwnerSlides:nativeCharts,materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation.json')});
console.log(JSON.stringify({final,font:FONT,slides:26,nativeChartSlides:nativeCharts,nativeTableSlides:nativeTables,result}));
