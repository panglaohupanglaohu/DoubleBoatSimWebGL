/**
 * Context Window - 上下文窗口管理器
 * 
 * Software 3.0 理念：Context Window = RAM
 * - 全船所有传感器数据（NMEA, Modbus）转化为文本或 Embedding
 * - 实时喂给 LLM 的上下文窗口
 * - 智能压缩和优先级管理
 * 
 * 数据流：
 * Sensors → Raw Data → Text/Embedding → Context Window → LLM
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class ContextWindow extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      maxTokens: config.maxTokens || 128000, // 最大 token 数
      compressionThreshold: config.compressionThreshold || 0.8, // 压缩阈值（80%）
      priorityLevels: config.priorityLevels || ['critical', 'high', 'medium', 'low'],
      updateInterval: config.updateInterval || 1000, // 更新间隔（毫秒）
      ...config
    };
    
    // 上下文存储（分优先级）
    this.contexts = {
      system: [], // 系统提示词（Vibe）
      critical: [], // 关键数据（警报、紧急状态）
      high: [], // 重要数据（主要设备状态）
      medium: [], // 常规数据（传感器读数）
      low: [] // 低优先级（历史日志）
    };
    
    // 传感器数据缓存
    this.sensorCache = new Map();
    
    // 估算当前 token 使用量
    this.currentTokens = 0;
    
    // 更新定时器
    this.updateTimer = null;
    
    this._startAutoUpdate();
    
    console.log('🧠 Context Window initialized (max tokens:', this.config.maxTokens, ')');
  }
  
  /**
   * 添加系统提示词（Vibe）
   * @param {string} vibe - 系统角色定义
   */
  setSystemVibe(vibe) {
    this.contexts.system = [{
      type: 'system',
      content: vibe,
      timestamp: new Date().toISOString(),
      permanent: true // 永不被压缩掉
    }];
    
    this._recalculateTokens();
  }
  
  /**
   * 添加传感器数据
   * @param {string} sensorId - 传感器 ID
   * @param {*} value - 传感器值
   * @param {string} priority - 优先级
   */
  addSensorData(sensorId, value, priority = 'medium') {
    // 缓存原始数据
    this.sensorCache.set(sensorId, {
      value,
      timestamp: Date.now(),
      priority
    });
    
    // 转换为文本
    const textContent = this._sensorToText(sensorId, value);
    
    // 添加到相应优先级的上下文
    if (this.contexts[priority]) {
      this.contexts[priority].push({
        type: 'sensor',
        sensorId,
        content: textContent,
        timestamp: new Date().toISOString(),
        priority
      });
    }
    
    // 触发更新
    this._recalculateTokens();
  }
  
  /**
   * 传感器数据转文本
   * @private
   */
  _sensorToText(sensorId, value) {
    // 将传感器数据转为 LLM 可理解的自然语言
    // 例如：MainEngine.ExhaustTemp = 380 → "主机排温：380°C"
    
    const sensorNames = {
      'MainEngine.ExhaustTemp': '主机排温',
      'MainEngine.RPM': '主机转速',
      'GPS.Latitude': '纬度',
      'GPS.Longitude': '经度',
      'GPS.Heading': '航向',
      'FuelTank.Level': '燃油液位',
      'Weather.WindSpeed': '风速',
      'Weather.WindDirection': '风向'
      // ... 更多传感器映射
    };
    
    const name = sensorNames[sensorId] || sensorId;
    
    // 格式化数值
    let formattedValue = value;
    if (typeof value === 'number') {
      formattedValue = value.toFixed(2);
    }
    
    return `${name}: ${formattedValue}`;
  }
  
  /**
   * 添加事件（警报、操作日志）
   * @param {string} event - 事件描述
   * @param {string} priority - 优先级
   */
  addEvent(event, priority = 'high') {
    if (this.contexts[priority]) {
      this.contexts[priority].push({
        type: 'event',
        content: event,
        timestamp: new Date().toISOString(),
        priority
      });
    }
    
    this._recalculateTokens();
    
    // 触发事件
    this.emit('event:added', { event, priority });
  }
  
  /**
   * 获取完整上下文（给 LLM 使用）
   * @returns {Array} - 上下文数组
   */
  getContext() {
    const context = [];
    
    // 按优先级顺序合并（system > critical > high > medium > low）
    context.push(...this.contexts.system);
    context.push(...this.contexts.critical);
    context.push(...this.contexts.high);
    context.push(...this.contexts.medium);
    context.push(...this.contexts.low);
    
    return context;
  }
  
  /**
   * 获取摘要上下文（压缩版本）
   * @returns {Array} - 压缩后的上下文
   */
  getCompressedContext() {
    const context = [];
    
    // System vibe 永远保留
    context.push(...this.contexts.system);
    
    // Critical 和 High 保留最近的
    context.push(...this._getTail(this.contexts.critical, 5));
    context.push(...this._getTail(this.contexts.high, 10));
    
    // Medium 和 Low 做摘要
    const mediumSummary = this._summarize(this.contexts.medium, 'medium');
    const lowSummary = this._summarize(this.contexts.low, 'low');
    
    if (mediumSummary) context.push(mediumSummary);
    if (lowSummary) context.push(lowSummary);
    
    return context;
  }
  
  /**
   * 获取数组的末尾 N 项
   * @private
   */
  _getTail(array, count) {
    return array.slice(-count);
  }
  
  /**
   * 摘要压缩
   * @private
   */
  _summarize(items, priority) {
    if (items.length === 0) return null;
    
    // 简单的摘要策略：只保留最新的几条，其余折叠
    const recentCount = priority === 'medium' ? 5 : 2;
    const recent = items.slice(-recentCount);
    const older = items.slice(0, -recentCount);
    
    const summary = {
      type: 'summary',
      content: `[压缩] ${priority} 优先级数据：${older.length} 条历史记录已折叠。最近 ${recentCount} 条：\n${recent.map(r => r.content).join('\n')}`,
      timestamp: new Date().toISOString(),
      priority
    };
    
    return summary;
  }
  
  /**
   * 重新计算 token 使用量
   * @private
   */
  _recalculateTokens() {
    // 简化估算：1 token ≈ 4 字符（英文）或 1.5 字符（中文）
    const allContext = this.getContext();
    const totalChars = allContext.reduce((sum, item) => {
      return sum + (item.content ? item.content.length : 0);
    }, 0);
    
    // 估算 tokens（中英文混合，取平均）
    this.currentTokens = Math.ceil(totalChars / 2.5);
    
    // 如果超过阈值，触发压缩
    const threshold = this.config.maxTokens * this.config.compressionThreshold;
    if (this.currentTokens > threshold) {
      console.warn(`⚠️ Context window approaching limit: ${this.currentTokens} / ${this.config.maxTokens} tokens`);
      this._compress();
    }
    
    // 触发事件
    this.emit('tokens:updated', {
      current: this.currentTokens,
      max: this.config.maxTokens,
      usage: (this.currentTokens / this.config.maxTokens * 100).toFixed(1) + '%'
    });
  }
  
  /**
   * 压缩上下文
   * @private
   */
  _compress() {
    console.log('🗜️ Compressing context window...');
    
    // 压缩策略：
    // 1. System vibe 永不删除
    // 2. Critical 保留最近 10 条
    // 3. High 保留最近 20 条
    // 4. Medium 保留最近 30 条
    // 5. Low 保留最近 10 条
    
    this.contexts.critical = this._getTail(this.contexts.critical, 10);
    this.contexts.high = this._getTail(this.contexts.high, 20);
    this.contexts.medium = this._getTail(this.contexts.medium, 30);
    this.contexts.low = this._getTail(this.contexts.low, 10);
    
    this._recalculateTokens();
    
    console.log(`✅ Context compressed to ${this.currentTokens} tokens`);
  }
  
  /**
   * 清空上下文（保留 system vibe）
   */
  clear() {
    const systemVibe = this.contexts.system;
    
    this.contexts = {
      system: systemVibe,
      critical: [],
      high: [],
      medium: [],
      low: []
    };
    
    this.sensorCache.clear();
    this._recalculateTokens();
    
    console.log('🧹 Context window cleared');
  }
  
  /**
   * 启动自动更新
   * @private
   */
  _startAutoUpdate() {
    this.updateTimer = setInterval(() => {
      // 定期清理过期数据（超过 1 小时的低优先级数据）
      const now = Date.now();
      const oneHourAgo = now - 3600000;
      
      ['medium', 'low'].forEach(priority => {
        this.contexts[priority] = this.contexts[priority].filter(item => {
          const itemTime = new Date(item.timestamp).getTime();
          return itemTime > oneHourAgo;
        });
      });
      
      this._recalculateTokens();
    }, this.config.updateInterval);
  }
  
  /**
   * 获取统计信息
   */
  getStats() {
    return {
      totalTokens: this.currentTokens,
      maxTokens: this.config.maxTokens,
      usage: (this.currentTokens / this.config.maxTokens * 100).toFixed(1) + '%',
      counts: {
        system: this.contexts.system.length,
        critical: this.contexts.critical.length,
        high: this.contexts.high.length,
        medium: this.contexts.medium.length,
        low: this.contexts.low.length
      },
      sensors: this.sensorCache.size
    };
  }
  
  /**
   * 销毁
   */
  dispose() {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
    
    this.clear();
    this.removeAllListeners();
    
    console.log('🗑️ Context Window disposed');
  }
}
