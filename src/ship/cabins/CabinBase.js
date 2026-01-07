/**
 * 舱室基类
 * Base Cabin Class
 * 
 * 所有舱室的基类，定义舱室的基本属性和接口
 */

import * as THREE from '../../../public/lib/three.module.js';

export class CabinBase {
  constructor(config = {}) {
    this.id = config.id || 'cabin-' + Date.now();
    this.name = config.name || 'Cabin';
    this.type = config.type || 'generic'; // 'warehouse', 'datacenter', 'accommodation'
    this.description = config.description || '';
    
    // 舱室边界（局部坐标，相对于船体中心）
    this.bounds = config.bounds || new THREE.Box3(
      new THREE.Vector3(-5, 0, -5),
      new THREE.Vector3(5, 3, 5)
    );
    
    // 相机配置（进入舱室时的相机位置和视角）
    this.cameraConfig = config.cameraConfig || {
      position: [0, 2, 5],
      target: [0, 1.5, 0],
      fov: 75
    };
    
    // 3D对象
    this.mesh = null;
    this.objects = []; // 舱室内物体
    this.interactableObjects = []; // 可交互物体
    
    // 状态
    this.isActive = false;
    this.isVisible = true;
  }

  /**
   * 构建舱室3D模型
   * @param {THREE.Scene} scene 
   * @param {THREE.Vector3} shipPosition - 船体位置
   * @param {THREE.Quaternion} shipRotation - 船体旋转
   */
  build(scene, shipPosition, shipRotation) {
    // 子类实现
    throw new Error('build() must be implemented by subclass');
  }

  /**
   * 进入舱室（场景切换）
   * @param {THREE.Camera} camera 
   * @param {THREE.Vector3} shipPosition 
   * @param {THREE.Quaternion} shipRotation 
   */
  enter(camera, shipPosition, shipRotation) {
    this.isActive = true;
    
    // 计算舱室的世界坐标
    const worldPosition = this.bounds.getCenter(new THREE.Vector3())
      .add(shipPosition)
      .applyQuaternion(shipRotation);
    
    const worldTarget = worldPosition.clone().add(
      new THREE.Vector3(0, 1.5, 0).applyQuaternion(shipRotation)
    );
    
    // 设置相机位置
    const camPos = new THREE.Vector3(...this.cameraConfig.position)
      .add(worldPosition)
      .sub(shipPosition)
      .applyQuaternion(shipRotation)
      .add(shipPosition);
    
    const camTarget = new THREE.Vector3(...this.cameraConfig.target)
      .add(worldPosition)
      .sub(shipPosition)
      .applyQuaternion(shipRotation)
      .add(shipPosition);
    
    return {
      position: camPos,
      target: camTarget,
      fov: this.cameraConfig.fov
    };
  }

  /**
   * 离开舱室
   */
  exit() {
    this.isActive = false;
  }

  /**
   * 更新舱室（动画等）
   * @param {number} deltaTime 
   */
  update(deltaTime) {
    // 子类可以重写
  }

  /**
   * 显示/隐藏舱室
   * @param {boolean} visible 
   */
  setVisible(visible) {
    this.isVisible = visible;
    if (this.mesh) {
      this.mesh.visible = visible;
    }
    this.objects.forEach(obj => {
      if (obj.visible !== undefined) {
        obj.visible = visible;
      }
    });
  }

  /**
   * 添加物体到舱室
   * @param {THREE.Object3D} object 
   * @param {boolean} interactable 
   */
  addObject(object, interactable = false) {
    this.objects.push(object);
    if (interactable) {
      this.interactableObjects.push(object);
    }
    if (this.mesh) {
      this.mesh.add(object);
    }
  }

  /**
   * 创建高度标尺（从模型底部到舱室地板）
   * @param {THREE.Group} cabinGroup - 舱室组
   * @returns {THREE.Group} 标尺组
   */
  _createHeightRuler(cabinGroup) {
    const rulerGroup = new THREE.Group();
    rulerGroup.name = 'HeightRuler';
    
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const floorHeight = this.bounds.min.y; // 舱室地板高度（距离模型底部）
    const modelBottom = 0; // 模型底部在Y=0
    
    // 创建高亮标尺线（从模型底部到舱室地板）
    const rulerGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(boundsCenter.x, modelBottom, boundsCenter.z), // 模型底部（Y=0）
      new THREE.Vector3(boundsCenter.x, floorHeight, boundsCenter.z) // 舱室地板
    ]);
    
    // 高亮标尺线材质（发光蓝色）
    const rulerMaterial = new THREE.LineBasicMaterial({
      color: 0x00ffff, // 青色，高亮
      linewidth: 8,
      transparent: true,
      opacity: 1.0,
      emissive: 0x00ffff, // 发光效果
      emissiveIntensity: 1.0
    });
    
    const rulerLine = new THREE.Line(rulerGeometry, rulerMaterial);
    rulerLine.renderOrder = 998; // 确保在最前面渲染
    rulerGroup.add(rulerLine);
    
    // 添加箭头指示器（在顶部和底部）
    const arrowLength = 2;
    const arrowGeometry = new THREE.ConeGeometry(0.5, arrowLength, 8);
    const arrowMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      emissive: 0x00ffff,
      emissiveIntensity: 1.0
    });
    
    // 顶部箭头（指向舱室地板）
    const topArrow = new THREE.Mesh(arrowGeometry, arrowMaterial);
    topArrow.position.set(boundsCenter.x, floorHeight, boundsCenter.z);
    topArrow.rotation.x = Math.PI; // 向下
    rulerGroup.add(topArrow);
    
    // 底部箭头（指向模型底部）
    const bottomArrow = new THREE.Mesh(arrowGeometry, arrowMaterial);
    bottomArrow.position.set(boundsCenter.x, modelBottom, boundsCenter.z);
    bottomArrow.rotation.x = 0; // 向上
    rulerGroup.add(bottomArrow);
    
    // 添加距离标签（5米大小，高亮显示）
    const distanceLabel = this._createHighlightCabinNameLabel(
      `${floorHeight.toFixed(1)}m`,
      5.0,
      new THREE.Vector3(boundsCenter.x + 8, floorHeight * 0.5, boundsCenter.z) // 标尺中间位置，右侧
    );
    rulerGroup.add(distanceLabel);
    
    // 添加"地板高度"标签（5米大小，高亮显示）
    const floorLabel = this._createHighlightCabinNameLabel(
      '地板高度',
      5.0,
      new THREE.Vector3(boundsCenter.x - 8, floorHeight * 0.5, boundsCenter.z) // 标尺中间位置，左侧
    );
    rulerGroup.add(floorLabel);
    
    return rulerGroup;
  }

  /**
   * 创建舱室名字标注（5米大小）
   * @param {string} text - 标注文字
   * @param {number} worldSize - 世界尺寸（米），默认5米
   * @param {THREE.Vector3} position - 位置（相对于舱室中心），默认在天花板下方
   * @returns {THREE.Sprite} 文字精灵
   */
  _createCabinNameLabel(text, worldSize = 5.0, position = null) {
    // 使用更大的 canvas 和字体，确保5米大小清晰可见
    const canvas = document.createElement('canvas');
    const size = 512; // 增大 canvas 尺寸
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    
    // 清除背景
    ctx.clearRect(0, 0, size, size);
    
    // 添加半透明黑色背景，提高可读性
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, size, size);
    
    // 设置超大字体
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 120px Arial'; // 超大字体
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 8;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // 先描边，再填充，使文字更醒目
    ctx.strokeText(text, size / 2, size / 2);
    ctx.fillText(text, size / 2, size / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    const material = new THREE.SpriteMaterial({ 
      map: texture, 
      transparent: true,
      depthTest: false, // 始终显示在最前面
      depthWrite: false
    });
    const sprite = new THREE.Sprite(material);
    // 设置精灵大小为5米正方
    sprite.scale.set(worldSize, worldSize, 1);
    sprite.renderOrder = 1000; // 确保在最前面渲染
    
    // 设置位置（默认在天花板下方）
    if (position) {
      sprite.position.copy(position);
    } else {
      const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
      sprite.position.set(
        boundsCenter.x,
        this.bounds.max.y - 1, // 天花板下方1米
        boundsCenter.z
      );
    }
    
    return sprite;
  }

  /**
   * 创建高亮舱室名字标注（5米大小）
   * 这是 _createCabinNameLabel 的别名方法，用于保持向后兼容
   * @param {string} text - 标注文字
   * @param {number} worldSize - 世界尺寸（米），默认5米
   * @param {THREE.Vector3} position - 位置（相对于舱室中心），可选
   * @returns {THREE.Sprite} 文字精灵
   */
  _createHighlightCabinNameLabel(text, worldSize = 5.0, position = null) {
    return this._createCabinNameLabel(text, worldSize, position);
  }

  /**
   * 清理资源
   */
  dispose() {
    if (this.mesh) {
      this.mesh.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => m.dispose());
          } else {
            child.material.dispose();
          }
        }
      });
    }
    this.objects = [];
    this.interactableObjects = [];
  }
}

