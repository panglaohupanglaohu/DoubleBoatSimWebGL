/**
 * Autopilot Panel - 自动舵面板
 *
 * 显示自动舵模式、航向、偏航距离、在航状态。
 * 从 /api/autopilot/status 获取数据。
 */

export class AutopilotPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/autopilot/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Autopilot data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const mode = d.mode ?? 'STANDBY';
    const setHeading = d.set_heading ?? d.heading_set ?? '--';
    const actualHeading = d.actual_heading ?? d.heading ?? '--';
    const deviation = d.deviation ?? d.heading_error ?? '--';
    const xte = d.xte ?? d.cross_track_error ?? '--';
    const onCourse = d.on_course ?? d.course_ok ?? null;

    const modeColors = {
      STANDBY: '#888',
      HEADING_HOLD: '#2196f3',
      TRACK: '#4caf50',
    };
    const modeColor = modeColors[mode] || '#888';

    const courseColor = onCourse === true ? '#4caf50' : onCourse === false ? '#f44336' : '#888';
    const courseText = onCourse === true ? 'ON COURSE' : onCourse === false ? 'OFF COURSE' : '--';

    this.container.innerHTML = `
      <div style="width:300px;min-height:220px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <h3 style="margin:0 0 10px 0;font-size:15px;">🧭 Autopilot</h3>

        <div style="text-align:center;margin-bottom:10px;">
          <div style="display:inline-block;padding:6px 18px;border-radius:6px;background:#111;border:2px solid ${modeColor};">
            <span style="font-size:16px;font-weight:bold;color:${modeColor};">${mode}</span>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;font-size:12px;">
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Set Heading</div>
            <div style="font-weight:bold;font-size:16px;">${typeof setHeading === 'number' ? setHeading.toFixed(1) + '°' : setHeading}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Actual Heading</div>
            <div style="font-weight:bold;font-size:16px;">${typeof actualHeading === 'number' ? actualHeading.toFixed(1) + '°' : actualHeading}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">Deviation</div>
            <div style="font-weight:bold;">${typeof deviation === 'number' ? deviation.toFixed(1) + '°' : deviation}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;">
            <div style="color:#888;">XTE</div>
            <div style="font-weight:bold;">${typeof xte === 'number' ? xte.toFixed(1) + ' m' : xte}</div>
          </div>
        </div>

        <div style="text-align:center;background:#111;border-radius:6px;padding:8px;">
          <span style="font-size:14px;font-weight:bold;color:${courseColor};">${courseText}</span>
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
    console.log('🧭 Autopilot Panel initialized');
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
