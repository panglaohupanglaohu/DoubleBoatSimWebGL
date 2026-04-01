/**
 * Power Management Panel - 电力管理面板
 *
 * 显示发电量、负载、储备功率、电池 SOC、发电机列表和燃油效率。
 * 每 3 秒从 /api/power/status 获取数据。
 */

export class PowerManagementPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
    this._blinkState = false;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/power/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Power management fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const totalGen = d.total_generation_kw ?? 0;
    const totalLoad = d.total_load_kw ?? 0;
    const reserveKw = d.reserve_kw ?? 0;
    const reservePct = d.reserve_percent ?? 0;
    const shedding = d.load_shedding_needed ?? false;
    const batterySoc = d.battery_soc_percent ?? 80;
    const generators = d.generators || [];
    const efficiencyRating = d.efficiency_rating ?? 'good';

    const reserveColor = reservePct > 30 ? '#4caf50' : reservePct > 15 ? '#ff9800' : '#f44336';
    this._blinkState = !this._blinkState;
    const sheddingStyle = shedding
      ? `color:#f44336;font-weight:bold;${this._blinkState ? 'opacity:1' : 'opacity:0.3'}`
      : 'color:#4caf50';

    this.container.innerHTML = `
      <div style="width:300px;min-height:280px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px;font-size:15px;">⚡ Power Management</h3>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Generation</div>
            <div style="font-size:16px;font-weight:bold;">${totalGen.toFixed(0)}<span style="font-size:11px;color:#888;"> kW</span></div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Load</div>
            <div style="font-size:16px;font-weight:bold;">${totalLoad.toFixed(0)}<span style="font-size:11px;color:#888;"> kW</span></div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Reserve</div>
            <div style="font-size:16px;font-weight:bold;color:${reserveColor}">${reserveKw.toFixed(0)} kW <span style="font-size:11px;">${reservePct.toFixed(1)}%</span></div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Battery SOC</div>
            <div style="font-size:16px;font-weight:bold;">${batterySoc.toFixed(0)}%</div>
          </div>
        </div>

        <!-- Reserve bar -->
        <div style="margin-bottom:8px;">
          <div style="background:#333;border-radius:4px;height:6px;overflow:hidden;">
            <div style="width:${Math.min(Math.max(reservePct, 0), 100)}%;height:100%;background:${reserveColor};border-radius:4px;transition:width .3s;"></div>
          </div>
        </div>

        <!-- Load shedding warning -->
        <div style="margin-bottom:8px;font-size:12px;${sheddingStyle}">
          ${shedding ? '⚠️ LOAD SHEDDING REQUIRED' : '✅ Power balance normal'}
        </div>

        <!-- Generators list -->
        <div style="margin-bottom:6px;">
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Generators (${generators.length})</div>
          <div style="max-height:80px;overflow-y:auto;font-size:12px;">
            ${generators.length
              ? generators.map(g => {
                  const statusIcon = g.status === 'running' ? '🟢' : g.status === 'standby' ? '🟡' : '🔴';
                  return `<div style="padding:2px 6px;margin-bottom:2px;background:#111;border-radius:2px;display:flex;justify-content:space-between;">
                    <span>${statusIcon} ${g.gen_id}</span><span>${g.current_kw?.toFixed(0) ?? 0} kW</span>
                  </div>`;
                }).join('')
              : '<div style="color:#666;">No generators</div>'}
          </div>
        </div>

        <!-- Efficiency -->
        <div style="font-size:12px;color:#888;">Fuel Efficiency: <b style="color:${efficiencyRating === 'good' ? '#4caf50' : efficiencyRating === 'acceptable' ? '#ff9800' : '#f44336'}">${efficiencyRating}</b></div>
      </div>
    `;
  }

  update(data) {
    this.data = data;
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
    console.log('⚡ Power Management Panel initialized');
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
