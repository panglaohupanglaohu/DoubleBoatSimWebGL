/**
 * 安全态势监控系统
 * Safety Monitoring System
 * 
 * 实时监控船舶安全状态，包括：
 * - 主机状态
 * - 燃油消耗
 * - 舵机与推进系统健康度
 * - 关键结构应力
 * - 应急设备可用状态
 */

import * as THREE from '../../public/lib/three.module.js';

export class SafetyMonitor {
  constructor(scene, dataSource) {
    this.scene = scene;
    this.dataSource = dataSource; // 数据源（VirtualDataSource或真实数据源）
    
    this.monitoringObjects = new Map(); // 监控对象映射
    this.statusIndicators = new Map(); // 状态指示器映射
    this.alerts = []; // 警报列表
    
    this.updateInterval = 200; // 更新间隔（ms）
    this.lastUpdate = 0;
    
    // 状态阈值
    this.thresholds = {
      mainEngine: {
        temperature: { normal: [60, 90], warning: [50, 100], critical: [0, 50, 100, 200] },
        rpm: { normal: [800, 1200], warning: [700, 1300], critical: [0, 700, 1300, 2000] },
        pressure: { normal: [8, 12], warning: [7, 13], critical: [0, 7, 13, 20] }
      },
      fuel: {
        consumption: { normal: [0, 50], warning: [50, 80], critical: [80, 200] },
        level: { normal: [30, 100], warning: [20, 30], critical: [0, 20] }
      },
      rudder: {
        health: { normal: [80, 100], warning: [60, 80], critical: [0, 60] },
        angle: { normal: [-30, 30], warning: [-45, 45], critical: [-90, -45, 45, 90] }
      },
      propulsion: {
        health: { normal: [80, 100], warning: [60, 80], critical: [0, 60] },
        efficiency: { normal: [85, 100], warning: [70, 85], critical: [0, 70] }
      },
      structure: {
        stress: { normal: [0, 50], warning: [50, 80], critical: [80, 200] }
      },
      emergency: {
        firePump: { available: true },
        lifeboat: { available: true }
      }
    };
  }

  /**
   * 初始化监控系统
   */
  initialize() {
    try {
      // 创建主机状态监控
      this._createMainEngineMonitor();
      
      // 创建燃油消耗监控
      this._createFuelConsumptionMonitor();
      
      // 创建舵机系统监控
      this._createRudderMonitor();
      
      // 创建推进系统监控
      this._createPropulsionMonitor();
      
      // 创建结构应力监控
      this._createStructureStressMonitor();
      
      // 创建应急设备监控
      this._createEmergencyEquipmentMonitor();
      
      console.log('✅ Safety monitoring system initialized');
    } catch (error) {
      console.error('❌ Error initializing safety monitoring system:', error);
      throw error;
    }
  }

  /**
   * 创建主机状态监控
   * @private
   */
  _createMainEngineMonitor() {
    const engineGroup = new THREE.Group();
    engineGroup.name = 'MainEngineMonitor';
    
    // 主机3D模型（简化表示）
    const engineGeometry = new THREE.BoxGeometry(2, 1.5, 1.5);
    const engineMaterial = new THREE.MeshStandardMaterial({
      color: 0x333333,
      metalness: 0.8,
      roughness: 0.2
    });
    const engineMesh = new THREE.Mesh(engineGeometry, engineMaterial);
    engineMesh.position.set(0, 0, 0);
    engineGroup.add(engineMesh);
    
    // 温度指示器
    const tempIndicator = this._createStatusIndicator('温度', 0, 1, 0, 0.3);
    engineGroup.add(tempIndicator);
    
    // 转速指示器
    const rpmIndicator = this._createStatusIndicator('转速', 0, 0.5, 0, 0.3);
    engineGroup.add(rpmIndicator);
    
    // 压力指示器
    const pressureIndicator = this._createStatusIndicator('压力', 0, -0.5, 0, 0.3);
    engineGroup.add(pressureIndicator);
    
    // 状态灯（绿色=正常，黄色=警告，红色=故障）
    const statusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    statusLight.position.set(1, 0, 0);
    engineGroup.add(statusLight);
    
    // 设置位置（船体后部，发动机舱）
    engineGroup.position.set(0, 5, -25);
    engineGroup.scale.set(2, 2, 2);
    
    this.scene.add(engineGroup);
    
    this.monitoringObjects.set('mainEngine', {
      group: engineGroup,
      engineMesh: engineMesh,
      statusLight: statusLight,
      indicators: {
        temperature: tempIndicator,
        rpm: rpmIndicator,
        pressure: pressureIndicator
      },
      type: 'mainEngine'
    });
  }

  /**
   * 创建燃油消耗监控
   * @private
   */
  _createFuelConsumptionMonitor() {
    const fuelGroup = new THREE.Group();
    fuelGroup.name = 'FuelConsumptionMonitor';
    
    // 燃油表
    const gaugeGeometry = new THREE.CylinderGeometry(0.4, 0.4, 0.2, 32);
    const gaugeMaterial = new THREE.MeshStandardMaterial({
      color: 0x444444,
      metalness: 0.7,
      roughness: 0.3
    });
    const gauge = new THREE.Mesh(gaugeGeometry, gaugeMaterial);
    fuelGroup.add(gauge);
    
    // 指针
    const pointer = new THREE.Mesh(
      new THREE.BoxGeometry(0.05, 0.2, 0.05),
      new THREE.MeshStandardMaterial({ color: 0xff0000 })
    );
    pointer.position.set(0, 0.15, 0);
    fuelGroup.add(pointer);
    
    // 标签
    const label = this._createTextLabel('燃油消耗 | Fuel Consumption', 0, 0.5, 0);
    fuelGroup.add(label);
    
    // 数值显示
    const valueLabel = this._createTextLabel('0 L/h', 0, -0.3, 0, 0.25);
    fuelGroup.add(valueLabel);
    
    // 设置位置（船体左前方，燃油舱附近）
    fuelGroup.position.set(-12, 6, -18);
    fuelGroup.scale.set(2.5, 2.5, 2.5);
    
    this.scene.add(fuelGroup);
    
    this.monitoringObjects.set('fuelConsumption', {
      group: fuelGroup,
      gauge: gauge,
      pointer: pointer,
      valueLabel: valueLabel,
      type: 'fuel'
    });
  }

  /**
   * 创建舵机系统监控
   * @private
   */
  _createRudderMonitor() {
    const rudderGroup = new THREE.Group();
    rudderGroup.name = 'RudderMonitor';
    
    // 舵机模型
    const rudderGeometry = new THREE.BoxGeometry(0.5, 1, 0.3);
    const rudderMaterial = new THREE.MeshStandardMaterial({
      color: 0x555555,
      metalness: 0.6,
      roughness: 0.4
    });
    const rudderMesh = new THREE.Mesh(rudderGeometry, rudderMaterial);
    rudderGroup.add(rudderMesh);
    
    // 健康度指示器
    const healthIndicator = this._createStatusIndicator('健康度', 0, 0.8, 0, 0.25);
    rudderGroup.add(healthIndicator);
    
    // 舵角指示器
    const angleIndicator = this._createStatusIndicator('舵角', 0, 0.3, 0, 0.25);
    rudderGroup.add(angleIndicator);
    
    // 状态灯
    const statusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    statusLight.position.set(0.3, 0, 0);
    rudderGroup.add(statusLight);
    
    // 设置位置（船体后部，舵机舱）
    rudderGroup.position.set(0, 4, 18);
    rudderGroup.scale.set(2, 2, 2);
    
    this.scene.add(rudderGroup);
    
    this.monitoringObjects.set('rudder', {
      group: rudderGroup,
      rudderMesh: rudderMesh,
      statusLight: statusLight,
      indicators: {
        health: healthIndicator,
        angle: angleIndicator
      },
      type: 'rudder'
    });
  }

  /**
   * 创建推进系统监控
   * @private
   */
  _createPropulsionMonitor() {
    const propulsionGroup = new THREE.Group();
    propulsionGroup.name = 'PropulsionMonitor';
    
    // 推进器模型
    const propGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.5, 16);
    const propMaterial = new THREE.MeshStandardMaterial({
      color: 0x666666,
      metalness: 0.7,
      roughness: 0.3
    });
    const propMesh = new THREE.Mesh(propGeometry, propMaterial);
    propMesh.rotation.x = Math.PI / 2;
    propulsionGroup.add(propMesh);
    
    // 健康度指示器
    const healthIndicator = this._createStatusIndicator('健康度', 0, 0.6, 0, 0.25);
    propulsionGroup.add(healthIndicator);
    
    // 效率指示器
    const efficiencyIndicator = this._createStatusIndicator('效率', 0, 0.1, 0, 0.25);
    propulsionGroup.add(efficiencyIndicator);
    
    // 状态灯
    const statusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    statusLight.position.set(0.4, 0, 0);
    propulsionGroup.add(statusLight);
    
    // 设置位置（船体后部，推进器舱）
    propulsionGroup.position.set(0, 4, 20);
    propulsionGroup.scale.set(2.5, 2.5, 2.5);
    
    this.scene.add(propulsionGroup);
    
    this.monitoringObjects.set('propulsion', {
      group: propulsionGroup,
      propMesh: propMesh,
      statusLight: statusLight,
      indicators: {
        health: healthIndicator,
        efficiency: efficiencyIndicator
      },
      type: 'propulsion'
    });
  }

  /**
   * 创建结构应力监控
   * @private
   */
  _createStructureStressMonitor() {
    const stressGroup = new THREE.Group();
    stressGroup.name = 'StructureStressMonitor';
    
    // 应力传感器位置（船首、船中、船尾）
    const sensorPositions = [
      { name: '船首', pos: new THREE.Vector3(0, 8, -20) },
      { name: '船中', pos: new THREE.Vector3(0, 8, 0) },
      { name: '船尾', pos: new THREE.Vector3(0, 8, 20) }
    ];
    
    const sensors = [];
    sensorPositions.forEach((sensor, index) => {
      // 传感器模型
      const sensorGeometry = new THREE.SphereGeometry(0.2, 16, 16);
      const sensorMaterial = new THREE.MeshStandardMaterial({
        color: 0x888888,
        metalness: 0.5,
        roughness: 0.5
      });
      const sensorMesh = new THREE.Mesh(sensorGeometry, sensorMaterial);
      sensorMesh.position.copy(sensor.pos);
      stressGroup.add(sensorMesh);
      
      // 应力值标签
      const stressLabel = this._createTextLabel(
        `${sensor.name}应力`, 
        sensor.pos.x, 
        sensor.pos.y + 0.5, 
        sensor.pos.z, 
        0.2
      );
      stressGroup.add(stressLabel);
      
      sensors.push({
        mesh: sensorMesh,
        label: stressLabel,
        position: sensor.pos,
        name: sensor.name
      });
    });
    
    // 设置位置（相对于船体）
    stressGroup.position.set(0, 0, 0);
    
    this.scene.add(stressGroup);
    
    this.monitoringObjects.set('structureStress', {
      group: stressGroup,
      sensors: sensors,
      type: 'structure'
    });
  }

  /**
   * 创建应急设备监控
   * @private
   */
  _createEmergencyEquipmentMonitor() {
    const emergencyGroup = new THREE.Group();
    emergencyGroup.name = 'EmergencyEquipmentMonitor';
    
    // 消防泵
    const firePumpGroup = new THREE.Group();
    const pumpGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.6, 16);
    const pumpMaterial = new THREE.MeshStandardMaterial({
      color: 0xff0000,
      metalness: 0.6,
      roughness: 0.4
    });
    const pumpMesh = new THREE.Mesh(pumpGeometry, pumpMaterial);
    firePumpGroup.add(pumpMesh);
    
    const pumpLabel = this._createTextLabel('消防泵 | Fire Pump', 0, 0.5, 0, 0.25);
    firePumpGroup.add(pumpLabel);
    
    const pumpStatusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    pumpStatusLight.position.set(0.3, 0, 0);
    firePumpGroup.add(pumpStatusLight);
    
    firePumpGroup.position.set(-8, 6, 15);
    firePumpGroup.scale.set(2, 2, 2);
    emergencyGroup.add(firePumpGroup);
    
    // 救生艇
    const lifeboatGroup = new THREE.Group();
    const boatGeometry = new THREE.BoxGeometry(1, 0.3, 0.5);
    const boatMaterial = new THREE.MeshStandardMaterial({
      color: 0xffaa00,
      metalness: 0.3,
      roughness: 0.7
    });
    const boatMesh = new THREE.Mesh(boatGeometry, boatMaterial);
    lifeboatGroup.add(boatMesh);
    
    const boatLabel = this._createTextLabel('救生艇 | Lifeboat', 0, 0.4, 0, 0.25);
    lifeboatGroup.add(boatLabel);
    
    const boatStatusLight = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 16),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 1.0
      })
    );
    boatStatusLight.position.set(0.5, 0, 0);
    lifeboatGroup.add(boatStatusLight);
    
    lifeboatGroup.position.set(8, 6, 15);
    lifeboatGroup.scale.set(2, 2, 2);
    emergencyGroup.add(lifeboatGroup);
    
    this.scene.add(emergencyGroup);
    
    this.monitoringObjects.set('emergency', {
      group: emergencyGroup,
      firePump: {
        group: firePumpGroup,
        mesh: pumpMesh,
        statusLight: pumpStatusLight,
        label: pumpLabel
      },
      lifeboat: {
        group: lifeboatGroup,
        mesh: boatMesh,
        statusLight: boatStatusLight,
        label: boatLabel
      },
      type: 'emergency'
    });
  }

  /**
   * 创建状态指示器
   * @private
   */
  _createStatusIndicator(name, x, y, z, scale = 0.3) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = 'bold 24px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(name, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(x, y, z);
    sprite.scale.set(scale * 2, scale * 0.5, 1);
    
    return sprite;
  }

  /**
   * 创建文字标签
   * @private
   */
  _createTextLabel(text, x, y, z, scale = 0.3) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 128;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = 'bold 32px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(x, y, z);
    sprite.scale.set(scale * 4, scale, 1);
    
    return sprite;
  }

  /**
   * 评估状态等级
   * @private
   */
  _evaluateStatus(value, threshold) {
    if (value >= threshold.normal[0] && value <= threshold.normal[1]) {
      return 'normal';
    } else if (value >= threshold.warning[0] && value <= threshold.warning[1]) {
      return 'warning';
    } else {
      return 'critical';
    }
  }

  /**
   * 更新状态指示器颜色
   * @private
   */
  _updateStatusLight(light, status) {
    if (!light || !light.material) return;
    
    switch (status) {
      case 'normal':
        light.material.color.setHex(0x00ff00);
        light.material.emissive.setHex(0x00ff00);
        break;
      case 'warning':
        light.material.color.setHex(0xffff00);
        light.material.emissive.setHex(0xffff00);
        break;
      case 'critical':
        light.material.color.setHex(0xff0000);
        light.material.emissive.setHex(0xff0000);
        break;
    }
  }

  /**
   * 更新监控数据
   */
  update(deltaTime) {
    const now = Date.now();
    if (now - this.lastUpdate < this.updateInterval) return;
    this.lastUpdate = now;

    if (!this.dataSource) return;

    try {
      const data = this.dataSource.getRealtimeData();
      
      // 更新主机状态
      this._updateMainEngine(data.mainEngine);
      
      // 更新燃油消耗
      this._updateFuelConsumption(data.fuel);
      
      // 更新舵机系统
      this._updateRudder(data.rudder);
      
      // 更新推进系统
      this._updatePropulsion(data.propulsion);
      
      // 更新结构应力
      this._updateStructureStress(data.structure);
      
      // 更新应急设备
      this._updateEmergencyEquipment(data.emergency);
      
    } catch (error) {
      console.error('❌ Error updating safety monitor:', error);
    }
  }

  /**
   * 更新主机状态
   * @private
   */
  _updateMainEngine(engineData) {
    const monitor = this.monitoringObjects.get('mainEngine');
    if (!monitor || !engineData) return;

    // 更新温度
    const tempStatus = this._evaluateStatus(engineData.temperature, this.thresholds.mainEngine.temperature);
    this._updateStatusLight(monitor.statusLight, tempStatus);
    
    // 更新指示器文本
    if (monitor.indicators.temperature) {
      this._updateIndicatorText(monitor.indicators.temperature, 
        `温度: ${engineData.temperature.toFixed(1)}°C`);
    }
    
    // 更新转速
    if (monitor.indicators.rpm) {
      this._updateIndicatorText(monitor.indicators.rpm, 
        `转速: ${engineData.rpm.toFixed(0)} RPM`);
    }
    
    // 更新压力
    if (monitor.indicators.pressure) {
      this._updateIndicatorText(monitor.indicators.pressure, 
        `压力: ${engineData.pressure.toFixed(1)} bar`);
    }
  }

  /**
   * 更新燃油消耗
   * @private
   */
  _updateFuelConsumption(fuelData) {
    const monitor = this.monitoringObjects.get('fuelConsumption');
    if (!monitor || !fuelData) return;

    // 检查 consumption 属性是否存在，提供默认值
    const consumption = fuelData.consumption ?? 0;

    // 更新指针角度（0-180度对应0-100 L/h）
    const maxConsumption = 100;
    const angle = (consumption / maxConsumption) * Math.PI;
    
    if (monitor.pointer) {
      monitor.pointer.rotation.z = -angle;
    }
    
    // 更新数值显示
    if (monitor.valueLabel) {
      this._updateLabelText(monitor.valueLabel, 
        `${consumption.toFixed(1)} L/h`);
    }
  }

  /**
   * 更新舵机系统
   * @private
   */
  _updateRudder(rudderData) {
    const monitor = this.monitoringObjects.get('rudder');
    if (!monitor || !rudderData) return;

    const healthStatus = this._evaluateStatus(rudderData.health, this.thresholds.rudder.health);
    this._updateStatusLight(monitor.statusLight, healthStatus);
    
    if (monitor.indicators.health) {
      this._updateIndicatorText(monitor.indicators.health, 
        `健康度: ${rudderData.health.toFixed(0)}%`);
    }
    
    if (monitor.indicators.angle) {
      this._updateIndicatorText(monitor.indicators.angle, 
        `舵角: ${rudderData.angle.toFixed(1)}°`);
    }
  }

  /**
   * 更新推进系统
   * @private
   */
  _updatePropulsion(propulsionData) {
    const monitor = this.monitoringObjects.get('propulsion');
    if (!monitor || !propulsionData) return;

    const healthStatus = this._evaluateStatus(propulsionData.health, this.thresholds.propulsion.health);
    this._updateStatusLight(monitor.statusLight, healthStatus);
    
    if (monitor.indicators.health) {
      this._updateIndicatorText(monitor.indicators.health, 
        `健康度: ${propulsionData.health.toFixed(0)}%`);
    }
    
    if (monitor.indicators.efficiency) {
      this._updateIndicatorText(monitor.indicators.efficiency, 
        `效率: ${propulsionData.efficiency.toFixed(0)}%`);
    }
  }

  /**
   * 更新结构应力
   * @private
   */
  _updateStructureStress(structureData) {
    const monitor = this.monitoringObjects.get('structureStress');
    if (!monitor || !structureData) return;

    monitor.sensors.forEach((sensor, index) => {
      const stress = structureData.stress[index] || 0;
      const status = this._evaluateStatus(stress, this.thresholds.structure.stress);
      
      // 更新传感器颜色
      if (sensor.mesh && sensor.mesh.material) {
        switch (status) {
          case 'normal':
            sensor.mesh.material.color.setHex(0x00ff00);
            break;
          case 'warning':
            sensor.mesh.material.color.setHex(0xffff00);
            break;
          case 'critical':
            sensor.mesh.material.color.setHex(0xff0000);
            break;
        }
      }
      
      // 更新标签文本
      if (sensor.label) {
        this._updateLabelText(sensor.label, 
          `${sensor.name}: ${stress.toFixed(1)} MPa`);
      }
    });
  }

  /**
   * 更新应急设备
   * @private
   */
  _updateEmergencyEquipment(emergencyData) {
    const monitor = this.monitoringObjects.get('emergency');
    if (!monitor || !emergencyData) return;

    // 更新消防泵
    if (monitor.firePump) {
      const available = emergencyData.firePump?.available ?? true;
      this._updateStatusLight(monitor.firePump.statusLight, 
        available ? 'normal' : 'critical');
    }
    
    // 更新救生艇
    if (monitor.lifeboat) {
      const available = emergencyData.lifeboat?.available ?? true;
      this._updateStatusLight(monitor.lifeboat.statusLight, 
        available ? 'normal' : 'critical');
    }
  }

  /**
   * 更新指示器文本
   * @private
   */
  _updateIndicatorText(sprite, text) {
    if (!sprite || !sprite.material || !sprite.material.map) return;
    
    const canvas = sprite.material.map.image;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = 'bold 24px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    sprite.material.map.needsUpdate = true;
  }

  /**
   * 更新标签文本
   * @private
   */
  _updateLabelText(sprite, text) {
    if (!sprite || !sprite.material || !sprite.material.map) return;
    
    const canvas = sprite.material.map.image;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = 'bold 32px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    sprite.material.map.needsUpdate = true;
  }

  /**
   * 获取当前警报列表
   */
  getAlerts() {
    return this.alerts;
  }

  /**
   * 获取监控状态摘要
   */
  getStatusSummary() {
    const summary = {
      mainEngine: 'normal',
      fuel: 'normal',
      rudder: 'normal',
      propulsion: 'normal',
      structure: 'normal',
      emergency: 'normal'
    };
    
    // 这里可以根据实际数据计算状态
    // 简化实现，实际应该根据监控数据判断
    
    return summary;
  }
}



