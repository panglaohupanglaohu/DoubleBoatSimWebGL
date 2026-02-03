/**
 * Poseidon-X 完整集成 Demo
 * 
 * 将 Poseidon-X AI 系统与现有的 3D 数字孪生系统深度集成
 * 
 * 使用方法：
 * 在 HTML 中导入此文件，替代原有的 demo-refactored.js
 */

// 导入现有系统组件（来自 demo-refactored.js）
import * as THREE from '../public/lib/three.module.js';
import { OrbitControls } from '../public/lib/OrbitControls.js';
import * as CANNON from '../public/lib/cannon-es.js';
import GUI from '../public/lib/lil-gui.esm.min.js';

import { waveParams, getWaveHeight, waterUniforms, waterVertexShader, waterFragmentShader } from './waves.js';
import { ShipController } from './ship/ShipController.js';
import { SimulatorEngine } from './physics/SimulatorEngine.js';
import { BuoyancyAlgorithm } from './physics/algorithms/BuoyancyAlgorithm.js';
import { StabilizerAlgorithm } from './physics/algorithms/StabilizerAlgorithm.js';
import { WindAlgorithm } from './physics/algorithms/WindAlgorithm.js';
import { RainAlgorithm } from './physics/algorithms/RainAlgorithm.js';
import { WeatherSystem } from './weather/WeatherSystem.js';
import { ShipStabilityAnalyzer } from './ship/ShipStabilityAnalyzer.js';
import { CabinManager } from './ship/cabins/CabinManager.js';
import { VirtualDataSource } from './data/VirtualDataSource.js';
import { ShipDashboardDisplay } from './monitoring/ShipDashboardDisplay.js';
import { patchThreeJS } from './tests/ThreeJSPatch.js';

// 导入 Poseidon-X 系统
import { createIntegratedPoseidonX } from './poseidon/PoseidonXIntegration.js';

// 全局变量
let renderer, scene, camera, controls;
let world, shipController, simulatorEngine, weatherSystem;
let virtualDataSource, stabilityAnalyzer, cabinManager;
let shipDashboardDisplay;
let waterMeshFar, gui, clock;
let poseidonIntegration = null;
let hemiLight, dirLight;

// 配置
const config = {
  boatSize: { x: 85, y: 95, z: 138 },
  boatMass: 37000000,
  draftDepth: 0,
  yFlip: -1,
  buoyancy: {
    buoyancyCoeff: 40000000,
    dragCoeff: 6,
    density: 1.0,
    maxBuoyancy: 3.0,
    effectivePointCount: 0.2
  },
  stabilizer: {
    enableStabilizer: true,
    uprightStiffness: 12.0,
    uprightDamping: 6.0,
    wobbleBoost: 0.8
  },
  display: {
    showAxesHelper: false,
    showDimensionLines: false,
    wireframeWater: false
  }
};

// 聚焦船体：重置姿态、显示坐标轴/尺寸线、相机对准船体
function focusBoat() {
  if (!shipController || !shipController.mesh) return;
  if (shipController.toggleAxesHelper) {
    shipController.toggleAxesHelper(true);
    config.display.showAxesHelper = true;
  }
  if (shipController.toggleDimensionLines) {
    shipController.toggleDimensionLines(true);
    config.display.showDimensionLines = true;
  }
  shipController.reset();
  shipController.placeOnWater(clock.elapsedTime);
  const pos = shipController.mesh.position.clone();
  camera.position.set(pos.x + 50, pos.y + 30, pos.z + 50);
  controls.target.copy(pos);
  controls.update();
}

// 船身稳定：调用稳定性分析器并应用调整
function stabilizeShip() {
  if (!shipController || !shipController.body || !stabilityAnalyzer || !simulatorEngine) return;
  const result = stabilityAnalyzer.stabilize(
    shipController.body,
    clock.elapsedTime,
    config,
    simulatorEngine,
    shipController
  );
  if (shipController.body) {
    shipController.body.wakeUp();
    if (shipController.mesh) {
      shipController.mesh.position.copy(shipController.body.position);
      shipController.mesh.quaternion.copy(shipController.body.quaternion);
    }
  }
  console.log('⚖️ 船身稳定执行完成 | Stabilize done:', result?.stable);
}

// 初始化
async function init() {
  // 确保 DOM 已加载
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
    return;
  }
  
  // 确保 app 元素存在
  const appElement = document.getElementById('app');
  if (!appElement) {
    console.warn('⚠️ 找不到 app 元素，等待 DOM 加载...');
    setTimeout(init, 100);
    return;
  }
  
  console.log('🚀 ========== 初始化集成系统 ==========');
  
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1525);
  scene.fog = new THREE.Fog(0x0b1525, 60, 220);
  
  // 创建相机
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(150, 80, 150);
  
  // 应用 Three.js patch
  patchThreeJS();
  
  // 创建渲染器（使用与 demo-refactored.js 相同的配置）
  try {
    renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      powerPreference: 'high-performance',
      failIfMajorPerformanceCaveat: false
    });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;
    
    // 设置颜色空间
    if (renderer.outputColorSpace !== undefined) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    
    appElement.appendChild(renderer.domElement);
    
    console.log('✅ WebGL 渲染器创建成功');
  } catch (error) {
    console.error('❌ 渲染器创建失败:', error);
    
    // 显示用户友好的错误提示
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(244, 67, 54, 0.95);
      color: white;
      padding: 30px;
      border-radius: 12px;
      max-width: 600px;
      z-index: 10000;
      text-align: center;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    `;
    
    errorDiv.innerHTML = `
      <h2 style="margin-bottom: 20px;">⚠️ WebGL 初始化失败</h2>
      <p style="margin-bottom: 20px; line-height: 1.6;">
        无法创建 WebGL 上下文。可能的原因：<br>
        1. 同时打开了多个 WebGL 页面（index-refactored.html）<br>
        2. 浏览器的 WebGL 已达到上限
      </p>
      <div style="margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 6px;">
        <strong>解决方法：</strong><br>
        1. 关闭其他标签页（特别是 index-refactored.html）<br>
        2. 刷新本页面（F5）<br>
        3. 或重启浏览器
      </div>
      <button onclick="window.location.reload()" style="
        padding: 12px 24px;
        background: white;
        color: #f44336;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        cursor: pointer;
        font-size: 14px;
      ">🔄 刷新页面重试</button>
    `;
    
    document.body.appendChild(errorDiv);
    return;
  }
  
  // 创建控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.target.set(0, 30, 0);
  
  // 创建时钟
  clock = new THREE.Clock();
  
  // 创建物理世界
  world = new CANNON.World({
    gravity: new CANNON.Vec3(0, -9.82, 0)
  });
  world.broadphase = new CANNON.SAPBroadphase(world);
  world.allowSleep = true;
  world.solver.iterations = 14;
  
  // 设置灯光
  setupLights();
  
  // 创建水面
  createWater();
  
  // 创建模拟器引擎
  simulatorEngine = new SimulatorEngine(world);
  window.simulatorEngine = simulatorEngine;
  
  // 注册算法
  const buoyancyAlg = new BuoyancyAlgorithm(config.buoyancy);
  simulatorEngine.registerAlgorithm(buoyancyAlg);
  buoyancyAlg.initialize(world, scene);
  
  const stabilizerAlg = new StabilizerAlgorithm(config.stabilizer);
  simulatorEngine.registerAlgorithm(stabilizerAlg);
  
  const windAlg = new WindAlgorithm({ windSpeed: 0, windDirection: 0 });
  simulatorEngine.registerAlgorithm(windAlg);
  
  const rainAlg = new RainAlgorithm({ rainIntensity: 0 });
  simulatorEngine.registerAlgorithm(rainAlg);
  
  // 创建天气系统
  weatherSystem = new WeatherSystem(scene, simulatorEngine);
  weatherSystem.initialize();
  
  // 创建稳定性分析器
  stabilityAnalyzer = new ShipStabilityAnalyzer();
  
  // 创建虚拟数据源
  virtualDataSource = new VirtualDataSource();
  
  // 创建船体控制器
  shipController = new ShipController(scene, world, {
    mass: config.boatMass,
    size: config.boatSize,
    draftDepth: config.draftDepth,
    yFlip: config.yFlip,
    desiredSize: config.boatSize,
    platformHeight: 45,
    catamaran: { enabled: true },
    glbPath: '/public/boat 1.glb'
  });
  
  window.shipController = shipController;
  
  console.log('📦 船体控制器已创建');
  
  // 加载船体
  await shipController.load();
  
  if (shipController.loaded && shipController.mesh) {
    console.log('✅ 船体模型加载成功');
    
    // 重新生成浮力点
    const buoyancyAlg = simulatorEngine.getAlgorithm('Buoyancy');
    if (buoyancyAlg) {
      buoyancyAlg.generateBuoyancyPoints(shipController.size);
    }
    
    shipController.placeOnWater(clock.elapsedTime);
  }
  
  // 延迟创建舱室管理器
  setTimeout(() => {
    if (shipController && shipController.loaded) {
      cabinManager = new CabinManager(scene, camera, shipController);
      cabinManager.initialize();
      console.log('✅ 舱室管理器初始化完成');
    }
  }, 2000);
  
  // 延迟创建仪表盘
  setTimeout(() => {
    shipDashboardDisplay = new ShipDashboardDisplay(scene, virtualDataSource);
    shipDashboardDisplay.initialize();
  }, 1500);
  
  // ========== 🌊 初始化 Poseidon-X 集成 ==========
  console.log('\n🌊 ========== 初始化 Poseidon-X AI 系统 ==========\n');
  
  poseidonIntegration = await createIntegratedPoseidonX({
    scene,
    camera,
    shipController,
    simulatorEngine,
    weatherSystem,
    virtualDataSource,
    world,
    cabinManager,
    clock,
    config,
    stabilityAnalyzer
  });
  
  // 暴露到全局
  window.poseidonSystem = poseidonIntegration.poseidonSystem;
  window.poseidonIntegration = poseidonIntegration;
  
  console.log('\n✅ ========== Poseidon-X 集成完成 ==========\n');
  console.log('💡 你现在可以：');
  console.log('   1. 使用 Bridge Chat 对话框（右下角）');
  console.log('   2. 在控制台执行: poseidonSystem.executeTask("你的问题")');
  console.log('   3. 或使用: poseidonIntegration.executeNaturalLanguageCommand("设置12级台风")');
  
  // 更新顶部状态
  const systemStatusEl = document.getElementById('system-status');
  const agentCountEl = document.getElementById('agent-count');
  
  if (systemStatusEl) {
    systemStatusEl.textContent = '系统在线';
  }
  
  if (agentCountEl) {
    const agents = poseidonIntegration.poseidonSystem.agents;
    agentCountEl.textContent = `🤖 ${Object.keys(agents).length} Agents Active`;
  }
  
  // 设置 GUI
  setupGUI();
  
  // 窗口大小调整
  window.addEventListener('resize', onResize);
  
  // 隐藏加载界面
  setTimeout(() => {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
      loadingEl.classList.add('hide');
    }
  }, 1000);
  
  // 启动动画循环
  animate();
}

// 设置灯光（保存 hemiLight/dirLight 供 GUI 灯光系统使用）
function setupLights() {
  hemiLight = new THREE.HemisphereLight(0xaadfff, 0x0b1120, 6.0);
  scene.add(hemiLight);

  dirLight = new THREE.DirectionalLight(0xffffff, 6.0);
  dirLight.position.set(500, 400, 300);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(4096, 4096);
  dirLight.shadow.camera.near = 1;
  dirLight.shadow.camera.far = 1000;
  dirLight.shadow.camera.left = -600;
  dirLight.shadow.camera.right = 600;
  dirLight.shadow.camera.top = 600;
  dirLight.shadow.camera.bottom = -600;
  scene.add(dirLight);

  const ambientLight = new THREE.AmbientLight(0xffffff, 2.0);
  scene.add(ambientLight);
}

// 创建水面
function createWater() {
  const geom = new THREE.PlaneGeometry(500, 500, 200, 200);
  geom.rotateX(-Math.PI / 2);
  
  const material = new THREE.ShaderMaterial({
    uniforms: waterUniforms,
    vertexShader: waterVertexShader,
    fragmentShader: waterFragmentShader,
    transparent: true,
    side: THREE.DoubleSide
  });
  
  waterMeshFar = new THREE.Mesh(geom, material);
  waterMeshFar.receiveShadow = true;
  scene.add(waterMeshFar);
}

// 设置 GUI
function setupGUI() {
  gui = new GUI({ width: 380, title: '🚢 数字孪生控制面板 | Digital Twin Control Panel' });
  gui.domElement.style.zIndex = '20';
  
  // 菜单动作统一入口（与 Bridge 输入对应，先走 LLM 识别后再调用）
  const menuActions = {
    check_collision: () => {
      if (poseidonSystem) {
        poseidonSystem.executeTask("右舷那艘集装箱船有碰撞风险吗？")
          .then(r => console.log('✅ Navigator:', r));
      }
    },
    check_engine: () => {
      if (poseidonSystem) {
        poseidonSystem.executeTask("主机排温正常吗？").then(r => console.log('✅ Engineer:', r));
      }
    },
    set_typhoon: () => {
      if (poseidonIntegration) {
        poseidonIntegration.executeNaturalLanguageCommand("设置17级台风").then(r => console.log('✅:', r));
      }
    },
    stabilize_ship: () => {
      if (poseidonIntegration) {
        poseidonIntegration.executeNaturalLanguageCommand("稳定船体").then(r => console.log('✅:', r));
      }
    },
    reset_ship: () => {
      if (shipController) {
        shipController.reset();
        shipController.placeOnWater(clock.elapsedTime);
      }
    }
  };
  
  // Poseidon-X AI 控制
  const aiFolder = gui.addFolder('🤖 Poseidon-X AI System');
  aiFolder.add({
    askQuestion: () => {
      const question = prompt('请输入问题 | Enter your question:');
      if (question && poseidonIntegration) {
        poseidonIntegration.executeNaturalLanguageCommand(question)
          .then(result => { console.log('✅ AI Response:', result); alert(`Poseidon-X: ${JSON.stringify(result, null, 2)}`); });
      }
    }
  }, 'askQuestion').name('💬 Ask Poseidon');
  aiFolder.add(menuActions, 'check_collision').name('🚢 Check Collision Risk');
  aiFolder.add(menuActions, 'check_engine').name('⚙️ Check Engine');
  aiFolder.add(menuActions, 'set_typhoon').name('🌀 Set Typhoon (17)');
  
  // 船舶控制
  const shipFolder = gui.addFolder('🚢 Ship Control');
  shipFolder.add(menuActions, 'stabilize_ship').name('⚖️ Stabilize Ship');
  shipFolder.add(menuActions, 'reset_ship').name('🔄 Reset Ship');
  
  // 海况 | Sea Condition → 波浪参数（与 index-refactored 一致）
  const seaConditionFolder = gui.addFolder('🌊 海况 | Sea Condition');
  const waveFolder = seaConditionFolder.addFolder('🌊 波浪参数 | Wave Parameters');
  waveFolder.add(waveParams, 'amplitude', 0.1, 3.0, 0.05).name('波高 | Amplitude');
  waveFolder.add(waveParams, 'wavelength', 4, 40, 0.5).name('波长 | Wavelength');
  waveFolder.add(waveParams, 'speed', 0.2, 4.0, 0.05).name('波速 | Speed');
  waveFolder.add(waveParams, 'steepness', 0.2, 1.2, 0.02).name('陡度 | Steepness');
  waveFolder.add(config.display, 'wireframeWater').name('水面线框 | Wireframe Water').onChange(v => {
    if (waterMeshFar && waterMeshFar.material) waterMeshFar.material.wireframe = v;
  });
  
  // 菜单 → Bridge 联动：把当前天气/环境推送到 Bridge 的 shipContext，供 LLM 与输入一致
  function pushEnvironmentToBridge() {
    if (!window.poseidonIntegration?.poseidonSystem || !weatherSystem) return;
    const w = weatherSystem.getWeatherState();
    window.poseidonIntegration.poseidonSystem.updateShipContext({
      environment: {
        windSpeed: w.windSpeed ?? 0,
        windDirection: w.windDirection ?? 0,
        rainIntensity: w.rainIntensity ?? 0,
        snowIntensity: weatherSystem.weather.snowIntensity ?? 0,
        temperature: weatherSystem.weather.temperature ?? 15,
        visibility: w.visibility ?? 1,
        seaState: w.seaState ?? 'calm'
      }
    });
  }

  // 天气控制（与 Bridge 联动：设置后需 updateDisplay 使菜单滑块同步；菜单变更时立即推送到 Bridge）
  const weatherFolder = gui.addFolder('⛈️ 天气系统 | Weather System');
  let weatherControllers = {};
  if (weatherSystem) {
    weatherFolder.add(weatherSystem, 'preset', ['calm', 'moderate', 'storm', 'typhoon', 'snow']).name('天气预设 | Weather Preset')
      .onChange(v => {
        weatherSystem.setPreset(v);
        weatherControllers.windSpeed?.updateDisplay?.();
        weatherControllers.windDirection?.updateDisplay?.();
        weatherControllers.rainIntensity?.updateDisplay?.();
        pushEnvironmentToBridge();
      });
    weatherControllers.windSpeed = weatherFolder.add(weatherSystem.weather, 'windSpeed', 0, 100, 1)
      .name('风速 | Wind Speed (m/s)')
      .onChange(v => {
        weatherSystem.setWind(v, weatherSystem.weather.windDirection);
        pushEnvironmentToBridge();
      });
    weatherControllers.windDirection = weatherFolder.add(weatherSystem.weather, 'windDirection', 0, 360, 1)
      .name('风向 | Wind Direction (°)')
      .onChange(v => {
        weatherSystem.setWind(weatherSystem.weather.windSpeed, v);
        pushEnvironmentToBridge();
      });
    weatherControllers.rainIntensity = weatherFolder.add(weatherSystem.weather, 'rainIntensity', 0, 200, 1)
      .name('降雨强度 | Rain Intensity (mm/h)')
      .onChange(v => {
        weatherSystem.setRain(v);
        pushEnvironmentToBridge();
      });
    weatherFolder.add(weatherSystem.weather, 'snowIntensity', 0, 100, 1).name('降雪强度 | Snow Intensity (mm/h)')
      .onChange(v => { weatherSystem.setSnow(v); pushEnvironmentToBridge(); });
    weatherFolder.add(weatherSystem.weather, 'temperature', -20, 30, 1).name('温度 | Temperature (°C)')
      .onChange(v => { weatherSystem.setTemperature(v); pushEnvironmentToBridge(); });
    weatherFolder.add({ typhoonLevel: 0 }, 'typhoonLevel', 0, 17, 1).name('台风等级 | Typhoon Level (0=关闭)')
      .onChange(v => { if (v > 0) weatherSystem.setTyphoonLevel(v); else weatherSystem.setPreset('calm'); pushEnvironmentToBridge(); });
  }
  // 控制器挂到 window，确保 Bridge 输入触发 poseidonSet* 时能刷新菜单（不依赖闭包）
  window.__poseidonGUI = window.__poseidonGUI || {};
  window.__poseidonGUI.weatherControllers = weatherControllers;

  // Bridge 设置风向/风速/降雨时同步到天气系统并刷新菜单显示
  window.poseidonSetWindDirection = function (degrees) {
    if (!weatherSystem) return false;
    const deg = Math.round(Number(degrees));
    if (isNaN(deg)) return false;
    weatherSystem.weather.windDirection = Math.max(0, Math.min(360, deg));
    weatherSystem.setWind(weatherSystem.weather.windSpeed, weatherSystem.weather.windDirection);
    const ctrls = window.__poseidonGUI?.weatherControllers;
    if (ctrls?.windDirection && typeof ctrls.windDirection.updateDisplay === 'function') ctrls.windDirection.updateDisplay();
    pushEnvironmentToBridge();
    return true;
  };
  window.poseidonSetWindSpeed = function (speed) {
    if (!weatherSystem) return false;
    const v = Number(speed);
    if (isNaN(v)) return false;
    weatherSystem.weather.windSpeed = Math.max(0, Math.min(100, v));
    weatherSystem.setWind(weatherSystem.weather.windSpeed, weatherSystem.weather.windDirection);
    const ctrls = window.__poseidonGUI?.weatherControllers;
    if (ctrls?.windSpeed && typeof ctrls.windSpeed.updateDisplay === 'function') ctrls.windSpeed.updateDisplay();
    pushEnvironmentToBridge();
    return true;
  };
  window.poseidonSetRainIntensity = function (value) {
    if (!weatherSystem) return false;
    const v = Math.max(0, Math.min(200, Number(value)));
    if (isNaN(v)) return false;
    weatherSystem.weather.rainIntensity = v;
    weatherSystem.setRain(v);
    const ctrls = window.__poseidonGUI?.weatherControllers;
    if (ctrls?.rainIntensity && typeof ctrls.rainIntensity.updateDisplay === 'function') ctrls.rainIntensity.updateDisplay();
    pushEnvironmentToBridge();
    return true;
  };
  
  // 物理 | Physics → 算法管理（与 index-refactored 一致）
  const physicsFolder = gui.addFolder('⚛️ 物理 | Physics');
  const algoFolder = physicsFolder.addFolder('⚙️ 算法管理 | Algorithms');
  const buoyancyAlg = simulatorEngine.getAlgorithm('Buoyancy');
  const stabilizerAlg = simulatorEngine.getAlgorithm('Stabilizer');
  const windAlg = simulatorEngine.getAlgorithm('Wind');
  const rainAlg = simulatorEngine.getAlgorithm('Rain');
  if (buoyancyAlg) algoFolder.add(buoyancyAlg, 'enabled').name('浮力 | Buoyancy');
  if (stabilizerAlg) algoFolder.add(stabilizerAlg, 'enableStabilizer').name('自稳 | Stabilizer');
  if (windAlg) algoFolder.add(windAlg, 'enabled').name('风力 | Wind');
  if (rainAlg) algoFolder.add(rainAlg, 'enabled').name('降雨 | Rain');
  
  // 航行 | Navigation → 浮力与稳定性（与 index-refactored 一致）
  const navigationFolder = gui.addFolder('🚢 航行 | Navigation');
  const buoyancyFolder = navigationFolder.addFolder('⚓ 浮力与稳定性 | Buoyancy & Stability');
  if (buoyancyAlg) {
    const buoyancyProxy = {
      get buoyancyCoeff() { return config.buoyancy.buoyancyCoeff; },
      set buoyancyCoeff(value) {
        const num = Number(value);
        if (isNaN(num)) return;
        config.buoyancy.buoyancyCoeff = num;
        buoyancyAlg.buoyancyCoeff = num;
        if (shipController?.body) { shipController.body.wakeUp(); shipController.body.velocity.y = 0; }
      }
    };
    buoyancyFolder.add(buoyancyProxy, 'buoyancyCoeff', 1000000, 150000000, 10000).name('浮力系数 | Buoyancy Coeff');
    buoyancyFolder.add(config.buoyancy, 'dragCoeff', 0, 20, 0.1).name('阻尼系数 | Drag Coeff')
      .onChange(v => { buoyancyAlg.dragCoeff = v; config.buoyancy.dragCoeff = v; });
  }
  if (stabilizerAlg) {
    buoyancyFolder.add(config.stabilizer, 'enableStabilizer').name('启用自稳 | Enable Stabilizer')
      .onChange(v => { stabilizerAlg.enableStabilizer = v; });
    buoyancyFolder.add(config.stabilizer, 'uprightStiffness', 0, 15, 0.1).name('自稳刚度 | Stabilizer Stiffness')
      .onChange(v => stabilizerAlg.setStiffness?.(v));
    buoyancyFolder.add(config.stabilizer, 'uprightDamping', 0, 10, 0.1).name('自稳阻尼 | Stabilizer Damping')
      .onChange(v => stabilizerAlg.setDamping?.(v));
    buoyancyFolder.add(config.stabilizer, 'wobbleBoost', 0.2, 5.0, 0.1).name('摇晃增强 | Wobble Boost')
      .onChange(v => stabilizerAlg.setWobbleBoost?.(v));
  }
  buoyancyFolder.add({ reset: () => { if (shipController) { shipController.reset(); shipController.placeOnWater(clock.elapsedTime); } } }, 'reset').name('🔄 重置船体 | Reset Boat');
  buoyancyFolder.add({ stabilize: stabilizeShip }, 'stabilize').name('⚖️ 船身稳定 | Stabilize Ship');
  
  // 视图控制（与 Bridge 语音/文字「切换视图」对应，供 window.poseidonSwitchView 调用）
  const viewFolder = gui.addFolder('📷 Camera Views');
  const defaultSize = config.boatSize || { x: 85, y: 95, z: 138 };
  const viewActions = {
    overall: () => {
      const size = (shipController && shipController.size) || defaultSize;
      const distance = Math.max(size.x, size.y, size.z) * 2;
      camera.position.set(distance, distance * 0.6, distance);
      controls.target.set(0, (size.y || 30) * 0.3, 0);
      controls.update();
    },
    top: () => {
      const size = (shipController && shipController.size) || defaultSize;
      const maxXZ = Math.max(size.x || 100, size.z || 100);
      camera.position.set(0, maxXZ * 1.5, 0);
      controls.target.set(0, (size.y || 30) * 0.3, 0);
      controls.update();
    }
  };
  viewFolder.add(viewActions, 'overall').name('🌐 Overall View');
  viewFolder.add(viewActions, 'top').name('⬇️ Top View');
  // 供 Bridge Chat 调用：模拟点击菜单「📷 Camera Views」中的对应项
  window.poseidonSwitchView = function (viewName) {
    const raw = (viewName || '').trim();
    const name = raw.toLowerCase().replace(/\s/g, '');
    if (viewActions[name]) {
      viewActions[name]();
      return true;
    }
    if (raw === '顶视图' || raw === '俯视图' || name === 'topview' || raw.toLowerCase() === 'top view') {
      viewActions.top();
      return true;
    }
    if (raw === '整体视图' || name === 'overallview' || raw.toLowerCase() === 'overall view') {
      viewActions.overall();
      return true;
    }
    return false;
  };
  
  // 统一菜单入口：与 GUI 各菜单项一一对应，先走 LLM 识别后再调用
  window.poseidonMenuAction = function (actionId) {
    const id = (actionId || '').trim().toLowerCase();
    if (id === 'view_top' || id === 'view_top_down') {
      viewActions.top();
      return true;
    }
    if (id === 'view_overall') {
      viewActions.overall();
      return true;
    }
    if (menuActions[id]) {
      menuActions[id]();
      return true;
    }
    return false;
  };

  // 船体颜色标记：Bridge 可通过自然语言设置区域颜色
  window.poseidonSetHullRegionColor = function (regionKey, colorNameOrHex) {
    if (!shipController || typeof shipController.setHullRegionColor !== 'function') return false;
    const hex = typeof colorNameOrHex === 'number' ? colorNameOrHex : ShipController.colorNameToHex(String(colorNameOrHex));
    if (hex === undefined) return false;
    shipController.setHullRegionColor(regionKey, hex);
    return true;
  };
  window.poseidonSetHullColor = function (colorNameOrHex) {
    if (!shipController || typeof shipController.setHullColor !== 'function') return false;
    const hex = typeof colorNameOrHex === 'number' ? colorNameOrHex : ShipController.colorNameToHex(String(colorNameOrHex));
    if (hex === undefined) return false;
    shipController.setHullColor(hex);
    return true;
  };
  
  // 显示选项 | Display Options（与 Bridge 联动，需保存控制器以便 updateDisplay）
  const displayFolder = gui.addFolder('👁️ 显示选项 | Display Options');
  displayFolder.add({ focus: focusBoat }, 'focus').name('📍 聚焦船体 | Focus Boat');
  const displayControllers = {};
  displayControllers.showAxes = displayFolder.add(config.display, 'showAxesHelper')
    .name('显示坐标轴 | Show Axes')
    .onChange(v => {
      if (shipController) shipController.toggleAxesHelper(v);
    });
  displayControllers.showDimensions = displayFolder.add(config.display, 'showDimensionLines')
    .name('显示尺寸线 | Show Dimensions')
    .onChange(v => {
      if (shipController) shipController.toggleDimensionLines(v);
    });
  window.__poseidonGUI.displayControllers = displayControllers;
  const shipOpacityObj = { opacity: 0.6 };
  displayFolder.add(shipOpacityObj, 'opacity', 0.1, 1.0, 0.01).name('船体透明度 | Ship Opacity')
    .onChange(v => {
      if (shipController && typeof shipController.updateShipMaterialOpacity === 'function') {
        shipController.updateShipMaterialOpacity(v);
      }
    });
  // Display 切换供 Bridge 调用并刷新菜单
  menuActions.show_axes = () => {
    config.display.showAxesHelper = !config.display.showAxesHelper;
    if (shipController) shipController.toggleAxesHelper(config.display.showAxesHelper);
    if (displayControllers.showAxes && typeof displayControllers.showAxes.updateDisplay === 'function') {
      displayControllers.showAxes.updateDisplay();
    }
  };
  menuActions.show_dimensions = () => {
    config.display.showDimensionLines = !config.display.showDimensionLines;
    if (shipController) shipController.toggleDimensionLines(config.display.showDimensionLines);
    if (displayControllers.showDimensions && typeof displayControllers.showDimensions.updateDisplay === 'function') {
      displayControllers.showDimensions.updateDisplay();
    }
  };
  
  // 灯光系统 | Lighting System（与 index-refactored 一致）
  const lightingFolder = gui.addFolder('灯光系统 | Lighting System');
  if (hemiLight) {
    const hemiFolder = lightingFolder.addFolder('半球光 | Hemisphere Light');
    hemiFolder.add(hemiLight, 'intensity', 0, 3, 0.1).name('强度 | Intensity');
    hemiFolder.addColor({ color: hemiLight.color.getHex() }, 'color').name('天空颜色 | Sky Color')
      .onChange(v => hemiLight.color.setHex(v));
    hemiFolder.addColor({ color: hemiLight.groundColor.getHex() }, 'color').name('地面颜色 | Ground Color')
      .onChange(v => hemiLight.groundColor.setHex(v));
    hemiFolder.add(hemiLight, 'visible').name('可见 | Visible');
  }
  if (dirLight) {
    const dirFolder = lightingFolder.addFolder('主方向光 | Main Directional Light');
    dirFolder.add(dirLight, 'intensity', 0, 5, 0.1).name('强度 | Intensity');
    dirFolder.addColor({ color: dirLight.color.getHex() }, 'color').name('颜色 | Color')
      .onChange(v => dirLight.color.setHex(v));
    dirFolder.add(dirLight.position, 'x', -500, 500, 1).name('位置 X | Position X');
    dirFolder.add(dirLight.position, 'y', -500, 500, 1).name('位置 Y | Position Y');
    dirFolder.add(dirLight.position, 'z', -500, 500, 1).name('位置 Z | Position Z');
    dirFolder.add(dirLight, 'castShadow').name('投射阴影 | Cast Shadow');
    dirFolder.add(dirLight.shadow.camera, 'left', -600, 0, 10).name('阴影左边界 | Shadow Left');
    dirFolder.add(dirLight.shadow.camera, 'right', 0, 600, 10).name('阴影右边界 | Shadow Right');
    dirFolder.add(dirLight.shadow.camera, 'top', 0, 600, 10).name('阴影上边界 | Shadow Top');
    dirFolder.add(dirLight.shadow.camera, 'bottom', -600, 0, 10).name('阴影下边界 | Shadow Bottom');
    dirFolder.add(dirLight.shadow.camera, 'near', 0.1, 100, 0.1).name('阴影近平面 | Shadow Near');
  }
}

// 动画循环
function animate() {
  requestAnimationFrame(animate);
  
  const deltaTime = clock.getDelta();
  const elapsed = clock.elapsedTime;
  
  // 更新物理
  if (shipController && shipController.body && simulatorEngine) {
    const shipState = {
      body: shipController.body,
      mesh: shipController.mesh
    };
    
    const environment = {
      time: elapsed,
      weather: weatherSystem.getWeatherState()
    };
    
    simulatorEngine.update(deltaTime, shipState, environment);
  }
  
  world.step(1 / 60, deltaTime, 3);
  
  // 更新船体
  if (shipController) {
    shipController.update(deltaTime);
  }
  
  // 更新水面
  if (waterUniforms) {
    waterUniforms.uTime.value = elapsed;
    waterUniforms.uAmplitude.value = waveParams.amplitude;
    waterUniforms.uWavelength.value = waveParams.wavelength;
    waterUniforms.uSpeed.value = waveParams.speed;
    waterUniforms.uSteepness.value = waveParams.steepness;
    waterUniforms.uYFlip.value = config.yFlip;
  }
  
  // 更新天气
  if (weatherSystem) {
    weatherSystem.update(deltaTime);
  }
  
  // 更新仪表盘
  if (shipDashboardDisplay) {
    shipDashboardDisplay.update(deltaTime);
  }
  
  controls.update();
  renderer.render(scene, camera);
}

// 窗口大小调整
function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// 启动
init();
