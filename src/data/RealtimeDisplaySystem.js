/**
 * 实时数据显示系统
 * Realtime Display System
 * 
 * 管理船内外实时数据的虚拟对象显示
 */

import * as THREE from '../../public/lib/three.module.js';

export class RealtimeDisplaySystem {
  constructor(scene, dataSource) {
    this.scene = scene;
    this.dataSource = dataSource; // 数据源（VirtualDataSource或真实数据源）
    
    this.displayObjects = new Map(); // 显示对象映射
    this.labels = new Map(); // 标签映射
    this.updateInterval = 100; // 更新间隔（ms）
    this.lastUpdate = 0;
  }

  /**
   * 初始化显示系统
   */
  initialize() {
    try {
      // 创建船内数据对象
      this._createOnboardDisplays();
      
      // 创建船外数据对象（暂时禁用海上目标物，避免显示圆锥体）
      // this._createOffboardDisplays();
      
      console.log('✅ Realtime display system initialized');
    } catch (error) {
      console.error('❌ Error initializing realtime display system:', error);
      throw error;
    }
  }

  /**
   * 创建船内数据显示对象
   * @private
   */
  _createOnboardDisplays() {
    try {
      // 燃油显示
      this._createFuelDisplay();
      
      // 关键设备状态显示
      this._createEquipmentDisplays();
      
      // 人员位置显示
      this._createPersonnelDisplays();
      
      // 实验任务状态显示
      this._createExperimentDisplays();
      
      // 仓储物资显示
      this._createInventoryDisplays();
    } catch (error) {
      console.error('❌ Error creating onboard displays:', error);
    }
  }

  /**
   * 创建燃油显示
   * @private
   */
  _createFuelDisplay() {
    const fuelGroup = new THREE.Group();
    fuelGroup.name = 'FuelDisplay';
    
    // 燃油表盘（3D对象）
    const gaugeGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.1, 32);
    const gaugeMaterial = new THREE.MeshStandardMaterial({
      color: 0x333333,
      metalness: 0.8,
      roughness: 0.2
    });
    const gauge = new THREE.Mesh(gaugeGeometry, gaugeMaterial);
    gauge.position.set(0, 0, 0);
    fuelGroup.add(gauge);
    
    // 指针
    const pointer = new THREE.Mesh(
      new THREE.BoxGeometry(0.05, 0.15, 0.05),
      new THREE.MeshStandardMaterial({ color: 0xff0000 })
    );
    pointer.position.set(0, 0.1, 0);
    fuelGroup.add(pointer);
    
    // 标签
    const label = this._createTextLabel('燃油 | Fuel', 0, 0.5, 0);
    fuelGroup.add(label);
    
    // 数值显示
    const valueLabel = this._createTextLabel('100%', 0, -0.3, 0, 0.3);
    fuelGroup.add(valueLabel);
    
    // 设置燃油显示位置（船体左前方，船舱内）
    fuelGroup.position.set(-15, 8, -20);
    fuelGroup.scale.set(3, 3, 3); // 放大以便可见
    
    this.displayObjects.set('fuel', {
      group: fuelGroup,
      pointer: pointer,
      valueLabel: valueLabel,
      type: 'gauge'
    });
    
    this.scene.add(fuelGroup);
  }

  /**
   * 创建设备状态显示
   * @private
   */
  _createEquipmentDisplays() {
    // 吊机状态
    const craneGroup = new THREE.Group();
    craneGroup.name = 'CraneDisplay';
    
    // 状态指示器（LED灯）
    // 使用 MeshStandardMaterial 支持 emissive 属性
    const statusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshStandardMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    craneGroup.add(statusLight);
    
    const label = this._createTextLabel('吊机 | Crane', 0, 0.3, 0);
    craneGroup.add(label);
    
    const valueLabel = this._createTextLabel('正常 | Normal', 0, -0.2, 0, 0.25);
    craneGroup.add(valueLabel);
    
    // 设置吊机显示位置（船体右中部，甲板上）
    craneGroup.position.set(20, 12, 0);
    craneGroup.scale.set(4, 4, 4); // 放大以便可见
    
    this.displayObjects.set('crane', {
      group: craneGroup,
      statusLight: statusLight,
      valueLabel: valueLabel,
      type: 'status'
    });
    
    this.scene.add(craneGroup);
  }

  /**
   * 创建人员位置显示
   * @private
   */
  _createPersonnelDisplays() {
    const personnelGroup = new THREE.Group();
    personnelGroup.name = 'PersonnelDisplay';
    
    // 人员标记点
    for (let i = 0; i < 3; i++) {
      const marker = new THREE.Mesh(
        new THREE.SphereGeometry(0.15, 16, 16),
        new THREE.MeshBasicMaterial({
          color: 0x4a9eff,
          transparent: true,
          opacity: 0.8
        })
      );
      marker.position.set(i * 2 - 2, 0, 0);
      personnelGroup.add(marker);
    }
    
    const label = this._createTextLabel('人员 | Personnel', 0, 0.5, 0);
    personnelGroup.add(label);
    
    // 设置人员显示位置（船体中部，甲板层）
    personnelGroup.position.set(0, 10, 10);
    personnelGroup.scale.set(2, 2, 2);
    
    this.displayObjects.set('personnel', {
      group: personnelGroup,
      markers: personnelGroup.children.filter(c => c.type === 'Mesh'),
      type: 'markers'
    });
    
    this.scene.add(personnelGroup);
  }

  /**
   * 创建实验任务显示
   * @private
   */
  _createExperimentDisplays() {
    const experimentGroup = new THREE.Group();
    experimentGroup.name = 'ExperimentDisplay';
    
    // 进度条
    const progressBarBg = new THREE.Mesh(
      new THREE.BoxGeometry(2, 0.1, 0.05),
      new THREE.MeshStandardMaterial({ color: 0x333333 })
    );
    experimentGroup.add(progressBarBg);
    
    const progressBar = new THREE.Mesh(
      new THREE.BoxGeometry(1, 0.08, 0.05),
      new THREE.MeshStandardMaterial({ color: 0x4caf50 })
    );
    progressBar.position.x = -0.5;
    experimentGroup.add(progressBar);
    
    const label = this._createTextLabel('实验任务 | Experiment', 0, 0.4, 0);
    experimentGroup.add(label);
    
    const valueLabel = this._createTextLabel('50%', 0, -0.2, 0, 0.25);
    experimentGroup.add(valueLabel);
    
    // 设置实验任务显示位置（船体左后方，实验室区域）
    experimentGroup.position.set(-18, 8, 15);
    experimentGroup.scale.set(2.5, 2.5, 2.5);
    
    this.displayObjects.set('experiment', {
      group: experimentGroup,
      progressBar: progressBar,
      valueLabel: valueLabel,
      type: 'progress'
    });
    
    this.scene.add(experimentGroup);
  }

  /**
   * 创建仓储物资显示
   * @private
   */
  _createInventoryDisplays() {
    const inventoryGroup = new THREE.Group();
    inventoryGroup.name = 'InventoryDisplay';
    
    // 库存指示器
    const indicator = new THREE.Mesh(
      new THREE.BoxGeometry(0.5, 0.5, 0.5),
      new THREE.MeshStandardMaterial({ color: 0xff9800 })
    );
    inventoryGroup.add(indicator);
    
    const label = this._createTextLabel('仓储 | Inventory', 0, 0.5, 0);
    inventoryGroup.add(label);
    
    const valueLabel = this._createTextLabel('充足 | Sufficient', 0, -0.3, 0, 0.25);
    inventoryGroup.add(valueLabel);
    
    // 设置仓储显示位置（船体右后方，货仓区域）
    inventoryGroup.position.set(18, 8, -15);
    inventoryGroup.scale.set(3, 3, 3);
    
    this.displayObjects.set('inventory', {
      group: inventoryGroup,
      indicator: indicator,
      valueLabel: valueLabel,
      type: 'indicator'
    });
    
    this.scene.add(inventoryGroup);
  }

  /**
   * 创建船外数据显示对象
   * @private
   */
  _createOffboardDisplays() {
    // 环境数据显示（风、海况）
    this._createEnvironmentDisplays();
    
    // 海上目标物显示
    this._createMaritimeTargets();
  }

  /**
   * 创建环境数据显示
   * @private
   */
  _createEnvironmentDisplays() {
    // 风向指示器
    const windGroup = new THREE.Group();
    windGroup.name = 'WindDisplay';
    
    // 风向箭头
    const arrow = new THREE.ArrowHelper(
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(0, 0, 0),
      2,
      0x00ff00,
      0.5,
      0.3
    );
    windGroup.add(arrow);
    
    const label = this._createTextLabel('风向 | Wind', 0, 0.5, 0);
    windGroup.add(label);
    
    const valueLabel = this._createTextLabel('15 m/s', 0, -0.3, 0, 0.25);
    windGroup.add(valueLabel);
    
    // 设置风向显示位置（船体上方远处）
    windGroup.position.set(0, 25, 0);
    windGroup.scale.set(5, 5, 5);
    
    this.displayObjects.set('wind', {
      group: windGroup,
      arrow: arrow,
      valueLabel: valueLabel,
      type: 'vector'
    });
    
    this.scene.add(windGroup);
  }

  /**
   * 创建海上目标物显示
   * @private
   */
  _createMaritimeTargets() {
    const targetsGroup = new THREE.Group();
    targetsGroup.name = 'MaritimeTargets';
    
    // 示例：其他船只标记
    for (let i = 0; i < 2; i++) {
      const target = new THREE.Mesh(
        new THREE.ConeGeometry(0.3, 1, 8),
        new THREE.MeshBasicMaterial({
          color: 0xffff00,
          transparent: true,
          opacity: 0.7
        })
      );
      target.position.set(
        (Math.random() - 0.5) * 100,
        0.5,
        (Math.random() - 0.5) * 100
      );
      targetsGroup.add(target);
      
      const label = this._createTextLabel(`目标${i + 1} | Target ${i + 1}`, 0, 1.5, 0, 0.2);
      target.add(label);
    }
    
    this.displayObjects.set('maritimeTargets', {
      group: targetsGroup,
      targets: targetsGroup.children,
      type: 'targets'
    });
    
    this.scene.add(targetsGroup);
  }

  /**
   * 创建文本标签
   * @private
   */
  _createTextLabel(text, x, y, z, scale = 0.4) {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        console.warn('Canvas context not available');
        return null;
      }
      
      // 背景
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(0, 0, 512, 128);
      
      // 文字
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 32px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, 256, 64);
      
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.position.set(x, y, z);
      sprite.scale.set(scale, scale * 0.25, 1);
      
      return sprite;
    } catch (error) {
      console.error('❌ Error creating text label:', error);
      return null;
    }
  }

  /**
   * 更新所有显示对象
   * @param {number} deltaTime 
   */
  update(deltaTime) {
    const now = Date.now();
    if (now - this.lastUpdate < this.updateInterval) return;
    this.lastUpdate = now;
    
    if (!this.dataSource) return;
    
    // 获取实时数据
    const data = this.dataSource.getRealtimeData();
    
    // 更新各个显示对象
    this._updateFuelDisplay(data.fuel);
    this._updateEquipmentDisplays(data.equipment);
    this._updatePersonnelDisplays(data.personnel);
    this._updateExperimentDisplays(data.experiment);
    this._updateInventoryDisplays(data.inventory);
    this._updateEnvironmentDisplays(data.environment);
    this._updateMaritimeTargets(data.maritimeTargets);
  }

  /**
   * 更新燃油显示
   * @private
   */
  _updateFuelDisplay(fuelData) {
    const display = this.displayObjects.get('fuel');
    if (!display || !fuelData) return;
    
    // 检查 level 属性是否存在，提供默认值
    const level = fuelData.level ?? 0;
    
    // 更新指针旋转（0-100% 对应 0-180度）
    const angle = (level / 100) * Math.PI;
    if (display.pointer) {
      display.pointer.rotation.z = -angle;
    }
    
    // 更新数值标签
    this._updateTextLabel(display.valueLabel, `${level.toFixed(1)}%`);
    
    // 根据燃油量改变颜色
    const color = level > 30 ? 0x00ff00 : level > 10 ? 0xffff00 : 0xff0000;
    if (display.pointer && display.pointer.material) {
      display.pointer.material.color.setHex(color);
    }
  }

  /**
   * 更新设备显示
   * @private
   */
  _updateEquipmentDisplays(equipmentData) {
    const display = this.displayObjects.get('crane');
    if (!display || !equipmentData?.crane) return;
    
    // 检查 statusLight 和 material 是否存在
    if (!display.statusLight || !display.statusLight.material) return;
    
    const status = equipmentData.crane.status;
    const color = status === 'normal' ? 0x00ff00 : status === 'warning' ? 0xffff00 : 0xff0000;
    display.statusLight.material.color.setHex(color);
    
    // 检查 emissive 属性是否存在（某些材质可能没有）
    if (display.statusLight.material.emissive) {
      display.statusLight.material.emissive.setHex(color);
    }
    
    this._updateTextLabel(display.valueLabel, 
      status === 'normal' ? '正常 | Normal' : 
      status === 'warning' ? '警告 | Warning' : '故障 | Fault'
    );
  }

  /**
   * 更新人员显示
   * @private
   */
  _updatePersonnelDisplays(personnelData) {
    const display = this.displayObjects.get('personnel');
    if (!display || !personnelData) return;
    
    // 更新人员位置
    personnelData.positions?.forEach((pos, index) => {
      if (display.markers[index]) {
        display.markers[index].position.set(pos.x, pos.y, pos.z);
      }
    });
  }

  /**
   * 更新实验任务显示
   * @private
   */
  _updateExperimentDisplays(experimentData) {
    const display = this.displayObjects.get('experiment');
    if (!display || !experimentData) return;
    
    const progress = experimentData.progress ?? 0;
    if (display.progressBar) {
      display.progressBar.scale.x = progress / 100;
      display.progressBar.position.x = -1 + (progress / 100);
    }
    
    this._updateTextLabel(display.valueLabel, `${progress.toFixed(0)}%`);
  }

  /**
   * 更新仓储显示
   * @private
   */
  _updateInventoryDisplays(inventoryData) {
    const display = this.displayObjects.get('inventory');
    if (!display || !inventoryData) return;
    
    const level = inventoryData.level || 'sufficient';
    const color = level === 'sufficient' ? 0x4caf50 : level === 'low' ? 0xff9800 : 0xf44336;
    if (display.indicator && display.indicator.material) {
      display.indicator.material.color.setHex(color);
    }
    
    this._updateTextLabel(display.valueLabel,
      level === 'sufficient' ? '充足 | Sufficient' :
      level === 'low' ? '不足 | Low' : '紧急 | Critical'
    );
  }

  /**
   * 更新环境显示
   * @private
   */
  _updateEnvironmentDisplays(environmentData) {
    const display = this.displayObjects.get('wind');
    if (!display || !environmentData?.wind) return;
    
    const wind = environmentData.wind;
    const windSpeed = wind.speed ?? 0;
    const windDirection = wind.direction ?? 0;
    
    const direction = new THREE.Vector3(
      Math.cos(windDirection * Math.PI / 180),
      0,
      Math.sin(windDirection * Math.PI / 180)
    );
    
    if (display.arrow) {
      display.arrow.setDirection(direction);
      display.arrow.setLength(windSpeed / 5); // 缩放箭头长度
    }
    
    this._updateTextLabel(display.valueLabel, `${windSpeed.toFixed(1)} m/s`);
  }

  /**
   * 更新海上目标
   * @private
   */
  _updateMaritimeTargets(targetsData) {
    const display = this.displayObjects.get('maritimeTargets');
    if (!display || !targetsData) return;
    
    // 更新目标位置
    targetsData.forEach((target, index) => {
      if (display.targets[index]) {
        display.targets[index].position.set(target.x, target.y, target.z);
      }
    });
  }

  /**
   * 更新文本标签
   * @private
   */
  _updateTextLabel(sprite, text) {
    if (!sprite || !sprite.material.map) return;
    
    const canvas = sprite.material.map.image;
    const ctx = canvas.getContext('2d');
    
    // 清空
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 重绘文字
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 32px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 256, 64);
    
    sprite.material.map.needsUpdate = true;
  }

  /**
   * 设置显示对象位置（相对于船体）
   * @param {string} id 
   * @param {THREE.Vector3} position 
   */
  setDisplayPosition(id, position) {
    const display = this.displayObjects.get(id);
    if (display && display.group) {
      display.group.position.copy(position);
    }
  }

  /**
   * 显示/隐藏显示对象
   * @param {string} id 
   * @param {boolean} visible 
   */
  setDisplayVisible(id, visible) {
    const display = this.displayObjects.get(id);
    if (display && display.group) {
      display.group.visible = visible;
    }
  }
}

