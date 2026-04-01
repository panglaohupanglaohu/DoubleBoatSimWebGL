/**
 * Crew Fatigue Panel - 船员疲劳状态面板
 * 
 * 显示值班人员列表、疲劳评分、换班建议
 */

export class CrewFatiguePanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/v1/ai-native/crew/fatigue-status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Crew fatigue fetch failed:', e);
    }
  }

  render() {
    if (!this.container) {
      console.error('Container not found');
      return;
    }

    const activeWatch = this.data?.active_watch || [];
    const fatigueScores = this.data?.fatigue_scores || {};
    const riskAlerts = this.data?.risk_alerts || [];
    const totalCrew = this.data?.total_crew_tracked ?? '--';

    this.container.innerHTML = `
      <div class="marine-panel crew-fatigue-panel">
        <div class="panel-header">
          <h2>😴 船员疲劳监测</h2>
          <div class="panel-controls">
            <button class="btn-refresh" id="cf-refresh">🔄 刷新</button>
          </div>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">追踪船员数</div>
            <div class="metric-value">${totalCrew}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">当前值班</div>
            <div class="metric-value">${activeWatch.length}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">疲劳告警</div>
            <div class="metric-value" style="color:${riskAlerts.length ? '#f44336' : '#4caf50'}">${riskAlerts.length}</div>
          </div>
        </div>

        <!-- 值班人员 & 疲劳评分 -->
        <div class="alerts-section" style="margin-top:15px;">
          <h3>👤 值班人员疲劳评分</h3>
          <div id="cf-crew-list" class="alerts-container">
            ${this._renderCrewList(fatigueScores)}
          </div>
        </div>

        <!-- 建议列表 -->
        <div class="alerts-section" style="margin-top:15px;">
          <h3>📋 建议</h3>
          <div id="cf-recommendations" class="alerts-container">
            ${this._renderAlerts(riskAlerts)}
          </div>
        </div>
      </div>
    `;

    const refreshBtn = this.container.querySelector('#cf-refresh');
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
    console.log('😴 Crew Fatigue Panel initialized');
  }

  startAutoRefresh(intervalMs = 30000) {
    this.stopAutoRefresh();
    this._refreshTimer = setInterval(() => this.refresh(), intervalMs);
  }

  stopAutoRefresh() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
      this._refreshTimer = null;
    }
  }

  _renderCrewList(scores) {
    const entries = Object.entries(scores);
    if (!entries.length) {
      return '<div class="alert-placeholder">暂无船员数据</div>';
    }
    return entries.map(([crewId, score]) => {
      const color = this._fatigueColor(score);
      const pct = Math.max(0, Math.min(100, score));
      return `
        <div style="display:flex;align-items:center;padding:6px 10px;margin-bottom:4px;">
          <span style="min-width:80px;font-weight:600;">${crewId}</span>
          <div style="flex:1;background:#263238;border-radius:4px;height:18px;margin:0 10px;overflow:hidden;">
            <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width .3s;"></div>
          </div>
          <span style="min-width:40px;text-align:right;color:${color};font-weight:600;">${score}</span>
        </div>`;
    }).join('');
  }

  _renderAlerts(alerts) {
    if (!alerts.length) {
      return '<div class="alert-placeholder">暂无建议</div>';
    }
    return alerts.map(a => {
      const msg = typeof a === 'string' ? a : (a.message || JSON.stringify(a));
      return `<div class="alert-item" style="padding:6px 10px;border-left:3px solid #ff9800;margin-bottom:4px;">${msg}</div>`;
    }).join('');
  }

  _fatigueColor(score) {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ffeb3b';
    if (score >= 40) return '#ff9800';
    return '#f44336';
  }
}
