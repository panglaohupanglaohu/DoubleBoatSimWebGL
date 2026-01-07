/**
 * 场景预演系统
 * Scenario Simulation System
 * 
 * 支持自定义场景预演，包括：
 * - 暴雨漏水场景
 * - 第一人称视角
 * - 巡检人员路径
 * - 设备故障模拟
 */

import * as THREE from '../../public/lib/three.module.js';

export class ScenarioSimulator {
  constructor(scene, camera, shipController, weatherSystem) {
    this.scene = scene;
    this.camera = camera;
    this.shipController = shipController;
    this.weatherSystem = weatherSystem;
    
    this.activeScenario = null;
    this.scenarios = new Map();
    this.isFirstPerson = false;
    this.pathFollower = null;
    
    // 第一人称控制
    this.firstPersonControls = {
      moveSpeed: 2.0,
      lookSpeed: 0.002,
      keys: {
        forward: false,
        backward: false,
        left: false,
        right: false
      },
      mouse: {
        x: 0,
        y: 0,
        isDown: false
      }
    };
    
    // 路径点
    this.pathPoints = [];
    this.currentPathIndex = 0;
    this.pathVisualization = null;
    
    this.initializeScenarios();
    this.setupFirstPersonControls();
  }

  /**
   * 初始化预定义场景
   */
  initializeScenarios() {
    // 暴雨漏水场景
    this.scenarios.set('heavyRainLeak', {
      id: 'heavyRainLeak',
      name: '暴雨漏水场景 | Heavy Rain Leak Scenario',
      description: '模拟暴雨天气下船舱漏水，巡检人员从住宿舱室走到漏水点进行维修',
      weather: {
        preset: 'storm',
        windSpeed: 25,
        rainIntensity: 80,
        seaState: 6
      },
      path: [
        { name: '起始点：住宿舱室', position: [0, 3, -15], type: 'start' },
        { name: '走廊1', position: [0, 3, -10], type: 'waypoint' },
        { name: '走廊2', position: [0, 3, -5], type: 'waypoint' },
        { name: '漏水点：货仓', position: [5, 2, 0], type: 'target' }
      ],
      effects: ['rain', 'leak', 'water']
    });
  }

  /**
   * 设置第一人称控制
   */
  setupFirstPersonControls() {
    // 键盘事件
    document.addEventListener('keydown', (event) => {
      if (!this.isFirstPerson) return;
      
      switch (event.code) {
        case 'KeyW':
          this.firstPersonControls.keys.forward = true;
          break;
        case 'KeyS':
          this.firstPersonControls.keys.backward = true;
          break;
        case 'KeyA':
          this.firstPersonControls.keys.left = true;
          break;
        case 'KeyD':
          this.firstPersonControls.keys.right = true;
          break;
      }
    });
    
    document.addEventListener('keyup', (event) => {
      if (!this.isFirstPerson) return;
      
      switch (event.code) {
        case 'KeyW':
          this.firstPersonControls.keys.forward = false;
          break;
        case 'KeyS':
          this.firstPersonControls.keys.backward = false;
          break;
        case 'KeyA':
          this.firstPersonControls.keys.left = false;
          break;
        case 'KeyD':
          this.firstPersonControls.keys.right = false;
          break;
      }
    });
    
    // 鼠标事件
    document.addEventListener('mousedown', (event) => {
      if (!this.isFirstPerson) return;
      if (event.button === 0) { // 左键
        this.firstPersonControls.mouse.isDown = true;
        this.firstPersonControls.mouse.x = event.clientX;
        this.firstPersonControls.mouse.y = event.clientY;
      }
    });
    
    document.addEventListener('mouseup', () => {
      this.firstPersonControls.mouse.isDown = false;
    });
    
    document.addEventListener('mousemove', (event) => {
      if (!this.isFirstPerson || !this.firstPersonControls.mouse.isDown) return;
      
      const deltaX = event.clientX - this.firstPersonControls.mouse.x;
      const deltaY = event.clientY - this.firstPersonControls.mouse.y;
      
      // 旋转视角
      const euler = new THREE.Euler().setFromQuaternion(this.camera.quaternion);
      euler.y -= deltaX * this.firstPersonControls.lookSpeed;
      euler.x -= deltaY * this.firstPersonControls.lookSpeed;
      euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
      
      this.camera.quaternion.setFromEuler(euler);
      
      this.firstPersonControls.mouse.x = event.clientX;
      this.firstPersonControls.mouse.y = event.clientY;
    });
  }

  /**
   * 启动场景
   */
  startScenario(scenarioId) {
    const scenario = this.scenarios.get(scenarioId);
    if (!scenario) {
      console.error(`❌ Scenario ${scenarioId} not found`);
      return;
    }
    
    this.activeScenario = scenario;
    console.log(`🎬 Starting scenario: ${scenario.name}`);
    
    // 设置天气
    if (scenario.weather) {
      this.weatherSystem.setWeatherPreset(scenario.weather.preset);
      if (scenario.weather.windSpeed !== undefined) {
        this.weatherSystem.setWind(scenario.weather.windSpeed, 180);
      }
      if (scenario.weather.rainIntensity !== undefined) {
        this.weatherSystem.setRain(scenario.weather.rainIntensity);
      }
      if (scenario.weather.seaState !== undefined) {
        this.weatherSystem.setSeaState(scenario.weather.seaState);
      }
    }
    
    // 创建场景效果
    this._createScenarioEffects(scenario);
    
    // 设置路径
    if (scenario.path) {
      this.pathPoints = scenario.path.map(p => ({
        name: p.name,
        position: new THREE.Vector3(...p.position),
        type: p.type
      }));
      this._createPathVisualization();
      this.currentPathIndex = 0;
    }
    
    // 切换到第一人称视角
    this.enterFirstPerson();
    
    // 移动到起始点
    if (this.pathPoints.length > 0) {
      const startPoint = this.pathPoints[0];
      this.camera.position.copy(startPoint.position);
      this.camera.lookAt(this.pathPoints[1]?.position || startPoint.position);
    }
  }

  /**
   * 停止场景
   */
  stopScenario() {
    if (!this.activeScenario) return;
    
    console.log(`🛑 Stopping scenario: ${this.activeScenario.name}`);
    
    // 清理场景效果
    this._cleanupScenarioEffects();
    
    // 退出第一人称
    this.exitFirstPerson();
    
    // 清理路径
    if (this.pathVisualization) {
      this.scene.remove(this.pathVisualization);
      this.pathVisualization = null;
    }
    
    this.activeScenario = null;
    this.pathPoints = [];
    this.currentPathIndex = 0;
  }

  /**
   * 创建场景效果
   * @private
   */
  _createScenarioEffects(scenario) {
    if (!scenario.effects) return;
    
    scenario.effects.forEach(effect => {
      switch (effect) {
        case 'leak':
          this._createLeakEffect();
          break;
        case 'water':
          this._createWaterEffect();
          break;
      }
    });
  }

  /**
   * 创建漏水效果
   * @private
   */
  _createLeakEffect() {
    // 找到漏水点（货仓位置）
    const leakPosition = new THREE.Vector3(5, 2, 0);
    
    // 创建水滴粒子系统
    const particleCount = 100;
    const particles = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      positions[i3] = leakPosition.x + (Math.random() - 0.5) * 0.5;
      positions[i3 + 1] = leakPosition.y;
      positions[i3 + 2] = leakPosition.z + (Math.random() - 0.5) * 0.5;
      
      velocities[i3] = (Math.random() - 0.5) * 0.1;
      velocities[i3 + 1] = -Math.random() * 0.5;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.1;
    }
    
    particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particles.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x4a9eff,
      size: 0.1,
      transparent: true,
      opacity: 0.8
    });
    
    const particleSystem = new THREE.Points(particles, particleMaterial);
    particleSystem.userData = {
      type: 'leak',
      velocities: velocities,
      leakPosition: leakPosition
    };
    
    this.scene.add(particleSystem);
    
    // 创建漏水标记
    const leakMarker = new THREE.Mesh(
      new THREE.SphereGeometry(0.3, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0xff0000,
        emissive: 0xff0000,
        emissiveIntensity: 1.0,
        transparent: true,
        opacity: 0.7
      })
    );
    leakMarker.position.copy(leakPosition);
    leakMarker.userData = { type: 'leakMarker' };
    this.scene.add(leakMarker);
    
    // 保存引用
    if (!this.activeScenario.effectObjects) {
      this.activeScenario.effectObjects = [];
    }
    this.activeScenario.effectObjects.push(particleSystem, leakMarker);
  }

  /**
   * 创建积水效果
   * @private
   */
  _createWaterEffect() {
    // 在漏水点下方创建积水平面
    const waterGeometry = new THREE.PlaneGeometry(3, 3);
    const waterMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a9eff,
      transparent: true,
      opacity: 0.6,
      metalness: 0.1,
      roughness: 0.9
    });
    
    const waterPlane = new THREE.Mesh(waterGeometry, waterMaterial);
    waterPlane.rotation.x = -Math.PI / 2;
    waterPlane.position.set(5, 1.5, 0);
    waterPlane.userData = { type: 'water' };
    
    this.scene.add(waterPlane);
    
    if (!this.activeScenario.effectObjects) {
      this.activeScenario.effectObjects = [];
    }
    this.activeScenario.effectObjects.push(waterPlane);
  }

  /**
   * 清理场景效果
   * @private
   */
  _cleanupScenarioEffects() {
    if (!this.activeScenario || !this.activeScenario.effectObjects) return;
    
    this.activeScenario.effectObjects.forEach(obj => {
      this.scene.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.dispose());
        } else {
          obj.material.dispose();
        }
      }
    });
    
    this.activeScenario.effectObjects = [];
  }

  /**
   * 创建路径可视化
   * @private
   */
  _createPathVisualization() {
    if (this.pathPoints.length < 2) return;
    
    const pathGroup = new THREE.Group();
    pathGroup.name = 'ScenarioPath';
    
    // 创建路径线
    const points = this.pathPoints.map(p => p.position);
    const curve = new THREE.CatmullRomCurve3(points);
    const geometry = new THREE.TubeGeometry(curve, 50, 0.1, 8, false);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.5
    });
    const pathLine = new THREE.Mesh(geometry, material);
    pathGroup.add(pathLine);
    
    // 创建路径点标记
    this.pathPoints.forEach((point, index) => {
      const markerGeometry = new THREE.SphereGeometry(0.2, 16, 16);
      let markerMaterial;
      
      if (point.type === 'start') {
        markerMaterial = new THREE.MeshBasicMaterial({
          color: 0x00ff00,
          emissive: 0x00ff00,
          emissiveIntensity: 1.0
        });
      } else if (point.type === 'target') {
        markerMaterial = new THREE.MeshBasicMaterial({
          color: 0xff0000,
          emissive: 0xff0000,
          emissiveIntensity: 1.0
        });
      } else {
        markerMaterial = new THREE.MeshBasicMaterial({
          color: 0xffff00,
          emissive: 0xffff00,
          emissiveIntensity: 0.8
        });
      }
      
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.copy(point.position);
      marker.userData = { pointIndex: index, pointName: point.name };
      pathGroup.add(marker);
      
      // 添加文字标签
      const label = this._createPathLabel(point.name, point.position);
      pathGroup.add(label);
    });
    
    this.scene.add(pathGroup);
    this.pathVisualization = pathGroup;
  }

  /**
   * 创建路径标签
   * @private
   */
  _createPathLabel(text, position) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = 'bold 20px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.copy(position);
    sprite.position.y += 0.5;
    sprite.scale.set(2, 0.5, 1);
    
    return sprite;
  }

  /**
   * 进入第一人称视角
   */
  enterFirstPerson() {
    this.isFirstPerson = true;
    this.camera.fov = 75;
    this.camera.updateProjectionMatrix();
    
    // 锁定鼠标指针（可选）
    // document.body.requestPointerLock();
    
    console.log('👁️ 进入第一人称视角 | Entered first-person view');
  }

  /**
   * 退出第一人称视角
   */
  exitFirstPerson() {
    this.isFirstPerson = false;
    
    // 解锁鼠标指针
    // document.exitPointerLock();
    
    console.log('👁️ 退出第一人称视角 | Exited first-person view');
  }

  /**
   * 更新场景
   */
  update(deltaTime) {
    if (!this.activeScenario) return;
    
    // 更新第一人称移动
    if (this.isFirstPerson) {
      this._updateFirstPersonMovement(deltaTime);
    }
    
    // 更新场景效果
    this._updateScenarioEffects(deltaTime);
  }

  /**
   * 更新第一人称移动
   * @private
   */
  _updateFirstPersonMovement(deltaTime) {
    const controls = this.firstPersonControls;
    const moveSpeed = controls.moveSpeed * deltaTime;
    
    // 计算移动方向
    const direction = new THREE.Vector3();
    const right = new THREE.Vector3();
    
    // 获取相机方向
    this.camera.getWorldDirection(direction);
    right.crossVectors(direction, this.camera.up).normalize();
    
    // 前后移动
    if (controls.keys.forward) {
      this.camera.position.addScaledVector(direction, moveSpeed);
    }
    if (controls.keys.backward) {
      this.camera.position.addScaledVector(direction, -moveSpeed);
    }
    
    // 左右移动
    if (controls.keys.left) {
      this.camera.position.addScaledVector(right, -moveSpeed);
    }
    if (controls.keys.right) {
      this.camera.position.addScaledVector(right, moveSpeed);
    }
  }

  /**
   * 更新场景效果
   * @private
   */
  _updateScenarioEffects(deltaTime) {
    if (!this.activeScenario || !this.activeScenario.effectObjects) return;
    
    this.activeScenario.effectObjects.forEach(obj => {
      if (obj.userData.type === 'leak' && obj.geometry) {
        // 更新漏水粒子
        const positions = obj.geometry.attributes.position.array;
        const velocities = obj.userData.velocities;
        const leakPos = obj.userData.leakPosition;
        
        for (let i = 0; i < positions.length; i += 3) {
          // 更新位置
          positions[i] += velocities[i] * deltaTime;
          positions[i + 1] += velocities[i + 1] * deltaTime;
          positions[i + 2] += velocities[i + 2] * deltaTime;
          
          // 如果粒子掉到地面以下，重置到漏水点
          if (positions[i + 1] < leakPos.y - 2) {
            positions[i] = leakPos.x + (Math.random() - 0.5) * 0.5;
            positions[i + 1] = leakPos.y;
            positions[i + 2] = leakPos.z + (Math.random() - 0.5) * 0.5;
            
            velocities[i] = (Math.random() - 0.5) * 0.1;
            velocities[i + 1] = -Math.random() * 0.5;
            velocities[i + 2] = (Math.random() - 0.5) * 0.1;
          }
        }
        
        obj.geometry.attributes.position.needsUpdate = true;
      }
    });
  }

  /**
   * 跟随路径
   */
  followPath(speed = 1.0) {
    if (this.pathPoints.length === 0 || this.currentPathIndex >= this.pathPoints.length - 1) {
      return false; // 路径完成
    }
    
    const current = this.pathPoints[this.currentPathIndex];
    const next = this.pathPoints[this.currentPathIndex + 1];
    
    const direction = new THREE.Vector3().subVectors(next.position, this.camera.position);
    const distance = direction.length();
    
    if (distance < 0.5) {
      // 到达当前点，移动到下一个点
      this.currentPathIndex++;
      if (this.currentPathIndex >= this.pathPoints.length - 1) {
        console.log('✅ 到达目标点 | Reached target point');
        return false;
      }
    } else {
      // 向目标点移动
      direction.normalize();
      this.camera.position.addScaledVector(direction, speed * 0.016); // 假设60fps
      this.camera.lookAt(next.position);
    }
    
    return true; // 路径未完成
  }

  /**
   * 获取可用场景列表
   */
  getAvailableScenarios() {
    return Array.from(this.scenarios.values());
  }

  /**
   * 获取当前活动场景
   */
  getActiveScenario() {
    return this.activeScenario;
  }
}



