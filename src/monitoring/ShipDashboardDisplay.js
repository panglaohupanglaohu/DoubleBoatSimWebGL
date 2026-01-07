/**
 * 船舶仪表盘显示系统
 * Ship Dashboard Display System
 * 
 * 模拟船舶驾驶舱仪表盘结构，形象化显示各类数据
 */

import * as THREE from '../../public/lib/three.module.js';

export class ShipDashboardDisplay {
  constructor(scene, dataSource) {
    this.scene = scene;
    this.dataSource = dataSource;
    
    this.dashboards = new Map(); // 仪表盘对象映射
    this.updateInterval = 200; // 更新间隔（ms）
    this.lastUpdate = 0;
  }

  /**
   * 初始化仪表盘系统
   */
  initialize() {
    try {
      // 创建设备运行数据仪表盘
      this._createEquipmentDashboard();
      
      // 创建能源与动力数据仪表盘
      this._createEnergyDashboard();
      
      // 创建结构健康数据仪表盘
      this._createStructureDashboard();
      
      // 创建泵阀系统数据仪表盘
      this._createPumpValveDashboard();
      
      console.log('✅ Ship dashboard display system initialized');
    } catch (error) {
      console.error('❌ Error initializing dashboard display system:', error);
      throw error;
    }
  }

  /**
   * 创建圆形仪表盘
   * @param {Object} config - 配置对象
   * @returns {Object} 包含仪表盘组件的对象
   */
  _createCircularGauge(config) {
    const {
      name = 'Gauge',
      min = 0,
      max = 100,
      value = 0,
      unit = '',
      color = 0x00ff00,
      size = 1.0
    } = config;

    const group = new THREE.Group();
    group.name = name;

    // 创建仪表盘外圈
    const outerRadius = size * 0.5;
    const innerRadius = size * 0.4;
    const segments = 64;
    
    const outerGeometry = new THREE.RingGeometry(innerRadius, outerRadius, segments);
    const outerMaterial = new THREE.MeshBasicMaterial({
      color: 0x333333,
      side: THREE.DoubleSide
    });
    const outerRing = new THREE.Mesh(outerGeometry, outerMaterial);
    outerRing.rotation.x = -Math.PI / 2;
    group.add(outerRing);

    // 创建刻度环
    const scaleGeometry = new THREE.RingGeometry(innerRadius * 0.95, innerRadius, segments);
    const scaleMaterial = new THREE.MeshBasicMaterial({
      color: 0x666666,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.5
    });
    const scaleRing = new THREE.Mesh(scaleGeometry, scaleMaterial);
    scaleRing.rotation.x = -Math.PI / 2;
    group.add(scaleRing);

    // 创建指针
    const pointerGeometry = new THREE.BoxGeometry(0.02, outerRadius * 0.6, 0.01);
    const pointerMaterial = new THREE.MeshBasicMaterial({ color: color });
    const pointer = new THREE.Mesh(pointerGeometry, pointerMaterial);
    pointer.position.y = outerRadius * 0.3;
    pointer.rotation.z = -Math.PI / 2;
    group.add(pointer);

    // 创建中心圆盘
    const centerGeometry = new THREE.CylinderGeometry(outerRadius * 0.15, outerRadius * 0.15, 0.05, 32);
    const centerMaterial = new THREE.MeshBasicMaterial({ color: 0x222222 });
    const centerDisk = new THREE.Mesh(centerGeometry, centerMaterial);
    centerDisk.rotation.x = Math.PI / 2;
    group.add(centerDisk);

    // 创建数值标签（使用Sprite）
    const label = this._createTextSprite(`${value.toFixed(1)}${unit}`, 0, -outerRadius * 0.7);
    group.add(label);

    // 创建标题标签
    const titleLabel = this._createTextSprite(name, 0, outerRadius * 0.8, 0.3);
    group.add(titleLabel);

    return {
      group: group,
      pointer: pointer,
      valueLabel: label,
      titleLabel: titleLabel,
      min: min,
      max: max
    };
  }

  /**
   * 创建条形仪表
   * @param {Object} config - 配置对象
   * @returns {Object} 包含条形仪表组件的对象
   */
  _createBarGauge(config) {
    const {
      name = 'Bar',
      min = 0,
      max = 100,
      value = 0,
      unit = '',
      color = 0x00ff00,
      width = 1.0,
      height = 0.2
    } = config;

    const group = new THREE.Group();
    group.name = name;

    // 创建背景条
    const bgGeometry = new THREE.BoxGeometry(width, height, 0.01);
    const bgMaterial = new THREE.MeshBasicMaterial({
      color: 0x333333,
      transparent: true,
      opacity: 0.5
    });
    const bgBar = new THREE.Mesh(bgGeometry, bgMaterial);
    group.add(bgBar);

    // 创建数值条
    const valueRatio = Math.max(0, Math.min(1, (value - min) / (max - min)));
    const valueWidth = width * valueRatio;
    const valueGeometry = new THREE.BoxGeometry(valueWidth, height * 0.9, 0.02);
    const valueMaterial = new THREE.MeshBasicMaterial({ color: color });
    const valueBar = new THREE.Mesh(valueGeometry, valueMaterial);
    valueBar.position.x = -(width - valueWidth) / 2;
    group.add(valueBar);

    // 创建标签
    const label = this._createTextSprite(`${name}: ${value.toFixed(1)}${unit}`, 0, height * 0.7, 0.25);
    label.userData.unit = unit;
    label.userData.name = name;
    group.add(label);

    return {
      group: group,
      valueBar: valueBar,
      valueLabel: label,
      min: min,
      max: max,
      width: width
    };
  }

  /**
   * 创建状态指示灯
   * @param {Object} config - 配置对象
   * @returns {Object} 包含指示灯的对象
   */
  _createStatusIndicator(config) {
    const {
      name = 'Status',
      status = 'normal', // normal, warning, fault
      size = 0.1
    } = config;

    const group = new THREE.Group();
    group.name = name;

    // 根据状态设置颜色
    const color = status === 'normal' ? 0x00ff00 : 
                  status === 'warning' ? 0xffff00 : 0xff0000;

    // 创建指示灯
    // 使用 MeshStandardMaterial 支持 emissive 属性
    const indicatorGeometry = new THREE.SphereGeometry(size, 16, 16);
    const indicatorMaterial = new THREE.MeshStandardMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 1.0
    });
    const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial);
    group.add(indicator);

    // 创建标签
    const label = this._createTextSprite(name, 0, size * 1.5, 0.2);
    group.add(label);

    return {
      group: group,
      indicator: indicator,
      label: label
    };
  }

  /**
   * 创建文本Sprite
   * @private
   */
  _createTextSprite(text, x, y, scale = 0.4) {
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
    sprite.position.set(x, y, 0);
    sprite.scale.set(scale, scale * 0.25, 1);

    return sprite;
  }

  /**
   * 创建设备运行数据仪表盘
   * @private
   */
  _createEquipmentDashboard() {
    const dashboard = {
      mainEngine: this._createCircularGauge({
        name: '主机转速',
        min: 0,
        max: 2000,
        unit: ' RPM',
        color: 0x00ff00,
        size: 1.2
      }),
      rudder: this._createCircularGauge({
        name: '舵角',
        min: -35,
        max: 35,
        unit: '°',
        color: 0x4a9eff,
        size: 1.0
      }),
      propulsion: this._createBarGauge({
        name: '推进效率',
        min: 0,
        max: 100,
        unit: '%',
        color: 0x00ff00,
        width: 1.5
      }),
      generator: this._createStatusIndicator({
        name: '发电机',
        status: 'normal'
      }),
      crane: this._createStatusIndicator({
        name: '吊机',
        status: 'normal'
      })
    };

    // 创建仪表盘容器组
    const equipmentGroup = new THREE.Group();
    equipmentGroup.name = 'EquipmentDashboard';
    
    // 布局仪表盘（2x3网格）
    dashboard.mainEngine.group.position.set(-1.5, 1, 0);
    dashboard.rudder.group.position.set(1.5, 1, 0);
    dashboard.propulsion.group.position.set(0, 0, 0);
    dashboard.generator.group.position.set(-1.5, -1, 0);
    dashboard.crane.group.position.set(1.5, -1, 0);
    
    // 将所有仪表盘添加到容器组
    Object.values(dashboard).forEach(item => {
      if (item && item.group) {
        equipmentGroup.add(item.group);
      }
    });
    
    // 设置容器位置（船体上方，便于查看）
    equipmentGroup.position.set(0, 20, 0);
    equipmentGroup.visible = false;
    this.scene.add(equipmentGroup);
    
    dashboard.container = equipmentGroup;
    this.dashboards.set('equipment', dashboard);
  }

  /**
   * 创建能源与动力数据仪表盘
   * @private
   */
  _createEnergyDashboard() {
    const dashboard = {
      fuelLevel: this._createCircularGauge({
        name: '燃油储量',
        min: 0,
        max: 100,
        unit: '%',
        color: 0xffaa00,
        size: 1.2
      }),
      fuelConsumption: this._createBarGauge({
        name: '油耗',
        min: 0,
        max: 100,
        unit: ' L/h',
        color: 0xff6600,
        width: 1.5
      }),
      remainingRange: this._createBarGauge({
        name: '剩余航程',
        min: 0,
        max: 1000,
        unit: ' nm',
        color: 0x4a9eff,
        width: 1.5
      }),
      powerLoad: this._createBarGauge({
        name: '电力负载',
        min: 0,
        max: 100,
        unit: '%',
        color: 0x00ff00,
        width: 1.5
      })
    };

    // 创建仪表盘容器组
    const energyGroup = new THREE.Group();
    energyGroup.name = 'EnergyDashboard';
    
    // 布局仪表盘（2x2网格）
    dashboard.fuelLevel.group.position.set(-1, 1, 0);
    dashboard.fuelConsumption.group.position.set(1, 1, 0);
    dashboard.remainingRange.group.position.set(-1, -1, 0);
    dashboard.powerLoad.group.position.set(1, -1, 0);
    
    // 将所有仪表盘添加到容器组
    Object.values(dashboard).forEach(item => {
      if (item && item.group) {
        energyGroup.add(item.group);
      }
    });
    
    // 设置容器位置
    energyGroup.position.set(0, 20, 5);
    energyGroup.visible = false;
    this.scene.add(energyGroup);
    
    dashboard.container = energyGroup;
    this.dashboards.set('energy', dashboard);
  }

  /**
   * 创建结构健康数据仪表盘
   * @private
   */
  _createStructureDashboard() {
    const dashboard = {
      bow: this._createBarGauge({
        name: '船首应力',
        min: 0,
        max: 100,
        unit: ' MPa',
        color: 0x00ff00,
        width: 1.5
      }),
      midship: this._createBarGauge({
        name: '船中应力',
        min: 0,
        max: 100,
        unit: ' MPa',
        color: 0x00ff00,
        width: 1.5
      }),
      stern: this._createBarGauge({
        name: '船尾应力',
        min: 0,
        max: 100,
        unit: ' MPa',
        color: 0x00ff00,
        width: 1.5
      })
    };

    // 创建仪表盘容器组
    const structureGroup = new THREE.Group();
    structureGroup.name = 'StructureDashboard';
    
    // 垂直布局
    dashboard.bow.group.position.set(0, 1.5, 0);
    dashboard.midship.group.position.set(0, 0, 0);
    dashboard.stern.group.position.set(0, -1.5, 0);
    
    // 将所有仪表盘添加到容器组
    Object.values(dashboard).forEach(item => {
      if (item && item.group) {
        structureGroup.add(item.group);
      }
    });
    
    // 设置容器位置
    structureGroup.position.set(0, 20, 10);
    structureGroup.visible = false;
    this.scene.add(structureGroup);
    
    dashboard.container = structureGroup;
    this.dashboards.set('structure', dashboard);
  }

  /**
   * 创建泵阀系统数据仪表盘
   * @private
   */
  _createPumpValveDashboard() {
    const dashboard = {
      pump1: this._createStatusIndicator({
        name: '主泵',
        status: 'normal'
      }),
      pump2: this._createStatusIndicator({
        name: '备用泵',
        status: 'normal'
      }),
      valve1: this._createBarGauge({
        name: '主阀开度',
        min: 0,
        max: 100,
        unit: '%',
        color: 0x4a9eff,
        width: 1.2
      }),
      valve2: this._createBarGauge({
        name: '副阀开度',
        min: 0,
        max: 100,
        unit: '%',
        color: 0x4a9eff,
        width: 1.2
      }),
      flowRate: this._createBarGauge({
        name: '流量',
        min: 0,
        max: 500,
        unit: ' L/min',
        color: 0x00ff00,
        width: 1.5
      })
    };

    // 创建仪表盘容器组
    const pumpValveGroup = new THREE.Group();
    pumpValveGroup.name = 'PumpValveDashboard';
    
    // 布局（2x3网格）
    dashboard.pump1.group.position.set(-1.5, 1.5, 0);
    dashboard.pump2.group.position.set(1.5, 1.5, 0);
    dashboard.valve1.group.position.set(-1.5, 0, 0);
    dashboard.valve2.group.position.set(1.5, 0, 0);
    dashboard.flowRate.group.position.set(0, -1.5, 0);
    
    // 将所有仪表盘添加到容器组
    Object.values(dashboard).forEach(item => {
      if (item && item.group) {
        pumpValveGroup.add(item.group);
      }
    });
    
    // 设置容器位置
    pumpValveGroup.position.set(0, 20, 15);
    pumpValveGroup.visible = false;
    this.scene.add(pumpValveGroup);
    
    dashboard.container = pumpValveGroup;
    this.dashboards.set('pumpValve', dashboard);
  }

  /**
   * 更新仪表盘数据
   */
  update(deltaTime) {
    const now = Date.now();
    if (now - this.lastUpdate < this.updateInterval) return;
    this.lastUpdate = now;

    if (!this.dataSource) return;

    try {
      const data = this.dataSource.getAllData();
      const realtimeData = this.dataSource.getRealtimeData();

      // 更新设备运行数据
      this._updateEquipmentDashboard(data, realtimeData);
      
      // 更新能源与动力数据
      this._updateEnergyDashboard(data, realtimeData);
      
      // 更新结构健康数据
      this._updateStructureDashboard(data);
      
      // 更新泵阀系统数据
      this._updatePumpValveDashboard(data);
    } catch (error) {
      console.error('❌ Error updating dashboard:', error);
    }
  }

  /**
   * 更新设备运行数据仪表盘
   * @private
   */
  _updateEquipmentDashboard(data, realtimeData) {
    const dashboard = this.dashboards.get('equipment');
    if (!dashboard) return;

    // 更新主机转速
    if (dashboard.mainEngine && data.ship?.mainEngine) {
      const rpm = data.ship.mainEngine.rpm || 0;
      const angle = (rpm / dashboard.mainEngine.max) * Math.PI;
      dashboard.mainEngine.pointer.rotation.z = -Math.PI / 2 - angle;
      this._updateTextSprite(dashboard.mainEngine.valueLabel, 
        `${rpm.toFixed(0)} RPM`);
    }

    // 更新舵角
    if (dashboard.rudder && data.ship?.rudder) {
      const angle = data.ship.rudder.angle || 0;
      const normalizedAngle = (angle + 35) / 70; // 归一化到0-1
      const pointerAngle = normalizedAngle * Math.PI;
      dashboard.rudder.pointer.rotation.z = -Math.PI / 2 - pointerAngle;
      this._updateTextSprite(dashboard.rudder.valueLabel, 
        `${angle.toFixed(1)}°`);
    }

    // 更新推进效率
    if (dashboard.propulsion && data.ship?.propulsion) {
      const efficiency = (data.ship.propulsion.efficiency || 0) * 100;
      this._updateBarGauge(dashboard.propulsion, efficiency);
    }

    // 更新发电机状态
    if (dashboard.generator) {
      const status = 'normal'; // 可以从数据中获取
      this._updateStatusIndicator(dashboard.generator, status);
    }

    // 更新吊机状态
    if (dashboard.crane && realtimeData.equipment?.crane) {
      const status = realtimeData.equipment.crane.status;
      this._updateStatusIndicator(dashboard.crane, status);
    }
  }

  /**
   * 更新能源与动力数据仪表盘
   * @private
   */
  _updateEnergyDashboard(data, realtimeData) {
    const dashboard = this.dashboards.get('energy');
    if (!dashboard) return;

    // 更新燃油储量
    if (dashboard.fuelLevel && data.ship?.fuel) {
      const level = data.ship.fuel.level || 0;
      const angle = (level / 100) * Math.PI;
      dashboard.fuelLevel.pointer.rotation.z = -Math.PI / 2 - angle;
      this._updateTextSprite(dashboard.fuelLevel.valueLabel, 
        `${level.toFixed(1)}%`);
    }

    // 更新油耗
    if (dashboard.fuelConsumption && data.ship?.fuel) {
      const consumption = data.ship.fuel.flowRate || 0;
      this._updateBarGauge(dashboard.fuelConsumption, consumption);
    }

    // 更新剩余航程（计算值）
    if (dashboard.remainingRange && data.ship?.fuel) {
      const remaining = data.ship.fuel.remaining || 0;
      const consumption = data.ship.fuel.flowRate || 1;
      const range = remaining / consumption * 0.1; // 简化计算
      this._updateBarGauge(dashboard.remainingRange, range);
    }

    // 更新电力负载（模拟数据）
    if (dashboard.powerLoad) {
      const load = 65; // 可以从数据中获取
      this._updateBarGauge(dashboard.powerLoad, load);
    }
  }

  /**
   * 更新结构健康数据仪表盘
   * @private
   */
  _updateStructureDashboard(data) {
    const dashboard = this.dashboards.get('structure');
    if (!dashboard) return;

    // 更新船首应力
    if (dashboard.bow && data.ship?.structure?.bow) {
      const stress = data.ship.structure.bow.stress || 0;
      this._updateBarGauge(dashboard.bow, stress);
    }

    // 更新船中应力
    if (dashboard.midship && data.ship?.structure?.midship) {
      const stress = data.ship.structure.midship.stress || 0;
      this._updateBarGauge(dashboard.midship, stress);
    }

    // 更新船尾应力
    if (dashboard.stern && data.ship?.structure?.stern) {
      const stress = data.ship.structure.stern.stress || 0;
      this._updateBarGauge(dashboard.stern, stress);
    }
  }

  /**
   * 更新泵阀系统数据仪表盘
   * @private
   */
  _updatePumpValveDashboard(data) {
    const dashboard = this.dashboards.get('pumpValve');
    if (!dashboard) return;

    // 更新泵状态（模拟数据）
    if (dashboard.pump1) {
      this._updateStatusIndicator(dashboard.pump1, 'normal');
    }
    if (dashboard.pump2) {
      this._updateStatusIndicator(dashboard.pump2, 'normal');
    }

    // 更新阀门开度（模拟数据）
    if (dashboard.valve1) {
      this._updateBarGauge(dashboard.valve1, 75);
    }
    if (dashboard.valve2) {
      this._updateBarGauge(dashboard.valve2, 50);
    }

    // 更新流量（模拟数据）
    if (dashboard.flowRate) {
      this._updateBarGauge(dashboard.flowRate, 250);
    }
  }

  /**
   * 更新条形仪表
   * @private
   */
  _updateBarGauge(barGauge, value) {
    if (!barGauge || !barGauge.valueBar) return;

    const ratio = Math.max(0, Math.min(1, (value - barGauge.min) / (barGauge.max - barGauge.min)));
    const newWidth = barGauge.width * ratio;
    
    barGauge.valueBar.scale.x = ratio;
    barGauge.valueBar.position.x = -(barGauge.width - newWidth) / 2;

    // 更新标签
    const unit = barGauge.valueLabel.userData.unit || '';
    const name = barGauge.valueLabel.userData.name || '';
    this._updateTextSprite(barGauge.valueLabel, 
      `${name}: ${value.toFixed(1)}${unit}`);
  }

  /**
   * 更新状态指示灯
   * @private
   */
  _updateStatusIndicator(indicator, status) {
    // 安全检查：确保indicator对象和其属性存在
    if (!indicator) {
      console.warn('⚠️ Status indicator is undefined');
      return;
    }
    
    if (!indicator.indicator) {
      console.warn('⚠️ Status indicator.indicator is undefined');
      return;
    }
    
    if (!indicator.indicator.material) {
      console.warn('⚠️ Status indicator material is undefined');
      return;
    }

    const color = status === 'normal' ? 0x00ff00 : 
                  status === 'warning' ? 0xffff00 : 0xff0000;
    
    try {
      // 安全地设置颜色
      if (indicator.indicator.material.color) {
        indicator.indicator.material.color.setHex(color);
      }
      
      // 安全地设置自发光颜色
      // MeshBasicMaterial支持emissive，但需要检查是否存在
      if (indicator.indicator.material.emissive) {
        indicator.indicator.material.emissive.setHex(color);
      } else {
        // 如果emissive不存在，创建它（对于MeshBasicMaterial应该总是存在）
        // 但为了安全，我们检查material类型
        if (indicator.indicator.material.isMeshBasicMaterial) {
          // MeshBasicMaterial应该已经有emissive，如果不存在可能是版本问题
          indicator.indicator.material.emissive = new THREE.Color(color);
          indicator.indicator.material.emissiveIntensity = 1.0;
        }
      }
    } catch (error) {
      console.warn('⚠️ Error updating status indicator:', error);
    }
  }

  /**
   * 更新文本Sprite
   * @private
   */
  _updateTextSprite(sprite, text) {
    if (!sprite || !sprite.material) return;

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

    sprite.material.map.dispose();
    sprite.material.map = new THREE.CanvasTexture(canvas);
    sprite.material.needsUpdate = true;
  }

  /**
   * 显示/隐藏仪表盘
   */
  showDashboard(name, visible = true) {
    const dashboard = this.dashboards.get(name);
    if (!dashboard) return;

    // 通过容器组控制可见性
    if (dashboard.container) {
      dashboard.container.visible = visible;
    } else {
      // 兼容旧方式
      Object.values(dashboard).forEach(item => {
        if (item && item.group) {
          item.group.visible = visible;
        }
      });
    }
  }

  /**
   * 获取仪表盘对象
   */
  getDashboard(name) {
    return this.dashboards.get(name);
  }
}

