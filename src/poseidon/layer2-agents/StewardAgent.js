/**
 * Steward Agent - 大管家智能体
 * 
 * Vibe: "细致入微的后勤总管，不仅管物，更管人。"
 * 
 * 职责：
 * - 仓储管理（RFID 智能仓库）
 * - 伙食管理（菜单生成、营养均衡）
 * - 环境控制（舱室温湿度、CO2、照明）
 * - 船员福祉（疲劳监测、生活质量）
 * 
 * 能力：
 * - 管理 RFID 智能仓库
 * - 根据船员国籍和库存保质期自动生成菜单
 * - 监控舱室环境，自动调节空调和照明
 * - 检测船员疲劳，提供健康建议
 */

import { AgentBase } from './AgentBase.js';

export class StewardAgent extends AgentBase {
  constructor(config = {}) {
    super({
      ...config,
      id: 'steward-agent',
      name: 'Steward Agent',
      role: 'steward',
      vibe: `你是 Poseidon-X 的大管家智能体。
你是一位细致入微的后勤总管，关心每一位船员的生活质量。

核心职责：
1. 仓储管理：跟踪所有物资的位置、数量、保质期
2. 伙食管理：生成营养均衡、符合船员口味的菜单
3. 环境控制：维持舒适的舱室温度、湿度、空气质量
4. 船员福祉：监测船员健康状态，提供生活建议

你的能力：
- RFID 智能仓库管理（实时库存追踪）
- 营养分析和菜单优化
- 环境传感器监控（温湿度、CO2、照度）
- 疲劳检测和健康建议

决策原则：
- 以人为本，关注船员需求
- 未雨绸缪，提前补给
- 节约资源，避免浪费
- 营造温馨的"海上之家"

你的语气温暖亲切，像一位贴心的管家。`,
      deploymentLocation: 'edge'
    });
    
    // 注册工具
    this._registerTools();
    
    // 大管家专属状态
    this.stewardState = {
      inventory: new Map(), // 库存（RFID 数据）
      menu: [], // 菜单计划
      environment: new Map(), // 舱室环境数据
      crewPreferences: new Map(), // 船员偏好
      supplies: {
        freshWater: 0.68, // 淡水余量（百分比）
        food: 0.75,
        medicine: 0.90,
        spareParts: 0.60
      }
    };
    
    this._registerTools();
    this._loadInventoryKnowledge();
    
    console.log('🏠 Steward Agent ready');
  }
  
  /**
   * 执行任务
   */
  async execute(task, context = {}) {
    console.log(`🏠 StewardAgent executing: ${task}`);
    
    const taskLower = task.toLowerCase();
    
    // 根据任务类型选择工具
    try {
      // 库存查询
      if (taskLower.includes('库存') || taskLower.includes('淡水') || taskLower.includes('食物') || taskLower.includes('物资')) {
        let itemName = '淡水'; // 默认查询淡水
        if (taskLower.includes('大米') || taskLower.includes('鸡') || taskLower.includes('蔬菜')) {
          itemName = task.match(/(大米|鸡肉|蔬菜)/)?.[1] || '淡水';
        }
        
        const result = await this.useTool('checkInventory', { itemName });
        return {
          response: `📦 ${itemName} 库存情况：${result.quantity} ${result.unit}，状态：${result.status}`,
          tool: 'checkInventory',
          result
        };
      }
      
      // 菜单生成
      if (taskLower.includes('菜单') || taskLower.includes('吃饭') || taskLower.includes('伙食')) {
        const result = await this.useTool('generateMenu', {
          date: new Date().toISOString().split('T')[0],
          crewNationalities: ['CN', 'PH']
        });
        return {
          response: `🍽️ 今日菜单：${result.breakfast} / ${result.lunch} / ${result.dinner}`,
          tool: 'generateMenu',
          result
        };
      }
      
      // 环境查询
      if (taskLower.includes('环境') || taskLower.includes('温度') || taskLower.includes('舱室')) {
        const cabinId = taskLower.match(/([ABC])区?/)?.[1] || 'A';
        const result = await this.useTool('monitorCabinEnvironment', { cabinId: `cabin-${cabinId}` });
        return {
          response: `🏠 舱室${cabinId}区：温度${result.temperature.toFixed(1)}°C，湿度${result.humidity.toFixed(1)}%`,
          tool: 'monitorCabinEnvironment',
          result
        };
      }
      
      // 默认：调用 LLM 思考
      const thought = await this.think(task, context);
      return {
        response: thought.content,
        thinking: true
      };
      
    } catch (error) {
      console.error('StewardAgent execute error:', error);
      return {
        response: `处理任务时出错：${error.message}`,
        error: true
      };
    }
  }
  
  /**
   * 注册工具
   * @private
   */
  _registerTools() {
    // 工具 1: 生成菜单
    this.registerTool('generateMenu', async (params) => {
      const { date, crewNationalities, inventoryData } = params;
      
      // 根据船员国籍和库存生成菜单
      const cuisines = {
        'CN': ['宫保鸡丁', '红烧肉', '炒青菜'],
        'PH': ['Adobo', 'Sinigang', 'Pancit'],
        'IN': ['Curry', 'Dal', 'Roti'],
        'EU': ['Steak', 'Pasta', 'Salad']
      };
      
      const menu = [];
      
      // 早餐
      menu.push({
        meal: '早餐',
        time: '07:00',
        dishes: ['鸡蛋', '面包', '牛奶', '水果'],
        calories: 650
      });
      
      // 午餐（根据船员国籍）
      const lunchDishes = [];
      crewNationalities.forEach(nat => {
        if (cuisines[nat]) {
          lunchDishes.push(...cuisines[nat].slice(0, 1));
        }
      });
      
      menu.push({
        meal: '午餐',
        time: '12:00',
        dishes: lunchDishes.length > 0 ? lunchDishes : ['米饭', '炒菜', '汤'],
        calories: 900
      });
      
      // 晚餐
      menu.push({
        meal: '晚餐',
        time: '18:00',
        dishes: ['海鲜', '蔬菜', '米饭'],
        calories: 800
      });
      
      return {
        date,
        menu,
        totalCalories: menu.reduce((sum, m) => sum + m.calories, 0),
        balanced: true
      };
    }, 'Generate daily menu based on crew preferences and inventory');
    
    // 工具 2: 检查库存
    this.registerTool('checkInventory', async (params) => {
      const { itemName } = params;
      
      // 模拟库存查询（实际应该查询 RFID 数据库）
      const mockInventory = {
        '大米': { quantity: 500, unit: 'kg', expiryDate: '2026-06-30', location: 'Warehouse-A-03' },
        '鸡肉': { quantity: 150, unit: 'kg', expiryDate: '2026-02-15', location: 'Freezer-01' },
        '蔬菜': { quantity: 80, unit: 'kg', expiryDate: '2026-02-05', location: 'Refrigerator-02' },
        '淡水': { quantity: 45000, unit: 'L', expiryDate: null, location: 'FreshWaterTank' }
      };
      
      const item = mockInventory[itemName] || { quantity: 0, unit: 'unknown', expiryDate: null, location: 'unknown' };
      
      // 计算剩余天数
      let daysRemaining = null;
      if (item.expiryDate) {
        const expiry = new Date(item.expiryDate);
        const now = new Date();
        daysRemaining = Math.ceil((expiry - now) / 86400000);
      }
      
      return {
        itemName,
        ...item,
        daysRemaining,
        status: daysRemaining && daysRemaining < 7 ? 'expiring_soon' : 
                item.quantity < 50 ? 'low_stock' : 'sufficient'
      };
    }, 'Check inventory for specific item');
    
    // 工具 3: 监控舱室环境
    this.registerTool('monitorCabinEnvironment', async (params) => {
      const { cabinId } = params;
      
      // 模拟环境传感器数据
      const environment = {
        temperature: 24 + Math.random() * 2, // 24-26°C
        humidity: 50 + Math.random() * 10, // 50-60%
        co2: 600 + Math.random() * 400, // 600-1000 ppm
        lighting: Math.random() > 0.5 ? 'on' : 'off'
      };
      
      // 评估舒适度
      let comfort = 'comfortable';
      const issues = [];
      
      if (environment.temperature < 20 || environment.temperature > 28) {
        comfort = 'uncomfortable';
        issues.push('温度不适');
      }
      
      if (environment.humidity > 70) {
        comfort = 'uncomfortable';
        issues.push('湿度过高');
      }
      
      if (environment.co2 > 1000) {
        comfort = 'unhealthy';
        issues.push('CO2 超标，需要通风');
      }
      
      return {
        cabinId,
        environment,
        comfort,
        issues,
        recommendation: issues.length > 0 ? 
          `建议：${issues.join('；')}。已自动调节空调。` :
          '舱室环境良好。'
      };
    }, 'Monitor cabin environment (temp, humidity, CO2)');
    
    // 工具 4: 检测船员疲劳
    this.registerTool('detectCrewFatigue', async (params) => {
      const { crewId, recentActivity } = params;
      
      // 简化的疲劳检测（实际应该基于作息、工作时长、生理数据）
      const fatigueScore = Math.random() * 100;
      
      let status = 'normal';
      let recommendation = '';
      
      if (fatigueScore > 70) {
        status = 'fatigued';
        recommendation = '建议休息。已调整舱室照明为暖光模式，有助于睡眠。';
      } else if (fatigueScore > 50) {
        status = 'mild_fatigue';
        recommendation = '注意休息，避免长时间值班。';
      } else {
        status = 'normal';
        recommendation = '状态良好。';
      }
      
      return {
        crewId,
        fatigueScore: fatigueScore.toFixed(0),
        status,
        recommendation
      };
    }, 'Detect crew fatigue level');
  }
  
  /**
   * 加载库存知识库
   * @private
   */
  _loadInventoryKnowledge() {
    // 物资消耗速率（每天）
    const consumptionRates = {
      '大米': 15, // kg/day
      '淡水': 3000, // L/day (20人 * 150L/人/天)
      '柴油': 5000, // L/day
      '蔬菜': 20 // kg/day
    };
    
    Object.entries(consumptionRates).forEach(([item, rate]) => {
      this.learn(`Consumption.${item}`, rate);
    });
    
    console.log('📦 Inventory knowledge loaded');
  }
  
  /**
   * 处理设备查询
   * @private
   */
  async _handleEquipmentQuery(task, context) {
    const thought = await this.think(task, context);
    
    return {
      type: 'general',
      response: thought.content
    };
  }
  
  /**
   * 更新物资库存
   * @param {string} itemName - 物资名称
   * @param {number} quantity - 数量
   */
  updateInventory(itemName, quantity) {
    this.stewardState.inventory.set(itemName, {
      quantity,
      lastUpdate: Date.now()
    });
    
    // 检查是否低于安全库存
    const consumptionRate = this.recall(`Consumption.${itemName}`) || 0;
    const daysRemaining = consumptionRate > 0 ? quantity / consumptionRate : Infinity;
    
    if (daysRemaining < 7) {
      this.emit('inventory:low', {
        itemName,
        quantity,
        daysRemaining: daysRemaining.toFixed(1)
      });
      
      console.warn(`📦 Low inventory: ${itemName} (${daysRemaining.toFixed(1)} days remaining)`);
    }
  }
}
