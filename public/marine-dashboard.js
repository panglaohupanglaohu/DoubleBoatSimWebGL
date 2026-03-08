/**
 * Marine Engineering Dashboard
 * 船舶工程监控面板
 * 
 * 基于船舶理论知识库的专业监控功能
 * 集成稳定性计算、运动响应、能效分析
 */

class MarineEngineeringDashboard {
  constructor(apiBaseUrl = 'http://localhost:3001') {
    this.apiBaseUrl = apiBaseUrl;
    this.shipData = {
      // 双体船主参数 (138 米双体客船)
      length: 138,        // 船长 (m)
      beam: 26,           // 船宽 (m)
      draft: 5.5,         // 吃水 (m)
      displacement: 37000, // 排水量 (吨)
      hullSpacing: 80,    // 两船体间距 (m)
      
      // 实时状态
      stability: null,
      motion: null,
      efficiency: null,
      alerts: []
    };
    
    this.init();
  }
  
  async init() {
    console.log('⚓ Marine Engineering Dashboard initialized');
    this.render();
    this.startMonitoring();
  }
  
  /**
   * 渲染监控面板
   */
  render() {
    const container = document.getElementById('marine-dashboard');
    if (!container) {
      console.error('Marine dashboard container not found');
      return;
    }
    
    container.innerHTML = `
      <div class="marine-panel">
        <h2>⚓ 船舶工程监控</h2>
        
        <!-- 稳定性监控 -->
        <div class="section">
          <h3>📊 稳定性监控</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">初稳性高度 GMt</div>
              <div class="metric-value" id="gmt-value">--</div>
              <div class="metric-unit">m</div>
            </div>
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
          </div>
          <div class="status-bar" id="stability-status">
            <span class="status-indicator">等待数据...</span>
          </div>
        </div>
        
        <!-- IMO 合规检查 -->
        <div class="section">
          <h3>📋 IMO 稳性衡准</h3>
          <div class="imo-checks">
            <div class="check-item" id="imo-gmt">
              <span class="check-icon">⏳</span>
              <span class="check-label">最小 GMt (≥0.15m)</span>
            </div>
            <div class="check-item" id="imo-roll">
              <span class="check-icon">⏳</span>
              <span class="check-label">最大横倾角 (≤30°)</span>
            </div>
            <div class="check-item" id="imo-gz">
              <span class="check-icon">⏳</span>
              <span class="check-label">GZ 曲线合规</span>
            </div>
          </div>
        </div>
        
        <!-- 运动响应 -->
        <div class="section">
          <h3>🌊 运动响应</h3>
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
          </div>
        </div>
        
        <!-- 能效分析 -->
        <div class="section">
          <h3>⚡ 能效分析</h3>
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
        </div>
        
        <!-- 告警列表 -->
        <div class="section">
          <h3>⚠️ 告警列表</h3>
          <div id="alerts-list" class="alerts-container">
            <div class="alert-placeholder">暂无告警</div>
          </div>
        </div>
      </div>
    `;
    
    this.updateStyles();
  }
  
  /**
   * 更新样式
   */
  updateStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .marine-panel {
        background: linear-gradient(135deg, rgba(0,105,148,0.1) 0%, rgba(0,50,100,0.15) 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(0,212,255,0.2);
      }
      
      .marine-panel h2 {
        color: #00d4ff;
        margin-bottom: 20px;
        font-size: 24px;
      }
      
      .marine-panel h3 {
        color: #7b2ff7;
        margin: 20px 0 15px 0;
        font-size: 18px;
        border-bottom: 1px solid rgba(123,47,247,0.3);
        padding-bottom: 8px;
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
      
      .status-indicator {
        font-size: 14px;
      }
      
      .status-good { color: #00cc99; }
      .status-warning { color: #ffaa00; }
      .status-critical { color: #ff4444; }
      
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
      .check-label { font-size: 14px; color: #ccc; }
      
      .check-pass .check-icon { content: '✅'; }
      .check-fail .check-icon { content: '❌'; }
      
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
      
      .alert-level {
        font-weight: bold;
        margin-bottom: 4px;
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
    // 每 5 秒更新一次数据
    setInterval(() => this.updateData(), 5000);
    this.updateData();
  }
  
  /**
   * 更新数据
   */
  async updateData() {
    try {
      // 模拟数据 (实际应从后端 API 获取)
      const mockData = this.generateMockData();
      this.shipData = { ...this.shipData, ...mockData };
      
      this.updateDisplay();
      this.checkIMOCompliance();
      this.updateAlerts();
    } catch (error) {
      console.error('Failed to update marine data:', error);
    }
  }
  
  /**
   * 生成模拟数据
   */
  generateMockData() {
    // 基于船舶理论的模拟数据
    const GMt = 8.5 + Math.random() * 2; // 8.5-10.5m
    const rollAngle = (Math.random() - 0.5) * 10; // -5° to 5°
    const rollPeriod = 2 * Math.PI * 26 / Math.sqrt(GMt * 9.81);
    const pitchPeriod = 2 * Math.PI * 138 / Math.sqrt(GMt * 9.81 * 0.8);
    
    const waveHeight = 1.5 + Math.random() * 2;
    const mskIndex = waveHeight * 0.3 + Math.random() * 0.5;
    
    return {
      stability: {
        GMt: GMt.toFixed(2),
        rollPeriod: rollPeriod.toFixed(2),
        pitchPeriod: pitchPeriod.toFixed(2),
        rollAngle: rollAngle.toFixed(2)
      },
      motion: {
        mskIndex: mskIndex.toFixed(2),
        comfortLevel: this.getComfortLevel(mskIndex),
        waveHeight: waveHeight.toFixed(1)
      },
      efficiency: {
        propEfficiency: (55 + Math.random() * 15).toFixed(1),
        sfc: (170 + Math.random() * 40).toFixed(1),
        score: Math.floor(70 + Math.random() * 25)
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
    this.setValue('gmt-value', this.shipData.stability?.GMt || '--');
    this.setValue('roll-period', this.shipData.stability?.rollPeriod || '--');
    this.setValue('pitch-period', this.shipData.stability?.pitchPeriod || '--');
    this.setValue('roll-angle', this.shipData.stability?.rollAngle || '--');
    
    // 运动
    this.setValue('msk-index', this.shipData.motion?.mskIndex || '--');
    this.setValue('comfort-level', this.shipData.motion?.comfortLevel || '--');
    this.setValue('wave-height', this.shipData.motion?.waveHeight || '--');
    
    // 能效
    this.setValue('prop-efficiency', this.shipData.efficiency?.propEfficiency + '%' || '--');
    this.setValue('sfc', this.shipData.efficiency?.sfc || '--');
    this.setValue('efficiency-score', this.shipData.efficiency?.score || '--');
    
    // 稳定性状态
    const statusEl = document.getElementById('stability-status');
    if (statusEl) {
      const gmt = parseFloat(this.shipData.stability?.GMt || 0);
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
  checkIMOCompliance() {
    const gmt = parseFloat(this.shipData.stability?.GMt || 0);
    const roll = Math.abs(parseFloat(this.shipData.stability?.rollAngle || 0));
    
    this.setCheck('imo-gmt', gmt >= 0.15);
    this.setCheck('imo-roll', roll <= 30);
    this.setCheck('imo-gz', gmt >= 0.15 && roll <= 30);
  }
  
  /**
   * 设置检查项状态
   */
  setCheck(id, passed) {
    const el = document.getElementById(id);
    if (el) {
      el.className = `check-item ${passed ? 'check-pass' : 'check-fail'}`;
      el.querySelector('.check-icon').textContent = passed ? '✅' : '❌';
    }
  }
  
  /**
   * 更新告警
   */
  updateAlerts() {
    const alerts = [];
    const gmt = parseFloat(this.shipData.stability?.GMt || 0);
    const roll = Math.abs(parseFloat(this.shipData.stability?.rollAngle || 0));
    const msk = parseFloat(this.shipData.motion?.mskIndex || 0);
    
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
}

// 自动初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.marineDashboard = new MarineEngineeringDashboard();
  });
} else {
  window.marineDashboard = new MarineEngineeringDashboard();
}
