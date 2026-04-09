/**
 * map.js — Leaflet 地圖視覺化
 *
 * 對外暴露 window.PyVRP.map：
 *   render(result, request)          渲染求解結果
 *   previewLocations(requestData)    預覽表單地點（未求解前）
 *   highlightRoute(vehicleIndex)     高亮某條路線
 */

window.PyVRP = window.PyVRP || {};

window.PyVRP.map = (() => {

  /* ── 顏色 palette（與 serializer.py 相同順序） ── */
  const PALETTE = [
    '#FF0033', '#FF6600', '#FFCC00', '#00FF88', '#00CCFF',
    '#CC00FF', '#FF0099', '#00FFEE', '#AAFF00', '#FF4400',
  ];
  const color = idx => PALETTE[idx % PALETTE.length];

  /* ── Leaflet 初始化 ── */
  const map = L.map('map', {
    center: [25.0478, 121.5170],   // 台北車站
    zoom: 12,
    zoomControl: true,
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> © <a href="https://carto.com/">CARTO</a>',
    maxZoom: 19,
  }).addTo(map);

  /* ── 圖層管理（一次 clearLayers 清空所有） ── */
  const depotLayer  = L.layerGroup().addTo(map);
  const storeLayer  = L.layerGroup().addTo(map);
  const routeLayer  = L.layerGroup().addTo(map);
  const arrowLayer  = L.layerGroup().addTo(map);
  const previewLayer = L.layerGroup().addTo(map);

  /* 保留路線折線引用，供 highlightRoute 操作 */
  let _polylines = [];   // [{ vehicleIdx, polyline }]
  let _activeIdx = null;

  /* ── 自訂圖示工廠 ── */

  function depotIcon() {
    return L.divIcon({
      className: '',
      html: `<div style="
        width:36px; height:36px;
        background:#E63946; border-radius:50% 50% 50% 0;
        transform:rotate(-45deg);
        display:flex; align-items:center; justify-content:center;
        box-shadow:0 2px 8px rgba(0,0,0,.25);
        border:2px solid white;
      "><span style="transform:rotate(45deg); font-size:16px;">🏠</span></div>`,
      iconSize:   [36, 36],
      iconAnchor: [18, 36],
      popupAnchor:[0, -38],
    });
  }

  function storeIcon(num, clr) {
    return L.divIcon({
      className: '',
      html: `<div style="
        width:30px; height:30px;
        background:${clr}; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        color:white; font-size:12px; font-weight:800;
        box-shadow:0 0 0 3px white, 0 0 10px 2px ${clr}99, 0 2px 6px rgba(0,0,0,.2);
        border:none;
        font-family:Inter,sans-serif;
        text-shadow:0 1px 2px rgba(0,0,0,.3);
      ">${num}</div>`,
      iconSize:   [30, 30],
      iconAnchor: [15, 15],
      popupAnchor:[0, -18],
    });
  }

  function grayIcon(label) {
    return L.divIcon({
      className: '',
      html: `<div style="
        width:28px; height:28px;
        background:#adb5bd; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        color:white; font-size:10px; font-weight:700;
        box-shadow:0 2px 6px rgba(0,0,0,.2);
        border:2px dashed white;
        font-family:Inter,sans-serif;
      ">${label}</div>`,
      iconSize:   [28, 28],
      iconAnchor: [14, 14],
    });
  }

  /* ── 分鐘 → HH:MM ── */
  function minToHHMM(min) {
    const h = String(Math.floor(min / 60)).padStart(2, '0');
    const m = String(min % 60).padStart(2, '0');
    return `${h}:${m}`;
  }

  /* ── 清空所有圖層 ── */
  function clearAll() {
    depotLayer.clearLayers();
    storeLayer.clearLayers();
    routeLayer.clearLayers();
    arrowLayer.clearLayers();
    previewLayer.clearLayers();
    _polylines = [];
    _activeIdx = null;
  }

  /* ── 倉庫 Marker ── */
  function renderDepot(depot) {
    const { lat, lng } = depot.location;
    const marker = L.marker([lat, lng], { icon: depotIcon(), zIndexOffset: 1000 });
    marker.bindPopup(`
      <b>${depot.name}</b><br>
      開放時間：${minToHHMM(depot.time_window.start)} – ${minToHHMM(depot.time_window.end)}
    `);
    depotLayer.addLayer(marker);
  }

  /* ── 店面 Marker ── */
  /* hex #RRGGBB → rgba 字串 */
  function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  }

  /* 閃爍指定 card，用路線顏色 */
  function flashCard(vehicleIdx, clr) {
    const card = document.querySelector(`.route-card[data-vehicle-idx="${vehicleIdx}"]`);
    if (!card) return;
    document.querySelectorAll('.route-card').forEach(c => c.classList.remove('active', 'flash'));
    card.classList.add('active');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    card.style.setProperty('--flash-color', hexToRgba(clr, 0.28));
    void card.offsetWidth;
    card.classList.add('flash');
  }

  function renderStoreMarker(stop, orderNum, clr, vehicleIdx) {
    if (stop.store_id === 'depot') return;
    const { lat, lng } = stop.location;
    const marker = L.marker([lat, lng], { icon: storeIcon(orderNum, clr) });

    const waitStr = stop.wait_minutes > 0
      ? `<br>⏳ 等待 ${stop.wait_minutes} 分`
      : '';
    marker.bindPopup(`
      <b>${stop.name}</b><br>
      抵達：${minToHHMM(stop.arrival_minutes)}<br>
      離開：${minToHHMM(stop.departure_minutes)}
      ${waitStr}<br>
      距上站：${stop.distance_from_prev_km} km
    `);

    // 點擊節點 = 點擊所屬路線
    marker.on('click', (e) => {
      L.DomEvent.stopPropagation(e);
      highlightRoute(vehicleIdx);
      flashCard(vehicleIdx, clr);
    });

    storeLayer.addLayer(marker);
  }

  /* ── 路線折線 + 方向箭頭 ── */
  function renderPolyline(route) {
    const clr    = route.color;
    const coords = route.stops.map(s => [s.location.lat, s.location.lng]);

    // 路線實線
    const poly = L.polyline(coords, {
      color:   clr,
      weight:  4,
      opacity: 0.85,
    });

    // 點擊路線：聚焦此路線 + 右側面板錨定並閃爍
    poly.on('click', (e) => {
      L.DomEvent.stopPropagation(e);
      highlightRoute(route.vehicle_index);
      flashCard(route.vehicle_index, clr);
    });

    routeLayer.addLayer(poly);
    _polylines.push({ vehicleIdx: route.vehicle_index, polyline: poly });

    // 在每段線段的中點加箭頭
    for (let i = 0; i < coords.length - 1; i++) {
      const [lat1, lng1] = coords[i];
      const [lat2, lng2] = coords[i + 1];
      const midLat = (lat1 + lat2) / 2;
      const midLng = (lng1 + lng2) / 2;

      // 方向角（度）
      const angle = Math.atan2(lat2 - lat1, lng2 - lng1) * (180 / Math.PI);

      const arrowIcon = L.divIcon({
        className: '',
        html: `<div style="
          width:10px; height:10px;
          transform:rotate(${-angle + 90}deg);
          color:${clr}; font-size:12px; line-height:1;
          text-shadow:0 0 2px white;
        ">▲</div>`,
        iconSize:   [10, 10],
        iconAnchor: [5, 5],
      });
      arrowLayer.addLayer(L.marker([midLat, midLng], { icon: arrowIcon, interactive: false }));
    }
  }

  /* ── 高亮 / 重置 ── */
  function highlightRoute(vehicleIdx, fitView = false) {
    _activeIdx = vehicleIdx;
    _polylines.forEach(({ vehicleIdx: vi, polyline }) => {
      polyline.setStyle(vi === vehicleIdx
        ? { weight: 5, opacity: 1 }
        : { weight: 4, opacity: 0.2 }
      );
      if (vi === vehicleIdx) polyline.bringToFront();
    });

    if (fitView) {
      const target = _polylines.find(p => p.vehicleIdx === vehicleIdx);
      if (target) map.fitBounds(target.polyline.getBounds(), { padding: [40, 40] });
    }
  }

  function resetHighlight() {
    _activeIdx = null;
    _polylines.forEach(({ polyline }) => {
      polyline.setStyle({ weight: 4, opacity: 0.85 });
    });
  }

  // 點擊地圖空白處恢復所有路線
  map.on('click', () => {
    resetHighlight();
    document.querySelectorAll('.route-card').forEach(c => c.classList.remove('active', 'flash'));
  });

  /* ── fitBounds ── */
  function fitAll(latLngs) {
    if (!latLngs.length) return;
    const bounds = L.latLngBounds(latLngs);
    map.fitBounds(bounds, { padding: [50, 50] });
  }

  /* ── 主渲染入口 ── */
  function render(result, request) {
    clearAll();

    const allLatLngs = [];

    // 倉庫
    renderDepot(request.depot);
    allLatLngs.push([request.depot.location.lat, request.depot.location.lng]);

    // 找出被服務的店面 ID 集合（用於顯示未服務的灰色點）
    const servedIds = new Set();
    result.routes.forEach(route => {
      route.stops.forEach(s => { if (s.store_id !== 'depot') servedIds.add(s.store_id); });
    });

    // 路線（折線 + 店面 markers）
    result.routes.forEach(route => {
      renderPolyline(route);

      // 中途站（跳過起訖倉庫）
      let order = 1;
      route.stops.forEach(stop => {
        if (stop.store_id === 'depot') return;
        renderStoreMarker(stop, order++, route.color, route.vehicle_index);
        allLatLngs.push([stop.location.lat, stop.location.lng]);
      });
    });

    // 未被服務的店面（不可行解時可能有）
    request.stores.forEach((store, i) => {
      if (!servedIds.has(store.id)) {
        const marker = L.marker(
          [store.location.lat, store.location.lng],
          { icon: grayIcon(i + 1) }
        );
        marker.bindPopup(`<b>${store.name}</b><br><i style="color:#adb5bd">未被服務</i>`);
        storeLayer.addLayer(marker);
        allLatLngs.push([store.location.lat, store.location.lng]);
      }
    });

    fitAll(allLatLngs);
  }

  /* ── 預覽（未求解時，只放倉庫＋店面圓點） ── */
  function previewLocations(data) {
    previewLayer.clearLayers();
    const allLatLngs = [];

    const { lat: dLat, lng: dLng } = data.depot.location;
    if (dLat && dLng) {
      L.marker([dLat, dLng], { icon: depotIcon() })
        .bindPopup(data.depot.name)
        .addTo(previewLayer);
      allLatLngs.push([dLat, dLng]);
    }

    data.stores.forEach((s, i) => {
      const { lat, lng } = s.location;
      if (lat && lng) {
        L.marker([lat, lng], { icon: storeIcon(i + 1, '#2E86AB') })
          .bindPopup(s.name)
          .addTo(previewLayer);
        allLatLngs.push([lat, lng]);
      }
    });

    fitAll(allLatLngs);
  }

  /* ── 公開介面 ── */
  return { render, previewLocations, highlightRoute, clearAll };

})();
