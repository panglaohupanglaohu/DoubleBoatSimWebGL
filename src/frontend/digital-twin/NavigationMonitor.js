/**
 * NavigationMonitor - WorldMonitor 集成预留组件
 *
 * 当前阶段：方案层代码 / 结构骨架
 * 目标：为后续接入 globe.gl / deck.gl / MapLibre 提供统一接口
 */

export class NavigationMonitor {
  constructor(containerId, config = {}) {
    this.containerId = containerId;
    this.container = typeof document !== 'undefined' ? document.getElementById(containerId) : null;
    this.config = {
      mode: 'placeholder',
      showAtmosphere: true,
      labelsData: [],
      arcsData: [],
      ...config,
    };

    this.ownShip = null;
    this.targets = [];
    this.layers = {
      ais: true,
      weather: false,
      routes: false,
      ports: false,
    };

    this.renderPlaceholder();
  }

  renderPlaceholder() {
    if (!this.container) return;
    const mode = this.config.mode === 'connected' ? '已连接' : '占位模式';
    const statusColor = this.config.mode === 'connected' ? '#81c784' : '#ffb74d';
    this.container.innerHTML = `
      <div style="padding:12px; border-radius:10px; background:rgba(9,18,32,0.88); border:1px solid rgba(79,195,247,0.25); color:#d7ecff; font-size:12px;">
        <div style="font-weight:700; margin-bottom:8px; color:#4fc3f7;">🌍 WorldMonitor Navigation Monitor</div>
        <div style="opacity:0.9; line-height:1.5; margin-bottom:8px;">
          ${this.config.mode === 'connected' ? '已接入真实数据源' : '方案层骨架，后续将接入 globe.gl / deck.gl / MapLibre 进行 3D/2D 导航监控可视化。'}
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
          <span style="width:8px; height:8px; border-radius:50%; background:${statusColor}; display:inline-block;"></span>
          <span style="color:${statusColor}; font-size:11px;">${mode}</span>
        </div>
        <div id="wm-nav-summary" style="margin-top:10px; color:#9fc5e8; font-size:11px;">${this.config.mode === 'connected' ? '正在加载实时态势数据...' : '尚未接入实时态势数据。'}</div>
      </div>
    `;
  }

  setOwnShip(position) {
    this.ownShip = position;
    this.refreshSummary();
  }

  addAISTarget(target) {
    this.targets.push(target);
    this.refreshSummary();
  }

  setAISTargets(targets = []) {
    this.targets = [...targets];
    this.refreshSummary();
  }

  setLayerEnabled(layerName, enabled) {
    if (layerName in this.layers) {
      this.layers[layerName] = !!enabled;
    }
    this.refreshSummary();
  }

  refreshSummary() {
    if (!this.container) return;
    const summary = this.container.querySelector('#wm-nav-summary');
    if (!summary) return;

    const own = this.ownShip
      ? `本船 ${Number(this.ownShip.latitude || 0).toFixed(4)}, ${Number(this.ownShip.longitude || 0).toFixed(4)}`
      : '本船位置未设置';
    summary.textContent = `${own} ｜ AIS 目标 ${this.targets.length} 个 ｜ 图层: ${Object.entries(this.layers).filter(([, on]) => on).map(([k]) => k).join(', ')}`;
  }
}

export default NavigationMonitor;
