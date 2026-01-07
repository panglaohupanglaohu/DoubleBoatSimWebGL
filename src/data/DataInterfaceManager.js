/**
 * 数据接口管理器
 * 管理虚拟数据源和真实系统的对接
 * 支持可视化连线配置
 */

import { EventEmitter } from '../utils/EventEmitter.js';

export class DataInterfaceManager extends EventEmitter {
  constructor() {
    super();
    this.dataSources = new Map(); // 数据源映射
    this.dataBindings = new Map(); // 数据绑定映射 (virtualObject -> dataSource)
    this.subscriptions = new Map(); // 订阅管理
    this.isConnected = false;
  }

  /**
   * 注册数据源
   * @param {string} id - 数据源ID
   * @param {IDataSource} dataSource - 数据源实例
   */
  registerDataSource(id, dataSource) {
    if (this.dataSources.has(id)) {
      console.warn(`Data source "${id}" already registered, replacing...`);
    }

    this.dataSources.set(id, dataSource);
    
    if (dataSource.initialize) {
      dataSource.initialize();
    }

    this.emit('datasource:registered', { id, type: dataSource.type });
    console.log(`✅ Data source registered: ${id} (${dataSource.type})`);
  }

  /**
   * 移除数据源
   * @param {string} id 
   */
  unregisterDataSource(id) {
    const dataSource = this.dataSources.get(id);
    if (dataSource) {
      if (dataSource.dispose) {
        dataSource.dispose();
      }
      this.dataSources.delete(id);
      this.emit('datasource:unregistered', { id });
      console.log(`❌ Data source unregistered: ${id}`);
    }
  }

  /**
   * 绑定虚拟对象到数据源
   * @param {string} objectId - 虚拟对象ID
   * @param {string} dataSourceId - 数据源ID
   * @param {string} dataPath - 数据路径 (例如: "ship.fuel.level")
   * @param {function} transformer - 数据转换函数（可选）
   */
  bindData(objectId, dataSourceId, dataPath, transformer = null) {
    const dataSource = this.dataSources.get(dataSourceId);
    if (!dataSource) {
      console.error(`Data source "${dataSourceId}" not found`);
      return false;
    }

    const binding = {
      objectId,
      dataSourceId,
      dataPath,
      transformer,
      lastValue: null,
      lastUpdate: 0
    };

    this.dataBindings.set(objectId, binding);
    this.emit('binding:created', binding);
    
    console.log(`🔗 Data binding created: ${objectId} <- ${dataSourceId}.${dataPath}`);
    return true;
  }

  /**
   * 解绑数据
   * @param {string} objectId 
   */
  unbindData(objectId) {
    const binding = this.dataBindings.get(objectId);
    if (binding) {
      this.dataBindings.delete(objectId);
      this.emit('binding:removed', { objectId });
      console.log(`🔓 Data binding removed: ${objectId}`);
      return true;
    }
    return false;
  }

  /**
   * 订阅数据更新
   * @param {string} objectId 
   * @param {function} callback 
   */
  subscribe(objectId, callback) {
    if (!this.subscriptions.has(objectId)) {
      this.subscriptions.set(objectId, []);
    }
    this.subscriptions.get(objectId).push(callback);
    
    return () => this.unsubscribe(objectId, callback);
  }

  /**
   * 取消订阅
   * @param {string} objectId 
   * @param {function} callback 
   */
  unsubscribe(objectId, callback) {
    const callbacks = this.subscriptions.get(objectId);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * 更新所有绑定的数据
   * @param {number} deltaTime 
   */
  update(deltaTime) {
    for (const [objectId, binding] of this.dataBindings) {
      try {
        // 从数据源获取数据
        const dataSource = this.dataSources.get(binding.dataSourceId);
        if (!dataSource) continue;

        const rawValue = dataSource.getData(binding.dataPath);
        
        // 应用转换器
        const value = binding.transformer 
          ? binding.transformer(rawValue) 
          : rawValue;

        // 检查值是否变化
        if (value !== binding.lastValue) {
          binding.lastValue = value;
          binding.lastUpdate = Date.now();

          // 通知订阅者
          this._notifySubscribers(objectId, value);
        }
      } catch (error) {
        console.error(`Error updating binding for ${objectId}:`, error);
      }
    }
  }

  /**
   * 通知订阅者
   * @private
   */
  _notifySubscribers(objectId, value) {
    const callbacks = this.subscriptions.get(objectId);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(value);
        } catch (error) {
          console.error(`Error in subscription callback for ${objectId}:`, error);
        }
      });
    }
    
    this.emit('data:updated', { objectId, value });
  }

  /**
   * 获取当前值
   * @param {string} objectId 
   */
  getValue(objectId) {
    const binding = this.dataBindings.get(objectId);
    return binding ? binding.lastValue : null;
  }

  /**
   * 导出配置（用于保存和加载）
   */
  exportConfig() {
    const bindings = [];
    for (const [objectId, binding] of this.dataBindings) {
      bindings.push({
        objectId,
        dataSourceId: binding.dataSourceId,
        dataPath: binding.dataPath,
        // transformer 函数不能序列化，需要通过名称引用
      });
    }

    return {
      bindings,
      dataSources: Array.from(this.dataSources.keys()).map(id => {
        const ds = this.dataSources.get(id);
        return {
          id,
          type: ds.type,
          config: ds.config || {}
        };
      })
    };
  }

  /**
   * 导入配置
   * @param {object} config 
   */
  importConfig(config) {
    // 清除现有绑定
    this.dataBindings.clear();
    
    // 重新创建绑定
    config.bindings.forEach(binding => {
      this.bindData(
        binding.objectId,
        binding.dataSourceId,
        binding.dataPath
      );
    });

    this.emit('config:imported', config);
    console.log(`📥 Configuration imported: ${config.bindings.length} bindings`);
  }

  /**
   * 获取绑定信息
   */
  getBindings() {
    const result = [];
    for (const [objectId, binding] of this.dataBindings) {
      result.push({
        objectId,
        dataSourceId: binding.dataSourceId,
        dataPath: binding.dataPath,
        lastValue: binding.lastValue,
        lastUpdate: binding.lastUpdate
      });
    }
    return result;
  }

  /**
   * 连接到真实系统
   */
  async connect() {
    try {
      // 连接所有数据源
      for (const [id, dataSource] of this.dataSources) {
        if (dataSource.connect) {
          await dataSource.connect();
        }
      }
      
      this.isConnected = true;
      this.emit('connected');
      console.log('✅ Connected to real system');
      return true;
    } catch (error) {
      console.error('❌ Failed to connect:', error);
      this.emit('connection:error', error);
      return false;
    }
  }

  /**
   * 断开连接
   */
  async disconnect() {
    try {
      for (const [id, dataSource] of this.dataSources) {
        if (dataSource.disconnect) {
          await dataSource.disconnect();
        }
      }
      
      this.isConnected = false;
      this.emit('disconnected');
      console.log('🔌 Disconnected from real system');
    } catch (error) {
      console.error('Error disconnecting:', error);
    }
  }

  /**
   * 清理所有资源
   */
  dispose() {
    this.disconnect();
    
    for (const [id, dataSource] of this.dataSources) {
      this.unregisterDataSource(id);
    }
    
    this.dataBindings.clear();
    this.subscriptions.clear();
    this.removeAllListeners();
  }
}

/**
 * 数据源接口定义
 */
export class IDataSource {
  constructor(type) {
    this.type = type; // 'virtual', 'graphql', 'rest', 'websocket'
    this.config = {};
  }

  /**
   * 初始化数据源
   */
  initialize() {
    // Override in subclass
  }

  /**
   * 连接到数据源
   */
  async connect() {
    // Override in subclass
  }

  /**
   * 断开连接
   */
  async disconnect() {
    // Override in subclass
  }

  /**
   * 获取数据
   * @param {string} path - 数据路径
   */
  getData(path) {
    // Override in subclass
    return null;
  }

  /**
   * 设置数据
   * @param {string} path 
   * @param {any} value 
   */
  setData(path, value) {
    // Override in subclass
  }

  /**
   * 清理资源
   */
  dispose() {
    // Override in subclass
  }
}

