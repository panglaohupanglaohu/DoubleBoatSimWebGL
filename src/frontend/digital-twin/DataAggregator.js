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
      coordinationUrl: '/api/v1/ai-native/coordination/status',
      missionBriefUrl: '/api/v1/ai-native/cps/mission-brief',
      fusionStateUrl: '/api/v1/ai-native/perception/fusion-state',
      worldmonitorAisUrl: '/api/v1/worldmonitor/ais',
      worldmonitorWeatherUrl: '/api/v1/worldmonitor/weather',
      refreshIntervalMs: 15000,
      cacheTtlMs: 3000,
      ...config,
    };
    this.cache = new Map();
    this._inflight = new Map();
  }

  async fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`fetch failed: ${url} (${response.status})`);
    }
    return response.json();
  }

  /**
   * TTL-aware fetch with in-flight dedup.
   * Returns cached data if fresh; coalesces concurrent requests to same URL.
   */
  async _cachedFetch(key, url) {
    const cached = this.cache.get(key);
    if (cached && (Date.now() - cached.ts) < this.config.cacheTtlMs) {
      return cached.data;
    }
    if (this._inflight.has(key)) {
      return this._inflight.get(key);
    }
    const promise = this.fetchJson(url).then(data => {
      this.cache.set(key, { ts: Date.now(), data });
      this._inflight.delete(key);
      return data;
    }).catch(err => {
      this._inflight.delete(key);
      throw err;
    });
    this._inflight.set(key, promise);
    return promise;
  }

  async getLocalDashboard() {
    return this._cachedFetch('dashboard', this.config.dashboardUrl);
  }

  async getCoordinationStatus() {
    return this._cachedFetch('ai-native:coordination', this.config.coordinationUrl);
  }

  async getMissionBrief() {
    return this._cachedFetch('ai-native:mission-brief', this.config.missionBriefUrl);
  }

  async getFusionState() {
    return this._cachedFetch('ai-native:fusion-state', this.config.fusionStateUrl);
  }

  async getWorldMonitorAis() {
    return this._cachedFetch('worldmonitor:ais', this.config.worldmonitorAisUrl);
  }

  async getWorldMonitorWeather(lat, lng) {
    const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
    return this._cachedFetch('worldmonitor:weather', `${this.config.worldmonitorWeatherUrl}?${params.toString()}`);
  }

  async buildUnifiedView() {
    const [dashboardResult, coordinationResult, missionResult, fusionResult] = await Promise.allSettled([
      this.getLocalDashboard(),
      this.getCoordinationStatus(),
      this.getMissionBrief(),
      this.getFusionState(),
    ]);
    const dashboard = dashboardResult.status === 'fulfilled' ? dashboardResult.value : null;
    const coordination = coordinationResult.status === 'fulfilled' ? coordinationResult.value : null;
    const missionBrief = missionResult.status === 'fulfilled' ? missionResult.value : null;
    const fusionState = fusionResult.status === 'fulfilled' ? fusionResult.value : null;
    
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
      aiNative: {
        coordination,
        missionBrief,
        fusionState,
      },
      worldmonitor: {
        ais: wmAis,
        weather: wmWeather,
        status: wmStatus,
      },
    };
  }
}

export default DataAggregator;
