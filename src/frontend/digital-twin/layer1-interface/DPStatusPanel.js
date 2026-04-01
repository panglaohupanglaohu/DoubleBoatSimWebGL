/**
 * DP Status Panel - 动态定位状态面板
 *
 * 显示 DP 模式、目标站位、当前位置、偏移距离和推进器状态。
 * 每 3 秒从 /api/dp/status 获取数据。
 */

export class DPStatusPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/dp/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('DP status fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const dpMode = d.dp_mode ?? 'standby';
    const station = d.station || null;
    const pos = d.current_position || { lat: 0, lon: 0 };
    const excursion = d.excursion_m ?? 0;
    const limit = d.excursion_limit_m ?? 25;
    const thrusters = d.thrusters || [];

    const overLimit = excursion > limit;
    const excursionColor = overLimit ? '#f44336' : excursion > limit * 0.7 ? '#ff9800' : '#4caf50';
    const modeColors = { standby: '#90a4ae', station_keeping: '#4caf50', transit: '#2196f3' };
    const modeColor = modeColors[dpMode] || '#90a4ae';

    this.container.innerHTML = `
      <div style="width:300px;min-height:250px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px;font-size:15px;">📍 Dynamic Positioning</h3>

        <!-- Mode -->
        <div style="margin-bottom:10px;text-align:center;">
          <span style="display:inline-block;padding:4px 14px;border-radius:12px;background:${modeColor}22;color:${modeColor};font-weight:bold;font-size:13px;border:1px solid ${modeColor};">${dpMode.replace('_', ' ').toUpperCase()}</span>
        </div>

        <!-- Positions -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">
          <div style="background:#111;border-radius:6px;padding:8px;">
            <div style="font-size:11px;color:#888;">Target Station</div>
            <div style="font-size:12px;font-weight:bold;">${station ? `${station.lat.toFixed(4)}, ${station.lon.toFixed(4)}` : '-- not set --'}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;">
            <div style="font-size:11px;color:#888;">Current Position</div>
            <div style="font-size:12px;font-weight:bold;">${pos.lat.toFixed(4)}, ${pos.lon.toFixed(4)}</div>
          </div>
        </div>

        <!-- Excursion -->
        <div style="margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
            <span>Offset: <b style="color:${excursionColor}">${excursion.toFixed(1)} m</b></span>
            <span style="color:#888;">Limit: ${limit} m</span>
          </div>
          <div style="background:#333;border-radius:4px;height:6px;overflow:hidden;">
            <div style="width:${Math.min(excursion / limit * 100, 100)}%;height:100%;background:${excursionColor};border-radius:4px;transition:width .3s;"></div>
          </div>
          ${overLimit ? '<div style="color:#f44336;font-size:11px;font-weight:bold;margin-top:3px;">⚠️ EXCURSION OVER LIMIT</div>' : ''}
        </div>

        <!-- Thrusters -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Thrusters (${thrusters.length})</div>
          <div style="max-height:70px;overflow-y:auto;font-size:12px;">
            ${thrusters.length
              ? thrusters.map(t => {
                  const pct = t.thrust_pct ?? 0;
                  const tColor = pct > 80 ? '#f44336' : pct > 40 ? '#ff9800' : '#4caf50';
                  return `<div style="padding:2px 6px;margin-bottom:2px;background:#111;border-radius:2px;display:flex;justify-content:space-between;">
                    <span>${t.id}</span><span style="color:${tColor}">${pct.toFixed(0)}%</span>
                  </div>`;
                }).join('')
              : '<div style="color:#666;">No thrusters</div>'}
          </div>
        </div>
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
    console.log('📍 DP Status Panel initialized');
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
