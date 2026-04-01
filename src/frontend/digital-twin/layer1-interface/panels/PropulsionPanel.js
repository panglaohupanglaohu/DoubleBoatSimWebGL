/**
 * Propulsion Panel - 推进系统面板
 *
 * 显示主机列表、推进器列表、总功率/推力、效率。
 * 从 /api/propulsion/status 获取数据。
 */

export class PropulsionPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/propulsion/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Propulsion data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const engines = d.engines || [];
    const thrusters = d.thrusters || [];
    const totalPower = d.total_power ?? '--';
    const totalThrust = d.total_thrust ?? '--';
    const efficiency = d.efficiency ?? '--';

    const engineRows = engines.length
      ? engines.map(e => {
          const pct = e.rated_power ? Math.round((e.power / e.rated_power) * 100) : 0;
          const statusColor = e.status === 'running' ? '#4caf50' : e.status === 'standby' ? '#ffeb3b' : '#f44336';
          return `<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
            <span style="width:8px;height:8px;border-radius:50%;background:${statusColor};flex-shrink:0;"></span>
            <span style="width:50px;font-size:11px;">${e.id || e.name || '--'}</span>
            <div style="flex:1;background:#222;border-radius:3px;height:12px;overflow:hidden;">
              <div style="width:${pct}%;height:100%;background:${pct > 90 ? '#f44336' : pct > 70 ? '#ff9800' : '#4caf50'};border-radius:3px;"></div>
            </div>
            <span style="font-size:11px;width:36px;text-align:right;">${pct}%</span>
          </div>`;
        }).join('')
      : '<div style="color:#666;font-size:12px;">No engine data</div>';

    const thrusterRows = thrusters.length
      ? thrusters.map(t => {
          return `<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px;">
            <span>${t.id || t.name || '--'}</span>
            <span>${t.thrust ?? '--'} kN</span>
          </div>`;
        }).join('')
      : '<div style="color:#666;font-size:12px;">No thruster data</div>';

    this.container.innerHTML = `
      <div style="width:320px;min-height:300px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px 0;font-size:15px;">🚢 Propulsion System</h3>

        <div style="font-size:12px;color:#888;margin-bottom:4px;">Engines</div>
        <div style="background:#111;border-radius:6px;padding:8px;margin-bottom:8px;">
          ${engineRows}
        </div>

        <div style="font-size:12px;color:#888;margin-bottom:4px;">Thrusters</div>
        <div style="background:#111;border-radius:6px;padding:8px;margin-bottom:8px;">
          ${thrusterRows}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;">
            <div style="color:#888;font-size:10px;">Total Power</div>
            <div style="font-weight:bold;">${totalPower} kW</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;">
            <div style="color:#888;font-size:10px;">Total Thrust</div>
            <div style="font-weight:bold;">${totalThrust} kN</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;">
            <div style="color:#888;font-size:10px;">Efficiency</div>
            <div style="font-weight:bold;color:${typeof efficiency === 'number' && efficiency >= 80 ? '#4caf50' : '#ff9800'};">${typeof efficiency === 'number' ? efficiency + '%' : efficiency}</div>
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
    console.log('🚢 Propulsion Panel initialized');
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
