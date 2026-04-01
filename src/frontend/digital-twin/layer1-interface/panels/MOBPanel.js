/**
 * MOB Panel - 落水告警面板
 *
 * 显示 MOB 状态、落水位置、经过时间、搜救模式。
 * 从 /api/mob/status 获取数据。
 */

export class MOBPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/mob/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('MOB data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const active = d.active ?? false;
    const lat = d.latitude ?? d.lat ?? '--';
    const lon = d.longitude ?? d.lon ?? '--';
    const elapsed = d.elapsed_minutes ?? d.elapsed ?? '--';
    const mode = d.search_mode ?? d.mode ?? 'N/A';
    const markers = d.marker_count ?? d.markers ?? 0;

    const statusColor = active ? '#f44336' : '#4caf50';
    const statusText = active ? 'ACTIVE' : 'STANDBY';
    const flash = active ? 'animation:mob-flash 1s infinite;' : '';

    this.container.innerHTML = `
      <style>
        @keyframes mob-flash {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      </style>
      <div style="width:300px;min-height:200px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px 0;font-size:15px;">🆘 Man Overboard</h3>

        <div style="text-align:center;margin-bottom:10px;">
          <div style="font-size:28px;font-weight:bold;color:${statusColor};${flash}">${statusText}</div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Latitude</div>
            <div style="font-weight:bold;">${typeof lat === 'number' ? lat.toFixed(5) : lat}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Longitude</div>
            <div style="font-weight:bold;">${typeof lon === 'number' ? lon.toFixed(5) : lon}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Elapsed</div>
            <div style="font-weight:bold;">${elapsed} min</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Markers</div>
            <div style="font-weight:bold;">${markers}</div>
          </div>
        </div>

        <div style="margin-top:8px;background:#111;border-radius:6px;padding:6px;font-size:12px;">
          <div style="color:#888;">Search Mode</div>
          <div style="font-weight:bold;">${mode}</div>
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
    console.log('🆘 MOB Panel initialized');
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
