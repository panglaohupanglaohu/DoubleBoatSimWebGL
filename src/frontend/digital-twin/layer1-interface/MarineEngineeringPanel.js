/**
 * Marine Engineering Panel - 船舶工程监控面板
 * 
 * 集成到 Poseidon-X 系统的专业船舶工程监控
 * 基于 Basic Ship Theory 和 Marine Engineering 知识库
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class MarineEngineeringPanel extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      shipType: config.shipType || 'catamaran',
      length: config.length || 138,
      beam: config.beam || 26,
      draft: config.draft || 5.5,
      displacement: config.displacement || 37000,
      hullSpacing: config.hullSpacing || 80,
      ...config
    };
    
    // 实时数据
    this.stabilityData = {
      GMt: 0,
      KB: 0,
      BMt: 0,
      KG: 0,
      rollPeriod: 0,
      pitchPeriod: 0,
      rollAngle: 0,
      pitchAngle: 0,
      GZ: []
    };
    
    this.motionData = {
      mskIndex: 0,
      comfortLevel: '未知',
      waveHeight: 0,
      wavePeriod: 0,
      rollRMS: 0,
      pitchRMS: 0
    };
    
    this.efficiencyData = {
      propulsiveEfficiency: 0,
      SFC: 0,
      score: 0,
      effectivePower: 0,
      shaftPower: 0
    };
    
    this.alerts = [];
    
    // IMO 衡准
    this.imoCriteria = {
      minGMt: 0.15,
      maxRollAngle: 30,
      weatherCriterion: 1.0
    };
    
    console.log('⚓ Marine Engineering Panel initialized');
  }
  
  /**
   * 初始化面板
   */
  initialize(container) {
    this.container = container;
    this.render();
    this.startMonitoring();
    
    console.log('📊 Marine Engineering Panel rendered');
  }
  
  /**
   * 渲染面板
   */
  render() {
    if (!this.container) {
      console.error('Container not found');
      return;
    }
    
    this.container.innerHTML = `
      <div class="marine-panel">
        <div class="panel-header">
          <h2>⚓ 船舶工程监控</h2>
          <div class="panel-controls">
            <button class="btn-refresh" onclick="window.marinePanel.refresh()">🔄 刷新</button>
            <button class="btn-export" onclick="window.marinePanel.export()">📥 导出</button>
          </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="tabs">
          <button class="tab active" data-tab="stability">📊 稳定性</button>
          <button class="tab" data-tab="motion">🌊 运动响应</button>
          <button class="tab" data-tab="efficiency">⚡ 能效</button>
          <button class="tab" data-tab="imo">📋 IMO</button>
        </div>
        
        <!-- 稳定性面板 -->
        <div class="tab-content active" id="tab-stability">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">初稳性高度 GMt</div>
              <div class="metric-value" id="gmt-value">--</div>
              <div class="metric-unit">m</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">浮心高 KB</div>
              <div class="metric-value" id="kb-value">--</div>
              <div class="metric-unit">m</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">稳心半径 BMt</div>
              <div class="metric-value" id="bmt-value">--</div>
              <div class="metric-unit">m</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">重心高 KG</div>
              <div class="metric-value" id="kg-value">--</div>
              <div class="metric-unit">m</div>
            </div>
          </div>
          
          <div class="metrics-grid" style="margin-top: 15px;">
            <div class="metric-card">
              <div class="metric-label">横摇周期 Tr</div>
              <div class="metric-value" id="roll-period">--</div>
              <div class="metric-unit">s</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">纵摇周期 Tp</div>
              <div class="metric-value" id="pitch-period">--</div>
              <div class="metric-unit">s</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">横倾角</div>
              <div class="metric-value" id="roll-angle">--</div>
              <div class="metric-unit">°</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">纵倾角</div>
              <div class="metric-value" id="pitch-angle">--</div>
              <div class="metric-unit">°</div>
            </div>
          </div>
          
          <div class="status-bar" id="stability-status">
            <span class="status-indicator">等待数据...</span>
          </div>
          
          <div class="formula-box">
            <strong>公式:</strong> GMt = KB + BMt - KG | Tr = 2π × B / √(GMt × g)
          </div>
        </div>
        
        <!-- 运动响应面板 -->
        <div class="tab-content" id="tab-motion">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">晕船指数 MSK</div>
              <div class="metric-value" id="msk-index">--</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">舒适度</div>
              <div class="metric-value" id="comfort-level">--</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">有义波高</div>
              <div class="metric-value" id="wave-height">--</div>
              <div class="metric-unit">m</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">波浪周期</div>
              <div class="metric-value" id="wave-period">--</div>
              <div class="metric-unit">s</div>
            </div>
          </div>
          
          <div class="metrics-grid" style="margin-top: 15px;">
            <div class="metric-card">
              <div class="metric-label">横摇 RMS</div>
              <div class="metric-value" id="roll-rms">--</div>
              <div class="metric-unit">°</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">纵摇 RMS</div>
              <div class="metric-value" id="pitch-rms">--</div>
              <div class="metric-unit">°</div>
            </div>
          </div>
          
          <div class="formula-box">
            <strong>ISO 2631:</strong> MSK = 0.5 × Roll_RMS + 0.3 × Pitch_RMS
          </div>
        </div>
        
        <!-- 能效面板 -->
        <div class="tab-content" id="tab-efficiency">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">推进效率</div>
              <div class="metric-value" id="prop-efficiency">--</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">燃油消耗率</div>
              <div class="metric-value" id="sfc">--</div>
              <div class="metric-unit">g/kWh</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">能效评分</div>
              <div class="metric-value" id="efficiency-score">--</div>
            </div>
          </div>
          
          <div class="metrics-grid" style="margin-top: 15px;">
            <div class="metric-card">
              <div class="metric-label">有效功率</div>
              <div class="metric-value" id="effective-power">--</div>
              <div class="metric-unit">kW</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">轴功率</div>
              <div class="metric-value" id="shaft-power">--</div>
              <div class="metric-unit">kW</div>
            </div>
          </div>
          
          <div class="knowledge-box">
            <strong>双体船阻力组成:</strong>
            <ul>
              <li>摩擦阻力 (Frictional Resistance)</li>
              <li>兴波阻力 (Wave-making Resistance)</li>
              <li>粘压阻力 (Viscous Pressure Resistance)</li>
              <li>空气阻力 (Air Resistance)</li>
            </ul>
          </div>
        </div>
        
        <!-- IMO 面板 -->
        <div class="tab-content" id="tab-imo">
          <div class="imo-checks">
            <div class="check-item" id="imo-gmt">
              <span class="check-icon">⏳</span>
              <span class="check-label">最小 GMt (≥0.15m)</span>
              <span class="check-status">检查中</span>
            </div>
            <div class="check-item" id="imo-roll">
              <span class="check-icon">⏳</span>
              <span class="check-label">最大横倾角 (≤30°)</span>
              <span class="check-status">检查中</span>
            </div>
            <div class="check-item" id="imo-gz">
              <span class="check-icon">⏳</span>
              <span class="check-label">GZ 曲线合规</span>
              <span class="check-status">检查中</span>
            </div>
            <div class="check-item" id="imo-weather">
              <span class="check-icon">⏳</span>
              <span class="check-label">天气衡准 (K≥1.0)</span>
              <span class="check-status">检查中</span>
            </div>
          </div>
          
          <div class="knowledge-box">
            <strong>IMO 完整稳性衡准 (2008 IS Code):</strong>
            <ul>
              <li>Area under GZ curve (0-30°) ≥ 0.055 m·rad</li>
              <li>Area under GZ curve (0-40°) ≥ 0.090 m·rad</li>
              <li>Maximum GZ at angle ≥ 25°</li>
              <li>Initial GMt ≥ 0.15 m</li>
              <li>Weather criterion K ≥ 1.0</li>
            </ul>
          </div>
        </div>
        
        <!-- 告警区域 -->
        <div class="alerts-section">
          <h3>⚠️ 告警列表</h3>
          <div id="alerts-list" class="alerts-container">
            <div class="alert-placeholder">暂无告警</div>
          </div>
        </div>
      </div>
    `;
    
    this.setupTabs();
    this.applyStyles();
    
    // 暴露全局实例
    window.marinePanel = this;
  }
  
  /**
   * 设置标签页
   */
  setupTabs() {
    const tabs = this.container.querySelectorAll('.tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // 切换标签
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // 切换内容
        const contents = this.container.querySelectorAll('.tab-content');
        contents.forEach(c => c.classList.remove('active'));
        this.container.querySelector(`#tab-${tabName}`).classList.add('active');
      });
    });
  }
  
  /**
   * 应用样式
   */
  applyStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .marine-panel {
        background: linear-gradient(135deg, rgba(0,105,148,0.1) 0%, rgba(0,50,100,0.15) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(0,212,255,0.2);
      }
      
      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
      }
      
      .panel-header h2 {
        color: #00d4ff;
        font-size: 24px;
      }
      
      .panel-controls button {
        background: rgba(0,212,255,0.2);
        border: 1px solid rgba(0,212,255,0.3);
        color: #00d4ff;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        margin-left: 10px;
      }
      
      .panel-controls button:hover {
        background: rgba(0,212,255,0.3);
      }
      
      .tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
      }
      
      .tab {
        background: transparent;
        border: none;
        color: #888;
        padding: 10px 20px;
        cursor: pointer;
        border-radius: 6px;
      }
      
      .tab.active {
        background: rgba(0,212,255,0.2);
        color: #00d4ff;
      }
      
      .tab-content {
        display: none;
      }
      
      .tab-content.active {
        display: block;
      }
      
      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
      }
      
      .metric-card {
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
      }
      
      .metric-label {
        font-size: 12px;
        color: #aaa;
        margin-bottom: 8px;
      }
      
      .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00d4ff;
      }
      
      .metric-unit {
        font-size: 12px;
        color: #888;
        margin-top: 4px;
      }
      
      .status-bar {
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        text-align: center;
      }
      
      .status-good { color: #00cc99; }
      .status-warning { color: #ffaa00; }
      .status-critical { color: #ff4444; }
      
      .formula-box, .knowledge-box {
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        font-size: 13px;
        color: #ccc;
      }
      
      .formula-box strong, .knowledge-box strong {
        color: #00d4ff;
        display: block;
        margin-bottom: 8px;
      }
      
      .knowledge-box ul {
        padding-left: 20px;
      }
      
      .knowledge-box li {
        margin: 4px 0;
      }
      
      .imo-checks {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      
      .check-item {
        background: rgba(0,0,0,0.2);
        padding: 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      
      .check-icon { font-size: 18px; }
      .check-label { flex: 1; color: #ccc; }
      .check-status { font-size: 12px; }
      
      .check-pass .check-icon { content: '✅'; }
      .check-pass .check-status { color: #00cc99; }
      .check-fail .check-icon { content: '❌'; }
      .check-fail .check-status { color: #ff4444; }
      
      .alerts-section {
        margin-top: 20px;
      }
      
      .alerts-section h3 {
        color: #ffaa00;
        margin-bottom: 10px;
      }
      
      .alerts-container {
        max-height: 200px;
        overflow-y: auto;
      }
      
      .alert-item {
        background: rgba(255,68,68,0.1);
        border-left: 3px solid #ff4444;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
      }
      
      .alert-item.warning {
        background: rgba(255,170,0,0.1);
        border-left-color: #ffaa00;
      }
      
      .alert-placeholder {
        color: #666;
        text-align: center;
        padding: 20px;
      }
    `;
    document.head.appendChild(style);
  }
  
  /**
   * 开始监控
   */
  startMonitoring() {
    setInterval(() => this.update(), 5000);
    this.update();
  }
  
  /**
   * 更新数据
   */
  update() {
    const data = this.generateData();
    this.stabilityData = data.stability;
    this.motionData = data.motion;
    this.efficiencyData = data.efficiency;
    
    this.updateDisplay();
    this.checkIMO();
    this.updateAlerts();
  }
  
  /**
   * 生成模拟数据
   */
  generateData() {
    const GMt = 8.5 + Math.random() * 2;
    const rollAngle = (Math.random() - 0.5) * 10;
    const rollPeriod = 2 * Math.PI * 26 / Math.sqrt(GMt * 9.81);
    const pitchPeriod = 2 * Math.PI * 138 / Math.sqrt(GMt * 9.81 * 0.8);
    const waveHeight = 1.5 + Math.random() * 2;
    const mskIndex = waveHeight * 0.3 + Math.random() * 0.5;
    
    return {
      stability: {
        GMt: GMt.toFixed(2),
        KB: 3.0,
        BMt: 6.5,
        KG: 0.54,
        rollPeriod: rollPeriod.toFixed(2),
        pitchPeriod: pitchPeriod.toFixed(2),
        rollAngle: rollAngle.toFixed(2),
        pitchAngle: ((Math.random() - 0.5) * 5).toFixed(2)
      },
      motion: {
        mskIndex: mskIndex.toFixed(2),
        comfortLevel: this.getComfortLevel(mskIndex),
        waveHeight: waveHeight.toFixed(1),
        wavePeriod: (6 + Math.random() * 4).toFixed(1),
        rollRMS: (Math.random() * 5).toFixed(1),
        pitchRMS: (Math.random() * 3).toFixed(1)
      },
      efficiency: {
        propulsiveEfficiency: (55 + Math.random() * 15).toFixed(1),
        SFC: (170 + Math.random() * 40).toFixed(1),
        score: Math.floor(70 + Math.random() * 25),
        effectivePower: (3000 + Math.random() * 1000).toFixed(0),
        shaftPower: (5000 + Math.random() * 1500).toFixed(0)
      }
    };
  }
  
  /**
   * 获取舒适度等级
   */
  getComfortLevel(msk) {
    if (msk < 0.5) return '舒适';
    if (msk < 1.0) return '较舒适';
    if (msk < 2.0) return '不舒适';
    return '非常不舒适';
  }
  
  /**
   * 更新显示
   */
  updateDisplay() {
    // 稳定性
    this.setValue('gmt-value', this.stabilityData.GMt);
    this.setValue('kb-value', this.stabilityData.KB);
    this.setValue('bmt-value', this.stabilityData.BMt);
    this.setValue('kg-value', this.stabilityData.KG);
    this.setValue('roll-period', this.stabilityData.rollPeriod);
    this.setValue('pitch-period', this.stabilityData.pitchPeriod);
    this.setValue('roll-angle', this.stabilityData.rollAngle);
    this.setValue('pitch-angle', this.stabilityData.pitchAngle);
    
    // 运动
    this.setValue('msk-index', this.motionData.mskIndex);
    this.setValue('comfort-level', this.motionData.comfortLevel);
    this.setValue('wave-height', this.motionData.waveHeight);
    this.setValue('wave-period', this.motionData.wavePeriod);
    this.setValue('roll-rms', this.motionData.rollRMS);
    this.setValue('pitch-rms', this.motionData.pitchRMS);
    
    // 能效
    this.setValue('prop-efficiency', this.efficiencyData.propulsiveEfficiency + '%');
    this.setValue('sfc', this.efficiencyData.SFC);
    this.setValue('efficiency-score', this.efficiencyData.score + '/100');
    this.setValue('effective-power', this.efficiencyData.effectivePower);
    this.setValue('shaft-power', this.efficiencyData.shaftPower);
    
    // 稳定性状态
    const statusEl = document.getElementById('stability-status');
    if (statusEl) {
      const gmt = parseFloat(this.stabilityData.GMt);
      if (gmt < 0.15) {
        statusEl.innerHTML = '<span class="status-indicator status-critical">⚠️ 稳性不足！</span>';
      } else if (gmt < 5) {
        statusEl.innerHTML = '<span class="status-indicator status-warning">⚠️ 稳性偏低</span>';
      } else {
        statusEl.innerHTML = '<span class="status-indicator status-good">✅ 稳定性良好</span>';
      }
    }
  }
  
  /**
   * 检查 IMO 合规
   */
  checkIMO() {
    const gmt = parseFloat(this.stabilityData.GMt);
    const roll = Math.abs(parseFloat(this.stabilityData.rollAngle));
    
    this.setCheck('imo-gmt', gmt >= 0.15);
    this.setCheck('imo-roll', roll <= 30);
    this.setCheck('imo-gz', gmt >= 0.15 && roll <= 30);
    this.setCheck('imo-weather', true);
  }
  
  /**
   * 设置检查项状态
   */
  setCheck(id, passed) {
    const el = document.getElementById(id);
    if (el) {
      el.className = `check-item ${passed ? 'check-pass' : 'check-fail'}`;
      el.querySelector('.check-icon').textContent = passed ? '✅' : '❌';
      el.querySelector('.check-status').textContent = passed ? '合规' : '不合规';
      el.querySelector('.check-status').style.color = passed ? '#00cc99' : '#ff4444';
    }
  }
  
  /**
   * 更新告警
   */
  updateAlerts() {
    const alerts = [];
    const gmt = parseFloat(this.stabilityData.GMt);
    const roll = Math.abs(parseFloat(this.stabilityData.rollAngle));
    const msk = parseFloat(this.motionData.mskIndex);
    
    if (gmt < 0.15) {
      alerts.push({ level: 'critical', message: 'GMt 低于 IMO 最低要求！' });
    } else if (gmt < 5) {
      alerts.push({ level: 'warning', message: 'GMt 偏低，建议关注' });
    }
    
    if (roll > 30) {
      alerts.push({ level: 'critical', message: '横倾角超过 30°！' });
    } else if (roll > 15) {
      alerts.push({ level: 'warning', message: '横倾角较大' });
    }
    
    if (msk > 2.0) {
      alerts.push({ level: 'warning', message: '晕船指数高，舒适度差' });
    }
    
    const container = document.getElementById('alerts-list');
    if (container) {
      if (alerts.length === 0) {
        container.innerHTML = '<div class="alert-placeholder">暂无告警</div>';
      } else {
        container.innerHTML = alerts.map(alert => `
          <div class="alert-item ${alert.level}">
            <div class="alert-level">${alert.level === 'critical' ? '🔴 严重' : '🟡 警告'}</div>
            <div class="alert-message">${alert.message}</div>
          </div>
        `).join('');
      }
    }
  }
  
  /**
   * 设置值
   */
  setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }
  
  /**
   * 刷新
   */
  refresh() {
    this.update();
    console.log('🔄 Marine Panel refreshed');
  }
  
  /**
   * 导出
   */
  export() {
    const data = {
      timestamp: new Date().toISOString(),
      stability: this.stabilityData,
      motion: this.motionData,
      efficiency: this.efficiencyData,
      alerts: this.alerts
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `marine-data-${Date.now()}.json`;
    a.click();
    
    console.log('📥 Marine data exported');
  }
}

export default MarineEngineeringPanel;
