import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
process.on('uncaughtException',err=>{console.error(err.message);console.error(String(err.stack).split('\n').filter(l=>l.includes('build_deck')).join('\n'));process.exit(1);});

const SKILL = 'C:/Users/sandh/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11348/skills/presentations';
const LOCAL = 'D:/projects/indus_valley_script/data/raw/2026-10-24-town-axis-presentation';
const RUNTIME_PYTHON = 'C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_PYTHON=RUNTIME_PYTHON;
process.env.RUNTIME_NODE='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';
process.env.RUNTIME_BIN_DIR='C:/Users/sandh/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override';
const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const FONT = resolvePresentationFont();
const RUN = process.argv[2] || 'v1';
const build = path.join(LOCAL, 'build', RUN);
await fs.mkdir(build); // A new run preserves every earlier draft.
const data = JSON.parse(await fs.readFile(path.join(LOCAL, 'build/evidence.json'), 'utf8'));
const p = Presentation.create({slideSize: {width:1280, height:720}});
const C = {bg:'#F7F4ED', ink:'#182C30', muted:'#56676A', teal:'#207D80', rust:'#BA573B', line:'#D9DCD5', light:'#FFFFFF'};
const P = 'experiments/2026-10-24-q1032-town-axis-register/';
const W = 'Wanzke, H. (1987), Axis Systems and Orientation at Mohenjo-Daro, in M. Jansen and G. Urban (eds), Interim Reports, Vol. 2, pp. 33–44. Held PDF: research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf. Physical: D:/projects/indus_valley_script/research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf. SHA-256 e488536488de84426de6391764a8364275aa557613bc0efb82ff385e561e8c6f. Printed pp. 33–44 = zero-based PDF indices 35–46.';
const J = 'Joshi (1990), Excavation at Surkotada 1971–72 and Exploration in Kutch, MASI 87, Fig. 8, unpaginated fold-out, zero-based PDF index 61. Logical: data/raw/2026-10-21-town-axes/plan-B/downloads/joshi1990_surkotada_masi87.pdf. Physical: D:/projects/indus_valley_script/data/raw/2026-10-21-town-axes/plan-B/downloads/joshi1990_surkotada_masi87.pdf. SHA-256 46e405f16464ce6d1f82da48f5515b61e09eec63bc2a28cdc348fe32a3a06245. Plan arrow reads N, north reference unspecified.';
const RC = 'Agrawal, D. P. and Kusumgar, S. (1973), Tata Institute Radiocarbon Date List X, Radiocarbon 15(3), 574–585. DOI https://doi.org/10.1017/S0033822200009024. Logical: data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-X.pdf. Physical: D:/projects/indus_valley_script/data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-X.pdf. SHA-256 68534b5cb7d59644f2737c69e3071541d7f760c22e24c1f2839a064a65f181b2. Printed pp. 574, 579–580 = zero-based PDF indices 0, 5–6. Individual BP ages use a 5568-year half-life. BC figures are arithmetic, uncalibrated. IC association comes from the inherited excavation-phase join, rather than the date list alone.';
const DEM = 'Copernicus DEM GLO-30 and GLO-90. https://registry.opendata.aws/copernicus-dem/ and https://copernicus-dem-30m.s3.amazonaws.com/readme.html. Attribution: produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. Dataset-specific licence retained. Full ray profiles and acquisition records: '+P+'horizon-repair-v1/horizons.json. 46 tiles, 349,539,705 bytes, local-only on D:/projects/indus_valley_script/data/raw/2026-10-24-q1032-town-axis-register/dem/.';
const deg = n => (n<0?'−':n>0?'+':'')+Math.abs(n).toFixed(2)+'°';

function text(s, value, x,y,w,h, size=28, opts={}) {
  const t=s.shapes.add({geometry:'textbox', name:opts.name || value.slice(0,48), position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0}});
  t.text=value;
  t.text.style={typeface:FONT,fontSize:size,color:opts.color||C.ink,bold:opts.bold||false,lineSpacing:1.08,verticalAlignment:'top',autoFit:'none',insets:0,alignment:opts.align||'left'};
  return t;
}
function slide(title, notes='', dark=false) {
  const s=p.slides.add(); s.background.fill=dark?C.ink:C.bg;
  if(title) text(s,title,64,44,1150,75,44,{bold:true,color:dark?C.bg:C.ink,name:'slide-title'});
  s.speakerNotes.text=notes;
  return s;
}
function foot(s,v){text(s,v,64,660,1150,43,18,{color:C.muted,name:'source-footnote'});}
function table(s,values,x,y,width,height,widths,size=24){
  const tb=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height,columnWidths:widths,values});
  tb.styleOptions={headerRow:false,bandedRows:false};
  tb.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{top:5,bottom:5,left:9,right:9}});
  tb.borders.assign({fill:C.line,width:.7,style:'solid'});
  for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=tb.getCell(r,c);cell.fill=r===0?C.ink:C.bg;
    cell.text.style={typeface:FONT,fontSize:size,color:r===0?C.bg:C.ink,bold:r===0,verticalAlignment:'middle',insets:10};
  }
  return tb;
}
function chart(s,type,config){
  // Excel's chart workbook accepts 15 significant digits. Twelve retain more
  // precision than these observations support, while avoiding binary tails.
  config={...config,series:config.series.map(r=>({...r,...Object.fromEntries(['values','xValues'].filter(k=>r[k]).map(k=>[k,r[k].map(v=>v===null?null:Number(v.toPrecision(12)))]))}))};
  const ch=s.charts.add(type,{hasLegend:false,chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config});
  applyPresentationChartFont(ch,{fontFamily:FONT});
  config.series.forEach((r,i)=>{if(r.dataLabels?.textStyle)ch.series.getItemAt(i).dataLabels.textStyle.typeface=FONT;});
  return ch;
}
const axisText={fontSize:24,fill:C.muted};
const grid={fill:C.line,width:1,style:'solid'};
function intervalChart(s,rows,{x=450,y=230,w=750,h=330,min=-4,max=2,unit=1,precision=1,label='Deviation from the nearest cardinal axis (°)',color=C.teal}={}){
  const ss=[];
  rows.forEach((r,i)=>{
    const yy=rows.length-i;
    const col=r.color||color;
    ss.push({name:r.label+' interval',xValues:[r.value-r.sigma,r.value+r.sigma],values:[yy,yy],line:{fill:col,width:4},marker:{symbol:'none'},dataLabels:{showValue:false}});
    ss.push({name:r.label,xValues:[r.value],values:[yy],line:{fill:col,width:1},stroke:{fill:col,width:1},marker:{symbol:'circle',size:12,fill:col},dataLabels:{showValue:false,showSeriesName:true,position:'top',textStyle:{fontSize:24,fill:C.ink}}});
  });
  return chart(s,'scatter',{position:{left:x,top:y,width:w,height:h},scatterOptions:{style:'lineWithMarkers'},series:ss,xAxis:{min,max,majorUnit:unit,title:{text:label,textStyle:{fontSize:22,fill:C.muted}},textStyle:axisText,numberFormatCode:`+0.${'0'.repeat(precision)}"°";-0.${'0'.repeat(precision)}"°";0"°"`,majorGridlines:grid,line:{fill:C.muted,width:1}},yAxis:{min:0,max:rows.length+1,visible:false,majorGridlines:null},dataLabels:{showValue:false}});
}

// 1. A spare cover introduces the observational conclusion.
{
 const s=slide('',P+'REPORT.md and TABLE.md. This deck presents source-reviewed exploratory observations, not a new confirmation test. The current register endpoint is run-v5. No new inscribed object, radiocarbon determination or scientific orientation statistic enters this presentation.',true);
 text(s,'A town has\nseveral axes',76,144,1090,236,82,{bold:true,color:C.bg});
 text(s,'Town orientations in the Indus world',80,437,1100,66,36,{color:'#CEE1DD'});
 text(s,'Q-1032\n24 October 2026',80,570,1100,80,26,{color:C.bg});
}
// 2. Coverage uses a shared town denominator, rather than incomparable record counts.
{
 const s=slide('Coverage across 34 candidate towns',P+'run-v5/coverage.json. All eleven required Q-1032 towns are present. Categories overlap and show availability, not completeness or independent validation. The frame is not an exhaustive list of every measurable Harappan settlement. New in this continuation: 35 published orientation rows, two exploratory image lines, two corrected-location horizons.');
 text(s,'All 11 required towns\nenter the register.',65,165,350,112,36,{bold:true});
 text(s,'The measurements still\ncover different parts\nand building episodes.',65,327,350,153,28);
 chart(s,'bar',{position:{left:443,top:164,width:760,height:410},categories:['Direct imagery','Plans','Usable modern horizons'],series:[{name:'Towns with evidence',values:[6,24,20],fill:C.teal}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:80},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:30,fill:C.ink,bold:true}},xAxis:{visible:true,textStyle:axisText,majorGridlines:null},yAxis:{min:0,max:34,majorUnit:10,textStyle:axisText,line:{fill:'none',width:0},majorGridlines:grid}});
 text(s,'New: 35 published rows, 2 image lines and 2 corrected-location horizons.',65,588,1145,45,25,{color:C.rust});
 foot(s,'Availability counts overlap. Source: run-v5/coverage.json.');
}
// 3. Required-town evidence table preserves the uneven coverage.
{
 const s=slide('The eleven required towns',P+'run-v5/town-axis-table.json, /towns. Image and plan entries count line records, including repeated readings. Phase entries count dated-part assertions, including competing source claims. Present means a usable horizon at the retained modern location. It does not imply a palaeohorizon or a complete error budget. Rakhigarhi has dating assertions but no measured lines in the retained register.');
 const vals=[['Town','Image lines','Plan lines','Modern horizon','Part assertions'],...data.required_towns.map(t=>[t.town,String(t.image_lines),String(t.plan_lines),t.horizon,String(t.phase_assertions)])];
 table(s,vals,64,141,1152,468,[300,180,180,266,226],23);
 foot(s,'Line records include repeat readings. Part assertions retain competing phase claims.');
}
// 4. North conventions are an evidence table, rather than an illustrative compass.
{
 const s=slide('North and uncertainty remain attached',P+'REPORT.md, run-v5/measurements.jsonl and measurement-field-gaps.csv. Bearing is clockwise from north modulo 180°. Deviation folds to the nearest cardinal axis in [−45°, +45°], positive clockwise. Original north classifications remain distinct. '+W+' '+J+' Plan-registration REPORT.md retains its failed frozen validation.');
 table(s,[['Evidence','North reference','Precision or status'],['Wanzke’s Mohenjo-daro survey','True north','Selected axis errors unreported'],['Joshi’s Surkotada Fig. 8','Arrow reads “N”','True or magnetic unspecified'],['Registered plan bearings','Transformed to true north','Exploratory, validation failed'],['Imagery line picks','Georeferenced true north','Reading and provider errors differ']],64,165,1152,328,[390,320,442],25);
 text(s,'Deviation is positive clockwise and negative anticlockwise.\nA repeated reading of one image measures reading consistency.',65,544,1135,87,28);
 foot(s,'The register keeps source labels, transformations and uncertainty reasons for each observation.');
}
// 5. Three exact rows show the source-backed architectural distinction.
{
 const s=slide('Mohenjo-daro preserves different axes',W+' Values from printed p. 33, zero-based PDF index 35. Published gon values: Moneer N-S 5 −0.4, Moneer N-S 6 −0.1, HR First Street +8.3. Multiply by 0.9 degrees per gon. The astronomical survey reference establishes true north. These three rows have no reported one-sigma error. This is an architectural comparison, not a chronology or astronomical targeting test. Entered records: '+P+'run-v5/published-wanzke.json.');
 text(s,'Near-cardinal\nMoneer axes coexist\nwith a turned street.',65,170,370,177,36,{bold:true});
 intervalChart(s,data.mohenjo_daro.map(r=>({label:r.part+' '+deg(r.deg),value:r.deg,sigma:0})),{min:-2,max:10,unit:2,x:446,y:173,w:754,h:380});
 text(s,'One gon = 0.9°. Wanzke reports no one-sigma errors for these rows.',65,585,1145,58,25,{color:C.rust});
 foot(s,'Wanzke (1987), p. 33. True-north survey axes.');
}
// 6. The interval lines are chart series. They do not imply a complete error model.
{
 const s=slide('Lothal dock: imagery differs by 2.07°',P+'REPORT.md and experiments/2026-10-21-town-orientations-verification/comparison-v3/comparison.json. Esri −1.88 ±0.30°, Sentinel-2 +0.19 ±0.30°, reported one-sigma errors. The nominal difference is about 4.9 combined reported standard errors. The empirical Sentinel-2 calibration gives larger errors for these short lines, so that nominal discrepancy is not a valid independent significance claim. The register preserves both products without pooling them. Intervals in this chart show only the reported one-sigma ranges.');
 text(s,'2.07°',66,171,330,96,84,{bold:true,color:C.rust});
 text(s,'Both products measure\nthe dock, yet their\nbearings disagree.',67,300,340,146,30);
 intervalChart(s,data.lothal.map((r,i)=>({label:r.source+' '+deg(r.deviation_deg),value:r.deviation_deg,sigma:r.reported_sigma_deg,color:i?C.rust:C.teal})),{min:-3,max:1,unit:1,x:446,y:190,w:757,h:369});
 text(s,'Bars show reported ±0.30° errors. Short Sentinel-2 lines have larger empirical errors.',66,591,1137,62,26,{color:C.rust});
 foot(s,'Independent verification, comparison-v3. A dock survey can decide the discrepancy.');
}
// 7. The two new lines share a raster and an observer.
{
 const s=slide('Surkotada: two short wall segments',P+'new-observations.json /structures/0 and /structures/1; geodesic-check.json; run-v5/measurements.jsonl IDs new-surkotada:SK-W and new-surkotada:SK-S. '+J+' Esri World Imagery Wayback release 8432, source Esri, Vantor, Earthstar Geographics and the GIS User Community. Local-only raster: '+data.surkotada_picks.sources[0].file+'. SHA-256 '+data.surkotada_picks.sources[0].sha256+'. The image exposure date is unknown. Release 8432 identifies an archive product, not the exposure date. Corrected site 23.6113 N, 70.9174 E, about 8 km east of the old point. Picks are unblinded and exploratory. WGS84 inverse geodesic bearings use three-pixel endpoint uncertainty. Total error is unknown.');
 text(s,'Western face  26.7 m\nSouthern face  25.7 m',65,170,372,105,29,{bold:true});
 text(s,'The corrected location\nreveals two faces near\n−12° from cardinal.',65,328,360,139,31);
 const rows=data.surkotada_lines.map((r,i)=>({label:(i?'Southern':'Western')+' '+deg(r.deviation_deg),value:r.deviation_deg,sigma:r.sigma_digitizing_deg,color:i?C.rust:C.teal}));
 intervalChart(s,rows,{min:-20,max:0,unit:5,x:446,y:193,w:754,h:369});
 text(s,'Digitizing-only errors: ±4.96° and ±5.18°. Total uncertainty remains unknown.',65,588,1148,57,26,{color:C.rust});
 foot(s,'One archived image and one observer. Exploratory picks after reading prior bearings.');
}
// 8. A phase distinction accompanies the laboratory determinations.
{
 const s=slide('Surkotada’s walls and dates belong to episodes',J+' '+RC+' '+P+'run-v5/chronology-parts.jsonl and radiocarbon.jsonl. The enclosure line starts in IA. Fig. 8 identifies the exposed stone rebuilding as IC. IC-associated charcoal relies on the inherited excavation-phase join. The four determinations were present in the prior verification and are not new acquisitions or determinations. No construction boundary or calendar founding date is estimated here.');
 text(s,'IA',67,169,120,64,48,{bold:true,color:C.teal});
 text(s,'First enclosure line',67,244,365,61,29);
 text(s,'IC',67,368,120,64,48,{bold:true,color:C.rust});
 text(s,'Exposed stone rebuilding',67,442,365,83,29);
 table(s,[['IC-associated charcoal','Reported age'],...data.radiocarbon.map(r=>[r.lab,`${r.bp} ± ${r.sigma} BP`])],480,173,730,337,[390,340],28);
 text(s,'The wall episode needs its own stratigraphic join to the dated deposits.',65,572,1145,66,30,{bold:true});
 foot(s,'Joshi (1990), Fig. 8. Agrawal & Kusumgar (1973), pp. 579–580. BP ages are uncalibrated.');
}
// 9. Full-resolution chart data preserve every 0.1° ray in the two sectors.
{
 const s=slide('Horizons at the corrected modern locations',DEM+' '+P+'HORIZON-REPAIR.md. GLO-30 from 2–20 km at 30 m steps, GLO-90 from 20–250 km at 90 m steps. Inner 2 km excluded. Rays every 0.1°, eye height 1.6 m, terrestrial refraction coefficient 0.13. The deck plots every retained ray. Farmana location is approximate (29.040 N, 76.306 E), rather than a surveyed wall point. Surkotada 23.6113 N, 70.9174 E. No total one-sigma error is available. Modern DSM includes structures and vegetation. Sector maxima: Surkotada east +0.096°, west +0.689°; Farmana east +0.049°, west +0.133°.');
 text(s,'Eastern sector',65,144,530,43,29,{bold:true});text(s,'Western sector',663,144,530,43,29,{bold:true});
 for(const [sector,left,min,max] of [['east',55,45,135],['west',654,225,315]]){
   const horizonChart=chart(s,'scatter',{position:{left,top:189,width:565,height:337},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:23,fill:C.ink}},scatterOptions:{style:'line'},series:data.horizons.map((t,i)=>{const rows=t.profile.filter(r=>r.az>=min&&r.az<=max);return {name:t.town==='surkotada'?'Surkotada':'Farmana',xValues:rows.map(r=>r.az),values:rows.map(r=>r.alt_deg),line:{fill:i?C.rust:C.teal,width:2.5},marker:{symbol:'none'}};}),xAxis:{min,max,majorUnit:30,tickLabelPosition:'low',title:{text:'Azimuth (°)',textStyle:{fontSize:22,fill:C.muted}},textStyle:{fontSize:22,fill:C.muted},majorGridlines:null},yAxis:{min:-.25,max:.8,majorUnit:.25,title:sector==='east'?{text:'Apparent altitude (°)',textStyle:{fontSize:22,fill:C.muted}}:undefined,textStyle:{fontSize:22,fill:C.muted},numberFormatCode:'0.00',majorGridlines:grid}});
   horizonChart.yAxis={crossesAt:-.25};
 }
 text(s,'Modern surface model, with the inner 2 km excluded.\nAncient ground level and vegetation remain unresolved.',65,549,1145,82,27);
 foot(s,'Copernicus WorldDEM-30 © DLR / Airbus, provided under COPERNICUS by the EU and ESA. All rights reserved.');
}
// 10. Every missing-field count comes from the retained town-level reasons.
{
 const s=slide('Missing fields across 34 towns',P+'run-v5/missing-fields.csv and town-axis-table.json /towns/*/missing. The counts total 218 missing or conflicting town-field rows across 34 towns, not independent observations. "Validated independent imagery" means the complete condition: different source products, matching part, agreement or retained discordance, and validated error. It does not mean every town has zero imagery products. The register assigns no pooled founding date and no Bayesian construction boundary. Fourteen lack a usable modern-location profile: thirteen have no profile and Gola Dhoro has an excluded profile at an unverified site point.');
 text(s,'Number of towns with a missing or conflicting field',65,124,1145,35,24,{color:C.muted});
 chart(s,'bar',{position:{left:55,top:165,width:1150,height:419},categories:data.gaps.map(r=>r.label),series:[{name:'Towns with missing or conflicting field',values:data.gaps.map(r=>r.count),fill:C.teal}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:48},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:27,fill:C.ink,bold:true}},xAxis:{textStyle:{fontSize:24,fill:C.ink},majorGridlines:null},yAxis:{min:0,max:38,majorUnit:10,textStyle:axisText,majorGridlines:grid,line:{fill:'none',width:0}}});
 text(s,'218 missing or conflicting town fields retain a reason in the table.',65,596,1140,47,29,{bold:true});
 foot(s,'A missing field records what evidence would make the next analysis possible.');
}
// 11. A single record shows the preserved chain into source observations.
{
 const s=slide('Each bearing keeps its source trail',P+'run-v5/measurements.jsonl, measurement_id new-surkotada:SK-W. Record pointer: '+P+'new-observations.json /structures/0. Exact source mosaic, native endpoint pixels, hash and acquisition date remain in new-observations.json /sources/0. '+data.surkotada_picks.sources[0].file+'. SHA-256 '+data.surkotada_picks.sources[0].sha256+'. Record hash ada52cd9b7330a7f8bef5ec8cc169ba23327829569a5c5aba6ff622404c04ba8. Geodesic record SHA-256 4fd88974b03b2abe72ac38c78d60ff87a01ac13689e6e498c41277812f779113 /rows/0. The full register links source locators, north labels, phase evidence, missingness and original uncertainty statements. Raw plans and imagery remain local-only and are not embedded here.');
 table(s,[['Western rampart, Surkotada','Retained evidence'],['Image locator','Wayback 8432, native mosaic and endpoints'],['North and bearing','True north, WGS84 inverse geodesic'],['Measured result','−11.83°, segment length 26.7 m'],['Uncertainty','±4.96° digitizing, total error unknown'],['Building episode','IC rebuilding on the IA enclosure line'],['Missing evidence','Exposure date and restoration survey']],64,151,1152,432,[410,742],25);
 foot(s,'Record: new-surkotada:SK-W. Exact source paths, SHA-256 and JSON pointers appear in the notes.');
}
// 12. The requested storage migration stays visible but separate from scientific claims.
{
 const s=slide('Bulk inputs now live on D:', 'LOCAL_STORAGE.md and LOCAL_STORAGE.json. experiments/2026-10-24-storage-migration/summary.json. SHA-256 verification matched 187,131 accessible files, 35,099,820,039 bytes, before removal of the C: originals. Nine junctions and 434 file links preserve historical paths. Fourteen denied subdirectories and one unreadable 110-byte file in an old plotting environment remain preserved on C: under data/storage-remnants-2026-10-24/. No unreadable content is claimed migrated. Tracked code and research records remain in the C: checkout. Migration manifest: D:/projects/indus_valley_script/migration-2026-10-24.json. New raw inputs and render files remain local-only under D:/projects/indus_valley_script/data/raw/.');
 text(s,'35.1 GB',65,168,570,117,88,{bold:true,color:C.teal});
 text(s,'187,131 accessible files\nverified before C: removal',69,311,560,107,31);
 text(s,'D:\\projects\\\nindus_valley_script',665,187,550,135,37,{bold:true});
 text(s,'Historical paths continue through\n9 junctions and 434 file links.',665,376,550,113,29);
 text(s,'New raw imagery, plans and DEM files stay local-only.\nAn inaccessible plotting environment remains preserved on C:.',65,554,1145,85,27);
 foot(s,'Local storage instructions and the migration manifest document the physical and logical paths.');
}
// 13. Short bibliography on the slide, complete locators and rights in notes.
{
 const s=slide('Sources and evidence routes',W+'\n\n'+J+'\n\n'+RC+'\n\n'+DEM+'\n\nPrior attempts: experiments/2026-10-21-town-axes/REPORT.md; experiments/2026-10-21-town-orientations-verification/REPORT.md; experiments/2026-10-21-plan-registration/REPORT.md. Current source-backed register '+P+'REPORT.md, TABLE.md, run-v5/. Earlier sources remain frozen. Current register audit: 207 input hashes and 3,009 references verified in audit-v5.json. Source-use counts are not publication counts. Original project prose and aggregate evidence under CC0, project code under Unlicense. Third-party source scans, imagery and DEM retain their own terms, remain local-only and are not embedded in this deck. Charts and tables remain native editable objects.');
 table(s,[['Source','Precise reading route'],['Wanzke (1987), Axis Systems and Orientation at Mohenjo-Daro','Printed pp. 33–44, PDF indices 35–46'],['Joshi (1990), Surkotada excavation report','Fig. 8 fold-out, PDF index 61'],['Agrawal & Kusumgar (1973), Date List X','Printed pp. 574, 579–580, DOI in notes'],['Copernicus DEM GLO-30 and GLO-90','Corrected-location profiles and tile records'],['Q-1032 experiment package','REPORT.md, TABLE.md and run-v5/']],64,155,1152,411,[620,532],25);
 text(s,'The notes preserve source paths, hashes, page locators and dataset attribution.',65,592,1145,49,26);
 foot(s,'Presentation of existing observations. No new source acquisition or confirmation test.');
}
// 14. The deck ends on the strongest reading and its deciding test.
{
 const s=slide('The deciding survey',P+'REPORT.md, final paragraph. Prospective test, not a new result. Relevant unit: a particular architectural system in a particular building episode. Before reading the survey, freeze wall identities, document restorations and register dated stratigraphic joins. Obtain true-north control sufficient for angular error below 0.5°. Predictions: Mohenjo-daro retains a near-cardinal system and a street system turned more than 5°; Surkotada IC ramparts remain more than 5° anticlockwise. If surveyed phase-linked walls collapse onto one common axis within their errors, the reading fails. A separate Lothal dock survey decides the imagery discrepancy. The earlier settlement-axis population has already been examined. This deck spends no new confirmation population.',true);
 text(s,'An architectural system in a building\nepisode is the unit the evidence supports.',65,148,1150,111,39,{bold:true,color:C.bg});
 text(s,'Mohenjo-daro',67,311,300,44,28,{bold:true,color:'#85C5BC'});
 text(s,'Moneer axes near cardinal, HR First Street turned >5°',387,311,819,70,28,{color:C.bg});
 text(s,'Surkotada',67,400,300,44,28,{bold:true,color:'#85C5BC'});
 text(s,'IC ramparts anticlockwise by >5°',387,400,819,44,28,{color:C.bg});
 text(s,'Lothal',67,479,300,44,28,{bold:true,color:'#85C5BC'});
 text(s,'Dock survey decides the imagery discrepancy',387,479,819,44,28,{color:C.bg});
 text(s,'True-north error <0.5°. Freeze walls and phase joins before reading.\nIf the phase-linked walls share one axis within errors, this reading fails.',65,592,1150,82,25,{color:C.bg});
}

const expected=14;
if(p.slides.items.length!==expected)throw new Error('Unexpected slide count');
await fs.writeFile(path.join(build,'deck.json'),JSON.stringify(p.toProto()));
for(const [i,s] of p.slides.items.entries()){
  const file=path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`);
  const blob=await p.export({slide:s,format:'png',scale:1});
  await fs.writeFile(file,new Uint8Array(await blob.arrayBuffer()));
  console.log(`Rendered ${i+1}/${expected}`);
}
const montage=await p.export({format:'webp',montage:true});
await fs.writeFile(path.join(build,'montage.webp'),new Uint8Array(await montage.arrayBuffer()));
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
const final=path.join(LOCAL,'output',`town-axes-2026-10-24-${RUN}.pptx`);
const result=await finalizePresentation({
 workspaceDir:LOCAL,candidatePath:candidate,finalPath:final,pythonExecutable:RUNTIME_PYTHON,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,4,8,11,13].flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:expected,requiredNativeTableOwnerSlides:[3,4,8,11,13],requiredNativeChartOwnerSlides:[2,5,6,7,9,10],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation.json')
});
console.log(JSON.stringify({final,font:FONT,result}));
