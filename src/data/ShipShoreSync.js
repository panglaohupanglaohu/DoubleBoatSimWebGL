/**
 * 船岸数据同步系统
 * Ship-Shore Data Synchronization System
 * 
 * 实现船端和岸端数字孪生系统的数据同步：
 * - 静态数据批次传输（船体数据）
 * - 动态数据批次传输（移动数据）
 * - 数据压缩与筛选
 * - 优先级管理
 */

import { EventEmitter } from '../utils/EventEmitter.js';

export class ShipShoreSync extends EventEmitter {
  constructor(dataSource, options = {}) {
    super();
    
    this.dataSource = dataSource; // 数据源（VirtualDataSource或真实数据源）
    
    // 配置选项
    this.config = {
      // 传输间隔（ms）
      staticDataInterval: 5000,    // 静态数据每5秒发送一次
      dynamicDataInterval: 1000,   // 动态数据每1秒发送一次
      
      // 数据压缩
      enableCompression: options.enableCompression ?? true,
      compressionThreshold: options.compressionThreshold ?? 1024, // 超过1KB才压缩
      
      // 优先级管理
      enablePriority: options.enablePriority ?? true,
      criticalPriority: ['emergency', 'structure', 'mainEngine'], // 关键数据
      highPriority: ['fuel', 'rudder', 'propulsion'],
      normalPriority: ['personnel', 'inventory', 'experiment'],
      lowPriority: ['environment', 'targets'],
      
      // 数据筛选
      enableFiltering: options.enableFiltering ?? true,
      filterThreshold: options.filterThreshold ?? 0.01, // 变化超过1%才发送
      
      // 批次大小
      batchSize: options.batchSize ?? 50, // 每批最多50条数据
      
      // 模拟网络延迟（ms）
      networkLatency: options.networkLatency ?? 100,
      
      // 模拟网络丢包率（0-1）
      packetLossRate: options.packetLossRate ?? 0.01
    };
    
    // 状态
    this.isConnected = false;
    this.isSending = false;
    this.lastStaticSend = 0;
    this.lastDynamicSend = 0;
    
    // 数据缓存
    this.staticDataCache = new Map(); // 静态数据缓存
    this.dynamicDataCache = new Map(); // 动态数据缓存
    this.lastSentValues = new Map(); // 上次发送的值，用于变化检测
    
    // 传输队列
    this.transmissionQueue = [];
    this.priorityQueue = [];
    
    // 统计数据
    this.stats = {
      staticDataSent: 0,
      dynamicDataSent: 0,
      totalBytesSent: 0,
      totalBytesCompressed: 0,
      packetsDropped: 0,
      averageLatency: 0
    };
  }

  /**
   * 连接到岸端系统
   */
  connect() {
    if (this.isConnected) {
      console.warn('⚠️ Already connected to shore system');
      return;
    }
    
    this.isConnected = true;
    this.isSending = true;
    
    console.log('📡 Connected to shore system');
    this.emit('connected');
    
    // 立即发送一次静态数据
    this.sendStaticData();
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (!this.isConnected) {
      return;
    }
    
    this.isConnected = false;
    this.isSending = false;
    
    console.log('📡 Disconnected from shore system');
    this.emit('disconnected');
  }

  /**
   * 更新同步系统
   */
  update(deltaTime) {
    if (!this.isConnected || !this.isSending) return;
    
    const now = Date.now();
    
    // 发送静态数据（低频）
    if (now - this.lastStaticSend >= this.config.staticDataInterval) {
      this.sendStaticData();
      this.lastStaticSend = now;
    }
    
    // 发送动态数据（高频）
    if (now - this.lastDynamicSend >= this.config.dynamicDataInterval) {
      this.sendDynamicData();
      this.lastDynamicSend = now;
    }
    
    // 处理传输队列
    this._processTransmissionQueue();
  }

  /**
   * 发送静态数据批次
   */
  sendStaticData() {
    if (!this.dataSource) return;
    
    try {
      const data = this.dataSource.getRealtimeData();
      
      // 提取静态数据（船体基本信息）
      const staticData = {
        timestamp: Date.now(),
        type: 'static',
        shipInfo: {
          id: 'SHIP-001',
          name: '数字孪生船舶',
          length: 100,
          width: 20,
          height: 10,
          mass: 7000,
          draftDepth: 1.2
        },
        equipment: {
          mainEngine: {
            model: 'Diesel Engine 5000HP',
            installedDate: '2020-01-15'
          },
          rudder: {
            type: 'Hydraulic Rudder',
            maxAngle: 35
          },
          propulsion: {
            type: 'Fixed Pitch Propeller',
            diameter: 3.5
          }
        },
        structure: {
          material: 'Steel',
          buildYear: 2020,
          classification: 'CCS'
        }
      };
      
      // 数据筛选和压缩
      const processedData = this._processData(staticData, 'static');
      
      // 添加到传输队列
      this._addToQueue(processedData, 'critical');
      
      this.stats.staticDataSent++;
      
    } catch (error) {
      console.error('❌ Error sending static data:', error);
    }
  }

  /**
   * 发送动态数据批次
   */
  sendDynamicData() {
    if (!this.dataSource) return;
    
    try {
      const data = this.dataSource.getRealtimeData();
      
      // 提取动态数据（实时变化的数据）
      const dynamicData = {
        timestamp: Date.now(),
        type: 'dynamic',
        position: {
          x: this.shipController?.body?.position?.x || 0,
          y: this.shipController?.body?.position?.y || 0,
          z: this.shipController?.body?.position?.z || 0
        },
        orientation: {
          x: this.shipController?.body?.quaternion?.x || 0,
          y: this.shipController?.body?.quaternion?.y || 0,
          z: this.shipController?.body?.quaternion?.z || 0,
          w: this.shipController?.body?.quaternion?.w || 1
        },
        velocity: {
          x: this.shipController?.body?.velocity?.x || 0,
          y: this.shipController?.body?.velocity?.y || 0,
          z: this.shipController?.body?.velocity?.z || 0
        },
        mainEngine: data.mainEngine ? {
          temperature: data.mainEngine.temperature,
          rpm: data.mainEngine.rpm,
          pressure: data.mainEngine.pressure
        } : null,
        fuel: data.fuel ? {
          level: data.fuel.level,
          consumption: data.fuel.consumption,
          flow: data.fuel.flow
        } : null,
        rudder: data.rudder ? {
          angle: data.rudder.angle,
          health: data.rudder.health
        } : null,
        propulsion: data.propulsion ? {
          health: data.propulsion.health,
          efficiency: data.propulsion.efficiency
        } : null,
        structure: data.structure ? {
          stress: data.structure.stress
        } : null,
        emergency: data.emergency ? {
          firePump: data.emergency.firePump,
          lifeboat: data.emergency.lifeboat
        } : null
      };
      
      // 数据筛选（只发送变化的数据）
      const filteredData = this._filterChangedData(dynamicData);
      if (!filteredData || Object.keys(filteredData).length <= 2) {
        return; // 没有变化，不发送
      }
      
      // 数据压缩和优先级处理
      const processedData = this._processData(filteredData, 'dynamic');
      
      // 确定优先级
      const priority = this._determinePriority(filteredData);
      
      // 添加到传输队列
      this._addToQueue(processedData, priority);
      
      this.stats.dynamicDataSent++;
      
    } catch (error) {
      console.error('❌ Error sending dynamic data:', error);
    }
  }

  /**
   * 处理数据（压缩、格式化）
   * @private
   */
  _processData(data, type) {
    let processed = JSON.stringify(data);
    const originalSize = new Blob([processed]).size;
    
    // 数据压缩（如果启用且数据较大）
    if (this.config.enableCompression && originalSize > this.config.compressionThreshold) {
      // 简化实现：移除不必要的空格和换行
      processed = processed.replace(/\s+/g, ' ').trim();
      
      const compressedSize = new Blob([processed]).size;
      this.stats.totalBytesCompressed += (originalSize - compressedSize);
    }
    
    this.stats.totalBytesSent += new Blob([processed]).size;
    
    return {
      data: processed,
      type: type,
      size: new Blob([processed]).size,
      timestamp: Date.now()
    };
  }

  /**
   * 筛选变化的数据
   * @private
   */
  _filterChangedData(data) {
    if (!this.config.enableFiltering) {
      return data;
    }
    
    const filtered = {
      timestamp: data.timestamp,
      type: data.type
    };
    
    // 检查每个字段的变化
    Object.keys(data).forEach(key => {
      if (key === 'timestamp' || key === 'type') return;
      
      const currentValue = data[key];
      const lastValue = this.lastSentValues.get(key);
      
      // 如果是对象，递归检查
      if (typeof currentValue === 'object' && currentValue !== null) {
        const changed = this._hasObjectChanged(currentValue, lastValue);
        if (changed) {
          filtered[key] = currentValue;
          this.lastSentValues.set(key, JSON.parse(JSON.stringify(currentValue)));
        }
      } else {
        // 简单值，检查变化阈值
        if (lastValue === undefined || 
            Math.abs(currentValue - lastValue) / Math.max(Math.abs(lastValue), 1) > this.config.filterThreshold) {
          filtered[key] = currentValue;
          this.lastSentValues.set(key, currentValue);
        }
      }
    });
    
    return filtered;
  }

  /**
   * 检查对象是否变化
   * @private
   */
  _hasObjectChanged(current, last) {
    if (!last) return true;
    if (typeof current !== typeof last) return true;
    
    if (Array.isArray(current)) {
      if (!Array.isArray(last) || current.length !== last.length) return true;
      for (let i = 0; i < current.length; i++) {
        if (this._hasObjectChanged(current[i], last[i])) return true;
      }
      return false;
    }
    
    if (typeof current === 'object') {
      const currentKeys = Object.keys(current);
      const lastKeys = Object.keys(last);
      if (currentKeys.length !== lastKeys.length) return true;
      
      for (const key of currentKeys) {
        if (this._hasObjectChanged(current[key], last[key])) return true;
      }
      return false;
    }
    
    return Math.abs(current - last) / Math.max(Math.abs(last), 1) > this.config.filterThreshold;
  }

  /**
   * 确定数据优先级
   * @private
   */
  _determinePriority(data) {
    if (!this.config.enablePriority) {
      return 'normal';
    }
    
    // 检查是否包含关键数据
    for (const key of this.config.criticalPriority) {
      if (data[key] !== undefined) {
        return 'critical';
      }
    }
    
    // 检查是否包含高优先级数据
    for (const key of this.config.highPriority) {
      if (data[key] !== undefined) {
        return 'high';
      }
    }
    
    // 检查是否包含低优先级数据
    for (const key of this.config.lowPriority) {
      if (data[key] !== undefined) {
        return 'low';
      }
    }
    
    return 'normal';
  }

  /**
   * 添加到传输队列
   * @private
   */
  _addToQueue(data, priority) {
    const queueItem = {
      data: data,
      priority: priority,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    // 根据优先级添加到不同队列
    if (priority === 'critical') {
      this.priorityQueue.unshift(queueItem); // 关键数据插到前面
    } else {
      this.transmissionQueue.push(queueItem);
    }
    
    // 限制队列大小
    if (this.transmissionQueue.length > this.config.batchSize * 2) {
      this.transmissionQueue.shift(); // 移除最旧的数据
    }
    if (this.priorityQueue.length > this.config.batchSize) {
      this.priorityQueue.shift();
    }
  }

  /**
   * 处理传输队列
   * @private
   */
  _processTransmissionQueue() {
    // 优先处理关键数据队列
    while (this.priorityQueue.length > 0) {
      const item = this.priorityQueue.shift();
      this._sendDataItem(item);
    }
    
    // 处理普通队列（批次发送）
    const batch = [];
    while (this.transmissionQueue.length > 0 && batch.length < this.config.batchSize) {
      batch.push(this.transmissionQueue.shift());
    }
    
    if (batch.length > 0) {
      this._sendBatch(batch);
    }
  }

  /**
   * 发送单个数据项
   * @private
   */
  _sendDataItem(item) {
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟丢包
      if (Math.random() < this.config.packetLossRate) {
        this.stats.packetsDropped++;
        console.warn('⚠️ Packet dropped:', item.priority);
        return;
      }
      
      // 发送数据（实际应该通过WebSocket或HTTP发送到岸端）
      this.emit('dataSent', {
        data: item.data,
        priority: item.priority,
        timestamp: item.timestamp
      });
      
      // 更新延迟统计
      const latency = Date.now() - item.timestamp;
      this.stats.averageLatency = 
        (this.stats.averageLatency * (this.stats.staticDataSent + this.stats.dynamicDataSent - 1) + latency) /
        (this.stats.staticDataSent + this.stats.dynamicDataSent);
      
    }, this.config.networkLatency);
  }

  /**
   * 批量发送数据
   * @private
   */
  _sendBatch(batch) {
    // 合并批次数据
    const batchData = {
      timestamp: Date.now(),
      type: 'batch',
      count: batch.length,
      items: batch.map(item => item.data)
    };
    
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟丢包
      if (Math.random() < this.config.packetLossRate) {
        this.stats.packetsDropped += batch.length;
        console.warn(`⚠️ Batch dropped: ${batch.length} items`);
        return;
      }
      
      // 发送批次数据
      this.emit('batchSent', {
        data: batchData,
        timestamp: Date.now()
      });
      
    }, this.config.networkLatency);
  }

  /**
   * 设置船体控制器引用（用于获取位置和姿态）
   */
  setShipController(shipController) {
    this.shipController = shipController;
  }

  /**
   * 获取统计数据
   */
  getStats() {
    return {
      ...this.stats,
      queueSize: this.transmissionQueue.length,
      priorityQueueSize: this.priorityQueue.length,
      isConnected: this.isConnected,
      compressionRatio: this.stats.totalBytesSent > 0 
        ? (this.stats.totalBytesCompressed / this.stats.totalBytesSent * 100).toFixed(2) + '%'
        : '0%'
    };
  }

  /**
   * 重置统计数据
   */
  resetStats() {
    this.stats = {
      staticDataSent: 0,
      dynamicDataSent: 0,
      totalBytesSent: 0,
      totalBytesCompressed: 0,
      packetsDropped: 0,
      averageLatency: 0
    };
  }
}



