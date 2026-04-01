/**
 * Tank Level Panel - 液舱水位面板
 *
 * 显示燃油总量/百分比、淡水总量、续航小时、低/高液位告警。
 * 从 /api/tanks/summary 和 /api/tanks/fuel-endurance 获取数据。
 */

export class TankLevelPanel {
  constructor(container) {
    this.container = container;
    this.summaryData = null;
    this.enduranceData = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const [summaryResp, enduranceResp] = await Promise.all([
        fetch('/api/tanks/summary'),
        fetch('/api/tanks/fuel-endurance'),
      ]);
      if (summaryResp.ok) {
        const json = await summaryResp.json();
        this.summaryData = json.result || json;
      }
      if (enduranceResp.ok) {
        const json = await enduranceResp.json();
        this.enduranceData = json.result || json;
      }
    } catch (e) {
      console.warn('Tank data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const s = this.summaryData || {};
    const e = this.enduranceData || {};
    const fuelTotal = s.fuel_total_m3 ?? 0;
    const fuelPct = s.fuel_percent ?? 0;
    const freshWater = s.fresh_water_m3 ?? 0;
    const enduranceHours = e.endurance_hours ?? 0;
    const lowAlarms = s.low_level_alarms || [];
    const highAlarms = s.high_level_alarms || [];

    const fuelColor = fuelPct > 50 ? '#4caf50' : fuelPct > 20 ? '#ff9800' : '#f44336';

    this.container.innerHTML = `
      <div style="width:320px;min-height:280px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px;font-size:15px;">🛢️ Tank Levels</h3>

        <!-- Fuel bar -->
        <div style="margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
            <span>Fuel: <b style="color:${fuelColor}">${typeof fuelTotal === 'number' ? fuelTotal.toFixed(1) : fuelTotal} m³</b></span>
            <span style="color:${fuelColor};font-weight:bold;">${typeof fuelPct === 'number' ? fuelPct.toFixed(1) : fuelPct}%</span>
          </div>
          <div style="background:#333;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:${Math.min(fuelPct, 100)}%;height:100%;background:${fuelColor};border-radius:4px;transition:width .3s;"></div>
          </div>
        </div>

        <!-- Stats grid -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Fresh Water</div>
            <div style="font-size:16px;font-weight:bold;">${typeof freshWater === 'number' ? freshWater.toFixed(1) : freshWater}<span style="font-size:11px;color:#888;"> m³</span></div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Endurance</div>
            <div style="font-size:16px;font-weight:bold;">${typeof enduranceHours === 'number' ? enduranceHours.toFixed(0) : enduranceHours}<span style="font-size:11px;color:#888;"> hrs</span></div>
          </div>
        </div>

        <!-- Low level alarms -->
        <div style="margin-bottom:8px;">
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Low Level Alarms (${lowAlarms.length})</div>
          <div style="max-height:50px;overflow-y:auto;font-size:12px;">
            ${lowAlarms.length
              ? lowAlarms.map(a => `<div style="padding:2px 6px;margin-bottom:2px;background:#3a1c1c;border-left:3px solid #f44336;border-radius:2px;">${a.tank_id || a}: ${a.level_percent != null ? a.level_percent.toFixed(1) + '%' : ''}</div>`).join('')
              : '<div style="color:#4caf50;">None</div>'}
          </div>
        </div>

        <!-- High level alarms -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">High Level Alarms (${highAlarms.length})</div>
          <div style="max-height:50px;overflow-y:auto;font-size:12px;">
            ${highAlarms.length
              ? highAlarms.map(a => `<div style="padding:2px 6px;margin-bottom:2px;background:#3a2a1a;border-left:3px solid #ff9800;border-radius:2px;">${a.tank_id || a}: ${a.level_percent != null ? a.level_percent.toFixed(1) + '%' : ''}</div>`).join('')
              : '<div style="color:#4caf50;">None</div>'}
          </div>
        </div>
      </div>
    `;
  }

  update(data) {
    if (data.summary) this.summaryData = data.summary;
    if (data.endurance) this.enduranceData = data.endurance;
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
    console.log('🛢️ Tank Level Panel initialized');
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
