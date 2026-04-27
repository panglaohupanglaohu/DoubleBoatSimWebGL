/**
 * DoubleBoatClawSystem - 数字孪生主入口
 * 
 * 整合 Three.js 3D 渲染与后端实时数据
 */

import * as THREE from 'https://esm.sh/three@0.165.0';
import { OrbitControls } from 'https://esm.sh/three@0.165.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://esm.sh/three@0.165.0/examples/jsm/loaders/GLTFLoader.js';
import { EffectComposer } from 'https://esm.sh/three@0.165.0/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://esm.sh/three@0.165.0/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'https://esm.sh/three@0.165.0/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'https://esm.sh/three@0.165.0/examples/jsm/postprocessing/ShaderPass.js';

// 导入现有模块
import { waveParams, waterUniforms, getWaveHeight } from './waves.js';
import AgentTeamMonitor from './layer1-interface/AgentTeamMonitor.js';
import WeatherEffects from './WeatherEffects.js';

// ==================== 全局状态 ====================

const state = {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    boatMesh: null,
    waterMesh: null,
    ws: null,
    latestData: null,
    heatmapMaterials: [],
    semanticLabels: [],
    fusionMarkers: [],
    // AR-CAS 场景对象
    cargoShip: null,
    icebergs: [],
    arCasTargets: [],       // {mesh, label, data}
    arCasEnabled: true,
    externalSync: {
        ownShip: null,
        selectedTarget: null,
        alarms: [],
        weather: null,
        fusionTracks: [],
        taskGraph: null,
        source: null,
        updatedAt: null,
    },
    cameraControl: {
        mode: 'bridge',
        lastSelectedTargetKey: null,
        lastAppliedAt: null,
        animationToken: 0,
        manualTargetSelection: false,
    },
    agentTeamMonitor: null,
    weatherEffects: null,
};

// ==================== 初始化 ====================

export function init() {
    console.log('🚀 Initializing Digital Twin...');
    
    // 立即隐藏加载动画 (1 秒后)
    setTimeout(() => {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
    }, 1000);
    
    // 创建场景
    state.scene = new THREE.Scene();
    state.scene.background = new THREE.Color(0x0b1525);
    state.scene.fog = new THREE.Fog(0x0b1525, 80, 600);
    
    // 创建相机
    const container = document.getElementById('canvas-container');
    state.camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        800
    );
    state.camera.position.set(45, 30, 50);
    
    // 创建渲染器
    state.renderer = new THREE.WebGLRenderer({ 
        canvas: document.getElementById('three-canvas'),
        antialias: true,
        powerPreference: 'high-performance',
    });
    state.renderer.setSize(container.clientWidth, container.clientHeight);
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    state.renderer.shadowMap.enabled = true;
    state.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    state.renderer.toneMappingExposure = 1.35;  // 日间模式: 更亮的暴光
    state.renderer.outputColorSpace = THREE.SRGBColorSpace;
    
    // 后处理效果链
    state._composer = new EffectComposer(state.renderer);
    // (will be initialized after scene & camera are ready)
    
    // 创建控制器
    state.controls = new OrbitControls(state.camera, state.renderer.domElement);
    state.controls.enableDamping = true;
    state.controls.enableZoom = true;
    state.controls.maxPolarAngle = Math.PI * 0.49;
    state.controls.target.set(0, 0, 0);
    state.controls.minDistance = 10;
    state.controls.maxDistance = 120;

    // ── 监控摄像头预设（worldmonitor-map.html 通过 ?cam=top|bow|stern 嵌入）──
    const camParam = new URLSearchParams(window.location.search).get('cam');
    if (camParam && ['top', 'bow', 'stern'].includes(camParam)) {
        state.cctvPreset = camParam;
        // 关闭旋转/平移，仅保留鼠标滚轮缩放（用户要求）
        state.controls.enableRotate = false;
        state.controls.enablePan = false;
        state.controls.enableZoom = true;
        state.controls.minDistance = 5;
        state.controls.maxDistance = 400;
        // canvas 仍要响应滚轮事件
        try { state.renderer.domElement.style.pointerEvents = 'auto'; } catch (e) {}
        if (camParam === 'top') {
            state.camera.position.set(0, 180, 1);
            state.camera.fov = 60;
        } else {
            state.camera.fov = 50;
        }
        state.camera.updateProjectionMatrix();
        console.log(`[CCTV] preset=${camParam} 已激活（鼠标滚轮可缩放）`);
        // 鼠标滚轮缩放（调整 FOV，35° ~ 95°）
        state.cctvZoom = 1.0;
        state.renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            const baseFov = camParam === 'top' ? 60 : 50;
            state.cctvZoom = Math.max(0.4, Math.min(2.0, state.cctvZoom + (e.deltaY > 0 ? 0.05 : -0.05)));
            state.camera.fov = baseFov * state.cctvZoom;
            state.camera.updateProjectionMatrix();
        }, { passive: false });
        // 强制 resize，避免 canvas 尺寸残留
        setTimeout(() => { try { window.dispatchEvent(new Event('resize')); } catch(e) {} }, 50);
        setTimeout(() => { try { window.dispatchEvent(new Event('resize')); } catch(e) {} }, 500);
    }
    
    // 设置灯光
    setupLights();
    
    // 创建水面
    createWater();
    
    // 加载船体模型
    loadBoat();
    
    // 创建 AR-CAS 场景元素 (货船 + 冰山)
    createCargoShip();
    createIcebergs();
    
    // 创建 wabi-sabi 风格 HUD (货船轨道遥测)
    createCargoOrbitHUD();
    
    // 测深仪声纳可视化
    createDepthSounder();
    
    // 航道浮标
    createNavigationBuoys();
    
    // 3D 指北标记
    createCompassRose3D();
    
    // 灯塔
    createLighthouse();
    
    // 海底地形
    createSeaFloor();
    
    // 海面参考网格
    createSeaGrid();
    
    // 水下螺旋桨
    createPropellers();
    
    // 船旗
    createShipFlag();
    
    // 吃水标尺
    createDraughtMarks();
    
    // 锚链
    createAnchorChain();
    
    // 舵叶 + 舭龙骨
    createRudderAndKeels();
    
    // 船首侧推器
    createBowThrusterTunnel();
    
    // 水下光束
    createUnderwaterLightShafts();
    
    // 船舱内部
    createCabinInteriors();
    
    // 船名标签
    if (state.boatMesh) {
        const nameLabel = createFloatingLabel('POSEIDON-X\nIMO 9876543', 0x38bdf8,
            new THREE.Vector3(0, 12, 0));
        nameLabel.scale.set(4, 2, 1);
        state.boatMesh.add(nameLabel);
    }
    
    // 海鸥粒子群
    createSeagullFlock();
    
    // 雨滴系统
    createRainSystem();
    
    // 排气烟雾
    createExhaustSmoke();
    
    // 水线泡沫
    createWaterlineEffect();
    
    // 连接 WebSocket
    connectWebSocket();
    
    // 窗口大小调整
    window.addEventListener('resize', onWindowResize);
    window.addEventListener('beforeunload', () => {
        if (state.agentTeamMonitor) {
            state.agentTeamMonitor.stop();
        }
    });
    
    // 开始动画循环
    // 初始化后处理
    setupPostProcessing(container);
    animate();

    // 初始化双智能体团队监控浮层
    // Init weather effects
    state.weatherEffects = new WeatherEffects(state.scene);
    window.DigitalTwin.weatherEffects = state.weatherEffects;

    // initAgentTeamMonitor();  // 已禁用 - 占屏且遮挡 HUD
    
    console.log('✅ Digital Twin initialized');

    // 默认进入 Bridge 视角，禁止外部同步直接把相机拉到目标上。
    setCameraMode('bridge');
}

function makeDraggable(element, handleSelector) {
    let dragState = null;
    const handle = handleSelector ? element.querySelector(handleSelector) : element;
    if (!handle) return;
    handle.style.cursor = 'move';
    handle.style.userSelect = 'none';

    handle.addEventListener('mousedown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT') return;
        e.preventDefault();
        const rect = element.getBoundingClientRect();
        dragState = { startX: e.clientX, startY: e.clientY, startLeft: rect.left, startTop: rect.top };
        element.style.transition = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!dragState) return;
        const dx = e.clientX - dragState.startX;
        const dy = e.clientY - dragState.startY;
        const newLeft = Math.max(0, Math.min(dragState.startLeft + dx, window.innerWidth - element.offsetWidth));
        const newTop = Math.max(0, Math.min(dragState.startTop + dy, window.innerHeight - element.offsetHeight));
        element.style.left = newLeft + 'px';
        element.style.top = newTop + 'px';
        element.style.right = 'auto';
        element.style.bottom = 'auto';
    });

    document.addEventListener('mouseup', () => {
        if (dragState) {
            dragState = null;
            element.style.transition = 'box-shadow 0.2s';
        }
    });
}

function initAgentTeamMonitor() {
    const container = document.createElement('div');
    container.id = 'agent-team-monitor-container';
    container.style.cssText = `
      position: fixed;
      left: 80px;
      top: 60px;
      width: 520px;
      max-width: calc(100vw - 100px);
      max-height: 60vh;
      overflow: hidden;
      z-index: 999;
      background: rgba(5, 12, 20, 0.82);
      border: 1px solid rgba(79, 195, 247, 0.28);
      border-radius: 10px;
      backdrop-filter: blur(8px);
      transition: width 0.25s ease, max-height 0.25s ease;
    `;

    document.body.appendChild(container);

    state.agentTeamMonitor = new AgentTeamMonitor(container, {
        refreshInterval: 5000,
        apiBase: '/api/v1/agent-teams',
    });
    state.agentTeamMonitor.start();

    // -- Add collapse/expand toggle after render --
    setTimeout(() => {
        const header = container.querySelector('h2');
        if (!header) return;

        // Toggle button
        const toggleBtn = document.createElement('span');
        toggleBtn.textContent = '▼';
        toggleBtn.title = '收起/展开';
        toggleBtn.style.cssText = `
          cursor: pointer; margin-left: 8px; font-size: 12px;
          color: #78909c; user-select: none; transition: transform 0.2s;
          display: inline-block;
        `;
        header.appendChild(toggleBtn);

        let collapsed = true;  // start collapsed
        const body = container.querySelector('.agent-team-monitor');
        const contentEls = body ? Array.from(body.children).slice(1) : []; // everything after h2

        function setCollapsed(val) {
            collapsed = val;
            contentEls.forEach(el => el.style.display = collapsed ? 'none' : '');
            toggleBtn.textContent = collapsed ? '▶' : '▼';
            container.style.maxHeight = collapsed ? '48px' : '60vh';
            container.style.overflow = collapsed ? 'hidden' : 'auto';
        }

        setCollapsed(true); // default collapsed

        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            setCollapsed(!collapsed);
        });
        header.style.cursor = 'pointer';
        header.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            setCollapsed(!collapsed);
        });

        makeDraggable(container, 'h2');
    }, 300);
}

// ==================== 灯光 ====================

function setupLights() {
    // 环境光 (显著提亮场景)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
    state.scene.add(ambientLight);
    state._ambientLight = ambientLight;
    
    // 半球光 (天空蓝 + 海面浅蓝反射, 增亮 1.8x)
    const hemiLight = new THREE.HemisphereLight(0xbfe4ff, 0x4a7ba8, 1.6);
    state.scene.add(hemiLight);
    state._hemiLight = hemiLight;
    
    // 平行光 (太阳, 更亮更白)
    const dirLight = new THREE.DirectionalLight(0xfffaea, 2.2);
    dirLight.position.set(30, 60, 20);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(2048, 2048);
    dirLight.shadow.camera.near = 1;
    dirLight.shadow.camera.far = 200;
    dirLight.shadow.camera.left = -80;
    dirLight.shadow.camera.right = 80;
    dirLight.shadow.camera.top = 80;
    dirLight.shadow.camera.bottom = -80;
    dirLight.shadow.bias = -0.001;
    state.scene.add(dirLight);
    state._dirLight = dirLight;

    // 补光 (模拟天空散射, 增强)
    const fillLight = new THREE.DirectionalLight(0xa8d0ff, 0.6);
    fillLight.position.set(-20, 30, -10);
    state.scene.add(fillLight);
    
    // 正面柔光 (避免船体正面过暗)
    const frontFill = new THREE.DirectionalLight(0xffe8c8, 0.4);
    frontFill.position.set(0, 10, 50);
    state.scene.add(frontFill);

    // 创建天空
    createSky();
}

// ==================== 程序化天空 ====================

function createSky() {
    // 天空球 — 渐变从地平线到天顶
    const skyGeom = new THREE.SphereGeometry(380, 32, 32);
    const skyMat = new THREE.ShaderMaterial({
        uniforms: {
            topColor:     { value: new THREE.Color(0x4a8ac8) },   // 日间明亮蓝
            horizonColor: { value: new THREE.Color(0xc8dcf0) },   // 地平线浅灰蓝
            bottomColor:  { value: new THREE.Color(0x6a92b8) },
            sunDirection: { value: new THREE.Vector3(0.35, 0.55, 0.4).normalize() },
            sunColor:     { value: new THREE.Color(0xfff0c8) },   // 暖白太阳
            starDensity:  { value: 0.0 },   // 白天无星
            time:         { value: 0 },
        },
        vertexShader: /* glsl */ `
            varying vec3 vWorldPosition;
            varying vec3 vDirection;
            void main() {
                vec4 worldPos = modelMatrix * vec4(position, 1.0);
                vWorldPosition = worldPos.xyz;
                vDirection = normalize(position);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: /* glsl */ `
            uniform vec3 topColor;
            uniform vec3 horizonColor;
            uniform vec3 bottomColor;
            uniform vec3 sunDirection;
            uniform vec3 sunColor;
            uniform float starDensity;
            uniform float time;

            varying vec3 vWorldPosition;
            varying vec3 vDirection;

            // 伪随机哈希
            float hash(vec2 p) {
                return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
            }

            void main() {
                vec3 dir = normalize(vDirection);
                float y = dir.y;

                // 天空渐变
                vec3 sky;
                if (y > 0.0) {
                    float t = pow(y, 0.5);
                    sky = mix(horizonColor, topColor, t);
                } else {
                    sky = mix(horizonColor, bottomColor, min(-y * 3.0, 1.0));
                }

                // 星星
                if (y > 0.05) {
                    vec2 starUV = dir.xz / (dir.y + 0.001) * 50.0;
                    float starVal = hash(floor(starUV));
                    float starBrightness = step(1.0 - starDensity, starVal);
                    // 闪烁
                    starBrightness *= 0.5 + 0.5 * sin(starVal * 100.0 + time * (0.5 + starVal * 2.0));
                    starBrightness *= smoothstep(0.05, 0.3, y); // 靠近地平线淡出
                    sky += vec3(starBrightness * 0.8);
                }

                // 太阳光晕
                float sunDot = max(dot(dir, sunDirection), 0.0);
                vec3 sunGlow = sunColor * pow(sunDot, 64.0) * 2.0;
                sunGlow += sunColor * pow(sunDot, 8.0) * 0.3;
                // 地平线附近大气散射
                float horizonGlow = exp(-abs(y) * 4.0) * pow(sunDot, 2.0) * 0.4;
                sky += sunGlow;
                sky += sunColor * horizonGlow * 0.5;

                // 淡淡的银河带
                float milkyWay = smoothstep(0.3, 0.7, y) * (1.0 - smoothstep(0.7, 0.95, y));
                float mwNoise = hash(floor(dir.xz / (dir.y + 0.01) * 30.0)) * 0.3;
                sky += vec3(0.15, 0.18, 0.25) * milkyWay * mwNoise;

                gl_FragColor = vec4(sky, 1.0);
            }
        `,
        side: THREE.BackSide,
        depthWrite: false,
    });

    const skyMesh = new THREE.Mesh(skyGeom, skyMat);
    state.scene.add(skyMesh);
    state._skyMesh = skyMesh;
}

// ==================== 后处理效果 ====================

function setupPostProcessing(container) {
    const renderPass = new RenderPass(state.scene, state.camera);
    state._composer.addPass(renderPass);
    
    // Bloom — 给导航灯、水面高光添加光晕
    const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(container.clientWidth, container.clientHeight),
        0.35,   // strength (subtle)
        0.6,    // radius
        0.85    // threshold
    );
    state._composer.addPass(bloomPass);
    state._bloomPass = bloomPass;
    
    // 色彩校正着色器 — 增加对比度和色偏
    const colorCorrectionShader = {
        uniforms: {
            tDiffuse: { value: null },
            brightness: { value: 0.02 },
            contrast: { value: 1.08 },
            saturation: { value: 1.12 },
        },
        vertexShader: /* glsl */ `
            varying vec2 vUv;
            void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
        `,
        fragmentShader: /* glsl */ `
            uniform sampler2D tDiffuse;
            uniform float brightness;
            uniform float contrast;
            uniform float saturation;
            varying vec2 vUv;
            void main() {
                vec4 color = texture2D(tDiffuse, vUv);
                // 亮度
                color.rgb += brightness;
                // 对比度
                color.rgb = (color.rgb - 0.5) * contrast + 0.5;
                // 饱和度
                float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                color.rgb = mix(vec3(gray), color.rgb, saturation);
                // 轻微暗角 (vignette)
                float dist = length(vUv - 0.5) * 1.4;
                float vignette = 1.0 - dist * dist * 0.35;
                color.rgb *= vignette;
                gl_FragColor = color;
            }
        `,
    };
    const colorPass = new ShaderPass(colorCorrectionShader);
    state._composer.addPass(colorPass);
}

// ==================== 水面 (Gerstner 波浪海洋着色器) ====================

function createWater() {
    const geometry = new THREE.PlaneGeometry(600, 600, 256, 256);
    geometry.rotateX(-Math.PI / 2);

    const material = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            deepColor:    { value: new THREE.Color(0x001830) },
            shallowColor: { value: new THREE.Color(0x006994) },
            skyColor:     { value: new THREE.Color(0x87ceeb) },
            sunDirection: { value: new THREE.Vector3(0.5, 0.7, 0.3).normalize() },
            sunColor:     { value: new THREE.Color(0xfff5e6) },
            foamColor:    { value: new THREE.Color(0xffffff) },
            waveHeight:   { value: 0.8 },
            waveFreq:     { value: 0.12 },
            fogNear:      { value: 80.0 },
            fogFar:       { value: 600.0 },
            fogColor:     { value: new THREE.Color(0x0b1525) },
        },
        vertexShader: /* glsl */ `
            uniform float time;
            uniform float waveHeight;
            uniform float waveFreq;

            varying vec3 vWorldPos;
            varying vec3 vNormal;
            varying float vHeight;
            varying vec2 vUv;
            varying float vFogDepth;

            // Gerstner wave function
            vec3 gerstnerWave(vec2 pos, float amplitude, vec2 direction, float frequency, float speed, float steepness, float t) {
                float k = frequency;
                float w = sqrt(9.81 * k);  // 深水色散关系
                float phase = k * dot(direction, pos) - w * speed * t;
                float s = steepness / (k * amplitude);
                return vec3(
                    s * direction.x * amplitude * cos(phase),
                    amplitude * sin(phase),
                    s * direction.y * amplitude * cos(phase)
                );
            }

            void main() {
                vUv = uv;
                vec3 pos = position;
                vec2 xz = pos.xz;

                // 4 层 Gerstner 波叠加 (不同方向、频率、振幅)
                float A = waveHeight;
                vec3 w1 = gerstnerWave(xz, A * 0.5,  normalize(vec2(1.0, 0.3)),  waveFreq * 1.0, 1.0, 0.55, time);
                vec3 w2 = gerstnerWave(xz, A * 0.35, normalize(vec2(-0.7, 0.8)), waveFreq * 1.6, 0.9, 0.45, time);
                vec3 w3 = gerstnerWave(xz, A * 0.2,  normalize(vec2(0.3, -1.0)), waveFreq * 2.4, 1.1, 0.35, time);
                vec3 w4 = gerstnerWave(xz, A * 0.1,  normalize(vec2(-1.0, -0.4)),waveFreq * 3.8, 1.3, 0.25, time);

                vec3 displaced = pos + w1 + w2 + w3 + w4;
                vHeight = displaced.y - pos.y;

                // 有限差分法计算法线
                float eps = 0.5;
                vec2 xzR = xz + vec2(eps, 0.0);
                vec2 xzU = xz + vec2(0.0, eps);
                vec3 pR = pos + vec3(eps, 0.0, 0.0)
                    + gerstnerWave(xzR, A*0.5, normalize(vec2(1.0,0.3)),  waveFreq*1.0,1.0,0.55,time)
                    + gerstnerWave(xzR, A*0.35,normalize(vec2(-0.7,0.8)), waveFreq*1.6,0.9,0.45,time)
                    + gerstnerWave(xzR, A*0.2, normalize(vec2(0.3,-1.0)), waveFreq*2.4,1.1,0.35,time)
                    + gerstnerWave(xzR, A*0.1, normalize(vec2(-1.0,-0.4)),waveFreq*3.8,1.3,0.25,time);
                vec3 pU = pos + vec3(0.0, 0.0, eps)
                    + gerstnerWave(xzU, A*0.5, normalize(vec2(1.0,0.3)),  waveFreq*1.0,1.0,0.55,time)
                    + gerstnerWave(xzU, A*0.35,normalize(vec2(-0.7,0.8)), waveFreq*1.6,0.9,0.45,time)
                    + gerstnerWave(xzU, A*0.2, normalize(vec2(0.3,-1.0)), waveFreq*2.4,1.1,0.35,time)
                    + gerstnerWave(xzU, A*0.1, normalize(vec2(-1.0,-0.4)),waveFreq*3.8,1.3,0.25,time);

                vec3 tangent = normalize(pR - displaced);
                vec3 bitangent = normalize(pU - displaced);
                vNormal = normalize(cross(bitangent, tangent));

                vWorldPos = (modelMatrix * vec4(displaced, 1.0)).xyz;
                vFogDepth = length((modelViewMatrix * vec4(displaced, 1.0)).xyz);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
            }
        `,
        fragmentShader: /* glsl */ `
            uniform vec3 deepColor;
            uniform vec3 shallowColor;
            uniform vec3 skyColor;
            uniform vec3 sunDirection;
            uniform vec3 sunColor;
            uniform vec3 foamColor;
            uniform float fogNear;
            uniform float fogFar;
            uniform vec3 fogColor;
            uniform float time;

            varying vec3 vWorldPos;
            varying vec3 vNormal;
            varying float vHeight;
            varying vec2 vUv;
            varying float vFogDepth;

            void main() {
                vec3 normal = normalize(vNormal);
                vec3 viewDir = normalize(cameraPosition - vWorldPos);

                // 菲涅尔效应 — 掠射角更多反射天空色
                float fresnel = pow(1.0 - max(dot(viewDir, normal), 0.0), 4.0);
                fresnel = clamp(fresnel, 0.05, 0.95);

                // 深/浅水颜色混合 (基于波高)
                float depthFactor = clamp(vHeight * 0.6 + 0.5, 0.0, 1.0);
                vec3 waterColor = mix(deepColor, shallowColor, depthFactor);

                // 天空反射
                vec3 reflected = mix(waterColor, skyColor * 0.6, fresnel);

                // 镜面高光 (太阳光斑)
                vec3 halfVec = normalize(sunDirection + viewDir);
                float specular = pow(max(dot(normal, halfVec), 0.0), 256.0);
                specular += pow(max(dot(normal, halfVec), 0.0), 32.0) * 0.3;
                vec3 specColor = sunColor * specular * 1.2;

                // 次表面散射模拟 (光线穿透浅水区)
                float sss = pow(max(dot(viewDir, -sunDirection), 0.0), 3.0) * 0.15;
                vec3 sssColor = shallowColor * sss;

                // 泡沫 (波峰处白色)
                float foamThreshold = 0.45;
                float foam = smoothstep(foamThreshold, foamThreshold + 0.3, vHeight);
                // 添加泡沫噪点
                float foamNoise = fract(sin(dot(vUv * 200.0 + time * 0.5, vec2(12.9898, 78.233))) * 43758.5453);
                foam *= 0.6 + foamNoise * 0.4;

                vec3 finalColor = reflected + specColor + sssColor;
                finalColor = mix(finalColor, foamColor, foam * 0.7);

                // 雾气
                float fogFactor = smoothstep(fogNear, fogFar, vFogDepth);
                finalColor = mix(finalColor, fogColor, fogFactor);

                // 深海边缘渐变透明
                float edgeDist = max(abs(vWorldPos.x), abs(vWorldPos.z));
                float edgeAlpha = 1.0 - smoothstep(220.0, 300.0, edgeDist);

                gl_FragColor = vec4(finalColor, 0.92 * edgeAlpha);
            }
        `,
        transparent: true,
        side: THREE.FrontSide,
    });

    state.waterMesh = new THREE.Mesh(geometry, material);
    state.waterMesh.receiveShadow = true;
    state.waterMesh.position.y = -1;
    state.scene.add(state.waterMesh);
}

// ==================== 船体模型 ====================

function loadBoat() {
    console.log('🚢 Loading GLB model: GLB_20251223141542.glb');
    
    const loader = new GLTFLoader();
    const modelPath = 'GLB_20251223141542.glb';
    
    console.log('📍 Model path:', modelPath);
    
    loader.load(
        modelPath,
        (gltf) => {
            console.log('✅ GLB model loaded successfully!');
            state.boatMesh = gltf.scene;
            state.boatMesh.scale.set(0.5, 0.5, 0.5);
            state.boatMesh.position.set(0, 0, 0);
            
            state.boatMesh.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            
            state.scene.add(state.boatMesh);
            console.log('🚢 Boat model added to scene');
            
            // 为 GLB 模型也添加导航灯和航迹
            addNavigationLights(state.boatMesh);
            createWakeTrail();
            createBowSpray();
            
            createSemanticLabels();
            
            // 隐藏加载动画
            const loading = document.getElementById('loading');
            if (loading) loading.style.display = 'none';
        },
        (xhr) => {
            const percent = (xhr.loaded / xhr.total * 100).toFixed(0);
            console.log(`📊 Loading progress: ${percent}%`);
            
            // 更新加载文本
            const loadingText = document.querySelector('#loading div:last-child');
            if (loadingText && xhr.total > 0) {
                const mb = (xhr.total / 1024 / 1024).toFixed(1);
                loadingText.textContent = `正在加载船体模型... ${percent}% (${mb}MB)`;
            }
        },
        (error) => {
            console.error('❌ GLB model load error:', error);
            console.warn('⚠️ Using fallback simplified model');
            createFallbackBoat();
            
            // 隐藏加载动画
            const loading = document.getElementById('loading');
            if (loading) loading.style.display = 'none';
        }
    );
}

// 详细版 WPC 穿浪双体船模型 (fallback)
function createFallbackBoat() {
    state.boatMesh = new THREE.Group();
    
    const hullMat = new THREE.MeshPhysicalMaterial({
        color: 0x2d2a26, roughness: 0.45, metalness: 0.10, clearcoat: 0.15,
    });
    const deckMat = new THREE.MeshPhysicalMaterial({
        color: 0x8a8378, roughness: 0.7, metalness: 0.03,
    });
    const superMat = new THREE.MeshPhysicalMaterial({
        color: 0xe8e3db, roughness: 0.5, metalness: 0.05,
    });
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x8a9b8a, roughness: 0.08, metalness: 0.2,
        transmission: 0.5, thickness: 0.2, transparent: true, opacity: 0.65,
    });
    const redMat = new THREE.MeshPhongMaterial({ color: 0x8f4a3a });
    
    // === 左右浮筒 (流线型截面 — 用拉伸曲面) ===
    function createPontoon(side) {
        const pontoon = new THREE.Group();
        const xOff = side * 4;
        
        // 主体 — 圆角长方体近似
        const shape = new THREE.Shape();
        const w = 1.4, h = 1.2;
        const r = 0.35;
        shape.moveTo(-w + r, -h);
        shape.lineTo(w - r, -h);
        shape.quadraticCurveTo(w, -h, w, -h + r);
        shape.lineTo(w, h - r);
        shape.quadraticCurveTo(w, h, w - r, h);
        shape.lineTo(-w + r, h);
        shape.quadraticCurveTo(-w, h, -w, h - r);
        shape.lineTo(-w, -h + r);
        shape.quadraticCurveTo(-w, -h, -w + r, -h);
        
        const extrudeSettings = { depth: 14, bevelEnabled: true, bevelThickness: 0.15, bevelSize: 0.1, bevelSegments: 3 };
        const pontGeom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        pontGeom.rotateX(Math.PI / 2);
        pontGeom.translate(0, 0, -7);
        const pontMesh = new THREE.Mesh(pontGeom, hullMat);
        pontMesh.position.set(xOff, -0.8, 0);
        pontMesh.castShadow = true;
        pontoon.add(pontMesh);
        
        // 艏部尖削
        const bowGeom = new THREE.ConeGeometry(1.2, 3.5, 8, 1, false, 0, Math.PI);
        bowGeom.rotateX(Math.PI / 2);
        bowGeom.rotateZ(Math.PI);
        const bowMesh = new THREE.Mesh(bowGeom, hullMat);
        bowMesh.position.set(xOff, -0.8, -8.5);
        bowMesh.castShadow = true;
        pontoon.add(bowMesh);
        
        // 水线漆 (红色防锈底漆)
        const wlGeom = new THREE.BoxGeometry(2.9, 0.3, 15);
        const wlMesh = new THREE.Mesh(wlGeom, redMat);
        wlMesh.position.set(xOff, -1.7, -0.5);
        pontoon.add(wlMesh);
        
        return pontoon;
    }
    
    state.boatMesh.add(createPontoon(-1));
    state.boatMesh.add(createPontoon(1));
    
    // === 连接桥/甲板 ===
    const deckGeom = new THREE.BoxGeometry(11, 0.35, 12);
    const deck = new THREE.Mesh(deckGeom, deckMat);
    deck.position.set(0, 0.5, -0.5);
    deck.castShadow = true;
    deck.receiveShadow = true;
    state.boatMesh.add(deck);
    
    // 甲板围栏
    const railMat = new THREE.MeshPhongMaterial({ color: 0x999999 });
    [[-5.3, 'left'], [5.3, 'right']].forEach(([x]) => {
        for (let z = -5.5; z <= 5; z += 1.2) {
            const post = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.0, 4), railMat);
            post.position.set(x, 1.15, z);
            state.boatMesh.add(post);
        }
        // 横杆
        const rail = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.03, 11), railMat);
        rail.position.set(x, 1.6, -0.5);
        state.boatMesh.add(rail);
    });
    
    // === 上层建筑 (驾驶室) ===
    const superGroup = new THREE.Group();
    
    // 第一层
    const level1 = new THREE.Mesh(new THREE.BoxGeometry(8, 1.8, 4), superMat);
    level1.position.set(0, 1.8, 1.5);
    level1.castShadow = true;
    superGroup.add(level1);
    
    // 第二层 (驾驶台 — 略收窄)
    const level2 = new THREE.Mesh(new THREE.BoxGeometry(7.5, 1.5, 3.5), superMat);
    level2.position.set(0, 3.45, 1.3);
    level2.castShadow = true;
    superGroup.add(level2);
    
    // 驾驶室窗户 (环形窗)
    const windowPositions = [
        // 前窗
        { pos: [0, 3.5, -0.4], size: [6, 0.9, 0.05] },
        // 侧窗
        { pos: [-3.8, 3.5, 1.3], size: [0.05, 0.9, 2.8] },
        { pos: [3.8, 3.5, 1.3], size: [0.05, 0.9, 2.8] },
    ];
    windowPositions.forEach(({ pos, size }) => {
        const win = new THREE.Mesh(new THREE.BoxGeometry(...size), glassMat);
        win.position.set(...pos);
        superGroup.add(win);
    });
    
    // 顶部甲板 + 桅杆
    const topDeck = new THREE.Mesh(new THREE.BoxGeometry(7, 0.15, 3), deckMat);
    topDeck.position.set(0, 4.3, 1.3);
    superGroup.add(topDeck);
    
    // 桅杆
    const mastMat = new THREE.MeshPhongMaterial({ color: 0xcccccc });
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 4, 6), mastMat);
    mast.position.set(0, 6.3, 1.3);
    mast.castShadow = true;
    superGroup.add(mast);
    
    // 雷达旋转盘
    const radarArm = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.08, 0.25), mastMat);
    radarArm.position.set(0, 7.8, 1.3);
    superGroup.add(radarArm);
    // 第二层雷达
    const radarArm2 = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.06, 0.2), mastMat);
    radarArm2.position.set(0, 8.5, 1.3);
    radarArm2.rotation.y = Math.PI / 4;
    superGroup.add(radarArm2);
    
    // 烟囱
    const funnel = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.5, 1.8, 8), 
        new THREE.MeshPhongMaterial({ color: 0x333344 }));
    funnel.position.set(0, 2.5, 3.5);
    funnel.castShadow = true;
    superGroup.add(funnel);
    // 烟囱顶
    const funnelTop = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.4, 0.3, 8),
        new THREE.MeshPhongMaterial({ color: 0x222233 }));
    funnelTop.position.set(0, 3.5, 3.5);
    superGroup.add(funnelTop);
    
    state.boatMesh.add(superGroup);
    
    // === 导航灯 ===
    addNavigationLights(state.boatMesh);
    
    // === 船尾航迹系统 ===
    createWakeTrail();
    
    // === 船首飞溅 ===
    createBowSpray();
    
    state.boatMesh.position.set(0, 0, 0);
    state.scene.add(state.boatMesh);
    
    console.log('✅ Detailed WPC catamaran fallback created');
    createSemanticLabels();
}

// ==================== 导航灯系统 (IMO COLREG 规则) ====================

function addNavigationLights(ship) {
    state._navLights = [];
    
    // 右舷绿灯 (112.5° 扇区)
    const stbdLight = new THREE.PointLight(0x00ff00, 2, 15);
    stbdLight.position.set(5.5, 2, -4);
    ship.add(stbdLight);
    const stbdGlow = new THREE.Mesh(
        new THREE.SphereGeometry(0.12, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0x00ff00 })
    );
    stbdGlow.position.copy(stbdLight.position);
    ship.add(stbdGlow);
    state._navLights.push({ light: stbdLight, glow: stbdGlow, type: 'sidelight' });
    
    // 左舷红灯
    const portLight = new THREE.PointLight(0xff0000, 2, 15);
    portLight.position.set(-5.5, 2, -4);
    ship.add(portLight);
    const portGlow = new THREE.Mesh(
        new THREE.SphereGeometry(0.12, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xff0000 })
    );
    portGlow.position.copy(portLight.position);
    ship.add(portGlow);
    state._navLights.push({ light: portLight, glow: portGlow, type: 'sidelight' });
    
    // 桅灯 (白色, 225° 扇区, 前方)
    const mastLight = new THREE.PointLight(0xffffff, 3, 25);
    mastLight.position.set(0, 8.8, 1.3);
    ship.add(mastLight);
    const mastGlow = new THREE.Mesh(
        new THREE.SphereGeometry(0.1, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xffffee })
    );
    mastGlow.position.copy(mastLight.position);
    ship.add(mastGlow);
    state._navLights.push({ light: mastLight, glow: mastGlow, type: 'masthead' });
    
    // 尾灯 (白色, 135° 扇区)
    const sternLight = new THREE.PointLight(0xffffff, 1.5, 12);
    sternLight.position.set(0, 1.5, 6);
    ship.add(sternLight);
    const sternGlow = new THREE.Mesh(
        new THREE.SphereGeometry(0.1, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xffffdd })
    );
    sternGlow.position.copy(sternLight.position);
    ship.add(sternGlow);
    state._navLights.push({ light: sternLight, glow: sternGlow, type: 'stern' });
}

function updateNavLights(time) {
    // 桅灯微弱闪烁 (模拟灯泡抖动)
    if (state._navLights) {
        state._navLights.forEach(nl => {
            if (nl.type === 'masthead') {
                nl.light.intensity = 3 + Math.sin(time * 12) * 0.15;
            }
        });
    }
}

// ==================== 船尾航迹 (Kelvin wake pattern) ====================

function createWakeTrail() {
    const maxPoints = 120;
    const positions = new Float32Array(maxPoints * 3);
    const alphas = new Float32Array(maxPoints);
    const widths = new Float32Array(maxPoints);
    
    // 初始化
    for (let i = 0; i < maxPoints; i++) {
        positions[i * 3] = 0;
        positions[i * 3 + 1] = -0.5;
        positions[i * 3 + 2] = i * 0.5;
        alphas[i] = 1.0 - i / maxPoints;
        widths[i] = 0.3 + (i / maxPoints) * 3.0;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));
    
    const material = new THREE.ShaderMaterial({
        uniforms: {
            color: { value: new THREE.Color(0x88bbdd) },
        },
        vertexShader: /* glsl */ `
            attribute float alpha;
            varying float vAlpha;
            void main() {
                vAlpha = alpha;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = max(1.0, (1.0 - vAlpha) * 6.0 + 2.0);
            }
        `,
        fragmentShader: /* glsl */ `
            uniform vec3 color;
            varying float vAlpha;
            void main() {
                // 圆形点
                float dist = length(gl_PointCoord - vec2(0.5));
                if (dist > 0.5) discard;
                float a = vAlpha * (1.0 - dist * 2.0);
                gl_FragColor = vec4(color, a * 0.6);
            }
        `,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    });
    
    const wake = new THREE.Points(geometry, material);
    wake.frustumCulled = false;
    state.scene.add(wake);
    state._wakeTrail = wake;
    state._wakePositions = positions;
    state._wakeMaxPoints = maxPoints;
}

function updateWakeTrail(time) {
    if (!state._wakeTrail || !state.boatMesh) return;
    const positions = state._wakePositions;
    const maxPts = state._wakeMaxPoints;
    
    // 船尾位置
    const sternWorld = new THREE.Vector3(0, -0.3, 6);
    state.boatMesh.localToWorld(sternWorld);
    
    // 前移所有点
    for (let i = maxPts - 1; i > 0; i--) {
        positions[i * 3] = positions[(i - 1) * 3];
        positions[i * 3 + 1] = positions[(i - 1) * 3 + 1];
        positions[i * 3 + 2] = positions[(i - 1) * 3 + 2];
    }
    // 新点 = 船尾位置 + 轻微随机
    positions[0] = sternWorld.x + (Math.random() - 0.5) * 0.5;
    positions[1] = -0.6 + Math.random() * 0.15;
    positions[2] = sternWorld.z + (Math.random() - 0.5) * 0.3;
    
    state._wakeTrail.geometry.attributes.position.needsUpdate = true;
    
    // Kelvin 尾迹 V 形 (19.47° 半角)
    if (!state._kelvinWake && state.boatMesh) {
        const vLen = 40, halfAngle = 19.47 * Math.PI / 180;
        const pts = [];
        // 左侧
        for (let i = 0; i <= 20; i++) {
            const t = i / 20;
            pts.push(new THREE.Vector3(
                -Math.sin(halfAngle) * vLen * t,
                -0.5,
                Math.cos(halfAngle) * vLen * t + 6
            ));
        }
        // 回到船尾
        pts.push(new THREE.Vector3(0, -0.5, 6));
        // 右侧
        for (let i = 0; i <= 20; i++) {
            const t = i / 20;
            pts.push(new THREE.Vector3(
                Math.sin(halfAngle) * vLen * t,
                -0.5,
                Math.cos(halfAngle) * vLen * t + 6
            ));
        }
        const lineGeom = new THREE.BufferGeometry().setFromPoints(pts);
        const lineMat = new THREE.LineBasicMaterial({
            color: 0xaaccee, transparent: true, opacity: 0.25,
            blending: THREE.AdditiveBlending,
        });
        const kelvin = new THREE.Line(lineGeom, lineMat);
        state.boatMesh.add(kelvin); // 附加到船上, 随船运动
        state._kelvinWake = kelvin;
    }
    
    // 更新船首飞溅
    updateBowSpray(time);
}

// ==================== 船首飞溅粒子 ====================

function createBowSpray() {
    const count = 200;
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const lifetimes = new Float32Array(count);
    const sizes = new Float32Array(count);
    
    for (let i = 0; i < count; i++) {
        positions[i * 3] = 0;
        positions[i * 3 + 1] = -10; // hidden below
        positions[i * 3 + 2] = 0;
        velocities[i * 3] = 0;
        velocities[i * 3 + 1] = 0;
        velocities[i * 3 + 2] = 0;
        lifetimes[i] = 0;
        sizes[i] = 0.5 + Math.random() * 1.0;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    const material = new THREE.ShaderMaterial({
        uniforms: {
            color: { value: new THREE.Color(0xccddee) },
        },
        vertexShader: /* glsl */ `
            attribute float size;
            varying float vSize;
            void main() {
                vSize = size;
                vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = size * (80.0 / -mvPos.z);
                gl_Position = projectionMatrix * mvPos;
            }
        `,
        fragmentShader: /* glsl */ `
            uniform vec3 color;
            varying float vSize;
            void main() {
                float d = length(gl_PointCoord - 0.5);
                if (d > 0.5) discard;
                float a = (1.0 - d * 2.0) * 0.5;
                gl_FragColor = vec4(color, a);
            }
        `,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    });
    
    const points = new THREE.Points(geometry, material);
    points.frustumCulled = false;
    state.scene.add(points);
    
    state._bowSpray = {
        mesh: points,
        positions,
        velocities,
        lifetimes,
        count,
        nextEmit: 0,
    };
}

function updateBowSpray(time) {
    if (!state._bowSpray || !state.boatMesh) return;
    const spray = state._bowSpray;
    const pos = spray.positions;
    const vel = spray.velocities;
    const life = spray.lifetimes;
    const dt = 0.016;
    
    // 波高影响飞溅强度
    let waveH = 0.5;
    if (state.weatherEffects) {
        waveH = state.weatherEffects.weather.wave.height;
    }
    const sprayIntensity = Math.min(waveH * 2.0, 5.0);
    
    // 船首世界位置
    const bowWorld = new THREE.Vector3(0, 0.5, -8);
    state.boatMesh.localToWorld(bowWorld);
    
    // 更新现有粒子
    for (let i = 0; i < spray.count; i++) {
        if (life[i] > 0) {
            life[i] -= dt;
            // 重力 + 风阻
            vel[i * 3 + 1] -= 9.8 * dt;
            vel[i * 3] *= 0.98;
            vel[i * 3 + 2] *= 0.98;
            pos[i * 3] += vel[i * 3] * dt;
            pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
            pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
            // 落入水面以下则消亡
            if (pos[i * 3 + 1] < -1.0) life[i] = 0;
        }
    }
    
    // 每帧发射几个新粒子 (基于波高)
    const emitCount = Math.floor(sprayIntensity * 3);
    for (let e = 0; e < emitCount; e++) {
        const idx = spray.nextEmit % spray.count;
        spray.nextEmit++;
        pos[idx * 3] = bowWorld.x + (Math.random() - 0.5) * 3;
        pos[idx * 3 + 1] = bowWorld.y + Math.random() * 0.5;
        pos[idx * 3 + 2] = bowWorld.z + (Math.random() - 0.5) * 1.5;
        // 向上向外飞溅
        vel[idx * 3] = (Math.random() - 0.5) * sprayIntensity * 2;
        vel[idx * 3 + 1] = 2 + Math.random() * sprayIntensity * 3;
        vel[idx * 3 + 2] = -(1 + Math.random() * sprayIntensity);
        life[idx] = 0.5 + Math.random() * 0.8;
    }
    
    spray.mesh.geometry.attributes.position.needsUpdate = true;
}

// ==================== AR-CAS: 货船模型 (参考 NMRI threeShipAnimation 集装箱船) ====================

function _buildHullGeometry(length, beam, depth, bowTaper, sternTaper) {
    // 构建真实船体形状 — 带尖艏和方艉的 BufferGeometry
    const segs = 24; // 沿船长方向分段
    const radSegs = 8; // 横截面半圆分段
    const vertices = [];
    const indices = [];
    const normals = [];

    for (let i = 0; i <= segs; i++) {
        const t = i / segs; // 0=艏, 1=艉
        const z = (t - 0.5) * length; // z 从 -length/2 到 +length/2

        // 横截面宽度: 艏部收窄, 中部最宽, 艉部略窄
        let widthFactor = 1.0;
        if (t < bowTaper) {
            // 艏部渐缩 (抛物线)
            const bt = t / bowTaper;
            widthFactor = Math.sqrt(bt);
        } else if (t > (1.0 - sternTaper)) {
            // 艉部渐缩
            const st = (1.0 - t) / sternTaper;
            widthFactor = 0.7 + 0.3 * st;
        }
        const halfW = (beam / 2) * widthFactor;

        // 底部 V 形龙骨
        let keelDepth = depth;
        if (t < bowTaper * 0.6) {
            keelDepth = depth * (0.5 + 0.5 * (t / (bowTaper * 0.6)));
        }

        // 半圆截面 (从左舷到右舷, 底部圆弧)
        for (let j = 0; j <= radSegs; j++) {
            const a = (j / radSegs) * Math.PI; // 0 → π
            const x = Math.cos(a) * halfW;
            const y = -Math.sin(a) * keelDepth;
            vertices.push(x, y, z);
            // 近似法线
            const nx = Math.cos(a) * widthFactor;
            const ny = -Math.sin(a);
            const len = Math.sqrt(nx * nx + ny * ny) || 1;
            normals.push(nx / len, ny / len, 0);
        }
    }

    // 索引
    const stride = radSegs + 1;
    for (let i = 0; i < segs; i++) {
        for (let j = 0; j < radSegs; j++) {
            const a = i * stride + j;
            const b = a + stride;
            const c = a + 1;
            const d = b + 1;
            indices.push(a, b, c);
            indices.push(c, b, d);
        }
    }

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geom.setIndex(indices);
    geom.computeVertexNormals();
    return geom;
}

function createCargoShip() {
    const ship = new THREE.Group();

    // ========== 材质定义 ==========
    const hullMat = new THREE.MeshPhongMaterial({
        color: 0x2d2a26, shininess: 40, specular: 0x1a1a1a
    });
    const hullBottomMat = new THREE.MeshPhongMaterial({
        color: 0x6b3a2a, shininess: 20  // 防污漆 — 侘寂朱色
    });
    const deckMat = new THREE.MeshPhongMaterial({
        color: 0x8a8378, shininess: 15
    });
    const superMat = new THREE.MeshPhongMaterial({
        color: 0xe8e3db, shininess: 35
    });
    const windowMat = new THREE.MeshPhongMaterial({
        color: 0x5a6b5a, shininess: 80, specular: 0x3a5a3a,
        emissive: 0x0a150a, emissiveIntensity: 0.2
    });
    const funnelMat = new THREE.MeshPhongMaterial({
        color: 0x3a3632, shininess: 30
    });
    const funnelBandMat = new THREE.MeshPhongMaterial({
        color: 0x8f4a3a, shininess: 20
    });
    const railMat = new THREE.MeshPhongMaterial({
        color: 0xbfb9b0, shininess: 40
    });

    // ========== 1. 船体 (约 300TEU 集装箱船, length≈70, beam≈12) ==========
    const L = 70, B = 12, D = 5.5;

    // 水线以下 (红色防污漆)
    const hullLower = new THREE.Mesh(
        _buildHullGeometry(L, B, D * 0.6, 0.25, 0.15),
        hullBottomMat
    );
    hullLower.position.y = -0.5;
    hullLower.castShadow = true;
    hullLower.receiveShadow = true;
    ship.add(hullLower);

    // 水线以上 (深蓝色船体)
    const hullUpper = new THREE.Mesh(
        new THREE.BoxGeometry(B, D * 0.45, L),
        hullMat
    );
    hullUpper.position.y = 0.8;
    hullUpper.castShadow = true;
    ship.add(hullUpper);

    // 艏部楔形 — 让船头看起来尖锐
    const bowShape = new THREE.Shape();
    bowShape.moveTo(0, 0);
    bowShape.lineTo(-B / 2, 0);
    bowShape.lineTo(0, -10);
    bowShape.closePath();
    const bowExtrudeSettings = { depth: D * 0.45, bevelEnabled: false };
    const bowGeom = new THREE.ExtrudeGeometry(bowShape, bowExtrudeSettings);
    const bowMesh = new THREE.Mesh(bowGeom, hullMat);
    bowMesh.rotation.x = -Math.PI / 2;
    bowMesh.position.set(0, 0.8 + D * 0.225, -L / 2);
    bowMesh.castShadow = true;
    ship.add(bowMesh);
    // 右舷对称
    const bowShapeR = new THREE.Shape();
    bowShapeR.moveTo(0, 0);
    bowShapeR.lineTo(B / 2, 0);
    bowShapeR.lineTo(0, -10);
    bowShapeR.closePath();
    const bowMeshR = new THREE.Mesh(
        new THREE.ExtrudeGeometry(bowShapeR, bowExtrudeSettings),
        hullMat
    );
    bowMeshR.rotation.x = -Math.PI / 2;
    bowMeshR.position.set(0, 0.8 + D * 0.225, -L / 2);
    bowMeshR.castShadow = true;
    ship.add(bowMeshR);

    // ========== 2. 主甲板 ==========
    const mainDeck = new THREE.Mesh(
        new THREE.BoxGeometry(B + 0.5, 0.25, L + 1),
        deckMat
    );
    mainDeck.position.y = 1.8;
    mainDeck.receiveShadow = true;
    ship.add(mainDeck);

    // ========== 3. 集装箱货舱 (多层多列彩色集装箱) ==========
    const containerColors = [
        0x2196f3, 0xe53935, 0x43a047, 0xff9800, 0x8e24aa,
        0x00acc1, 0xd81b60, 0xfdd835, 0x546e7a, 0x6d4c41,
        0x1565c0, 0xc62828, 0x2e7d32, 0xef6c00, 0x4527a0,
        0x00838f, 0xad1457, 0xf9a825, 0x37474f, 0x4e342e
    ];

    // 20ft 集装箱: 约 6m×2.6m×2.4m → 缩放到场景 ≈ 2.6×1.1×1.0
    const cW = 2.4, cH = 1.05, cL = 5.2;
    const containerGeom = new THREE.BoxGeometry(cW, cH, cL);
    // 集装箱门面细节 (前后面凹槽效果)
    const cDetailGeom = new THREE.BoxGeometry(cW * 0.92, cH * 0.88, 0.05);

    // 集装箱排列: 5 个 bay, 每 bay 4 列 x 4 层
    const bayCount = 5;
    const colCount = 4;
    const layerCount = 4;
    const baySpacing = cL + 0.6;
    const bayStartZ = -(bayCount * baySpacing) / 2 + baySpacing / 2 - 3; // 偏向船头

    // InstancedMesh 方案 — 大幅减少 draw calls
    const maxContainers = bayCount * colCount * layerCount;
    const instancedMat = new THREE.MeshPhongMaterial({ shininess: 25, vertexColors: false });
    const instancedMesh = new THREE.InstancedMesh(containerGeom, instancedMat, maxContainers);
    instancedMesh.castShadow = true;
    instancedMesh.receiveShadow = true;
    
    // 每个实例的颜色
    const instanceColors = new Float32Array(maxContainers * 3);
    const dummy = new THREE.Object3D();
    const tempColor = new THREE.Color();
    let instanceIdx = 0;
    
    for (let bay = 0; bay < bayCount; bay++) {
        const bayZ = bayStartZ + bay * baySpacing;
        for (let col = 0; col < colCount; col++) {
            const colX = (col - (colCount - 1) / 2) * (cW + 0.15);
            for (let layer = 0; layer < layerCount; layer++) {
                if (layer >= 3 && Math.random() < 0.3) continue;
                if (layer >= 2 && Math.random() < 0.1) continue;
                if (instanceIdx >= maxContainers) break;

                const layerY = 2.1 + layer * (cH + 0.05);
                const colorIdx = (bay * 7 + col * 3 + layer * 5) % containerColors.length;
                
                dummy.position.set(colX, layerY, bayZ);
                dummy.updateMatrix();
                instancedMesh.setMatrixAt(instanceIdx, dummy.matrix);
                
                tempColor.setHex(containerColors[colorIdx]);
                instancedMesh.setColorAt(instanceIdx, tempColor);
                
                instanceIdx++;
            }
        }

        // Bay 之间的集装箱导轨 (cell guide)
        const guideH = layerCount * (cH + 0.05) + 0.5;
        for (let g = 0; g <= colCount; g++) {
            const gx = (g - colCount / 2) * (cW + 0.15);
            const guide = new THREE.Mesh(
                new THREE.BoxGeometry(0.08, guideH, 0.08),
                railMat
            );
            guide.position.set(gx, 2.1 + guideH / 2 - 0.3, bayZ);
            ship.add(guide);
        }
    }
    
    // 将 InstancedMesh 的实例数截断到实际使用量, 启用 per-instance color
    instancedMesh.count = instanceIdx;
    instancedMesh.instanceMatrix.needsUpdate = true;
    instancedMesh.instanceColor.needsUpdate = true;
    instancedMesh.material.vertexColors = false; // InstancedMesh uses setColorAt
    ship.add(instancedMesh);

    // ========== 4. 驾驶台 / 上层建筑 (船尾, 多层) ==========
    const superStartZ = L / 2 - 12;

    // 底层 — 机舱棚
    const superBase = new THREE.Mesh(
        new THREE.BoxGeometry(B - 1, 3.5, 10),
        superMat
    );
    superBase.position.set(0, 3.5, superStartZ);
    superBase.castShadow = true;
    ship.add(superBase);

    // 二层 — 船员生活区
    const superL2 = new THREE.Mesh(
        new THREE.BoxGeometry(B - 2, 2.5, 8),
        superMat
    );
    superL2.position.set(0, 6.5, superStartZ + 0.5);
    superL2.castShadow = true;
    ship.add(superL2);

    // 三层 — 驾驶台
    const bridgeDeck = new THREE.Mesh(
        new THREE.BoxGeometry(B - 2.5, 2.2, 6),
        superMat
    );
    bridgeDeck.position.set(0, 8.8, superStartZ + 1);
    bridgeDeck.castShadow = true;
    ship.add(bridgeDeck);

    // 驾驶台窗户 — 环形大窗
    const windowPositions = [
        { x: 0, y: 9.0, z: superStartZ - 2.2, sx: B - 3, sy: 1.2, sz: 0.15 }, // 前窗
        { x: (B - 2.5) / 2 + 0.08, y: 9.0, z: superStartZ + 1, sx: 0.15, sy: 1.2, sz: 5.5 }, // 右舷窗
        { x: -(B - 2.5) / 2 - 0.08, y: 9.0, z: superStartZ + 1, sx: 0.15, sy: 1.2, sz: 5.5 }, // 左舷窗
    ];
    windowPositions.forEach(w => {
        const win = new THREE.Mesh(
            new THREE.BoxGeometry(w.sx, w.sy, w.sz),
            windowMat
        );
        win.position.set(w.x, w.y, w.z);
        ship.add(win);
    });

    // 驾驶台顶部 — 罗经甲板 + 雷达桅
    const compassDeck = new THREE.Mesh(
        new THREE.BoxGeometry(B - 3, 0.2, 7),
        new THREE.MeshPhongMaterial({ color: 0xcccccc })
    );
    compassDeck.position.set(0, 10.0, superStartZ + 1);
    ship.add(compassDeck);

    // 雷达桅杆
    const mastGeom = new THREE.CylinderGeometry(0.12, 0.15, 5, 6);
    const mast = new THREE.Mesh(mastGeom, railMat);
    mast.position.set(0, 12.5, superStartZ + 0.5);
    ship.add(mast);

    // 雷达天线 (旋转横杆)
    const radarBar = new THREE.Mesh(
        new THREE.BoxGeometry(4, 0.15, 0.3),
        new THREE.MeshPhongMaterial({ color: 0xeeeeee })
    );
    radarBar.position.set(0, 14.8, superStartZ + 0.5);
    ship.add(radarBar);

    // ========== 5. 烟囱 ==========
    const funnelGroup = new THREE.Group();

    const funnelBody = new THREE.Mesh(
        new THREE.BoxGeometry(3, 5, 2.5),
        funnelMat
    );
    funnelBody.position.y = 2.5;
    funnelGroup.add(funnelBody);

    // 烟囱顶部排气口
    const funnelTop = new THREE.Mesh(
        new THREE.CylinderGeometry(0.8, 1.0, 1.5, 8),
        funnelMat
    );
    funnelTop.position.y = 5.5;
    funnelGroup.add(funnelTop);

    // 烟囱色带 (船公司标识)
    const funnelBand = new THREE.Mesh(
        new THREE.BoxGeometry(3.05, 1.2, 2.55),
        funnelBandMat
    );
    funnelBand.position.y = 3.5;
    funnelGroup.add(funnelBand);

    funnelGroup.position.set(0, 5.2, superStartZ + 4);
    ship.add(funnelGroup);

    // ========== 6. 船艏细节 ==========

    // 艏楼甲板 (略高于主甲板)
    const forecastle = new THREE.Mesh(
        new THREE.BoxGeometry(B - 0.5, 1.0, 8),
        deckMat
    );
    forecastle.position.set(0, 2.2, -L / 2 + 5);
    ship.add(forecastle);

    // 锚机
    const windlass = new THREE.Mesh(
        new THREE.CylinderGeometry(0.5, 0.5, 1.5, 8),
        railMat
    );
    windlass.rotation.z = Math.PI / 2;
    windlass.position.set(0, 3.0, -L / 2 + 3);
    ship.add(windlass);

    // 前桅杆
    const foreMast = new THREE.Mesh(
        new THREE.CylinderGeometry(0.1, 0.12, 8, 6),
        railMat
    );
    foreMast.position.set(0, 6.0, -L / 2 + 6);
    ship.add(foreMast);

    // 前桅横桁
    const foreYard = new THREE.Mesh(
        new THREE.BoxGeometry(3, 0.1, 0.1),
        railMat
    );
    foreYard.position.set(0, 9.5, -L / 2 + 6);
    ship.add(foreYard);

    // ========== 7. 舷侧细节 ==========

    // 吃水线标识
    const waterline = new THREE.Mesh(
        new THREE.BoxGeometry(B + 0.3, 0.1, L + 0.5),
        new THREE.MeshPhongMaterial({ color: 0x222222 })
    );
    waterline.position.y = -0.2;
    ship.add(waterline);

    // 舷墙 (两侧)
    for (const side of [-1, 1]) {
        const bulwark = new THREE.Mesh(
            new THREE.BoxGeometry(0.15, 1.2, L - 10),
            hullMat
        );
        bulwark.position.set(side * (B / 2 + 0.07), 2.3, 2);
        ship.add(bulwark);
    }

    // ========== 8. 甲板吊车 (2 台) ==========
    for (const craneZ of [-18, 10]) {
        const craneGroup = new THREE.Group();

        // 吊车底座
        const craneBase = new THREE.Mesh(
            new THREE.BoxGeometry(1.5, 1.5, 1.5),
            new THREE.MeshPhongMaterial({ color: 0xffab00 })
        );
        craneBase.position.y = 0.75;
        craneGroup.add(craneBase);

        // 吊车立柱
        const cranePillar = new THREE.Mesh(
            new THREE.BoxGeometry(0.6, 6, 0.6),
            new THREE.MeshPhongMaterial({ color: 0xffab00 })
        );
        cranePillar.position.y = 4.5;
        craneGroup.add(cranePillar);

        // 吊臂
        const craneBoom = new THREE.Mesh(
            new THREE.BoxGeometry(0.3, 0.3, 10),
            new THREE.MeshPhongMaterial({ color: 0xffab00 })
        );
        craneBoom.position.set(0, 7.5, -4);
        craneBoom.rotation.x = -0.15;
        craneGroup.add(craneBoom);

        craneGroup.position.set(B / 2 - 0.5, 1.8, craneZ);
        ship.add(craneGroup);
    }

    // ========== 配置 ==========
    // 初始位置 — 右前方 (~200m 距离)
    ship.position.set(85, 0, -45);
    ship.rotation.y = Math.PI * 0.15; // 略偏航向
    ship.scale.set(1, 1, 1);

    state.scene.add(ship);
    state.cargoShip = ship;

    // 给货船也加导航灯
    const cargoLights = [];
    // 右舷绿灯
    const cStbd = new THREE.PointLight(0x00ff00, 1.5, 20);
    cStbd.position.set(6, 3, -15);
    ship.add(cStbd);
    ship.add(new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 6), new THREE.MeshBasicMaterial({color:0x00ff00})));
    ship.children[ship.children.length-1].position.copy(cStbd.position);
    // 左舷红灯
    const cPort = new THREE.PointLight(0xff0000, 1.5, 20);
    cPort.position.set(-6, 3, -15);
    ship.add(cPort);
    ship.add(new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 6), new THREE.MeshBasicMaterial({color:0xff0000})));
    ship.children[ship.children.length-1].position.copy(cPort.position);
    // 桅灯
    const cMast = new THREE.PointLight(0xffffff, 2, 30);
    cMast.position.set(0, 18, 15);
    ship.add(cMast);
    ship.add(new THREE.Mesh(new THREE.SphereGeometry(0.15, 6, 6), new THREE.MeshBasicMaterial({color:0xffffdd})));
    ship.children[ship.children.length-1].position.copy(cMast.position);
    // 前桅灯 (大型船双桅灯)
    const cMast2 = new THREE.PointLight(0xffffff, 2, 30);
    cMast2.position.set(0, 14, -20);
    ship.add(cMast2);
    ship.add(new THREE.Mesh(new THREE.SphereGeometry(0.15, 6, 6), new THREE.MeshBasicMaterial({color:0xffffdd})));
    ship.children[ship.children.length-1].position.copy(cMast2.position);

    // AIS 标签
    const label = createFloatingLabel('CONTAINER VESSEL\nMMSI 412034567\n~160m Feeder', 0xff9800,
        new THREE.Vector3(85, 20, -45));
    state.scene.add(label);
    state.arCasTargets.push({ mesh: ship, label, data: {
        name: 'MV Pacific Fortune', mmsi: '412034567', type: 'Container',
        course: 195, speed: 12.5, cpa: 0.8, tcpa: 18.5, risk: 'medium'
    }});

    console.log('✅ AR-CAS: Container ship created (NMRI-style) with nav lights');
}

// ==================== AR-CAS: 冰山模型 ====================

function createIcebergs() {
    // 冰山尺寸: radius=scale (1unit≈2.3m), 直径≈scale*4.6m
    const icebergPositions = [
        { x: -55, z: -70, scale: 9, above: 7 },      // ~42m 大型冰山
        { x: -80, z: -45, scale: 5.5, above: 4 },    // ~25m 中型冰山
        { x: -40, z: -100, scale: 7, above: 5.5 },   // ~32m 中型冰山
        { x: -95, z: -90, scale: 3.0, above: 2.2 },  // ~14m 小型冰山 (growler)
        { x: -30, z: -55, scale: 2.0, above: 1.5 },  // ~9m bergy bit
    ];
    
    // 自定义冰山着色器 — 半透明次表面散射冰效果
    const iceMaterial = new THREE.ShaderMaterial({
        uniforms: {
            iceColor:    { value: new THREE.Color(0xc8eaf5) },
            deepIceColor:{ value: new THREE.Color(0x2a6090) },
            time:        { value: 0 },
        },
        vertexShader: /* glsl */ `
            varying vec3 vNormal;
            varying vec3 vWorldPos;
            varying float vY;
            void main() {
                vNormal = normalize(normalMatrix * normal);
                vec4 wp = modelMatrix * vec4(position, 1.0);
                vWorldPos = wp.xyz;
                vY = position.y;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: /* glsl */ `
            uniform vec3 iceColor;
            uniform vec3 deepIceColor;
            uniform float time;
            varying vec3 vNormal;
            varying vec3 vWorldPos;
            varying float vY;
            void main() {
                vec3 viewDir = normalize(cameraPosition - vWorldPos);
                vec3 normal = normalize(vNormal);
                // 菲涅尔 — 边缘更蓝更透明
                float fresnel = pow(1.0 - max(dot(viewDir, normal), 0.0), 3.0);
                // 深度混合 — 上部白，下部蓝
                float depthMix = clamp(vY * 0.15 + 0.5, 0.0, 1.0);
                vec3 color = mix(deepIceColor, iceColor, depthMix);
                // 光照
                vec3 lightDir = normalize(vec3(0.5, 0.7, 0.3));
                float diff = max(dot(normal, lightDir), 0.0) * 0.6 + 0.4;
                // 次表面散射 (背光照亮内部)
                float sss = pow(max(dot(viewDir, -lightDir), 0.0), 2.0) * 0.25;
                vec3 finalColor = color * diff + deepIceColor * sss + vec3(0.7, 0.85, 1.0) * fresnel * 0.3;
                // 微弱闪烁 (冰面结晶反光)
                float sparkle = pow(max(dot(reflect(-lightDir, normal), viewDir), 0.0), 128.0) * 0.8;
                finalColor += vec3(sparkle);
                float alpha = 0.88 - fresnel * 0.2;
                gl_FragColor = vec4(finalColor, alpha);
            }
        `,
        transparent: true,
        side: THREE.FrontSide,
        depthWrite: true,
    });
    
    icebergPositions.forEach((pos, idx) => {
        const iceberg = new THREE.Group();
        
        // 水上部分 — 高细分不规则多面体 + 冰着色器
        const detail = pos.scale > 6 ? 2 : 1;
        const aboveGeom = new THREE.IcosahedronGeometry(pos.scale, detail);
        const abovePositions = aboveGeom.attributes.position;
        // 分形噪声变形
        for (let i = 0; i < abovePositions.count; i++) {
            let x = abovePositions.getX(i);
            let y = abovePositions.getY(i);
            let z = abovePositions.getZ(i);
            // 大尺度变形
            const noise1 = 0.7 + Math.abs(Math.sin(x * 1.3 + z * 0.7)) * 0.4;
            // 中尺度裂缝
            const noise2 = 1.0 + Math.sin(x * 3.7 + y * 2.1) * 0.1;
            // 底部平坦 (水线)
            y = Math.max(y * noise1, -0.5) * noise2;
            x *= noise1 * noise2;
            z *= noise1 * noise2;
            // 顶部尖峰
            if (y > pos.scale * 0.5) y *= 1.0 + Math.random() * 0.3;
            abovePositions.setXYZ(i, x, y, z);
        }
        aboveGeom.computeVertexNormals();
        
        const aboveMesh = new THREE.Mesh(aboveGeom, iceMaterial.clone());
        aboveMesh.position.y = pos.above;
        aboveMesh.castShadow = true;
        aboveMesh.receiveShadow = true;
        iceberg.add(aboveMesh);
        
        // 水下部分 — 更大的深蓝半透明体
        const belowGeom = new THREE.IcosahedronGeometry(pos.scale * 2.2, 1);
        const belowPositions = belowGeom.attributes.position;
        for (let i = 0; i < belowPositions.count; i++) {
            let y = belowPositions.getY(i);
            if (y > 0.3) y = 0.3;
            belowPositions.setY(i, y);
            const noise = 0.6 + Math.abs(Math.sin(
                belowPositions.getX(i) * 0.8 + belowPositions.getZ(i) * 1.2
            )) * 0.5;
            belowPositions.setX(i, belowPositions.getX(i) * noise);
            belowPositions.setZ(i, belowPositions.getZ(i) * noise);
        }
        belowGeom.computeVertexNormals();
        
        const belowMat = new THREE.MeshPhongMaterial({
            color: 0x2a6090,
            transparent: true,
            opacity: 0.18,
            side: THREE.DoubleSide,
        });
        const belowMesh = new THREE.Mesh(belowGeom, belowMat);
        belowMesh.position.y = -pos.scale * 0.8;
        iceberg.add(belowMesh);
        
        // 冰山周围小浮冰碎片
        if (pos.scale > 4) {
            for (let f = 0; f < 6; f++) {
                const fragSize = 0.3 + Math.random() * 0.8;
                const fragGeom = new THREE.DodecahedronGeometry(fragSize, 0);
                const fragMesh = new THREE.Mesh(fragGeom, iceMaterial.clone());
                fragMesh.position.set(
                    (Math.random() - 0.5) * pos.scale * 3,
                    -0.2 + Math.random() * 0.3,
                    (Math.random() - 0.5) * pos.scale * 3
                );
                fragMesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
                iceberg.add(fragMesh);
            }
        }
        
        iceberg.position.set(pos.x, 0, pos.z);
        state.scene.add(iceberg);
        state.icebergs.push(iceberg);
        
        // 冰山标签 (直径≈scale*4.6m)
        const label = createFloatingLabel(
            `⚠ ICEBERG ${idx + 1}\n~${(pos.scale * 4.6).toFixed(0)}m`,
            0x00bcd4,
            new THREE.Vector3(pos.x, pos.above + pos.scale + 4, pos.z)
        );
        state.scene.add(label);
    });
    
    console.log(`✅ AR-CAS: ${icebergPositions.length} icebergs created`);
}

// ==================== AR-CAS: CPA/TCPA 计算 ====================

function calculateCPA(ownShip, target) {
    if (!ownShip || !target) return { cpa: 99, tcpa: 99, risk: 'low' };
    const dx = target.mesh.position.x - (state.boatMesh?.position.x || 0);
    const dz = target.mesh.position.z - (state.boatMesh?.position.z || 0);
    const dist = Math.sqrt(dx * dx + dz * dz);
    // 简化 CPA: 按距离/速度估算
    const relSpeed = Math.max(target.data.speed || 1, 1);
    const cpa = dist * 0.02;   // 场景坐标 → NM 近似
    const tcpa = (dist / relSpeed) * 2.0;
    let risk = 'low';
    if (cpa < 0.5 && tcpa < 30) risk = 'high';
    else if (cpa < 1.0 && tcpa < 60) risk = 'medium';
    return { cpa: Math.round(cpa * 100) / 100, tcpa: Math.round(tcpa * 10) / 10, risk };
}

function updateArCasPanel() {
    // 更新 AR-CAS HUD 面板
    const panel = document.getElementById('ar-cas-targets');
    if (!panel) return;
    
    let html = '';
    state.arCasTargets.forEach((t, i) => {
        const cpaData = calculateCPA(state.boatMesh, t);
        const riskColor = cpaData.risk === 'high' ? '#f56565' : cpaData.risk === 'medium' ? '#f6ad55' : '#48bb78';
        const riskIcon = cpaData.risk === 'high' ? '🔴' : cpaData.risk === 'medium' ? '🟡' : '🟢';
        const d = t.data || {};
        // COLREGs 规则判定
        let rule = '—';
        if (cpaData.risk === 'high') rule = 'Rule 13/14 让路';
        else if (cpaData.risk === 'medium') rule = 'Rule 15/17 保持航向';
        html += `<div style="padding:8px 10px;margin-bottom:6px;background:rgba(0,0,0,0.25);border-left:3px solid ${riskColor};border-radius:5px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <span style="color:${riskColor};font-weight:700">${riskIcon} ${d.name || 'Target ' + (i+1)}</span>
                <span style="font-size:11px;color:#94a3b8">MMSI ${d.mmsi || '---'}</span>
            </div>
            <div style="font-size:11px;color:#cbd5e1;margin-top:4px;">${d.type || 'Vessel'} | ${d.speed ?? '--'} kn @ ${d.course ?? '--'}°</div>
            <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:12px;">
                <span>CPA: <strong style="color:${riskColor}">${cpaData.cpa} NM</strong></span>
                <span>TCPA: <strong>${cpaData.tcpa} min</strong></span>
            </div>
            <div style="margin-top:4px;font-size:10px;color:#fde047;">📜 ${rule}</div>
        </div>`;
    });
    
    // 冰山信息
    state.icebergs.forEach((ib, i) => {
        const dx = ib.position.x - (state.boatMesh?.position.x || 0);
        const dz = ib.position.z - (state.boatMesh?.position.z || 0);
        const dist = (Math.sqrt(dx*dx + dz*dz) * 0.02).toFixed(2);
        const bearing = ((Math.atan2(dx, -dz) * 180 / Math.PI + 360) % 360).toFixed(0);
        html += `<div style="padding:8px 10px;margin-bottom:6px;background:rgba(0,188,212,0.08);border-left:3px solid #00bcd4;border-radius:5px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <span style="color:#22d3ee;font-weight:700">🧊 Iceberg ${i+1}</span>
                <span style="font-size:11px;color:#94a3b8">冰山</span>
            </div>
            <div style="font-size:11px;color:#cbd5e1;margin-top:4px;">漂浮冰山 (Ice Hazard)</div>
            <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:12px;">
                <span>距离: <strong style="color:#22d3ee">${dist} NM</strong></span>
                <span>方位: <strong>${bearing}°</strong></span>
            </div>
            <div style="margin-top:4px;font-size:10px;color:#fde047;">📜 Rule 6 — 保持安全航速</div>
        </div>`;
    });
    
    panel.innerHTML = html || '<div style="color:#94a3b8;text-align:center;padding:18px;">无目标</div>';
    
    // 更新 COLREGs 概览
    const colregsEl = document.getElementById('ar-cas-colregs');
    if (colregsEl) {
        const highCount = state.arCasTargets.filter(t => calculateCPA(state.boatMesh, t).risk === 'high').length;
        const medCount = state.arCasTargets.filter(t => calculateCPA(state.boatMesh, t).risk === 'medium').length;
        const lowCount = state.arCasTargets.length - highCount - medCount;
        colregsEl.innerHTML = `
            <span style="color:#f56565">🔴 高: ${highCount}</span>
            <span style="color:#f6ad55;margin-left:10px">🟡 中: ${medCount}</span>
            <span style="color:#48bb78;margin-left:10px">🟢 低: ${lowCount}</span>
            <span style="color:#22d3ee;margin-left:10px">🧊 冰山: ${state.icebergs.length}</span>
        `;
    }
    
    // 本船状态
    const osEl = document.getElementById('ar-cas-ownship-info');
    if (osEl && state.boatMesh) {
        const hdg = ((state.boatMesh.rotation.y * 180 / Math.PI + 360) % 360).toFixed(1);
        const spd = (state.boatSpeed || 12).toFixed(1);
        osEl.innerHTML = `航向 HDG ${hdg}° | 航速 SOG ${spd} kn<br>位置 ${state.boatMesh.position.x.toFixed(1)}, ${state.boatMesh.position.z.toFixed(1)} (相对)`;
    }
    
    // COLREGs 建议
    const adviceEl = document.getElementById('ar-cas-advice-text');
    if (adviceEl) {
        const highCount = state.arCasTargets.filter(t => calculateCPA(state.boatMesh, t).risk === 'high').length;
        const medCount = state.arCasTargets.filter(t => calculateCPA(state.boatMesh, t).risk === 'medium').length;
        let advice = '所有目标均在安全范围, 维持当前航向航速';
        if (highCount > 0) advice = `⚠️ ${highCount} 个高风险目标 — 立即采取让路行动 (右转/减速), COLREGs Rule 13/14 适用`;
        else if (medCount > 0) advice = `🟡 ${medCount} 个中风险目标 — 密切监视 CPA/TCPA, 准备机动`;
        else if (state.icebergs.length > 0) advice = `🧊 冰区航行 — Rule 6 安全航速, 加强瞭望, 开启雷达跟踪`;
        adviceEl.textContent = advice;
    }
    
    // 环境
    const envEl = document.getElementById('ar-cas-env-info');
    if (envEl) {
        const wx = window._lastWeather || { wind: 12, waveHeight: 1.5, visibility: 10 };
        envEl.innerHTML = `风速 ${(wx.wind||12).toFixed?.(1) || wx.wind} kn | 浪高 ${(wx.waveHeight||1.5).toFixed?.(1) || wx.waveHeight} m<br>能见度 ${wx.visibility || '>10'} NM | 海况 ${Math.ceil((wx.wind||12)/5)} 级`;
    }
}

// ==================== 水线飞溅泡沫 ====================

function createWaterlineEffect() {
    // 船两侧水线处的泡沫粒子
    const COUNT = 60;
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    
    for (let i = 0; i < COUNT; i++) {
        const side = i < COUNT / 2 ? -1 : 1;
        positions[i * 3] = side * (2.5 + Math.random() * 1.0);
        positions[i * 3 + 1] = -0.3 + Math.random() * 0.4;
        positions[i * 3 + 2] = (Math.random() - 0.3) * 8;
    }
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const mat = new THREE.PointsMaterial({
        color: 0xccddee,
        size: 0.25,
        transparent: true,
        opacity: 0.4,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    });
    
    const particles = new THREE.Points(geom, mat);
    if (state.boatMesh) state.boatMesh.add(particles);
    state._waterline = particles;
}

// ==================== 烟囱排气 ====================

function createExhaustSmoke() {
    const COUNT = 80;
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    const sizes = new Float32Array(COUNT);
    const opacities = new Float32Array(COUNT);
    const ages = new Float32Array(COUNT);
    
    for (let i = 0; i < COUNT; i++) {
        positions[i * 3] = 0;
        positions[i * 3 + 1] = -50; // hidden
        positions[i * 3 + 2] = 0;
        sizes[i] = 0.5;
        opacities[i] = 0;
        ages[i] = Math.random() * 5; // stagger
    }
    
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    const mat = new THREE.PointsMaterial({
        color: 0x888888,
        size: 1.5,
        transparent: true,
        opacity: 0.3,
        depthWrite: false,
        sizeAttenuation: true,
    });
    
    const smoke = new THREE.Points(geom, mat);
    smoke.frustumCulled = false;
    state.scene.add(smoke);
    state._exhaust = { points: smoke, ages, velocities: new Float32Array(COUNT * 3) };
    
    // 初始化速度
    for (let i = 0; i < COUNT; i++) {
        state._exhaust.velocities[i * 3] = (Math.random() - 0.5) * 0.02;
        state._exhaust.velocities[i * 3 + 1] = 0.03 + Math.random() * 0.02;
        state._exhaust.velocities[i * 3 + 2] = -0.01 + Math.random() * 0.01; // 向后飘
    }
}

function updateExhaustSmoke(time) {
    if (!state._exhaust || !state.boatMesh) return;
    const { points, ages, velocities } = state._exhaust;
    const pos = points.geometry.attributes.position;
    
    // 烟囱位置 (WPC 双体船上层建筑后方)
    const funnelPos = new THREE.Vector3(0, 7.5, 1.5);
    state.boatMesh.localToWorld(funnelPos);
    
    for (let i = 0; i < ages.length; i++) {
        ages[i] += 0.016;
        
        if (ages[i] > 4.0) {
            // 重生
            ages[i] = 0;
            pos.setXYZ(i, funnelPos.x, funnelPos.y, funnelPos.z);
            velocities[i * 3] = (Math.random() - 0.5) * 0.02;
            velocities[i * 3 + 1] = 0.03 + Math.random() * 0.02;
            velocities[i * 3 + 2] = -0.01 + Math.random() * 0.02;
        } else {
            // 上升 + 风漂移 + 扩散
            pos.setX(i, pos.getX(i) + velocities[i * 3] + Math.sin(time + i) * 0.003);
            pos.setY(i, pos.getY(i) + velocities[i * 3 + 1]);
            pos.setZ(i, pos.getZ(i) + velocities[i * 3 + 2]);
            // 减速
            velocities[i * 3 + 1] *= 0.998;
        }
    }
    pos.needsUpdate = true;
    
    // 随年龄变大变淡
    points.material.opacity = 0.25;
}

// ==================== 雨滴粒子系统 ====================

function createRainSystem() {
    const COUNT = 3000;
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    const velocities = new Float32Array(COUNT);
    
    for (let i = 0; i < COUNT; i++) {
        positions[i * 3]     = (Math.random() - 0.5) * 120;
        positions[i * 3 + 1] = Math.random() * 60;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 120;
        velocities[i] = 0.5 + Math.random() * 0.8;
    }
    
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const mat = new THREE.PointsMaterial({
        color: 0x8899bb,
        size: 0.15,
        transparent: true,
        opacity: 0.4,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    });
    
    const rain = new THREE.Points(geom, mat);
    rain.visible = false; // 默认隐藏, 仅暴风雨时显示
    state.scene.add(rain);
    state._rain = { points: rain, velocities };
}

function updateRain(intensity) {
    if (!state._rain) return;
    const { points, velocities } = state._rain;
    
    if (intensity <= 0.05) {
        points.visible = false;
        return;
    }
    points.visible = true;
    points.material.opacity = Math.min(0.6, intensity * 0.6);
    
    const pos = points.geometry.attributes.position;
    for (let i = 0; i < velocities.length; i++) {
        let y = pos.getY(i) - velocities[i] * (0.5 + intensity);
        if (y < -1) {
            y = 50 + Math.random() * 10;
            pos.setX(i, (Math.random() - 0.5) * 120);
            pos.setZ(i, (Math.random() - 0.5) * 120);
        }
        // 风偏移
        pos.setX(i, pos.getX(i) + intensity * 0.05);
        pos.setY(i, y);
    }
    pos.needsUpdate = true;
}

// ==================== 海鸥粒子群 ====================

function createSeagullFlock() {
    const COUNT = 24;
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    const velocities = [];
    
    for (let i = 0; i < COUNT; i++) {
        positions[i * 3]     = (Math.random() - 0.5) * 60;
        positions[i * 3 + 1] = 15 + Math.random() * 20;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 60;
        velocities.push({
            vx: (Math.random() - 0.5) * 0.06,
            vy: (Math.random() - 0.5) * 0.01,
            vz: (Math.random() - 0.5) * 0.06,
            phase: Math.random() * Math.PI * 2,
        });
    }
    
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // V 字形海鸥纹理 (canvas)
    const canvas = document.createElement('canvas');
    canvas.width = 32; canvas.height = 32;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(4, 16);
    ctx.quadraticCurveTo(16, 4, 28, 16);
    ctx.stroke();
    const tex = new THREE.CanvasTexture(canvas);
    
    const mat = new THREE.PointsMaterial({
        size: 2.5,
        map: tex,
        transparent: true,
        opacity: 0.9,
        depthWrite: false,
        sizeAttenuation: true,
    });
    
    const points = new THREE.Points(geom, mat);
    state.scene.add(points);
    state._seagulls = { points, velocities };
}

function updateSeagullFlock(time) {
    if (!state._seagulls) return;
    const { points, velocities } = state._seagulls;
    const pos = points.geometry.attributes.position;
    
    for (let i = 0; i < velocities.length; i++) {
        const v = velocities[i];
        let x = pos.getX(i) + v.vx;
        let y = pos.getY(i) + v.vy + Math.sin(time * 2.0 + v.phase) * 0.02;
        let z = pos.getZ(i) + v.vz;
        
        // 边界反弹 (围绕船附近)
        if (Math.abs(x) > 60) v.vx *= -1;
        if (y > 35) v.vy = -Math.abs(v.vy);
        if (y < 10) v.vy = Math.abs(v.vy);
        if (Math.abs(z) > 60) v.vz *= -1;
        
        // 微扰 + 聚集倾向
        v.vx += (Math.random() - 0.5) * 0.003 - x * 0.00003;
        v.vz += (Math.random() - 0.5) * 0.003 - z * 0.00003;
        
        pos.setXYZ(i, x, y, z);
    }
    pos.needsUpdate = true;
}

// ==================== 航道浮标 (IALA Maritime Buoyage System) ====================

function createNavigationBuoys() {
    const buoys = [
        // 左舷标 (红色, 圆柱形 — IALA Region A)
        { x: -20, z: -35, color: 0xcc2222, shape: 'can', light: 0xff0000, label: 'P1' },
        { x: -25, z: -60, color: 0xcc2222, shape: 'can', light: 0xff0000, label: 'P3' },
        // 右舷标 (绿色, 锥形)
        { x: 15, z: -35, color: 0x22aa44, shape: 'cone', light: 0x00ff00, label: 'S2' },
        { x: 20, z: -60, color: 0x22aa44, shape: 'cone', light: 0x00ff00, label: 'S4' },
        // 安全水域标 (红白竖条)
        { x: 0, z: -90, color: 0xffffff, shape: 'sphere', light: 0xffffff, label: 'FW' },
    ];
    
    state._buoys = [];
    
    buoys.forEach(b => {
        const group = new THREE.Group();
        
        let geom;
        if (b.shape === 'can') {
            geom = new THREE.CylinderGeometry(0.6, 0.6, 2.0, 8);
        } else if (b.shape === 'cone') {
            geom = new THREE.ConeGeometry(0.6, 2.0, 8);
        } else {
            geom = new THREE.SphereGeometry(0.7, 8, 8);
        }
        
        const mat = new THREE.MeshPhongMaterial({ color: b.color, shininess: 60 });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.position.y = 0.5;
        mesh.castShadow = true;
        group.add(mesh);
        
        // 浮标灯
        const light = new THREE.PointLight(b.light, 1.5, 10);
        light.position.set(0, 2.0, 0);
        group.add(light);
        const glow = new THREE.Mesh(
            new THREE.SphereGeometry(0.12, 6, 6),
            new THREE.MeshBasicMaterial({ color: b.light })
        );
        glow.position.copy(light.position);
        group.add(glow);
        
        // 标签
        const label = createFloatingLabel(b.label, b.color,
            new THREE.Vector3(b.x, 3.5, b.z));
        state.scene.add(label);
        
        group.position.set(b.x, 0, b.z);
        state.scene.add(group);
        state._buoys.push({ group, light, glow, phase: Math.random() * Math.PI * 2 });
    });
}

// ==================== 灯塔 ====================

function createLighthouse() {
    const group = new THREE.Group();
    
    // 基座 (岩石)
    const rockGeom = new THREE.DodecahedronGeometry(5, 1);
    const rock = new THREE.Mesh(rockGeom, new THREE.MeshPhongMaterial({
        color: 0x4a4a3a, shininess: 10,
    }));
    rock.position.y = 1.5;
    rock.scale.set(1, 0.5, 1);
    group.add(rock);
    
    // 塔身 (白色圆锥台)
    const towerGeom = new THREE.CylinderGeometry(1.2, 2.0, 18, 8);
    const tower = new THREE.Mesh(towerGeom, new THREE.MeshPhongMaterial({
        color: 0xf5f5dc, shininess: 30,
    }));
    tower.position.y = 12;
    tower.castShadow = true;
    group.add(tower);
    
    // 红色条纹
    const stripe = new THREE.Mesh(
        new THREE.CylinderGeometry(1.35, 1.65, 3, 8),
        new THREE.MeshPhongMaterial({ color: 0xcc3333 })
    );
    stripe.position.y = 8;
    group.add(stripe);
    
    // 灯室
    const lanternGeom = new THREE.CylinderGeometry(1.5, 1.3, 2, 8);
    const lantern = new THREE.Mesh(lanternGeom, new THREE.MeshPhongMaterial({
        color: 0x222222, shininess: 80,
    }));
    lantern.position.y = 22;
    group.add(lantern);
    
    // 灯光
    const light = new THREE.PointLight(0xffffcc, 5, 150);
    light.position.y = 22;
    group.add(light);
    
    const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.8, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xffffcc })
    );
    glow.position.y = 22;
    group.add(glow);
    
    group.position.set(-80, 0, -120);
    state.scene.add(group);
    state._lighthouse = { group, light, glow };
}

// ==================== 3D 指北标记 ====================

function createCompassRose3D() {
    // 在场景中放置一个方位指示器 (远处地平线上)
    const group = new THREE.Group();
    
    // 北方标记 (红色箭头)
    const arrowGeom = new THREE.ConeGeometry(1.5, 5, 3);
    const northArrow = new THREE.Mesh(arrowGeom, new THREE.MeshBasicMaterial({ color: 0xff4444 }));
    northArrow.position.set(0, 2, -200);
    group.add(northArrow);
    
    const northLabel = createFloatingLabel('N', 0xff4444, new THREE.Vector3(0, 8, -200));
    group.add(northLabel);
    
    // E/S/W 标记
    const dirs = [
        { label: 'E', pos: [200, 2, 0], color: 0xaaaaaa },
        { label: 'S', pos: [0, 2, 200], color: 0xaaaaaa },
        { label: 'W', pos: [-200, 2, 0], color: 0xaaaaaa },
    ];
    dirs.forEach(d => {
        const marker = new THREE.Mesh(
            new THREE.ConeGeometry(1, 3, 3),
            new THREE.MeshBasicMaterial({ color: d.color, transparent: true, opacity: 0.5 })
        );
        marker.position.set(...d.pos);
        group.add(marker);
        
        const label = createFloatingLabel(d.label, d.color,
            new THREE.Vector3(d.pos[0], 8, d.pos[2]));
        group.add(label);
    });
    
    state.scene.add(group);
}

// ==================== 锚链可视化 ====================

function createAnchorChain() {
    if (!state.boatMesh) return;
    
    // 锚 (简化几何体)
    const anchorGroup = new THREE.Group();
    
    // 锚体
    const anchorGeo = new THREE.CylinderGeometry(0.15, 0.3, 1.5, 6);
    const anchorMat = new THREE.MeshStandardMaterial({
        color: 0x333333, metalness: 0.9, roughness: 0.4,
    });
    const anchorBody = new THREE.Mesh(anchorGeo, anchorMat);
    anchorGroup.add(anchorBody);
    
    // 锚爪 (两个弯曲)
    const clawGeo = new THREE.TorusGeometry(0.5, 0.08, 6, 8, Math.PI * 0.6);
    const claw1 = new THREE.Mesh(clawGeo, anchorMat);
    claw1.position.set(0, -0.7, 0);
    claw1.rotation.z = -0.3;
    anchorGroup.add(claw1);
    const claw2 = new THREE.Mesh(clawGeo, anchorMat);
    claw2.position.set(0, -0.7, 0);
    claw2.rotation.z = 0.3;
    claw2.rotation.y = Math.PI;
    anchorGroup.add(claw2);
    
    // 锚杆顶部横杆
    const crossGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.0, 6);
    const crossBar = new THREE.Mesh(crossGeo, anchorMat);
    crossBar.rotation.z = Math.PI / 2;
    crossBar.position.y = 0.75;
    anchorGroup.add(crossBar);
    
    anchorGroup.position.set(0, -6, 10);
    anchorGroup.scale.set(0.8, 0.8, 0.8);
    
    // 锚链 (catenary curve using small spheres)
    const chainPoints = [];
    const CHAIN_SEGS = 20;
    for (let i = 0; i <= CHAIN_SEGS; i++) {
        const t = i / CHAIN_SEGS;
        const x = 0;
        const y = -t * 5.5 + Math.cosh((t - 0.5) * 2) * 0.3 - 0.3;
        const z = 10 - t * 0.5;
        chainPoints.push(new THREE.Vector3(x, y, z));
    }
    
    const chainCurve = new THREE.CatmullRomCurve3(chainPoints);
    const chainGeo = new THREE.TubeGeometry(chainCurve, 30, 0.04, 6, false);
    const chainMat = new THREE.MeshStandardMaterial({
        color: 0x444444, metalness: 0.85, roughness: 0.3,
    });
    const chainMesh = new THREE.Mesh(chainGeo, chainMat);
    
    state.boatMesh.add(chainMesh);
    state.boatMesh.add(anchorGroup);
    
    // 锚链链环标记 (每隔一段距离一个亮环)
    for (let i = 2; i < CHAIN_SEGS; i += 3) {
        const pt = chainCurve.getPoint(i / CHAIN_SEGS);
        const linkGeo = new THREE.TorusGeometry(0.08, 0.025, 6, 8);
        const linkMat = new THREE.MeshStandardMaterial({ color: 0xff4444, metalness: 0.7, roughness: 0.3 });
        const link = new THREE.Mesh(linkGeo, linkMat);
        link.position.copy(pt);
        link.rotation.x = Math.PI / 2;
        state.boatMesh.add(link);
    }
    
    state._anchorChain = { group: anchorGroup, chain: chainMesh };
    console.log('⚓ Anchor chain added');
}

// ==================== 吃水标尺 (Draught Marks) ====================

function createDraughtMarks() {
    if (!state.boatMesh) return;
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'transparent';
    ctx.clearRect(0, 0, 64, 512);
    
    // 绘制吃水刻度 (1m - 8m, 每0.5m一格)
    for (let d = 1; d <= 8; d += 0.5) {
        const y = 512 - (d / 8) * 480 - 16;
        const isWhole = d === Math.floor(d);
        ctx.fillStyle = '#ffffff';
        ctx.font = isWhole ? 'bold 28px monospace' : '16px monospace';
        ctx.textAlign = 'center';
        if (isWhole) {
            ctx.fillText(d.toString(), 32, y + 8);
        }
        // 水平刻度线
        ctx.fillRect(isWhole ? 4 : 16, y, isWhole ? 56 : 32, isWhole ? 3 : 2);
    }
    
    const tex = new THREE.CanvasTexture(canvas);
    tex.needsUpdate = true;
    const mat = new THREE.MeshBasicMaterial({
        map: tex,
        transparent: true,
        side: THREE.DoubleSide,
        depthWrite: false,
    });
    const geo = new THREE.PlaneGeometry(1.2, 8);
    
    // 左舷船首
    const markPF = new THREE.Mesh(geo, mat);
    markPF.position.set(-3.2, -2, 8);
    markPF.rotation.y = Math.PI / 2;
    state.boatMesh.add(markPF);
    
    // 右舷船首
    const markSF = new THREE.Mesh(geo, mat.clone());
    markSF.position.set(3.2, -2, 8);
    markSF.rotation.y = -Math.PI / 2;
    state.boatMesh.add(markSF);
    
    // 左舷船尾
    const markPA = new THREE.Mesh(geo, mat.clone());
    markPA.position.set(-3.2, -2, -8);
    markPA.rotation.y = Math.PI / 2;
    state.boatMesh.add(markPA);
    
    // 右舷船尾
    const markSA = new THREE.Mesh(geo, mat.clone());
    markSA.position.set(3.2, -2, -8);
    markSA.rotation.y = -Math.PI / 2;
    state.boatMesh.add(markSA);
    
    console.log('📏 Draught marks added (4 locations)');
}

// ==================== 舵叶 + 舭龙骨 (Rudder & Bilge Keels) ====================

function createRudderAndKeels() {
    if (!state.boatMesh) return;
    
    // 舵叶 (NACA翼型简化 — 用extruded shape)
    const rudderShape = new THREE.Shape();
    rudderShape.moveTo(0, 0);
    rudderShape.lineTo(0.6, 0.1);
    rudderShape.lineTo(1.2, 0.05);
    rudderShape.lineTo(1.5, 0);
    rudderShape.lineTo(1.2, -0.05);
    rudderShape.lineTo(0.6, -0.1);
    rudderShape.closePath();
    
    const rudderGeo = new THREE.ExtrudeGeometry(rudderShape, {
        steps: 1, depth: 2.5, bevelEnabled: false,
    });
    const rudderMat = new THREE.MeshStandardMaterial({
        color: 0xcc3333, metalness: 0.6, roughness: 0.4,
    });
    
    // 左舵
    const rudderP = new THREE.Mesh(rudderGeo, rudderMat);
    rudderP.position.set(-1.8, -3.5, -10.5);
    rudderP.rotation.x = Math.PI / 2;
    state.boatMesh.add(rudderP);
    
    // 右舵
    const rudderS = new THREE.Mesh(rudderGeo, rudderMat.clone());
    rudderS.position.set(1.8, -3.5, -10.5);
    rudderS.rotation.x = Math.PI / 2;
    state.boatMesh.add(rudderS);
    
    state._rudders = [rudderP, rudderS];
    
    // 舭龙骨 (bilge keels) — 船底两侧突起的稳定翼
    const keelShape = new THREE.Shape();
    keelShape.moveTo(0, 0);
    keelShape.lineTo(8, 0);
    keelShape.lineTo(7.5, -0.8);
    keelShape.lineTo(0.5, -0.8);
    keelShape.closePath();
    
    const keelGeo = new THREE.ExtrudeGeometry(keelShape, {
        steps: 1, depth: 0.08, bevelEnabled: false,
    });
    const keelMat = new THREE.MeshStandardMaterial({
        color: 0x8B0000, metalness: 0.5, roughness: 0.6,
    });
    
    // 左舭龙骨
    const keelP = new THREE.Mesh(keelGeo, keelMat);
    keelP.position.set(-3.0, -4.2, -4);
    keelP.rotation.y = Math.PI / 2;
    keelP.rotation.z = 0.3; // 倾斜 ~17°
    state.boatMesh.add(keelP);
    
    // 右舭龙骨
    const keelS = new THREE.Mesh(keelGeo, keelMat.clone());
    keelS.position.set(3.0, -4.2, -4);
    keelS.rotation.y = Math.PI / 2;
    keelS.rotation.z = -0.3;
    state.boatMesh.add(keelS);
    
    console.log('⚓ Rudders (2) + bilge keels (2) added');
}

// ==================== 船首侧推器隧道 ====================

function createBowThrusterTunnel() {
    if (!state.boatMesh) return;
    
    // 侧推器隧道 (横穿船体的圆管)
    const tunnelGeo = new THREE.CylinderGeometry(0.6, 0.6, 7, 16, 1, true);
    const tunnelMat = new THREE.MeshStandardMaterial({
        color: 0x222222,
        side: THREE.DoubleSide,
        metalness: 0.8,
        roughness: 0.3,
    });
    const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
    tunnel.rotation.z = Math.PI / 2;
    tunnel.position.set(0, -2.5, 7.5); // 船首水线以下
    state.boatMesh.add(tunnel);
    
    // 隧道口环 (左右两侧)
    const ringGeo = new THREE.TorusGeometry(0.65, 0.08, 8, 16);
    const ringMat = new THREE.MeshStandardMaterial({ color: 0x444444, metalness: 0.9, roughness: 0.2 });
    const ringP = new THREE.Mesh(ringGeo, ringMat);
    ringP.position.set(-3.5, -2.5, 7.5);
    ringP.rotation.y = Math.PI / 2;
    state.boatMesh.add(ringP);
    
    const ringS = new THREE.Mesh(ringGeo, ringMat.clone());
    ringS.position.set(3.5, -2.5, 7.5);
    ringS.rotation.y = Math.PI / 2;
    state.boatMesh.add(ringS);
    
    // 侧推器叶片 (在隧道中心)
    const bladeGeo = new THREE.BoxGeometry(0.1, 0.45, 0.15);
    const bladeMat = new THREE.MeshStandardMaterial({ color: 0xccaa00, metalness: 0.7 });
    const thrusterHub = new THREE.Group();
    for (let i = 0; i < 4; i++) {
        const blade = new THREE.Mesh(bladeGeo, bladeMat);
        blade.position.y = 0.25;
        const arm = new THREE.Group();
        arm.add(blade);
        arm.rotation.z = (Math.PI / 2) * i;
        thrusterHub.add(arm);
    }
    thrusterHub.rotation.z = Math.PI / 2;
    thrusterHub.position.set(0, -2.5, 7.5);
    state.boatMesh.add(thrusterHub);
    state._bowThruster = thrusterHub;
    
    console.log('🔄 Bow thruster tunnel added');
}

// ==================== 水下光束 (God Rays) ====================

function createUnderwaterLightShafts() {
    // 从水面透下的光束 (volumetric light 简化版)
    const shaftCount = 5;
    const shaftGroup = new THREE.Group();
    
    for (let i = 0; i < shaftCount; i++) {
        const height = 15 + Math.random() * 10;
        const geo = new THREE.ConeGeometry(1.5 + Math.random(), height, 4, 1, true);
        const mat = new THREE.MeshBasicMaterial({
            color: 0x44aacc,
            transparent: true,
            opacity: 0.04 + Math.random() * 0.03,
            side: THREE.DoubleSide,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        });
        const shaft = new THREE.Mesh(geo, mat);
        shaft.position.set(
            (Math.random() - 0.5) * 80,
            -height / 2,
            (Math.random() - 0.5) * 80
        );
        shaft.rotation.z = (Math.random() - 0.5) * 0.15;
        shaft.rotation.x = (Math.random() - 0.5) * 0.15;
        shaftGroup.add(shaft);
    }
    
    state.scene.add(shaftGroup);
    state._lightShafts = shaftGroup;
    console.log('🔦 Underwater light shafts added');
}

// ==================== 舱室内部 (Cabin Interiors) ====================

function createCabinInteriors() {
    if (!state.boatMesh) return;
    
    const cabinsGroup = new THREE.Group();
    cabinsGroup.name = 'CabinInteriors';
    state._cabins = {};
    
    // ─── 1. 驾驶台内部 (Bridge) ───
    const bridge = new THREE.Group();
    bridge.position.set(0, 9.5, 1.5);
    
    // 控制台 (前向U型)
    const consoleMat = new THREE.MeshStandardMaterial({ color: 0x222831, metalness: 0.6, roughness: 0.4 });
    const consoleGeo = new THREE.BoxGeometry(5.5, 0.4, 1.0);
    const console_ = new THREE.Mesh(consoleGeo, consoleMat);
    console_.position.set(0, -0.6, -1.8);
    bridge.add(console_);
    
    // 控制台显示器 (3 块发光屏)
    const screenMat = new THREE.MeshBasicMaterial({ color: 0x0066aa, transparent: true, opacity: 0.85 });
    for (let i = -1; i <= 1; i++) {
        const screen = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.85, 0.05), screenMat);
        screen.position.set(i * 1.6, -0.1, -2.3);
        screen.rotation.x = -0.2;
        bridge.add(screen);
    }
    
    // 舵 (helm wheel)
    const wheelGeo = new THREE.TorusGeometry(0.35, 0.04, 6, 16);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x6b3410, metalness: 0.3, roughness: 0.6 });
    const wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.position.set(0, -0.3, -1.5);
    wheel.rotation.x = Math.PI / 2;
    bridge.add(wheel);
    state._helm = wheel;
    
    // 船长椅
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x111418, metalness: 0.2, roughness: 0.8 });
    const chair = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.5, 0.6), chairMat);
    chair.position.set(0, -0.5, 0.3);
    bridge.add(chair);
    const chairBack = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.8, 0.15), chairMat);
    chairBack.position.set(0, 0.2, 0.6);
    bridge.add(chairBack);
    
    // 雷达屏 (悬挂)
    const radarGeo = new THREE.CircleGeometry(0.4, 24);
    const radarMat = new THREE.MeshBasicMaterial({ color: 0x00ff66, transparent: true, opacity: 0.7 });
    const radarScreen = new THREE.Mesh(radarGeo, radarMat);
    radarScreen.position.set(2.0, 0.4, -2.4);
    radarScreen.rotation.y = -0.3;
    bridge.add(radarScreen);
    state._bridgeRadarScreen = radarScreen;
    
    // 顶灯
    const ceilingLight = new THREE.PointLight(0xfff0c4, 0.6, 8);
    ceilingLight.position.set(0, 1.4, -0.5);
    bridge.add(ceilingLight);
    
    cabinsGroup.add(bridge);
    state._cabins.bridge = bridge;
    
    // ─── 2. 机舱 (Engine Room) ───
    const engine = new THREE.Group();
    engine.position.set(0, 3.0, 9.0);
    
    // 主机机体 (双主机)
    const enbodyMat = new THREE.MeshStandardMaterial({ color: 0x2c5530, metalness: 0.7, roughness: 0.3 });
    for (let s = -1; s <= 1; s += 2) {
        const block = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.8, 3.6), enbodyMat);
        block.position.set(s * 1.4, 0, 0);
        engine.add(block);
        
        // 6 缸缸盖
        for (let c = 0; c < 6; c++) {
            const head = new THREE.Mesh(
                new THREE.CylinderGeometry(0.3, 0.3, 0.5, 12),
                new THREE.MeshStandardMaterial({ color: 0x3a4a3a, metalness: 0.8, roughness: 0.3 })
            );
            head.position.set(s * 1.4, 1.15, -1.5 + c * 0.6);
            engine.add(head);
            
            // 排气歧管
            const pipe = new THREE.Mesh(
                new THREE.TorusGeometry(0.18, 0.06, 6, 8, Math.PI),
                new THREE.MeshStandardMaterial({ color: 0xaa4422, emissive: 0x441100, emissiveIntensity: 0.4, metalness: 0.5 })
            );
            pipe.position.set(s * 1.6, 1.5, -1.5 + c * 0.6);
            pipe.rotation.z = Math.PI / 2 * s;
            engine.add(pipe);
        }
        
        // 涡轮增压器
        const turbo = new THREE.Mesh(
            new THREE.CylinderGeometry(0.5, 0.4, 0.6, 12),
            new THREE.MeshStandardMaterial({ color: 0x666666, metalness: 0.9, roughness: 0.2 })
        );
        turbo.position.set(s * 1.6, 1.2, 2.2);
        turbo.rotation.x = Math.PI / 2;
        engine.add(turbo);
        state._cabins['turbo_' + s] = turbo;
    }
    
    // 控制台
    const ctrlPanel = new THREE.Mesh(
        new THREE.BoxGeometry(2.5, 1.5, 0.3),
        new THREE.MeshStandardMaterial({ color: 0x1a1a2e, metalness: 0.3, roughness: 0.6 })
    );
    ctrlPanel.position.set(0, 0.5, -2.5);
    engine.add(ctrlPanel);
    
    // 仪表盘灯 (一排小光点)
    for (let i = 0; i < 8; i++) {
        const led = new THREE.Mesh(
            new THREE.SphereGeometry(0.03, 6, 6),
            new THREE.MeshBasicMaterial({ color: i % 3 === 0 ? 0x00ff00 : 0xffaa00 })
        );
        led.position.set(-1.0 + i * 0.28, 0.8, -2.3);
        engine.add(led);
    }
    state._engineLEDs = engine.children.slice(-8);
    
    // 机舱顶灯 (黄色工业光)
    const engLight = new THREE.PointLight(0xffe080, 0.5, 12);
    engLight.position.set(0, 2.5, 0);
    engine.add(engLight);
    
    // 管道 (蓝色冷却水/红色燃油/黄色润滑油)
    const pipeColors = [0x0066cc, 0xcc3333, 0xddaa00];
    pipeColors.forEach((color, idx) => {
        const pipe = new THREE.Mesh(
            new THREE.CylinderGeometry(0.05, 0.05, 6, 6),
            new THREE.MeshStandardMaterial({ color, metalness: 0.6, roughness: 0.4 })
        );
        pipe.position.set(-2.5 + idx * 0.2, 1.8, 0);
        pipe.rotation.x = Math.PI / 2;
        engine.add(pipe);
    });
    
    cabinsGroup.add(engine);
    state._cabins.engine = engine;
    
    // ─── 3. 货舱 (Cargo Hold) ───
    const cargo = new THREE.Group();
    cargo.position.set(0, 3.0, -2.0);
    
    // 货舱底板
    const holdFloor = new THREE.Mesh(
        new THREE.BoxGeometry(8, 0.15, 16),
        new THREE.MeshStandardMaterial({ color: 0x3a3a3a, metalness: 0.4, roughness: 0.7 })
    );
    holdFloor.position.set(0, -2.5, 0);
    cargo.add(holdFloor);
    
    // 集装箱内部展示 (3排2列堆叠)
    const containerColors = [0xc0392b, 0x2980b9, 0x27ae60, 0xf39c12, 0x8e44ad, 0x16a085];
    let cIdx = 0;
    for (let row = 0; row < 3; row++) {
        for (let col = -1; col <= 1; col += 2) {
            for (let layer = 0; layer < 2; layer++) {
                const cmat = new THREE.MeshStandardMaterial({
                    color: containerColors[cIdx % containerColors.length],
                    metalness: 0.3, roughness: 0.7,
                });
                const cont = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.4, 4.5), cmat);
                cont.position.set(col * 1.2, -1.6 + layer * 1.5, -5 + row * 5);
                cargo.add(cont);
                cIdx++;
            }
        }
    }
    
    // 货舱照明
    const cargoLight = new THREE.PointLight(0xffe0b0, 0.7, 25);
    cargoLight.position.set(0, 4, 0);
    cargo.add(cargoLight);
    
    cabinsGroup.add(cargo);
    state._cabins.cargo = cargo;
    
    // ─── 4. 船员舱 (Crew Accommodation) ───
    const crew = new THREE.Group();
    crew.position.set(2.5, 7.5, 5.5);
    
    // 床 (双层)
    const bedMat = new THREE.MeshStandardMaterial({ color: 0xddccaa, roughness: 0.8 });
    for (let i = 0; i < 2; i++) {
        const bed = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.18, 1.9), bedMat);
        bed.position.set(0, -0.5 + i * 0.9, 0);
        crew.add(bed);
        const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.08, 0.4), 
            new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95 }));
        pillow.position.set(0, -0.4 + i * 0.9, -0.7);
        crew.add(pillow);
    }
    
    // 桌子
    const desk = new THREE.Mesh(
        new THREE.BoxGeometry(1.2, 0.05, 0.5),
        new THREE.MeshStandardMaterial({ color: 0x6b4226, roughness: 0.6 })
    );
    desk.position.set(1.0, -0.2, 0.5);
    crew.add(desk);
    
    // 灯
    const cabinLight = new THREE.PointLight(0xffe8c0, 0.4, 5);
    cabinLight.position.set(0, 0.8, 0);
    crew.add(cabinLight);
    
    cabinsGroup.add(crew);
    state._cabins.crew = crew;
    
    // ─── 5. 厨房 (Galley) ───
    const galley = new THREE.Group();
    galley.position.set(-2.5, 7.0, 6.0);
    
    // 灶台 (不锈钢)
    const stoveMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.9, roughness: 0.2 });
    const stove = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.85, 0.7), stoveMat);
    stove.position.set(0, -0.5, 0);
    galley.add(stove);
    
    // 4 个灶眼
    for (let r = 0; r < 2; r++) {
        for (let c = 0; c < 2; c++) {
            const burner = new THREE.Mesh(
                new THREE.CylinderGeometry(0.15, 0.15, 0.05, 12),
                new THREE.MeshStandardMaterial({ color: 0x333333, emissive: 0xff4400, emissiveIntensity: 0.5 })
            );
            burner.position.set(-0.4 + c * 0.8, -0.05, -0.2 + r * 0.4);
            galley.add(burner);
        }
    }
    
    // 抽油烟机
    const hood = new THREE.Mesh(
        new THREE.BoxGeometry(1.5, 0.4, 0.7),
        stoveMat
    );
    hood.position.set(0, 0.6, 0);
    galley.add(hood);
    
    // 厨房灯
    const galleyLight = new THREE.PointLight(0xffffff, 0.5, 6);
    galleyLight.position.set(0, 1.2, 0);
    galley.add(galleyLight);
    
    cabinsGroup.add(galley);
    state._cabins.galley = galley;
    
    // ─── 6. 控制中心 (Engine Control Room) ───
    const ecr = new THREE.Group();
    ecr.position.set(2.0, 5.0, 8.5);
    
    // 控制台 (大型)
    const ecrConsole = new THREE.Mesh(
        new THREE.BoxGeometry(2.5, 0.5, 0.8),
        new THREE.MeshStandardMaterial({ color: 0x1a2030, metalness: 0.4, roughness: 0.5 })
    );
    ecrConsole.position.set(0, -0.3, 0);
    ecr.add(ecrConsole);
    
    // 大屏幕墙 (4 块)
    for (let i = 0; i < 4; i++) {
        const screen = new THREE.Mesh(
            new THREE.BoxGeometry(0.55, 0.4, 0.04),
            new THREE.MeshBasicMaterial({ color: i === 1 ? 0x00aa44 : 0x0066bb, transparent: true, opacity: 0.85 })
        );
        screen.position.set(-0.85 + i * 0.55, 0.6, -0.55);
        ecr.add(screen);
    }
    state._ecrScreens = ecr.children.slice(-4);
    
    // 工程师椅
    const ecrChair = new THREE.Mesh(
        new THREE.BoxGeometry(0.5, 0.4, 0.5),
        new THREE.MeshStandardMaterial({ color: 0x111418, roughness: 0.8 })
    );
    ecrChair.position.set(0, -0.5, 0.7);
    ecr.add(ecrChair);
    
    // 控制中心灯
    const ecrLight = new THREE.PointLight(0xb0d0ff, 0.4, 5);
    ecrLight.position.set(0, 1.0, 0);
    ecr.add(ecrLight);
    
    cabinsGroup.add(ecr);
    state._cabins.ecr = ecr;
    
    // 默认隐藏 (只在进入舱室时显示)
    cabinsGroup.visible = false;
    state.boatMesh.add(cabinsGroup);
    state._cabinsGroup = cabinsGroup;
    
    console.log('🏠 Cabin interiors created (6 cabins)');
}

window.toggleCabinInteriors = function(visible) {
    if (state._cabinsGroup) {
        state._cabinsGroup.visible = visible;
    }
};

// ==================== 船旗 (中国国旗) ====================

function createShipFlag() {
    if (!state.boatMesh) return;
    
    // 旗杆
    const poleGeom = new THREE.CylinderGeometry(0.03, 0.03, 3, 6);
    const poleMat = new THREE.MeshPhongMaterial({ color: 0xcccccc, shininess: 80 });
    const pole = new THREE.Mesh(poleGeom, poleMat);
    pole.position.set(0, 9.8, -0.5); // 驾驶台顶部
    state.boatMesh.add(pole);
    
    // 旗帜 (平面 + 顶点动画)
    const flagW = 1.5, flagH = 1.0;
    const flagGeom = new THREE.PlaneGeometry(flagW, flagH, 12, 6);
    
    // 红色旗帜 canvas
    const canvas = document.createElement('canvas');
    canvas.width = 128; canvas.height = 85;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#de2910';
    ctx.fillRect(0, 0, 128, 85);
    // 简化五星
    ctx.fillStyle = '#ffde00';
    ctx.font = 'bold 24px serif';
    ctx.fillText('★', 15, 30);
    ctx.font = '10px serif';
    ctx.fillText('★', 40, 15);
    ctx.fillText('★', 48, 25);
    ctx.fillText('★', 48, 38);
    ctx.fillText('★', 40, 48);
    
    const flagTex = new THREE.CanvasTexture(canvas);
    const flagMat = new THREE.MeshPhongMaterial({
        map: flagTex,
        side: THREE.DoubleSide,
        transparent: true,
    });
    
    const flagMesh = new THREE.Mesh(flagGeom, flagMat);
    flagMesh.position.set(flagW / 2 + 0.05, 10.5, -0.5);
    state.boatMesh.add(flagMesh);
    state._flag = flagMesh;
}

function updateFlag(time) {
    if (!state._flag) return;
    const pos = state._flag.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        // 波浪形飘动 (越远离旗杆幅度越大)
        const wave = Math.sin(time * 3.0 + x * 4.0) * 0.08 * (x + 0.75);
        pos.setZ(i, wave);
    }
    pos.needsUpdate = true;
    state._flag.geometry.computeVertexNormals();
}

// ==================== 水下螺旋桨 ====================

function createPropellers() {
    if (!state.boatMesh) return;
    
    const propGroup = new THREE.Group();
    
    // WPC 双体船: 左右各一个螺旋桨
    [-2.5, 2.5].forEach(offsetX => {
        const bladeGroup = new THREE.Group();
        
        // 4 叶螺旋桨
        for (let i = 0; i < 4; i++) {
            const bladeShape = new THREE.Shape();
            bladeShape.moveTo(0, 0);
            bladeShape.quadraticCurveTo(0.15, 0.3, 0.08, 0.7);
            bladeShape.quadraticCurveTo(0, 0.75, -0.08, 0.7);
            bladeShape.quadraticCurveTo(-0.15, 0.3, 0, 0);
            
            const bladeGeom = new THREE.ExtrudeGeometry(bladeShape, {
                depth: 0.04, bevelEnabled: false,
            });
            const blade = new THREE.Mesh(bladeGeom, new THREE.MeshPhongMaterial({
                color: 0xb8860b, shininess: 80, specular: 0xffcc44,
            }));
            blade.rotation.z = (i * Math.PI) / 2;
            bladeGroup.add(blade);
        }
        
        // 螺旋桨轴
        const shaft = new THREE.Mesh(
            new THREE.CylinderGeometry(0.06, 0.06, 1.5, 8),
            new THREE.MeshPhongMaterial({ color: 0x666666, shininess: 60 })
        );
        shaft.rotation.x = Math.PI / 2;
        shaft.position.z = -0.75;
        bladeGroup.add(shaft);
        
        bladeGroup.position.set(offsetX, -2.0, 5.5);
        bladeGroup.rotation.x = Math.PI / 2; // 面朝后
        propGroup.add(bladeGroup);
    });
    
    state.boatMesh.add(propGroup);
    state._propellers = propGroup;
}

function updatePropellers(rpm) {
    if (!state._propellers) return;
    const rotSpeed = (rpm / 720) * 0.15; // 归一化旋转速度
    state._propellers.children.forEach(prop => {
        // 每个 prop 的第一个 children 组是叶片组
        prop.children.forEach(child => {
            if (child.rotation) child.rotation.z += rotSpeed;
        });
        prop.rotation.z += rotSpeed;
    });
}

// ==================== 海面网格参考线 ====================

function createSeaGrid() {
    const size = 200, divisions = 20;
    const gridHelper = new THREE.GridHelper(size, divisions, 0x1a3a5c, 0x0d2035);
    gridHelper.position.y = -0.3;
    gridHelper.material.transparent = true;
    gridHelper.material.opacity = 0.15;
    gridHelper.material.depthWrite = false;
    state.scene.add(gridHelper);
    
    // 距离环 (每 25m 一个圆环)
    for (let r = 25; r <= 100; r += 25) {
        const ringGeom = new THREE.RingGeometry(r - 0.1, r + 0.1, 64);
        ringGeom.rotateX(-Math.PI / 2);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x1a4a6c,
            transparent: true,
            opacity: 0.08,
            side: THREE.DoubleSide,
        });
        const ring = new THREE.Mesh(ringGeom, ringMat);
        ring.position.y = -0.2;
        state.scene.add(ring);
    }
}

// ==================== 海底地形 ====================

function createSeaFloor() {
    const size = 400, segments = 80;
    const geom = new THREE.PlaneGeometry(size, size, segments, segments);
    geom.rotateX(-Math.PI / 2);
    
    // 程序化地形高度
    const pos = geom.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        const z = pos.getZ(i);
        // 多层 Perlin-like 高度 (简化 sin 叠加)
        let h = -35; // 基础深度
        h += Math.sin(x * 0.02) * Math.cos(z * 0.025) * 5.0;
        h += Math.sin(x * 0.06 + 1.3) * Math.cos(z * 0.08 + 0.7) * 2.0;
        h += Math.sin(x * 0.15 + 3.1) * Math.cos(z * 0.12 + 2.2) * 0.6;
        // 沟壑 (中央海沟)
        const dist = Math.abs(x * 0.8 + z * 0.2);
        if (dist < 15) h -= (15 - dist) * 0.8;
        pos.setY(i, h);
    }
    geom.computeVertexNormals();
    
    const mat = new THREE.ShaderMaterial({
        uniforms: {
            deepColor: { value: new THREE.Color(0x0a1628) },
            shallowColor: { value: new THREE.Color(0x1a3a5c) },
            sandColor: { value: new THREE.Color(0x4a6741) },
            minDepth: { value: -45.0 },
            maxDepth: { value: -25.0 },
            time: { value: 0 },
        },
        vertexShader: `
            varying float vDepth;
            varying vec3 vNormal;
            varying vec2 vUv;
            void main() {
                vDepth = position.y;
                vNormal = normalize(normalMatrix * normal);
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 deepColor;
            uniform vec3 shallowColor;
            uniform vec3 sandColor;
            uniform float minDepth;
            uniform float maxDepth;
            uniform float time;
            varying float vDepth;
            varying vec3 vNormal;
            varying vec2 vUv;
            
            // 水下焦散 (caustics)
            float caustic(vec2 uv) {
                float c = 0.0;
                vec2 p = uv * 8.0;
                c += sin(p.x * 2.3 + time * 0.8) * sin(p.y * 2.7 + time * 0.6) * 0.5;
                c += sin(p.x * 3.1 - time * 0.5 + p.y * 1.4) * 0.3;
                c += sin(p.y * 4.2 + time * 1.1 + p.x * 0.8) * 0.2;
                return max(c, 0.0);
            }
            
            void main() {
                float t = clamp((vDepth - minDepth) / (maxDepth - minDepth), 0.0, 1.0);
                vec3 baseColor = mix(deepColor, shallowColor, t);
                if (t > 0.7) baseColor = mix(baseColor, sandColor, (t - 0.7) / 0.3);
                float light = dot(vNormal, vec3(0.0, 1.0, 0.0)) * 0.5 + 0.5;
                // 焦散光斑 (浅处更明显)
                float causticsVal = caustic(vUv) * t * 0.35;
                baseColor += vec3(0.1, 0.2, 0.3) * causticsVal;
                gl_FragColor = vec4(baseColor * light * 0.6, 0.85);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide,
    });
    
    const mesh = new THREE.Mesh(geom, mat);
    state.scene.add(mesh);
    state._seaFloor = mesh;
}

// ==================== 测深仪可视化 ====================

function createDepthSounder() {
    // 声纳锥形扫描线 (船底向下)
    const coneGeom = new THREE.ConeGeometry(8, 30, 16, 1, true);
    coneGeom.rotateX(Math.PI); // 尖头朝上
    
    const coneMat = new THREE.ShaderMaterial({
        uniforms: {
            time:  { value: 0 },
            color: { value: new THREE.Color(0x00ccff) },
        },
        vertexShader: /* glsl */ `
            varying float vY;
            varying vec2 vUv;
            void main() {
                vY = position.y;
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: /* glsl */ `
            uniform float time;
            uniform vec3 color;
            varying float vY;
            varying vec2 vUv;
            void main() {
                // 扫描环 (从上到下脉冲)
                float pulse = fract(time * 0.5);
                float ring = smoothstep(pulse - 0.05, pulse, vUv.y) - smoothstep(pulse, pulse + 0.05, vUv.y);
                float baseAlpha = 0.03 + ring * 0.15;
                // 越深越透明
                float depthFade = 1.0 - vUv.y;
                gl_FragColor = vec4(color, baseAlpha * depthFade);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    });
    
    const cone = new THREE.Mesh(coneGeom, coneMat);
    cone.position.set(0, -16, 0);
    cone.frustumCulled = false;
    
    state.scene.add(cone);
    state._depthSounder = cone;
}

// ==================== 语义标签 ====================

function createSemanticLabels() {
    // 示例语义标签
    const labels = [
        { id: 'engine-room', name: '机舱', position: [0, 1, 0] },
        { id: 'bridge', name: '驾驶台', position: [0, 3, 2] },
        { id: 'cargo-hold', name: '货舱', position: [0, 0, -5] },
        { id: 'left-hull', name: '左船体', position: [-4, 0, 0] },
        { id: 'right-hull', name: '右船体', position: [4, 0, 0] },
    ];
    
    state.semanticLabels = labels;
    console.log('✅ Semantic labels created:', labels.length);
}

// ==================== WebSocket 连接 ====================

function connectWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    console.log('📡 Connecting to WebSocket:', wsUrl);
    
    state.ws = new WebSocket(wsUrl);
    
    state.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        updateConnectionStatus('connected');
        
        // 订阅数据
        state.ws.send(JSON.stringify({
            action: 'subscribe',
            channel: 'all'
        }));
    };
    
    state.ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        updateConnectionStatus('disconnected');
        
        // 自动重连
        setTimeout(connectWebSocket, 3000);
    };
    
    state.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    state.ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            if (message.type === 'data_update') {
                state.latestData = message.data;
                // 同步 own_ship 到 externalSync
                if (message.data.own_ship) {
                    state.externalSync.ownShip = message.data.own_ship;
                }
                updateDigitalTwin(message.data);
            }
        } catch (e) {
            console.error('Error parsing message:', e);
        }
    };
}

// ==================== 数字孪生更新 ====================

function updateDigitalTwin(data) {
    // 更新船体状态 (基于主机数据) — 不覆盖 animate() 中的波浪运动
    if (data.engine && state.boatMesh) {
        // 储存 RPM 用于 animate 高频振动
        state._currentRPM = data.engine.rpm || 0;
    }
    
    // 同步 AIS 目标到 3D 场景
    if (data.ais_targets) {
        syncAISTargets3D(data.ais_targets);
    }
    
    // 更新 UI
    updateUI(data);
}

// ==================== AIS 目标 3D 同步 ====================

function syncAISTargets3D(aisTargets) {
    if (!state.scene) return;
    
    // 初始化 AIS 3D 标记容器
    if (!state._ais3DMarkers) state._ais3DMarkers = {};
    
    const activeMMSIs = new Set();
    
    Object.entries(aisTargets).forEach(([mmsi, target]) => {
        activeMMSIs.add(mmsi);
        const scenePos = geoToScenePosition(target);
        
        if (state._ais3DMarkers[mmsi]) {
            // 更新已有标记位置 (平滑插值)
            const marker = state._ais3DMarkers[mmsi];
            marker.mesh.position.lerp(scenePos, 0.1);
            // 更新航向旋转
            if (target.course != null) {
                marker.mesh.rotation.y = -target.course * Math.PI / 180;
            }
        } else {
            // 创建新的 AIS 目标 3D 标记 — 简化小船模型
            const group = new THREE.Group();
            
            // 船体 (小三角形指示器)
            const hullGeom = new THREE.ConeGeometry(1.2, 4, 4);
            hullGeom.rotateX(Math.PI / 2);
            const cpa = Number(target.cpa ?? 5);
            const hullColor = cpa < 0.5 ? 0xff4444 : cpa < 1.5 ? 0xffaa00 : 0x44aaff;
            const hullMesh = new THREE.Mesh(hullGeom, new THREE.MeshPhongMaterial({
                color: hullColor,
                emissive: hullColor,
                emissiveIntensity: 0.3,
            }));
            group.add(hullMesh);
            
            // CPA 危险圆环 (仅当 CPA < 2nm)
            if (cpa < 2.0) {
                const ringGeom = new THREE.RingGeometry(cpa * 3 + 1, cpa * 3 + 1.3, 32);
                ringGeom.rotateX(-Math.PI / 2);
                const ringMat = new THREE.MeshBasicMaterial({
                    color: hullColor,
                    transparent: true,
                    opacity: cpa < 0.5 ? 0.5 : 0.25,
                    side: THREE.DoubleSide,
                });
                group.add(new THREE.Mesh(ringGeom, ringMat));
            }
            
            // 预测航迹线 (前方 5 个点)
            if (target.course != null && target.speed != null) {
                const courseRad = (target.course ?? 0) * Math.PI / 180;
                const spd = (target.speed ?? 0);
                const predPoints = [];
                for (let p = 0; p <= 5; p++) {
                    const dist = p * spd * 0.3; // 预测距离
                    predPoints.push(new THREE.Vector3(
                        Math.sin(courseRad) * dist,
                        0.5,
                        -Math.cos(courseRad) * dist
                    ));
                }
                const predGeom = new THREE.BufferGeometry().setFromPoints(predPoints);
                const predLine = new THREE.Line(predGeom, new THREE.LineDashedMaterial({
                    color: hullColor,
                    dashSize: 1,
                    gapSize: 0.5,
                    transparent: true,
                    opacity: 0.5,
                }));
                predLine.computeLineDistances();
                group.add(predLine);
            }
            
            // 高度标记线 (从水面到船)
            const lineGeom = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0, -scenePos.y, 0),
                new THREE.Vector3(0, 0, 0),
            ]);
            const lineMat = new THREE.LineBasicMaterial({ color: hullColor, transparent: true, opacity: 0.3 });
            group.add(new THREE.Line(lineGeom, lineMat));
            
            group.position.copy(scenePos);
            if (target.course != null) {
                group.rotation.y = -target.course * Math.PI / 180;
            }
            
            state.scene.add(group);
            state._ais3DMarkers[mmsi] = { mesh: group, data: target };
        }
    });
    
    // 移除不再活跃的目标
    Object.keys(state._ais3DMarkers).forEach(mmsi => {
        if (!activeMMSIs.has(mmsi)) {
            state.scene.remove(state._ais3DMarkers[mmsi].mesh);
            delete state._ais3DMarkers[mmsi];
        }
    });
}

// ==================== 热力图渲染 ====================

function updateHeatmap(sensors) {
    // 热力图已禁用 — 不再破坏性修改船体材质颜色
    // 传感器数据在 UI 面板中展示即可
}

// ==================== UI 更新 ====================

function updateUI(data) {
    const mergedOwnShip = state.externalSync.ownShip;

    // 更新导航数据
    if (mergedOwnShip) {
        const navLatEl = document.getElementById('nav-lat');
        const navLonEl = document.getElementById('nav-lon');
        const navCourseEl = document.getElementById('nav-course');
        const navSpeedEl = document.getElementById('nav-speed');

        if (navLatEl && mergedOwnShip.latitude != null) navLatEl.textContent = Number(mergedOwnShip.latitude).toFixed(4);
        if (navLonEl && mergedOwnShip.longitude != null) navLonEl.textContent = Number(mergedOwnShip.longitude).toFixed(4);
        if (navCourseEl && mergedOwnShip.course != null) navCourseEl.textContent = `${Number(mergedOwnShip.course).toFixed(1)}°`;
        if (navSpeedEl && mergedOwnShip.speed != null) navSpeedEl.textContent = `${Number(mergedOwnShip.speed).toFixed(1)} kn`;
    } else if (data.sensors) {
        const gps = data.sensors['GPS-001'];
        if (gps) {
            // 这里可以从传感器数据更新
        }
    }
    
    // 更新主机数据
    if (data.engine) {
        const el = document.getElementById('eng-rpm');
        if (el) el.textContent = `${data.engine.rpm.toFixed(1)} RPM`;
        
        const loadEl = document.getElementById('eng-load');
        if (loadEl) loadEl.textContent = `${data.engine.load.toFixed(1)} %`;
    }
    
    // 更新 AIS 目标数
    if (data.ais_targets) {
        const countEl = document.getElementById('ais-count');
        if (countEl) countEl.textContent = Object.keys(data.ais_targets).length;
    }
    
    // 隐藏加载动画
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
}

function updateConnectionStatus(status) {
    const dot = document.getElementById('ws-status');
    const text = document.getElementById('ws-status-text');
    
    if (dot && text) {
        dot.className = `status-dot ${status}`;
        text.textContent = status === 'connected' ? '已连接' : '已断开';
    }
}

function normalizeExternalAlarm(alarm) {
    return {
        level: alarm.level || 'INFO',
        message: alarm.message || '外部告警',
        source: alarm.source || 'worldmonitor',
        timestamp: alarm.timestamp || new Date().toISOString(),
    };
}

function geoToScenePosition(target = {}) {
    const latitude = Number(target.latitude ?? target.lat ?? target.position?.latitude ?? 0);
    const longitude = Number(target.longitude ?? target.lng ?? target.position?.longitude ?? 0);
    const x = ((longitude % 1) - 0.5) * 20;
    const z = ((latitude % 1) - 0.5) * 20;
    return new THREE.Vector3(x, 1.4, z);
}

function clearFusionMarkers() {
    state.fusionMarkers.forEach(({ marker, label }) => {
        if (marker) {
            state.scene.remove(marker);
            marker.geometry.dispose();
            marker.material.dispose();
        }
        if (label) {
            state.scene.remove(label);
            label.material.map.dispose();
            label.material.dispose();
        }
    });
    state.fusionMarkers = [];
}

function renderFusionTracks(tracks = []) {
    if (!state.scene) return;

    clearFusionMarkers();

    tracks.slice(0, 10).forEach((track, index) => {
        const position = geoToScenePosition(track.position || track);
        const confidence = Number(track.confidence ?? 0.5);
        const color = confidence >= 0.8 ? 0x00e5ff : confidence >= 0.6 ? 0xffc107 : 0xff7043;
        const marker = new THREE.Mesh(
            new THREE.SphereGeometry(0.45 + confidence * 0.25, 16, 16),
            new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85 })
        );
        marker.position.copy(position);

        const label = createFloatingLabel(
            `FUS-${index + 1}\n${Math.round(confidence * 100)}%`,
            color,
            position.clone().add(new THREE.Vector3(0, 1.6, 0))
        );

        state.scene.add(marker);
        state.scene.add(label);
        state.fusionMarkers.push({ marker, label });
    });
}

function createFloatingLabel(text, color, position) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 128;
    ctx.fillStyle = 'rgba(8, 16, 28, 0.78)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
    ctx.font = 'bold 30px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const lines = String(text).split('\n');
    lines.forEach((line, idx) => {
        ctx.fillText(line, canvas.width / 2, 42 + idx * 32);
    });

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(material);
    sprite.position.copy(position);
    sprite.scale.set(6, 3, 1);
    return sprite;
}

// ==================== 摄像机预设 ====================

const CAMERA_PRESETS = {
    overview: { pos: [30, 20, 30], target: [0, 0, 0] },
    bridge:   { pos: [0, 8, 2], target: [0, 6, -20] },
    bow:      { pos: [0, 4, -18], target: [0, 2, -40] },
    stern:    { pos: [0, 6, 18], target: [0, 2, -5] },
    underwater: { pos: [12, -15, 12], target: [0, -30, 0] },
    top:      { pos: [0, 80, 0.1], target: [0, 0, 0] },
    // ── 舱内视角 ──
    'cabin-bridge':       { pos: [0, 9.8, 6.5], target: [0, 9.5, 1.0] },
    'cabin-engine':       { pos: [-2, 4.5, 12], target: [0, 3.0, 9.0] },
    'cabin-cargo':        { pos: [0, 6.5, -8], target: [0, 3.0, -2] },
    'cabin-crew':         { pos: [3.5, 7.5, 7], target: [0, 7.5, 5] },
    'cabin-galley':       { pos: [-3.5, 7.0, 8], target: [-1.0, 7.0, 6] },
    'cabin-control':      { pos: [2, 5.5, 10.5], target: [0, 5.0, 8.5] },
};

window.setCameraPreset = function(name) {
    const preset = CAMERA_PRESETS[name];
    if (!preset || !state.camera || !state.controls) return;
    
    const startPos = state.camera.position.clone();
    const startTarget = state.controls.target.clone();
    const endPos = new THREE.Vector3(...preset.pos);
    const endTarget = new THREE.Vector3(...preset.target);
    const duration = 800;
    const startTime = performance.now();
    
    function easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    function animateCamera(now) {
        const elapsed = now - startTime;
        const t = easeInOutCubic(Math.min(elapsed / duration, 1.0));
        state.camera.position.lerpVectors(startPos, endPos, t);
        state.controls.target.lerpVectors(startTarget, endTarget, t);
        state.controls.update();
        if (elapsed < duration) requestAnimationFrame(animateCamera);
    }
    requestAnimationFrame(animateCamera);
};

function focusOnCoordinates(target = {}) {
    if (!state.camera || !state.controls) return;

    const latitude = Number(target.latitude ?? target.lat ?? 0);
    const longitude = Number(target.longitude ?? target.lng ?? 0);
    const heading = Number(target.course ?? target.heading ?? 0);

    const relativeX = ((longitude % 1) - 0.5) * 20;
    const relativeZ = ((latitude % 1) - 0.5) * 20;
    const relativeY = 2 + Math.abs(Math.sin((heading * Math.PI) / 180)) * 4;

    const targetPosition = new THREE.Vector3(relativeX, relativeY, relativeZ);
    const cameraOffset = new THREE.Vector3(12, 8, 12);
    const nextCameraPosition = targetPosition.clone().add(cameraOffset);
    const startCameraPosition = state.camera.position.clone();
    const startTarget = state.controls.target.clone();
    const durationMs = 900;
    const startTime = performance.now();
    const token = ++state.cameraControl.animationToken;

    function animateFocus(now) {
        if (token !== state.cameraControl.animationToken) {
            return;
        }
        const progress = Math.min((now - startTime) / durationMs, 1);
        state.camera.position.lerpVectors(startCameraPosition, nextCameraPosition, progress);
        state.controls.target.lerpVectors(startTarget, targetPosition, progress);
        state.controls.update();

        if (progress < 1) {
            requestAnimationFrame(animateFocus);
        }
    }

    requestAnimationFrame(animateFocus);
}

function animateCameraTo(targetPosition, cameraPosition, durationMs = 900) {
    if (!state.camera || !state.controls) return;

    const startCameraPosition = state.camera.position.clone();
    const startTarget = state.controls.target.clone();
    const startTime = performance.now();
    const token = ++state.cameraControl.animationToken;

    function animateStep(now) {
        if (token !== state.cameraControl.animationToken) {
            return;
        }
        const progress = Math.min((now - startTime) / durationMs, 1);
        state.camera.position.lerpVectors(startCameraPosition, cameraPosition, progress);
        state.controls.target.lerpVectors(startTarget, targetPosition, progress);
        state.controls.update();
        if (progress < 1) {
            requestAnimationFrame(animateStep);
        }
    }

    requestAnimationFrame(animateStep);
}

function computeBridgeView() {
    const bridgeTarget = new THREE.Vector3(0, 2.8, 2.2);
    const bridgeCamera = new THREE.Vector3(8.5, 6.5, 14.5);
    return { target: bridgeTarget, camera: bridgeCamera };
}

function getSelectedTargetKey(target = {}) {
    return String(target.mmsi || target.id || `${target.latitude ?? target.lat}-${target.longitude ?? target.lng}`);
}

function getTargetLabel(target = {}) {
    return String(target.vessel_type || target.name || target.mmsi || target.id || 'UNSPECIFIED');
}

function getTargetScenePosition(target = {}) {
    const latitude = Number(target.latitude ?? target.lat ?? 0);
    const longitude = Number(target.longitude ?? target.lng ?? 0);
    const heading = Number(target.course ?? target.heading ?? 0);
    const relativeX = ((longitude % 1) - 0.5) * 20;
    const relativeZ = ((latitude % 1) - 0.5) * 20;
    const relativeY = 2 + Math.abs(Math.sin((heading * Math.PI) / 180)) * 4;
    return new THREE.Vector3(relativeX, relativeY, relativeZ);
}

function focusOnSelectedTarget() {
    if (!state.externalSync.selectedTarget) {
        return;
    }
    focusOnCoordinates(state.externalSync.selectedTarget);
    state.cameraControl.lastSelectedTargetKey = getSelectedTargetKey(state.externalSync.selectedTarget);
    state.cameraControl.lastAppliedAt = new Date().toISOString();
}

function setSelectedTarget(target = null, options = {}) {
    state.externalSync.selectedTarget = target;
    state.externalSync.source = options.source || (target ? 'bridge-operator' : state.externalSync.source);
    state.externalSync.updatedAt = new Date().toISOString();
    state.cameraControl.manualTargetSelection = options.manual !== false && Boolean(target);

    if (!target) {
        state.cameraControl.lastSelectedTargetKey = null;
        if (options.cameraMode) {
            setCameraMode(options.cameraMode);
        }
        return;
    }

    state.cameraControl.lastSelectedTargetKey = getSelectedTargetKey(target);

    if (options.cameraMode) {
        setCameraMode(options.cameraMode);
    } else {
        updateUI(state.latestData || {});
    }
}

function stopTrackingTarget() {
    setCameraMode('bridge');
}

function setCameraMode(mode = 'bridge') {
    state.cameraControl.mode = mode;
    state.cameraControl.lastAppliedAt = new Date().toISOString();

    if (mode === 'free') {
        return;
    }

    if (mode === 'bridge') {
        const bridgeView = computeBridgeView();
        animateCameraTo(bridgeView.target, bridgeView.camera, 700);
        return;
    }

    if (mode === 'target-track') {
        focusOnSelectedTarget();
        return;
    }

    // Extended camera presets
    const presets = {
        'top':       { target: new THREE.Vector3(0, 0, 0),   camera: new THREE.Vector3(0, 60, 0.1) },
        'bow':       { target: new THREE.Vector3(0, 2, 0),   camera: new THREE.Vector3(0, 6, -25) },
        'stern':     { target: new THREE.Vector3(0, 2, 0),   camera: new THREE.Vector3(0, 6, 25) },
        'port':      { target: new THREE.Vector3(0, 2, 0),   camera: new THREE.Vector3(-25, 8, 0) },
        'starboard': { target: new THREE.Vector3(0, 2, 0),   camera: new THREE.Vector3(25, 8, 0) },
        'overview':  { target: new THREE.Vector3(0, 0, 0),   camera: new THREE.Vector3(40, 30, 40) },
    };

    const preset = presets[mode];
    if (preset) {
        animateCameraTo(preset.target, preset.camera, 700);
    }
}

function getCameraControlState() {
    return {
        mode: state.cameraControl.mode,
        hasSelectedTarget: Boolean(state.externalSync.selectedTarget),
        currentSelectedTargetKey: state.externalSync.selectedTarget ? getSelectedTargetKey(state.externalSync.selectedTarget) : null,
        lastSelectedTargetKey: state.cameraControl.lastSelectedTargetKey,
        lastAppliedAt: state.cameraControl.lastAppliedAt,
        selectedTargetLabel: state.externalSync.selectedTarget ? getTargetLabel(state.externalSync.selectedTarget) : null,
        selectedTargetRisk: state.externalSync.selectedTarget?.risk_level || null,
        source: state.externalSync.source || null,
        manualTargetSelection: state.cameraControl.manualTargetSelection,
    };
}

function applyExternalSync(payload = {}) {
    const nextSelectedTarget = state.cameraControl.manualTargetSelection && state.externalSync.selectedTarget
        ? state.externalSync.selectedTarget
        : (payload.selectedTarget || state.externalSync.selectedTarget);
    const nextSource = state.cameraControl.manualTargetSelection && state.externalSync.selectedTarget
        ? state.externalSync.source || 'bridge-operator'
        : (payload.source || state.externalSync.source || 'worldmonitor');

    state.externalSync = {
        ownShip: payload.ownShip || state.externalSync.ownShip,
        selectedTarget: nextSelectedTarget,
        alarms: Array.isArray(payload.alarms) ? payload.alarms.map(normalizeExternalAlarm) : state.externalSync.alarms,
        weather: payload.weather || state.externalSync.weather,
        fusionTracks: Array.isArray(payload.fusionTracks) ? payload.fusionTracks : state.externalSync.fusionTracks,
        taskGraph: payload.taskGraph || state.externalSync.taskGraph,
        source: nextSource,
        updatedAt: payload.updatedAt || new Date().toISOString(),
    };

    renderFusionTracks(state.externalSync.fusionTracks || []);

    // Sync weather effects
    if (state.weatherEffects && state.externalSync.weather) {
        state.weatherEffects.setWeather(state.externalSync.weather);
    }

    updateUI(state.latestData || {});
}

function handleWindowMessage(event) {
    if (event.origin !== window.location.origin) return;

    const message = event.data;
    if (!message || message.source !== 'worldmonitor-ar-cas-pro') return;

    if (message.type === 'bridge_sync') {
        applyExternalSync(message.payload || {});
    }
}

// ==================== Wabi-Sabi 风格 HUD (货船轨道遥测) ====================

function createCargoOrbitHUD() {
    // 创建 HUD 容器 — 侘寂风格: 粗粝质感、不对称、留白、自然色
    const container = document.createElement('div');
    container.id = 'cargo-orbit-hud';
    container.innerHTML = `
      <div class="wabisabi-hud">
        <div class="hud-title">⛵ 貨船軌道 · 侘寂</div>
        <div class="hud-body">
          <div class="hud-row">
            <span class="hud-label">方位角</span>
            <span class="hud-value" id="orbit-angle">0.0°</span>
          </div>
          <div class="hud-row">
            <span class="hud-label">距本船</span>
            <span class="hud-value" id="orbit-distance">80.0 m</span>
          </div>
          <div class="hud-row">
            <span class="hud-label">航向</span>
            <span class="hud-value" id="orbit-heading">090°</span>
          </div>
          <div class="hud-row">
            <span class="hud-label">緯度</span>
            <span class="hud-value" id="orbit-lat">--</span>
          </div>
          <div class="hud-row">
            <span class="hud-label">經度</span>
            <span class="hud-value" id="orbit-lon">--</span>
          </div>
        </div>
        <div class="hud-footer">— 不完全の美 —</div>
      </div>
    `;
    document.body.appendChild(container);

    // 注入 wabi-sabi 样式
    const style = document.createElement('style');
    style.textContent = `
      #cargo-orbit-hud {
        position: fixed;
        right: 24px;
        bottom: 80px;
        z-index: 1000;
        font-family: 'Noto Serif SC', 'Georgia', 'Times New Roman', serif;
        user-select: none;
        pointer-events: none;
        opacity: 0;
        animation: wabisabiFadeIn 2.5s ease-out 1.5s forwards;
      }
      @keyframes wabisabiFadeIn {
        to { opacity: 1; }
      }
      .wabisabi-hud {
        background: rgba(18, 22, 18, 0.72);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(140, 130, 110, 0.35);
        border-radius: 2px;
        padding: 18px 22px 14px;
        min-width: 180px;
        box-shadow:
          0 0 0 1px rgba(100, 90, 70, 0.12) inset,
          4px 6px 18px rgba(0, 0, 0, 0.5);
        /* 不对称偏移 — 侘寂的「不完全」 */
        transform: rotate(-0.6deg) translateY(2px);
      }
      .hud-title {
        font-size: 13px;
        letter-spacing: 3px;
        color: #b8aa8a;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(140, 130, 110, 0.25);
        padding-bottom: 8px;
        margin-bottom: 10px;
        font-weight: 400;
      }
      .hud-body {
        display: flex;
        flex-direction: column;
        gap: 5px;
      }
      .hud-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 16px;
      }
      .hud-label {
        font-size: 11px;
        color: #8a8a7a;
        letter-spacing: 1px;
        font-weight: 300;
      }
      .hud-value {
        font-size: 15px;
        color: #d4cfc0;
        font-weight: 400;
        font-variant-numeric: tabular-nums;
        letter-spacing: 0.5px;
        text-shadow: 0 0 6px rgba(180, 170, 140, 0.15);
      }
      .hud-footer {
        font-size: 10px;
        color: #6a6a5a;
        text-align: right;
        margin-top: 10px;
        padding-top: 6px;
        border-top: 1px solid rgba(140, 130, 110, 0.15);
        letter-spacing: 2px;
        font-style: italic;
      }
    `;
    document.head.appendChild(style);

    // 缓存 DOM 引用
    state._hudAngle = document.getElementById('orbit-angle');
    state._hudDistance = document.getElementById('orbit-distance');
    state._hudHeading = document.getElementById('orbit-heading');
    state._hudLat = document.getElementById('orbit-lat');
    state._hudLon = document.getElementById('orbit-lon');
}

function updateCargoOrbitHUD() {
    if (!state.cargoShip || !state._hudAngle) return;

    // 从 cargo ship 位置计算角度和距离
    const cx = state.cargoShip.position.x;
    const cz = state.cargoShip.position.z;

    // 距原点 (双体船) 的距离
    const distance = Math.sqrt(cx * cx + cz * cz);

    // 当前角度 (度) — 从正北顺时针
    let angleDeg = Math.atan2(cx, cz) * (180 / Math.PI);
    if (angleDeg < 0) angleDeg += 360;

    // 航向 (切线方向 = 径向 + 90°)
    let headingDeg = (angleDeg + 90) % 360;

    // 更新 HUD
    state._hudAngle.textContent = angleDeg.toFixed(1) + '°';
    state._hudDistance.textContent = distance.toFixed(1) + ' m';
    state._hudHeading.textContent = headingDeg.toFixed(0).padStart(3, '0') + '°';

    // 模拟地理坐标 (与后端 cargo_orbit_telemetry 一致)
    const originLat = 31.2304;
    const originLon = 121.4737;
    const sceneToDeg = 0.0001;
    const lat = originLat + cz * sceneToDeg;
    const lon = originLon + cx * sceneToDeg;
    state._hudLat.textContent = lat.toFixed(4) + '°N';
    state._hudLon.textContent = lon.toFixed(4) + '°E';
}

// ==================== 动画循环 ====================

function animate() {
    requestAnimationFrame(animate);
    
    state.controls.update();
    const now = performance.now() * 0.001;

    // ── CCTV 预设相机：锁定为顶视/船头/船尾 跟随双体船 ──
    if (state.cctvPreset && state.boatMesh) {
        const b = state.boatMesh;
        const heading = b.rotation.y || 0;
        const sin = Math.sin(heading), cos = Math.cos(heading);
        const cargo = state.cargoShip;

        if (state.cctvPreset === 'top') {
            // 全局俯视：高空看双体船 + 货船轨道；轻微跟随双体船位置
            state.camera.position.set(b.position.x, 180, b.position.z + 1);
            state.camera.up.set(0, 0, -1);
            state.camera.lookAt(b.position.x, 0, b.position.z);
        } else if (state.cctvPreset === 'bow' && cargo) {
            // 前置摄像头：起点位于双体船船头，终点落在货船上
            const bowOff = -10;  // 本地 -Z 是船首方向
            const bx = b.position.x + bowOff * sin;
            const bz = b.position.z + bowOff * cos;
            state.camera.position.set(bx, b.position.y + 5.5, bz);
            state.camera.up.set(0, 1, 0);
            state.camera.lookAt(cargo.position.x, cargo.position.y + 3, cargo.position.z);
        } else if (state.cctvPreset === 'stern' && cargo) {
            // 后置摄像头：起点位于双体船船尾，终点落在货船上
            const sternOff = 10;
            const sx = b.position.x + sternOff * sin;
            const sz = b.position.z + sternOff * cos;
            state.camera.position.set(sx, b.position.y + 5.5, sz);
            state.camera.up.set(0, 1, 0);
            state.camera.lookAt(cargo.position.x, cargo.position.y + 3, cargo.position.z);
        } else if (state.cctvPreset === 'bow' || state.cctvPreset === 'stern') {
            // 货船尚未加载时，给一个临时朝向
            const dir = state.cctvPreset === 'bow' ? -1 : 1;
            state.camera.position.set(b.position.x, b.position.y + 5.5, b.position.z + dir * 10);
            state.camera.lookAt(b.position.x, b.position.y + 3, b.position.z + dir * 80);
        }
    }

    // 更新水面 + 天空时间
    if (state.waterMesh) {
        state.waterMesh.material.uniforms.time.value = now;
        // 天气联动: 波高/频率随海况变化
        if (state.weatherEffects) {
            const wh = state.weatherEffects.weather.wave.height;
            const wp = Math.max(state.weatherEffects.weather.wave.period, 3);
            state.waterMesh.material.uniforms.waveHeight.value = wh * 0.8;
            state.waterMesh.material.uniforms.waveFreq.value = 0.08 + (1.0 / wp) * 0.3;
            // 能见度影响雾距
            const vis = state.weatherEffects.weather.visibility ?? 10;
            state.waterMesh.material.uniforms.fogFar.value = Math.max(vis * 50, 100);
            state.waterMesh.material.uniforms.fogNear.value = Math.max(vis * 15, 30);
            // 场景雾联动能见度
            if (state.scene.fog) {
                state.scene.fog.near = Math.max(vis * 12, 20);
                state.scene.fog.far = Math.max(vis * 55, 80);
            }
            // 低能见度时天空变暗
            if (state._dirLight) {
                const fogDim = Math.max(0.3, Math.min(1.0, vis / 10.0));
                state._dirLight.intensity = 1.2 * fogDim;
            }
        }
    }
    if (state._skyMesh) {
        state._skyMesh.material.uniforms.time.value = now;
        // 太阳方向随时间移动 (一个完整天/夜循环 = 600s)
        const sunAngle = (now * 0.01047) % (Math.PI * 2); // 2π / 600
        const sunY = Math.sin(sunAngle) * 0.8;
        const sunX = Math.cos(sunAngle) * 0.5;
        state._skyMesh.material.uniforms.sunDirection.value.set(sunX, Math.max(sunY, -0.2), 0.3).normalize();
        // 日光联动
        if (state._dirLight) {
            state._dirLight.position.set(sunX * 100, Math.max(sunY * 80, 5), 30);
            const daylight = Math.max(0, sunY);
            state._dirLight.intensity = 0.3 + daylight * 1.2;
            // 日落/日出色温
            if (sunY > 0 && sunY < 0.2) {
                state._dirLight.color.setHex(0xffaa66); // 暖色
            } else if (sunY >= 0.2) {
                state._dirLight.color.setHex(0xffeedd); // 日间白
            } else {
                state._dirLight.color.setHex(0x334466); // 夜间冷蓝
            }
        }
    }
    
    // 船体运动响应波浪 (WPC穿浪双体船 RAO模型)
    if (state.boatMesh) {
        const time = now;
        let waveHeight = 0.5;
        let wavePeriod = 8.0;
        if (state.weatherEffects) {
            waveHeight = state.weatherEffects.weather.wave.height;
            wavePeriod = Math.max(state.weatherEffects.weather.wave.period, 3);
        }
        // WPC RAO: roll=0.045 rad/m, pitch=0.025 rad/m, heave=0.35 m/m
        const rollAmp = Math.min(waveHeight * 0.045, 0.35);
        const pitchAmp = Math.min(waveHeight * 0.025, 0.20);
        const heaveAmp = Math.min(waveHeight * 0.35, 3.5);
        const waveFreq = (2 * Math.PI) / wavePeriod;
        // 添加2阶高频耦合 (WPC特有: 穿浪时的短周期冲击)
        const highFreqRoll = Math.sin(time * waveFreq * 3.2) * rollAmp * 0.08;
        const highFreqPitch = Math.cos(time * waveFreq * 2.8) * pitchAmp * 0.12;
        state.boatMesh.rotation.z = Math.sin(time * waveFreq) * rollAmp + highFreqRoll;
        state.boatMesh.rotation.x = Math.cos(time * waveFreq * 0.9) * pitchAmp + highFreqPitch;
        state.boatMesh.position.y = Math.sin(time * waveFreq * 1.1) * heaveAmp;
        // 轻微偏航 (sway 横摇耦合)
        state.boatMesh.rotation.y = Math.sin(time * waveFreq * 0.4) * rollAmp * 0.03;
        // RPM 微振动叠加
        const rpm = state._currentRPM || 0;
        if (rpm > 0) {
            const vibAmp = (rpm / 200) * 0.008;
            state.boatMesh.position.y += Math.sin(time * rpm * 0.1) * vibAmp;
        }
        // 螺旋桨旋转
        updatePropellers(rpm || 720);
    }
    
    // 更新船尾航迹
    if (state._wakeTrail && state.boatMesh) {
        updateWakeTrail(now);
    }
    
    // Weather effects update
    if (state.weatherEffects) {
        state.weatherEffects.update(0.016);
        // 雨滴粒子与天气联动
        const precip = state.weatherEffects.weather?.precipitation?.intensity ?? 0;
        updateRain(precip);
    }
    
    // 测深仪声纳脉冲更新
    if (state._depthSounder) {
        state._depthSounder.material.uniforms.time.value = now;
        // 跟随自船位置
        if (state.boatMesh) {
            state._depthSounder.position.x = state.boatMesh.position.x;
            state._depthSounder.position.z = state.boatMesh.position.z;
        }
    }
    
    // 海底焦散动画
    if (state._seaFloor && state._seaFloor.material.uniforms) {
        state._seaFloor.material.uniforms.time.value = now;
    }
    
    // AR-CAS: 货船运动 — 以双体船(原点)为圆心做椭圆运动 (速度别太快)
    if (state.cargoShip) {
        // 使用帧计数器: 每帧递增，角速度 0.005 rad/帧 ≈ 0.3°/s @60fps
        if (state._cargoOrbitAngle === undefined) state._cargoOrbitAngle = 0;
        state._cargoOrbitAngle += 0.005;
        const orbitAngle = state._cargoOrbitAngle;
        // 椭圆运动参数: 长轴沿 X 轴 (120 units), 短轴沿 Z 轴 (60 units)
        const orbitRadiusX = 120;        // 长轴半径 (X方向)
        const orbitRadiusZ = 60;         // 短轴半径 (Z方向)
        // 计算椭圆位置: 以原点(双体船位置)为圆心
        state.cargoShip.position.x = Math.cos(orbitAngle) * orbitRadiusX;
        state.cargoShip.position.z = Math.sin(orbitAngle) * orbitRadiusZ;
        // 船头指向运动方向 (椭圆切线方向)
        // 椭圆参数方程: x = a*cos(θ), z = b*sin(θ)
        // 切线方向: dx/dθ = -a*sin(θ), dz/dθ = b*cos(θ)
        const headingAngle = Math.atan2(
            orbitRadiusX * Math.cos(orbitAngle),   // dz/dθ 的符号
            -orbitRadiusZ * Math.sin(orbitAngle)    // dx/dθ 的符号
        );
        state.cargoShip.rotation.y = headingAngle;
        // 大型船波浪影响 — 摇摆幅度小、周期长
        state.cargoShip.rotation.z = Math.sin(now * 0.4) * 0.008;
        state.cargoShip.rotation.x = Math.cos(now * 0.3) * 0.006;
        state.cargoShip.position.y = Math.sin(now * 0.5) * 0.5;

        // 更新 wabi-sabi HUD
        updateCargoOrbitHUD();
    }
    
    // AR-CAS: 冰山漂浮 (大型冰山, 缓慢漂移)
    state.icebergs.forEach((ib, i) => {
        const t = now + i * 1.5;
        ib.position.y = Math.sin(t * 0.25) * 0.4;
        ib.rotation.y += 0.0002;
        // 缓慢漂移
        ib.position.x += Math.sin(t * 0.03 + i) * 0.0008;
        ib.position.z += Math.cos(t * 0.025 + i) * 0.0008;
    });
    
    // 浮标晃动 + 灯光闪烁
    if (state._buoys) {
        state._buoys.forEach((b, i) => {
            const t = now + b.phase;
            b.group.position.y = Math.sin(t * 0.8) * 0.3;
            b.group.rotation.z = Math.sin(t * 0.6) * 0.05;
            // 灯光闪烁 (3s 周期, 0.3s 亮)
            const flashPhase = (t * 0.33) % 1.0;
            const isOn = flashPhase < 0.15;
            b.light.intensity = isOn ? 3.0 : 0.0;
            b.glow.visible = isOn;
        });
    }
    
    // 更新导航灯闪烁
    if (state._navLights) {
        updateNavLights(now);
    }
    
    // 海鸥群
    updateSeagullFlock(now);
    
    // 排气烟雾
    updateExhaustSmoke(now);
    
    // 船旗飘动
    updateFlag(now);
    
    // 舵叶微调 (自动舵 PID 模拟)
    if (state._rudders) {
        const rudderAngle = Math.sin(now * 0.4) * 0.08 + Math.sin(now * 1.2) * 0.03;
        state._rudders.forEach(r => { r.rotation.z = rudderAngle; });
    }
    
    // 船首侧推器空转
    if (state._bowThruster) {
        state._bowThruster.rotation.x += 0.02;
    }
    
    // 舱内动画 (仅在可见时)
    if (state._cabinsGroup && state._cabinsGroup.visible) {
        // 涡轮增压器旋转
        if (state._cabins['turbo_-1']) state._cabins['turbo_-1'].rotation.y += 0.4;
        if (state._cabins['turbo_1']) state._cabins['turbo_1'].rotation.y += 0.4;
        // 舵轮缓慢摆动
        if (state._helm) state._helm.rotation.z = Math.sin(now * 0.3) * 0.3;
        // ECR 屏幕色彩呼吸
        if (state._ecrScreens) {
            state._ecrScreens.forEach((s, i) => {
                const v = 0.6 + Math.sin(now * 1.5 + i * 0.7) * 0.25;
                s.material.opacity = v;
            });
        }
        // 机舱 LED 闪烁
        if (state._engineLEDs) {
            state._engineLEDs.forEach((led, i) => {
                const blink = Math.sin(now * (2 + i * 0.5) + i) > 0.6;
                led.material.opacity = blink ? 1.0 : 0.4;
                led.material.transparent = true;
            });
        }
        // 雷达屏幕扫描效果
        if (state._bridgeRadarScreen) {
            state._bridgeRadarScreen.material.opacity = 0.5 + Math.sin(now * 2.5) * 0.2;
        }
    }
    
    // 水下光束摇曳
    if (state._lightShafts) {
        state._lightShafts.children.forEach((shaft, i) => {
            shaft.rotation.z = Math.sin(now * 0.15 + i * 1.5) * 0.08;
            shaft.material.opacity = 0.03 + Math.sin(now * 0.2 + i) * 0.015;
        });
    }
    
    // 灯塔旋转光束
    if (state._lighthouse) {
        const lh = state._lighthouse;
        // 旋转灯光 (5s 周期)
        const beamAngle = (now * 1.257) % (Math.PI * 2);
        lh.light.position.x = lh.group.position.x + Math.cos(beamAngle) * 3;
        lh.light.position.z = lh.group.position.z + Math.sin(beamAngle) * 3;
        // 闪烁模式 (2闪, 10s周期)
        const flashPhase = (now * 0.1) % 1.0;
        const isOn = flashPhase < 0.1 || (flashPhase > 0.15 && flashPhase < 0.25);
        lh.light.intensity = isOn ? 8.0 : 0.5;
        lh.glow.material.opacity = isOn ? 1.0 : 0.2;
    }

    // 使用后处理管线渲染
    if (state._composer) {
        state._composer.render();
    } else {
        state.renderer.render(state.scene, state.camera);
    }
}

// ==================== 窗口大小调整 ====================

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    if (!container) return;
    
    state.camera.aspect = container.clientWidth / container.clientHeight;
    state.camera.updateProjectionMatrix();
    state.renderer.setSize(container.clientWidth, container.clientHeight);
    if (state._composer) {
        state._composer.setSize(container.clientWidth, container.clientHeight);
    }
    if (state._bloomPass) {
        state._bloomPass.resolution.set(container.clientWidth, container.clientHeight);
    }
}

// ==================== 搜索功能 ====================

export function searchAndFocus(query) {
    console.log('🔍 Searching for:', query);
    
    // 模糊搜索语义标签
    const results = state.semanticLabels.filter(label => 
        label.name.toLowerCase().includes(query.toLowerCase()) ||
        label.id.toLowerCase().includes(query.toLowerCase())
    );
    
    if (results.length > 0) {
        const target = results[0];
        console.log('✅ Found:', target);
        
        // 平滑移动相机到目标位置
        const targetPosition = new THREE.Vector3(
            target.position[0] + 10,
            target.position[1] + 5,
            target.position[2] + 10
        );
        
        // 简单动画
        const startPos = state.camera.position.clone();
        const duration = 1000;
        const startTime = Date.now();
        
        function animateCamera() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            state.camera.position.lerpVectors(startPos, targetPosition, progress);
            state.controls.target.set(
                target.position[0],
                target.position[1],
                target.position[2]
            );
            
            if (progress < 1) {
                requestAnimationFrame(animateCamera);
            }
        }
        
        animateCamera();
        
        return results;
    }
    
    console.log('❌ No results found');
    return [];
}

// ==================== 导出 API ====================

window.DigitalTwin = {
    init,
    searchAndFocus,
    applyExternalSync,
    focusOnCoordinates,
    setCameraMode,
    focusOnSelectedTarget,
    setSelectedTarget,
    stopTrackingTarget,
    getCameraControlState,
    getState: () => state,
    getWeatherEffects: () => state.weatherEffects,
    _updateArCas: updateArCasPanel,
};

// 自动初始化
window.addEventListener('DOMContentLoaded', init);
window.addEventListener('message', handleWindowMessage);
