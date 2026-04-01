/**
 * Weather Routing Panel - 天气航线面板
 * 
 * 显示天气风险和航线建议，集成到 Poseidon-X 系统
 */

export class WeatherRoutingPanel {
  constructor(container) {
    this.container = container;
    this.data = null;
    this._refreshTimer = null;
  }

  async fetchData() {
    try {
      const resp = await fetch('/api/v1/ai-native/weather-routing/status');
      if (resp.ok) {
        const json = await resp.json();
        this.data = json.result || json;
      }
    } catch (e) {
      console.warn('Weather routing fetch failed:', e);
    }
  }

  render() {
    if (!this.container) {
      console.error('Container not found');
      return;
    }

    const weather = this.data?.current_weather || {};
    const riskLevel = weather.risk_level || this.data?.alert_level || 'normal';
    const forecastCount = this.data?.forecast_count ?? '--';
    const routeCount = this.data?.recommended_routes ?? '--';

    const riskColor = this._riskColor(riskLevel);

    this.container.innerHTML = `
      <div class="marine-panel weather-routing-panel">
        <div class="panel-header">
          <h2>🌤️ 天气航线面板</h2>
          <div class="panel-controls">
            <button class="btn-refresh" id="wr-refresh">🔄 刷新</button>
          </div>
        </div>

        <!-- 风险等级 -->
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">风险等级</div>
            <div class="metric-value" style="color:${riskColor}">${riskLevel}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">预报区域数</div>
            <div class="metric-value">${forecastCount}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">推荐航线</div>
            <div class="metric-value">${routeCount}</div>
          </div>
        </div>

        <!-- 当前天气 -->
        <div class="metrics-grid" style="margin-top:15px;">
          <div class="metric-card">
            <div class="metric-label">风速</div>
            <div class="metric-value">${weather.wind_speed ?? '--'}</div>
            <div class="metric-unit">kn</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">浪高</div>
            <div class="metric-value">${weather.wave_height ?? '--'}</div>
            <div class="metric-unit">m</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">能见度</div>
            <div class="metric-value">${weather.visibility ?? '--'}</div>
            <div class="metric-unit">nm</div>
          </div>
        </div>

        <!-- 建议列表 -->
        <div class="alerts-section" style="margin-top:15px;">
          <h3>📋 航线建议</h3>
          <div id="wr-recommendations" class="alerts-container">
            ${this._renderRecommendations()}
          </div>
        </div>
      </div>
    `;

    const refreshBtn = this.container.querySelector('#wr-refresh');
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
    console.log('🌤️ Weather Routing Panel initialized');
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

  _renderRecommendations() {
    const recs = this.data?.current_weather
      ? this._generateLocalRecommendations()
      : [];
    if (!recs.length) {
      return '<div class="alert-placeholder">暂无建议</div>';
    }
    return recs
      .map(r => `<div class="alert-item" style="padding:6px 10px;border-left:3px solid #4fc3f7;margin-bottom:4px;">${r}</div>`)
      .join('');
  }

  _generateLocalRecommendations() {
    const w = this.data?.current_weather || {};
    const recs = [];
    if ((w.wind_speed ?? 0) > 40) recs.push(`风速 ${w.wind_speed}kn 超过安全阈值，建议避开或降速`);
    if ((w.wave_height ?? 0) > 4) recs.push(`浪高 ${w.wave_height}m 达中危，建议调整航向`);
    if ((w.visibility ?? 10) < 1) recs.push(`能见度 ${w.visibility}nm 极低，开启雾航模式`);
    if (!recs.length) recs.push('当前气象条件适合航行');
    return recs;
  }

  _riskColor(level) {
    const map = { normal: '#4caf50', low: '#4caf50', medium: '#ff9800', high: '#f44336', critical: '#d50000' };
    return map[level] || '#90a4ae';
  }
}
