/**
 * 船舶数字孪生系统 - 重构版主文件
 * Ship Digital Twin System - Refactored Main File
 */

// ============= 导入 =============
// 使用 jsDelivr CDN (国内有CDN节点，速度快)
import * as THREE from '../public/lib/three.module.js';
import { OrbitControls } from '../public/lib/OrbitControls.js';
import * as CANNON from '../public/lib/cannon-es.js';
import GUI from '../public/lib/lil-gui.esm.min.js';

// 1. Imports
import { setupLights } from './scene/LightingSystem.js';
import { createWater } from './scene/EnvironmentSystem.js';
import { initializeRenderer } from './core/RendererSystem.js';

// ... (Inside init function) ...

// 设置灯光 (Using new module)
const lights = setupLights(scene);
hemiLight = lights.hemiLight;
dirLight = lights.dirLight;

// 创建水面 (Using new module)
waterMeshFar = createWater(scene, config);

// ... (Remove old functions at the bottom) ...

import { ShipController } from './ship/ShipController.js';
import { SimulatorEngine } from './physics/SimulatorEngine.js';
import { BuoyancyAlgorithm } from './physics/algorithms/BuoyancyAlgorithm.js';
import { StabilizerAlgorithm } from './physics/algorithms/StabilizerAlgorithm.js';
import { WindAlgorithm } from './physics/algorithms/WindAlgorithm.js';
import { RainAlgorithm } from './physics/algorithms/RainAlgorithm.js';
import { WeatherSystem } from './weather/WeatherSystem.js';
import { ShipStabilityAnalyzer } from './ship/ShipStabilityAnalyzer.js';
import { CabinManager } from './ship/cabins/CabinManager.js';
import { RealtimeDisplaySystem } from './data/RealtimeDisplaySystem.js';
import { VirtualDataSource } from './data/VirtualDataSource.js';
import { ShipDashboardDisplay } from './monitoring/ShipDashboardDisplay.js';
import { SafetyMonitor } from './monitoring/SafetyMonitor.js';
import { ScenarioSimulator } from './simulation/ScenarioSimulator.js';
import { InspectionScenario } from './simulation/InspectionScenario.js';
import { FireDrillScenario } from './simulation/FireDrillScenario.js';
import { AutoStabilizationSystem } from './ship/AutoStabilizationSystem.js';
import { ShipShoreSync } from './data/ShipShoreSync.js';
import { i18n } from './utils/i18n.js';
import { preRenderValidator } from './tests/PreRenderValidator.js';
import { patchThreeJS } from './tests/ThreeJSPatch.js';
import { initAutoValidator } from '../tests/AutoGUIValidator.js';

// ============= 全局变量 =============
let renderer, scene, camera, controls;
let world;
let shipController;
let simulatorEngine;
let weatherSystem;
let stabilityAnalyzer;
let cabinManager;
let realtimeDisplaySystem;
let virtualDataSource;
let shipDashboardDisplay;
let safetyMonitor;
let scenarioSimulator;
let inspectionScenario;
let fireDrillScenario;
let autoStabilizationSystem;
let shipShoreSync;
let waterMeshFar;
let gui;
let clock;
let lastStabilizationResult = null;

// 巡检相关
let isInspecting = false;
let originalCameraState = null;
let firstPersonControls = {
  moveSpeed: 5.0,
  lookSpeed: 0.002,
  keys: {
    forward: false,
    backward: false,
    left: false,
    right: false
  },
  mouse: {
    isDown: false,
    x: 0,
    y: 0
  },
  euler: new THREE.Euler(0, 0, 0, 'YXZ')
};

// 灯光
let hemiLight, dirLight;

// ============= 配置对象 =============
const config = {
  // 船体参数 - 138米长双体船
  boatSize: { x: 85, y: 95, z: 138 }, // 宽度、高度、长度
  boatMass: 37000000, // 37,000吨 = 37,000,000 kg
  draftDepth: 0, // 吃水深度0米（船底与水面接触）
  yFlip: -1, // Y轴翻转系数

  // 浮力参数
  buoyancy: {
    // 浮力系数：船体质量37,000,000 kg，重力363,340,000 N
    // 假设95个浮力点，船底与水面接触时平均深度约0.1米
    // 总浮力 = 95 × 0.1 × buoyancyCoeff ≈ 363,340,000
    // buoyancyCoeff ≈ 38,246,000
    // 考虑到浮力点分布和实际深度变化，设置为40,000,000确保船底与水面接触
    buoyancyCoeff: 40000000, // 浮力系数（使船底与水面接触）
    dragCoeff: 6, // 阻尼系数
    density: 1.0, // 水密度
    maxBuoyancy: 3.0, // 最大浮力倍数
    effectivePointCount: 0.2 // 有效浮力点比例
  },

  // 17级台风需要极强的稳定性
  stabilizer: {
    enableStabilizer: true,
    uprightStiffness: 12.0, // 自稳刚度
    uprightDamping: 6.0, // 自稳阻尼
    wobbleBoost: 0.8 // 降低摇晃增强，提高稳定性
  },

  // 显示选项
  display: {
    showAxesHelper: false,
    showDimensionLines: false,
    wireframeWater: false
  }
};

// ============= 初始化 =============
async function init() {
  // 确保DOM已加载
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
    return;
  }

  // 确保app元素存在
  const appElement = document.getElementById('app');
  if (!appElement) {
    console.warn('⚠️ 找不到app元素，等待DOM加载 | App element not found, waiting for DOM...');
    setTimeout(init, 100);
    return;
  }

  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1525);
  scene.fog = new THREE.Fog(0x0b1525, 60, 220);

  // 创建相机
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(15, 9, 22);

  // 立即应用 Three.js patch
  patchThreeJS();

  // 创建渲染器 (使用了 module 中的错误处理)
  try {
    renderer = await initializeRenderer('app');
    // 渲染器设置中已完成 toneMapping 等配置，直接继续
    _continueInit();
  } catch (e) {
    console.error("❌ 初始化致命错误 | Fatal Init Error:", e);
  }
}

// ============= 继续初始化 =============
function _continueInit() {
  if (!renderer || !camera) {
    console.error('❌ 渲染器或相机未初始化 | Renderer or camera not initialized');
    return;
  }

  try {
    // 创建控制器
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.target.set(0, 1.5, 0);

    // 创建时钟
    clock = new THREE.Clock();

    // 创建物理世界
    world = new CANNON.World({
      gravity: new CANNON.Vec3(0, -9.82, 0)
    });
    world.broadphase = new CANNON.SAPBroadphase(world);
    world.allowSleep = true;
    world.solver.iterations = 14;

    // 设置灯光 (使用新模块)
    const lights = setupLights(scene);
    hemiLight = lights.hemiLight;
    dirLight = lights.dirLight;

    // 创建水面 (使用新模块)
    waterMeshFar = createWater(scene, config);

    // 创建模拟器引擎
    simulatorEngine = new SimulatorEngine(world);

    // 将simulatorEngine暴露到全局
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

    // 创建稳定分析器
    stabilityAnalyzer = new ShipStabilityAnalyzer();

    // 创建船体控制器
    shipController = new ShipController(scene, world, {
      mass: config.boatMass,
      size: config.boatSize,
      draftDepth: config.draftDepth,
      yFlip: config.yFlip,
      desiredSize: config.boatSize,
      platformHeight: 45,
      catamaran: { enabled: true },
      glbPath: '/public/GLB_20251223141542.glb'
    });

    console.log('📦 船体控制器已创建 | Ship controller created');

    window.shipController = shipController;

    // 加载船体 (Calls the now-top-level function)
    loadBoat().catch(err => {
      console.error('❌ 船体加载过程中出错 | Error during ship loading:', err);
    });

    // 创建虚拟数据源
    virtualDataSource = new VirtualDataSource();

    // 延迟初始化子系统
    startSubsystems();

    // Window Resize
    window.addEventListener('resize', onResize);

    // Start Animation Loop
    animate();

  } catch (error) {
    console.error('❌ 初始化过程出错 | Error during initialization:', error);
  }
}

// ============= 子系统启动 =============
function startSubsystems() {
  setTimeout(() => {
    if (scene && virtualDataSource) {
      realtimeDisplaySystem = new RealtimeDisplaySystem(scene, virtualDataSource);
      realtimeDisplaySystem.initialize();
    }
  }, 1000);

  setTimeout(() => {
    if (scene && virtualDataSource) {
      shipDashboardDisplay = new ShipDashboardDisplay(scene, virtualDataSource);
      shipDashboardDisplay.initialize();
    }
  }, 1200);

  setTimeout(() => {
    if (scene && virtualDataSource) {
      safetyMonitor = new SafetyMonitor(scene, virtualDataSource);
      safetyMonitor.initialize();
    }
  }, 1500);

  // 场景与交互
  setTimeout(() => {
    if (scene && camera && shipController && weatherSystem) {
      scenarioSimulator = new ScenarioSimulator(scene, camera, shipController, weatherSystem);
    }
  }, 2000);

  setTimeout(() => {
    if (cabinManager) {
      inspectionScenario = new InspectionScenario(scene, camera, cabinManager, shipController);
      inspectionScenario.initialize();
    }
  }, 2500);

  setTimeout(() => {
    if (cabinManager) {
      fireDrillScenario = new FireDrillScenario(scene, camera, cabinManager, shipController);
      fireDrillScenario.initialize();
    }
  }, 3000);

  setTimeout(() => {
    if (stabilityAnalyzer && simulatorEngine && shipController) {
      autoStabilizationSystem = new AutoStabilizationSystem(stabilityAnalyzer, simulatorEngine, shipController);
    }
  }, 1000);

  setTimeout(() => {
    shipShoreSync = new ShipShoreSync(virtualDataSource, { autoConnect: true, syncInterval: 1000 });
    shipShoreSync.connect();
  }, 2500);

  setTimeout(() => {
    initializeCabins();
  }, 3000);

  setupGUI();
}

// ============= 动画循环 =============
function animate() {
  requestAnimationFrame(animate);
  const dt = clock.getDelta();

  if (controls) controls.update();

  // Physics
  if (world) {
    world.step(1 / 60, dt, 3);
  }

  // Engine
  if (simulatorEngine) {
    simulatorEngine.update(dt);
  }

  // Ship
  if (shipController) {
    shipController.update(dt);
    if (stabilityAnalyzer) stabilityAnalyzer.update(shipController);
  }

  // Systems
  if (weatherSystem) weatherSystem.update(dt);
  if (realtimeDisplaySystem) realtimeDisplaySystem.update();
  if (shipDashboardDisplay) shipDashboardDisplay.update();
  if (safetyMonitor) safetyMonitor.update();
  if (autoStabilizationSystem) autoStabilizationSystem.update(dt);
  if (inspectionScenario) inspectionScenario.update(dt);
  if (fireDrillScenario) fireDrillScenario.update(dt);

  // Render
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

// ============= 窗口调整 =============
function onResize() {
  if (camera && renderer) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

        <ol style="margin-top: 10px; padding-left: 20px;">
          <li>更新显卡驱动程序 | Update your graphics card drivers</li>
          <li>在浏览器设置中启用硬件加速 | Enable hardware acceleration in browser settings</li>
          <li>检查浏览器是否支持 WebGL | Check if your browser supports WebGL</li>
          <li>尝试使用其他浏览器（Chrome、Firefox、Edge）| Try a different browser</li>
          <li>检查系统是否禁用了 WebGL | Check if WebGL is disabled in your system</li>
          <li>关闭可能干扰 WebGL 的浏览器扩展 | Disable browser extensions that might interfere with WebGL</li>
        </ol>
      </div>
      <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
        <strong>快速检查 | Quick Check:</strong>
        <ul style="margin-top: 10px; padding-left: 20px;">
          <li>访问 <a href="https://get.webgl.org/" target="_blank">https://get.webgl.org/</a> 检查 WebGL 支持</li>
          <li>在 Chrome: 设置 → 系统 → 使用硬件加速（如果可用）</li>
          <li>在 Firefox: 设置 → 常规 → 性能 → 取消勾选"使用推荐的性能设置"</li>
        </ul>
      </div>
      <p style="color: #666; font-size: 12px; margin-top: 15px;">
        如果问题持续存在，请联系技术支持 | If the problem persists, please contact technical support.
      </p>
    </div>
  `;

// 创建错误对话框
const dialog = document.createElement('div');
dialog.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 10000;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  `;

const content = document.createElement('div');
content.style.cssText = `
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    max-width: 700px;
    max-height: 90vh;
    overflow-y: auto;
  `;
content.innerHTML = errorMsg;

const closeBtn = document.createElement('button');
closeBtn.textContent = '关闭 | Close';
closeBtn.style.cssText = `
    margin: 20px;
    padding: 10px 20px;
    background: #4fc3f7;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
  `;
closeBtn.onclick = () => {
  document.body.removeChild(dialog);
};
content.appendChild(closeBtn);

dialog.appendChild(content);
document.body.appendChild(dialog);
}

// ============= 初始化 =============
function init() {
  // 确保DOM已加载
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
    return;
  }

  // 确保app元素存在
  const appElement = document.getElementById('app');
  if (!appElement) {
    console.warn('⚠️ 找不到app元素，等待DOM加载 | App element not found, waiting for DOM...');
    setTimeout(init, 100);
    return;
  }

  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1525);
  scene.fog = new THREE.Fog(0x0b1525, 60, 220);

  // 创建相机
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(15, 9, 22);

  // 立即应用 Three.js patch
  patchThreeJS();

  // 创建渲染器（带错误处理和重试机制）
  _createWebGLRendererWithRetry();
}

// ============= WebGL 渲染器创建（带重试） =============
function _createWebGLRendererWithRetry(retryCount = 0) {
  const maxRetries = 3;
  const retryDelays = [0, 500, 1000, 2000]; // 首次立即，然后500ms, 1s, 2s

  if (retryCount > 0) {
    console.log(`🔄 重试创建WebGL渲染器 (${retryCount}/${maxRetries}) | Retrying WebGL renderer creation (${retryCount}/${maxRetries})...`);
  }

  renderer = _createWebGLRenderer();

  if (!renderer) {
    if (retryCount < maxRetries) {
      const delay = retryDelays[retryCount + 1] || 2000;
      console.warn(`⚠️ 创建失败，将在 ${delay}ms 后重试 | Creation failed, retrying in ${delay}ms...`);
      setTimeout(() => {
        _createWebGLRendererWithRetry(retryCount + 1);
      }, delay);
    } else {
      const error = new Error('经过多次重试后仍无法创建 WebGL 渲染器 | Unable to create WebGL renderer after multiple retries');
      console.error('❌', error.message);
      _showWebGLError(error);
      return;
    }
  } else {
    _setupRenderer();
  }
}

// ============= WebGL 渲染器创建辅助函数 =============
function _createWebGLRenderer() {
  try {
    // 首先检查WebGL支持
    const canvas = document.createElement('canvas');
    const webgl2 = canvas.getContext('webgl2');
    const webgl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    // 详细的WebGL支持诊断
    console.log('🔍 WebGL支持检测 | WebGL Support Detection:');
    console.log('  WebGL 2.0:', webgl2 ? '✅ 支持' : '❌ 不支持');
    console.log('  WebGL 1.0:', webgl ? '✅ 支持' : '❌ 不支持');

    if (!webgl2 && !webgl) {
      console.error('❌ 浏览器不支持 WebGL | Browser does not support WebGL');
      // 尝试检测原因
      const userAgent = navigator.userAgent;
      console.error('  用户代理 | User Agent:', userAgent);
      if (userAgent.includes('Chrome')) {
        console.error('  提示：Chrome浏览器，请检查 chrome://flags/#ignore-gpu-blacklist');
      } else if (userAgent.includes('Firefox')) {
        console.error('  提示：Firefox浏览器，请检查 about:config 中的 webgl.force-enabled');
      }
      return null;
    }

    // 如果只有WebGL 1.0，Three.js r165可能需要WebGL 2.0，但我们可以尝试降级
    if (!webgl2 && webgl) {
      console.warn('⚠️ 仅支持 WebGL 1.0，Three.js r165 可能需要 WebGL 2.0 | Only WebGL 1.0 supported, Three.js r165 may require WebGL 2.0');
      console.warn('  将尝试使用 WebGL 1.0 兼容模式 | Will try WebGL 1.0 compatibility mode');
    }

    // 尝试多种配置，从最优化到最宽松
    const rendererConfigs = [
      {
        antialias: true,
        powerPreference: 'high-performance',
        failIfMajorPerformanceCaveat: false,
        stencil: false,
        depth: true,
        alpha: false
      },
      {
        antialias: true,
        powerPreference: 'default',
        failIfMajorPerformanceCaveat: false,
        stencil: false,
        depth: true,
        alpha: false
      },
      {
        antialias: false,
        powerPreference: 'default',
        failIfMajorPerformanceCaveat: false,
        stencil: false,
        depth: true,
        alpha: false
      },
      {
        antialias: false,
        powerPreference: 'low-power',
        failIfMajorPerformanceCaveat: false,
        stencil: false,
        depth: true,
        alpha: false
      },
      {
        antialias: false,
        powerPreference: 'low-power',
        failIfMajorPerformanceCaveat: true,
        stencil: false,
        depth: true,
        alpha: false
      },
      // 最宽松的配置
      {
        antialias: false,
        powerPreference: 'low-power',
        failIfMajorPerformanceCaveat: true,
        preserveDrawingBuffer: false,
        premultipliedAlpha: false,
        stencil: false,
        depth: true,
        alpha: false
      }
    ];

    let rendererCreated = false;
    let lastError = null;
    let lastConfig = null;

    for (let i = 0; i < rendererConfigs.length; i++) {
      const config = rendererConfigs[i];
      try {
        console.log(`🔄 尝试配置 ${i + 1}/${rendererConfigs.length} | Trying config ${i + 1}/${rendererConfigs.length}:`, config);

        // 使用try-catch包装，因为Three.js可能抛出异常
        const testRenderer = new THREE.WebGLRenderer(config);

        // 验证渲染器是否真的可用
        if (testRenderer && testRenderer.domElement) {
          const gl = testRenderer.getContext();
          if (gl) {
            // 检查上下文是否丢失（WebGL 2.0才有isContextLost方法）
            if (typeof gl.isContextLost === 'function' && gl.isContextLost()) {
              console.warn('⚠️ 渲染器上下文已丢失 | Renderer context lost');
              testRenderer.dispose();
              continue;
            }

            // 检查WebGL版本（安全获取）
            try {
              const version = gl.getParameter(gl.VERSION);
              const vendor = gl.getParameter(gl.VENDOR);
              const rendererInfo = gl.getParameter(gl.RENDERER);
              console.log('  WebGL版本 | WebGL Version:', version);
              console.log('  供应商 | Vendor:', vendor);
              console.log('  渲染器信息 | Renderer Info:', rendererInfo);
            } catch (paramError) {
              console.warn('⚠️ 无法获取WebGL参数 | Cannot get WebGL parameters:', paramError);
            }

            // 验证基本功能
            try {
              const testShader = gl.createShader(gl.VERTEX_SHADER);
              if (!testShader) {
                throw new Error('无法创建测试着色器 | Cannot create test shader');
              }
              gl.deleteShader(testShader);
            } catch (shaderError) {
              console.warn('⚠️ 着色器创建测试失败 | Shader creation test failed:', shaderError);
              testRenderer.dispose();
              continue;
            }

            // 成功创建渲染器
            renderer = testRenderer;
            rendererCreated = true;
            lastConfig = config;
            console.log('✅ WebGL 渲染器创建成功 | WebGL renderer created successfully');
            console.log('  使用配置 | Using config:', config);

            break;
          } else {
            console.warn('⚠️ 无法获取WebGL上下文 | Cannot get WebGL context');
            testRenderer.dispose();
          }
        } else {
          console.warn('⚠️ 渲染器或DOM元素无效 | Renderer or DOM element invalid');
          if (testRenderer) {
            testRenderer.dispose();
          }
        }
      } catch (e) {
        lastError = e;
        console.warn(`⚠️ 配置 ${i + 1} 失败 | Config ${i + 1} failed:`, e.message);
        if (e.stack) {
          console.warn('  堆栈 | Stack:', e.stack.split('\n').slice(0, 3).join('\n'));
        }
        continue;
      }
    }

    if (!rendererCreated) {
      console.error('❌ 所有渲染器配置都失败 | All renderer configs failed');
      if (lastError) {
        console.error('  最后错误 | Last error:', lastError.message);
        if (lastError.stack) {
          console.error('  堆栈 | Stack:', lastError.stack);
        }
      }

      // 提供详细的诊断信息
      console.error('📋 诊断信息 | Diagnostic Info:');
      console.error('  User Agent:', navigator.userAgent);
      console.error('  Platform:', navigator.platform);
      console.error('  Hardware Concurrency:', navigator.hardwareConcurrency || 'unknown');
      console.error('  Device Memory:', navigator.deviceMemory || 'unknown');

      // 尝试获取GPU信息（如果可用）
      if (navigator.gpu) {
        navigator.gpu.requestAdapter().then(adapter => {
          if (adapter) {
            console.error('  GPU Adapter:', adapter.info || 'available');
          }
        }).catch(() => { });
      }

      return null;
    }

    return renderer;
  } catch (error) {
    console.error('❌ WebGL 渲染器创建过程出错 | Error during WebGL renderer creation:', error);
    console.error('  错误类型 | Error type:', error.constructor.name);
    console.error('  错误消息 | Error message:', error.message);
    if (error.stack) {
      console.error('  堆栈 | Stack:', error.stack);
    }
    return null;
  }
}

// ============= 渲染器设置 =============
function _setupRenderer() {
  if (!renderer) {
    console.error('❌ 渲染器未创建，无法设置 | Renderer not created, cannot setup');
    return;
  }

  try {
    // 验证渲染器上下文
    const gl = renderer.getContext();
    if (!gl) {
      throw new Error('渲染器上下文无效 | Renderer context invalid');
    }

    if (gl.isContextLost()) {
      throw new Error('渲染器上下文已丢失 | Renderer context lost');
    }

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // 启用物理材质支持（透明玻璃需要）
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3; // 增加曝光度，让透明船体更清晰可见

    // 设置颜色空间（Three.js r165+ 使用 outputColorSpace，旧版本使用 outputEncoding）
    if (renderer.outputColorSpace !== undefined) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    } else if (renderer.outputEncoding !== undefined) {
      renderer.outputEncoding = THREE.sRGBEncoding;
    }

    // 设置 transmission 分辨率缩放（确保 transmission render target 正确初始化）
    if (renderer.transmissionResolutionScale !== undefined) {
      renderer.transmissionResolutionScale = 0.5; // 降低分辨率以提高性能
    }

    // 确保物理光照正确（MeshPhysicalMaterial需要）
    // 注意：Three.js r165 中，physicallyCorrectLights 已废弃，使用 toneMapping 代替

    // 确保app元素存在
    const appElement = document.getElementById('app');
    if (!appElement) {
      throw new Error('找不到app元素 | App element not found');
    }

    // 清除可能存在的旧渲染器
    const oldCanvas = appElement.querySelector('canvas');
    if (oldCanvas) {
      oldCanvas.remove();
    }

    appElement.appendChild(renderer.domElement);

    console.log('✅ WebGL 渲染器设置完成 | WebGL renderer setup completed');

    // 继续初始化其他组件
    _continueInit();

  } catch (error) {
    console.error('❌ WebGL 渲染器设置失败 | WebGL renderer setup failed:', error);

    // 提供更详细的错误信息
    let errorMessage = error.message || '无法设置 WebGL 渲染器 | Could not setup WebGL renderer';

    // 检查是否是 WebGL 不支持的错误
    if (errorMessage.includes('WebGL') || errorMessage.includes('context')) {
      // 尝试检测 WebGL 支持情况
      // 1. Imports
      import { setupLights } from './scene/LightingSystem.js';
      import { createWater } from './scene/EnvironmentSystem.js';
      import { initializeRenderer } from './core/RendererSystem.js';

      // ...

      // ============= 初始化 =============
      async function init() {
        // 确保DOM已加载
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', init);
          return;
        }

        // 确保app元素存在
        const appElement = document.getElementById('app');
        if (!appElement) {
          console.warn('⚠️ 找不到app元素，等待DOM加载 | App element not found, waiting for DOM...');
          setTimeout(init, 100);
          return;
        }

        // 创建场景
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0b1525);
        scene.fog = new THREE.Fog(0x0b1525, 60, 220);

        // 创建相机
        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
        camera.position.set(15, 9, 22);

        // 立即应用 Three.js patch
        patchThreeJS();

        // 创建渲染器 (Using new module)
        try {
          renderer = await initializeRenderer('app');

          // 渲染器设置中已完成 toneMapping 等配置，这里直接继续初始化
          _continueInit();
        } catch (e) {
          console.error("❌ 初始化致命错误 | Fatal Init Error:", e);
          // Error dialog is shown by RendererSystem
        }
      }

      // ============= 继续初始化 =============
      function _continueInit() {
        if (!renderer || !camera) {
          console.error('❌ 渲染器或相机未初始化，无法继续 | Renderer or camera not initialized');
          return;
        }

        try {
          // 创建控制器
          controls = new OrbitControls(camera, renderer.domElement);
          controls.enableDamping = true;
          controls.maxPolarAngle = Math.PI * 0.49;
          controls.target.set(0, 1.5, 0);

          // 创建时钟
          clock = new THREE.Clock();

          // 创建物理世界
          world = new CANNON.World({
            gravity: new CANNON.Vec3(0, -9.82, 0)
          });
          world.broadphase = new CANNON.SAPBroadphase(world);
          world.allowSleep = true;
          world.solver.iterations = 14;


          // 设置灯光 (Using new module)
          const lights = setupLights(scene);
          hemiLight = lights.hemiLight;
          dirLight = lights.dirLight;

          // 创建水面 (Using new module)
          waterMeshFar = createWater(scene, config);

          // 创建模拟器引擎
          simulatorEngine = new SimulatorEngine(world);

          // 将simulatorEngine暴露到全局，方便其他模块访问
          window.simulatorEngine = simulatorEngine;

          // 注册算法
          const buoyancyAlg = new BuoyancyAlgorithm(config.buoyancy);
          simulatorEngine.registerAlgorithm(buoyancyAlg);
          buoyancyAlg.initialize(world, scene); // 传递scene用于可视化

          const stabilizerAlg = new StabilizerAlgorithm(config.stabilizer);
          simulatorEngine.registerAlgorithm(stabilizerAlg);

          const windAlg = new WindAlgorithm({ windSpeed: 0, windDirection: 0 });
          simulatorEngine.registerAlgorithm(windAlg);

          const rainAlg = new RainAlgorithm({ rainIntensity: 0 });
          simulatorEngine.registerAlgorithm(rainAlg);

          // 创建天气系统
          weatherSystem = new WeatherSystem(scene, simulatorEngine);
          weatherSystem.initialize(); // 初始化天气视觉效果（雨粒子和风向指示器）

          // 创建稳定分析器
          stabilityAnalyzer = new ShipStabilityAnalyzer();

          // 创建船体控制器
          shipController = new ShipController(scene, world, {
            mass: config.boatMass,
            size: config.boatSize,
            draftDepth: config.draftDepth,
            yFlip: config.yFlip,
            desiredSize: config.boatSize,
            platformHeight: 45,
            catamaran: { enabled: true },
            glbPath: '/public/GLB_20251223141542.glb' // 明确指定GLB路径（绝对路径）
          });

          console.log('📦 船体控制器已创建 | Ship controller created');
          console.log('📁 GLB路径配置 | GLB path:', shipController.config.glbPath);

          // 将 shipController 暴露到 window 对象，供 HTML 中的函数调用
          window.shipController = shipController;

          // 加载船体（异步，不阻塞）
          loadBoat().catch(err => {
            console.error('❌ 船体加载过程中出错 | Error during ship loading:', err);
          });

          // 创建虚拟数据源
          virtualDataSource = new VirtualDataSource();

          // 创建实时数据显示系统（延迟初始化）
          setTimeout(() => {
            realtimeDisplaySystem = new RealtimeDisplaySystem(scene, virtualDataSource);
            realtimeDisplaySystem.initialize();
          }, 1000);

          // 创建船舶仪表盘显示系统（延迟初始化）
          setTimeout(() => {
            shipDashboardDisplay = new ShipDashboardDisplay(scene, virtualDataSource);
            shipDashboardDisplay.initialize();
          }, 1200);

          // 显示 WebGL 错误对话框
          // 创建安全态势监控系统（延迟1.5秒初始化）
          setTimeout(() => {
            safetyMonitor = new SafetyMonitor(scene, virtualDataSource);
            safetyMonitor.initialize();
            console.log('✅ Safety monitoring system initialized');
          }, 1500);

          // 创建场景预演系统（延迟2秒初始化）
          setTimeout(() => {
            scenarioSimulator = new ScenarioSimulator(scene, camera, shipController, weatherSystem);
            // 注意：ScenarioSimulator 在构造函数中已完成初始化（调用 initializeScenarios 和 setupFirstPersonControls）
            console.log('✅ Scenario simulator initialized');
          }, 2000);

          // 创建巡检场景系统（延迟2.5秒初始化）
          setTimeout(() => {
            if (cabinManager) {
              inspectionScenario = new InspectionScenario(scene, camera, cabinManager, shipController);
              inspectionScenario.initialize();
              console.log('✅ Inspection scenario initialized');
            }
          }, 2500);

          // 创建消防演练场景系统（延迟3秒初始化）
          setTimeout(() => {
            if (cabinManager) {
              fireDrillScenario = new FireDrillScenario(scene, camera, cabinManager, shipController);
              fireDrillScenario.initialize();
              console.log('✅ Fire drill scenario initialized');
            }
          }, 3000);

          // 创建自动稳定系统（延迟1秒初始化）
          setTimeout(() => {
            if (stabilityAnalyzer && simulatorEngine && shipController) {
              autoStabilizationSystem = new AutoStabilizationSystem(
                stabilityAnalyzer,
                simulatorEngine,
                shipController
              );
              console.log('✅ Auto stabilization system initialized');
            }
          }, 1000);

          // 创建船岸数据同步系统（延迟2.5秒初始化并自动连接）
          setTimeout(() => {
            shipShoreSync = new ShipShoreSync(virtualDataSource, {
              autoConnect: true,
              syncInterval: 1000
            });
            // ShipShoreSync 没有 initialize() 方法，需要手动调用 connect() 来连接
            shipShoreSync.connect();
            console.log('✅ Ship-shore sync system initialized and connected');
          }, 2500);

          // 创建舱室管理器（延迟初始化，等待船体加载完成）
          setTimeout(() => {
            initializeCabins();
          }, 3000);

          // 设置GUI
          setupGUI();

          // 窗口大小调整
          window.addEventListener('resize', onResize);

        } catch (error) {
          console.error('❌ 初始化过程出错 | Error during initialization:', error);
          _showWebGLError(new Error('初始化失败: ' + error.message));
        }
      }

      async function loadBoat() {
        try {
          console.log('🚢 开始加载船体模型 | Starting to load ship model...');
          console.log('📁 模型路径配置 | Model path config:', shipController.config.glbPath);

          await shipController.load();

          if (shipController.loaded && shipController.mesh) {
            console.log('✅ 船体模型加载成功 | Ship model loaded successfully');
            console.log('📏 船体尺寸 | Ship size:', shipController.size);

            // 使用实际船体尺寸重新生成浮力点（沿Z轴均匀分布）
            if (shipController.size && simulatorEngine) {
              const buoyancyAlg = simulatorEngine.getAlgorithm('Buoyancy');
              if (buoyancyAlg) {
                // 使用实际船体尺寸生成浮力点
                buoyancyAlg.generateBuoyancyPoints({
                  x: shipController.size.x, // 宽度
                  y: shipController.size.y, // 高度
                  z: shipController.size.z  // 长度（Z轴，蓝色轴线）
                });
                console.log('✅ 浮力点已根据实际船体尺寸重新生成 | Buoyancy points regenerated with actual ship size');
              }
            }

            // 如果舱室管理器已初始化，重新绑定所有舱室到船体
            if (cabinManager && cabinManager.cabins) {
              console.log('🔄 重新绑定舱室到船体 | Rebinding cabins to ship...');
              console.log(`   舱室数量 | Cabin count: ${cabinManager.cabins.size}`);
              cabinManager.cabins.forEach((cabin, cabinId) => {
                console.log(`   检查舱室 | Checking cabin: ${cabin.name}`);
                console.log(`     mesh存在: ${cabin.mesh ? 'yes' : 'no'}`);
                if (cabin.mesh) {
                  console.log(`     mesh父对象: ${cabin.mesh.parent ? (cabin.mesh.parent.name || 'Group') : 'null'}`);
                  console.log(`     mesh可见性: ${cabin.mesh.visible}`);
                  console.log(`     目标父对象: ${shipController.mesh ? 'shipController.mesh' : 'null'}`);

                  // 检查舱室mesh是否已添加到场景但未绑定到船体
                  if (cabin.mesh.parent !== shipController.mesh) {
                    // 从场景中移除
                    if (cabin.mesh.parent) {
                      cabin.mesh.parent.remove(cabin.mesh);
                      console.log(`     从原父对象移除 | Removed from parent`);
                    }
                    // 添加到船体
                    shipController.mesh.add(cabin.mesh);
                    cabin.mesh.visible = true;
                    cabin.mesh.traverse((child) => {
                      if (child.isMesh || child.isGroup) {
                        child.visible = true;
                      }
                    });
                    console.log(`✅ 舱室 ${cabin.name} 已重新绑定到船体 | Cabin ${cabin.name} rebound to ship`);
                  } else {
                    console.log(`     ✅ 舱室 ${cabin.name} 已在船体上 | Cabin ${cabin.name} already on ship`);
                  }
                } else {
                  console.warn(`     ⚠️ 舱室 ${cabin.name} 没有mesh | Cabin ${cabin.name} has no mesh`);
                }
              });
            } else {
              console.warn('⚠️ 舱室管理器未初始化 | Cabin manager not initialized');
            }

            // 立即放置，不等待
            if (shipController.body) {
              shipController.body.quaternion.set(0, 0, 0, 1);
              shipController.body.velocity.setZero();
              shipController.body.angularVelocity.setZero();
              shipController.body.force.setZero();
              shipController.body.torque.setZero();

              // 立即放置在水面附近
              shipController.placeOnWater(clock.elapsedTime);
              console.log('🚢 Boat placed on water surface');
              console.log('💡 提示：船体已放置在水面，请点击"船身稳定"按钮来调整浮力并稳定船体');
              // 注意：不再自动触发稳定化，等待用户点击"船身稳定"按钮

              // 运行材质验证和修复（使用 PreRenderValidator）
              try {
                console.log('🔍 验证和修复材质 | Validating and fixing materials...');
                const fixCount = preRenderValidator.validateBeforeRender(scene, true);
                if (fixCount > 0) {
                  console.log(`✅ 已修复 ${fixCount} 个 uniform 问题 | Fixed ${fixCount} uniform issues`);
                } else {
                  console.log('✅ 材质验证通过 | Material validation passed');
                }
              } catch (diagError) {
                console.error('❌ 材质验证失败 | Material validation failed:', diagError);
              }
            } else {
              console.warn('⚠️ 船体物理体未创建 | Ship physics body not created');
            }
          } else {
            console.error('❌ 船体模型加载失败 | Ship model loading failed');
            console.error('   loaded:', shipController.loaded);
            console.error('   mesh:', shipController.mesh ? 'exists' : 'null');
          }
        } catch (error) {
          console.error('❌ Failed to load ship:', error);
          console.error('   错误详情 | Error details:', error.message);
          console.error('   堆栈 | Stack:', error.stack);
          // 错误弹窗已在ShipController中显示
        }
      }

      // ============= 初始化舱室 =============
      function initializeCabins() {
        const maxRetries = 100; // 最多重试100次（10秒）
        let retries = 0;

        const tryInitialize = () => {
          if (shipController && shipController.loaded && shipController.mesh) {
            try {
              // 如果已经初始化过，先清除
              if (cabinManager) {
                console.log('🔄 重新初始化舱室管理器 | Reinitializing cabin manager...');
                cabinManager.clearAllCabins();
              }

              cabinManager = new CabinManager(scene, camera, shipController);
              cabinManager.initialize();
              console.log('✅ 舱室管理器初始化完成 | Cabin manager initialized');
              console.log(`   舱室数量 | Cabin count: ${cabinManager.cabins.size}`);

              // 验证舱室是否正确添加
              cabinManager.cabins.forEach((cabin, id) => {
                if (cabin.mesh) {
                  console.log(`   ✅ ${cabin.name}: mesh存在, 父对象=${cabin.mesh.parent ? (cabin.mesh.parent.name || 'Group') : 'null'}, 可见=${cabin.mesh.visible}`);
                  if (cabin.indicator) {
                    console.log(`     指示器存在, 可见=${cabin.indicator.visible}, 在场景中=${scene.children.includes(cabin.indicator)}`);
                  }
                } else {
                  console.warn(`   ⚠️ ${cabin.name}: mesh不存在`);
                }
              });
            } catch (error) {
              console.error('❌ Error initializing cabin manager:', error);
              console.error('   错误详情 | Error details:', error.message);
              console.error('   堆栈 | Stack:', error.stack);
            }
          } else {
            retries++;
            if (retries < maxRetries) {
              setTimeout(tryInitialize, 100);
            } else {
              console.warn('⚠️ 舱室初始化超时 | Cabin initialization timeout');
              console.warn(`   shipController=${shipController ? 'exists' : 'null'}`);
              console.warn(`   shipController.loaded=${shipController ? shipController.loaded : 'N/A'}`);
              console.warn(`   shipController.mesh=${shipController && shipController.mesh ? 'exists' : 'null'}`);
            }
          }
        };

        tryInitialize();
      }

      // ============= 材质快速修复（仅针对关键问题） =============
      function quickFixMaterials() {
        if (!scene) return;

        scene.traverse((object) => {
          if (!object || !object.material) return;

          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => {
            if (!material) return;

            // 只检查 ShaderMaterial 的 uniforms
            if (material.type === 'ShaderMaterial' && material.uniforms) {
              for (const uniformName in material.uniforms) {
                try {
                  const uniform = material.uniforms[uniformName];
                  if (!uniform || typeof uniform !== 'object' || !('value' in uniform) || uniform.value === undefined) {
                    material.uniforms[uniformName] = { value: 0.0 };
                  }
                } catch (e) {
                  // 静默失败
                }
              }
            }
          });
        });
      }

      // ============= 更新循环 =============
      function animate() {
        requestAnimationFrame(animate);

        // 检查必要的变量是否已初始化
        if (!clock || !renderer || !scene || !camera) {
          // 如果初始化未完成，跳过这一帧
          return;
        }

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

          // 模拟器引擎统一更新
          simulatorEngine.update(deltaTime, shipState, environment);
        }

        // 物理世界步进
        world.step(1 / 60, deltaTime, 3);

        // 更新船体控制器
        if (shipController) {
          shipController.update(deltaTime);
        }

        // 更新水面（简单 shader，使用 waterUniforms）
        if (waterUniforms && typeof waterUniforms === 'object') {
          try {
            // 确保所有 uniform 都存在且有效
            if (!waterUniforms.uTime || typeof waterUniforms.uTime !== 'object' || !('value' in waterUniforms.uTime)) {
              waterUniforms.uTime = { value: 0 };
            }
            if (!waterUniforms.uAmplitude || typeof waterUniforms.uAmplitude !== 'object' || !('value' in waterUniforms.uAmplitude)) {
              waterUniforms.uAmplitude = { value: 0.8 };
            }
            if (!waterUniforms.uWavelength || typeof waterUniforms.uWavelength !== 'object' || !('value' in waterUniforms.uWavelength)) {
              waterUniforms.uWavelength = { value: 12.0 };
            }
            if (!waterUniforms.uSpeed || typeof waterUniforms.uSpeed !== 'object' || !('value' in waterUniforms.uSpeed)) {
              waterUniforms.uSpeed = { value: 1.2 };
            }
            if (!waterUniforms.uSteepness || typeof waterUniforms.uSteepness !== 'object' || !('value' in waterUniforms.uSteepness)) {
              waterUniforms.uSteepness = { value: 0.65 };
            }
            if (!waterUniforms.uYFlip || typeof waterUniforms.uYFlip !== 'object' || !('value' in waterUniforms.uYFlip)) {
              waterUniforms.uYFlip = { value: 1.0 };
            }

            // 更新 uniform 值
            waterUniforms.uTime.value = elapsed;

            // 使用waveParams对象（从waves.js导入），而不是直接访问属性
            if (waveParams && typeof waveParams === 'object') {
              waterUniforms.uAmplitude.value = (waveParams.amplitude !== undefined && waveParams.amplitude !== null) ? waveParams.amplitude : 0.8;
              waterUniforms.uWavelength.value = (waveParams.wavelength !== undefined && waveParams.wavelength !== null) ? waveParams.wavelength : 12.0;
              waterUniforms.uSpeed.value = (waveParams.speed !== undefined && waveParams.speed !== null) ? waveParams.speed : 1.2;
              waterUniforms.uSteepness.value = (waveParams.steepness !== undefined && waveParams.steepness !== null) ? waveParams.steepness : 0.65;
            }

            if (config && config.yFlip !== undefined) {
              waterUniforms.uYFlip.value = config.yFlip;
            }
          } catch (err) {
            // 静默处理错误，避免中断动画循环
            console.warn('⚠️ Error updating water uniforms:', err);
          }
        }

        // 更新天气系统
        if (weatherSystem) {
          weatherSystem.update(deltaTime);

          // 根据天气自动调整波浪参数
          if (waterUniforms && typeof waterUniforms === 'object') {
            try {
              const waveParams = weatherSystem.getWaveParameters();
              if (waveParams && typeof waveParams === 'object' && waveParams.amplitude > 0) {
                // 确保所有 uniform 都存在
                if (!waterUniforms.uAmplitude || typeof waterUniforms.uAmplitude !== 'object' || !('value' in waterUniforms.uAmplitude)) {
                  waterUniforms.uAmplitude = { value: 0.8 };
                }
                if (!waterUniforms.uWavelength || typeof waterUniforms.uWavelength !== 'object' || !('value' in waterUniforms.uWavelength)) {
                  waterUniforms.uWavelength = { value: 12.0 };
                }
                if (!waterUniforms.uSpeed || typeof waterUniforms.uSpeed !== 'object' || !('value' in waterUniforms.uSpeed)) {
                  waterUniforms.uSpeed = { value: 1.2 };
                }
                if (!waterUniforms.uSteepness || typeof waterUniforms.uSteepness !== 'object' || !('value' in waterUniforms.uSteepness)) {
                  waterUniforms.uSteepness = { value: 0.65 };
                }

                // 平滑过渡波浪参数（安全检查）
                const currentAmp = (waterUniforms.uAmplitude.value || 0);
                const newAmp = (waveParams.amplitude !== undefined && waveParams.amplitude !== null) ? waveParams.amplitude : 0.8;
                waterUniforms.uAmplitude.value = currentAmp * 0.95 + newAmp * 0.05;

                const currentWl = (waterUniforms.uWavelength.value || 0);
                const newWl = (waveParams.wavelength !== undefined && waveParams.wavelength !== null) ? waveParams.wavelength : 12.0;
                waterUniforms.uWavelength.value = currentWl * 0.95 + newWl * 0.05;

                const currentSpeed = (waterUniforms.uSpeed.value || 0);
                const newSpeed = (waveParams.speed !== undefined && waveParams.speed !== null) ? waveParams.speed : 1.2;
                waterUniforms.uSpeed.value = currentSpeed * 0.95 + newSpeed * 0.05;

                const newSteepness = (waveParams.steepness !== undefined && waveParams.steepness !== null) ? waveParams.steepness : 0.65;
                waterUniforms.uSteepness.value = newSteepness;
              }
            } catch (err) {
              // 静默处理错误，避免中断动画循环
              console.warn('⚠️ Error updating wave parameters from weather:', err);
            }
          }

          // 根据天气调整灯光（每帧更新，平滑过渡）
          _updateLightingForWeather();
        }

        // 更新自动稳定系统
        if (autoStabilizationSystem) {
          autoStabilizationSystem.update(deltaTime, clock);
        }

        // 更新巡检场景
        if (inspectionScenario) {
          inspectionScenario.update(deltaTime);
        }

        // 更新消防演练场景
        if (fireDrillScenario) {
          fireDrillScenario.update(deltaTime);
        }

        // 更新舱室系统
        if (cabinManager) {
          cabinManager.update(deltaTime);
        }

        // 更新实时数据显示系统
        if (realtimeDisplaySystem) {
          realtimeDisplaySystem.update(deltaTime);
        }

        // 更新安全态势监控系统
        if (safetyMonitor) {
          safetyMonitor.update(deltaTime);
        }

        // 更新船舶仪表盘显示系统
        if (shipDashboardDisplay) {
          shipDashboardDisplay.update(deltaTime);
        }

        // 更新HTML仪表盘数据
        if (virtualDataSource && typeof window.updateDashboardData === 'function') {
          const now = Date.now();
          if (!window.lastDashboardUpdate || now - window.lastDashboardUpdate > 200) {
            const data = virtualDataSource.getAllData();
            window.updateDashboardData(data);
            window.lastDashboardUpdate = now;
          }
        }

        // 更新巡检第一人称移动
        if (isInspecting) {
          updateInspectionMovement(deltaTime);
        }

        // 更新场景预演系统
        if (scenarioSimulator) {
          scenarioSimulator.update(deltaTime);
        }

        // 更新船岸数据同步系统
        if (shipShoreSync) {
          shipShoreSync.update(deltaTime);
        }

        // 更新控制器
        controls.update();

        // 渲染（使用多层保护）
        if (renderer && scene && camera) {
          try {
            // 第一层：PreRenderValidator 验证和修复
            const fixCount = preRenderValidator.validateBeforeRender(scene);

            if (fixCount > 0 && (!window._lastValidatorFixLog || Date.now() - window._lastValidatorFixLog > 5000)) {
              console.log(`🔧 PreRenderValidator 自动修复了 ${fixCount} 个 uniform 问题 | Auto-fixed ${fixCount} uniform issues`);
              window._lastValidatorFixLog = Date.now();
            }

            // 第二层：紧急修复（如果存在，只执行一次）
            if (window._fixAllUniforms && !window._emergencyFixApplied) {
              const emergencyFixCount = window._fixAllUniforms(scene);
              if (emergencyFixCount > 0) {
                window._emergencyFixApplied = true;
              }
            }

            // 执行渲染
            renderer.render(scene, camera);

          } catch (renderError) {
            // 渲染错误：只记录一次
            if (!window._renderErrorLogged) {
              console.error('❌ 渲染错误 | Render error:', renderError);
              console.error('   错误消息 | Error message:', renderError.message);

              // 最后的尝试：使用紧急修复（只执行一次）
              if (window._fixAllUniforms && !window._emergencyFixApplied) {
                console.log('🚑 使用紧急修复...');
                window._fixAllUniforms(scene);
                window._emergencyFixApplied = true;
              }

              window._renderErrorLogged = true;
            }
          }
        }

        // 更新状态显示（每帧更新）
        updateStatus();
      }

      // ============= GUI设置 =============
      function setupGUI() {
        gui = new GUI({ width: 380, title: i18n.gui.title });
        gui.domElement.style.zIndex = '20';

        const numericCtrls = [];

        // 海况文件夹
        const seaConditionFolder = gui.addFolder(i18n.seaCondition.folder);

        // 波浪参数
        const waveFolder = seaConditionFolder.addFolder(i18n.wave.folder);
        numericCtrls.push(waveFolder.add(waveParams, 'amplitude', 0.1, 3.0, 0.05).name(i18n.wave.amplitude));
        numericCtrls.push(waveFolder.add(waveParams, 'wavelength', 4, 40, 0.5).name(i18n.wave.wavelength));
        numericCtrls.push(waveFolder.add(waveParams, 'speed', 0.2, 4.0, 0.05).name(i18n.wave.speed));
        numericCtrls.push(waveFolder.add(waveParams, 'steepness', 0.2, 1.2, 0.02).name(i18n.wave.steepness));
        waveFolder.add(config.display, 'wireframeWater').name(i18n.display.wireframeWater).onChange((v) => {
          if (waterMeshFar && waterMeshFar.material) {
            waterMeshFar.material.wireframe = v;
          }
        });

        // 天气系统
        const weatherFolder = seaConditionFolder.addFolder(i18n.weather.folder);

        // 保存天气控件引用，用于预设切换时更新GUI显示
        const weatherControls = {};

        weatherFolder.add(weatherSystem, 'preset', Object.keys(i18n.weather.presets)).name(i18n.weather.preset)
          .onChange((value) => {
            // 设置天气预设
            weatherSystem.setPreset(value);

            // 更新所有天气控件的显示值
            if (weatherControls.windSpeed) weatherControls.windSpeed.updateDisplay();
            if (weatherControls.windDirection) weatherControls.windDirection.updateDisplay();
            if (weatherControls.rainIntensity) weatherControls.rainIntensity.updateDisplay();
            if (weatherControls.snowIntensity) weatherControls.snowIntensity.updateDisplay();
            if (weatherControls.temperature) weatherControls.temperature.updateDisplay();

            // 调整灯光以适应天气
            _updateLightingForWeather();

            console.log(`🌤️ 天气预设已更新到: ${value} | Weather preset updated to: ${value}`);
          });

        weatherControls.windSpeed = weatherFolder.add(weatherSystem.weather, 'windSpeed', 0, 100, 0.5).name(i18n.weather.windSpeed)
          .onChange((value) => {
            // 使用WeatherSystem的方法来更新，这样会同时更新视觉效果和算法
            weatherSystem.setWind(value, weatherSystem.weather.windDirection);
          });
        numericCtrls.push(weatherControls.windSpeed);

        weatherControls.windDirection = weatherFolder.add(weatherSystem.weather, 'windDirection', 0, 360, 1).name(i18n.weather.windDirection)
          .onChange((value) => {
            // 使用WeatherSystem的方法来更新，这样会同时更新视觉效果和算法
            weatherSystem.setWind(weatherSystem.weather.windSpeed, value);
          });
        numericCtrls.push(weatherControls.windDirection);

        weatherControls.rainIntensity = weatherFolder.add(weatherSystem.weather, 'rainIntensity', 0, 200, 1).name(i18n.weather.rainIntensity)
          .onChange((value) => {
            // 使用WeatherSystem的方法来更新，这样会同时更新视觉效果和算法
            weatherSystem.setRain(value);
            // 调整灯光以适应天气
            _updateLightingForWeather();
          });
        numericCtrls.push(weatherControls.rainIntensity);

        // 降雪控制（确保可以调整）
        // 允许用户调整降雪强度，即使温度>0也可以设置（但不会显示降雪效果）
        weatherControls.snowIntensity = weatherFolder.add(weatherSystem.weather, 'snowIntensity', 0, 100, 1)
          .name('降雪强度 | Snow Intensity (mm/h)')
          .onChange((value) => {
            // 直接设置降雪强度，允许用户调整
            // setSnow方法内部会处理温度检查
            weatherSystem.setSnow(value);
            _updateLightingForWeather();

            // 如果温度>0且降雪强度>0，提示用户
            if (weatherSystem.weather.temperature > 0 && value > 0) {
              console.log(`💡 提示：当前温度 ${weatherSystem.weather.temperature}°C > 0°C，降雪已自动转换为降雨 | Tip: Temperature > 0°C, snow converted to rain`);
            }
          });
        numericCtrls.push(weatherControls.snowIntensity);

        // 温度控制（影响降雨/降雪）
        weatherControls.temperature = weatherFolder.add(weatherSystem.weather, 'temperature', -20, 30, 1).name('温度 | Temperature (°C)')
          .onChange((value) => {
            weatherSystem.setTemperature(value);
          });
        numericCtrls.push(weatherControls.temperature);

        // 台风等级控制（1-17级）
        const typhoonControl = weatherFolder.add({ typhoonLevel: 0 }, 'typhoonLevel', 0, 17, 1)
          .name('台风等级 | Typhoon Level (0=关闭)')
          .onChange((value) => {
            if (value > 0) {
              weatherSystem.setTyphoonLevel(value);
            } else {
              // 关闭台风，恢复平静
              weatherSystem.setPreset('calm');
            }
          });

        // 物理文件夹
        const physicsFolder = gui.addFolder(i18n.physics.folder);

        // 算法管理
        const algoFolder = physicsFolder.addFolder(i18n.physics.algorithms.folder);
        algoFolder.add({ 'Buoyancy': i18n.physics.algorithms.buoyancy }, 'Buoyancy').name('浮力 | Buoyancy');
        algoFolder.add({ 'Stabilizer': i18n.physics.algorithms.stabilizer }, 'Stabilizer').name('自稳 | Stabilizer');
        algoFolder.add({ 'Wind': i18n.physics.algorithms.wind }, 'Wind').name('风力 | Wind');
        algoFolder.add({ 'Rain': i18n.physics.algorithms.rain }, 'Rain').name('降雨 | Rain');

        const buoyancyAlg = simulatorEngine.getAlgorithm('Buoyancy');
        if (buoyancyAlg) {
          algoFolder.add(buoyancyAlg, 'enabled').name('浮力 | Buoyancy');
        }
        const stabilizerAlg = simulatorEngine.getAlgorithm('Stabilizer');
        if (stabilizerAlg) {
          algoFolder.add(stabilizerAlg, 'enableStabilizer').name('自稳 | Stabilizer');
        }
        const windAlg = simulatorEngine.getAlgorithm('Wind');
        if (windAlg) {
          algoFolder.add(windAlg, 'enabled').name('风力 | Wind');
        }
        const rainAlg = simulatorEngine.getAlgorithm('Rain');
        if (rainAlg) {
          algoFolder.add(rainAlg, 'enabled').name('降雨 | Rain');
        }

        // 航行文件夹
        const navigationFolder = gui.addFolder(i18n.navigation.folder);

        // 浮力与稳定性（放在航行下）
        const buoyancyFolder = navigationFolder.addFolder(i18n.buoyancy.folder);

        if (buoyancyAlg) {
          // 确保算法对象的值与config同步
          buoyancyAlg.buoyancyCoeff = config.buoyancy.buoyancyCoeff;

          // 创建一个代理对象，确保GUI控制器能正确更新算法
          const buoyancyProxy = {
            get buoyancyCoeff() {
              return config.buoyancy.buoyancyCoeff;
            },
            set buoyancyCoeff(value) {
              const numValue = Number(value);
              if (isNaN(numValue)) {
                console.warn('⚠️ 无效的浮力系数值 | Invalid buoyancy coefficient value:', value);
                return;
              }

              // 更新config和算法
              config.buoyancy.buoyancyCoeff = numValue;
              buoyancyAlg.buoyancyCoeff = numValue;

              // 强制唤醒物理体，使浮力变化立即生效
              if (shipController && shipController.body) {
                shipController.body.wakeUp();
                shipController.body.velocity.y = 0;
              }

              console.log(`🔧 浮力系数已更新 | Buoyancy coefficient updated: ${numValue.toLocaleString()}`);
            }
          };

          // 创建浮力系数控制器（减小步长，提高拖拉和箭头控制的流畅度）
          const buoyancyCtrl = buoyancyFolder.add(buoyancyProxy, 'buoyancyCoeff', 1000000, 15000000, 10000);
          buoyancyCtrl.name(i18n.buoyancy.buoyancyCoeff);
          buoyancyCtrl.onChange((value) => {
            // onChange回调也会触发，但我们已经通过setter处理了
            // 这里可以添加额外的逻辑，比如重新放置船体
            if (shipController && shipController.body && clock && clock.elapsedTime !== undefined) {
              // 不立即重新放置，让浮力自然调整船体位置
              // shipController.placeOnWater(clock.elapsedTime);
            }
          });
          // 确保控制器添加到数组，以便支持上下箭头
          numericCtrls.push(buoyancyCtrl);
          numericCtrls.push(buoyancyFolder.add(config.buoyancy, 'dragCoeff', 0, 20, 0.1).name(i18n.buoyancy.dragCoeff)
            .onChange((value) => {
              buoyancyAlg.dragCoeff = value;
              config.buoyancy.dragCoeff = value;
            }));
        }

        if (stabilizerAlg) {
          buoyancyFolder.add(config.stabilizer, 'enableStabilizer').name(i18n.buoyancy.enableStabilizer)
            .onChange((value) => {
              const alg = simulatorEngine.getAlgorithm('Stabilizer');
              if (alg) alg.enableStabilizer = value;
            });

          buoyancyFolder.add(config.stabilizer, 'uprightStiffness', 0, 15, 0.1).name(i18n.buoyancy.uprightStiffness)
            .onChange((value) => {
              const alg = simulatorEngine.getAlgorithm('Stabilizer');
              if (alg) alg.setStiffness(value);
            });

          buoyancyFolder.add(config.stabilizer, 'uprightDamping', 0, 10, 0.1).name(i18n.buoyancy.uprightDamping)
            .onChange((value) => {
              const alg = simulatorEngine.getAlgorithm('Stabilizer');
              if (alg) alg.setDamping(value);
            });

          buoyancyFolder.add(config.stabilizer, 'wobbleBoost', 0.2, 5.0, 0.1).name(i18n.buoyancy.wobbleBoost)
            .onChange((value) => {
              const alg = simulatorEngine.getAlgorithm('Stabilizer');
              if (alg) alg.setWobbleBoost(value);
            });
        }

        buoyancyFolder.add({
          reset: () => {
            if (shipController) {
              shipController.reset();
              shipController.placeOnWater(clock.elapsedTime);
            }
          }
        }, 'reset').name(i18n.buoyancy.reset);

        buoyancyFolder.add({ stabilize: stabilizeShip }, 'stabilize').name('⚖️ 船身稳定 | Stabilize Ship');

        // 自动稳定系统控制
        if (autoStabilizationSystem) {
          const autoStabFolder = navigationFolder.addFolder('自动稳定系统 | Auto Stabilization');
          autoStabFolder.add(autoStabilizationSystem, 'enabled').name('启用自动稳定 | Enable Auto Stabilization');
          autoStabFolder.add({
            viewLog: () => {
              const log = autoStabilizationSystem.getRecentLog(5);
              console.log('📋 最近稳定记录 | Recent stabilization log:', log);
            }
          }, 'viewLog').name('查看稳定记录 | View Log');
          autoStabFolder.add({
            clearLog: () => {
              autoStabilizationSystem.clearLog();
              console.log('🗑️ 稳定记录已清除 | Stabilization log cleared');
            }
          }, 'clearLog').name('清除记录 | Clear Log');
        }

        // 显示选项
        const displayFolder = gui.addFolder(i18n.display.folder);
        displayFolder.add({ focus: focusBoat }, 'focus').name(i18n.display.focusBoat);
        displayFolder.add(config.display, 'showAxesHelper').name(i18n.display.showAxesHelper)
          .onChange((value) => {
            if (shipController) {
              shipController.toggleAxesHelper(value);
            }
          });
        displayFolder.add(config.display, 'showDimensionLines').name(i18n.display.showDimensionLines)
          .onChange((value) => {
            if (shipController) {
              shipController.toggleDimensionLines(value);
            }
          });

        // 船体材质透明度控制
        const shipMaterialOpacity = { opacity: 0.6 }; // 默认60%不透明度
        displayFolder.add(shipMaterialOpacity, 'opacity', 0.1, 1.0, 0.01)
          .name('船体透明度 | Ship Opacity')
          .onChange((value) => {
            if (shipController && shipController.updateShipMaterialOpacity) {
              shipController.updateShipMaterialOpacity(value);
              console.log(`🔵 船体材质透明度已更新 | Ship material opacity updated: ${(value * 100).toFixed(1)}%`);
            } else {
              console.warn('⚠️ shipController 未就绪，无法更新船体材质透明度');
            }
          });

        // 灯光控制文件夹
        const lightingFolder = gui.addFolder('灯光系统 | Lighting System');

        // 半球光控制
        if (hemiLight) {
          const hemiFolder = lightingFolder.addFolder('半球光 | Hemisphere Light');
          hemiFolder.add(hemiLight, 'intensity', 0, 3, 0.1).name('强度 | Intensity');
          hemiFolder.addColor({ color: hemiLight.color.getHex() }, 'color').name('天空颜色 | Sky Color')
            .onChange((value) => {
              hemiLight.color.setHex(value);
            });
          hemiFolder.addColor({ color: hemiLight.groundColor.getHex() }, 'color').name('地面颜色 | Ground Color')
            .onChange((value) => {
              hemiLight.groundColor.setHex(value);
            });
          hemiFolder.add(hemiLight, 'visible').name('可见 | Visible');
        }

        // 主方向光控制
        if (dirLight) {
          const dirFolder = lightingFolder.addFolder('主方向光 | Main Directional Light');
          dirFolder.add(dirLight, 'intensity', 0, 5, 0.1).name('强度 | Intensity');
          dirFolder.addColor({ color: dirLight.color.getHex() }, 'color').name('颜色 | Color')
            .onChange((value) => {
              dirLight.color.setHex(value);
            });
          dirFolder.add(dirLight.position, 'x', -500, 500, 1).name('位置 X | Position X');
          dirFolder.add(dirLight.position, 'y', -500, 500, 1).name('位置 Y | Position Y');
          dirFolder.add(dirLight.position, 'z', -500, 500, 1).name('位置 Z | Position Z');
          dirFolder.add(dirLight, 'castShadow').name('投射阴影 | Cast Shadow');
          dirFolder.add(dirLight.shadow.camera, 'left', -500, 0, 10).name('阴影左边界 | Shadow Left');
          dirFolder.add(dirLight.shadow.camera, 'right', 0, 500, 10).name('阴影右边界 | Shadow Right');
          dirFolder.add(dirLight.shadow.camera, 'top', 0, 500, 10).name('阴影上边界 | Shadow Top');
          dirFolder.add(dirLight.shadow.camera, 'bottom', -500, 0, 10).name('阴影下边界 | Shadow Bottom');
          dirFolder.add(dirLight.shadow.camera, 'near', 0.1, 100, 0.1).name('阴影近平面 | Shadow Near');
          dirFolder.add(dirLight.shadow.camera, 'far', 100, 1000, 10).name('阴影远平面 | Shadow Far');
          dirFolder.add(dirLight, 'visible').name('可见 | Visible');
        }

        // 补充方向光控制
        const dirLight2 = scene.children.find(child => child instanceof THREE.DirectionalLight && child !== dirLight);
        if (dirLight2) {
          const dir2Folder = lightingFolder.addFolder('补充方向光 | Secondary Directional Light');
          dir2Folder.add(dirLight2, 'intensity', 0, 3, 0.1).name('强度 | Intensity');
          dir2Folder.addColor({ color: dirLight2.color.getHex() }, 'color').name('颜色 | Color')
            .onChange((value) => {
              dirLight2.color.setHex(value);
            });
          dir2Folder.add(dirLight2.position, 'x', -500, 500, 1).name('位置 X | Position X');
          dir2Folder.add(dirLight2.position, 'y', -500, 500, 1).name('位置 Y | Position Y');
          dir2Folder.add(dirLight2.position, 'z', -500, 500, 1).name('位置 Z | Position Z');
          dir2Folder.add(dirLight2, 'visible').name('可见 | Visible');
        }

        // 点光源控制
        const pointLight = scene.children.find(child => child instanceof THREE.PointLight);
        if (pointLight) {
          const pointFolder = lightingFolder.addFolder('点光源 | Point Light');
          pointFolder.add(pointLight, 'intensity', 0, 3, 0.1).name('强度 | Intensity');
          pointFolder.addColor({ color: pointLight.color.getHex() }, 'color').name('颜色 | Color')
            .onChange((value) => {
              pointLight.color.setHex(value);
            });
          pointFolder.add(pointLight.position, 'x', -500, 500, 1).name('位置 X | Position X');
          pointFolder.add(pointLight.position, 'y', -500, 500, 1).name('位置 Y | Position Y');
          pointFolder.add(pointLight.position, 'z', -500, 500, 1).name('位置 Z | Position Z');
          pointFolder.add(pointLight, 'distance', 0, 1000, 10).name('距离 | Distance');
          pointFolder.add(pointLight, 'decay', 0, 2, 0.1).name('衰减 | Decay');
          pointFolder.add(pointLight, 'visible').name('可见 | Visible');
        }

        // 天气对灯光的影响（自动调整）
        lightingFolder.add({ autoAdjust: true }, 'autoAdjust').name('根据天气自动调整 | Auto Adjust by Weather')
          .onChange((value) => {
            if (value) {
              console.log('✅ 灯光将根据天气自动调整 | Lighting will auto-adjust based on weather');
            } else {
              console.log('⚠️ 灯光自动调整已禁用 | Lighting auto-adjust disabled');
            }
          });

        // 场景控制文件夹（合并巡检和消防演练）
        const scenarioFolder = gui.addFolder(i18n.scenario?.folder || '场景控制 | Scenario Control');

        // 巡检场景控制
        if (inspectionScenario) {
          const inspectionFolder = scenarioFolder.addFolder('船舱巡检 | Cabin Inspection');
          inspectionFolder.add({
            startInspection: () => {
              inspectionScenario.start();
            }
          }, 'startInspection').name('🚢 开始巡检 | Start Inspection');
          inspectionFolder.add({
            stopInspection: () => {
              inspectionScenario.stop();
            }
          }, 'stopInspection').name('⏹️ 停止巡检 | Stop Inspection');
          inspectionFolder.add({
            viewReport: () => {
              const report = inspectionScenario.getReport();
              console.log('📊 巡检报告 | Inspection Report:', report);
            }
          }, 'viewReport').name('查看巡检报告 | View Report');
        }

        // 消防演练场景控制
        if (fireDrillScenario) {
          const fireDrillFolder = scenarioFolder.addFolder('消防演练 | Fire Drill');
          fireDrillFolder.add({
            startFireDrill: () => {
              fireDrillScenario.start();
            }
          }, 'startFireDrill').name('🔥 开始消防演练 | Start Fire Drill');
          fireDrillFolder.add({
            stopFireDrill: () => {
              fireDrillScenario.stop();
            }
          }, 'stopFireDrill').name('⏹️ 停止演练 | Stop Drill');
          fireDrillFolder.add({
            viewStatus: () => {
              const status = fireDrillScenario.getStatus();
              console.log('📊 演练状态 | Drill Status:', status);
            }
          }, 'viewStatus').name('查看演练状态 | View Status');
        }

        // 巡检功能（保留原有功能，如果存在）
        if (typeof startInspection === 'function' && typeof endInspection === 'function') {
          const oldInspectionFolder = scenarioFolder.addFolder(i18n.inspection?.folder || '原有巡检 | Legacy Inspection');
          oldInspectionFolder.add({ start: startInspection }, 'start').name(i18n.inspection?.startInspection || '开始 | Start');
          oldInspectionFolder.add({ end: endInspection }, 'end').name(i18n.inspection?.endInspection || '结束 | End');
        }

        // 给所有数字输入加"上下箭头"支持
        numericCtrls.forEach((ctrl) => {
          if (ctrl && ctrl.domElement) {
            const input = ctrl.domElement.querySelector('input[type="text"], input[type="number"]');
            if (input) {
              input.type = 'number';
              // 确保输入框可以正常输入和修改
              input.addEventListener('input', (e) => {
                // 允许用户直接输入数值，lil-gui会自动处理
                const value = parseFloat(e.target.value);
                if (!isNaN(value) && ctrl && typeof ctrl.updateDisplay === 'function') {
                  ctrl.updateDisplay();
                }
              });
              // 确保上下箭头可以工作（鼠标滚轮）
              input.addEventListener('wheel', (e) => {
                if (e.deltaY !== 0 && ctrl) {
                  e.preventDefault();
                  const currentValue = parseFloat(input.value) || 0;
                  const step = ctrl.step || (ctrl.max - ctrl.min) / 100;
                  const newValue = e.deltaY > 0
                    ? Math.max(ctrl.min, currentValue - step)
                    : Math.min(ctrl.max, currentValue + step);
                  if (typeof ctrl.setValue === 'function') {
                    ctrl.setValue(newValue);
                  }
                }
              }, { passive: false });
            }
          }
        });

        // 相机视图控制文件夹
        const cameraFolder = gui.addFolder('📷 相机视图 | Camera Views');

        // 整体视图 - 能够看到整个船体的视角
        cameraFolder.add({
          viewOverall: () => {
            if (!shipController || !shipController.size) {
              console.warn('⚠️ 船体未加载，无法切换到整体视图 | Ship not loaded, cannot switch to overall view');
              return;
            }

            const shipSize = shipController.size;
            const shipLength = shipSize.z; // Z轴=长度
            const shipWidth = shipSize.x;  // X轴=宽度
            const shipHeight = shipSize.y;  // Y轴=高度

            // 计算相机距离：确保能看到整个船体
            // 考虑相机的FOV（视野角度）来计算合适的距离
            // 使用船体的对角线长度作为参考
            const diagonal = Math.sqrt(shipLength * shipLength + shipWidth * shipWidth + shipHeight * shipHeight);
            const fov = camera.fov * (Math.PI / 180); // 转换为弧度
            // 计算距离：确保船体的对角线能够完全显示在视野内
            // tan(fov/2) = (diagonal/2) / distance
            // distance = (diagonal/2) / tan(fov/2)
            const distance = (diagonal * 0.6) / Math.tan(fov / 2); // 使用0.6倍对角线，留出一些边距

            // 设置相机位置：从斜上方45度角观察，能看到船体的正面和侧面
            // 使用球坐标系：从船体中心点出发
            const angle = Math.PI / 4; // 45度角
            const height = shipHeight * 0.5 + distance * 0.25; // 相机高度：船体中心高度 + 距离的25%

            camera.position.set(
              distance * Math.cos(angle),  // X: 从右侧观察
              height,                      // Y: 从上方观察
              distance * Math.sin(angle)   // Z: 从前方观察
            );

            // 设置相机目标：船体中心（船体底部在Y=0，中心在Y=shipHeight/2）
            controls.target.set(0, shipHeight * 0.3, 0); // 稍微偏下，能看到船体底部
            controls.update();

            console.log('📷 已切换到整体视图 | Switched to overall view');
            console.log(`   相机位置 | Camera position: (${camera.position.x.toFixed(1)}, ${camera.position.y.toFixed(1)}, ${camera.position.z.toFixed(1)})`);
            console.log(`   相机目标 | Camera target: (${controls.target.x.toFixed(1)}, ${controls.target.y.toFixed(1)}, ${controls.target.z.toFixed(1)})`);
            console.log(`   船体尺寸 | Ship size: ${shipWidth.toFixed(1)}m × ${shipHeight.toFixed(1)}m × ${shipLength.toFixed(1)}m`);
          }
        }, 'viewOverall').name('🌐 整体视图 | Overall View');

        // 俯视图 - 从正上方看
        cameraFolder.add({
          viewTop: () => {
            if (!shipController || !shipController.size) {
              console.warn('⚠️ 船体未加载，无法切换到俯视图 | Ship not loaded, cannot switch to top view');
              return;
            }

            const shipSize = shipController.size;
            const shipLength = shipSize.z;
            const shipWidth = shipSize.x;
            const maxDimension = Math.max(shipLength, shipWidth);
            const distance = maxDimension * 1.2; // 从上方看，距离可以近一些

            camera.position.set(0, distance, 0); // 正上方
            controls.target.set(0, shipSize.y * 0.3, 0); // 目标在船体中心偏下
            controls.update();

            console.log('📷 已切换到俯视图 | Switched to top view');
          }
        }, 'viewTop').name('⬇️ 俯视图 | Top View');

        // 侧视图 - 从侧面看
        cameraFolder.add({
          viewSide: () => {
            if (!shipController || !shipController.size) {
              console.warn('⚠️ 船体未加载，无法切换到侧视图 | Ship not loaded, cannot switch to side view');
              return;
            }

            const shipSize = shipController.size;
            const shipLength = shipSize.z;
            const shipHeight = shipSize.y;
            const maxDimension = Math.max(shipLength, shipHeight);
            const distance = maxDimension * 1.5;

            camera.position.set(distance, shipHeight * 0.5, 0); // 从右侧看
            controls.target.set(0, shipHeight * 0.3, 0);
            controls.update();

            console.log('📷 已切换到侧视图 | Switched to side view');
          }
        }, 'viewSide').name('👁️ 侧视图 | Side View');

        // 前视图 - 从船头看
        cameraFolder.add({
          viewFront: () => {
            if (!shipController || !shipController.size) {
              console.warn('⚠️ 船体未加载，无法切换到前视图 | Ship not loaded, cannot switch to front view');
              return;
            }

            const shipSize = shipController.size;
            const shipWidth = shipSize.x;
            const shipHeight = shipSize.y;
            const maxDimension = Math.max(shipWidth, shipHeight);
            const distance = maxDimension * 1.5;

            camera.position.set(0, shipHeight * 0.5, -distance); // 从船头前方看（负Z方向）
            controls.target.set(0, shipHeight * 0.3, 0);
            controls.update();

            console.log('📷 已切换到前视图 | Switched to front view');
          }
        }, 'viewFront').name('🚢 前视图 | Front View');

        // 重置到默认视图
        cameraFolder.add({
          resetView: () => {
            camera.position.set(15, 9, 22);
            controls.target.set(0, 1.5, 0);
            controls.update();
            console.log('📷 已重置到默认视图 | Reset to default view');
          }
        }, 'resetView').name('🔄 重置视图 | Reset View');

        // 默认折叠一些文件夹
        waveFolder.close();
        algoFolder.close();
        cameraFolder.close(); // 默认折叠相机视图文件夹
      }

      // ============= 稳定化船体 =============
      function stabilizeShip() {
        if (!shipController || !shipController.body || !stabilityAnalyzer) {
          console.warn('⚠️ 船体或分析器未就绪 | Ship or analyzer not ready');
          return;
        }

        if (!simulatorEngine) {
          console.warn('⚠️ 模拟器引擎未就绪 | Simulator engine not ready');
          return;
        }

        console.log('⚖️ 开始稳定化船体 | Starting ship stabilization...');

        // 获取当前浮力算法状态（用于对比）
        const buoyancyAlg = simulatorEngine.getAlgorithm('Buoyancy');
        const oldBuoyancyCoeff = buoyancyAlg ? buoyancyAlg.buoyancyCoeff : 0;
        const oldDragCoeff = buoyancyAlg ? buoyancyAlg.dragCoeff : 0;

        console.log(`💧 稳定化前浮力参数 | Before: 浮力系数=${oldBuoyancyCoeff.toFixed(0)}, 阻尼系数=${oldDragCoeff.toFixed(1)}`);

        // 执行稳定化（这会分析状态并调整浮力等参数）
        const result = stabilityAnalyzer.stabilize(
          shipController.body,
          clock.elapsedTime,
          config,
          simulatorEngine,
          shipController
        );

        // 保存结果
        result.timestamp = Date.now();
        lastStabilizationResult = result;

        // 检查浮力是否被调整
        if (buoyancyAlg) {
          const newBuoyancyCoeff = buoyancyAlg.buoyancyCoeff;
          const newDragCoeff = buoyancyAlg.dragCoeff;

          console.log(`💧 稳定化后浮力参数 | After: 浮力系数=${newBuoyancyCoeff.toFixed(0)}, 阻尼系数=${newDragCoeff.toFixed(1)}`);

          if (newBuoyancyCoeff !== oldBuoyancyCoeff) {
            console.log(`✅ 浮力系数已调整 | Buoyancy adjusted: ${oldBuoyancyCoeff.toFixed(0)} → ${newBuoyancyCoeff.toFixed(0)}`);
          }
          if (newDragCoeff !== oldDragCoeff) {
            console.log(`✅ 阻尼系数已调整 | Drag adjusted: ${oldDragCoeff.toFixed(1)} → ${newDragCoeff.toFixed(1)}`);
          }
          if (newBuoyancyCoeff === oldBuoyancyCoeff && newDragCoeff === oldDragCoeff) {
            console.log(`⚠️ 浮力参数未变化，可能需要手动调整 | Buoyancy params unchanged`);
          }
        }

        // 确保物理体继续更新（唤醒物理体）
        if (shipController && shipController.body) {
          shipController.body.wakeUp();
          // 同步网格位置
          if (shipController.mesh) {
            shipController.mesh.position.copy(shipController.body.position);
            shipController.mesh.quaternion.copy(shipController.body.quaternion);
          }
        }

        // 立即更新一次状态菜单，确保数据同步
        setTimeout(() => {
          updateStatus();
        }, 0);

        // 显示结果
        const statusEl = document.getElementById('status');
        if (statusEl) {
          let statusHTML = '<strong>⚖️ 稳定化结果 | Stabilization Result</strong><br>';

          if (result.stable) {
            statusHTML += '<span style="color: #81c784;">✅ 船体已稳定 | Ship stabilized</span><br>';
          } else {
            statusHTML += '<span style="color: #f44336;">❌ 发现问题 | Issues found:</span><br>';
            result.issues.forEach(issue => {
              statusHTML += `  • ${issue}<br>`;
            });
          }

          if (result.warnings.length > 0) {
            statusHTML += '<span style="color: #ffa726;">⚠️ 警告 | Warnings:</span><br>';
            result.warnings.forEach(warning => {
              statusHTML += `  • ${warning}<br>`;
            });
          }

          if (result.suggestions.length > 0) {
            statusHTML += '<br><strong>💡 已应用调整 | Applied Adjustments:</strong><br>';
            result.applied.forEach(adjustment => {
              statusHTML += `  ✅ ${adjustment}<br>`;
            });

            statusHTML += '<br><strong>📋 建议 | Suggestions:</strong><br>';
            result.suggestions.forEach(suggestion => {
              statusHTML += `  • ${suggestion.param}: ${suggestion.current} → ${suggestion.suggested}<br>`;
              statusHTML += `    ${suggestion.reason}<br>`;
            });
          }

          statusHTML += '<br><strong>📊 当前指标 | Current Metrics:</strong><br>';
          statusHTML += `  倾斜角度 | Tilt: ${result.metrics.tilt?.toFixed(2) || 'N/A'}°<br>`;
          statusHTML += `  下沉深度 | Sink: ${result.metrics.sink?.toFixed(2) || 'N/A'} m<br>`;
          statusHTML += `  角速度 | Angular Speed: ${result.metrics.angularSpeed?.toFixed(2) || 'N/A'} rad/s<br>`;

          statusEl.innerHTML = statusHTML;
        }

        // 控制台输出
        console.log('📊 稳定化完成 | Stabilization complete:');
        console.log(`  状态 | Status: ${result.stable ? '✅ 稳定' : '❌ 不稳定'}`);
        console.log(`  倾斜角度 | Tilt: ${result.metrics.tilt?.toFixed(2)}°`);
        console.log(`  下沉深度 | Sink: ${result.metrics.sink?.toFixed(2)} m`);

        if (result.applied.length > 0) {
          console.log('✅ 已应用调整 | Applied adjustments:');
          result.applied.forEach(adj => console.log(`  - ${adj}`));
        }

        if (result.suggestions.length > 0) {
          console.log('💡 建议 | Suggestions:');
          result.suggestions.forEach(sug => {
            console.log(`  - ${sug.param}: ${sug.current} → ${sug.suggested}`);
            console.log(`    ${sug.reason}`);
          });
        }
      }

      // ============= 聚焦船体 =============
      function focusBoat() {
        if (!shipController || !shipController.mesh) return;

        // 显示坐标轴（高亮延长到模型外）
        if (shipController.toggleAxesHelper) {
          shipController.toggleAxesHelper(true);
          config.display.showAxesHelper = true;
        }

        // 显示尺寸线段（长宽高）
        if (shipController.toggleDimensionLines) {
          shipController.toggleDimensionLines(true);
          config.display.showDimensionLines = true;
        }

        // 重置船体姿态和位置
        shipController.reset();
        shipController.placeOnWater(clock.elapsedTime);

        // 调整相机位置
        const pos = shipController.mesh.position.clone();
        camera.position.set(pos.x + 50, pos.y + 30, pos.z + 50);
        controls.target.copy(pos);
        controls.update();
      }

      // ============= 开始巡检 =============
      function startInspection() {
        if (!shipController || !shipController.mesh) {
          console.warn('⚠️ 船体未加载 | Ship not loaded');
          return;
        }

        isInspecting = true;

        // 保存原始相机状态
        originalCameraState = {
          position: camera.position.clone(),
          target: controls.target.clone(),
          fov: camera.fov
        };

        // 禁用轨道控制器
        controls.enabled = false;

        // 设置第一人称视角（进入船体内部）
        const shipPos = shipController.mesh.position.clone();
        camera.position.set(shipPos.x, shipPos.y + 10, shipPos.z);
        camera.lookAt(shipPos.x, shipPos.y + 10, shipPos.z + 10);

        // 重置第一人称控制状态
        firstPersonControls.euler.setFromQuaternion(camera.quaternion);
        firstPersonControls.keys.forward = false;
        firstPersonControls.keys.backward = false;
        firstPersonControls.keys.left = false;
        firstPersonControls.keys.right = false;
        firstPersonControls.mouse.isDown = false;

        // 隐藏船体（可选，根据需要）
        // shipController.mesh.visible = false;

        // 添加键盘和鼠标事件监听
        document.addEventListener('keydown', onInspectionKeyDown);
        document.addEventListener('keyup', onInspectionKeyUp);
        document.addEventListener('mousedown', onInspectionMouseDown);
        document.addEventListener('mouseup', onInspectionMouseUp);
        document.addEventListener('mousemove', onInspectionMouseMove);

        console.log('🔍 开始巡检 | Inspection started');
      }

      // ============= 结束巡检 =============
      function endInspection() {
        if (!isInspecting) return;

        isInspecting = false;

        // 恢复原始相机状态
        if (originalCameraState) {
          camera.position.copy(originalCameraState.position);
          controls.target.copy(originalCameraState.target);
          camera.fov = originalCameraState.fov;
          camera.updateProjectionMatrix();
        }

        // 启用轨道控制器
        controls.enabled = true;

        // 显示船体（如果之前隐藏了）
        // if (shipController && shipController.mesh) {
        //   shipController.mesh.visible = true;
        // }

        // 移除事件监听
        document.removeEventListener('keydown', onInspectionKeyDown);
        document.removeEventListener('keyup', onInspectionKeyUp);
        document.removeEventListener('mousedown', onInspectionMouseDown);
        document.removeEventListener('mouseup', onInspectionMouseUp);
        document.removeEventListener('mousemove', onInspectionMouseMove);

        console.log('🔍 结束巡检 | Inspection ended');
      }

      // ============= 巡检键盘事件 =============
      function onInspectionKeyDown(event) {
        if (!isInspecting) return;

        switch (event.code) {
          case 'KeyW':
            firstPersonControls.keys.forward = true;
            break;
          case 'KeyS':
            firstPersonControls.keys.backward = true;
            break;
          case 'KeyA':
            firstPersonControls.keys.left = true;
            break;
          case 'KeyD':
            firstPersonControls.keys.right = true;
            break;
        }
      }

      function onInspectionKeyUp(event) {
        if (!isInspecting) return;

        switch (event.code) {
          case 'KeyW':
            firstPersonControls.keys.forward = false;
            break;
          case 'KeyS':
            firstPersonControls.keys.backward = false;
            break;
          case 'KeyA':
            firstPersonControls.keys.left = false;
            break;
          case 'KeyD':
            firstPersonControls.keys.right = false;
            break;
        }
      }

      // ============= 巡检鼠标事件 =============
      function onInspectionMouseDown(event) {
        if (!isInspecting) return;
        if (event.button !== 0) return; // 只处理左键

        firstPersonControls.mouse.isDown = true;
        firstPersonControls.mouse.x = event.clientX;
        firstPersonControls.mouse.y = event.clientY;
      }

      function onInspectionMouseUp(event) {
        if (!isInspecting) return;
        firstPersonControls.mouse.isDown = false;
      }

      function onInspectionMouseMove(event) {
        if (!isInspecting || !firstPersonControls.mouse.isDown) return;

        const deltaX = event.clientX - firstPersonControls.mouse.x;
        const deltaY = event.clientY - firstPersonControls.mouse.y;

        firstPersonControls.euler.y -= deltaX * firstPersonControls.lookSpeed;
        firstPersonControls.euler.x -= deltaY * firstPersonControls.lookSpeed;
        firstPersonControls.euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, firstPersonControls.euler.x));

        camera.quaternion.setFromEuler(firstPersonControls.euler);

        firstPersonControls.mouse.x = event.clientX;
        firstPersonControls.mouse.y = event.clientY;
      }

      // ============= 更新巡检移动 =============
      function updateInspectionMovement(deltaTime) {
        if (!isInspecting) return;

        const moveSpeed = firstPersonControls.moveSpeed * deltaTime;
        const direction = new THREE.Vector3();

        if (firstPersonControls.keys.forward) {
          direction.z -= 1;
        }
        if (firstPersonControls.keys.backward) {
          direction.z += 1;
        }
        if (firstPersonControls.keys.left) {
          direction.x -= 1;
        }
        if (firstPersonControls.keys.right) {
          direction.x += 1;
        }

        direction.normalize();
        direction.multiplyScalar(moveSpeed);
        direction.applyQuaternion(camera.quaternion);

        camera.position.add(direction);
      }

      // ============= 窗口大小调整 =============
      function onResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }

      // ============= 根据天气调整灯光 =============
      function _updateLightingForWeather() {
        if (!weatherSystem || !dirLight || !hemiLight) return;

        try {
          const weather = weatherSystem.getWeatherState();
          if (!weather || typeof weather !== 'object') return;

          const rainIntensity = (weather.rainIntensity !== undefined && weather.rainIntensity !== null) ? weather.rainIntensity : 0;
          const snowIntensity = (weather.snowIntensity !== undefined && weather.snowIntensity !== null) ? weather.snowIntensity : 0;
          const totalPrecipitation = rainIntensity + snowIntensity;

          // 根据降水强度调整光照（为了看到降雨和降雪，不完全降低光照）
          // 轻微降低光照，但保持足够的亮度以看到粒子效果
          const precipitationFactor = Math.max(0.6, 1.0 - totalPrecipitation / 400); // 最大降低40%，保持60%亮度

          // 平滑过渡光照强度（安全检查）
          if (dirLight && typeof dirLight.intensity === 'number') {
            const originalIntensity = (dirLight.userData && dirLight.userData.originalIntensity !== undefined)
              ? dirLight.userData.originalIntensity
              : (dirLight.intensity || 4.0);
            const targetIntensity = originalIntensity * precipitationFactor;
            dirLight.intensity = dirLight.intensity * 0.95 + targetIntensity * 0.05;
          }

          // 增强半球光强度，提高整体场景亮度，使粒子更可见（安全检查）
          if (hemiLight && typeof hemiLight.intensity === 'number') {
            if (totalPrecipitation > 0) {
              hemiLight.intensity = Math.max(1.5, 1.2 + totalPrecipitation / 200); // 降雨/降雪时增强半球光
            } else {
              hemiLight.intensity = 3.0; // 晴天时恢复（使用setupLights中的初始值）
            }
          }

          // 调整光照颜色（降雨时偏冷，降雪时更冷，但保持较亮）（安全检查）
          if (dirLight && dirLight.color && typeof dirLight.color.lerp === 'function') {
            if (rainIntensity > 0) {
              // 降雨：偏蓝灰色，但保持较亮
              dirLight.color.lerp(new THREE.Color(0xddddff), 0.05);
            } else if (snowIntensity > 0) {
              // 降雪：更冷的蓝白色，但保持较亮
              dirLight.color.lerp(new THREE.Color(0xeeeeff), 0.05);
            } else {
              // 晴天：恢复原始颜色
              dirLight.color.lerp(new THREE.Color(0xffffff), 0.05);
            }
          }

          if (hemiLight && hemiLight.color && typeof hemiLight.color.lerp === 'function') {
            if (rainIntensity > 0) {
              hemiLight.color.lerp(new THREE.Color(0xaabbcc), 0.05);
            } else if (snowIntensity > 0) {
              hemiLight.color.lerp(new THREE.Color(0xbbccdd), 0.05);
            } else {
              hemiLight.color.lerp(new THREE.Color(0xaadfff), 0.05);
            }
          }
        } catch (err) {
          // 静默处理错误
        }
      }

      // ============= 更新状态显示 =============
      // 完全重写 updateStatus 函数，确保数据实时同步
      function updateStatus() {
        // 获取所有DOM元素（在函数开头获取，避免重复查找）
        const shipPositionEl = document.getElementById('shipPosition');
        const shipMassEl = document.getElementById('shipMass');
        const waterHeightEl = document.getElementById('waterHeight');
        const waterOffsetEl = document.getElementById('waterOffset');
        const shipStabilityEl = document.getElementById('shipStability');
        const windSpeedEl = document.getElementById('windSpeed');
        const windDirectionEl = document.getElementById('windDirection');
        const rainIntensityEl = document.getElementById('rainIntensity');
        const visibilityEl = document.getElementById('visibility');
        const seaStateEl = document.getElementById('seaState');

        // 如果船体未加载，显示默认值
        if (!shipController || !shipController.body) {
          if (shipPositionEl) shipPositionEl.textContent = '等待加载...';
          if (shipMassEl) shipMassEl.textContent = config.boatMass ? `${config.boatMass.toFixed(0)} kg` : '-';
          if (waterHeightEl) waterHeightEl.textContent = '-';
          if (waterOffsetEl) waterOffsetEl.textContent = '-';
          if (shipStabilityEl) shipStabilityEl.textContent = '等待加载...';
          return;
        }

        try {
          // 直接获取物理体的实时位置（这是最准确的数据源）
          const body = shipController.body;
          const pos = body.position;

          // 获取当前时间
          const currentTime = clock ? clock.elapsedTime : 0;

          // 计算水面高度（使用实时时间）
          let waterH = 0;
          if (clock && typeof getWaveHeight === 'function') {
            try {
              waterH = getWaveHeight(pos.x, -pos.z, currentTime) * config.yFlip;
              if (!isFinite(waterH)) waterH = 0;
            } catch (err) {
              waterH = 0;
            }
          }

          // 计算离水面距离
          const deltaY = pos.y - waterH;

          // ========== 更新船体状态数值（强制更新，不依赖任何条件） ==========

          // 更新位置（直接从物理体获取，每帧更新）
          if (shipPositionEl) {
            const x = isFinite(pos.x) ? pos.x : 0;
            const y = isFinite(pos.y) ? pos.y : 0;
            const z = isFinite(pos.z) ? pos.z : 0;
            shipPositionEl.textContent = `(${x.toFixed(1)}, ${y.toFixed(1)}, ${z.toFixed(1)})`;
          }

          // 更新质量
          if (shipMassEl) {
            shipMassEl.textContent = `${config.boatMass.toFixed(0)} kg`;
          }

          // 更新水面高度（实时计算）
          if (waterHeightEl) {
            waterHeightEl.textContent = `${waterH.toFixed(2)} m`;
          }

          // 更新离水面距离（实时计算）
          if (waterOffsetEl) {
            const offset = isFinite(deltaY) ? deltaY : 0;
            waterOffsetEl.textContent = `${offset.toFixed(2)} m`;
          }

          // ========== 更新稳定性状态 ==========
          if (shipStabilityEl) {
            let stabilityStatus = '-';
            let stabilityDetails = '';

            // 实时分析船体稳定性
            if (stabilityAnalyzer && clock) {
              try {
                const quickAnalysis = stabilityAnalyzer.analyze(body, currentTime, config);

                if (quickAnalysis && quickAnalysis.stable) {
                  stabilityStatus = '✅ 稳定 | Stable';
                } else if (quickAnalysis && quickAnalysis.issues && quickAnalysis.issues.length > 0) {
                  stabilityStatus = `❌ ${quickAnalysis.issues[0]}`;
                } else if (quickAnalysis && quickAnalysis.warnings && quickAnalysis.warnings.length > 0) {
                  stabilityStatus = `⚠️ ${quickAnalysis.warnings[0]}`;
                }

                if (quickAnalysis && quickAnalysis.suggestions && quickAnalysis.suggestions.length > 0) {
                  stabilityDetails = `建议: ${quickAnalysis.suggestions.length}项`;
                }
              } catch (err) {
                stabilityStatus = '分析中...';
              }
            }

            // 添加稳定化标记（如果有）
            if (lastStabilizationResult && lastStabilizationResult.timestamp) {
              const timeSinceStabilization = Date.now() - lastStabilizationResult.timestamp;
              if (timeSinceStabilization < 5000) {
                stabilityDetails = (stabilityDetails ? stabilityDetails + ', ' : '') + '已稳定化';
              }
            }

            shipStabilityEl.textContent = stabilityStatus + (stabilityDetails ? ` (${stabilityDetails})` : '');
          }

          // ========== 更新天气状态 ==========
          if (weatherSystem) {
            try {
              const weather = weatherSystem.getWeatherState();
              if (weather) {
                if (windSpeedEl) {
                  windSpeedEl.textContent = `${weather.windSpeed.toFixed(1)} m/s`;
                }
                if (windDirectionEl) {
                  windDirectionEl.textContent = `${weather.windDirection.toFixed(0)}°`;
                }
                if (rainIntensityEl) {
                  rainIntensityEl.textContent = `${weather.rainIntensity.toFixed(1)} mm/h`;
                }
                if (visibilityEl) {
                  visibilityEl.textContent = `${(weather.visibility * 100).toFixed(0)}%`;
                }
                if (seaStateEl) {
                  seaStateEl.textContent = weather.seaState || '-';
                }
              }
            } catch (err) {
              // 天气更新失败不影响船体状态更新
            }
          }

        } catch (error) {
          // 错误处理：即使出错也尝试显示基本信息
          console.error('❌ Error updating status:', error);

          // 尝试显示错误状态
          if (shipPositionEl) {
            shipPositionEl.textContent = '更新错误';
          }
          if (shipStabilityEl) {
            shipStabilityEl.textContent = '更新错误';
          }
        }
      }

      // ============= 启动应用 =============
      init();

      // 初始化自动验证器（延迟3秒，确保所有系统都已加载完成）
      setTimeout(() => {
        const demoInstance = {
          weatherSystem,
          simulatorEngine,
          shipController,
          camera,
          controls,
          waterMeshFar,
          resetBoatPose: typeof resetBoatPose !== 'undefined' ? resetBoatPose : null,
          setOverallView: typeof setOverallView !== 'undefined' ? setOverallView : null,
          setTopView: typeof setTopView !== 'undefined' ? setTopView : null,
          setSideView: typeof setSideView !== 'undefined' ? setSideView : null,
          setFrontView: typeof setFrontView !== 'undefined' ? setFrontView : null
        };

        initAutoValidator(demoInstance);

        console.log('');
        console.log('═══════════════════════════════════════════════════════');
        console.log('🧪 提示：输入以下命令运行自动验证 | Tip: Run auto validation');
        console.log('   autoValidator.runAllTests()');
        console.log('═══════════════════════════════════════════════════════');
        console.log('');
      }, 3000);

      animate();
