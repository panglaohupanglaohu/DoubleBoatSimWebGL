/**
 * Safety Panel - 安全系统面板
 *
 * 显示 SOLAS 就绪状态、水密完整性、系统计数、需检查列表。
 * 从 /api/safety/status 获取数据。
 */

export class SafetyPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/safety/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Safety data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const solasReady = d.solas_ready ?? d.solas ?? false;
    const watertight = d.watertight_integrity ?? d.watertight ?? false;
    const ready = d.ready_count ?? d.ready ?? 0;
    const notReady = d.not_ready_count ?? d.not_ready ?? 0;
    const faulty = d.faulty_count ?? d.faulty ?? 0;
    const checkList = d.check_required || d.needs_check || [];

    const solasColor = solasReady ? '#4caf50' : '#f44336';
    const solasText = solasReady ? 'READY' : 'NOT READY';
    const wtColor = watertight ? '#4caf50' : '#f44336';
    const wtText = watertight ? 'INTACT' : 'BREACH';

    this.container.innerHTML = `
      <div style="width:300px;min-height:250px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px 0;font-size:15px;">🛡️ Safety Systems</h3>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
          <div style="background:#111;border-radius:6px;padding:10px;text-align:center;">
            <div style="color:#888;font-size:10px;">SOLAS Status</div>
            <div style="font-size:20px;font-weight:bold;color:${solasColor};">${solasText}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:10px;text-align:center;">
            <div style="color:#888;font-size:10px;">Watertight</div>
            <div style="font-size:20px;font-weight:bold;color:${wtColor};">${wtText}</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:10px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #4caf50;">
            <div style="color:#888;font-size:10px;">Ready</div>
            <div style="font-size:16px;font-weight:bold;color:#4caf50;">${ready}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #ff9800;">
            <div style="color:#888;font-size:10px;">Not Ready</div>
            <div style="font-size:16px;font-weight:bold;color:#ff9800;">${notReady}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #f44336;">
            <div style="color:#888;font-size:10px;">Faulty</div>
            <div style="font-size:16px;font-weight:bold;color:#f44336;">${faulty}</div>
          </div>
        </div>

        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Needs Inspection (${checkList.length})</div>
          <div style="max-height:80px;overflow-y:auto;font-size:12px;">
            ${checkList.length
              ? checkList.map(item => `<div style="padding:3px 6px;margin-bottom:2px;background:#111;border-left:3px solid #ff9800;border-radius:2px;">${typeof item === 'string' ? item : item.name || '--'}</div>`).join('')
              : '<div style="color:#4caf50;text-align:center;padding:6px;">All systems OK</div>'}
          </div>
        </div>
      </div>
    `;
  }

  update(data) {
    if (data) this.data = data;
    this.render();
  }

  async refresh() {
    await this.fetchData();
    this.render();
  }

  async initialize() {
    await this.fetchData();
    this.render();
    this.startAutoRefresh(3000);
    console.log('🛡️ Safety Panel initialized');
  }

  startAutoRefresh(intervalMs = 3000) {
    this.stopAutoRefresh();
    this._refreshTimer = setInterval(() => this.refresh(), intervalMs);
  }

  stopAutoRefresh() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
      this._refreshTimer = null;
    }
  }
}
