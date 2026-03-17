/**
 * PoseidonXChannels.js - PoseidonX 数字孪生体 Channel 数据集成
 * 
 * 扩展 PoseidonX 类支持 Channel 数据输入，实现 WebSocket 客户端连接 Python 后端，
 * 添加 Channel 数据缓存与更新机制，实现 AI 决策与 Channel 数据联动。
 * 
 * @version 1.0.0
 * @date 2026-03-12
 */

class PoseidonXChannels {
  /**
   * 创建 PoseidonXChannels 实例
   * @param {Object} options - 配置选项
   * @param {string} options.wsUrl - WebSocket 服务器地址 (默认：ws://localhost:8765)
   * @param {string} options.apiUrl - REST API 基础地址 (默认：http://localhost:8080)
   * @param {number} options.reconnectInterval - 重连间隔 (毫秒，默认：3000)
   * @param {number} options.cacheMaxSize - 缓存最大条目数 (默认：1000)
   * @param {number} options.cacheTTL - 缓存 TTL (毫秒，默认：300000)
   */
  constructor(options = {}) {
    this.wsUrl = options.wsUrl || 'ws://localhost:8765';
    this.apiUrl = options.apiUrl || 'http://localhost:8080';
    this.reconnectInterval = options.reconnectInterval || 3000;
    this.cacheMaxSize = options.cacheMaxSize || 1000;
    this.cacheTTL = options.cacheTTL || 300000;

    // WebSocket 连接
    this.ws = null;
    this.wsConnected = false;

    // 数据缓存 (LRU Cache)
    this.cache = new Map();
    this.cacheTimestamps = new Map();

    // 数据订阅回调
    this.subscribers = new Map(); // channel -> [callbacks]

    // 通道数据状态
    this.channels = {};
    this.channelMetadata = {};

    // AI 决策引擎引用
    this.aiDecisionEngine = null;

    // 日志
    this.logger = this._createLogger();

    // 自动重连标志
    this.autoReconnect = true;
    this.reconnectTimer = null;
  }

  /**
   * 创建日志记录器
   * @private
   */
  _createLogger() {
    const prefix = '[PoseidonXChannels]';
    return {
      info: (...args) => console.log(prefix, '[INFO]', ...args),
      warn: (...args) => console.warn(prefix, '[WARN]', ...args),
      error: (...args) => console.error(prefix, '[ERROR]', ...args),
      debug: (...args) => console.debug(prefix, '[DEBUG]', ...args),
    };
  }

  /**
   * 初始化连接
   * @returns {Promise<void>}
   */
  async connect() {
    this.logger.info('正在连接到 Poseidon Server...', this.wsUrl);

    try {
      // 获取 Channel 元数据
      await this._fetchChannelMetadata();

      // 建立 WebSocket 连接
      await this._connectWebSocket();

      this.logger.info('连接成功');
    } catch (error) {
      this.logger.error('连接失败:', error);
      throw error;
    }
  }

  /**
   * 获取 Channel 元数据
   * @private
   */
  async _fetchChannelMetadata() {
    try {
      const response = await fetch(`${this.apiUrl}/api/channels`);
      const data = await response.json();
      
      this.channelMetadata = {
        channels: data.channels || [],
        timestamp: Date.now(),
      };

      // 初始化通道数据结构
      this.channelMetadata.channels.forEach(channel => {
        this.channels[channel] = {
          data: null,
          timestamp: null,
          status: 'pending',
        };
      });

      this.logger.info(`获取到 ${this.channelMetadata.channels.length} 个 Channel`);
    } catch (error) {
      this.logger.warn('获取 Channel 元数据失败，使用默认配置:', error);
      // 使用默认 Channel 列表
      this.channelMetadata = {
        channels: [
          'nmea_parser', 'vessel_ais', 'engine_monitor', 'power_management',
          'navigation_data', 'cargo_monitor', 'weather_routing', 'web',
        ],
        timestamp: Date.now(),
      };
    }
  }

  /**
   * 连接 WebSocket
   * @private
   */
  _connectWebSocket() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.wsUrl);

        this.ws.onopen = () => {
          this.wsConnected = true;
          this.logger.info('WebSocket 连接已建立');
          
          // 清除重连定时器
          if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
          }

          // 发送订阅请求
          this._subscribeToAllChannels();

          resolve();
        };

        this.ws.onmessage = (event) => {
          this._handleWebSocketMessage(event);
        };

        this.ws.onclose = () => {
          this.wsConnected = false;
          this.logger.warn('WebSocket 连接已关闭');
          
          // 自动重连
          if (this.autoReconnect) {
            this._scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          this.logger.error('WebSocket 错误:', error);
          reject(error);
        };

        // 连接超时
        setTimeout(() => {
          if (!this.wsConnected) {
            reject(new Error('WebSocket 连接超时'));
          }
        }, 10000);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 安排重连
   * @private
   */
  _scheduleReconnect() {
    if (this.reconnectTimer) {
      return;
    }

    this.logger.info(`将在 ${this.reconnectInterval}ms 后重连...`);
    this.reconnectTimer = setTimeout(async () => {
      this.reconnectTimer = null;
      try {
        await this._connectWebSocket();
      } catch (error) {
        this.logger.error('重连失败:', error);
        this._scheduleReconnect();
      }
    }, this.reconnectInterval);
  }

  /**
   * 订阅所有 Channel
   * @private
   */
  _subscribeToAllChannels() {
    if (!this.ws || !this.wsConnected) {
      return;
    }

    const subscribeMessage = {
      type: 'subscribe',
      channels: this.channelMetadata.channels,
    };

    this.ws.send(JSON.stringify(subscribeMessage));
    this.logger.info('已订阅所有 Channel');
  }

  /**
   * 处理 WebSocket 消息
   * @private
   * @param {MessageEvent} event - WebSocket 消息事件
   */
  _handleWebSocketMessage(event) {
    try {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'data_update':
          this._handleDataUpdate(message);
          break;
        case 'alarm':
          this._handleAlarm(message);
          break;
        case 'channel_status':
          this._handleChannelStatus(message);
          break;
        default:
          this.logger.debug('未知消息类型:', message.type);
      }
    } catch (error) {
      this.logger.error('解析 WebSocket 消息失败:', error);
    }
  }

  /**
   * 处理数据更新
   * @private
   * @param {Object} message - 消息内容
   */
  _handleDataUpdate(message) {
    const { channel, data, timestamp } = message;

    // 更新缓存
    this._setCache(channel, data);

    // 更新通道状态
    if (this.channels[channel]) {
      this.channels[channel].data = data;
      this.channels[channel].timestamp = timestamp || Date.now();
      this.channels[channel].status = 'active';
    }

    // 通知订阅者
    this._notifySubscribers(channel, data);

    // 触发 AI 决策引擎
    if (this.aiDecisionEngine) {
      this.aiDecisionEngine.onChannelDataUpdate(channel, data);
    }
  }

  /**
   * 处理报警
   * @private
   * @param {Object} message - 报警消息
   */
  _handleAlarm(message) {
    const { channel, level, rule, value, threshold, timestamp } = message;

    this.logger.warn(`[${channel}] 报警 [${level}]: ${rule}, 当前值=${value}, 阈值=${threshold}`);

    // 通知订阅者
    this._notifySubscribers(channel, {
      type: 'alarm',
      level,
      rule,
      value,
      threshold,
      timestamp,
    });
  }

  /**
   * 处理 Channel 状态
   * @private
   * @param {Object} message - 状态消息
   */
  _handleChannelStatus(message) {
    const { channel, status, message: statusMessage } = message;

    if (this.channels[channel]) {
      this.channels[channel].status = status;
    }

    this.logger.info(`[${channel}] 状态更新: ${status} - ${statusMessage}`);
  }

  /**
   * 设置缓存
   * @private
   * @param {string} key - 缓存键
   * @param {any} value - 缓存值
   */
  _setCache(key, value) {
    // LRU 缓存管理
    if (this.cache.size >= this.cacheMaxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
      this.cacheTimestamps.delete(firstKey);
    }

    this.cache.set(key, value);
    this.cacheTimestamps.set(key, Date.now());
  }

  /**
   * 获取缓存
   * @private
   * @param {string} key - 缓存键
   * @returns {any|null} 缓存值，如果过期或不存在则返回 null
   */
  _getCache(key) {
    const timestamp = this.cacheTimestamps.get(key);
    if (!timestamp || Date.now() - timestamp > this.cacheTTL) {
      this.cache.delete(key);
      this.cacheTimestamps.delete(key);
      return null;
    }
    return this.cache.get(key);
  }

  /**
   * 订阅 Channel 数据
   * @param {string} channel - Channel 名称
   * @param {Function} callback - 回调函数 (data) => void
   * @returns {Function} 取消订阅函数
   */
  subscribe(channel, callback) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, []);
    }

    this.subscribers.get(channel).push(callback);

    // 如果已有缓存数据，立即回调
    const cachedData = this._getCache(channel);
    if (cachedData) {
      callback(cachedData);
    }

    // 返回取消订阅函数
    return () => {
      const callbacks = this.subscribers.get(channel);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  /**
   * 通知订阅者
   * @private
   * @param {string} channel - Channel 名称
   * @param {any} data - 数据
   */
  _notifySubscribers(channel, data) {
    const callbacks = this.subscribers.get(channel);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          this.logger.error(`订阅者回调失败 [${channel}]:`, error);
        }
      });
    }
  }

  /**
   * 获取 Channel 数据
   * @param {string} channel - Channel 名称
   * @returns {Object|null} Channel 数据
   */
  getChannelData(channel) {
    // 优先返回缓存数据
    const cached = this._getCache(channel);
    if (cached) {
      return cached;
    }

    // 返回最新数据
    return this.channels[channel]?.data || null;
  }

  /**
   * 获取所有 Channel 数据
   * @returns {Object} 所有 Channel 数据
   */
  getAllChannelData() {
    const result = {};
    this.channelMetadata.channels.forEach(channel => {
      result[channel] = this.getChannelData(channel);
    });
    return result;
  }

  /**
   * 通过 REST API 获取历史数据
   * @param {string} channel - Channel 名称
   * @param {Object} options - 查询选项
   * @param {string} options.startTime - 开始时间 (ISO 8601)
   * @param {string} options.endTime - 结束时间 (ISO 8601)
   * @param {number} options.limit - 最大返回条数
   * @returns {Promise<Array>} 历史数据数组
   */
  async getHistoricalData(channel, options = {}) {
    const params = new URLSearchParams();
    if (options.startTime) params.append('start_time', options.startTime);
    if (options.endTime) params.append('end_time', options.endTime);
    if (options.limit) params.append('limit', options.limit);

    const response = await fetch(
      `${this.apiUrl}/api/timeseries?channel=${channel}&${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data || [];
  }

  /**
   * 设置 AI 决策引擎
   * @param {Object} engine - AI 决策引擎实例
   */
  setAIDecisionEngine(engine) {
    this.aiDecisionEngine = engine;
    this.logger.info('AI 决策引擎已设置');
  }

  /**
   * 发送数据到后端
   * @param {string} channel - Channel 名称
   * @param {Object} data - 数据
   * @returns {Promise<Object>} 服务器响应
   */
  async sendData(channel, data) {
    const response = await fetch(`${this.apiUrl}/api/data/${channel}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.autoReconnect = false;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.wsConnected = false;
    this.logger.info('连接已断开');
  }

  /**
   * 获取连接状态
   * @returns {Object} 连接状态
   */
  getStatus() {
    return {
      connected: this.wsConnected,
      channels: Object.keys(this.channels),
      cacheSize: this.cache.size,
      subscribersCount: Array.from(this.subscribers.values()).reduce(
        (sum, arr) => sum + arr.length,
        0
      ),
    };
  }
}

/**
 * AI 决策引擎基类
 * 可扩展实现自定义 AI 决策逻辑
 */
class AIDecisionEngine {
  /**
   * 处理 Channel 数据更新
   * @param {string} channel - Channel 名称
   * @param {Object} data - 数据
   */
  onChannelDataUpdate(channel, data) {
    // 默认实现：子类应重写此方法
    console.debug('[AIDecisionEngine] 数据更新:', channel, data);
  }

  /**
   * 做出决策
   * @param {Object} context - 决策上下文
   * @returns {Object} 决策结果
   */
  makeDecision(context) {
    throw new Error('子类必须实现 makeDecision 方法');
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PoseidonXChannels, AIDecisionEngine };
} else {
  window.PoseidonXChannels = PoseidonXChannels;
  window.AIDecisionEngine = AIDecisionEngine;
}
