/**
 * 舱室管理系统
 * Cabin Management System
 * 
 * 管理所有舱室，处理场景切换和交互
 */

import * as THREE from '../../../public/lib/three.module.js';
import { PartsWarehouse } from './PartsWarehouse.js';
import { DataCenter } from './DataCenter.js';
import { PowerSupplyCabin } from './PowerSupplyCabin.js';
import { SatelliteCommCabin } from './SatelliteCommCabin.js';
import { NavigationControlCabin } from './NavigationControlCabin.js';
import { HighPerformanceComputingCabin } from './HighPerformanceComputingCabin.js';
import { LivingCabin } from './LivingCabin.js';
import { ScienceLabCabin } from './ScienceLabCabin.js';

export class CabinManager {
  constructor(scene, camera, shipController) {
    this.scene = scene;
    this.camera = camera;
    this.shipController = shipController;
    
    this.cabins = new Map();
    this.activeCabin = null;
    this.cameraController = null;
    
    // 相机切换动画
    this.cameraTransition = {
      isTransitioning: false,
      startPos: null,
      startTarget: null,
      endPos: null,
      endTarget: null,
      duration: 1000, // ms
      elapsed: 0
    };
    
    // 原始相机状态（船外视角）
    this.originalCameraState = {
      position: null,
      target: null,
      fov: 75
    };
  }

  /**
   * 清除所有舱室
   */
  clearAllCabins() {
    console.log('🗑️ 清除所有舱室 | Clearing all cabins...');
    this.cabins.forEach((cabin) => {
      if (cabin.mesh) {
        // 从场景或船模型中移除
        if (cabin.mesh.parent) {
          cabin.mesh.parent.remove(cabin.mesh);
        }
        // 清理资源
        cabin.dispose();
      }
    });
    this.cabins.clear();
    this.activeCabin = null;
    console.log('✅ 所有舱室已清除 | All cabins cleared');
  }

  /**
   * 初始化舱室系统
   */
  initialize() {
    // 清除旧的舱室（如果存在）
    if (this.cabins.size > 0) {
      this.clearAllCabins();
    }
    
    // 检查船体是否已加载
    if (!this.shipController || !this.shipController.mesh) {
      console.warn('⚠️ 船体未加载，舱室初始化将延迟 | Ship not loaded, cabin initialization will be delayed');
      console.warn('   将在船体加载完成后重新初始化 | Will reinitialize after ship loads');
      // 延迟重试
      setTimeout(() => {
        if (this.shipController && this.shipController.mesh) {
          console.log('🔄 船体已加载，重新初始化舱室 | Ship loaded, reinitializing cabins...');
          this.initialize();
        }
      }, 1000);
      return;
    }
    
    // 船体尺寸：138m长（z轴），85m宽（x轴），95m高（y轴，含吊车）
    // 坐标系统：x轴=宽度，y轴=高度，z轴=长度（船头为负z，船尾为正z）
    // 重要：模型底部在Y=0（原点），所有舱室地板统一在Y=30米
    const shipLength = 138;  // z轴方向
    const shipWidth = 85;    // x轴方向
    const shipHeight = 95;   // y轴方向
    const cabinFloorHeight = 30; // 所有舱室地板距离模型底部30米
    
    console.log(`🏗️ 初始化舱室系统 | Initializing cabin system: 地板高度=${cabinFloorHeight}m (距离模型底部 | from model bottom)`);
    console.log(`   船体状态 | Ship status: loaded=${this.shipController.loaded}, mesh=${this.shipController.mesh ? 'exists' : 'null'}`);
    
    // 舱室沿z轴（长度方向）排列，从船头（负z）到船尾（正z）
    // x轴方向保持较小（宽度方向，船宽85m，舱室宽度约10-20m）
    // 所有舱室地板统一在Y=30米（距离模型底部30米）
    // 所有舱室组件基于bounds.min.y定位，会自动跟随地板位置调整
    
    // 1. 卫星通信舱室（船头，上层）- 沿z轴排列
    // 地板：30m，高度：10m（30-40m）
    const satelliteComm = new SatelliteCommCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-8, cabinFloorHeight, -60),  // 船头方向（负z），地板在30m
        new THREE.Vector3(8, cabinFloorHeight + 10, -40)  // 顶部在40m
      )
    });
    this.addCabin(satelliteComm);
    
    // 2. 导航控制舱室（船头前部，上层）- 沿z轴排列
    // 地板：30m，高度：8m（30-38m）
    const navigationControl = new NavigationControlCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-10, cabinFloorHeight, -40),  // 地板在30m
        new THREE.Vector3(10, cabinFloorHeight + 8, -20)  // 顶部在38m
      )
    });
    this.addCabin(navigationControl);
    
    // 3. 高性能计算舱室（船体前中部）- 沿z轴排列
    // 地板：30m，高度：12.5m（30-42.5m）
    const hpcCabin = new HighPerformanceComputingCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-10, cabinFloorHeight, -30),  // 地板在30m
        new THREE.Vector3(10, cabinFloorHeight + 12.5, -10)  // 顶部在42.5m
      )
    });
    this.addCabin(hpcCabin);
    
    // 4. 电源供应舱室（船体中部）- 沿z轴排列
    // 地板：30m，高度：9.5m（30-39.5m）
    const powerSupply = new PowerSupplyCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-8, cabinFloorHeight, -10),  // 地板在30m
        new THREE.Vector3(8, cabinFloorHeight + 9.5, 10)  // 顶部在39.5m
      )
    });
    this.addCabin(powerSupply);
    
    // 5. 科学实验舱室（船体中后部）- 沿z轴排列
    // 地板：30m，高度：10.5m（30-40.5m）
    const scienceLab = new ScienceLabCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-10, cabinFloorHeight, 10),  // 地板在30m
        new THREE.Vector3(10, cabinFloorHeight + 10.5, 30)  // 顶部在40.5m
      )
    });
    this.addCabin(scienceLab);
    
    // 6. 生活舱室（船尾）- 沿z轴排列
    // 地板：30m，高度：9.5m（30-39.5m）
    const livingCabin = new LivingCabin({
      bounds: new THREE.Box3(
        new THREE.Vector3(-12, cabinFloorHeight, 30),  // 船尾方向（正z），地板在30m
        new THREE.Vector3(12, cabinFloorHeight + 9.5, 60)  // 顶部在39.5m
      )
    });
    this.addCabin(livingCabin);
    
    // 7. 数据中心舱室（船体中部）
    // 地板：30m，高度：3.5m（30-33.5m）
    const dataCenter = new DataCenter({
      bounds: new THREE.Box3(
        new THREE.Vector3(-5, cabinFloorHeight, -5),  // 地板在30m
        new THREE.Vector3(5, cabinFloorHeight + 3.5, 5)  // 顶部在33.5m
      )
    });
    this.addCabin(dataCenter);
    
    // 保留原有的零部件仓库（可选，如果需要）
    // const warehouse = new PartsWarehouse({
    //   bounds: new THREE.Box3(
    //     new THREE.Vector3(-8, platformHeight, -6),
    //     new THREE.Vector3(8, platformHeight + 4, 6)
    //   )
    // });
    // this.addCabin(warehouse);
    
    // 保存原始相机状态
    this.originalCameraState.position = this.camera.position.clone();
    this.originalCameraState.target = new THREE.Vector3(0, 0, 0);
    
    // 输出舱室统计信息
    console.log(`✅ 舱室系统初始化完成 | Cabin system initialized: ${this.cabins.size} 个舱室 | ${this.cabins.size} cabins`);
    console.log(`   舱室列表 | Cabin list:`);
    this.cabins.forEach((cabin, id) => {
      console.log(`   - ${cabin.name} (${id}): bounds=(${cabin.bounds.min.x.toFixed(1)}, ${cabin.bounds.min.y.toFixed(1)}, ${cabin.bounds.min.z.toFixed(1)}) to (${cabin.bounds.max.x.toFixed(1)}, ${cabin.bounds.max.y.toFixed(1)}, ${cabin.bounds.max.z.toFixed(1)})`);
      console.log(`     mesh=${cabin.mesh ? 'exists' : 'null'}, visible=${cabin.mesh ? cabin.mesh.visible : 'N/A'}`);
    });
  }

  /**
   * 添加舱室
   * @param {CabinBase} cabin 
   */
  addCabin(cabin) {
    this.cabins.set(cabin.id, cabin);
    
    // 调试：输出舱室bounds信息
    console.log(`🏗️ 构建舱室 | Building cabin: ${cabin.name}`);
    console.log(`   bounds: min.y=${cabin.bounds.min.y.toFixed(2)}m, max.y=${cabin.bounds.max.y.toFixed(2)}m`);
    console.log(`   地板高度 | Floor height: ${cabin.bounds.min.y.toFixed(2)}m (距离模型底部 | from model bottom)`);
    
    // 构建舱室模型
    try {
      let shipPos, shipRot;
      
      if (this.shipController && this.shipController.body) {
        shipPos = new THREE.Vector3(
          this.shipController.body.position.x,
          this.shipController.body.position.y,
          this.shipController.body.position.z
        );
        shipRot = new THREE.Quaternion(
          this.shipController.body.quaternion.x,
          this.shipController.body.quaternion.y,
          this.shipController.body.quaternion.z,
          this.shipController.body.quaternion.w
        );
      } else {
        // 使用默认位置（船体中心）
        shipPos = new THREE.Vector3(0, 0, 0);
        shipRot = new THREE.Quaternion(0, 0, 0, 1);
      }
      
      const cabinMesh = cabin.build(this.scene, shipPos, shipRot);
      if (cabinMesh) {
        // 确保舱室可见
        cabinMesh.visible = true;
        cabinMesh.traverse((child) => {
          if (child.isMesh || child.isGroup) {
            child.visible = true;
          }
        });
        
        // 将舱室添加到船模型中，确保舱室与船体坐标系绑定，一起运动
        if (this.shipController && this.shipController.mesh) {
          // 舱室使用局部坐标（相对于船体中心），添加到船体mesh中
          // 这样舱室会自动跟随船体的位置和旋转
          this.shipController.mesh.add(cabinMesh);
          console.log(`✅ 舱室 ${cabin.name} 已绑定到船体坐标系 | Cabin ${cabin.name} bound to ship coordinate system`);
          console.log(`   舱室位置 | Cabin position: (${cabin.bounds.min.x.toFixed(1)}, ${cabin.bounds.min.y.toFixed(1)}, ${cabin.bounds.min.z.toFixed(1)})`);
          console.log(`   舱室mesh父对象 | Cabin mesh parent: ${cabinMesh.parent ? cabinMesh.parent.name || 'Group' : 'null'}`);
          console.log(`   船体mesh可见性 | Ship mesh visible: ${this.shipController.mesh.visible}`);
          
          // 确保船体mesh可见
          if (this.shipController.mesh) {
            this.shipController.mesh.visible = true;
            this.shipController.mesh.traverse((child) => {
              if (child.isMesh || child.isGroup) {
                child.visible = true;
              }
            });
          }
        } else {
          // 如果船模型未加载，暂时添加到场景（稍后会重新绑定）
          this.scene.add(cabinMesh);
          console.warn(`⚠️ 船体未加载，舱室 ${cabin.name} 暂时添加到场景 | Ship not loaded, cabin ${cabin.name} temporarily added to scene`);
          console.warn(`   将在船体加载完成后重新绑定 | Will rebind after ship loads`);
        }
        
        // 添加舱室入口指示器（发光边框）
        this._createCabinIndicator(cabin, shipPos, shipRot);
      } else {
        console.error(`❌ 舱室 ${cabin.name} 构建失败，未返回mesh | Cabin ${cabin.name} build failed, no mesh returned`);
      }
    } catch (error) {
      console.error(`❌ Error building cabin ${cabin.id}:`, error);
    }
  }

  /**
   * 创建舱室入口指示器（高亮标注）
   * @private
   * @param {CabinBase} cabin 
   * @param {THREE.Vector3} shipPosition 
   * @param {THREE.Quaternion} shipRotation 
   */
  _createCabinIndicator(cabin, shipPosition, shipRotation) {
    const bounds = cabin.bounds;
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    
    // 创建高亮标注组
    const indicatorGroup = new THREE.Group();
    indicatorGroup.name = `${cabin.id}-indicator`;
    indicatorGroup.userData = { cabinId: cabin.id, isCabinIndicator: true }; // 标记为可点击对象
    
    // 1. 高亮平面（可点击区域）- 覆盖在舱室入口
    const highlightPlaneGeometry = new THREE.PlaneGeometry(size.x * 1.2, size.y * 1.2);
    const highlightPlaneMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
      depthWrite: false
    });
    const highlightPlane = new THREE.Mesh(highlightPlaneGeometry, highlightPlaneMaterial);
    
    // 将平面定位在舱室入口（船体表面）
    highlightPlane.position.copy(center).add(shipPosition);
    highlightPlane.position.y += size.y * 0.5; // 移到舱室顶部
    highlightPlane.lookAt(center.clone().add(shipPosition).add(new THREE.Vector3(0, 1, 0)));
    highlightPlane.rotateX(Math.PI / 2); // 水平放置
    highlightPlane.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(highlightPlane);
    
    // 2. 发光边框（更明显）
    const outerBoxGeometry = new THREE.BoxGeometry(size.x * 1.15, size.y * 1.15, size.z * 1.15);
    const outerBoxMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.4,
      wireframe: true,
      side: THREE.DoubleSide
    });
    const outerBox = new THREE.Mesh(outerBoxGeometry, outerBoxMaterial);
    outerBox.position.copy(center).add(shipPosition);
    outerBox.applyQuaternion(shipRotation);
    outerBox.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(outerBox);
    
    // 3. 发光点标记（更亮更大）
    const markerGeometry = new THREE.SphereGeometry(0.8, 16, 16);
    const markerMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      emissive: 0x00ff00,
      emissiveIntensity: 2.0,
      transparent: true,
      opacity: 0.9
    });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.position.set(
      center.x + shipPosition.x,
      center.y + size.y / 2 + 1.5 + shipPosition.y,
      center.z + shipPosition.z
    );
    marker.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(marker);
    
    // 4. 文字标签（更明显）
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 128;
    
    // 背景
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // 边框
    context.strokeStyle = '#00ff00';
    context.lineWidth = 4;
    context.strokeRect(2, 2, canvas.width - 4, canvas.height - 4);
    
    // 文字
    context.font = 'bold 48px Arial';
    context.fillStyle = '#00ff00';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(cabin.name, canvas.width / 2, canvas.height / 2);
    
    // 提示文字
    context.font = '24px Arial';
    context.fillStyle = '#ffff00';
    context.fillText('双击进入 | Double-click to enter', canvas.width / 2, canvas.height - 20);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(
      center.x + shipPosition.x,
      center.y + size.y / 2 + 4 + shipPosition.y,
      center.z + shipPosition.z
    );
    sprite.scale.set(10, 2.5, 1);
    sprite.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(sprite);
    
    // 5. 添加脉冲光环效果
    const pulseRingGeometry = new THREE.RingGeometry(1, 1.5, 32);
    const pulseRingMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide
    });
    const pulseRing = new THREE.Mesh(pulseRingGeometry, pulseRingMaterial);
    pulseRing.position.copy(marker.position);
    pulseRing.rotation.x = -Math.PI / 2;
    pulseRing.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(pulseRing);
    
    // 6. 添加箭头指示器（引导用户进入）- 更大更明显
    const arrowLength = 5; // 增大到5米
    const arrowHeadLength = 1.5; // 增大箭头头部
    const arrowHeadWidth = 1.2; // 增大箭头宽度
    
    // 计算箭头起点位置（局部坐标，相对于舱室中心）
    const arrowStartLocal = new THREE.Vector3(
      center.x,
      center.y + size.y / 2 + 4, // 在标记点上方4米
      center.z
    );
    
    // 箭头方向（局部坐标，向下指向舱室入口）
    const arrowDirectionLocal = new THREE.Vector3(0, -1, 0);
    
    // 将indicatorGroup定位到船体位置和旋转
    indicatorGroup.position.copy(shipPosition);
    indicatorGroup.quaternion.copy(shipRotation);
    
    // 创建主箭头（使用局部坐标）
    const arrowHelper = new THREE.ArrowHelper(
      arrowDirectionLocal,
      arrowStartLocal,
      arrowLength,
      0x00ff00, // 绿色
      arrowHeadLength,
      arrowHeadWidth
    );
    arrowHelper.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(arrowHelper);
    
    // 添加箭头发光效果（额外的发光箭头，更大）
    const glowArrowHelper = new THREE.ArrowHelper(
      arrowDirectionLocal,
      arrowStartLocal,
      arrowLength * 1.15, // 比主箭头稍大
      0x00ff00, // 绿色
      arrowHeadLength * 1.3,
      arrowHeadWidth * 1.3
    );
    // 设置发光材质
    glowArrowHelper.children.forEach(child => {
      if (child.material) {
        child.material = child.material.clone();
        child.material.emissive = new THREE.Color(0x00ff00);
        child.material.emissiveIntensity = 2.0; // 增强发光
        child.material.transparent = true;
        child.material.opacity = 0.7; // 提高不透明度
      }
    });
    glowArrowHelper.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(glowArrowHelper);
    
    // 添加额外的粗箭头（更明显）
    const thickArrowHelper = new THREE.ArrowHelper(
      arrowDirectionLocal,
      arrowStartLocal,
      arrowLength * 0.8, // 稍短一点
      0xffff00, // 黄色，更醒目
      arrowHeadLength * 0.9,
      arrowHeadWidth * 1.5 // 更粗
    );
    // 设置黄色发光材质
    thickArrowHelper.children.forEach(child => {
      if (child.material) {
        child.material = child.material.clone();
        child.material.emissive = new THREE.Color(0xffff00);
        child.material.emissiveIntensity = 2.5;
        child.material.transparent = true;
        child.material.opacity = 0.8;
      }
    });
    thickArrowHelper.userData = { cabinId: cabin.id, isCabinIndicator: true };
    indicatorGroup.add(thickArrowHelper);
    
    // 添加到场景（指示器应该始终可见）
    indicatorGroup.visible = true;
    indicatorGroup.traverse((child) => {
      if (child.isMesh || child.isGroup || child.isSprite || child.isLine) {
        child.visible = true;
        if (child.material) {
          child.material.visible = true;
        }
      }
    });
    this.scene.add(indicatorGroup);
    cabin.indicator = indicatorGroup;
    
    // 调试信息
    console.log(`✅ 舱室 ${cabin.name} 箭头指示器已创建:`, {
      arrowLength: arrowLength,
      arrowStartLocal: arrowStartLocal,
      indicatorGroupPosition: indicatorGroup.position,
      indicatorGroupChildren: indicatorGroup.children.length,
      indicatorVisible: indicatorGroup.visible,
      indicatorInScene: this.scene.children.includes(indicatorGroup)
    });
    
    // 保存引用以便后续更新动画
    cabin.indicatorMarker = marker;
    cabin.indicatorBox = outerBox;
    cabin.highlightPlane = highlightPlane;
    cabin.pulseRing = pulseRing;
    cabin.arrowHelper = arrowHelper;
    cabin.glowArrowHelper = glowArrowHelper;
    cabin.thickArrowHelper = thickArrowHelper;
    cabin.arrowStartLocal = arrowStartLocal.clone(); // 保存局部坐标起点用于动画
  }

  /**
   * 进入舱室
   * @param {string} cabinId 
   */
  enterCabin(cabinId) {
    const cabin = this.cabins.get(cabinId);
    if (!cabin) {
      console.warn(`Cabin ${cabinId} not found`);
      return;
    }
    
    if (this.activeCabin === cabin) {
      return; // 已经在舱室内
    }
    
    // 退出当前舱室
    if (this.activeCabin) {
      this.exitCabin();
    }
    
    // 获取船体位置和旋转
    const shipPos = new THREE.Vector3(
      this.shipController.body.position.x,
      this.shipController.body.position.y,
      this.shipController.body.position.z
    );
    const shipRot = new THREE.Quaternion(
      this.shipController.body.quaternion.x,
      this.shipController.body.quaternion.y,
      this.shipController.body.quaternion.z,
      this.shipController.body.quaternion.w
    );
    
    // 获取舱室相机配置
    const cameraConfig = cabin.enter(this.camera, shipPos, shipRot);
    
    // 开始相机过渡动画
    this.startCameraTransition(cameraConfig);
    
    this.activeCabin = cabin;
    
    // 隐藏船体（可选）
    if (this.shipController.mesh) {
      this.shipController.mesh.visible = false;
    }
    
    console.log(`Entered cabin: ${cabin.name}`);
  }

  /**
   * 退出舱室
   */
  exitCabin() {
    if (!this.activeCabin) return;
    
    this.activeCabin.exit();
    
    // 恢复原始相机状态
    this.startCameraTransition({
      position: this.originalCameraState.position,
      target: this.originalCameraState.target,
      fov: this.originalCameraState.fov
    });
    
    // 显示船体
    if (this.shipController.mesh) {
      this.shipController.mesh.visible = true;
    }
    
    console.log(`Exited cabin: ${this.activeCabin.name}`);
    this.activeCabin = null;
  }

  /**
   * 开始相机过渡动画
   * @param {Object} targetConfig 
   */
  startCameraTransition(targetConfig) {
    this.cameraTransition.isTransitioning = true;
    this.cameraTransition.elapsed = 0;
    
    // 起始状态
    this.cameraTransition.startPos = this.camera.position.clone();
    this.cameraTransition.startTarget = new THREE.Vector3(0, 0, 0);
    this.camera.lookAt(this.cameraTransition.startTarget);
    
    // 目标状态
    this.cameraTransition.endPos = targetConfig.position.clone();
    this.cameraTransition.endTarget = targetConfig.target.clone();
    this.cameraTransition.endFov = targetConfig.fov || 75;
  }

  /**
   * 更新相机过渡动画
   * @param {number} deltaTime 
   */
  updateCameraTransition(deltaTime) {
    if (!this.cameraTransition.isTransitioning) return;
    
    this.cameraTransition.elapsed += deltaTime * 1000; // 转换为毫秒
    const progress = Math.min(this.cameraTransition.elapsed / this.cameraTransition.duration, 1);
    
    // 使用缓动函数（easeInOutCubic）
    const eased = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    // 插值相机位置
    this.camera.position.lerpVectors(
      this.cameraTransition.startPos,
      this.cameraTransition.endPos,
      eased
    );
    
    // 插值目标点
    const currentTarget = new THREE.Vector3().lerpVectors(
      this.cameraTransition.startTarget,
      this.cameraTransition.endTarget,
      eased
    );
    this.camera.lookAt(currentTarget);
    
    // 插值FOV
    this.camera.fov = THREE.MathUtils.lerp(
      this.camera.fov,
      this.cameraTransition.endFov,
      eased
    );
    this.camera.updateProjectionMatrix();
    
    // 完成过渡
    if (progress >= 1) {
      this.cameraTransition.isTransitioning = false;
    }
  }

  /**
   * 更新所有舱室
   * @param {number} deltaTime 
   */
  update(deltaTime) {
    // 更新相机过渡
    this.updateCameraTransition(deltaTime);
    
    // 更新活动舱室
    if (this.activeCabin) {
      this.activeCabin.update(deltaTime);
    }
    
    // 更新所有舱室（即使不活动）
    this.cabins.forEach(cabin => {
      if (cabin !== this.activeCabin && cabin && typeof cabin.update === 'function') {
        cabin.update(deltaTime);
      }
      
      // 更新舱室指示器动画（呼吸效果）
      if (cabin.indicatorMarker) {
        const time = Date.now() * 0.001;
        const pulse = Math.sin(time * 2) * 0.5 + 0.5; // 0-1范围
        cabin.indicatorMarker.material.opacity = 0.6 + pulse * 0.4;
        cabin.indicatorMarker.scale.setScalar(1 + pulse * 0.4);
      }
      
      // 更新边框动画
      if (cabin.indicatorBox) {
        const time = Date.now() * 0.001;
        cabin.indicatorBox.rotation.y += deltaTime * 0.5;
        const pulse = Math.sin(time * 2) * 0.5 + 0.5;
        cabin.indicatorBox.material.opacity = 0.2 + pulse * 0.3;
      }
      
      // 更新高亮平面动画
      if (cabin.highlightPlane) {
        const time = Date.now() * 0.001;
        const pulse = Math.sin(time * 2) * 0.5 + 0.5;
        cabin.highlightPlane.material.opacity = 0.2 + pulse * 0.2;
      }
      
      // 更新脉冲光环动画
      if (cabin.pulseRing) {
        const time = Date.now() * 0.001;
        const pulse = Math.sin(time * 3) * 0.5 + 0.5;
        cabin.pulseRing.material.opacity = 0.3 + pulse * 0.5;
        cabin.pulseRing.scale.setScalar(1 + pulse * 0.5);
      }
      
      // 更新indicatorGroup位置和旋转（跟随船体）
      if (cabin.indicator) {
        const shipPos = new THREE.Vector3(
          this.shipController.body.position.x,
          this.shipController.body.position.y,
          this.shipController.body.position.z
        );
        const shipRot = new THREE.Quaternion(
          this.shipController.body.quaternion.x,
          this.shipController.body.quaternion.y,
          this.shipController.body.quaternion.z,
          this.shipController.body.quaternion.w
        );
        cabin.indicator.position.copy(shipPos);
        cabin.indicator.quaternion.copy(shipRot);
      }
      
      // 更新箭头指示器动画（上下浮动 + 发光脉冲）
      if (cabin.arrowHelper && cabin.arrowStartLocal) {
        const time = Date.now() * 0.001;
        
        // 上下浮动效果（相对于原始位置）
        const floatOffset = Math.sin(time * 2) * 0.5; // 上下浮动0.5米
        const currentArrowStart = cabin.arrowStartLocal.clone();
        currentArrowStart.y += floatOffset;
        
        // 更新箭头位置（重新设置起点）
        if (cabin.arrowHelper) {
          cabin.arrowHelper.position.copy(currentArrowStart);
        }
        if (cabin.glowArrowHelper) {
          cabin.glowArrowHelper.position.copy(currentArrowStart);
        }
        if (cabin.thickArrowHelper) {
          cabin.thickArrowHelper.position.copy(currentArrowStart);
        }
        
        // 发光脉冲效果
        const glowPulse = Math.sin(time * 3) * 0.5 + 0.5;
        if (cabin.glowArrowHelper) {
          cabin.glowArrowHelper.children.forEach(child => {
            if (child.material) {
              child.material.opacity = 0.5 + glowPulse * 0.3;
              child.material.emissiveIntensity = 1.5 + glowPulse * 0.8;
            }
          });
        }
        if (cabin.thickArrowHelper) {
          cabin.thickArrowHelper.children.forEach(child => {
            if (child.material) {
              child.material.opacity = 0.6 + glowPulse * 0.3;
              child.material.emissiveIntensity = 2.0 + glowPulse * 1.0;
            }
          });
        }
      }
    });
  }

  /**
   * 检查点击是否命中舱室（优先检测高亮标注）
   * @param {THREE.Raycaster} raycaster 
   * @param {THREE.Vector2} mouse 
   */
  checkCabinClick(raycaster, mouse) {
    raycaster.setFromCamera(mouse, this.camera);
    const intersects = raycaster.intersectObjects(this.scene.children, true);
    
    // 优先检测高亮标注（高亮平面、标记、标签等）
    for (const intersect of intersects) {
      const obj = intersect.object;
      
      // 检查是否是舱室指示器对象
      if (obj.userData && obj.userData.isCabinIndicator && obj.userData.cabinId) {
        const cabinId = obj.userData.cabinId;
        this.enterCabin(cabinId);
        return true;
      }
      
      // 向上查找父对象
      let parent = obj.parent;
      while (parent) {
        if (parent.userData && parent.userData.isCabinIndicator && parent.userData.cabinId) {
          const cabinId = parent.userData.cabinId;
          this.enterCabin(cabinId);
          return true;
        }
        parent = parent.parent;
      }
    }
    
    // 如果没有命中高亮标注，检查是否点击在舱室模型上（备用方案）
    for (const intersect of intersects) {
      let obj = intersect.object;
      while (obj) {
        for (const [id, cabin] of this.cabins) {
          if (cabin.mesh && (obj === cabin.mesh || cabin.mesh.children.includes(obj))) {
            // 检查是否点击在舱室边界内
            const worldPos = intersect.point;
            const shipPos = new THREE.Vector3(
              this.shipController.body.position.x,
              this.shipController.body.position.y,
              this.shipController.body.position.z
            );
            
            // 转换到船体局部坐标
            const localPos = worldPos.clone().sub(shipPos);
            const shipRot = new THREE.Quaternion(
              this.shipController.body.quaternion.x,
              this.shipController.body.quaternion.y,
              this.shipController.body.quaternion.z,
              this.shipController.body.quaternion.w
            );
            localPos.applyQuaternion(shipRot.clone().invert());
            
            // 检查是否在舱室边界内
            if (cabin.bounds.containsPoint(localPos)) {
              this.enterCabin(id);
              return true;
            }
          }
        }
        obj = obj.parent;
      }
    }
    
    return false;
  }

  /**
   * 获取所有舱室信息
   */
  getCabinsInfo() {
    const info = [];
    this.cabins.forEach(cabin => {
      info.push({
        id: cabin.id,
        name: cabin.name,
        type: cabin.type,
        description: cabin.description,
        isActive: cabin === this.activeCabin
      });
    });
    return info;
  }

  /**
   * 获取活动舱室
   */
  getActiveCabin() {
    return this.activeCabin;
  }
}

