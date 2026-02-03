/**
 * Digital Twin Map - 数字孪生海图
 * 
 * Software 3.0 理念：沉浸式可视化
 * - 3D 实时渲染的船舶模型和周边环境
 * - AR 增强现实投影（未来支持 Vision Pro/XR）
 * - 智能高亮关键信息（AIS 目标、危险区域、航线）
 */

import * as THREE from '../../../public/lib/three.module.js';
import { EventEmitter } from '../../utils/EventEmitter.js';

export class DigitalTwinMap extends EventEmitter {
  constructor(scene, camera, config = {}) {
    super();
    
    this.scene = scene;
    this.camera = camera;
    this.config = {
      showAIS: config.showAIS !== false, // 默认显示 AIS 目标
      showRoute: config.showRoute !== false, // 显示航线
      showDangerZones: config.showDangerZones !== false, // 显示危险区域
      highlightDuration: config.highlightDuration || 3000, // 高亮持续时间（毫秒）
      ...config
    };
    
    // 可视化元素
    this.aisTargets = new Map(); // AIS 目标船舶
    this.route = null; // 计划航线
    this.highlights = []; // 高亮标记
    this.annotations = []; // 文字标注
    
    // 图层管理
    this.layers = {
      ais: new THREE.Group(),
      route: new THREE.Group(),
      danger: new THREE.Group(),
      highlight: new THREE.Group(),
      annotation: new THREE.Group()
    };
    
    // 添加图层到场景
    Object.values(this.layers).forEach(layer => {
      this.scene.add(layer);
    });
    
    console.log('🗺️ Digital Twin Map initialized');
  }
  
  /**
   * 添加 AIS 目标
   * @param {string} mmsi - 目标船舶 MMSI
   * @param {Object} data - 目标数据
   */
  addAISTarget(mmsi, data) {
    if (this.aisTargets.has(mmsi)) {
      // 更新现有目标
      this.updateAISTarget(mmsi, data);
      return;
    }
    
    // 创建目标船舶标记（简化为一个方块 + 标签）
    const targetGroup = new THREE.Group();
    targetGroup.name = `AIS-${mmsi}`;
    
    // 船舶表示（小方块）
    const geometry = new THREE.BoxGeometry(2, 0.5, 4);
    const material = new THREE.MeshBasicMaterial({
      color: 0xff9800, // 橙色
      transparent: true,
      opacity: 0.8
    });
    const mesh = new THREE.Mesh(geometry, material);
    targetGroup.add(mesh);
    
    // 标签（显示船名和距离）
    const label = this._createLabel(`${data.name || mmsi}\n${data.distance || '?'} NM`, 0xff9800);
    label.position.y = 3;
    targetGroup.add(label);
    
    // 设置位置（相对于本船）
    targetGroup.position.set(
      data.relativeX || 0,
      0,
      data.relativeZ || 0
    );
    
    this.layers.ais.add(targetGroup);
    this.aisTargets.set(mmsi, {
      group: targetGroup,
      data: data
    });
    
    console.log(`🚢 AIS target added: ${mmsi} (${data.name || 'Unknown'})`);
  }
  
  /**
   * 更新 AIS 目标
   * @param {string} mmsi 
   * @param {Object} data 
   */
  updateAISTarget(mmsi, data) {
    const target = this.aisTargets.get(mmsi);
    if (!target) return;
    
    // 更新位置
    target.group.position.set(
      data.relativeX || target.data.relativeX || 0,
      0,
      data.relativeZ || target.data.relativeZ || 0
    );
    
    // 更新数据
    target.data = { ...target.data, ...data };
  }
  
  /**
   * 移除 AIS 目标
   * @param {string} mmsi 
   */
  removeAISTarget(mmsi) {
    const target = this.aisTargets.get(mmsi);
    if (!target) return;
    
    this.layers.ais.remove(target.group);
    this.aisTargets.delete(mmsi);
    
    console.log(`🚢 AIS target removed: ${mmsi}`);
  }
  
  /**
   * 高亮区域或目标
   * @param {Object} target - 目标对象或位置
   * @param {string} reason - 高亮原因
   */
  highlight(target, reason = '') {
    // 创建高亮圈
    const geometry = new THREE.RingGeometry(5, 6, 32);
    const material = new THREE.MeshBasicMaterial({
      color: 0xff0000,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6
    });
    const ring = new THREE.Mesh(geometry, material);
    ring.rotation.x = -Math.PI / 2; // 水平放置
    
    // 设置位置
    if (target.position) {
      ring.position.copy(target.position);
    } else if (target.x !== undefined && target.z !== undefined) {
      ring.position.set(target.x, 0.5, target.z);
    }
    
    this.layers.highlight.add(ring);
    
    // 添加标注
    if (reason) {
      const label = this._createLabel(`⚠️ ${reason}`, 0xff0000);
      label.position.copy(ring.position);
      label.position.y += 5;
      this.layers.annotation.add(label);
      this.annotations.push(label);
    }
    
    // 脉冲动画
    let opacity = 0.6;
    let direction = -1;
    const animate = () => {
      opacity += direction * 0.02;
      if (opacity <= 0.3) direction = 1;
      if (opacity >= 0.8) direction = -1;
      
      material.opacity = opacity;
    };
    
    const animationId = setInterval(animate, 50);
    
    // 自动移除（默认 3 秒后）
    setTimeout(() => {
      clearInterval(animationId);
      this.layers.highlight.remove(ring);
      
      // 清理资源
      geometry.dispose();
      material.dispose();
    }, this.config.highlightDuration);
    
    this.highlights.push({ ring, animationId });
    
    // 触发事件
    this.emit('highlight:created', { target, reason });
    
    console.log(`🎯 Highlighted:`, reason);
  }
  
  /**
   * 绘制航线
   * @param {Array} waypoints - 航路点数组 [{x, z}, ...]
   */
  drawRoute(waypoints) {
    // 清除旧航线
    if (this.route) {
      this.layers.route.remove(this.route);
      this.route.geometry.dispose();
      this.route.material.dispose();
    }
    
    // 创建航线
    const points = waypoints.map(wp => new THREE.Vector3(wp.x, 0.5, wp.z));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x00ff00,
      linewidth: 2,
      transparent: true,
      opacity: 0.7
    });
    
    this.route = new THREE.Line(geometry, material);
    this.layers.route.add(this.route);
    
    // 在每个航路点添加标记
    waypoints.forEach((wp, index) => {
      const marker = this._createWaypointMarker(index + 1);
      marker.position.set(wp.x, 0.5, wp.z);
      this.layers.route.add(marker);
    });
    
    console.log(`🗺️ Route drawn with ${waypoints.length} waypoints`);
  }
  
  /**
   * 创建航路点标记
   * @private
   */
  _createWaypointMarker(number) {
    const geometry = new THREE.CylinderGeometry(0.5, 0.5, 2, 16);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.7
    });
    const marker = new THREE.Mesh(geometry, material);
    
    // 添加编号标签
    const label = this._createLabel(`WP${number}`, 0x00ff00);
    label.position.y = 2;
    marker.add(label);
    
    return marker;
  }
  
  /**
   * 创建文字标签（Sprite）
   * @private
   */
  _createLabel(text, color = 0xffffff) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 256;
    
    // 绘制背景
    ctx.fillStyle = `rgba(0, 0, 0, 0.6)`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制文字
    ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false
    });
    
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(8, 4, 1);
    
    return sprite;
  }
  
  /**
   * 显示/隐藏图层
   * @param {string} layerName - 'ais' | 'route' | 'danger' | 'highlight' | 'annotation'
   * @param {boolean} visible 
   */
  toggleLayer(layerName, visible) {
    if (this.layers[layerName]) {
      this.layers[layerName].visible = visible;
      console.log(`🗺️ Layer "${layerName}" visibility: ${visible}`);
    }
  }
  
  /**
   * 清除所有高亮
   */
  clearHighlights() {
    this.highlights.forEach(({ ring, animationId }) => {
      clearInterval(animationId);
      this.layers.highlight.remove(ring);
      ring.geometry.dispose();
      ring.material.dispose();
    });
    
    this.highlights = [];
  }
  
  /**
   * 清除所有标注
   */
  clearAnnotations() {
    this.annotations.forEach(label => {
      this.layers.annotation.remove(label);
      label.material.map.dispose();
      label.material.dispose();
    });
    
    this.annotations = [];
  }
  
  /**
   * 销毁
   */
  dispose() {
    this.clearHighlights();
    this.clearAnnotations();
    
    // 清理 AIS 目标
    this.aisTargets.forEach((target) => {
      this.layers.ais.remove(target.group);
    });
    this.aisTargets.clear();
    
    // 清理航线
    if (this.route) {
      this.layers.route.remove(this.route);
      this.route.geometry.dispose();
      this.route.material.dispose();
    }
    
    // 移除图层
    Object.values(this.layers).forEach(layer => {
      this.scene.remove(layer);
    });
    
    this.removeAllListeners();
    console.log('🗑️ Digital Twin Map disposed');
  }
}
