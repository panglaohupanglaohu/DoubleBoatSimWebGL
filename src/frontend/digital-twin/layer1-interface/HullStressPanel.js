/**
 * Hull Stress Panel - 船体应力监测面板
 *
 * 显示结构健康度评分、最大应力、传感器数和 hotspot 列表。
 * 每 3 秒从 /api/hull/status 获取数据。
 */

export class HullStressPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/hull/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Hull stress fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const health = d.health_score ?? 100;
    const maxStress = d.max_stress ?? 0;
    const stressRatio = d.stress_ratio ?? 0;
    const hotspots = d.hotspots || [];
    const alarm = d.alarm_active ?? false;
    const sensorCount = d.sensor_count ?? hotspots.length;

    const color = health > 80 ? '#4caf50' : health > 60 ? '#ff9800' : '#f44336';
    const alarmColor = alarm ? '#f44336' : '#4caf50';

    this.container.innerHTML = `
      <div style="width:300px;min-height:250px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="margin:0;font-size:15px;">🔩 Hull Stress Monitor</h3>
          <span style="width:10px;height:10px;border-radius:50%;background:${alarmColor};display:inline-block;" title="Alarm: ${alarm ? 'ACTIVE' : 'OK'}"></span>
        </div>

        <!-- Health bar -->
        <div style="margin-bottom:8px;">
          <div style="font-size:12px;margin-bottom:3px;">Health: <b style="color:${color}">${health.toFixed(1)}%</b></div>
          <div style="background:#333;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:${Math.min(health, 100)}%;height:100%;background:${color};border-radius:4px;transition:width .3s;"></div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Max Stress</div>
            <div style="font-size:16px;font-weight:bold;">${maxStress.toFixed(1)}<span style="font-size:11px;color:#888;"> MPa</span></div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Stress Ratio</div>
            <div style="font-size:16px;font-weight:bold;">${(stressRatio * 100).toFixed(1)}%</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Sensors</div>
            <div style="font-size:16px;font-weight:bold;">${sensorCount}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Alarm</div>
            <div style="font-size:16px;font-weight:bold;color:${alarmColor}">${alarm ? 'ACTIVE' : 'OK'}</div>
          </div>
        </div>

        <!-- Hotspots -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Hotspots (${hotspots.length})</div>
          <div style="max-height:60px;overflow-y:auto;font-size:12px;">
            ${hotspots.length
              ? hotspots.map(h => `<div style="padding:2px 6px;margin-bottom:2px;background:#3a1c1c;border-left:3px solid #f44336;border-radius:2px;">${h}</div>`).join('')
              : '<div style="color:#666;">No hotspots</div>'}
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
    console.log('🔩 Hull Stress Panel initialized');
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
