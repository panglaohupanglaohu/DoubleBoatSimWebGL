/**
 * 消防演练场景
 * Fire Drill Scenario
 * 
 * 模拟火灾应急演练，包括：
 * - 火灾点定位
 * - 烟雾和火焰效果
 * - 应急响应流程
 * - 人员疏散路径
 * - 消防设备使用
 */

import * as THREE from '../../public/lib/three.module.js';

export class FireDrillScenario {
  constructor(scene, camera, cabinManager, shipController) {
    this.scene = scene;
    this.camera = camera;
    this.cabinManager = cabinManager;
    this.shipController = shipController;
    
    this.isRunning = false;
    this.currentPhase = 0;
    this.fireLocation = null;
    this.smokeParticles = null;
    this.flameParticles = null;
    this.evacuationPath = [];
    this.startTime = null;
    
    // 演练配置
    this.config = {
      fireIntensity: 1.0, // 0-1
      smokeDensity: 1.0,
      evacuationSpeed: 3.0,
      autoStart: false
    };
    
    // 演练阶段
    this.phases = [
      { name: '火灾发现', duration: 5 },
      { name: '报警响应', duration: 3 },
      { name: '人员疏散', duration: 10 },
      { name: '消防处置', duration: 15 },
      { name: '演练结束', duration: 2 }
    ];
  }

  /**
   * 初始化消防演练
   */
  initialize() {
    this._createFireEffects();
    this._createEvacuationPath();
    console.log('✅ 消防演练场景初始化完成 | Fire drill scenario initialized');
  }

  /**
   * 开始消防演练
   * @param {string} cabinId - 火灾发生的舱室ID（可选，随机选择）
   */
  start(cabinId = null) {
    if (this.isRunning) {
      console.warn('⚠️ 消防演练已在进行中 | Fire drill already running');
      return;
    }
    
    // 选择火灾位置
    if (!cabinId) {
      const cabins = Array.from(this.cabinManager.cabins.values());
      if (cabins.length > 0) {
        const randomCabin = cabins[Math.floor(Math.random() * cabins.length)];
        cabinId = randomCabin.id;
      }
    }
    
    const cabin = this.cabinManager.cabins.get(cabinId);
    if (!cabin) {
      console.error('❌ 无法开始消防演练：舱室不存在 | Cannot start fire drill: cabin not found');
      return;
    }
    
    this.fireLocation = cabin.bounds.getCenter(new THREE.Vector3());
    const shipPos = this.shipController.body 
      ? new THREE.Vector3(
          this.shipController.body.position.x,
          this.shipController.body.position.y,
          this.shipController.body.position.z
        )
      : new THREE.Vector3(0, 0, 0);
    
    this.fireLocation.add(shipPos);
    
    this.isRunning = true;
    this.currentPhase = 0;
    this.startTime = Date.now();
    this.phaseStartTime = Date.now();
    
    console.log(`🔥 开始消防演练 | Starting fire drill at: ${cabin.name}`);
    this._startPhase(0);
  }

  /**
   * 停止演练
   */
  stop() {
    this.isRunning = false;
    this._cleanupEffects();
    console.log('⏹️ 消防演练已停止 | Fire drill stopped');
  }

  /**
   * 开始演练阶段
   * @private
   */
  _startPhase(phaseIndex) {
    if (phaseIndex >= this.phases.length) {
      this._complete();
      return;
    }
    
    this.currentPhase = phaseIndex;
    this.phaseStartTime = Date.now();
    const phase = this.phases[phaseIndex];
    
    console.log(`📋 演练阶段 ${phaseIndex + 1}/${this.phases.length}: ${phase.name} | Phase ${phaseIndex + 1}/${this.phases.length}: ${phase.name}`);
    
    // 根据阶段执行不同操作
    switch (phaseIndex) {
      case 0: // 火灾发现
        this._showFire();
        break;
      case 1: // 报警响应
        this._triggerAlarm();
        break;
      case 2: // 人员疏散
        this._startEvacuation();
        break;
      case 3: // 消防处置
        this._startFirefighting();
        break;
      case 4: // 演练结束
        this._extinguishFire();
        break;
    }
    
    // 设置下一阶段
    setTimeout(() => {
      if (this.isRunning) {
        this._startPhase(phaseIndex + 1);
      }
    }, phase.duration * 1000);
  }

  /**
   * 显示火灾效果
   * @private
   */
  _showFire() {
    if (!this.fireLocation) return;
    
    // 显示火焰粒子
    if (this.flameParticles) {
      this.flameParticles.position.copy(this.fireLocation);
      this.flameParticles.visible = true;
    }
    
    // 显示烟雾
    if (this.smokeParticles) {
      this.smokeParticles.position.copy(this.fireLocation);
      this.smokeParticles.visible = true;
    }
  }

  /**
   * 触发报警
   * @private
   */
  _triggerAlarm() {
    console.log('🚨 火灾报警已触发 | Fire alarm triggered');
    // 可以添加声音或视觉提示
  }

  /**
   * 开始疏散
   * @private
   */
  _startEvacuation() {
    console.log('🚶 开始人员疏散 | Starting evacuation');
    // 显示疏散路径
    this._showEvacuationPath();
  }

  /**
   * 开始消防处置
   * @private
   */
  _startFirefighting() {
    console.log('💧 开始消防处置 | Starting firefighting');
    // 模拟消防设备使用
    this.config.fireIntensity *= 0.8; // 逐渐减小
  }

  /**
   * 扑灭火灾
   * @private
   */
  _extinguishFire() {
    console.log('✅ 火灾已扑灭 | Fire extinguished');
    this.config.fireIntensity = 0;
    if (this.flameParticles) {
      this.flameParticles.visible = false;
    }
  }

  /**
   * 创建火灾效果
   * @private
   */
  _createFireEffects() {
    // 创建火焰粒子系统
    const flameGeometry = new THREE.BufferGeometry();
    const flameCount = 200;
    const positions = new Float32Array(flameCount * 3);
    const colors = new Float32Array(flameCount * 3);
    const sizes = new Float32Array(flameCount);
    
    for (let i = 0; i < flameCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 2;
      positions[i * 3 + 1] = Math.random() * 3;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 2;
      
      // 火焰颜色（红-橙-黄）
      const hue = Math.random() * 0.1; // 0-0.1 (红色到黄色)
      colors[i * 3] = 1.0; // R
      colors[i * 3 + 1] = 0.3 + Math.random() * 0.4; // G
      colors[i * 3 + 2] = 0.0; // B
      
      sizes[i] = 0.1 + Math.random() * 0.2;
    }
    
    flameGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    flameGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    flameGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    const flameMaterial = new THREE.PointsMaterial({
      size: 0.3,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });
    
    this.flameParticles = new THREE.Points(flameGeometry, flameMaterial);
    this.flameParticles.visible = false;
    this.scene.add(this.flameParticles);
    
    // 创建烟雾粒子系统
    const smokeGeometry = new THREE.BufferGeometry();
    const smokeCount = 500;
    const smokePositions = new Float32Array(smokeCount * 3);
    const smokeSizes = new Float32Array(smokeCount);
    
    for (let i = 0; i < smokeCount; i++) {
      smokePositions[i * 3] = (Math.random() - 0.5) * 5;
      smokePositions[i * 3 + 1] = Math.random() * 8;
      smokePositions[i * 3 + 2] = (Math.random() - 0.5) * 5;
      smokeSizes[i] = 0.5 + Math.random() * 1.0;
    }
    
    smokeGeometry.setAttribute('position', new THREE.BufferAttribute(smokePositions, 3));
    smokeGeometry.setAttribute('size', new THREE.BufferAttribute(smokeSizes, 1));
    
    const smokeMaterial = new THREE.PointsMaterial({
      color: 0x333333,
      size: 1.0,
      transparent: true,
      opacity: 0.4,
      depthWrite: false
    });
    
    this.smokeParticles = new THREE.Points(smokeGeometry, smokeMaterial);
    this.smokeParticles.visible = false;
    this.scene.add(this.smokeParticles);
  }

  /**
   * 创建疏散路径
   * @private
   */
  _createEvacuationPath() {
    // 简单的疏散路径：从火灾点向最近的出口
    this.evacuationPath = [];
    
    if (!this.fireLocation) return;
    
    // 假设出口在船体外部
    const exitPoint = this.fireLocation.clone();
    exitPoint.x += 20; // 向右侧
    exitPoint.y = 0; // 到甲板层
    
    this.evacuationPath.push(this.fireLocation.clone());
    this.evacuationPath.push(exitPoint);
  }

  /**
   * 显示疏散路径
   * @private
   */
  _showEvacuationPath() {
    if (this.evacuationPath.length < 2) return;
    
    // 创建路径可视化
    const pathGeometry = new THREE.BufferGeometry().setFromPoints(this.evacuationPath);
    const pathMaterial = new THREE.LineBasicMaterial({
      color: 0x00ff00,
      linewidth: 3
    });
    const pathLine = new THREE.Line(pathGeometry, pathMaterial);
    this.scene.add(pathLine);
    
    // 存储以便后续清理
    this.evacuationPathLine = pathLine;
  }

  /**
   * 清理效果
   * @private
   */
  _cleanupEffects() {
    if (this.flameParticles) {
      this.flameParticles.visible = false;
    }
    if (this.smokeParticles) {
      this.smokeParticles.visible = false;
    }
    if (this.evacuationPathLine) {
      this.scene.remove(this.evacuationPathLine);
      this.evacuationPathLine = null;
    }
  }

  /**
   * 更新演练动画
   */
  update(deltaTime) {
    if (!this.isRunning) return;
    
    // 更新火焰动画
    if (this.flameParticles && this.flameParticles.visible) {
      const positions = this.flameParticles.geometry.attributes.position.array;
      const time = Date.now() * 0.001;
      
      for (let i = 0; i < positions.length / 3; i++) {
        // 火焰向上飘动
        positions[i * 3 + 1] += deltaTime * (1 + Math.random() * 0.5) * this.config.fireIntensity;
        
        // 重置超出范围的粒子
        if (positions[i * 3 + 1] > 5) {
          positions[i * 3 + 1] = 0;
          positions[i * 3] = (Math.random() - 0.5) * 2;
          positions[i * 3 + 2] = (Math.random() - 0.5) * 2;
        }
        
        // 火焰摆动
        positions[i * 3] += Math.sin(time * 2 + i) * 0.01;
        positions[i * 3 + 2] += Math.cos(time * 2 + i) * 0.01;
      }
      
      this.flameParticles.geometry.attributes.position.needsUpdate = true;
    }
    
    // 更新烟雾动画
    if (this.smokeParticles && this.smokeParticles.visible) {
      const positions = this.smokeParticles.geometry.attributes.position.array;
      
      for (let i = 0; i < positions.length / 3; i++) {
        // 烟雾向上扩散
        positions[i * 3 + 1] += deltaTime * 0.5 * this.config.smokeDensity;
        
        // 烟雾横向扩散
        positions[i * 3] += (Math.random() - 0.5) * deltaTime * 0.2;
        positions[i * 3 + 2] += (Math.random() - 0.5) * deltaTime * 0.2;
        
        // 重置超出范围的粒子
        if (positions[i * 3 + 1] > 15) {
          positions[i * 3 + 1] = 0;
          positions[i * 3] = (Math.random() - 0.5) * 5;
          positions[i * 3 + 2] = (Math.random() - 0.5) * 5;
        }
      }
      
      this.smokeParticles.geometry.attributes.position.needsUpdate = true;
    }
  }

  /**
   * 完成演练
   * @private
   */
  _complete() {
    this.isRunning = false;
    const duration = (Date.now() - this.startTime) / 1000;
    
    console.log(`✅ 消防演练完成 | Fire drill completed in ${duration.toFixed(1)}s`);
    
    // 清理效果
    setTimeout(() => {
      this._cleanupEffects();
    }, 2000);
    
    // 触发完成事件
    if (this.onComplete) {
      this.onComplete({
        duration,
        phases: this.phases.length,
        fireLocation: this.fireLocation
      });
    }
  }

  /**
   * 获取演练状态
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      currentPhase: this.currentPhase,
      phaseName: this.phases[this.currentPhase]?.name || 'Unknown',
      fireLocation: this.fireLocation,
      fireIntensity: this.config.fireIntensity
    };
  }
}

