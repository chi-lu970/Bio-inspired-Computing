/**
 * api.js — 後端 API 呼叫封裝
 *
 * 對外暴露：
 *   window.PyVRP.api.solve(payload)  → Promise<SolveResponse>
 *   window.PyVRP.api.loadExample()   → Promise<SolveRequest>
 */

const BASE = '';  // 同源，不需要 prefix

window.PyVRP = window.PyVRP || {};
window.PyVRP.api = {

  /**
   * POST /api/solve
   * @param {object} payload — 符合 SolveRequest schema 的物件
   * @returns {Promise<object>} SolveResponse
   * @throws {object} { status, code, message }
   */
  // 目前進行中的 AbortController（供取消用）
  _currentController: null,

  async solve(payload) {
    // 取消上一個還在等待的請求（避免堆積）
    if (this._currentController) {
      this._currentController.abort();
    }
    const controller = new AbortController();
    this._currentController = controller;

    // 前端 timeout：max_runtime_seconds 的 3 倍作為最後保險
    // 正常情況由後端 TimedNoImprovement 控制停止，不應觸發到這裡
    const frontendTimeout = (payload.config?.max_runtime_seconds ?? 10) * 3 + 10;
    const timer = setTimeout(() => controller.abort(), frontendTimeout * 1000);

    let resp;
    try {
      resp = await fetch(`${BASE}/api/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (err) {
      if (err.name === 'AbortError') {
        throw {
          status: 0,
          code: 'client_timeout',
          message: `前端等待逾時（${frontendTimeout} 秒），請縮短最大運算時間或減少店面數量後重試。`,
        };
      }
      throw err;
    } finally {
      clearTimeout(timer);
      if (this._currentController === controller) {
        this._currentController = null;
      }
    }

    const data = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      // FastAPI 的 detail 可能是物件（自訂 ErrorResponse）或字串
      const detail = data.detail ?? data;
      throw {
        status: resp.status,
        code: detail.error ?? 'unknown_error',
        message: detail.message ?? `HTTP ${resp.status} 錯誤`,
      };
    }
    return data;
  },

  /** 取消目前正在等待的求解請求 */
  cancelSolve() {
    if (this._currentController) {
      this._currentController.abort();
      this._currentController = null;
    }
  },

  /**
   * 載入示範資料 JSON
   * @returns {Promise<object>} SolveRequest 格式的範例物件
   */
  async loadExample(filename = 'taipei_demo.json') {
    const resp = await fetch(`/examples/${filename}`);
    if (!resp.ok) throw new Error('示範資料載入失敗');
    return resp.json();
  },
};
