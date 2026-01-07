/**
 * 国际化文本配置
 * Internationalization Text Configuration
 * 
 * 当前使用双语模式（中英文）
 * Currently using bilingual mode (Chinese-English)
 */

export const i18n = {
  // GUI 标题
  gui: {
    title: '🚢 数字孪生控制面板 | Digital Twin Control Panel'
  },

  // 波浪参数
  wave: {
    folder: '🌊 波浪参数 | Wave Parameters',
    amplitude: '波高 | Amplitude',
    wavelength: '波长 | Wavelength',
    speed: '波速 | Speed',
    steepness: '陡度 | Steepness'
  },

  // 天气系统
  weather: {
    folder: '⛈️ 天气系统 | Weather System',
    preset: '天气预设 | Weather Preset',
    presets: {
      calm: '平静 | Calm',
      moderate: '中等 | Moderate', 
      storm: '风暴 | Storm',
      typhoon: '台风 | Typhoon',
      snow: '降雪 | Snow'
    },
    windSpeed: '风速 | Wind Speed (m/s)',
    windDirection: '风向 | Wind Direction (°)',
    rainIntensity: '降雨强度 | Rain Intensity (mm/h)',
    seaState: '海况等级 | Sea State Level'
  },

  // 物理系统
  physics: {
    folder: '⚛️ 物理 | Physics',
    algorithms: {
      folder: '⚙️ 算法管理 | Algorithms',
      buoyancy: '浮力 | Buoyancy',
      stabilizer: '自稳 | Stabilizer',
      wind: '风力 | Wind',
      rain: '降雨 | Rain'
    }
  },

  // 算法管理（保持向后兼容）
  algorithms: {
    folder: '⚙️ 算法管理 | Algorithms',
    buoyancy: '浮力 | Buoyancy',
    stabilizer: '自稳 | Stabilizer',
    wind: '风力 | Wind',
    rain: '降雨 | Rain'
  },

  // 海况系统
  seaCondition: {
    folder: '🌊 海况 | Sea Condition'
  },

  // 航行系统
  navigation: {
    folder: '🚢 航行 | Navigation'
  },

  // 场景选择
  scenario: {
    folder: '🎬 选择场景 | Select Scenario'
  },

  // 船体与设备
  shipEquipment: {
    folder: '▣ 船体与设备 | Ship & Equipment',
    equipment: {
      folder: '◉ 设备运行数据 | Equipment Operation',
      mainEngine: '主机状态 | Main Engine',
      rudderPropulsion: '舵机/推进系统 | Rudder/Propulsion',
      generator: '发电机运行状态 | Generator Status',
      crane: '吊机运行状态 | Crane Status'
    },
    energy: {
      folder: '◈ 能源与动力数据 | Energy & Power',
      fuelLevel: '燃油储量 | Fuel Level',
      consumption: '油耗曲线 | Consumption Curve',
      range: '剩余航程预测 | Remaining Range',
      powerLoad: '电力系统负载分布 | Power Load Distribution'
    },
    structure: {
      folder: '◊ 结构健康数据 | Structure Health',
      stressSensors: '船体关键部位应力传感器 | Stress Sensors'
    },
    pumpValve: {
      folder: '◐ 泵阀系统数据 | Pump & Valve System',
      status: '开关状态 | Switch Status',
      opening: '开度及流量数据 | Opening & Flow Rate'
    }
  },

  // 浮力与稳定性
  buoyancy: {
    folder: '⚓ 浮力与稳定性 | Buoyancy & Stability',
    buoyancyCoeff: '浮力系数 | Buoyancy Coeff',
    dragCoeff: '阻尼系数 | Drag Coeff',
    density: '水密度 | Water Density',
    boatMass: '船体质量 | Boat Mass (kg)',
    draftDepth: '吃水深度 | Draft Depth (m)',
    enableStabilizer: '启用自稳 | Enable Stabilizer',
    uprightStiffness: '自稳刚度 | Stabilizer Stiffness',
    uprightDamping: '自稳阻尼 | Stabilizer Damping',
    wobbleBoost: '摇晃增强 | Wobble Boost (>1=more)',
    reset: '🔄 重置船体 | Reset Boat'
  },

  // 显示选项
  display: {
    folder: '👁️ 显示选项 | Display Options',
    showWeatherIndicators: '天气指示器 | Weather Indicators',
    wireframeWater: '水面线框 | Water Wireframe',
    showAxesHelper: '显示坐标轴 | Show Axes',
    showDimensionLines: '显示尺寸线 | Show Dimension Lines',
    focusBoat: '📍 聚焦船体 | Focus Boat'
  },

  // 巡检功能
  inspection: {
    folder: '🔍 巡检功能 | Inspection',
    startInspection: '开始巡检 | Start Inspection',
    endInspection: '结束巡检 | End Inspection'
  },

  // 状态信息
  status: {
    shipStatus: '船体状态 | Ship Status',
    position: '位置 | Position',
    mass: '质量 | Mass',
    waterHeight: '水面高度 | Water Height',
    offsetToSurface: '离水面 | Offset to Surface',
    weatherStatus: '天气状态 | Weather Status',
    windSpeed: '风速 | Wind Speed',
    windDirection: '风向 | Wind Direction',
    rain: '降雨 | Rain',
    visibility: '能见度 | Visibility',
    seaState: '海况 | Sea State'
  },

  // 页面信息
  page: {
    title: '🚢 船舶数字孪生系统 | Ship Digital Twin System',
    subtitle: '重构版 | Refactored Version',
    features: {
      title: '新特性 | New Features',
      pluggable: '可插拔模拟器 | Pluggable Simulator',
      weather: '天气系统 | Weather System',
      modular: '模块化架构 | Modular Architecture'
    },
    newFeatures: {
      title: '核心功能 | Core Features',
      simulator: '模拟器引擎 | SimulatorEngine - 可动态添加/移除算法 | Dynamic algorithms',
      weather: '天气系统 | WeatherSystem - 风、雨、海况模拟 | Wind, rain, sea state simulation',
      algorithms: '算法独立计算，结果自动合并 | Independent algorithm calculation, auto-merge results',
      events: '事件驱动架构，易于扩展 | Event-driven architecture, easy to extend'
    },
    controls: {
      title: '操作说明 | Controls',
      rotate: '拖动旋转 | Drag to rotate',
      zoom: '滚轮缩放 | Scroll to zoom',
      pan: 'Shift+拖动平移 | Shift+Drag to pan',
      menu: '右上角菜单可调节天气、波浪、算法参数 | Use top-right menu to adjust weather, waves, algorithms'
    },
    version: '版本 | Version',
    architecture: '模块化架构 | Modular Architecture',
    loading: '🚢 加载中... | Loading...',
    loadingText: '正在初始化数字孪生系统 | Initializing Digital Twin System'
  }
};

/**
 * 获取双语文本
 * @param {string} path - 文本路径，如 'wave.amplitude'
 * @returns {string}
 */
export function getText(path) {
  const keys = path.split('.');
  let value = i18n;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      console.warn(`i18n: Path not found: ${path}`);
      return path;
    }
  }
  
  return value;
}

/**
 * 格式化双语文本（用于动态拼接）
 * @param {string} zhText - 中文文本
 * @param {string} enText - 英文文本
 * @returns {string}
 */
export function formatBilingual(zhText, enText) {
  return `${zhText} | ${enText}`;
}

