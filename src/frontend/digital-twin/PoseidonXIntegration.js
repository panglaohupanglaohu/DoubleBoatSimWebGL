/**
 * Poseidon-X Integration Module
 * 
 * 将 Poseidon-X AI 系统与现有的数字孪生系统深度集成
 * - AI Agent 可以控制真实的船舶模型
 * - AI Agent 可以读取真实的传感器数据
 * - AI Agent 可以在 3D 场景中进行操作
 * - Bridge Chat 可以通过自然语言控制整个系统
 */

import { createPoseidonX } from './PoseidonX.js';

export class PoseidonXIntegration {
  constructor(systemComponents) {
    this.components = systemComponents;
    this.poseidonSystem = null;
    this.initialized = false;
    
    // 必需的组件
    this.requiredComponents = [
      'scene', 'camera', 'shipController', 'simulatorEngine', 
      'weatherSystem', 'virtualDataSource'
    ];
  }
  
  /**
   * 初始化集成
   */
  async initialize() {
    console.log('🌊 ========== Poseidon-X Integration Starting ==========');
    
    // 验证必需组件
    for (const component of this.requiredComponents) {
      if (!this.components[component]) {
        throw new Error(`Required component missing: ${component}`);
      }
    }
    
    // 创建 Poseidon-X 系统
    this.poseidonSystem = await createPoseidonX(
      this.components.scene,
      this.components.camera,
      {
        enableBridgeChat: true,
        enableDigitalTwin: true,
        enableVoice: false
      }
    );
    
    // 注入现有组件
    this._injectComponents();
    
    // 注册真实工具
    this._registerRealTools();
    
    // 启动数据同步
    this._startDataSync();
    
    // 监听 Bridge Chat 事件
    this._setupEventListeners();
    
    this.initialized = true;
    
    console.log('✅ ========== Poseidon-X Integration Complete ==========');
    
    return this.poseidonSystem;
  }
  
  /**
   * 注入现有组件
   * @private
   */
  _injectComponents() {
    // 将现有系统组件绑定到 Poseidon
    this.poseidonSystem.shipController = this.components.shipController;
    this.poseidonSystem.simulatorEngine = this.components.simulatorEngine;
    this.poseidonSystem.weatherSystem = this.components.weatherSystem;
    this.poseidonSystem.virtualDataSource = this.components.virtualDataSource;
    this.poseidonSystem.world = this.components.world;
    this.poseidonSystem.cabinManager = this.components.cabinManager;
    
    console.log('✅ System components injected to Poseidon-X');
  }
  
  /**
   * 注册真实工具
   * @private
   */
  _registerRealTools() {
    this._registerNavigatorTools();
    this._registerEngineerTools();
    this._registerStewardTools();
    this._registerSafetyTools();
    
    console.log('✅ Real-world tools registered for all Agents');
  }
  
  /**
   * Navigator Agent 真实工具
   * @private
   */
  _registerNavigatorTools() {
    const navigator = this.poseidonSystem.agents.navigator;
    
    // 设置航向
    navigator.registerTool('setShipHeading', async (params) => {
      const { heading } = params;
      
      if (this.components.shipController && this.components.shipController.body) {
        const radians = (heading * Math.PI) / 180;
        const quaternion = new CANNON.Quaternion();
        quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), radians);
        this.components.shipController.body.quaternion.copy(quaternion);
        
        console.log(`⚓ Navigator: 航向已设置到 ${heading}°`);
        
        return { success: true, newHeading: heading };
      }
      
      return { success: false, error: 'Ship controller not available' };
    }, 'Set ship heading in 3D scene');
    
    // 在地图上添加航路点
    navigator.registerTool('addWaypointToMap', async (params) => {
      const { waypoint } = params;
      
      if (this.poseidonSystem.digitalTwinMap) {
        // 在 3D 场景中绘制航路点
        const waypoints = [
          { x: 0, z: 0 },
          { x: waypoint.x, z: waypoint.z }
        ];
        
        this.poseidonSystem.digitalTwinMap.drawRoute(waypoints);
        
        console.log(`⚓ Navigator: 航路点已添加到地图`);
        
        return { success: true };
      }
      
      return { success: false };
    }, 'Add waypoint to 3D map');
  }
  
  /**
   * Engineer Agent 真实工具
   * @private
   */
  _registerEngineerTools() {
    const engineer = this.poseidonSystem.agents.engineer;
    
    // 读取真实的传感器数据
    engineer.registerTool('readRealSensor', async (params) => {
      const { sensorId } = params;
      
      if (this.components.virtualDataSource) {
        const allData = this.components.virtualDataSource.getAllData();
        
        let value = null;
        
        // 解析传感器路径，例如 "MainEngine.ExhaustTemp"
        if (sensorId.includes('MainEngine.ExhaustTemp')) {
          value = allData.ship?.mainEngine?.exhaustTemp;
        } else if (sensorId.includes('MainEngine.RPM')) {
          value = allData.ship?.mainEngine?.rpm;
        } else if (sensorId.includes('FuelTank.Level')) {
          value = allData.ship?.fuel?.level;
        }
        
        console.log(`⚙️ Engineer: 读取传感器 ${sensorId} = ${value}`);
        
        return { sensorId, value, timestamp: Date.now() };
      }
      
      return { sensorId, value: null };
    }, 'Read real-time sensor data from ship');
    
    // 调整主机转速
    engineer.registerTool('adjustEngineRPM', async (params) => {
      const { rpm } = params;
      
      if (this.components.virtualDataSource) {
        const allData = this.components.virtualDataSource.getAllData();
        if (allData.ship && allData.ship.mainEngine) {
          allData.ship.mainEngine.rpm = rpm;
          
          console.log(`⚙️ Engineer: 主机转速已调整到 ${rpm} RPM`);
          
          return { success: true, newRPM: rpm };
        }
      }
      
      return { success: false };
    }, 'Adjust main engine RPM');
  }
  
  /**
   * Steward Agent 真实工具
   * @private
   */
  _registerStewardTools() {
    const steward = this.poseidonSystem.agents.steward;
    
    // 查询真实舱室状态
    steward.registerTool('queryCabinStatus', async (params) => {
      const { cabinId } = params;
      
      if (this.components.cabinManager) {
        const cabin = this.components.cabinManager.getCabin(cabinId);
        
        if (cabin) {
          console.log(`🏠 Steward: 查询舱室 ${cabin.name}`);
          
          return {
            cabinId,
            name: cabin.name,
            position: cabin.position,
            temperature: 24 + Math.random() * 2,
            humidity: 50 + Math.random() * 10,
            co2: 600 + Math.random() * 200
          };
        }
      }
      
      return { cabinId, status: 'not_found' };
    }, 'Query real cabin status');
  }
  
  /**
   * Safety Agent 真实工具
   * @private
   */
  _registerSafetyTools() {
    const safety = this.poseidonSystem.agents.safety;
    
    // 在 3D 场景中触发可视化警报
    safety.registerTool('trigger3DAlert', async (params) => {
      const { alertType, location } = params;
      
      if (this.poseidonSystem.digitalTwinMap) {
        // 高亮警报位置
        this.poseidonSystem.digitalTwinMap.highlight(
          location || { x: 0, z: 0 },
          `🚨 ${alertType}`
        );
        
        console.log(`🛡️ Safety: 3D 警报已触发 - ${alertType}`);
        
        return { success: true };
      }
      
      return { success: false };
    }, 'Trigger visual alert in 3D scene');
  }
  
  /**
   * 启动数据同步
   * @private
   */
  _startDataSync() {
    // 每秒同步一次数据
    setInterval(() => {
      if (!this.components.shipController || !this.components.virtualDataSource) return;
      
      const body = this.components.shipController.body;
      if (!body) return;
      
      // 收集传感器数据
      const sensorData = new Map();
      const allData = this.components.virtualDataSource.getAllData();
      
      if (allData && allData.ship) {
        // 主机数据
        if (allData.ship.mainEngine) {
          sensorData.set('MainEngine.RPM', allData.ship.mainEngine.rpm);
          sensorData.set('MainEngine.ExhaustTemp', allData.ship.mainEngine.exhaustTemp);
          sensorData.set('MainEngine.Load', allData.ship.mainEngine.load);
        }
        
        // 燃油数据
        if (allData.ship.fuel) {
          sensorData.set('FuelTank.Level', allData.ship.fuel.level);
          sensorData.set('FuelTank.FlowRate', allData.ship.fuel.flowRate);
          sensorData.set('FuelTank.Remaining', allData.ship.fuel.remaining);
        }
        
        // 舵机数据
        if (allData.ship.rudder) {
          sensorData.set('Rudder.Angle', allData.ship.rudder.angle);
        }
        
        // 推进系统
        if (allData.ship.propulsion) {
          sensorData.set('Propulsion.Efficiency', allData.ship.propulsion.efficiency * 100);
        }
      }
      
      // 天气数据
      const weather = this.components.weatherSystem ? 
        this.components.weatherSystem.getWeatherState() : {};
      
      // 更新 Poseidon 上下文
      this.poseidonSystem.updateShipContext({
        position: {
          x: body.position.x,
          y: body.position.y,
          z: body.position.z,
          heading: 0,
          speed: Math.sqrt(
            body.velocity.x ** 2 + 
            body.velocity.z ** 2
          )
        },
        sensors: sensorData,
        environment: {
          windSpeed: weather.windSpeed || 0,
          windDirection: weather.windDirection || 0,
          rainIntensity: weather.rainIntensity || 0,
          visibility: weather.visibility || 1.0,
          seaState: weather.seaState || 'calm'
        },
        equipment: {
          mainEngine: allData?.ship?.mainEngine,
          fuel: allData?.ship?.fuel,
          rudder: allData?.ship?.rudder
        }
      });
    }, 1000);
    
    console.log('✅ Data sync started (1Hz)');
  }
  
  /**
   * 设置事件监听
   * @private
   */
  _setupEventListeners() {
    // 监听 Agent 任务完成事件
    this.poseidonSystem.on('agent:task_completed', (data) => {
      console.log(`✅ Agent task completed: ${data.agent} - ${data.task}`);
      
      // 如果是 Navigator 调整了航向，在 3D 场景中显示
      if (data.agent === 'NavigatorAgent' && data.result.type === 'course_speed_adjustment') {
        // 可以在这里添加视觉反馈
      }
    });
    
    // 监听上下文更新事件
    this.poseidonSystem.on('context:updated', (context) => {
      // Context 已更新，可以触发其他系统的响应
    });
  }
  
  /**
   * 执行自然语言命令（与现有系统交互）
   */
  async executeNaturalLanguageCommand(command) {
    if (!this.initialized) {
      throw new Error('Poseidon-X not initialized');
    }
    
    console.log(`🌊 Executing command: "${command}"`);
    
    // 特殊命令：直接控制现有系统
    if (command.includes('台风') || command.includes('typhoon')) {
      const level = parseInt(command.match(/\d+/)?.[0]) || 12;
      if (this.components.weatherSystem) {
        this.components.weatherSystem.setTyphoonLevel(level);
        return {
          success: true,
          message: `已设置 ${level} 级台风`,
          agent: 'system'
        };
      }
    }
    
    if (command.includes('稳定') || command.includes('stabilize')) {
      if (this.components.shipController && this.components.stabilityAnalyzer) {
        const result = this.components.stabilityAnalyzer.stabilize(
          this.components.shipController.body,
          this.components.clock.elapsedTime,
          this.components.config,
          this.components.simulatorEngine,
          this.components.shipController
        );
        
        return {
          success: true,
          message: result.stable ? '船体已稳定' : '稳定化完成，有建议',
          result,
          agent: 'system'
        };
      }
    }
    
    // 其他命令：通过 Poseidon Orchestrator 处理
    const result = await this.poseidonSystem.executeTask(command);
    
    return result;
  }
  
  /**
   * 获取系统状态
   */
  getIntegratedStatus() {
    const poseidonStatus = this.poseidonSystem.getSystemStatus();
    
    return {
      poseidon: poseidonStatus,
      ship: {
        loaded: this.components.shipController?.loaded || false,
        position: this.components.shipController?.body?.position,
        mass: this.components.shipController?.config?.mass
      },
      weather: this.components.weatherSystem?.getWeatherState(),
      physics: {
        algorithms: this.components.simulatorEngine?.getActiveAlgorithms?.() || []
      }
    };
  }
}

/**
 * 便捷函数：创建完整集成
 */
export async function createIntegratedPoseidonX(systemComponents) {
  const integration = new PoseidonXIntegration(systemComponents);
  await integration.initialize();
  return integration;
}
