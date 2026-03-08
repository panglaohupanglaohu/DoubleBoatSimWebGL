/**
 * 天气系统
 * 统一管理风、雨、海况等天气要素
 */

import { EventEmitter } from '../utils/EventEmitter.js';
import * as THREE from '../../public/lib/three.module.js';

export class WeatherSystem extends EventEmitter {
  constructor(scene, simulatorEngine) {
    super();
    this.scene = scene;
    this.simulatorEngine = simulatorEngine;
    this.quality = 'high'; // 'high' | 'medium' | 'low'
    
    // 当前天气预设
    this._currentPreset = 'calm';
    
    // 天气参数
    this.weather = {
      windSpeed: 0,        // m/s
      windDirection: 0,    // 度
      rainIntensity: 0,    // mm/h
      snowIntensity: 0,    // mm/h (新增降雪)
      visibility: 1.0,     // 0-1
      seaState: 0,         // 0-9 (道格拉斯海况等级)
      temperature: 15      // 摄氏度（用于判断降雨/降雪）
    };

    // 渲染对象
    this.rainParticles = null;
    this.snowParticles = null; // 新增降雪粒子
    this.windIndicator = null;
    
    // 可见性状态缓存（用于调试日志）
    this._lastRainVisible = undefined;
    this._lastSnowVisible = undefined;

    // 中低质量模式下用于跳帧的开关
    this._rainFrameToggle = false;
    this._snowFrameToggle = false;
    
    this.enabled = true;
    
    console.log('🌤️ WeatherSystem 已初始化 | Weather system initialized');
  }

  /**
   * 获取/设置当前预设（用于GUI绑定）
   */
  get preset() {
    return this._currentPreset;
  }
  
  set preset(value) {
    this.setPreset(value);
  }
  
  /**
   * 设置天气预设（别名，保持兼容）
   */
  setPreset(preset) {
    this.setWeatherPreset(preset);
  }

  /**
   * 初始化天气视觉效果
   */
  initialize() {
    this._createRainParticles();
    this._createSnowParticles(); // 新增降雪粒子
    this._createWindIndicator();
    this.emit('initialized');
  }

  /**
   * 设置天气预设
   * @param {string} preset - 'calm', 'moderate', 'storm', 'typhoon'
   */
  setWeatherPreset(preset) {
    const presets = {
      calm: {
        windSpeed: 2,
        windDirection: 180,
        rainIntensity: 0,
        snowIntensity: 0,
        seaState: 0,
        temperature: 20
      },
      moderate: {
        windSpeed: 10,
        windDirection: 180,
        rainIntensity: 5,
        snowIntensity: 0,
        seaState: 3,
        temperature: 18
      },
      storm: {
        windSpeed: 20,
        windDirection: 180,
        rainIntensity: 30,
        snowIntensity: 0,
        seaState: 6,
        temperature: 15
      },
      typhoon: {
        windSpeed: 35,
        windDirection: 180,
        rainIntensity: 80,
        snowIntensity: 0,
        seaState: 9,
        temperature: 18
      },
      snow: {
        windSpeed: 8,
        windDirection: 180,
        rainIntensity: 0,
        snowIntensity: 30,
        seaState: 2,
        temperature: -5
      },
      // 增强台风等级（1-17级，中国标准）
      typhoon1: { windSpeed: 17, windDirection: 180, rainIntensity: 20, seaState: 4 },   // 1级
      typhoon2: { windSpeed: 20, windDirection: 180, rainIntensity: 30, seaState: 5 },   // 2级
      typhoon3: { windSpeed: 24, windDirection: 180, rainIntensity: 40, seaState: 6 },   // 3级
      typhoon4: { windSpeed: 28, windDirection: 180, rainIntensity: 50, seaState: 7 },  // 4级
      typhoon5: { windSpeed: 32, windDirection: 180, rainIntensity: 60, seaState: 8 },    // 5级
      typhoon6: { windSpeed: 36, windDirection: 180, rainIntensity: 70, seaState: 9 },   // 6级
      typhoon7: { windSpeed: 41, windDirection: 180, rainIntensity: 80, seaState: 9 },   // 7级
      typhoon8: { windSpeed: 46, windDirection: 180, rainIntensity: 90, seaState: 9 },   // 8级
      typhoon9: { windSpeed: 51, windDirection: 180, rainIntensity: 100, seaState: 9 },  // 9级
      typhoon10: { windSpeed: 56, windDirection: 180, rainIntensity: 110, seaState: 9 }, // 10级
      typhoon11: { windSpeed: 61, windDirection: 180, rainIntensity: 120, seaState: 9 }, // 11级
      typhoon12: { windSpeed: 66, windDirection: 180, rainIntensity: 130, seaState: 9 }, // 12级
      typhoon13: { windSpeed: 72, windDirection: 180, rainIntensity: 140, seaState: 9 }, // 13级
      typhoon14: { windSpeed: 78, windDirection: 180, rainIntensity: 150, seaState: 9 }, // 14级
      typhoon15: { windSpeed: 85, windDirection: 180, rainIntensity: 160, seaState: 9 }, // 15级
      typhoon16: { windSpeed: 92, windDirection: 180, rainIntensity: 170, seaState: 9 }, // 16级
      typhoon17: { windSpeed: 100, windDirection: 180, rainIntensity: 200, seaState: 9 } // 17级（超强台风）
    };

    const config = presets[preset];
    if (config) {
      // 更新当前预设
      this._currentPreset = preset;
      
      // 设置温度（必须在雨雪之前）
      if (config.temperature !== undefined) {
        this.weather.temperature = config.temperature;
      }
      
      // 设置各项天气参数
      this.setWind(config.windSpeed, config.windDirection);
      this.setRain(config.rainIntensity);
      
      // 设置降雪（如果有）
      if (config.snowIntensity !== undefined) {
        this.setSnow(config.snowIntensity);
      }
      
      this.setSeaState(config.seaState);
      
      console.log(`🌤️ 天气预设已设置: ${preset} | Weather preset set: ${preset}`);
      this.emit('preset:changed', { preset, config });
    } else {
      console.warn(`⚠️ 未知天气预设: ${preset} | Unknown weather preset: ${preset}`);
    }
  }

  /**
   * 设置天气效果质量（high / medium / low）
   * 低质量会完全关闭雨雪粒子，减轻负载
   */
  setQuality(level) {
    const allowed = ['high', 'medium', 'low'];
    if (!allowed.includes(level)) {
      console.warn(`⚠️ 无效的天气质量等级: ${level}，可选值: high / medium / low`);
      return;
    }

    this.quality = level;

    // 根据质量等级立即调整可见性
    if (this.rainParticles) {
      this.rainParticles.visible = this.weather.rainIntensity > 0 && this.quality !== 'low';
    }
    if (this.snowParticles) {
      this.snowParticles.visible =
        this.weather.snowIntensity > 0 && this.weather.temperature <= 0 && this.quality !== 'low';
    }

    console.log(`🎚️ 天气质量已设置为: ${level}`);
  }

  /**
   * 设置风力
   * @param {number} speed - m/s
   * @param {number} direction - 度（0-360）
   */
  setWind(speed, direction) {
    this.weather.windSpeed = speed;
    this.weather.windDirection = direction % 360;
    
    // 更新模拟算法
    const windAlg = this.simulatorEngine?.getAlgorithm('Wind');
    if (windAlg) {
      windAlg.setWindSpeed(speed);
      windAlg.setWindDirection(direction);
    }

    // 根据风速自动计算海况
    this.calculateSeaStateFromWind();

    // 风向改变时，更新雨雪粒子以反映新的风向
    // 这样风对雨雪的影响会立即生效
    if (this.weather.rainIntensity > 0) {
      this._updateRainParticles();
    }
    if (this.weather.snowIntensity > 0 && this.weather.temperature <= 0) {
      this._updateSnowParticles();
    }

    this._updateWindIndicator();
    this.emit('wind:changed', { speed, direction });
  }

  /**
   * 设置降雨
   * @param {number} intensity - mm/h
   */
  setRain(intensity) {
    this.weather.rainIntensity = intensity;
    
    // 调试日志
    console.log(`🌧️ 设置降雨强度 | Setting rain intensity: ${intensity} mm/h`);
    
    // 更新模拟算法
    const rainAlg = this.simulatorEngine?.getAlgorithm('Rain');
    if (rainAlg) {
      rainAlg.setRainIntensity(intensity);
    }

    // 更新能见度
    this.weather.visibility = Math.max(0.3, 1 - intensity / 200);
    
    // 强制更新降雨粒子可见性
    this._updateRainParticles();
    this._updateVisibility();
    
    // 如果强度为0，确保粒子完全隐藏
    if (intensity === 0 && this.rainParticles) {
      this.rainParticles.visible = false;
      console.log(`✅ 降雨粒子已隐藏 | Rain particles hidden (intensity = 0)`);
    }
    
    this.emit('rain:changed', { intensity });
  }

  /**
   * 设置降雪
   * @param {number} intensity - mm/h
   */
  setSnow(intensity) {
    // 允许设置降雪强度，即使温度>0也可以设置（但不会显示降雪效果）
    this.weather.snowIntensity = intensity;
    
    // 调试日志
    console.log(`❄️ 设置降雪强度 | Setting snow intensity: ${intensity} mm/h (温度 | Temperature: ${this.weather.temperature}°C)`);
    
    // 降雪时，如果温度>0°C，自动转换为降雨（但不阻止用户设置数值）
    if (this.weather.temperature > 0 && intensity > 0) {
      // 同时设置降雨，但保留降雪强度数值（允许用户调整）
      this.setRain(intensity);
      // 不将snowIntensity设置为0，允许用户看到设置的数值
      // 但降雪粒子不会显示（因为温度>0）
      console.log(`🌡️ 温度 ${this.weather.temperature}°C > 0°C，降雪已转换为降雨（降雪强度仍可调整）| Temperature > 0°C, snow converted to rain (snow intensity still adjustable)`);
    }
    
    // 强制更新降雪粒子可见性
    this._updateSnowParticles();
    
    // 如果强度为0，确保粒子完全隐藏
    if (intensity === 0 && this.snowParticles) {
      this.snowParticles.visible = false;
      console.log(`✅ 降雪粒子已隐藏 | Snow particles hidden (intensity = 0)`);
    }
    
    this.emit('snow:changed', { intensity });
  }

  /**
   * 设置温度（影响降雨/降雪）
   * @param {number} temperature - 摄氏度
   */
  setTemperature(temperature) {
    this.weather.temperature = temperature;
    
    // 如果温度变化导致降雪转为降雨或反之
    if (temperature > 0 && this.weather.snowIntensity > 0) {
      this.setRain(this.weather.snowIntensity);
      this.weather.snowIntensity = 0;
    }
  }

  /**
   * 设置海况等级（0-9）
   */
  setSeaState(level) {
    this.weather.seaState = Math.min(9, Math.max(0, level));
    
    // 海况影响波浪参数（通过事件通知波浪系统）
    this.emit('seastate:changed', { level });
  }

  /**
   * 根据风速自动计算海况等级（道格拉斯海况）
   * 风速影响波浪高度和周期
   */
  calculateSeaStateFromWind() {
    const windSpeed = this.weather.windSpeed;
    
    // 道格拉斯海况等级与风速的关系（简化模型）
    // 0级: 0-0.5 m/s, 1级: 0.5-1.5, 2级: 1.5-3.5, 3级: 3.5-6, 4级: 6-10
    // 5级: 10-14, 6级: 14-20, 7级: 20-28, 8级: 28-38, 9级: 38+
    let seaState = 0;
    if (windSpeed >= 38) seaState = 9;
    else if (windSpeed >= 28) seaState = 8;
    else if (windSpeed >= 20) seaState = 7;
    else if (windSpeed >= 14) seaState = 6;
    else if (windSpeed >= 10) seaState = 5;
    else if (windSpeed >= 6) seaState = 4;
    else if (windSpeed >= 3.5) seaState = 3;
    else if (windSpeed >= 1.5) seaState = 2;
    else if (windSpeed >= 0.5) seaState = 1;
    
    this.setSeaState(seaState);
    return seaState;
  }

  /**
   * 获取波浪参数（根据海况和风速）
   */
  getWaveParameters() {
    const seaState = this.weather.seaState;
    const windSpeed = this.weather.windSpeed;
    
    // 道格拉斯海况对应的波浪参数
    // 海况等级 -> { 波高(m), 周期(s), 波长(m) }
    const seaStateParams = {
      0: { height: 0, period: 0, wavelength: 0 },
      1: { height: 0.1, period: 0.5, wavelength: 2 },
      2: { height: 0.3, period: 1.0, wavelength: 4 },
      3: { height: 0.6, period: 2.0, wavelength: 8 },
      4: { height: 1.0, period: 3.0, wavelength: 12 },
      5: { height: 2.0, period: 4.5, wavelength: 18 },
      6: { height: 3.5, period: 6.0, wavelength: 28 },
      7: { height: 6.0, period: 8.0, wavelength: 50 },
      8: { height: 9.0, period: 10.0, wavelength: 80 },
      9: { height: 14.0, period: 12.0, wavelength: 120 }
    };
    
    const baseParams = seaStateParams[Math.min(9, Math.max(0, seaState))] || seaStateParams[0];
    
    // 风速影响（额外增强，台风时更明显）
    let windFactor = 1 + (windSpeed / 50) * 0.3;
    
    // 台风级别（风速>32m/s）时，波浪显著增强
    if (windSpeed > 32) {
      const typhoonLevel = Math.min(17, Math.floor((windSpeed - 17) / 3) + 1);
      windFactor = 1 + (typhoonLevel / 17) * 2.0; // 17级台风时波浪增强3倍
    }
    
    // 计算最终波浪参数
    const amplitude = Math.min(20, baseParams.height * windFactor); // 限制最大波高20m
    const wavelength = baseParams.wavelength * (1 + windSpeed / 100);
    const speed = baseParams.period > 0 ? baseParams.wavelength / baseParams.period : 1.2;
    const steepness = Math.min(1.2, 0.5 + seaState * 0.05 + (windSpeed > 32 ? 0.3 : 0));
    
    return {
      amplitude,
      wavelength,
      speed,
      steepness
    };
  }

  /**
   * 设置台风等级（1-17级）
   */
  setTyphoonLevel(level) {
    level = Math.min(17, Math.max(1, Math.floor(level)));
    
    // 台风等级对应的风速（m/s，中国标准）
    const levelToWindSpeed = {
      1: 17, 2: 20, 3: 24, 4: 28, 5: 32, 6: 36, 7: 41, 8: 46, 9: 51,
      10: 56, 11: 61, 12: 66, 13: 72, 14: 78, 15: 85, 16: 92, 17: 100
    };
    
    const windSpeed = levelToWindSpeed[level] || 35;
    const rainIntensity = 20 + level * 10; // 降雨强度随等级增加
    
    this.setWind(windSpeed, 180);
    this.setRain(rainIntensity);
    this.setSeaState(9); // 台风时海况都是9级
    
    console.log(`🌀 设置台风等级 ${level} 级 | Typhoon level ${level} set: 风速 ${windSpeed}m/s, 降雨 ${rainIntensity}mm/h`);
  }

  /**
   * 更新天气系统
   * @param {number} deltaTime 
   */
  update(deltaTime) {
    if (!this.enabled) return;

    // 更新雨粒子动画（受风向影响）
    if (this.rainParticles && this.weather.rainIntensity > 0) {
      this._updateRainAnimation(deltaTime);
    }

    // 更新降雪粒子动画（受风向影响）
    if (this.snowParticles && this.weather.snowIntensity > 0 && this.weather.temperature <= 0) {
      this._updateSnowAnimation(deltaTime);
    }

    // 更新风向指示器
    if (this.windIndicator && this.weather.windSpeed > 0) {
      this._animateWindIndicator(deltaTime);
    }
  }

  /**
   * 创建雨粒子系统
   * @private
   */
  _createRainParticles() {
    // 大幅增加粒子数量和覆盖范围，确保摄像头缩放时也能看到
    const particleCount = 20000; // 增加粒子数量以提高可见性
    const geometry = new THREE.BufferGeometry();
    
    // 扩大覆盖范围：1000x1000米（X和Z轴），高度200-500米
    const rainAreaSize = 1000; // 覆盖范围：±500米
    const rainHeightMin = 200; // 最低高度
    const rainHeightMax = 500; // 最高高度
    
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount);
    const windOffsets = new Float32Array(particleCount * 2); // 存储风向偏移
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * rainAreaSize; // X轴：±500米
      positions[i * 3 + 1] = Math.random() * (rainHeightMax - rainHeightMin) + rainHeightMin; // Y轴：200-500米
      positions[i * 3 + 2] = (Math.random() - 0.5) * rainAreaSize; // Z轴：±500米
      velocities[i] = 15 + Math.random() * 10; // 增加速度
      // 风向偏移（用于受风向影响）
      windOffsets[i * 2] = Math.random() - 0.5;
      windOffsets[i * 2 + 1] = Math.random() - 0.5;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 1));
    geometry.setAttribute('windOffset', new THREE.BufferAttribute(windOffsets, 2));
    
    const material = new THREE.PointsMaterial({
      color: 0x88ccff, // 更明显的蓝色
      size: 1.0, // 增大粒子尺寸，提高可见性
      transparent: true,
      opacity: 0.9, // 提高不透明度
      depthWrite: false,
      blending: THREE.AdditiveBlending // 使用加法混合提高可见性
    });
    
    this.rainParticles = new THREE.Points(geometry, material);
    this.rainParticles.visible = false;
    this.scene.add(this.rainParticles);
  }

  /**
   * 创建降雪粒子系统
   * @private
   */
  _createSnowParticles() {
    // 大幅增加粒子数量和覆盖范围，确保摄像头缩放时也能看到
    const particleCount = 15000; // 增加粒子数量
    const geometry = new THREE.BufferGeometry();
    
    // 扩大覆盖范围：1000x1000米（X和Z轴），高度200-500米
    const snowAreaSize = 1000; // 覆盖范围：±500米
    const snowHeightMin = 200; // 最低高度
    const snowHeightMax = 500; // 最高高度
    
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount);
    const sizes = new Float32Array(particleCount);
    const windOffsets = new Float32Array(particleCount * 2);
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * snowAreaSize; // X轴：±500米
      positions[i * 3 + 1] = Math.random() * (snowHeightMax - snowHeightMin) + snowHeightMin; // Y轴：200-500米
      positions[i * 3 + 2] = (Math.random() - 0.5) * snowAreaSize; // Z轴：±500米
      velocities[i] = 2 + Math.random() * 3; // 降雪速度较慢
      sizes[i] = 0.3 + Math.random() * 0.5; // 雪花大小变化
      windOffsets[i * 2] = Math.random() - 0.5;
      windOffsets[i * 2 + 1] = Math.random() - 0.5;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 1));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('windOffset', new THREE.BufferAttribute(windOffsets, 2));
    
    const material = new THREE.PointsMaterial({
      color: 0xffffff, // 白色雪花
      size: 1.5, // 增大雪花尺寸，提高可见性
      transparent: true,
      opacity: 0.95, // 提高不透明度
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    
    this.snowParticles = new THREE.Points(geometry, material);
    this.snowParticles.visible = false;
    this.scene.add(this.snowParticles);
  }

  /**
   * 创建风向指示器
   * @private
   */
  _createWindIndicator() {
    // 简单的箭头几何体
    const group = new THREE.Group();
    
    const arrowGeom = new THREE.ConeGeometry(0.5, 2, 8);
    const arrowMat = new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: 0.7 });
    const arrow = new THREE.Mesh(arrowGeom, arrowMat);
    arrow.rotation.x = Math.PI / 2;
    
    group.add(arrow);
    group.position.set(20, 10, 0);
    group.visible = false;
    
    this.windIndicator = group;
    this.scene.add(this.windIndicator);
  }

  /**
   * 更新雨粒子
   * @private
   */
  _updateRainParticles() {
    if (!this.rainParticles) return;

    const shouldBeVisible = this.weather.rainIntensity > 0 && this.quality !== 'low';
    this.rainParticles.visible = shouldBeVisible;
    
    // 调试日志（仅在状态改变时输出）
    if (this._lastRainVisible !== shouldBeVisible) {
      console.log(`🌧️ 降雨粒子可见性 | Rain visibility: ${shouldBeVisible} (强度 | intensity: ${this.weather.rainIntensity})`);
      this._lastRainVisible = shouldBeVisible;
    }
    
    if (shouldBeVisible) {
      // 根据降雨强度调整不透明度和粒子大小
      const intensityFactor = Math.min(1.0, this.weather.rainIntensity / 100);
      this.rainParticles.material.opacity = 0.5 + intensityFactor * 0.5;
      this.rainParticles.material.size = 0.8 + intensityFactor * 1.2;
      
      // 根据降雨强度调整粒子数量（通过缩放可见范围）
      const scale = 0.7 + intensityFactor * 0.3;
      this.rainParticles.scale.set(scale, scale, scale);
      
      // 恢复材质的可见性属性
      this.rainParticles.material.needsUpdate = true;
    } else {
      // 强度为0时，只需要设置不可见即可，不要移动粒子位置
      // 移动位置会导致后续无法恢复
      this.rainParticles.material.opacity = 0;
      this.rainParticles.material.size = 0;
      this.rainParticles.scale.set(0, 0, 0);
      this.rainParticles.material.needsUpdate = true;
    }
  }

  /**
   * 更新降雪粒子
   * @private
   */
  _updateSnowParticles() {
    if (!this.snowParticles) return;

    const shouldBeVisible =
      this.weather.snowIntensity > 0 && this.weather.temperature <= 0 && this.quality !== 'low';
    this.snowParticles.visible = shouldBeVisible;
    
    // 调试日志（仅在状态改变时输出）
    if (this._lastSnowVisible !== shouldBeVisible) {
      console.log(`❄️ 降雪粒子可见性 | Snow visibility: ${shouldBeVisible} (强度 | intensity: ${this.weather.snowIntensity}, 温度 | temp: ${this.weather.temperature}°C)`);
      this._lastSnowVisible = shouldBeVisible;
    }
    
    if (shouldBeVisible) {
      const intensityFactor = Math.min(1.0, this.weather.snowIntensity / 50);
      this.snowParticles.material.opacity = 0.6 + intensityFactor * 0.4;
      this.snowParticles.material.size = 1.2 + intensityFactor * 0.8;
      const scale = 0.8 + intensityFactor * 0.2;
      this.snowParticles.scale.set(scale, scale, scale);
      
      // 恢复材质的可见性属性
      this.snowParticles.material.needsUpdate = true;
    } else {
      // 强度为0或温度>0时，只需要设置不可见即可，不要移动粒子位置
      // 移动位置会导致后续无法恢复
      this.snowParticles.material.opacity = 0;
      this.snowParticles.material.size = 0;
      this.snowParticles.scale.set(0, 0, 0);
      this.snowParticles.material.needsUpdate = true;
    }
  }

  /**
   * 雨粒子动画（受风向影响）
   * @private
   */
  _updateRainAnimation(deltaTime) {
    if (!this.rainParticles || !this.rainParticles.visible || this.weather.rainIntensity <= 0) return;

    // 中质量：隔帧更新；低质量在 _updateRainParticles 中直接隐藏
    if (this.quality === 'medium') {
      this._rainFrameToggle = !this._rainFrameToggle;
      if (this._rainFrameToggle) return;
    } else if (this.quality === 'low') {
      return;
    }
    
    const positions = this.rainParticles.geometry.attributes.position.array;
    const velocities = this.rainParticles.geometry.attributes.velocity.array;
    const windOffsets = this.rainParticles.geometry.attributes.windOffset?.array;
    
    // 计算风向向量（世界坐标）
    // 增强风对雨的影响：风速越大，雨粒子受风影响越明显
    const windDirRad = (this.weather.windDirection * Math.PI) / 180;
    const windFactor = 0.15 + (this.weather.windSpeed / 50) * 0.2; // 风速越大，影响越大（0.15-0.35）
    const windX = Math.sin(windDirRad) * this.weather.windSpeed * windFactor; // 风向X分量（增强）
    const windZ = Math.cos(windDirRad) * this.weather.windSpeed * windFactor; // 风向Z分量（增强）
    
    for (let i = 0; i < positions.length / 3; i++) {
      // 垂直下落（受风影响，风速越大，下落角度越倾斜）
      const windTilt = Math.min(0.3, this.weather.windSpeed / 100); // 风速越大，雨越倾斜
      positions[i * 3 + 1] -= velocities[i] * deltaTime * (1 - windTilt);
      
      // 受风向影响（水平偏移，增强效果）
      if (windOffsets) {
        const windStrength = 1 + windOffsets[i * 2] * 0.5; // 增加风的随机性
        positions[i * 3] += windX * deltaTime * windStrength;
        positions[i * 3 + 2] += windZ * deltaTime * (1 + windOffsets[i * 2 + 1] * 0.5);
      } else {
        // 即使没有windOffsets，也要受风影响
        positions[i * 3] += windX * deltaTime;
        positions[i * 3 + 2] += windZ * deltaTime;
      }
      
      // 重置超出范围的粒子（扩大边界范围）
      const rainAreaSize = 1000; // 覆盖范围：±500米
      const rainHeightMin = 200; // 最低高度
      const rainHeightMax = 500; // 最高高度
      const boundaryMargin = 50; // 边界余量
      
      if (positions[i * 3 + 1] < -10) {
        // 粒子落到地面以下，重新从顶部生成
        positions[i * 3 + 1] = rainHeightMax;
        positions[i * 3] = (Math.random() - 0.5) * rainAreaSize;
        positions[i * 3 + 2] = (Math.random() - 0.5) * rainAreaSize;
      }
      
      // 水平边界检查（扩大边界）
      if (Math.abs(positions[i * 3]) > rainAreaSize * 0.5 + boundaryMargin) {
        // 粒子超出X轴边界，重新生成在范围内
        positions[i * 3] = (Math.random() - 0.5) * rainAreaSize;
      }
      if (Math.abs(positions[i * 3 + 2]) > rainAreaSize * 0.5 + boundaryMargin) {
        // 粒子超出Z轴边界，重新生成在范围内
        positions[i * 3 + 2] = (Math.random() - 0.5) * rainAreaSize;
      }
    }
    
    this.rainParticles.geometry.attributes.position.needsUpdate = true;
  }

  /**
   * 降雪粒子动画（受风向影响，但更慢）
   * @private
   */
  _updateSnowAnimation(deltaTime) {
    if (!this.snowParticles || !this.snowParticles.visible || this.weather.snowIntensity <= 0 || this.weather.temperature > 0) return;

    // 中质量：隔帧更新；低质量在 _updateSnowParticles 中直接隐藏
    if (this.quality === 'medium') {
      this._snowFrameToggle = !this._snowFrameToggle;
      if (this._snowFrameToggle) return;
    } else if (this.quality === 'low') {
      return;
    }
    
    const positions = this.snowParticles.geometry.attributes.position.array;
    const velocities = this.snowParticles.geometry.attributes.velocity.array;
    const sizes = this.snowParticles.geometry.attributes.size?.array;
    const windOffsets = this.snowParticles.geometry.attributes.windOffset?.array;
    
    // 计算风向向量
    // 增强风对雪的影响：风速越大，雪花受风影响越明显
    const windDirRad = (this.weather.windDirection * Math.PI) / 180;
    const windFactor = 0.08 + (this.weather.windSpeed / 50) * 0.15; // 风速越大，影响越大（0.08-0.23）
    const windX = Math.sin(windDirRad) * this.weather.windSpeed * windFactor; // 风向X分量（增强）
    const windZ = Math.cos(windDirRad) * this.weather.windSpeed * windFactor; // 风向Z分量（增强）
    
    for (let i = 0; i < positions.length / 3; i++) {
      // 缓慢下落（带轻微摆动，受风影响）
      const sway = Math.sin(Date.now() * 0.001 + i) * 0.1;
      const windTilt = Math.min(0.2, this.weather.windSpeed / 80); // 风速越大，雪花越倾斜
      positions[i * 3 + 1] -= velocities[i] * deltaTime * (1 - windTilt);
      positions[i * 3] += sway * deltaTime;
      
      // 受风向影响（增强效果）
      if (windOffsets) {
        const windStrength = 1 + windOffsets[i * 2] * 0.8; // 增加风的随机性
        positions[i * 3] += windX * deltaTime * windStrength;
        positions[i * 3 + 2] += windZ * deltaTime * (1 + windOffsets[i * 2 + 1] * 0.8);
      } else {
        // 即使没有windOffsets，也要受风影响
        positions[i * 3] += windX * deltaTime;
        positions[i * 3 + 2] += windZ * deltaTime;
      }
      
      // 重置超出范围的粒子（扩大边界范围）
      const snowAreaSize = 1000; // 覆盖范围：±500米
      const snowHeightMin = 200; // 最低高度
      const snowHeightMax = 500; // 最高高度
      const boundaryMargin = 50; // 边界余量
      
      if (positions[i * 3 + 1] < -10) {
        // 粒子落到地面以下，重新从顶部生成
        positions[i * 3 + 1] = snowHeightMax;
        positions[i * 3] = (Math.random() - 0.5) * snowAreaSize;
        positions[i * 3 + 2] = (Math.random() - 0.5) * snowAreaSize;
      }
      
      // 水平边界检查（扩大边界）
      if (Math.abs(positions[i * 3]) > snowAreaSize * 0.5 + boundaryMargin) {
        // 粒子超出X轴边界，重新生成在范围内
        positions[i * 3] = (Math.random() - 0.5) * snowAreaSize;
      }
      if (Math.abs(positions[i * 3 + 2]) > snowAreaSize * 0.5 + boundaryMargin) {
        // 粒子超出Z轴边界，重新生成在范围内
        positions[i * 3 + 2] = (Math.random() - 0.5) * snowAreaSize;
      }
    }
    
    this.snowParticles.geometry.attributes.position.needsUpdate = true;
  }

  /**
   * 更新风向指示器
   * @private
   */
  _updateWindIndicator() {
    if (!this.windIndicator) return;
    
    this.windIndicator.visible = this.weather.windSpeed > 0;
    
    if (this.windIndicator.visible) {
      const angle = (this.weather.windDirection * Math.PI) / 180;
      this.windIndicator.rotation.y = -angle;
    }
  }

  /**
   * 风向指示器动画
   * @private
   */
  _animateWindIndicator(deltaTime) {
    // 根据风速摆动
    const swayAmount = this.weather.windSpeed * 0.01;
    this.windIndicator.rotation.z = Math.sin(Date.now() * 0.001) * swayAmount;
  }

  /**
   * 更新能见度（雾效果）
   * @private
   */
  _updateVisibility() {
    if (this.scene.fog) {
      const baseFar = 220;
      const fogFar = baseFar * this.weather.visibility;
      this.scene.fog.far = fogFar;
    }
  }

  /**
   * 显示/隐藏天气指示器
   */
  toggleIndicators(visible) {
    if (this.windIndicator) {
      this.windIndicator.visible = visible && this.weather.windSpeed > 0;
    }
  }

  /**
   * 获取当前天气状态
   */
  getWeatherState() {
    return { ...this.weather };
  }

  /**
   * 清理资源
   */
  dispose() {
    if (this.rainParticles) {
      this.scene.remove(this.rainParticles);
      this.rainParticles.geometry.dispose();
      this.rainParticles.material.dispose();
    }
    
    if (this.windIndicator) {
      this.scene.remove(this.windIndicator);
    }
    
    this.removeAllListeners();
  }
}

