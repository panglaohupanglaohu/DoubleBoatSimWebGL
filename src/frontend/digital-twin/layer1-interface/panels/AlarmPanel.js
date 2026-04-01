/**
 * Alarm Panel - 集中告警面板
 *
 * 显示告警统计、未确认数量、活跃告警列表（按优先级排序）。
 * 从 /api/alarms/summary 和 /api/alarms/active 获取数据。
 */

export class AlarmPanel {
  constructor(container) {
    this.container = container;
    this.summaryData = null;
    this.activeAlarms = [];
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const [summaryResp, activeResp] = await Promise.all([
        fetch('/api/alarms/summary'),
        fetch('/api/alarms/active'),
      ]);
      if (summaryResp.ok) {
        const json = await summaryResp.json();
        this.summaryData = json.result || json;
      }
      if (activeResp.ok) {
        const json = await activeResp.json();
        this.activeAlarms = json.alarms || json.result || [];
      }
    } catch (e) {
      console.warn('Alarm data fetch failed:', e);
    }
  }

  render() {
    if (!this.container) return;

    const s = this.summaryData || {};
    const counts = s.counts || {};
    const emergency = counts.emergency ?? 0;
    const alarm = counts.alarm ?? 0;
    const warning = counts.warning ?? 0;
    const caution = counts.caution ?? 0;
    const unacknowledged = s.unacknowledged ?? 0;

    const priorityOrder = { emergency: 0, alarm: 1, warning: 2, caution: 3 };
    const sorted = [...this.activeAlarms].sort(
      (a, b) => (priorityOrder[a.priority] ?? 9) - (priorityOrder[b.priority] ?? 9)
    );

    const priorityColors = {
      emergency: '#f44336',
      alarm: '#ff9800',
      warning: '#ffeb3b',
      caution: '#2196f3',
    };

    this.container.innerHTML = `
      <div style="width:350px;min-height:300px;background:#1a1a2e;color:#e0e0e0;border-radius:8px;padding:14px;font-family:sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="margin:0;font-size:15px;">🚨 Alarm Center</h3>
          <span style="font-size:12px;color:${unacknowledged > 0 ? '#f44336' : '#4caf50'};">${unacknowledged} unack</span>
        </div>

        <!-- Counts -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px;margin-bottom:10px;">
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #f44336;">
            <div style="font-size:10px;color:#888;">Emergency</div>
            <div style="font-size:18px;font-weight:bold;color:#f44336;">${emergency}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #ff9800;">
            <div style="font-size:10px;color:#888;">Alarm</div>
            <div style="font-size:18px;font-weight:bold;color:#ff9800;">${alarm}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #ffeb3b;">
            <div style="font-size:10px;color:#888;">Warning</div>
            <div style="font-size:18px;font-weight:bold;color:#ffeb3b;">${warning}</div>
          </div>
          <div style="background:#111;border-radius:6px;padding:6px;text-align:center;border-top:3px solid #2196f3;">
            <div style="font-size:10px;color:#888;">Caution</div>
            <div style="font-size:18px;font-weight:bold;color:#2196f3;">${caution}</div>
          </div>
        </div>

        <!-- Active alarms list -->
        <div>
          <div style="font-size:12px;color:#888;margin-bottom:4px;">Active Alarms (${sorted.length})</div>
          <div style="max-height:160px;overflow-y:auto;font-size:12px;">
            ${sorted.length
              ? sorted.map(a => {
                  const color = priorityColors[a.priority] || '#888';
                  const time = a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : '--';
                  return `<div style="padding:4px 6px;margin-bottom:3px;background:#111;border-left:3px solid ${color};border-radius:2px;">
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:${color};font-weight:bold;text-transform:uppercase;">${a.priority || 'unknown'}</span>
                      <span style="color:#666;">${time}</span>
                    </div>
                    <div style="margin-top:2px;">${a.description || '--'}</div>
                    <div style="color:#666;font-size:11px;">${a.source_channel || ''}</div>
                  </div>`;
                }).join('')
              : '<div style="color:#4caf50;padding:8px;text-align:center;">No active alarms</div>'}
          </div>
        </div>
      </div>
    `;
  }

  update(data) {
    if (data.summary) this.summaryData = data.summary;
    if (data.alarms) this.activeAlarms = data.alarms;
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
    console.log('🚨 Alarm Panel initialized');
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
