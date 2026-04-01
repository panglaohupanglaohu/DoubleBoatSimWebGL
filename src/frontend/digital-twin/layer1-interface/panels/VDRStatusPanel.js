/**
 * VDR Status Panel - VDR (航行数据记录仪) 状态面板
 *
 * 显示录制状态、缓冲大小、数据覆盖率、记录时间范围和数据完整性。
 * 每 3 秒从 /api/vdr/status 获取数据。
 */

export class VDRStatusPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/vdr/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('VDR status fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const d = this.data || {};
    const recording = d.recording ?? false;
    const bufferSize = d.buffer_size_mb ?? 0;
    const coveragePct = d.coverage_percent ?? 0;
    const oldestRecord = d.oldest_record ?? '--';
    const newestRecord = d.newest_record ?? '--';
    const missingItems = d.missing_items ?? [];

    // 数据完整性: 0 missing=green, 1-2=yellow, 3+=red
    const integrityColor = missingItems.length === 0
      ? '#4caf50'
      : missingItems.length <= 2 ? '#ff9800' : '#f44336';
    const integrityLabel = missingItems.length === 0
      ? 'Complete'
      : missingItems.length <= 2 ? 'Partial' : 'Degraded';

    const recordColor = recording ? '#4caf50' : '#f44336';
    const coverageColor = coveragePct > 90 ? '#4caf50' : coveragePct > 60 ? '#ff9800' : '#f44336';

    this.container.innerHTML = `
      <div style="width:300px;min-height:220px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="margin:0;font-size:15px;">📼 VDR Status</h3>
          <span style="width:10px;height:10px;border-radius:50%;background:${integrityColor};display:inline-block;" title="Integrity: ${integrityLabel}"></span>
        </div>

        <!-- Recording status -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Recording</div>
            <div style="font-size:14px;font-weight:bold;color:${recordColor}">${recording ? '● REC' : '■ STOP'}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;text-align:center;">
            <div style="font-size:11px;color:#888;">Buffer</div>
            <div style="font-size:14px;font-weight:bold;">${bufferSize}<span style="font-size:11px;color:#888;"> MB</span></div>
          </div>
        </div>

        <!-- Coverage bar -->
        <div style="margin-bottom:8px;">
          <div style="font-size:12px;margin-bottom:3px;">Coverage: <b style="color:${coverageColor}">${coveragePct.toFixed !== undefined ? coveragePct.toFixed(1) : coveragePct}%</b></div>
          <div style="background:#333;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:${Math.min(coveragePct, 100)}%;height:100%;background:${coverageColor};border-radius:4px;transition:width .3s;"></div>
          </div>
        </div>

        <!-- Time range -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">
          <div style="background:#111;border-radius:6px;padding:8px;">
            <div style="font-size:11px;color:#888;">Oldest Record</div>
            <div style="font-size:11px;font-weight:bold;">${oldestRecord}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:8px;">
            <div style="font-size:11px;color:#888;">Newest Record</div>
            <div style="font-size:11px;font-weight:bold;">${newestRecord}</div>
          </div>
        </div>

        <!-- Integrity -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Integrity: <b style="color:${integrityColor}">${integrityLabel}</b></div>
          <div style="max-height:40px;overflow-y:auto;font-size:12px;">
            ${missingItems.length
              ? missingItems.map(m => `<div style="padding:2px 6px;margin-bottom:2px;background:#3a1c1c;border-left:3px solid ${integrityColor};border-radius:2px;">${m}</div>`).join('')
              : '<div style="color:#4caf50;">All data sources OK</div>'}
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
    console.log('📼 VDR Status Panel initialized');
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
