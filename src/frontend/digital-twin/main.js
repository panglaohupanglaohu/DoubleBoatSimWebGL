/**
 * DoubleBoatClawSystem - 数字孪生主入口
 * 
 * 整合 Three.js 3D 渲染与后端实时数据
 */

import * as THREE from 'https://esm.sh/three@0.165.0';
import { OrbitControls } from 'https://esm.sh/three@0.165.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://esm.sh/three@0.165.0/examples/jsm/loaders/GLTFLoader.js';

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
    state.scene.fog = new THREE.Fog(0x0b1525, 60, 220);
    
    // 创建相机
    const container = document.getElementById('canvas-container');
    state.camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        500
    );
    state.camera.position.set(30, 20, 30);
    
    // 创建渲染器
    state.renderer = new THREE.WebGLRenderer({ 
        canvas: document.getElementById('three-canvas'),
        antialias: true 
    });
    state.renderer.setSize(container.clientWidth, container.clientHeight);
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    state.renderer.shadowMap.enabled = true;
    
    // 创建控制器
    state.controls = new OrbitControls(state.camera, state.renderer.domElement);
    state.controls.enableDamping = true;
    state.controls.enableZoom = true;
    state.controls.maxPolarAngle = Math.PI * 0.49;
    state.controls.target.set(0, 0, 0);
    state.controls.minDistance = 10;
    state.controls.maxDistance = 120;
    
    // 设置灯光
    setupLights();
    
    // 创建水面
    createWater();
    
    // 加载船体模型
    loadBoat();
    
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
    animate();

    // 初始化双智能体团队监控浮层
    // Init weather effects
    state.weatherEffects = new WeatherEffects(state.scene);
    window.DigitalTwin.weatherEffects = state.weatherEffects;

    initAgentTeamMonitor();
    
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
    container.style.position = 'fixed';
    container.style.right = '12px';
    container.style.bottom = '12px';
    container.style.width = '520px';
    container.style.maxWidth = 'calc(100vw - 24px)';
    container.style.maxHeight = '46vh';
    container.style.overflow = 'auto';
    container.style.zIndex = '999';
    container.style.background = 'rgba(5, 12, 20, 0.72)';
    container.style.border = '1px solid rgba(79, 195, 247, 0.28)';
    container.style.borderRadius = '10px';
    container.style.backdropFilter = 'blur(8px)';

    document.body.appendChild(container);

    state.agentTeamMonitor = new AgentTeamMonitor(container, {
        refreshInterval: 5000,
        apiBase: '/api/v1/agent-teams',
    });
    state.agentTeamMonitor.start();

    // Make the panel draggable by its header
    setTimeout(() => makeDraggable(container, 'h2'), 200);
}

// ==================== 灯光 ====================

function setupLights() {
    // 环境光
    const hemiLight = new THREE.HemisphereLight(0xaadfff, 0x0b1120, 0.9);
    state.scene.add(hemiLight);
    
    // 平行光
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
    dirLight.position.set(30, 40, 15);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(2048, 2048);
    dirLight.shadow.camera.near = 1;
    dirLight.shadow.camera.far = 120;
    dirLight.shadow.camera.left = -60;
    dirLight.shadow.camera.right = 60;
    dirLight.shadow.camera.top = 60;
    dirLight.shadow.camera.bottom = -60;
    state.scene.add(dirLight);
}

// ==================== 水面 ====================

function createWater() {
    const geometry = new THREE.PlaneGeometry(500, 500, 200, 200);
    geometry.rotateX(-Math.PI / 2);
    
    const material = new THREE.ShaderMaterial({
        uniforms: { time: { value: 0 }, color: { value: new THREE.Color(0x004488) } },
        vertexShader: `
            uniform float time;
            varying vec2 vUv;
            varying float vHeight;
            
            void main() {
                vUv = uv;
                vec3 pos = position;
                
                // 简单波浪
                float height = sin(pos.x * 0.05 + time) * 0.5 + 
                              cos(pos.y * 0.05 + time) * 0.5;
                pos.z += height;
                vHeight = height;
                
                vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                gl_Position = projectionMatrix * mvPosition;
            }
        `,
        fragmentShader: `
            uniform vec3 color;
            varying float vHeight;
            
            void main() {
                float brightness = 0.5 + vHeight * 0.3;
                vec3 finalColor = color * brightness;
                gl_FragColor = vec4(finalColor, 0.8);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide,
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

// 简化版双体船模型 (fallback)
function createFallbackBoat() {
    state.boatMesh = new THREE.Group();
    
    const hullMaterial = new THREE.MeshPhongMaterial({
        color: 0x4a90e2,
        shininess: 50,
    });
    
    // 左船体
    const leftHull = new THREE.Mesh(
        new THREE.BoxGeometry(3, 1.5, 15),
        hullMaterial
    );
    leftHull.position.set(-4, -0.5, 0);
    leftHull.castShadow = true;
    state.boatMesh.add(leftHull);
    
    // 右船体
    const rightHull = new THREE.Mesh(
        new THREE.BoxGeometry(3, 1.5, 15),
        hullMaterial
    );
    rightHull.position.set(4, -0.5, 0);
    rightHull.castShadow = true;
    state.boatMesh.add(rightHull);
    
    // 连接桥
    const bridge = new THREE.Mesh(
        new THREE.BoxGeometry(11, 0.5, 4),
        new THREE.MeshPhongMaterial({ color: 0x666666 })
    );
    bridge.position.set(0, 0.5, 0);
    state.boatMesh.add(bridge);
    
    // 上层建筑
    const superstructure = new THREE.Mesh(
        new THREE.BoxGeometry(8, 2, 3),
        new THREE.MeshPhongMaterial({ color: 0xffffff })
    );
    superstructure.position.set(0, 2, 1);
    state.boatMesh.add(superstructure);
    
    state.boatMesh.position.set(0, 0, 0);
    state.scene.add(state.boatMesh);
    
    console.log('✅ Fallback boat created');
    
    // 创建语义标签
    createSemanticLabels();
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
                updateDigitalTwin(message.data);
            }
        } catch (e) {
            console.error('Error parsing message:', e);
        }
    };
}

// ==================== 数字孪生更新 ====================

function updateDigitalTwin(data) {
    // 更新船体状态 (基于主机数据)
    if (data.engine && state.boatMesh) {
        // 根据 RPM 添加轻微振动
        const rpm = data.engine.rpm || 0;
        const vibration = (rpm / 200) * 0.02;
        state.boatMesh.position.y = Math.sin(Date.now() * 0.01) * vibration;
    }
    
    // 更新热力图 (基于传感器数据)
    if (data.sensors) {
        updateHeatmap(data.sensors);
    }
    
    // 更新 UI
    updateUI(data);
}

// ==================== 热力图渲染 ====================

function updateHeatmap(sensors) {
    // 示例：根据温度数据更新颜色
    const tempSensor = sensors['TEMP-001'];
    if (tempSensor && state.boatMesh) {
        const temp = tempSensor.value || 20;
        const normalizedTemp = (temp - 20) / 100; // 假设 20-120°C
        
        // 颜色映射 (蓝->绿->黄->红)
        const color = new THREE.Color();
        color.setHSL(0.6 - normalizedTemp * 0.6, 1.0, 0.5);
        
        state.boatMesh.traverse((child) => {
            if (child.isMesh && child.material) {
                child.material.color = color.clone();
            }
        });
    }
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

// ==================== 动画循环 ====================

function animate() {
    requestAnimationFrame(animate);
    
    state.controls.update();
    
    // 更新水面
    if (state.waterMesh) {
        state.waterMesh.material.uniforms.time.value = performance.now() * 0.001;
    }
    
    // 船体运动响应波浪 (WPC穿浪双体船 RAO模型)
    if (state.boatMesh) {
        const time = Date.now() * 0.001;
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
        state.boatMesh.rotation.z = Math.sin(time * waveFreq) * rollAmp;
        state.boatMesh.rotation.x = Math.cos(time * waveFreq * 0.9) * pitchAmp;
        state.boatMesh.position.y = Math.sin(time * waveFreq * 1.1) * heaveAmp;
    }
    
    // Weather effects update
    if (state.weatherEffects) {
        state.weatherEffects.update(0.016);
    }

    state.renderer.render(state.scene, state.camera);
}

// ==================== 窗口大小调整 ====================

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    if (!container) return;
    
    state.camera.aspect = container.clientWidth / container.clientHeight;
    state.camera.updateProjectionMatrix();
    state.renderer.setSize(container.clientWidth, container.clientHeight);
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
};

// 自动初始化
window.addEventListener('DOMContentLoaded', init);
window.addEventListener('message', handleWindowMessage);
