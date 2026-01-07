/**
 * 虚拟数据源
 * 用于开发阶段模拟真实系统数据
 */

import { IDataSource } from './DataInterfaceManager.js';

export class VirtualDataSource extends IDataSource {
  constructor(config = {}) {
    super('virtual');
    this.config = config;
    this.data = this._initializeData();
    this.simulationMode = true;
    this.updateInterval = config.updateInterval || 1000; // ms
    this.lastUpdate = Date.now();
  }

  /**
   * 初始化虚拟数据结构
   * @private
   */
  _initializeData() {
    return {
      ship: {
        // 基本信息
        info: {
          id: 'SHIP-001',
          name: 'Digital Twin Vessel',
          type: 'Research Vessel',
          length: 100,
          beam: 20,
          draft: 10
        },
        
        // 燃油系统
        fuel: {
          level: 75.5,          // % (0-100)
          flowRate: 12.3,       // L/h
          remaining: 45000,     // L
          capacity: 60000,      // L
          efficiency: 0.85,     // 效率
          temperature: 35.2,    // °C
          pressure: 2.3,        // bar
          quality: 'Good'
        },
        
        // 主机系统
        mainEngine: {
          status: 'Running',
          rpm: 1200,
          power: 5400,          // kW
          temperature: 78.5,    // °C
          oilPressure: 4.5,     // bar
          coolantTemp: 65.3,    // °C
          vibration: 0.8,       // mm/s
          health: 95,           // % (0-100)
          runningHours: 15234.5 // 小时
        },
        
        // 舵机系统
        rudder: {
          status: 'Normal',
          angle: 0,             // 度 (-35 to 35)
          speed: 2.5,           // 度/s
          hydraulicPressure: 150, // bar
          motorCurrent: 12.3,   // A
          health: 98            // %
        },
        
        // 推进系统
        propulsion: {
          status: 'Normal',
          thrust: 75,           // % (0-100)
          pitch: 15.5,          // 度
          rpm: 180,
          cavitation: 'None',
          efficiency: 0.88,
          health: 96            // %
        },
        
        // 结构应力
        structure: {
          bow: {
            stress: 45.2,       // MPa
            strain: 0.002,      // 无量纲
            fatigue: 15.3,      // %
            status: 'Normal'
          },
          midship: {
            stress: 38.7,
            strain: 0.0015,
            fatigue: 12.1,
            status: 'Normal'
          },
          stern: {
            stress: 42.8,
            strain: 0.0018,
            fatigue: 14.5,
            status: 'Normal'
          }
        },
        
        // 吊机设备
        crane: {
          status: 'Standby',
          load: 0,              // kg
          capacity: 5000,       // kg
          angle: 0,             // 度
          extension: 0,         // m
          acceleration: {
            x: 0.02,            // g
            y: 0.01,
            z: 0.03
          },
          health: 94            // %
        },
        
        // 人员情况
        personnel: {
          total: 28,
          onDuty: 8,
          offDuty: 20,
          locations: {
            bridge: 3,
            engineRoom: 2,
            deck: 1,
            accommodation: 20,
            laboratory: 2
          },
          alerts: []
        },
        
        // 物资仓储
        storage: {
          food: {
            level: 68,          // %
            daysRemaining: 45
          },
          water: {
            level: 82,          // %
            liters: 49200
          },
          fuelOil: {
            level: 75.5,        // %
            liters: 45000
          },
          spareParts: {
            level: 55,          // %
            criticalItems: 12
          }
        },
        
        // 实验任务
        experiments: {
          total: 5,
          completed: 3,
          inProgress: 2,
          pending: 0,
          completionRate: 60,  // %
          current: {
            id: 'EXP-004',
            name: 'Ocean Current Measurement',
            progress: 45,       // %
            duration: 120,      // minutes
            elapsed: 54         // minutes
          }
        },
        
        // 应急设备
        emergency: {
          firePump: {
            status: 'Ready',
            pressure: 8.5,      // bar
            lastTest: '2025-12-20',
            health: 100         // %
          },
          lifeBoats: {
            total: 4,
            ready: 4,
            capacity: 120,      // persons
            lastInspection: '2025-12-15'
          },
          fireExtinguishers: {
            total: 45,
            ready: 43,
            expired: 2
          },
          emergencyGenerator: {
            status: 'Standby',
            fuel: 85,           // %
            lastTest: '2025-12-18',
            health: 98          // %
          }
        }
      },
      
      // 环境数据
      environment: {
        wind: {
          speed: 5.2,           // m/s
          direction: 180,       // 度
          gust: 7.8             // m/s
        },
        wave: {
          height: 1.2,          // m
          period: 6.5,          // s
          direction: 175        // 度
        },
        rain: {
          intensity: 0,         // mm/h
          accumulated: 0        // mm
        },
        temperature: {
          air: 22.5,            // °C
          water: 18.3           // °C
        },
        visibility: 10000,      // m
        seaState: 2,            // 道格拉斯海况等级 (0-9)
        barometer: 1013.2       // hPa
      },
      
      // 其他海上目标
      targets: [
        {
          id: 'TARGET-001',
          type: 'Vessel',
          name: 'Cargo Ship',
          distance: 5200,       // m
          bearing: 45,          // 度 (修复：移除前导0，避免八进制字面量错误)
          speed: 12,            // knots
          course: 180           // 度
        },
        {
          id: 'TARGET-002',
          type: 'Buoy',
          name: 'Navigation Buoy',
          distance: 1800,
          bearing: 280
        }
      ]
    };
  }

  initialize() {
    console.log('✅ Virtual data source initialized');
    this._startSimulation();
  }

  /**
   * 启动数据模拟
   * @private
   */
  _startSimulation() {
    if (this.simulationMode) {
      this._simulationTimer = setInterval(() => {
        this._updateSimulatedData();
      }, this.updateInterval);
    }
  }

  /**
   * 更新模拟数据（添加随机波动）
   * @private
   */
  _updateSimulatedData() {
    const now = Date.now();
    const dt = (now - this.lastUpdate) / 1000; // 秒
    this.lastUpdate = now;

    // 燃油消耗
    this.data.ship.fuel.level -= 0.001 * dt;
    this.data.ship.fuel.remaining = 
      (this.data.ship.fuel.level / 100) * this.data.ship.fuel.capacity;

    // 主机参数波动
    this.data.ship.mainEngine.rpm += (Math.random() - 0.5) * 20;
    this.data.ship.mainEngine.temperature += (Math.random() - 0.5) * 2;
    this.data.ship.mainEngine.vibration = 0.5 + Math.random() * 0.5;

    // 吊机加速度（模拟船体摇晃）
    this.data.ship.crane.acceleration.x = (Math.random() - 0.5) * 0.1;
    this.data.ship.crane.acceleration.y = (Math.random() - 0.5) * 0.05;
    this.data.ship.crane.acceleration.z = (Math.random() - 0.5) * 0.12;

    // 环境数据波动
    this.data.environment.wind.speed += (Math.random() - 0.5) * 0.5;
    this.data.environment.wind.speed = Math.max(0, this.data.environment.wind.speed);
    
    this.data.environment.wave.height += (Math.random() - 0.5) * 0.2;
    this.data.environment.wave.height = Math.max(0, this.data.environment.wave.height);

    // 实验进度
    if (this.data.ship.experiments.current) {
      this.data.ship.experiments.current.elapsed += dt / 60; // 转换为分钟
      this.data.ship.experiments.current.progress = 
        (this.data.ship.experiments.current.elapsed / 
         this.data.ship.experiments.current.duration) * 100;
    }
  }

  /**
   * 获取数据（支持路径访问）
   * @param {string} path - 例如: "ship.fuel.level"
   */
  getData(path) {
    const parts = path.split('.');
    let value = this.data;
    
    for (const part of parts) {
      if (value && typeof value === 'object' && part in value) {
        value = value[part];
      } else {
        console.warn(`Data path not found: ${path}`);
        return null;
      }
    }
    
    return value;
  }

  /**
   * 设置数据
   * @param {string} path 
   * @param {any} value 
   */
  setData(path, value) {
    const parts = path.split('.');
    const lastPart = parts.pop();
    let obj = this.data;
    
    for (const part of parts) {
      if (!(part in obj)) {
        obj[part] = {};
      }
      obj = obj[part];
    }
    
    obj[lastPart] = value;
  }

  /**
   * 获取所有数据
   */
  getAllData() {
    return this.data;
  }

  /**
   * 获取实时数据（用于显示系统）
   * 返回格式化的实时数据，便于显示系统使用
   */
  getRealtimeData() {
    return {
      // 燃油数据
      fuel: {
        level: this.data.ship.fuel.level,
        remaining: this.data.ship.fuel.remaining,
        capacity: this.data.ship.fuel.capacity,
        flowRate: this.data.ship.fuel.flowRate
      },
      
      // 设备数据
      equipment: {
        crane: {
          status: this.data.ship.crane.status === 'Standby' ? 'normal' : 
                 this.data.ship.crane.health < 80 ? 'fault' : 'warning',
          acceleration: this.data.ship.crane.acceleration,
          load: this.data.ship.crane.load,
          capacity: this.data.ship.crane.capacity
        },
        mainEngine: {
          status: this.data.ship.mainEngine.status,
          rpm: this.data.ship.mainEngine.rpm,
          power: this.data.ship.mainEngine.power,
          health: this.data.ship.mainEngine.health
        }
      },
      
      // 人员数据
      personnel: {
        total: this.data.ship.personnel.total,
        onDuty: this.data.ship.personnel.onDuty,
        positions: [
          { x: 10, y: 2, z: 5 },   // 示例位置
          { x: -8, y: 1, z: 3 },
          { x: 5, y: 1.5, z: -4 }
        ]
      },
      
      // 实验数据
      experiment: {
        progress: this.data.ship.experiments.current?.progress || 0,
        name: this.data.ship.experiments.current?.name || 'No active experiment',
        completed: this.data.ship.experiments.completed,
        total: this.data.ship.experiments.total
      },
      
      // 仓储数据
      inventory: {
        level: this.data.ship.storage.spareParts.level > 50 ? 'sufficient' :
               this.data.ship.storage.spareParts.level > 20 ? 'low' : 'critical',
        spareParts: this.data.ship.storage.spareParts.level,
        food: this.data.ship.storage.food.level,
        water: this.data.ship.storage.water.level
      },
      
      // 环境数据
      environment: {
        wind: {
          speed: this.data.environment.wind.speed,
          direction: this.data.environment.wind.direction,
          gust: this.data.environment.wind.gust
        },
        wave: {
          height: this.data.environment.wave.height,
          period: this.data.environment.wave.period,
          direction: this.data.environment.wave.direction
        },
        rain: {
          intensity: this.data.environment.rain.intensity
        },
        seaState: this.data.environment.seaState
      },
      
      // 海上目标
      maritimeTargets: this.data.targets.map(target => ({
        x: Math.cos(target.bearing * Math.PI / 180) * (target.distance / 100),
        y: 0.5,
        z: Math.sin(target.bearing * Math.PI / 180) * (target.distance / 100),
        type: target.type,
        name: target.name
      }))
    };
  }

  /**
   * 停止模拟
   */
  dispose() {
    if (this._simulationTimer) {
      clearInterval(this._simulationTimer);
      this._simulationTimer = null;
    }
    console.log('🔌 Virtual data source disposed');
  }
}

