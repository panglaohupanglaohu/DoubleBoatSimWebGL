/**
 * Comms Status Panel - 通信系统状态面板
 *
 * 显示各通信系统状态指示灯、GMDSS 合规状态、遇险模式指示。
 * 从 /api/comms/status 获取数据。
 */

export class CommsStatusPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/comms/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Comms status fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const systems = d.systems || [];
    const gmdssCompliant = d.gmdss_compliant ?? false;
    const distressMode = d.distress_mode ?? false;

    const statusColors = {
      operational: '#4caf50',
      degraded: '#ff9800',
      failed: '#f44336',
    };

    const gmdssColor = gmdssCompliant ? '#4caf50' : '#f44336';
    const distressColor = distressMode ? '#f44336' : '#4caf50';

    this.container.innerHTML = `
      <div style="width:300px;min-height:250px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="margin:0;font-size:15px;">📡 Communications</h3>
          ${distressMode ? '<span style="color:#f44336;font-size:11px;font-weight:bold;animation:blink 1s infinite;">⚠ DISTRESS</span>' : ''}
        </div>

        <!-- GMDSS status -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">GMDSS</div>
            <div style="font-size:13px;font-weight:bold;color:${gmdssColor}">${gmdssCompliant ? 'COMPLIANT' : 'NON-COMPLIANT'}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Distress Mode</div>
            <div style="font-size:13px;font-weight:bold;color:${distressColor}">${distressMode ? 'ACTIVE' : 'OFF'}</div>
          </div>
        </div>

        <!-- Systems list with status lights -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Systems (${systems.length})</div>
          <div style="max-height:140px;overflow-y:auto;font-size:12px;">
            ${systems.length
              ? systems.map(sys => {
                  const color = statusColors[sys.status] || '#888';
                  return `<div style="padding:4px 8px;margin-bottom:3px;background:#111;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:6px;">
                      <span style="width:8px;height:8px;border-radius:50%;background:${color};display:inline-block;"></span>
                      <span>${sys.name || sys.system_id || 'Unknown'}</span>
                    </div>
                    <span style="color:${color};font-size:11px;text-transform:uppercase;">${sys.status || 'unknown'}</span>
                  </div>`;
                }).join('')
              : this._renderDefaultSystems()}
          </div>
        </div>
      </div>
      <style>
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
      </style>
    `;
  }

  _renderDefaultSystems() {
    const defaults = ['VHF', 'MF/HF', 'Inmarsat-C', 'EPIRB', 'SART', 'Navtex'];
    return defaults.map(name =>
      `<div style="padding:4px 8px;margin-bottom:3px;background:#111;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="width:8px;height:8px;border-radius:50%;background:#666;display:inline-block;"></span>
          <span>${name}</span>
        </div>
        <span style="color:#666;font-size:11px;">N/A</span>
      </div>`
    ).join('');
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
    console.log('📡 Comms Status Panel initialized');
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
