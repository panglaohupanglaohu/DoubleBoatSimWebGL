/**
 * Anchor Watch Panel - 锚泊监控面板
 * 
 * 显示锚位标记、摆动圆、漂移距离、走锚告警
 */

export class AnchorWatchPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/v1/ai-native/anchor/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Anchor watch fetch failed:', e);
    }
  }

  render() {
    if (!this.container) {
      console.error('Container not found');
      return;
    }

    const d = this.data || {};
    const anchored = d.anchored ?? false;
    const anchorPos = d.anchor_position || {};
    const swingRadius = d.swing_radius ?? '--';
    const driftDist = d.drift_distance ?? '--';
    const alarmStatus = d.alarm_status || 'normal';
    const depth = d.depth ?? '--';
    const chainLength = d.chain_length ?? '--';
    const anchorTime = d.anchor_time || '--';

    const alarmColor = alarmStatus === 'normal' ? '#4caf50' : '#f44336';

    this.container.innerHTML = `
      <div class="marine-panel anchor-watch-panel">
        <div class="panel-header">
          <h2>⚓ 锚泊监控</h2>
          <div class="panel-controls">
            <button class="btn-refresh" id="aw-refresh">🔄 刷新</button>
          </div>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">锚泊状态</div>
            <div class="metric-value" style="color:${anchored ? '#4caf50' : '#90a4ae'}">${anchored ? '已抛锚' : '未抛锚'}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">告警状态</div>
            <div class="metric-value" style="color:${alarmColor}">${alarmStatus}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">抛锚时间</div>
            <div class="metric-value" style="font-size:14px;">${anchorTime}</div>
          </div>
        </div>

        <div class="metrics-grid" style="margin-top:15px;">
          <div class="metric-card">
            <div class="metric-label">摆动半径</div>
            <div class="metric-value">${typeof swingRadius === 'number' ? swingRadius.toFixed(1) : swingRadius}</div>
            <div class="metric-unit">m</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">漂移距离</div>
            <div class="metric-value" style="color:${this._driftColor(driftDist, swingRadius)}">${typeof driftDist === 'number' ? driftDist.toFixed(1) : driftDist}</div>
            <div class="metric-unit">m</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">水深</div>
            <div class="metric-value">${depth}</div>
            <div class="metric-unit">m</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">出链长度</div>
            <div class="metric-value">${chainLength}</div>
            <div class="metric-unit">m</div>
          </div>
        </div>

        <!-- 锚位标记 -->
        <div class="alerts-section" style="margin-top:15px;">
          <h3>📍 锚位信息</h3>
          <div class="alerts-container">
            ${this._renderAnchorPosition(anchorPos, swingRadius, driftDist)}
          </div>
        </div>

        <!-- 走锚告警 -->
        <div class="alerts-section" style="margin-top:15px;">
          <h3>⚠️ 走锚告警</h3>
          <div class="alerts-container">
            ${this._renderDragAlarm(alarmStatus, driftDist, swingRadius)}
          </div>
        </div>
      </div>
    `;

    const refreshBtn = this.container.querySelector('#aw-refresh');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.refresh());
    }
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
    console.log('⚓ Anchor Watch Panel initialized');
  }

  startAutoRefresh(intervalMs = 15000) {
    this.stopAutoRefresh();
    this._refreshTimer = setInterval(() => this.refresh(), intervalMs);
  }

  stopAutoRefresh() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
      this._refreshTimer = null;
    }
  }

  _renderAnchorPosition(pos, swingRadius, driftDist) {
    if (!pos || (pos.lat === undefined && pos.latitude === undefined)) {
      return '<div class="alert-placeholder">未设置锚位</div>';
    }
    const lat = pos.lat ?? pos.latitude ?? 0;
    const lon = pos.lon ?? pos.longitude ?? 0;
    return `
      <div style="padding:8px 10px;">
        <div>纬度: <strong>${lat.toFixed(6)}</strong> | 经度: <strong>${lon.toFixed(6)}</strong></div>
        <div style="margin-top:6px;">摆动圆半径: <strong>${typeof swingRadius === 'number' ? swingRadius.toFixed(1) : swingRadius}m</strong></div>
        <div style="margin-top:4px;">当前漂移: <strong>${typeof driftDist === 'number' ? driftDist.toFixed(1) : driftDist}m</strong></div>
      </div>`;
  }

  _renderDragAlarm(alarm, drift, swing) {
    if (alarm === 'normal') {
      return '<div class="alert-placeholder" style="color:#4caf50;">锚泊正常，未检测到走锚</div>';
    }
    return `
      <div class="alert-item" style="padding:8px 10px;border-left:3px solid #f44336;color:#f44336;font-weight:600;">
        ⚠️ 走锚告警！漂移距离 ${typeof drift === 'number' ? drift.toFixed(1) : drift}m 超过摆动半径 ${typeof swing === 'number' ? swing.toFixed(1) : swing}m
      </div>`;
  }

  _driftColor(drift, swing) {
    if (typeof drift !== 'number' || typeof swing !== 'number') return '#90a4ae';
    if (drift > swing) return '#f44336';
    if (drift > swing * 0.8) return '#ff9800';
    return '#4caf50';
  }
}
