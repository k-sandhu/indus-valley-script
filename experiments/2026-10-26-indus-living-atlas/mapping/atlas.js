/* Original project code. Leaflet and Natural Earth retain their notices. */
(() => {
  "use strict";
  const data = window.INDUS_ATLAS;
  const $ = (id) => document.getElementById(id);
  if (!data || !window.L) {
    $("result-count").textContent = "The local map assets could not be loaded. Open the package README for the source records.";
    return;
  }
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const southAsia = new Set(["Pakistan", "India", "Afghanistan", "Nepal", "Bangladesh", "Sri Lanka", "Bhutan", "Maldives"]);
  const periodRanges = {early: [4000,2600], mature: [2600,1900], late: [1900,1300]};
  const major = new Set(["mohenjo-daro","harappa","dholavira","lothal","rakhigarhi","kalibangan","ganweriwala"]);
  const townLabels = new Set(["LT-01","LT-04","LT-05","LT-12","LT-15","LT-16"]);
  const state = {layer:"sites", period:"all", extent:"south-asia", query:"", country:"all", quality:"all", dateQuality:"all", year:2300, singleYear:false, labels:true, selected:null};
  const map = L.map("map", {zoomControl:false, minZoom:2, maxZoom:18, preferCanvas:true, zoomSnap:0.25, wheelPxPerZoomLevel:90}).setView([26.2,72.8],5);
  L.control.zoom({position:"topright"}).addTo(map);
  L.control.scale({imperial:false, maxWidth:110}).addTo(map);
  map.attributionControl.setPrefix('<a href="mapping/vendor/leaflet/LICENSE">Leaflet</a>');
  L.geoJSON(data.geography, {style:{color:"#bacdba",weight:0.8,fillColor:"#edf0dc",fillOpacity:1},interactive:false}).addTo(map);
  if(data.rivers)L.geoJSON(data.rivers, {style:{color:"#88adb1",weight:1.3,opacity:0.78},interactive:false}).addTo(map);
  map.attributionControl.addAttribution('<a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noopener">Natural Earth</a> · modern geographic context');
  const graticule = L.layerGroup().addTo(map);
  for(let lat=-10;lat<=50;lat+=5) L.polyline([[lat,25],[lat,110]],{color:"#91aca1",weight:0.5,opacity:0.16,interactive:false}).addTo(graticule);
  for(let lon=25;lon<=110;lon+=5) L.polyline([[-10,lon],[50,lon]],{color:"#91aca1",weight:0.5,opacity:0.16,interactive:false}).addTo(graticule);
  const countryLabels = L.layerGroup().addTo(map);
  [["PAKISTAN",29.0,67.0],["INDIA",23.0,78.4],["AFGHANISTAN",34.2,65.1],["NEPAL",28.3,83.0],["IRAN",32.0,54.8],["SRI LANKA",7.1,79.5],["BANGLADESH",23.8,88.9],["OMAN",20.3,55.2],["IRAQ",33.4,43.2]].forEach(([name,lat,lon]) => L.marker([lat,lon],{icon:L.divIcon({className:"country-label",html:esc(name),iconSize:[130,15]}),interactive:false}).addTo(countryLabels));
  [["Indus · modern course",27.7,68.4],["Ganges · modern course",25.5,82.0]].forEach(([name,lat,lon]) => L.marker([lat,lon],{icon:L.divIcon({className:"river-label",html:esc(name),iconSize:[140,12]}),interactive:false}).addTo(countryLabels));
  const markers = L.layerGroup().addTo(map);
  const lookup = new Map();
  let visible = [];
  let streets = null;
  const sourceLookup = new Map(data.sources.map(s => [s.id,s]));
  const townSourceLookup = new Map(data.town_sources.map(s => [s.id,s]));

  function isLocated(row) {return Number.isFinite(row.lat) && Number.isFinite(row.lon);}
  function phases(row) {return (row.phases || []).filter(p => Number.isFinite(p.start_bce) && Number.isFinite(p.end_bce));}
  function overlaps(p, older, younger) {
    if(older===younger||p.start_bce===p.end_bce)return p.start_bce>=younger&&p.end_bce<=older;
    return p.start_bce>younger&&p.end_bce<older;
  }
  function dateMatches(row) {
    if (row.layer === "town") return true;
    if (!state.singleYear && state.period === "all") return true;
    const range = state.singleYear ? [state.year,state.year] : periodRanges[state.period];
    return phases(row).some(p => overlaps(p,...range));
  }
  function isFlagged(row) {return (row.warnings||[]).some(s => /coordinate conflict|location check|locator that|coordinate.*conflict|site-specific witness/i.test(s));}
  function siteSpecific(row) {return phases(row).some(p => !p.convention);}
  function searchMatches(row) {
    const haystack = [row.name,row.country,row.region,...(row.alts||[])].join(" ").normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
    return haystack.includes(state.query.normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase());
  }
  function matches(row) {
    if (state.extent === "south-asia" && !southAsia.has(row.country)) return false;
    if (state.country !== "all" && row.country !== state.country) return false;
    if (!searchMatches(row) || !dateMatches(row)) return false;
    if (row.layer !== "town") {
      if(state.quality==="site" && row.coord_kind!=="site coordinate") return false;
      if(state.quality==="approximate" && row.coord_kind==="site coordinate") return false;
      if(state.quality==="flagged" && !isFlagged(row)) return false;
      if(state.dateQuality==="site" && !siteSpecific(row)) return false;
      if(state.dateQuality==="convention" && (siteSpecific(row)||phases(row).length===0)) return false;
    }
    return true;
  }
  const townReviewRows = data.towns.map(r => ({...r,layer:"town"}));
  const townRows = townReviewRows.filter(r => r.category !== "abandoned-indus-contrast");
  const siteRows = data.sites;
  const rowKey = (r) => `${r.layer}:${r.id}`;
  const allRows = [...siteRows,...townRows];
  const byKey = new Map(allRows.map(r => [rowKey(r),r]));
  const boundsFor = (rows) => rows.filter(isLocated).map(r=>[r.lat,r.lon]);

  function rangeText(row) {
    if(row.layer==="town") {
      const v=row.earliest_evidence_bce || {};
      return v.date_label || (v.earliest ? `${v.earliest} BCE · earliest evidence` : "Inspect dated sequence");
    }
    const p=phases(row);
    if(!p.length) return "No plotted phase range";
    return `${Math.max(...p.map(v=>v.start_bce)).toLocaleString()}–${Math.min(...p.map(v=>v.end_bce)).toLocaleString()} BCE`;
  }
  function pointStyle(row) {
    const selected = state.selected===rowKey(row);
    const town = row.layer==="town";
    return {radius:selected?9:major.has(row.id)?7:town?5.5:4.2,color:town?"#2a6a57":isFlagged(row)?"#a06423":"#9c6e38",fillColor:town?"#417f68":isFlagged(row)?"#fff0c9":major.has(row.id)?"#b97536":"#c39862",fillOpacity:selected?1:0.88,weight:selected?2.5:1.2,dashArray:!town&&row.coord_kind!=="site coordinate"?"2 2":null};
  }
  function render() {
    const rows = state.layer==="sites" ? siteRows : state.layer==="towns" ? townRows : allRows;
    visible = rows.filter(matches).sort((a,b)=>Number(major.has(b.id))-Number(major.has(a.id)) || a.name.localeCompare(b.name));
    markers.clearLayers();lookup.clear();
    for(const row of visible.filter(isLocated)) {
      const town = row.layer==="town";
      const marker = L.circleMarker([row.lat,row.lon],pointStyle(row)).addTo(markers);
      const label = row.name;
      marker.bindTooltip(esc(label), {permanent:state.labels&&(major.has(row.id)||map.getZoom()>=6.5||townLabels.has(row.id)),direction:"right",offset:[7,0],className:"site-label"});
      marker.on("click",()=>select(rowKey(row),false));
      lookup.set(rowKey(row),marker);
    }
    const located=visible.filter(isLocated).length;
    $("result-count").textContent=`${located} mapped${visible.length!==located?` · ${visible.length-located} unlocated`:""}`;
    $("place-list").innerHTML=visible.length ? visible.map(row=>`<button type="button" class="place ${row.layer==="town"?"town":""} ${isFlagged(row)?"flagged":""} ${!isLocated(row)?"unlocated":""} ${state.selected===rowKey(row)?"selected":""}" data-key="${esc(rowKey(row))}"><i class="place-symbol" aria-hidden="true"></i><span><span class="place-name">${esc(row.name)}${row.layer==="town"&&state.layer==="both"?" · today":""}</span><small>${esc(row.country)} · ${isLocated(row)?esc(rangeText(row)):"location unresolved"}</small></span><span class="place-arrow" aria-hidden="true">↗</span></button>`).join("") : '<p class="empty">No places match these filters. Try another period, country or map extent.</p>';
    $("map-mode").textContent=state.layer==="sites"?"INDUS FIND LOCATIONS":state.layer==="towns"?"TOWN / PLACE CANDIDATES":"PLACES AND TOWNS TODAY";
    $("map-subtitle").textContent=state.layer==="sites"?"Source-linked reference points":"Town / place anchors · separate occupation evidence";
    $("time-description").textContent=state.singleYear?`${state.year.toLocaleString()} BCE`:state.period==="all"?"All recorded periods":`${periodRanges[state.period][0]}–${periodRanges[state.period][1]} BCE`;
    $("time-note").textContent=state.layer==="sites"?"A recorded range overlaps the selected period. Site dates are separate from inscription dates.":"Date filters apply to archaeological find sites. Town anchors remain visible; inspect each occupation sequence.";
    if(state.selected&&!visible.some(r=>rowKey(r)===state.selected)) closeDetail();
    $("quality").disabled=state.layer==="towns";
    $("date-quality").disabled=state.layer==="towns";
    const datesDisabled=state.layer==="towns";
    document.querySelectorAll("[data-period]").forEach(b=>{b.disabled=datesDisabled;b.classList.toggle("active",!state.singleYear&&b.dataset.period===state.period);});
    $("single-year").disabled=datesDisabled;
    $("year").disabled=datesDisabled||!state.singleYear;
  }
  function fitResults() {
    const points=boundsFor(visible);
    if(!points.length)return;
    if(points.length===1)map.setView(points[0],9,{animate:false});
    else map.fitBounds(points,{padding:[48,48],maxZoom:8,animate:false});
  }
  function sourceMarkup(source) {
    if(!source)return "";
    const url=source.url||source.link;
    return `<cite>${url&&/^https?:\/\//.test(url)?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(source.title||source.id)} ↗</a>`:esc(source.title||source.id)}${source.authors?` · ${esc(Array.isArray(source.authors)?source.authors.join(", "):source.authors)}`:""}${source.year?` (${esc(source.year)})`:""}${source.locator?`<br>${esc(source.locator)}`:""}</cite>`;
  }
  function valueMarkup(value) {return esc(typeof value==="object" ? Object.entries(value||{}).map(([k,v])=>`${k.replaceAll("_"," ")}: ${typeof v==="object"?JSON.stringify(v):v}`).join("; ") : value);}
  function continuityText(value) {
    return ({"long-sequence-continuity-unproven":"A long sequence is recorded; uninterrupted occupation to the present remains unproven.","continuity-asserted-not-demonstrated":"The source asserts continuity. The full dated sequence has not been demonstrated in this review.","unresolved":"The earliest town occupation or its continuity remains unresolved.","documented-sequence-with-hiatus":"The recorded sequence includes an occupation break.","nearby-modern-settlement":"The older excavated settlement lies near the modern town.","archaeological-or-sacred-place-not-town-continuity":"This is an archaeological or sacred place; uninterrupted town occupation has not been demonstrated.","abandoned-ancient-city":"The ancient city was abandoned. Nearby modern settlement has a separate history."})[value] || String(value||"");
  }
  function select(key,pan=true) {
    const row=byKey.get(key);if(!row)return;
    state.selected=key;
    const panel=$("detail-panel");
    let html=`<button class="panel-close" type="button" aria-label="Close place details">×</button><span class="eyebrow">${row.layer==="town"?"LIVING TOWN · EVIDENCE REVIEW":"ARCHAEOLOGICAL PLACE"}</span><h2>${esc(row.name)}</h2><div class="location-line">${esc([row.province,row.region,row.country].filter(Boolean).join(" · "))}</div>`;
    if(row.layer==="town") {
      html+=`<span class="tag">Town / place anchor today</span><p>${esc(row.modern_civic_identity||"")}</p><p>${esc(row.summary)}</p><h3>Earliest recorded evidence</h3><p><strong>${esc(row.earliest_evidence_bce?.date_label||"Date unresolved")}</strong><br>${esc(row.earliest_evidence_bce?.basis||"")}</p><p class="source">Evidence place: ${esc(row.evidence_place||row.name)}</p><h3>Occupation and place</h3><p>${esc(continuityText(row.continuity_status))}</p><p>${valueMarkup(row.spatial_relation)}</p><h3>Overlap with Indus chronology</h3><p>2600–1900 BCE: ${esc(row.indus_overlap?.mature_2600_1900||"unresolved")}<br>1900–1300 BCE: ${esc(row.indus_overlap?.late_1900_1300||"unresolved")}</p><p class="source">${esc(row.indus_overlap?.basis||"")}</p>`;
      if(row.known_hiatuses?.length)html+=`<h3>Gaps and interruptions</h3>${row.known_hiatuses.map(v=>`<p>${esc(v)}</p>`).join("")}`;
      html+=`<h3>Location precision</h3><p>Approximate indexing radius: ${esc(row.coordinate_precision?.meters/1000)} km.<br>${esc(row.coordinate_precision?.basis||"")}</p>`;
      if(row.gaps?.length)html+=`<h3>Evidence still needed</h3>${row.gaps.map(g=>`<p>${esc(g)}</p>`).join("")}`;
      html+=`<h3>Sources</h3><div class="source">${(row.source_ids||[]).map(id=>sourceMarkup(townSourceLookup.get(id))).join("")}</div><a class="primary-link" href="research.html#living-towns">Read the living-towns study ↗</a>`;
    } else {
      html+=`<span class="tag">${esc(row.coord_kind||"Location unavailable")}</span><span class="tag">${siteSpecific(row)?"Site-specific date range":"Regional / unresolved dating"}</span>`;
      if(row.warnings?.length)html+=`<h3>Evidence to resolve</h3>${row.warnings.map(w=>`<p>${esc(w)}</p>`).join("")}`;
      html+=`<h3>Location</h3><p>${isLocated(row)?`${row.lat.toFixed(5)}° N, ${row.lon.toFixed(5)}° E<br>`:"No coordinate plotted.<br>"}${esc(row.coordinate_precision)}</p><p class="source">${esc(row.coord_source)}</p><p>${esc(row.coord_note||"")}</p>`;
      if(row.coordinate_assertions?.length) html+=`<div class="source"><details><summary>Compare ${row.coordinate_assertions.length} later coordinate assertions</summary>${row.coordinate_assertions.map(v=>`<p>${esc(v.lat)} N, ${esc(v.lon)} E · ${esc(v.basis||"")}</p>`).join("")}</details></div>`;
      html+=`<h3>Dated site phases</h3><p class="source">${esc(row.evidence_status)} Intervals refer to the site or deposit described by their source.</p>${phases(row).map(p=>`<div class="phase"><strong>c. ${esc(p.start_bce)}–${esc(p.end_bce)} BCE</strong><span>${esc(p.label)}</span><small>${p.convention?"Regional convention · ":""}${esc(p.basis||"Basis not supplied")}<br>${esc(p.source)}</small></div>`).join("")||'<p>No numerical phase range is supplied.</p>'}`;
      if(row.reviewed_ranges?.length)html+=`<h3>Rechecked summary</h3>${row.reviewed_ranges.map(p=>`<p>c. ${esc(p.start_bce)}–${esc(p.end_bce)} BCE · ${esc(p.label)}</p><p class="source">${esc(p.basis)}</p>`).join("")}`;
      const official=(row.official_source_ids||[]).map(id=>sourceMarkup(sourceLookup.get(id))).join("");
      if(official)html+=`<div class="source">${official}</div>`;
      const reports=(row.counts?.reported||[]);
      if(reports.length)html+=`<h3>Published object counts</h3><div class="source"><details><summary>Inspect ${reports.length} attributed count statements</summary>${reports.map(c=>`<p>${esc(c.text)}</p><cite>${esc(c.source)}</cite>`).join("")}</details></div>`;
      if(row.model_id)html+=`<a class="primary-link" href="reconstruction/index.html#model=${encodeURIComponent(row.model_id)}">Explore architecture in 3D ↗</a><a class="secondary-link" href="reconstruction/index.html#model=${encodeURIComponent(row.model_id)}&view=plan">Open the top-down city / building plan ↗</a>`;
      if(row.architectural_register)html+=`<a class="secondary-link" href="${esc(row.architectural_register)}">Architectural source register ↗</a>`;
      html+='<a class="secondary-link" href="https://github.com/k-sandhu/indus-valley-script/blob/feb2061f1c880b0817137417f4f36bda62795b1b/presentations/2026-10-08-site-map-and-overview/README.md">Earlier map: sources and known gaps ↗</a>';
    }
    panel.innerHTML=html;panel.hidden=false;
    panel.querySelector(".panel-close").addEventListener("click",closeDetail);
    if(pan&&isLocated(row))map.setView([row.lat,row.lon],Math.max(map.getZoom(),7),{animate:!window.matchMedia("(prefers-reduced-motion: reduce)").matches});
    document.querySelectorAll(".place").forEach(b=>b.classList.toggle("selected",b.dataset.key===key));
    for(const [k,marker] of lookup)marker.setStyle(pointStyle(byKey.get(k))).setRadius(pointStyle(byKey.get(k)).radius);
    if(window.innerWidth<=640&&pan)$("map").scrollIntoView({block:"start",behavior:"smooth"});
  }
  function closeDetail() {state.selected=null;$("detail-panel").hidden=true;for(const [key,m]of lookup){const style=pointStyle(byKey.get(key));m.setStyle(style).setRadius(style.radius);}document.querySelectorAll(".place.selected").forEach(b=>b.classList.remove("selected"));}
  function setLayer(layer) {
    state.layer=layer;closeDetail();
    document.querySelectorAll("[data-layer]").forEach(b=>b.classList.toggle("active",b.dataset.layer===layer));
    render();fitResults();
  }
  function renderTownTable() {
    $("town-table").innerHTML=townReviewRows.length ? `<table><thead><tr><th>TOWN / PLACE</th><th>EARLIEST EVIDENCE</th><th>CONTINUITY ASSESSED</th><th>PLACE AND SEQUENCE</th></tr></thead><tbody>${townReviewRows.map(r=>`<tr><td>${r.category==="abandoned-indus-contrast"?`<a href="index.html#site=${esc(r.name.toLowerCase())}">${esc(r.name)} ↗</a><br><span class="tag warn">Abandoned-city comparison</span>`:`<button type="button" data-town="${esc(rowKey(r))}">${esc(r.name)} ↗</button>`}<br><span class="small">${esc(r.country)}</span></td><td>${esc(rangeText(r))}</td><td>${esc(continuityText(r.continuity_status))}</td><td>${esc(r.summary)}</td></tr>`).join("")}</tbody></table>` : '<p>The living-town review is being prepared. Its source report is linked above.</p>';
  }
  function exportVisible() {
    const collection={type:"FeatureCollection",name:"Indus Atlas filtered reference points",metadata:{date:"2026-10-26",scope:data.scope,filters:{...state},unlocated:visible.filter(r=>!isLocated(r)).map(r=>({id:r.id,name:r.name,layer:r.layer})),coordinate_reference:"Longitude, latitude display coordinates; original source datum is not uniformly established."},features:visible.filter(isLocated).map(row=>({type:"Feature",id:rowKey(row),geometry:{type:"Point",coordinates:[row.lon,row.lat]},properties:row}))};
    const blob=new Blob([JSON.stringify(collection,null,2)],{type:"application/geo+json"});
    const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="indus-atlas-places.geojson";a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  const countries=[...new Set(allRows.map(r=>r.country))].sort();
  $("country").innerHTML='<option value="all">All countries</option>'+countries.map(c=>`<option>${esc(c)}</option>`).join("");
  $("search").addEventListener("input",e=>{state.query=e.target.value.trim();render();});
  $("extent").addEventListener("change",e=>{state.extent=e.target.value;render();fitResults();});
  $("country").addEventListener("change",e=>{state.country=e.target.value;render();fitResults();});
  $("quality").addEventListener("change",e=>{state.quality=e.target.value;render();});
  $("date-quality").addEventListener("change",e=>{state.dateQuality=e.target.value;render();});
  $("labels").addEventListener("change",e=>{state.labels=e.target.checked;render();});
  document.querySelectorAll("[data-layer]").forEach(b=>b.addEventListener("click",()=>setLayer(b.dataset.layer)));
  document.querySelectorAll("[data-period]").forEach(b=>b.addEventListener("click",()=>{state.period=b.dataset.period;state.singleYear=false;$("single-year").checked=false;render();}));
  $("single-year").addEventListener("change",e=>{state.singleYear=e.target.checked;render();});
  $("year").addEventListener("input",e=>{state.year=Number(e.target.value);$("year-label").textContent=`${state.year} BCE`;render();});
  $("place-list").addEventListener("click",e=>{const b=e.target.closest("[data-key]");if(b)select(b.dataset.key);});
  $("fit").addEventListener("click",fitResults);
  $("home").addEventListener("click",()=>{closeDetail();fitResults();});
  $("legend-toggle").addEventListener("click",()=>{const legend=$("legend");if(innerWidth<=640)legend.classList.toggle("mobile-visible");else legend.hidden=!legend.hidden;});
  $("export").addEventListener("click",exportVisible);
  $("about-open").addEventListener("click",()=>$("about-dialog").showModal());
  $("towns-open").addEventListener("click",()=>$("towns-dialog").showModal());
  document.querySelectorAll("[data-close]").forEach(b=>b.addEventListener("click",()=>$(b.dataset.close).close()));
  $("town-table").addEventListener("click",e=>{const b=e.target.closest("[data-town]");if(!b)return;$("towns-dialog").close();state.query="";$("search").value="";state.country="all";$("country").value="all";state.extent="south-asia";$("extent").value="south-asia";setLayer("towns");select(b.dataset.town);});
  document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDetail();});
  let lastLabelZoom=map.getZoom()>=6.5;
  map.on("zoomend",()=>{const current=map.getZoom()>=6.5;if(current!==lastLabelZoom){lastLabelZoom=current;render();}});
  renderTownTable();render();fitResults();
  const hash=new URLSearchParams(location.hash.slice(1));
  if(hash.get("layer")==="towns")setLayer("towns");
  if(hash.get("site"))select(`find-site:${hash.get("site")}`);
  window.indusAtlas={getState:()=>({...state}),getVisible:()=>visible.map(r=>({id:r.id,layer:r.layer,located:isLocated(r)})),overlaps};
})();
