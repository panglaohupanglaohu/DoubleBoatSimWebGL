// 使用 esm.sh 以解决 bare specifier（例如 examples 中的 "three"）解析问题
import * as THREE from '../public/lib/three.module.js';
import { OrbitControls } from 'https://esm.sh/three@0.165.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://esm.sh/three@0.165.0/examples/jsm/loaders/GLTFLoader.js';
import * as CANNON from '../public/lib/cannon-es.js';
import GUI from 'https://esm.sh/lil-gui@0.19.2';

import {
  waveParams,
  getWaveHeight,
  waterUniforms,
  waterVertexShader,
  waterFragmentShader
} from './waves.js';

let renderer, scene, camera, controls;
let world, boatMesh, boatBody, buoyancyPointsLocal = [];
let boatSize = null;
let waterMeshFar = null;
let waterMeshNear = null;
let hemiLight = null;
let dirLight = null;
let hemiHelper = null;
let dirHelper = null;
let cannonDebugger = null, debugVisible = false;

const clock = new THREE.Clock();
const statusEl = document.getElementById('status');

const simParams = {
  buoyancyCoeff: 520,
  dragCoeff: 6,
  density: 1.0,
  boatMass: 20000, // 100m 级船体质量，提高稳定性
  showPhysics: false,
  wireframeWater: false,
  draftDepth: 10, // 船体压入水面的深度（米，正值表示在水面下）
  enableStabilizer: true,
  uprightStiffness: 8.0, // 越小越容易晃动
  uprightDamping: 4.0,
  wobbleBoost: 1.0 // >1 表示更容易摇晃（减弱自稳）
};

// Y 方向翻转系数：1 正常，-1 反转
const Y_FLIP = -1;

const uiState = {
  showAxesHelper: false
};

const lightParams = {
  hemiIntensity: 0.9,
  hemiColor: '#aadfff',
  dirIntensity: 1.0,
  dirColor: '#ffffff',
  dirX: 30,
  dirY: 40,
  dirZ: 15,
  showHelpers: false
};

init();
animate();

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1525);
  scene.fog = new THREE.Fog(0x0b1525, 60, 220);

  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(15, 9, 22);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById('app').appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.target.set(0, 1.5, 0);

  setupLights();
  setupPhysics();
  createWater();
  loadBoat();
  setupGUI();

  window.addEventListener('resize', onResize);
}

function setupLights() {
  hemiLight = new THREE.HemisphereLight(0xaadfff, 0x0b1120, lightParams.hemiIntensity);
  scene.add(hemiLight);

  dirLight = new THREE.DirectionalLight(0xffffff, lightParams.dirIntensity);
  dirLight.position.set(lightParams.dirX, lightParams.dirY, lightParams.dirZ);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(2048, 2048);
  dirLight.shadow.camera.near = 1;
  dirLight.shadow.camera.far = 120;
  dirLight.shadow.camera.left = -60;
  dirLight.shadow.camera.right = 60;
  dirLight.shadow.camera.top = 60;
  dirLight.shadow.camera.bottom = -60;
  scene.add(dirLight);

  updateLightHelpers();
}

function setupPhysics() {
  world = new CANNON.World({
    gravity: new CANNON.Vec3(0, -9.82, 0)
  });
  world.broadphase = new CANNON.SAPBroadphase(world);
  world.allowSleep = true;
  world.solver.iterations = 14;
}

function createWater() {
  // 简化为单一水面网格，避免额外细化贴片
  const geom = new THREE.PlaneGeometry(500, 500, 200, 200);
  geom.rotateX(-Math.PI / 2); // make it XZ

  const material = new THREE.ShaderMaterial({
    uniforms: waterUniforms,
    vertexShader: waterVertexShader,
    fragmentShader: waterFragmentShader,
    transparent: true,
    side: THREE.DoubleSide,
    wireframe: simParams.wireframeWater
  });

  waterMeshFar = new THREE.Mesh(geom, material);
  waterMeshFar.receiveShadow = true;
  scene.add(waterMeshFar);

  // 不再使用近处高分辨率贴片
  waterMeshNear = null;
}

function loadBoat() {
  const loader = new GLTFLoader();

  // 统一使用绝对路径：/public/boat 1.glb
  // 文件位置：D:\DoubleBoatRefactor\DoubleBoatSimWebGL\public\boat 1.glb
  const base = window.location.origin;
  const candidates = [
    '/public/boat 1.glb', // 绝对路径（最优先）
    `${base}/public/boat 1.glb` // 完整URL（备选）
  ];

  let index = 0;
  let loaded = false;

  // 如果 3 秒后还没创建船，自动启用兜底方舟
  setTimeout(() => {
    if (!loaded && !boatMesh) {
      console.warn('GLB not loaded within timeout, using fallback box boat.');
      createFallbackBoat();
    }
  }, 3000);

  const tryLoadNext = () => {
    if (index >= candidates.length) {
      console.error('Failed to load boat GLB with all candidate paths, using box fallback.');
      createFallbackBoat();
      return;
    }

    const url = candidates[index++];
    loader.load(
      url,
      (gltf) => {
        loaded = true;
        boatMesh = gltf.scene;
        boatMesh.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        const box = new THREE.Box3().setFromObject(boatMesh);
        const size = new THREE.Vector3();
        const center = new THREE.Vector3();
        box.getSize(size);
        box.getCenter(center);

        // Re-center geometry pivot to its bounding box center
        boatMesh.position.sub(center);

        // 按目标船长（米）归一：模型 X 方向当前长度 -> 100 米
        const desiredLength = 100; // 目标长度（单位：米）
        const scaleFactor = desiredLength / size.x;
        boatMesh.scale.setScalar(scaleFactor);

        scene.add(boatMesh);
        // 物理尺寸也按比例放大
        const scaledSize = size.clone().multiplyScalar(scaleFactor);
        createBoatBody(scaledSize);
        console.log('Boat GLB loaded from', url);
      },
      undefined,
      (err) => {
        console.warn('Failed to load boat GLB from', url, err);
        tryLoadNext();
      }
    );
  };

  tryLoadNext();
}

function createFallbackBoat() {
  const geom = new THREE.BoxGeometry(4, 1, 1.6);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffaa55, metalness: 0.2, roughness: 0.4 });
  boatMesh = new THREE.Mesh(geom, mat);
  boatMesh.castShadow = true;
  boatMesh.receiveShadow = true;
  scene.add(boatMesh);

  const size = new THREE.Vector3(4, 1, 1.6);
  createBoatBody(size);
}

function createBoatBody(sizeVec3) {
  boatSize = sizeVec3.clone();
  const halfExtents = new CANNON.Vec3(sizeVec3.x * 0.5, sizeVec3.y * 0.5, sizeVec3.z * 0.5);
  const shape = new CANNON.Box(halfExtents);

  boatBody = new CANNON.Body({
    mass: simParams.boatMass,
    shape,
    angularDamping: 0.6,
    linearDamping: 0.15,
    position: new CANNON.Vec3(0, 4.0, 0) // 初始会再根据水面高度调整
  });
  world.addBody(boatBody);

  buoyancyPointsLocal = buildBuoyancyPoints(sizeVec3);

  // 将船放置到当前波面上方，避免初始扎水
  placeBoatOnWater();
}

function placeBoatOnWater() {
  if (!boatBody) return;
  const x = boatBody.position.x;
  const z = boatBody.position.z;
  const t = clock.elapsedTime;
  const waterH = getWaveHeight(x, -z, t) * Y_FLIP;

  // 设置吃水深度：正值表示压入水面
  boatBody.position.y = waterH - simParams.draftDepth;
  boatBody.velocity.setZero();
  boatBody.angularVelocity.setZero();
  boatBody.quaternion.set(0, 0, 0, 1);

  // 同步 Three.js mesh
  syncBoatMesh();
}

function buildBuoyancyPoints(sizeVec3) {
  const hx = sizeVec3.x * 0.5 * 0.85;
  const hy = -sizeVec3.y * 0.5 * 0.9; // slightly below bottom
  const hz = sizeVec3.z * 0.5 * 0.85;

  return [
    new CANNON.Vec3(-hx, hy, -hz),
    new CANNON.Vec3(hx, hy, -hz),
    new CANNON.Vec3(-hx, hy, hz),
    new CANNON.Vec3(hx, hy, hz),
    new CANNON.Vec3(0, hy, 0)
  ];
}

function applyBuoyancyForces(timeSeconds) {
  if (!boatBody) return;

  // 设定一个最大浮力，防止瞬间过度推离水面（按船重的 1.5 倍）
  const maxBuoyancy = boatBody.mass * 9.82 * 1.5;

  for (const localP of buoyancyPointsLocal) {
    const worldP = new CANNON.Vec3();
    boatBody.pointToWorldFrame(localP, worldP);

    // Z 取反，与 shader 一致
    const waterHeight = getWaveHeight(worldP.x, -worldP.z, timeSeconds) * Y_FLIP;
    const depth = waterHeight - worldP.y;

    if (depth > 0) {
      const forceMagnitude = Math.min(
        maxBuoyancy,
        depth * simParams.buoyancyCoeff * simParams.density
      );
      const upForce = new CANNON.Vec3(0, forceMagnitude, 0);

      const velAtPoint = new CANNON.Vec3();
      boatBody.getVelocityAtWorldPoint(worldP, velAtPoint);

      const drag = velAtPoint.scale(-simParams.dragCoeff);
      const totalForce = upForce.vadd(drag);

      boatBody.applyForce(totalForce, worldP);
    }
  }
}

// 简单的“自稳”力矩，避免船体倒扣疯狂旋转
function applyUprightTorque() {
  if (!boatBody || !simParams.enableStabilizer) return;
  const worldUp = new CANNON.Vec3(0, 1, 0);
  const bodyUp = boatBody.quaternion.vmult(new CANNON.Vec3(0, 1, 0));

  const dot = Math.max(-1, Math.min(1, bodyUp.dot(worldUp)));
  const angle = Math.acos(dot);

  // 如果角度很小就不用管
  if (angle < 0.01) return;

  const axis = bodyUp.cross(worldUp);
  const stiffness = Math.max(0, simParams.uprightStiffness);
  const damping = Math.max(0, simParams.uprightDamping);
  const wobble = Math.max(0.2, simParams.wobbleBoost); // 越大，自稳越弱，摇晃越大
  const effStiffness = stiffness / wobble;
  const effDamping = damping / wobble;
  if (effStiffness < 0.01 && effDamping < 0.01) return;

  const torque = axis.scale(angle * effStiffness).vsub(boatBody.angularVelocity.scale(effDamping));
  boatBody.torque.vadd(torque, boatBody.torque);
}

function syncBoatMesh() {
  if (!boatMesh || !boatBody) return;
  boatMesh.position.copy(boatBody.position);
  boatMesh.quaternion.copy(boatBody.quaternion);
}

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  const elapsed = clock.elapsedTime;

  applyBuoyancyForces(elapsed);
  applyUprightTorque();

  const fixedTimeStep = 1 / 60;
  world.step(fixedTimeStep, delta, 3);

  syncBoatMesh();
  updateWater(elapsed);
  updateStatus(elapsed);

  controls.update();
  // 调试线框关闭时跳过
  if (debugVisible && cannonDebugger) cannonDebugger.update();
  renderer.render(scene, camera);
}

function updateStatus(timeSeconds) {
  if (!statusEl) return;
  if (!boatBody) {
    statusEl.textContent = 'Loading boat...';
    return;
  }
  const pos = boatBody.position;
  const waterH = getWaveHeight(pos.x, -pos.z, timeSeconds) * Y_FLIP;
  const deltaY = pos.y - waterH;
  statusEl.textContent =
    `Boat position (x,y,z): ${pos.x.toFixed(2)}, ${pos.y.toFixed(2)}, ${pos.z.toFixed(2)}\n` +
    `Boat mass: ${simParams.boatMass.toFixed(0)} kg\n` +
    `Water height @ boat : ${waterH.toFixed(2)}\n` +
    `Offset to surface  : ${deltaY.toFixed(2)} m`;
}

function updateWater(timeSeconds) {
  waterUniforms.uTime.value = timeSeconds;
  waterUniforms.uAmplitude.value = waveParams.amplitude;
  waterUniforms.uWavelength.value = waveParams.wavelength;
  waterUniforms.uSpeed.value = waveParams.speed;
  waterUniforms.uSteepness.value = waveParams.steepness;
  waterUniforms.uYFlip.value = Y_FLIP;
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function setupGUI() {
  const gui = new GUI({ width: 320, title: 'Simulation Controls' });
  gui.domElement.style.zIndex = '20';

  const numericCtrls = [];

  const waveFolder = gui.addFolder('Wave');
  numericCtrls.push(waveFolder.add(waveParams, 'amplitude', 0.1, 3.0, 0.05));
  numericCtrls.push(waveFolder.add(waveParams, 'wavelength', 4, 40, 0.5));
  numericCtrls.push(waveFolder.add(waveParams, 'speed', 0.2, 4.0, 0.05));
  numericCtrls.push(waveFolder.add(waveParams, 'steepness', 0.2, 1.2, 0.02));

  const buoyFolder = gui.addFolder('Buoyancy');
  numericCtrls.push(buoyFolder.add(simParams, 'buoyancyCoeff', 200, 1200, 10));
  numericCtrls.push(buoyFolder.add(simParams, 'dragCoeff', 0, 20, 0.1));
  numericCtrls.push(buoyFolder.add(simParams, 'density', 0.5, 2.0, 0.05));
  const massCtrl = buoyFolder.add(simParams, 'boatMass', 1000, 100000, 500).name('Boat mass (kg)')
    .onFinishChange(() => {
      if (boatBody) {
        boatBody.mass = simParams.boatMass;
        boatBody.updateMassProperties();
      }
    });
  // 确认初始值显示为默认 20000
  massCtrl.setValue(simParams.boatMass);
  numericCtrls.push(massCtrl);
  buoyFolder.add(simParams, 'showPhysics').onChange((v) => {
    debugVisible = v;
  });
  buoyFolder.add(simParams, 'wireframeWater').onChange((v) => {
    if (waterMeshFar) waterMeshFar.material.wireframe = v;
    if (waterMeshNear) waterMeshNear.material.wireframe = v;
  });
  buoyFolder.add({ reset: resetBoatPose }, 'reset').name('Reset boat');
  numericCtrls.push(buoyFolder.add(simParams, 'draftDepth', -5, 25, 0.1).name('Draft depth (m)').onChange(() => {
    placeBoatOnWater();
  }));
  buoyFolder.add(simParams, 'enableStabilizer').name('Stabilizer on/off');
  numericCtrls.push(buoyFolder.add(simParams, 'uprightStiffness', 0, 15, 0.1).name('Stabilizer stiff'));
  numericCtrls.push(buoyFolder.add(simParams, 'uprightDamping', 0, 10, 0.1).name('Stabilizer damp'));
  numericCtrls.push(buoyFolder.add(simParams, 'wobbleBoost', 0.2, 5.0, 0.1).name('Wobble boost ↑=more swing'));

  const viewFolder = gui.addFolder('View / Helpers');
  viewFolder.add({ focus: focusBoat }, 'focus').name('Focus boat');
  viewFolder.add(uiState, 'showAxesHelper').name('Show axes').onChange(toggleAxesHelper);

  const lightFolder = gui.addFolder('Lighting');
  lightFolder.add(lightParams, 'showHelpers').name('Show helpers').onChange(updateLightHelpers);
  numericCtrls.push(lightFolder.add(lightParams, 'hemiIntensity', 0, 2, 0.01).onChange(updateLights));
  lightFolder.addColor(lightParams, 'hemiColor').name('Hemi color').onChange(updateLights);
  numericCtrls.push(lightFolder.add(lightParams, 'dirIntensity', 0, 3, 0.01).onChange(updateLights));
  lightFolder.addColor(lightParams, 'dirColor').name('Dir color').onChange(updateLights);
  numericCtrls.push(lightFolder.add(lightParams, 'dirX', -100, 100, 0.5).onChange(updateLights));
  numericCtrls.push(lightFolder.add(lightParams, 'dirY', 1, 120, 0.5).onChange(updateLights));
  numericCtrls.push(lightFolder.add(lightParams, 'dirZ', -100, 100, 0.5).onChange(updateLights));

  waveFolder.close();

  // 给所有数字输入加“上下箭头”支持（设为 number 类型）
  numericCtrls.forEach((ctrl) => addNumericArrows(ctrl));

  // 高亮摇晃调节控件
  const wobbleFolderDom = buoyFolder.domElement;
  if (wobbleFolderDom) {
    wobbleFolderDom.style.border = '1px solid #ffd54f';
    wobbleFolderDom.style.boxShadow = '0 0 8px rgba(255, 213, 79, 0.6)';
  }
}

function addNumericArrows(ctrl) {
  if (!ctrl || !ctrl.domElement) return;
  const input = ctrl.domElement.querySelector('input[type="text"], input[type="number"]');
  if (input) {
    input.type = 'number';
    // 如果有 step 设置，沿用 controller 的 step；否则保留现状
    if (typeof ctrl._step === 'number') {
      input.step = `${ctrl._step}`;
    }
    // 兼容部分浏览器隐藏箭头的情况
    input.style.appearance = 'number-input';
    input.style.MozAppearance = 'textfield';
  }
}

function resetBoatPose() {
  if (!boatBody) return;
  boatBody.position.set(0, 2.5, 0);
  boatBody.quaternion.set(0, 0, 0, 1);
  boatBody.velocity.setZero();
  boatBody.angularVelocity.setZero();
}

// 将摄像机对准船体，并垂直对齐（俯视/侧视混合）
function focusBoat() {
  if (!boatMesh) return;
  const pos = boatMesh.position.clone();
  // 把相机放到船体上方和后方一点
  camera.position.set(pos.x + 15, pos.y + 10, pos.z + 15);
  controls.target.copy(pos);
  controls.update();
  placeBoatOnWater(); // 同时把船放回水面，防止已偏离
}

let axesHelper = null;
let axisLabels = [];
function toggleAxesHelper(show) {
  if (show) {
    const axisLen = getAxisLen();
    axesHelper = new THREE.AxesHelper(axisLen);
    scene.add(axesHelper);
    addAxisLabels(axisLen);
    // 让轴跟随船体中心
    const updateAxes = () => {
      if (!axesHelper || !boatMesh) return;
      axesHelper.position.copy(boatMesh.position);
      updateAxisLabels(axisLen);
      requestAnimationFrame(updateAxes);
    };
    requestAnimationFrame(updateAxes);
  } else {
    if (axesHelper) scene.remove(axesHelper);
    removeAxisLabels();
  }
}

function getAxisLen() {
  if (!boatSize) return 6;
  const maxSide = Math.max(boatSize.x, boatSize.y, boatSize.z);
  return Math.max(6, maxSide * 0.4);
}

function makeTextSprite(text, color = '#ffffff', scale = 1.0) {
  const canvas = document.createElement('canvas');
  const size = 128;
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, size, size);
  ctx.fillStyle = color;
  ctx.font = 'bold 64px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, size / 2, size / 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(scale, scale, scale);
  return sprite;
}

function addAxisLabels(axisLen) {
  removeAxisLabels();
  const labelScale = Math.max(1.2, axisLen * 0.08);
  const xLabel = makeTextSprite('X', '#ff5555', labelScale);
  const yLabel = makeTextSprite('Y', '#55ff55', labelScale);
  const zLabel = makeTextSprite('Z', '#5599ff', labelScale);
  axisLabels = [xLabel, yLabel, zLabel];
  axisLabels.forEach((s) => scene.add(s));
}

function removeAxisLabels() {
  axisLabels.forEach((s) => scene.remove(s));
  axisLabels = [];
}

function updateAxisLabels(axisLen) {
  if (!boatMesh || axisLabels.length !== 3) return;
  const base = boatMesh.position;
  const offset = Math.max(4.4, axisLen * 0.65);
  axisLabels[0].position.set(base.x + offset, base.y, base.z);        // X
  axisLabels[1].position.set(base.x, base.y + offset, base.z);        // Y
  axisLabels[2].position.set(base.x, base.y, base.z + offset);        // Z (scene forward)
}

function updateLights() {
  if (hemiLight) {
    hemiLight.intensity = lightParams.hemiIntensity;
    hemiLight.color.set(lightParams.hemiColor);
  }
  if (dirLight) {
    dirLight.intensity = lightParams.dirIntensity;
    dirLight.color.set(lightParams.dirColor);
    dirLight.position.set(lightParams.dirX, lightParams.dirY, lightParams.dirZ);
  }
  updateLightHelpers();
}

function updateLightHelpers() {
  const needHelpers = lightParams.showHelpers;
  if (needHelpers) {
    if (hemiLight && !hemiHelper) {
      hemiHelper = new THREE.HemisphereLightHelper(hemiLight, 3);
      scene.add(hemiHelper);
    }
    if (dirLight && !dirHelper) {
      dirHelper = new THREE.DirectionalLightHelper(dirLight, 4);
      scene.add(dirHelper);
    }
    if (hemiHelper) hemiHelper.update();
    if (dirHelper) dirHelper.update();
  } else {
    if (hemiHelper) { scene.remove(hemiHelper); hemiHelper = null; }
    if (dirHelper) { scene.remove(dirHelper); dirHelper = null; }
  }
}

