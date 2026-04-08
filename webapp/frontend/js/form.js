/**
 * form.js — 表單邏輯、驗證、序列化、UI 狀態
 *
 * 依賴：
 *   window.PyVRP.api  （api.js）
 *   window.PyVRP.map  （map.js）
 */

/* ── 工具函式 ── */

/** "HH:MM" → 分鐘整數 */
function timeToMin(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

/** 分鐘整數 → "HH:MM" */
function minToTime(min) {
  const h = String(Math.floor(min / 60)).padStart(2, '0');
  const m = String(min % 60).padStart(2, '0');
  return `${h}:${m}`;
}

/** 產生唯一 ID（如 S001） */
let _storeSeq = 0;
function nextStoreId() { return `S${String(++_storeSeq).padStart(3, '0')}`; }
let _vtSeq = 0;
function nextVtId() { return ++_vtSeq; }

/* ── 驗證輔助 ── */

function setError(input, msg) {
  input.classList.add('error');
  const err = input.parentElement.querySelector('.err-msg');
  if (err) { err.textContent = msg || err.textContent; err.style.display = 'block'; }
}
function clearError(input) {
  input.classList.remove('error');
  const err = input.parentElement.querySelector('.err-msg');
  if (err) err.style.display = 'none';
}
function validateRange(input, min, max) {
  const v = parseFloat(input.value);
  if (isNaN(v) || v < min || v > max) { setError(input); return false; }
  clearError(input); return true;
}

/** 全域驗證：有任何 .error 元素就禁用送出按鈕 */
function refreshSolveBtn() {
  const hasError = document.querySelector('#panel-left input.error') !== null;
  const hasStores = document.querySelectorAll('.store-item').length > 0;
  const hasVts    = document.querySelectorAll('.vt-item').length > 0;
  const depotOk   = document.getElementById('depot-lat').value !== '' &&
                    document.getElementById('depot-lng').value !== '';
  document.getElementById('btn-solve').disabled = hasError || !hasStores || !hasVts || !depotOk;
}

/* ── 倉庫區塊 ── */

function initDepot() {
  const latEl  = document.getElementById('depot-lat');
  const lngEl  = document.getElementById('depot-lng');
  const twEnd  = document.getElementById('depot-tw-end');
  const twStart = document.getElementById('depot-tw-start');

  latEl.addEventListener('input', () => { validateRange(latEl, -90, 90); refreshSolveBtn(); });
  lngEl.addEventListener('input', () => { validateRange(lngEl, -180, 180); refreshSolveBtn(); });
  twEnd.addEventListener('change', () => {
    if (timeToMin(twEnd.value) <= timeToMin(twStart.value)) setError(twEnd, '結束需晚於開始');
    else clearError(twEnd);
    refreshSolveBtn();
  });
  twStart.addEventListener('change', () => { twEnd.dispatchEvent(new Event('change')); });
}

/* ── 店面動態列表 ── */

function createStoreCard(id, prefill = {}) {
  const div = document.createElement('div');
  div.className = 'item-card store-item';
  div.dataset.id = id;

  div.innerHTML = `
    <div class="item-header">
      <span class="item-name">店面 ${id}</span>
      <button class="del-btn" title="刪除">×</button>
    </div>
    <div class="item-body">
      <div class="field">
        <label>店面名稱</label>
        <input type="text" class="s-name" value="${prefill.name ?? ''}" placeholder="例：7-11 中正店" />
      </div>
      <div class="row-2">
        <div class="field">
          <label>緯度</label>
          <input type="number" class="s-lat" step="0.0001"
                 value="${prefill.lat ?? ''}" min="-90" max="90" placeholder="25.xxxx" />
          <span class="err-msg">緯度 -90~90</span>
        </div>
        <div class="field">
          <label>經度</label>
          <input type="number" class="s-lng" step="0.0001"
                 value="${prefill.lng ?? ''}" min="-180" max="180" placeholder="121.xxxx" />
          <span class="err-msg">經度 -180~180</span>
        </div>
      </div>
      <div class="row-2">
        <div class="field">
          <label>時間窗開始</label>
          <input type="time" class="s-tw-start" value="${prefill.twStart ?? '09:00'}" />
        </div>
        <div class="field">
          <label>時間窗結束</label>
          <input type="time" class="s-tw-end" value="${prefill.twEnd ?? '17:00'}" />
          <span class="err-msg">結束需晚於開始</span>
        </div>
      </div>
      <div class="row-2">
        <div class="field">
          <label>需求量</label>
          <input type="number" class="s-demand" value="${prefill.demand ?? 10}" min="0" />
          <span class="err-msg">需求量 ≥ 0</span>
        </div>
        <div class="field">
          <label>服務時長 (分)</label>
          <input type="number" class="s-service" value="${prefill.serviceMin ?? 10}" min="0" />
        </div>
      </div>
    </div>`;

  // 刪除
  div.querySelector('.del-btn').addEventListener('click', () => {
    div.remove();
    updateStoreCount();
    refreshSolveBtn();
  });

  // 驗證
  div.querySelector('.s-lat').addEventListener('input', e => { validateRange(e.target, -90, 90); refreshSolveBtn(); });
  div.querySelector('.s-lng').addEventListener('input', e => { validateRange(e.target, -180, 180); refreshSolveBtn(); });
  div.querySelector('.s-demand').addEventListener('input', e => { validateRange(e.target, 0, Infinity); refreshSolveBtn(); });

  const twS = div.querySelector('.s-tw-start');
  const twE = div.querySelector('.s-tw-end');
  const validateTw = () => {
    if (timeToMin(twE.value) <= timeToMin(twS.value)) setError(twE, '結束需晚於開始');
    else clearError(twE);
    refreshSolveBtn();
  };
  twS.addEventListener('change', validateTw);
  twE.addEventListener('change', validateTw);

  return div;
}

function updateStoreCount() {
  const n = document.querySelectorAll('.store-item').length;
  document.getElementById('store-count').textContent = n;
}

function addStore(prefill = {}) {
  const id = nextStoreId();
  const card = createStoreCard(id, prefill);
  document.getElementById('store-list').appendChild(card);
  updateStoreCount();
  refreshSolveBtn();
}

/* ── 車型動態列表 ── */

function createVtCard(prefill = {}) {
  const num = nextVtId();
  const div = document.createElement('div');
  div.className = 'item-card vt-item';

  div.innerHTML = `
    <div class="item-header">
      <span class="item-name">車型 ${num}</span>
      <button class="del-btn" title="刪除">×</button>
    </div>
    <div class="item-body">
      <div class="field">
        <label>車型名稱</label>
        <input type="text" class="vt-name" value="${prefill.name ?? `Vehicle Type ${num}`}" />
      </div>
      <div class="row-2">
        <div class="field">
          <label>載重上限</label>
          <input type="number" class="vt-cap" value="${prefill.capacity ?? 100}" min="1" />
          <span class="err-msg">容量 > 0</span>
        </div>
        <div class="field">
          <label>可用台數</label>
          <input type="number" class="vt-num" value="${prefill.num ?? 2}" min="1" />
          <span class="err-msg">台數 > 0</span>
        </div>
      </div>
    </div>`;

  div.querySelector('.del-btn').addEventListener('click', () => {
    div.remove();
    updateVtCount();
    refreshSolveBtn();
  });
  div.querySelector('.vt-cap').addEventListener('input', e => { validateRange(e.target, 1, Infinity); refreshSolveBtn(); });
  div.querySelector('.vt-num').addEventListener('input', e => { validateRange(e.target, 1, Infinity); refreshSolveBtn(); });

  return div;
}

function updateVtCount() {
  const n = document.querySelectorAll('.vt-item').length;
  document.getElementById('vt-count').textContent = n;
}

function addVehicleType(prefill = {}) {
  const card = createVtCard(prefill);
  document.getElementById('vt-list').appendChild(card);
  updateVtCount();
  refreshSolveBtn();
}

/* ── 序列化 ── */

function collectFormData() {
  // 倉庫
  const depot = {
    name: document.getElementById('depot-name').value.trim() || '倉庫',
    location: {
      lat: parseFloat(document.getElementById('depot-lat').value),
      lng: parseFloat(document.getElementById('depot-lng').value),
    },
    time_window: {
      start: timeToMin(document.getElementById('depot-tw-start').value),
      end:   timeToMin(document.getElementById('depot-tw-end').value),
    },
  };

  // 店面
  const stores = [...document.querySelectorAll('.store-item')].map(el => ({
    id:   el.dataset.id,
    name: el.querySelector('.s-name').value.trim() || el.dataset.id,
    location: {
      lat: parseFloat(el.querySelector('.s-lat').value),
      lng: parseFloat(el.querySelector('.s-lng').value),
    },
    time_window: {
      start: timeToMin(el.querySelector('.s-tw-start').value),
      end:   timeToMin(el.querySelector('.s-tw-end').value),
    },
    demand:          parseInt(el.querySelector('.s-demand').value) || 0,
    service_minutes: parseInt(el.querySelector('.s-service').value) || 0,
  }));

  // 車型
  const vehicle_types = [...document.querySelectorAll('.vt-item')].map(el => ({
    name:          el.querySelector('.vt-name').value.trim() || '車型',
    capacity:      parseInt(el.querySelector('.vt-cap').value),
    num_available: parseInt(el.querySelector('.vt-num').value),
  }));

  // 求解設定
  const config = {
    max_runtime_seconds: parseFloat(document.getElementById('cfg-runtime').value) || 10,
    avg_speed_kmh:       parseFloat(document.getElementById('cfg-speed').value)   || 40,
    seed:                parseInt(document.getElementById('cfg-seed').value)       ?? 42,
  };

  return { depot, stores, vehicle_types, config };
}

/* ── 填入範例資料 ── */

function fillForm(data) {
  // 倉庫
  document.getElementById('depot-name').value    = data.depot.name;
  document.getElementById('depot-lat').value     = data.depot.location.lat;
  document.getElementById('depot-lng').value     = data.depot.location.lng;
  document.getElementById('depot-tw-start').value = minToTime(data.depot.time_window.start);
  document.getElementById('depot-tw-end').value   = minToTime(data.depot.time_window.end);

  // 清除現有店面 / 車型
  document.getElementById('store-list').innerHTML = '';
  document.getElementById('vt-list').innerHTML    = '';
  _storeSeq = 0; _vtSeq = 0;

  // 店面
  data.stores.forEach(s => addStore({
    name:       s.name,
    lat:        s.location.lat,
    lng:        s.location.lng,
    twStart:    minToTime(s.time_window.start),
    twEnd:      minToTime(s.time_window.end),
    demand:     s.demand,
    serviceMin: s.service_minutes,
  }));

  // 車型
  data.vehicle_types.forEach(vt => addVehicleType({
    name:     vt.name,
    capacity: vt.capacity,
    num:      vt.num_available,
  }));

  // 求解設定
  if (data.config) {
    document.getElementById('cfg-runtime').value = data.config.max_runtime_seconds ?? 10;
    document.getElementById('cfg-speed').value   = data.config.avg_speed_kmh ?? 40;
    document.getElementById('cfg-seed').value    = data.config.seed ?? 42;
  }

  refreshSolveBtn();
}

/* ── 狀態列更新 ── */

function setFooter({ status, dist, vehicles, time } = {}) {
  const el = id => document.getElementById(id);
  if (status !== undefined) {
    el('ft-status').textContent = status.text;
    el('ft-status').className   = `stat-val ${status.cls}`;
  }
  if (dist     !== undefined) el('ft-dist').textContent     = dist;
  if (vehicles !== undefined) el('ft-vehicles').textContent = vehicles;
  if (time     !== undefined) el('ft-time').textContent     = time;
}

function showToast(msg, type = 'error') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className   = `show${type === 'warn' ? ' warn' : ''}`;
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.className = ''; }, 5000);
}

/* ── 求解主流程 ── */

async function onSolve() {
  const payload = collectFormData();

  // 顯示 loading
  document.getElementById('map-loading').classList.add('active');
  document.getElementById('btn-solve').disabled = true;
  setFooter({ status: { text: '求解中…', cls: 'idle' } });

  try {
    const result = await window.PyVRP.api.solve(payload);

    // 顯示警告（不可行解）
    if (!result.feasible) {
      showToast('找不到完全可行解，顯示最佳不可行解', 'warn');
    }

    // 更新地圖
    window.PyVRP.map.render(result, payload);

    // 更新右側面板
    renderResults(result);

    // 更新狀態列
    setFooter({
      status:   { text: result.feasible ? '求解完成 ✓' : '不可行解 ⚠', cls: result.feasible ? 'ok' : 'fail' },
      dist:     `${result.total_distance_km} km`,
      vehicles: `${result.num_routes_used} 台`,
      time:     `${result.runtime_seconds} 秒`,
    });

  } catch (err) {
    showToast(err.message ?? '求解失敗，請檢查輸入資料');
    setFooter({ status: { text: '求解失敗', cls: 'fail' } });
  } finally {
    document.getElementById('map-loading').classList.remove('active');
    refreshSolveBtn();
  }
}

/* ── 右側面板渲染 ── */

function minToTimeStr(min) {
  return minToTime(min);
}

function renderResults(result) {
  const scroll = document.getElementById('results-scroll');
  scroll.innerHTML = '';

  // 不可行橫幅
  if (!result.feasible) {
    const banner = document.createElement('div');
    banner.className = 'infeasible-banner';
    banner.textContent = '⚠ 在時限內未能找到完全可行解，以下為最佳不可行解';
    scroll.appendChild(banner);
  }

  result.routes.forEach(route => {
    const card = document.createElement('div');
    card.className = 'route-card';
    card.style.borderColor = route.color;
    card.dataset.vehicleIdx = route.vehicle_index;

    const loadPct = Math.round((route.total_load / route.capacity) * 100);

    card.innerHTML = `
      <div class="route-card-header" style="background:${route.color}18">
        <span class="color-dot" style="background:${route.color}"></span>
        🚚 ${route.vehicle_type} #${route.vehicle_index + 1}
      </div>
      <div class="route-stats">
        <span><b>${route.total_distance_km}</b> km</span>
        <span><b>${route.total_load}</b>/${route.capacity} 載重</span>
        <span><b>${loadPct}%</b> 滿載</span>
        <span><b>${route.total_duration_minutes}</b> 分</span>
      </div>
      <ul class="stop-list">
        ${route.stops.map((stop, i) => `
          <li class="stop-item${stop.store_id === 'depot' ? ' depot' : ''}">
            <span class="stop-num" style="background:${stop.store_id === 'depot' ? '#6c757d' : route.color}">
              ${stop.store_id === 'depot' ? '🏠' : i}
            </span>
            <div class="stop-info">
              <div class="stop-name">${stop.name}</div>
              <div class="stop-time">${minToTimeStr(stop.arrival_minutes)} 抵達 → ${minToTimeStr(stop.departure_minutes)} 離開</div>
              ${stop.wait_minutes > 0 ? `<div class="stop-wait">等待 ${stop.wait_minutes} 分</div>` : ''}
              ${i > 0 ? `<div class="stop-dist">距上站 ${stop.distance_from_prev_km} km</div>` : ''}
            </div>
          </li>`).join('')}
      </ul>`;

    // 點擊聯動地圖
    card.addEventListener('click', () => {
      document.querySelectorAll('.route-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      window.PyVRP.map.highlightRoute(route.vehicle_index, true);
    });

    scroll.appendChild(card);
  });
}

/* ── 重置（回首頁） ── */

function resetAll() {
  // 倉庫預設
  document.getElementById('depot-name').value     = '倉庫';
  document.getElementById('depot-lat').value      = '';
  document.getElementById('depot-lng').value      = '';
  document.getElementById('depot-tw-start').value = '08:00';
  document.getElementById('depot-tw-end').value   = '20:00';
  document.querySelectorAll('#depot-body input.error').forEach(el => clearError(el));

  // 清除店面、車型
  document.getElementById('store-list').innerHTML = '';
  document.getElementById('vt-list').innerHTML    = '';
  _storeSeq = 0; _vtSeq = 0;
  updateStoreCount();
  updateVtCount();

  // 求解設定預設
  document.getElementById('cfg-runtime').value = 10;
  document.getElementById('cfg-speed').value   = 40;
  document.getElementById('cfg-seed').value    = 42;

  // 右側結果面板
  const scroll = document.getElementById('results-scroll');
  scroll.innerHTML = '<div class="empty-state" id="results-empty"><div class="empty-icon">🗺️</div><p>填寫左側表單並點擊<br>「開始計算」，<br>路線規劃結果將顯示於此。</p></div>';

  // 狀態列
  setFooter({
    status:   { text: '待機', cls: 'idle' },
    dist:     '—',
    vehicles: '—',
    time:     '—',
  });

  // 清除地圖
  if (window.PyVRP.map?.clearAll) window.PyVRP.map.clearAll();

  // 還原所有 collapsed 狀態
  document.querySelectorAll('.section-card.collapsed').forEach(c => c.classList.remove('collapsed'));

  refreshSolveBtn();
}

/* ── 初始化 ── */

document.addEventListener('DOMContentLoaded', () => {
  initDepot();

  document.getElementById('btn-add-store').addEventListener('click', () => addStore());
  document.getElementById('btn-add-vt').addEventListener('click', () => addVehicleType());
  document.getElementById('btn-solve').addEventListener('click', onSolve);

  // Logo 回首頁
  document.getElementById('btn-home').addEventListener('click', () => {
    const hasData = document.querySelectorAll('.store-item').length > 0 ||
                    document.getElementById('depot-lat').value !== '';
    if (hasData) {
      if (!confirm('確定要清除所有資料並回到首頁？')) return;
    }
    resetAll();
  });

  // 區塊縮合
  document.querySelectorAll('.section-card .card-header').forEach(header => {
    header.addEventListener('click', e => {
      if (e.target.closest('.add-btn')) return; // 不攔截新增按鈕
      header.closest('.section-card').classList.toggle('collapsed');
    });
  });

  // 載入範例
  document.getElementById('btn-load-example').addEventListener('click', async () => {
    const hasData = document.querySelectorAll('.store-item').length > 0;
    if (hasData) {
      if (!confirm('載入範例將覆蓋現有資料，確定繼續？')) return;
    }
    try {
      const data = await window.PyVRP.api.loadExample();
      fillForm(data);
      // 通知地圖預覽位置
      if (window.PyVRP.map?.previewLocations) {
        window.PyVRP.map.previewLocations(data);
      }
    } catch {
      showToast('示範資料載入失敗');
    }
  });

  // 預設載入一個空店面和一個車型讓使用者感受到介面
  addVehicleType();
});
