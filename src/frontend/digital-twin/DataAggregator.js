/**
 * DataAggregator - WorldMonitor / 本地船舶数据聚合器
 *
 * 当前阶段：方案层代码 / 结构骨架
 * 目标：统一汇总本地 API 与未来 WorldMonitor 数据源
 */

export class DataAggregator {
  constructor(config = {}) {
    this.config = {
      dashboardUrl: '/api/v1/dashboard',
      worldmonitorAisUrl: '/api/v1/worldmonitor/ais',
      worldmonitorWeatherUrl: '/api/v1/worldmonitor/weather',
      refreshIntervalMs: 15000,
      ...config,
    };
    this.cache = new Map();
  }

  async fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`fetch failed: ${url} (${response.status})`);
    }
    return response.json();
  }

  async getLocalDashboard() {
    const data = await this.fetchJson(this.config.dashboardUrl);
    this.cache.set('dashboard', { ts: Date.now(), data });
    return data;
  }

  async getWorldMonitorAis() {
    const data = await this.fetchJson(this.config.worldmonitorAisUrl);
    this.cache.set('worldmonitor:ais', { ts: Date.now(), data });
    return data;
  }

  async getWorldMonitorWeather(lat, lng) {
    const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
    const data = await this.fetchJson(`${this.config.worldmonitorWeatherUrl}?${params.toString()}`);
    this.cache.set('worldmonitor:weather', { ts: Date.now(), data });
    return data;
  }

  async buildUnifiedView() {
    const dashboard = await this.getLocalDashboard();
    
    // Try to get real WorldMonitor data
    let wmAis = null;
    let wmWeather = null;
    let wmStatus = 'placeholder';
    
    try {
      wmAis = await this.getWorldMonitorAis();
      if (wmAis && wmAis.source === 'real') {
        wmStatus = 'connected';
      }
    } catch (e) {
      console.warn('Failed to get WorldMonitor AIS:', e);
    }
    
    try {
      wmWeather = await this.getWorldMonitorWeather(31.2304, 121.4737);
      if (wmWeather && wmWeather.source === 'real') {
        wmStatus = 'connected';
      }
    } catch (e) {
      console.warn('Failed to get WorldMonitor weather:', e);
    }
    
    return {
      generatedAt: new Date().toISOString(),
      source: wmStatus === 'connected' ? 'real' : 'hybrid',
      local: dashboard,
      worldmonitor: {
        ais: wmAis,
        weather: wmWeather,
        status: wmStatus,
      },
    };
  }
}

export default DataAggregator;
