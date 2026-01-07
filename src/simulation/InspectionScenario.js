/**
 * 船舱巡检场景
 * Cabin Inspection Scenario
 * 
 * 实现自动化巡检流程，包括：
 * - 预设巡检路径
 * - 自动相机移动
 * - 舱室状态检查
 * - 异常检测和报告
 */

import * as THREE from '../../public/lib/three.module.js';

export class InspectionScenario {
  constructor(scene, camera, cabinManager, shipController) {
    this.scene = scene;
    this.camera = camera;
    this.cabinManager = cabinManager;
    this.shipController = shipController;
    
    this.isRunning = false;
    this.currentStep = 0;
    this.inspectionPath = [];
    this.inspectionResults = [];
    this.startTime = null;
    
    // 巡检配置
    this.config = {
      inspectionSpeed: 2.0, // 相机移动速度
      pauseTime: 2.0, // 每个检查点暂停时间（秒）
      autoStart: false
    };
    
    // 相机动画
    this.cameraAnimation = {
      isAnimating: false,
      startPos: null,
      endPos: null,
      startTarget: null,
      endTarget: null,
      progress: 0,
      duration: 0
    };
  }

  /**
   * 初始化巡检路径
   */
  initialize() {
    if (!this.cabinManager || !this.shipController) {
      console.warn('⚠️ Inspection scenario: CabinManager or ShipController not available');
      return;
    }

    // 构建巡检路径：访问所有舱室
    this.inspectionPath = [];
    const cabins = Array.from(this.cabinManager.cabins.values());
    
    cabins.forEach((cabin, index) => {
      const bounds = cabin.bounds;
      const center = bounds.getCenter(new THREE.Vector3());
      const shipPos = this.shipController.body 
        ? new THREE.Vector3(
            this.shipController.body.position.x,
            this.shipController.body.position.y,
            this.shipController.body.position.z
          )
        : new THREE.Vector3(0, 0, 0);
      
      // 计算世界坐标
      const worldCenter = center.clone().add(shipPos);
      
      // 相机位置（舱室外侧，看向舱室）
      const cameraOffset = new THREE.Vector3(0, 2, 8);
      const cameraPos = worldCenter.clone().add(cameraOffset);
      const cameraTarget = worldCenter.clone();
      
      this.inspectionPath.push({
        cabinId: cabin.id,
        cabinName: cabin.name,
        position: cameraPos,
        target: cameraTarget,
        cabin: cabin
      });
    });
    
    // 添加起始和结束点
    if (this.inspectionPath.length > 0) {
      // 起始点：船体外部全景
      const firstCabin = this.inspectionPath[0];
      const startPos = firstCabin.position.clone().multiplyScalar(1.5);
      startPos.y += 10;
      
      this.inspectionPath.unshift({
        cabinId: 'start',
        cabinName: '起始点 | Start Point',
        position: startPos,
        target: shipPos,
        cabin: null
      });
      
      // 结束点：返回起始位置
      this.inspectionPath.push({
        cabinId: 'end',
        cabinName: '结束点 | End Point',
        position: startPos,
        target: shipPos,
        cabin: null
      });
    }
    
    console.log(`✅ 巡检路径初始化完成 | Inspection path initialized: ${this.inspectionPath.length} points`);
  }

  /**
   * 开始巡检
   */
  start() {
    if (this.isRunning) {
      console.warn('⚠️ 巡检已在进行中 | Inspection already running');
      return;
    }
    
    if (this.inspectionPath.length === 0) {
      this.initialize();
    }
    
    if (this.inspectionPath.length === 0) {
      console.error('❌ 无法开始巡检：没有可用的巡检路径 | Cannot start inspection: no path available');
      return;
    }
    
    this.isRunning = true;
    this.currentStep = 0;
    this.inspectionResults = [];
    this.startTime = Date.now();
    
    console.log('🚢 开始船舱巡检 | Starting cabin inspection...');
    this._moveToNextPoint();
  }

  /**
   * 停止巡检
   */
  stop() {
    this.isRunning = false;
    this.cameraAnimation.isAnimating = false;
    console.log('⏹️ 巡检已停止 | Inspection stopped');
  }

  /**
   * 移动到下一个检查点
   * @private
   */
  _moveToNextPoint() {
    if (!this.isRunning || this.currentStep >= this.inspectionPath.length) {
      this._complete();
      return;
    }
    
    const point = this.inspectionPath[this.currentStep];
    
    // 检查舱室状态
    if (point.cabin) {
      this._inspectCabin(point.cabin);
    }
    
    // 开始相机动画
    this._animateCameraToPoint(point);
  }

  /**
   * 检查舱室
   * @private
   */
  _inspectCabin(cabin) {
    const result = {
      cabinId: cabin.id,
      cabinName: cabin.name,
      timestamp: Date.now(),
      status: 'normal',
      issues: []
    };
    
    // 模拟检查逻辑
    // 检查舱室是否可见
    if (!cabin.isVisible) {
      result.status = 'warning';
      result.issues.push('舱室不可见 | Cabin not visible');
    }
    
    // 检查舱室mesh是否存在
    if (!cabin.mesh) {
      result.status = 'error';
      result.issues.push('舱室模型缺失 | Cabin mesh missing');
    }
    
    // 检查舱室位置
    if (cabin.bounds) {
      const size = cabin.bounds.getSize(new THREE.Vector3());
      if (size.x < 1 || size.y < 1 || size.z < 1) {
        result.status = 'warning';
        result.issues.push('舱室尺寸异常 | Abnormal cabin size');
      }
    }
    
    this.inspectionResults.push(result);
    
    if (result.status !== 'normal') {
      console.warn(`⚠️ 舱室检查发现问题 | Cabin inspection found issues: ${cabin.name}`, result.issues);
    } else {
      console.log(`✅ 舱室检查正常 | Cabin inspection normal: ${cabin.name}`);
    }
  }

  /**
   * 动画相机到指定点
   * @private
   */
  _animateCameraToPoint(point) {
    this.cameraAnimation.startPos = this.camera.position.clone();
    this.cameraAnimation.startTarget = new THREE.Vector3();
    if (this.camera.target) {
      this.cameraAnimation.startTarget.copy(this.camera.target);
    } else {
      // 从相机位置计算目标
      const direction = new THREE.Vector3();
      this.camera.getWorldDirection(direction);
      this.cameraAnimation.startTarget.copy(this.camera.position).add(direction.multiplyScalar(10));
    }
    
    this.cameraAnimation.endPos = point.position.clone();
    this.cameraAnimation.endTarget = point.target.clone();
    this.cameraAnimation.progress = 0;
    this.cameraAnimation.duration = this.cameraAnimation.startPos.distanceTo(this.cameraAnimation.endPos) / this.config.inspectionSpeed;
    this.cameraAnimation.isAnimating = true;
  }

  /**
   * 更新巡检动画
   */
  update(deltaTime) {
    if (!this.isRunning) return;
    
    // 更新相机动画
    if (this.cameraAnimation.isAnimating) {
      this.cameraAnimation.progress += deltaTime / this.cameraAnimation.duration;
      
      if (this.cameraAnimation.progress >= 1.0) {
        // 动画完成
        this.camera.position.copy(this.cameraAnimation.endPos);
        if (this.camera.target) {
          this.camera.target.copy(this.cameraAnimation.endTarget);
        }
        this.cameraAnimation.isAnimating = false;
        
        // 暂停一段时间后继续
        setTimeout(() => {
          this.currentStep++;
          this._moveToNextPoint();
        }, this.config.pauseTime * 1000);
      } else {
        // 插值相机位置
        const t = this._easeInOutCubic(this.cameraAnimation.progress);
        this.camera.position.lerpVectors(
          this.cameraAnimation.startPos,
          this.cameraAnimation.endPos,
          t
        );
        
        if (this.camera.target) {
          this.camera.target.lerpVectors(
            this.cameraAnimation.startTarget,
            this.cameraAnimation.endTarget,
            t
          );
        }
        
        // 更新OrbitControls目标
        if (this.camera.controls) {
          this.camera.controls.target.copy(this.camera.target);
          this.camera.controls.update();
        }
      }
    }
  }

  /**
   * 缓动函数
   * @private
   */
  _easeInOutCubic(t) {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /**
   * 完成巡检
   * @private
   */
  _complete() {
    this.isRunning = false;
    const duration = (Date.now() - this.startTime) / 1000;
    
    const summary = {
      totalCabins: this.inspectionResults.length,
      normal: this.inspectionResults.filter(r => r.status === 'normal').length,
      warnings: this.inspectionResults.filter(r => r.status === 'warning').length,
      errors: this.inspectionResults.filter(r => r.status === 'error').length,
      duration: duration
    };
    
    console.log('✅ 巡检完成 | Inspection completed:', summary);
    console.log('📊 巡检报告 | Inspection report:', this.inspectionResults);
    
    // 触发完成事件
    if (this.onComplete) {
      this.onComplete(summary, this.inspectionResults);
    }
  }

  /**
   * 获取巡检报告
   */
  getReport() {
    return {
      startTime: this.startTime,
      endTime: Date.now(),
      results: this.inspectionResults,
      summary: {
        total: this.inspectionResults.length,
        normal: this.inspectionResults.filter(r => r.status === 'normal').length,
        warnings: this.inspectionResults.filter(r => r.status === 'warning').length,
        errors: this.inspectionResults.filter(r => r.status === 'error').length
      }
    };
  }
}

