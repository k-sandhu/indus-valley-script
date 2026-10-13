(function () {
  'use strict';
  const data = window.ATLAS_DATA;
  const geography = window.ATLAS_GEOGRAPHY;
  if (!data) {
    document.getElementById('map').textContent = 'The local atlas data file could not load.';
    return;
  }
  const STATUS = {
    known: {label:'Known archaeological record', glyph:'●', color:'#235d87'},
    published_candidate: {label:'Published candidate', glyph:'◆', color:'#a46b08'},
    screening_lead: {label:'Unverified landform lead', glyph:'▲', color:'#8551ae'},
    rejected: {label:'Rejected screening feature', glyph:'×', color:'#ac4b4b'},
    control: {label:'Comparison or control', glyph:'○', color:'#277763'},
    context: {label:'Landscape context', glyph:'≈', color:'#427f92'}
  };
  const KIND = {rgb:'True colour', false_colour:'False colour', ndvi:'NDVI', terrain:'Terrain'};
  const blocks = data.study_blocks;
  const overlays = data.overlays;
  const features = data.feature_collection.features;
  const config = data.viewer_config;
  const byId = new Map(features.map(function (feature) { return [feature.properties.id, feature]; }));
  const enabled = new Set(Object.keys(STATUS).filter(function (key) { return key !== 'context'; }));
  const blockSelect = document.getElementById('block-select');
  const kindSelect = document.getElementById('raster-kind');
  const dateSelect = document.getElementById('date-select');
  const opacity = document.getElementById('opacity');
  const contextToggle = document.getElementById('context-toggle');
  const uncertaintyToggle = document.getElementById('uncertainty-toggle');
  const osmToggle = document.getElementById('osm-toggle');
  const sourceIndex = new Map();
  let map = null;
  let osm = null;
  let selected = null;
  let imagery = [];
  let featureLayers = new Map();
  let featureGroup = null;
  let uncertaintyGroup = null;
  let blockGroup = null;
  let countryLabels = null;
  let imageErrors = [];

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }
  function list(value) {
    if (value === undefined || value === null) return [];
    return Array.isArray(value) ? value : [value];
  }
  function display(value) {
    const items = list(value);
    return items.length ? items.map(function (item) {
      return typeof item === 'object' ? JSON.stringify(item) : String(item);
    }).join('; ') : 'Not supplied';
  }
  function safeLink(url, label) {
    if (typeof url !== 'string' || !/^https?:\/\//i.test(url)) return element('span', label || url || '');
    const link = element('a', label || url);
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener';
    return link;
  }
  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character];
    });
  }
  list(data.sources).forEach(function (source) {
    if (source && source.id) sourceIndex.set(source.id, source.url || source.href);
  });
  function sourceNodes(ids, urls) {
    const wrapper = element('span');
    list(ids).forEach(function (id, index) {
      if (index) wrapper.appendChild(document.createTextNode('; '));
      wrapper.appendChild(safeLink(sourceIndex.get(id), String(id)));
    });
    list(urls).forEach(function (url) {
      wrapper.appendChild(document.createTextNode(' '));
      wrapper.appendChild(safeLink(url, 'Source'));
    });
    if (!wrapper.textContent) wrapper.textContent = 'Not supplied';
    return wrapper;
  }
  function geometryBounds(feature) {
    let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity;
    function visit(values) {
      if (typeof values[0] === 'number') {
        west = Math.min(west, values[0]); east = Math.max(east, values[0]);
        south = Math.min(south, values[1]); north = Math.max(north, values[1]);
      } else values.forEach(visit);
    }
    visit(feature.geometry.coordinates);
    return [west, south, east, north];
  }
  function geographicLink(feature) {
    let lon, lat;
    if (feature.geometry.type === 'Point') {
      lon = feature.geometry.coordinates[0];
      lat = feature.geometry.coordinates[1];
    } else {
      const extent = geometryBounds(feature);
      lon = (extent[0] + extent[2]) / 2;
      lat = (extent[1] + extent[3]) / 2;
    }
    if (lon === undefined) return null;
    const pointQuery = feature.geometry.type === 'Point' ? '?mlat=' + lat + '&mlon=' + lon : '';
    return safeLink('https://www.openstreetmap.org/' + pointQuery + '#map=14/' + lat + '/' + lon,
      feature.geometry.type === 'Point' ? 'Open geographic location' : 'Open feature area on OSM');
  }
  function details(feature, compact) {
    const properties = feature.properties;
    const node = element('div');
    const status = STATUS[properties.status];
    node.appendChild(element('span', status.label, 'record-status'));
    node.appendChild(element('h3', properties.name || properties.id));
    node.appendChild(element('p', properties.explanation || 'No explanation was supplied.'));
    const dl = element('dl', null, 'popup-details');
    const location = feature.geometry.type === 'Point' ?
      feature.geometry.coordinates[1].toFixed(6) + '° latitude, ' + feature.geometry.coordinates[0].toFixed(6) + '° longitude' :
      geometryBounds(feature).map(function (value) { return value.toFixed(6); }).join(', ') + ' (west, south, east, north)';
    [
      ['Record', properties.id],
      ['Study block', display(properties.block_id)],
      [feature.geometry.type === 'Point' ? 'Recorded coordinates' : 'Geometry bounds', location],
      ['Observation IDs', display(properties.observation_ids)],
      ['Dates in record', display(properties.dates)],
      ['Analyst plotting buffer', properties.coordinate_uncertainty_m === undefined || properties.coordinate_uncertainty_m === null ? 'Not supplied' : properties.coordinate_uncertainty_m + ' m'],
      ['Next test', display(properties.next_test)]
    ].forEach(function (row) {
      dl.appendChild(element('dt', row[0]));
      dl.appendChild(element('dd', row[1]));
    });
    dl.appendChild(element('dt', 'Sources'));
    const sources = element('dd');
    sources.appendChild(sourceNodes(properties.source_ids, properties.source_urls));
    dl.appendChild(sources);
    node.appendChild(dl);
    if (properties.uncertainty_basis) node.appendChild(element('p', properties.uncertainty_basis, 'small-note'));
    if (properties.metrics) {
      const measurements = element('details');
      measurements.appendChild(element('summary', 'Supplied measurements and definitions'));
      measurements.appendChild(element('pre', JSON.stringify(properties.metrics, null, 2), 'metric-record'));
      node.appendChild(measurements);
    }
    const locationLink = geographicLink(feature);
    if (locationLink) node.appendChild(locationLink);
    if (!compact) {
      const matching = activeOverlays().filter(function (overlay) { return overlay.block_id === properties.block_id; })[0];
      if (properties.panel_path || matching) {
        const link = element('a');
        link.href = properties.panel_path || matching.path;
        link.target = '_blank'; link.rel = 'noopener';
        const image = element('img', null, 'evidence-image');
        image.src = link.href;
        image.alt = properties.panel_path ? 'Acquired-image and terrain evidence panel for ' + properties.id :
          KIND[matching.kind] + ' scene for ' + matching.block_id + ', ' + display(matching.date);
        link.appendChild(image);
        node.appendChild(link);
        if (properties.panel_path) node.appendChild(element('p', 'Open the full annotated evidence panel.', 'small-note'));
      }
    }
    return node;
  }
  function bounds(values) { return [[values[1], values[0]], [values[3], values[2]]]; }
  function blockMatches(blockId) { return blockSelect.value === 'all' || blockSelect.value === blockId; }
  function visibleFeature(feature) {
    const p = feature.properties;
    return (!p.block_id || blockMatches(p.block_id)) &&
      (p.status === 'context' ? contextToggle.checked : enabled.has(p.status));
  }
  function activeOverlays() {
    const candidates = overlays.filter(function (overlay) {
      return blockMatches(overlay.block_id) && overlay.kind === kindSelect.value &&
        (dateSelect.value === 'latest' || display(overlay.date) === dateSelect.value);
    });
    if (dateSelect.value !== 'latest') return candidates;
    const latest = new Map();
    candidates.forEach(function (overlay) {
      const previous = latest.get(overlay.block_id);
      if (!previous || display(overlay.date).localeCompare(display(previous.date)) > 0) latest.set(overlay.block_id, overlay);
    });
    return Array.from(latest.values());
  }
  function updateDates() {
    const previous = dateSelect.value;
    dateSelect.replaceChildren();
    const latest = element('option', 'Latest available per block');
    latest.value = 'latest';
    dateSelect.appendChild(latest);
    const dates = new Set(overlays.filter(function (overlay) {
      return blockMatches(overlay.block_id) && overlay.kind === kindSelect.value;
    }).map(function (overlay) { return display(overlay.date); }));
    Array.from(dates).sort().reverse().forEach(function (date) {
      const option = element('option', date);
      option.value = date;
      dateSelect.appendChild(option);
    });
    dateSelect.value = dates.has(previous) ? previous : 'latest';
    Array.from(kindSelect.options).forEach(function (option) {
      const available = overlays.some(function (overlay) { return blockMatches(overlay.block_id) && overlay.kind === option.value; });
      option.disabled = !available;
      option.textContent = (option.value === 'ndvi' ? 'Vegetation · ' : option.value === 'terrain' ? '' : 'Satellite · ') + KIND[option.value] + (available ? '' : ' · not supplied');
    });
    if (kindSelect.selectedOptions[0] && kindSelect.selectedOptions[0].disabled) {
      const available = Array.from(kindSelect.options).find(function (option) { return !option.disabled; });
      if (available) { kindSelect.value = available.value; updateDates(); }
    }
  }
  function updateProvenance() {
    const container = document.getElementById('image-provenance');
    container.replaceChildren();
    const active = activeOverlays();
    if (!active.length) container.appendChild(element('p', 'No acquired image was supplied for this selection.', 'small-note'));
    active.forEach(function (overlay) {
      const caption = element('div', null, 'image-caption');
      caption.appendChild(element('strong', overlay.block_id + ' · ' + KIND[overlay.kind] + ' · ' + display(overlay.date)));
      caption.appendChild(element('p', 'Native pixel size: ' + display(overlay.native_pixel_m) + ' m · display EPSG:3857'));
      if (overlay.display_pixel_m) caption.appendChild(element('p',
        'PNG grid: ' + overlay.width + ' × ' + overlay.height + ' pixels · ' +
        overlay.display_pixel_m.map(function (value) { return value.toFixed(2); }).join(' × ') + ' projected metres per pixel'));
      caption.appendChild(element('p', 'Source items: ' + display(overlay.source_item_ids)));
      caption.appendChild(element('p', display(overlay.attribution)));
      if (list(overlay.limits).length) caption.appendChild(element('p', display(overlay.limits)));
      const link = element('a', 'Open local image');
      link.href = overlay.path;
      link.target = '_blank';
      link.rel = 'noopener';
      caption.appendChild(link);
      container.appendChild(caption);
    });
    if (imageErrors.length) container.appendChild(element('p', 'Image load error: ' + imageErrors.join('; '), 'small-note'));
    if (!map) {
      const fallback = document.getElementById('fallback-links');
      fallback.replaceChildren();
      active.forEach(function (overlay) {
        const img = element('img', null, 'fallback-image');
        img.src = overlay.path;
        img.alt = overlay.block_id + ' ' + KIND[overlay.kind] + ', ' + display(overlay.date);
        fallback.appendChild(img);
      });
      const links = element('ul');
      features.filter(visibleFeature).forEach(function (feature) {
        const item = element('li', feature.properties.name || feature.properties.id);
        const link = geographicLink(feature);
        if (link) { item.appendChild(document.createTextNode(' · ')); item.appendChild(link); }
        links.appendChild(item);
      });
      fallback.appendChild(links);
    }
  }
  function renderImagery() {
    if (map) {
      imagery.forEach(function (layer) { map.removeLayer(layer); });
      imageErrors = [];
      imagery = activeOverlays().map(function (overlay) {
        const layer = L.imageOverlay(overlay.path, bounds(overlay.bounds_lonlat), {
          opacity:Number(opacity.value) / 100, pane:'imagery', interactive:false,
          alt:overlay.block_id + ' · ' + KIND[overlay.kind] + ' · ' + display(overlay.date),
          attribution:escapeHtml(overlay.attribution)
        });
        layer.on('error', function () { imageErrors.push(overlay.id); updateProvenance(); });
        layer.addTo(map);
        return layer;
      });
    }
    updateProvenance();
  }
  function symbol(status) {
    const color = STATUS[status].color;
    let shape;
    if (status === 'published_candidate') shape = '<path d="M11 1 L21 11 L11 21 L1 11 Z" fill="' + color + '" stroke="white" stroke-width="2"/>';
    else if (status === 'screening_lead') shape = '<path d="M11 1 L21 20 L1 20 Z" fill="' + color + '" stroke="white" stroke-width="2"/>';
    else if (status === 'rejected') shape = '<path d="M4 4 L18 18 M18 4 L4 18" fill="none" stroke="' + color + '" stroke-width="4"/>';
    else shape = '<circle cx="11" cy="11" r="8" fill="' + (status === 'control' ? 'white' : color) + '" stroke="' + (status === 'control' ? color : 'white') + '" stroke-width="3"/>';
    return L.divIcon({className:'feature-symbol', html:'<svg viewBox="0 0 22 22" width="22" height="22" aria-hidden="true">' + shape + '</svg>', iconSize:[22,22], iconAnchor:[11,11]});
  }
  function selectFeature(feature, move) {
    selected = feature.properties.id;
    const panel = document.getElementById('evidence-panel');
    panel.replaceChildren(element('h2', 'Selected evidence'), details(feature, false));
    renderList();
    const layer = featureLayers.get(selected);
    if (map && layer && move) {
      if (layer.getLatLng) map.setView(layer.getLatLng(), Math.max(map.getZoom(), 14));
      else if (layer.getBounds) map.fitBounds(layer.getBounds(), {padding:[45,45], maxZoom:16});
      layer.openPopup();
    }
  }
  function renderFeatures() {
    if (!map) { renderList(); updateProvenance(); return; }
    featureGroup.clearLayers();
    uncertaintyGroup.clearLayers();
    featureLayers = new Map();
    features.filter(visibleFeature).forEach(function (feature) {
      const p = feature.properties;
      const color = STATUS[p.status].color;
      const layer = L.geoJSON(feature, {
        pane:p.status === 'context' ? 'context' : 'features',
        style:{color:color, weight:p.status === 'context' ? 2 : 2.5, fillColor:color, fillOpacity:.17, dashArray:p.status === 'context' || p.status === 'rejected' ? '6 4' : undefined},
        pointToLayer:function (feature_, latlng) {
          return L.marker(latlng, {icon:symbol(p.status), pane:'features', title:(p.name || p.id) + ' · ' + STATUS[p.status].label, keyboard:true});
        },
        onEachFeature:function (feature_, leaf) {
          leaf.bindTooltip(element('span', p.name || p.id), {direction:'top'});
          leaf.bindPopup(function () { return details(feature, true); }, {maxWidth:370});
          leaf.on('click', function () { selectFeature(feature, false); });
        }
      });
      layer.addTo(featureGroup);
      const leaves = layer.getLayers();
      featureLayers.set(p.id, leaves.length === 1 ? leaves[0] : layer);
      if (uncertaintyToggle.checked && p.coordinate_uncertainty_m > 0 && feature.geometry.type === 'Point') {
        L.circle([feature.geometry.coordinates[1], feature.geometry.coordinates[0]], {
          radius:p.coordinate_uncertainty_m, color:color, fillOpacity:.03, weight:1, dashArray:'4 4', pane:'uncertainty'
        }).bindTooltip(element('span', p.id + ': analyst plotting buffer ' + p.coordinate_uncertainty_m + ' m')).addTo(uncertaintyGroup);
      }
    });
    renderList();
    if (selected && byId.has(selected) && visibleFeature(byId.get(selected))) {
      selectFeature(byId.get(selected), false);
    } else {
      selected = null;
      document.getElementById('evidence-panel').replaceChildren(
        element('h2', 'Selected evidence'), element('p', 'Select a mapped feature or an evidence record.', 'small-note'));
    }
  }
  function renderList() {
    const query = document.getElementById('feature-search').value.trim().toLowerCase();
    const visible = features.filter(visibleFeature).filter(function (feature) {
      return ((feature.properties.name || '') + ' ' + feature.properties.id).toLowerCase().includes(query);
    });
    const container = document.getElementById('feature-list');
    container.replaceChildren();
    visible.forEach(function (feature) {
      const p = feature.properties;
      const button = element('button', null, 'feature-button' + (p.id === selected ? ' selected' : ''));
      button.type = 'button';
      const glyph = element('span', STATUS[p.status].glyph, 'status-glyph');
      glyph.style.color = STATUS[p.status].color;
      button.appendChild(glyph);
      const text = element('span', p.name || p.id);
      text.appendChild(element('span', p.id, 'record-id'));
      button.appendChild(text);
      button.addEventListener('click', function () { selectFeature(feature, true); });
      container.appendChild(button);
    });
    document.getElementById('feature-count').textContent = visible.length + ' records in this selection';
    document.querySelectorAll('[data-status-count]').forEach(function (node) {
      node.textContent = features.filter(function (feature) {
        return (!feature.properties.block_id || blockMatches(feature.properties.block_id)) && feature.properties.status === node.dataset.statusCount;
      }).length;
    });
  }
  function updateBlockNote() {
    const selectedBlock = blocks.find(function (block) { return block.id === blockSelect.value; });
    document.getElementById('block-note').textContent = selectedBlock ?
      display(selectedBlock.region_ids) + ' · source EPSG:' + display(selectedBlock.native_epsg) :
      blocks.length + ' study blocks · local Natural Earth regional geography';
  }
  function fitBlock() {
    if (!map) return;
    if (blockSelect.value === 'all') {
      const total = L.latLngBounds([]);
      blocks.forEach(function (block) { total.extend(bounds(block.bbox_lonlat)); });
      map.fitBounds(total, {padding:[38,38]});
    } else {
      const block = blocks.find(function (item) { return item.id === blockSelect.value; });
      if (block) map.fitBounds(bounds(block.bbox_lonlat), {padding:[15,15], maxZoom:16});
    }
  }
  function updateBlock() {
    updateDates(); updateBlockNote(); renderImagery(); renderFeatures(); fitBlock();
  }
  blocks.forEach(function (block) {
    const option = element('option', block.id + ' · ' + block.name);
    option.value = block.id;
    blockSelect.appendChild(option);
  });
  const all = element('option', 'All study blocks');
  all.value = 'all';
  blockSelect.appendChild(all);
  const preferredBlock = blocks.find(function (block) {
    return block.id === 'B01' && overlays.some(function (overlay) { return overlay.block_id === block.id; });
  }) || blocks.find(function (block) {
    return overlays.some(function (overlay) { return overlay.block_id === block.id && overlay.kind === 'rgb'; });
  }) || blocks.find(function (block) {
    return overlays.some(function (overlay) { return overlay.block_id === block.id; });
  }) || blocks[0];
  blockSelect.value = preferredBlock.id;
  const filters = document.getElementById('status-filters');
  Object.keys(STATUS).filter(function (status) { return status !== 'context'; }).forEach(function (status) {
    const label = element('label', null, 'status-filter');
    const checkbox = element('input');
    checkbox.type = 'checkbox'; checkbox.checked = true; checkbox.dataset.status = status;
    const glyph = element('span', STATUS[status].glyph, 'status-glyph');
    glyph.style.color = STATUS[status].color;
    const count = element('span', '', 'status-count');
    count.dataset.statusCount = status;
    label.append(checkbox, glyph, element('span', STATUS[status].label), count);
    filters.appendChild(label);
    checkbox.addEventListener('change', function () {
      if (checkbox.checked) enabled.add(status); else enabled.delete(status);
      renderFeatures();
    });
  });
  const contextCount = features.filter(function (feature) { return feature.properties.status === 'context'; }).length;
  contextToggle.disabled = contextCount === 0;
  contextToggle.checked = contextCount > 0;
  document.getElementById('context-note').textContent = contextCount ?
    contextCount + ' supplied context records; dates and interpretations are in their popups.' :
    'No channel or palaeochannel linework was supplied.';
  if (window.L && geography) {
    map = L.map('map', {zoomControl:true, attributionControl:true, maxZoom:19, minZoom:2});
    [['geography',210], ['imagery',310], ['context',410], ['blocks',430], ['uncertainty',450], ['features',480]].forEach(function (entry) {
      map.createPane(entry[0]); map.getPane(entry[0]).style.zIndex = entry[1];
    });
    L.geoJSON(geography.countries, {pane:'geography', interactive:false, style:{color:'#b6c7c3', weight:.8, fillColor:'#eceee4', fillOpacity:1},
      attribution:'Made with <a href="https://www.naturalearthdata.com/about/terms-of-use/">Natural Earth</a> · public domain · 1:110m'}).addTo(map);
    L.geoJSON(geography.coastline, {pane:'geography', interactive:false, style:{color:'#809ea3', weight:1.1}}).addTo(map);
    countryLabels = L.layerGroup();
    geography.countries.features.forEach(function (country) {
      const p = country.properties;
      const lon = Number(p.LABEL_X), lat = Number(p.LABEL_Y);
      if (Number.isFinite(lon) && Number.isFinite(lat)) {
        const node = element('span', p.NAME_EN || p.NAME || p.ADMIN);
        L.marker([lat,lon], {icon:L.divIcon({className:'country-label', html:node, iconSize:[100,20], iconAnchor:[50,10]}), interactive:false, pane:'blocks'}).addTo(countryLabels);
      }
    });
    map.on('zoomend', function () {
      if (map.getZoom() <= 7) countryLabels.addTo(map); else if (map.hasLayer(countryLabels)) map.removeLayer(countryLabels);
    });
    featureGroup = L.layerGroup().addTo(map);
    uncertaintyGroup = L.layerGroup().addTo(map);
    blockGroup = L.layerGroup().addTo(map);
    blocks.forEach(function (block) {
      L.rectangle(bounds(block.bbox_lonlat), {pane:'blocks', color:'#416d59', weight:1.3, fill:false, dashArray:'5 4'})
        .bindTooltip(element('span', block.id + ' · ' + block.name), {permanent:true, direction:'top', className:'block-label'})
        .on('click', function () { blockSelect.value = block.id; updateBlock(); }).addTo(blockGroup);
    });
    L.control.scale({imperial:false}).addTo(map);
    const coordinateControl = L.control({position:'bottomleft'});
    let coordinateNode;
    coordinateControl.onAdd = function () {
      coordinateNode = element('div', '', 'map-coordinate');
      return coordinateNode;
    };
    coordinateControl.addTo(map);
    map.on('moveend', function () {
      const center = map.getCenter();
      coordinateNode.textContent = 'View centre: ' + center.lat.toFixed(5) + '°, ' + center.lng.toFixed(5) + '°';
    });
    osm = L.tileLayer(config.osm_tile_url, {
      maxZoom:19, pane:'geography', keepBuffer:0, updateWhenIdle:true, updateWhenZooming:false,
      attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · ODbL'
    });
    osm.on('tileerror', function () { document.getElementById('basemap-note').textContent = 'OSM tiles could not load. Local geography and imagery remain available.'; });
    window.ATLAS_MAP = map;
  } else {
    document.getElementById('map').hidden = true;
    document.getElementById('map-fallback').hidden = false;
  }
  function updateOsmAvailability() {
    const allowed = map && /^https?:$/.test(location.protocol) && navigator.onLine && !new URLSearchParams(location.search).has('offline');
    osmToggle.disabled = !allowed;
    if (!allowed) {
      osmToggle.checked = false;
      if (map && osm && map.hasLayer(osm)) map.removeLayer(osm);
    }
    document.getElementById('basemap-note').textContent = allowed ?
      'Local Natural Earth context. Enable OSM for live map detail.' :
      'Local imagery and Natural Earth context. Online OSM requires an HTTP view and network access.';
  }
  osmToggle.addEventListener('change', function () {
    if (osmToggle.checked && !osmToggle.disabled) {
      osm.addTo(map);
      document.getElementById('basemap-note').textContent = 'Live OSM context enabled. Adjust image opacity to compare layers.';
    } else {
      if (map && osm && map.hasLayer(osm)) map.removeLayer(osm);
      updateOsmAvailability();
    }
  });
  window.addEventListener('online', updateOsmAvailability);
  window.addEventListener('offline', updateOsmAvailability);
  blockSelect.addEventListener('change', updateBlock);
  document.getElementById('overview-button').addEventListener('click', function () { blockSelect.value = 'all'; updateBlock(); });
  kindSelect.addEventListener('change', function () { dateSelect.value = 'latest'; updateDates(); renderImagery(); if (selected) selectFeature(byId.get(selected), false); });
  dateSelect.addEventListener('change', function () { renderImagery(); if (selected) selectFeature(byId.get(selected), false); });
  opacity.addEventListener('input', function () {
    document.getElementById('opacity-value').textContent = opacity.value + '%';
    imagery.forEach(function (layer) { layer.setOpacity(Number(opacity.value) / 100); });
  });
  contextToggle.addEventListener('change', renderFeatures);
  uncertaintyToggle.addEventListener('change', renderFeatures);
  document.getElementById('feature-search').addEventListener('input', renderList);
  updateBlock(); updateOsmAvailability();
  window.ATLAS_VIEWER = {
    input:config.input_name,
    renderedOverlayIds:function () { return activeOverlays().map(function (overlay) { return overlay.id; }); },
    visibleFeatureIds:function () { return features.filter(visibleFeature).map(function (feature) { return feature.properties.id; }); },
    imageErrors:function () { return imageErrors.slice(); },
    osmEnabled:function () { return !!(map && osm && map.hasLayer(osm)); }
  };
})();
