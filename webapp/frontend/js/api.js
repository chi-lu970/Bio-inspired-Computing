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
  async solve(payload) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 90000);
    let resp;
    try {
      resp = await fetch(`${BASE}/api/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timer);
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
