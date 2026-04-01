/**
 * Rudder Panel - 舵机面板
 *
 * 显示舵角（图形化）、指令/实际舵角、SOLAS 合规、响应时间。
 * 从 /api/rudder/status 获取数据。
 */

export class RudderPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/rudder/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Rudder data fetch failed:', e);
    }
  }

  _renderRudderBar(commanded, actual) {
    const maxAngle = 35;
    const cmdPct = typeof commanded === 'number' ? (commanded / maxAngle) * 50 : 0;
    const actPct = typeof actual === 'number' ? (actual / maxAngle) * 50 : 0;

    const cmdLeft = commanded < 0 ? Math.abs(cmdPct) : 0;
    const cmdRight = commanded > 0 ? cmdPct : 0;
    const actLeft = actual < 0 ? Math.abs(actPct) : 0;
    const actRight = actual > 0 ? actPct : 0;

    return `
      <div style="position:relative;height:36px;background:#111;border-radius:4px;overflow:hidden;">
        <!-- center line -->
        <div style="position:absolute;left:50%;top:0;bottom:0;width:2px;background:#444;z-index:2;"></div>
        <!-- labels -->
        <div style="position:absolute;left:6px;top:2px;font-size:9px;color:#666;">PORT</div>
        <div style="position:absolute;right:6px;top:2px;font-size:9px;color:#666;">STBD</div>
        <!-- commanded (yellow) -->
        ${cmdLeft > 0 ? `<div style="position:absolute;right:50%;top:8px;height:10px;width:${cmdLeft}%;background:#ffeb3b;border-radius:2px 0 0 2px;"></div>` : ''}
        ${cmdRight > 0 ? `<div style="position:absolute;left:50%;top:8px;height:10px;width:${cmdRight}%;background:#ffeb3b;border-radius:0 2px 2px 0;"></div>` : ''}
        <!-- actual (cyan) -->
        ${actLeft > 0 ? `<div style="position:absolute;right:50%;top:20px;height:10px;width:${actLeft}%;background:#00bcd4;border-radius:2px 0 0 2px;"></div>` : ''}
        ${actRight > 0 ? `<div style="position:absolute;left:50%;top:20px;height:10px;width:${actRight}%;background:#00bcd4;border-radius:0 2px 2px 0;"></div>` : ''}
      </div>
      <div style="display:flex;justify-content:center;gap:12px;margin-top:4px;font-size:10px;">
        <span><span style="color:#ffeb3b;">■</span> Cmd</span>
        <span><span style="color:#00bcd4;">■</span> Actual</span>
      </div>
    `;
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const commanded = d.commanded_angle ?? d.commanded ?? null;
    const actual = d.actual_angle ?? d.actual ?? null;
    const solasOk = d.solas_compliant ?? d.solas ?? null;
    const responseTime = d.response_time ?? d.response ?? null;

    const solasColor = solasOk === true ? '#4caf50' : solasOk === false ? '#f44336' : '#888';
    const solasText = solasOk === true ? 'COMPLIANT' : solasOk === false ? 'NON-COMPLIANT' : '--';

    this.container.innerHTML = `
      <div style="width:280px;min-height:200px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px 0;font-size:15px;">⚓ Steering System</h3>

        <div style="margin-bottom:8px;">
          ${this._renderRudderBar(commanded, actual)}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Commanded</div>
            <div style="font-weight:bold;color:#ffeb3b;">${typeof commanded === 'number' ? commanded.toFixed(1) + '°' : '--'}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Actual</div>
            <div style="font-weight:bold;color:#00bcd4;">${typeof actual === 'number' ? actual.toFixed(1) + '°' : '--'}</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">SOLAS</div>
            <div style="font-weight:bold;color:${solasColor};">${solasText}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Response</div>
            <div style="font-weight:bold;">${typeof responseTime === 'number' ? responseTime.toFixed(1) + 's' : '--'}</div>
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
    console.log('⚓ Rudder Panel initialized');
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
