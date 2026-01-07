/**
 * 浮力算法
 * 多点采样计算船体浮力
 */

import * as CANNON from '../../../public/lib/cannon-es.js';
import * as THREE from '../../../public/lib/three.module.js';
import { SimulationAlgorithm } from '../SimulatorEngine.js';
import { getWaveHeight } from '../../waves.js';

export class BuoyancyAlgorithm extends SimulationAlgorithm {
  constructor(config = {}) {
    super('Buoyancy', 100); // 高优先级
    this.description = 'Multi-point buoyancy calculation';
    
    // 浮力参数
    // 计算合适的浮力系数，使船体底部与水面接触
    // 船体质量：37,000,000 kg，重力：363,340,000 N
    // 浮力点数量：约95个（双体船两列 + 中心线）
    // 目标：船底与水面接触（吃水接近0米）
    // 需要浮力 = 重力 = 363,340,000 N
    // 假设所有浮力点在水下，平均深度约0.1米（刚好接触水面）
    // 总浮力 = 95 × 0.1 × buoyancyCoeff ≈ 363,340,000
    // buoyancyCoeff ≈ 38,246,000
    // 考虑到浮力点分布和实际深度变化，设置为40,000,000确保船底与水面接触
    this.buoyancyCoeff = config.buoyancyCoeff || 40000000; // 默认值40000000，使船底与水面接触
    this.dragCoeff = config.dragCoeff || 6;
    this.density = config.density || 1.0;
    this.yFlip = config.yFlip || -1;
    
    // 浮力采样点（局部坐标）
    this.buoyancyPoints = [];
    
    // 船体尺寸（用于计算浮力权重）
    this.shipSize = null;
    
    // 浮力点可视化标记
    this.visualizationMarkers = [];
    this.scene = null; // 将在initialize或setScene时设置
  }

  initialize(physicsWorld, scene = null) {
    // 保存场景引用用于可视化
    if (scene) {
      this.scene = scene;
    }
    // 注意：浮力点将在船体加载完成后使用实际尺寸重新生成
    // 这里使用默认尺寸作为占位符
    this.generateBuoyancyPoints();
    // 创建可视化标记（如果有scene）
    if (this.scene) {
      this._createVisualizationMarkers();
    }
  }
  
  /**
   * 设置场景引用（用于可视化）
   */
  setScene(scene) {
    this.scene = scene;
    // 如果已经有浮力点，创建可视化标记
    if (this.buoyancyPoints.length > 0 && this.scene) {
      this._createVisualizationMarkers();
    }
  }

  setBuoyancyPoints(points) {
    this.buoyancyPoints = points;
  }

  generateBuoyancyPoints(shipSize = { x: 4, y: 1, z: 1.6 }) {
    // 保存船体尺寸
    // 注意：X轴=宽度，Y轴=高度，Z轴=长度
    this.shipSize = shipSize;
    
    // 计算各轴半长（考虑85%覆盖范围）
    const hx = shipSize.x * 0.5 * 0.85; // X轴半长（宽度方向）
    // 重要：模型底部在原点（Y=0），浮力点应该在船底，即 Y=0
    // 不再使用 -shipSize.y * 0.5，因为模型原点就在底部
    const hy = 0; // Y轴位置（模型底部，原点Y=0）
    const hz = shipSize.z * 0.5 * 0.85; // Z轴半长（长度方向）

    // 针对138米长船体的优化浮力采样点分布
    // 关键：沿船体长度方向（Z轴）均匀分布更多采样点，确保浮力分布均匀
    // 船头（z < 0）和船尾（z > 0）都需要足够的采样点，防止一头下沉一头上翘
    
    this.buoyancyPoints = [];
    
    // 双体船浮力点分布：沿Z轴（长度方向，138米）两列平行分布
    // 船身宽度85米，两列之间的距离是80米
    // 左列（左侧船体）：x = -40米
    // 右列（右侧船体）：x = +40米
    const catamaranSpacing = 80.0; // 两列之间的距离（米）
    const leftHullX = -catamaranSpacing / 2;  // 左列：-40米
    const rightHullX = catamaranSpacing / 2;   // 右列：+40米
    
    // 沿Z轴（长度方向）均匀分布采样点
    // 每3米一个采样位置，确保138米长度上有足够的采样点
    const segmentLength = 3; // 每3米一个位置
    const lengthSegments = Math.max(45, Math.floor(shipSize.z / segmentLength)); // 138m / 3m = 46个位置
    
    // 生成两列浮力点（沿Z轴均匀分布）
    for (let i = 0; i <= lengthSegments; i++) {
      // 从船头(-hz)到船尾(+hz)均匀分布
      const z = -hz + (2 * hz * i) / lengthSegments;
      
      // 左列浮力点（左侧船体）
      this.buoyancyPoints.push(new CANNON.Vec3(leftHullX, hy, z));
      
      // 右列浮力点（右侧船体）
      this.buoyancyPoints.push(new CANNON.Vec3(rightHullX, hy, z));
    }
    
    // 在船头、船中、船尾的关键位置添加中心线采样点（用于额外稳定性）
    const keyZPositions = [-hz, 0, hz]; // 船头、船中、船尾
    for (const z of keyZPositions) {
      // 中心线点（可选，用于额外稳定性）
      this.buoyancyPoints.push(new CANNON.Vec3(0, hy, z));
    }
    
    // 去重（如果有重复）
    const uniquePoints = [];
    const seen = new Set();
    for (const point of this.buoyancyPoints) {
      const key = `${point.x.toFixed(2)},${point.y.toFixed(2)},${point.z.toFixed(2)}`;
      if (!seen.has(key)) {
        seen.add(key);
        uniquePoints.push(point);
      }
    }
    this.buoyancyPoints = uniquePoints;
    
    console.log(`✅ Generated ${this.buoyancyPoints.length} buoyancy points for catamaran (双体船)`);
    console.log(`   尺寸 | Size: X=${shipSize.x.toFixed(0)}m (宽度) × Y=${shipSize.y.toFixed(0)}m (高度) × Z=${shipSize.z.toFixed(0)}m (长度)`);
    console.log(`   双体船配置 | Catamaran config: 两列间距 ${catamaranSpacing}m, 左列 x=${leftHullX.toFixed(1)}m, 右列 x=${rightHullX.toFixed(1)}m`);
    console.log(`   沿Z轴（蓝色轴线，长度方向）均匀分布 | Evenly distributed along Z-axis: ${lengthSegments + 1} positions per hull`);
    console.log(`   浮力点Y轴位置 | Buoyancy point Y position: ${hy.toFixed(2)}m (模型底部，原点Y=0)`);
    console.log(`   船体高度 | Ship height: ${shipSize.y.toFixed(2)}m`);
    console.log(`   船体底部 | Ship bottom: Y=0.00m (原点)`);
    console.log(`   船体顶部 | Ship top: Y=${shipSize.y.toFixed(2)}m`);
    
    // 统计船头、船中、船尾的采样点数量
    const bowPoints = this.buoyancyPoints.filter(p => p.z < -hz * 0.3).length;
    const midPoints = this.buoyancyPoints.filter(p => Math.abs(p.z) <= hz * 0.3).length;
    const sternPoints = this.buoyancyPoints.filter(p => p.z > hz * 0.3).length;
    const leftHullPoints = this.buoyancyPoints.filter(p => Math.abs(p.x - leftHullX) < 0.1).length; // 左列点
    const rightHullPoints = this.buoyancyPoints.filter(p => Math.abs(p.x - rightHullX) < 0.1).length; // 右列点
    console.log(`   船头采样点 | Bow: ${bowPoints}, 船中 | Midship: ${midPoints}, 船尾 | Stern: ${sternPoints}`);
    console.log(`   左列采样点 | Left hull: ${leftHullPoints}, 右列采样点 | Right hull: ${rightHullPoints}`);
    
    // 如果已有scene，创建可视化标记
    if (this.scene) {
      this._createVisualizationMarkers();
    }
  }

  /**
   * 创建浮力点可视化标记
   * @private
   */
  _createVisualizationMarkers() {
    if (!this.scene) return;
    
    // 清除旧的标记
    this._clearVisualizationMarkers();
    
    // 创建标记容器组
    const markersGroup = new THREE.Group();
    markersGroup.name = 'BuoyancyPointsVisualization';
    
    // 创建船底网状平面（高亮显示船底位置）
    if (this.shipSize) {
      const gridSize = 20; // 网格细分数量
      const gridGeometry = new THREE.PlaneGeometry(
        this.shipSize.x * 0.9, // 宽度（X轴）
        this.shipSize.z * 0.9,  // 长度（Z轴）
        gridSize, gridSize
      );
      
      // 网格材质（高亮绿色，半透明）
      const gridMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide,
        wireframe: true,
        depthWrite: false
      });
      
      const bottomPlane = new THREE.Mesh(gridGeometry, gridMaterial);
      // 重要：模型底部在原点（Y=0），绿色网状平面应该在 Y=0
      bottomPlane.position.set(0, 0, 0); // 模型底部（原点）
      bottomPlane.rotation.x = -Math.PI / 2; // 水平放置
      bottomPlane.renderOrder = 997;
      markersGroup.add(bottomPlane);
      
      // 添加实心平面（更明显的底部指示）
      const solidGeometry = new THREE.PlaneGeometry(
        this.shipSize.x * 0.9,
        this.shipSize.z * 0.9
      );
      const solidMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        transparent: true,
        opacity: 0.1,
        side: THREE.DoubleSide,
        depthWrite: false
      });
      const solidPlane = new THREE.Mesh(solidGeometry, solidMaterial);
      solidPlane.position.set(0, 0, 0); // 模型底部（原点）
      solidPlane.rotation.x = -Math.PI / 2;
      solidPlane.renderOrder = 996;
      markersGroup.add(solidPlane);
      
      console.log(`✅ Created bottom plane visualization at Y=0.00m (模型底部，原点)`);
    }
    
    // 为每个浮力点创建标记
    this.buoyancyPoints.forEach((point, index) => {
      // 创建球体标记（更大更醒目）
      const markerGeometry = new THREE.SphereGeometry(0.8, 16, 16);
      const markerMaterial = new THREE.MeshStandardMaterial({
        color: 0x00ff00, // 亮绿色
        emissive: 0x00ff00,
        emissiveIntensity: 1.0, // 提高发光强度
        transparent: true,
        opacity: 0.9 // 提高不透明度
      });
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.set(point.x, point.y, point.z);
      marker.renderOrder = 998; // 确保在标签前面
      markersGroup.add(marker);
      
      // 创建"浮"字标签（高亮显示）- 标签位置应该在浮力点正上方
      // 浮力点Y位置是hy=0（模型底部，原点），标签应该在浮力点上方0.1米处
      const label = this._createTextLabel('浮', point.x, point.y + 0.1, point.z);
      markersGroup.add(label);
      
      this.visualizationMarkers.push({ marker, label, point });
    });
    
    this.scene.add(markersGroup);
    console.log(`✅ Created ${this.visualizationMarkers.length} buoyancy point visualization markers`);
  }

  /**
   * 创建文本标签（高亮"浮"字）
   * @private
   */
  _createTextLabel(text, x, y, z) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 256;
    
    // 半透明黑色背景
    context.fillStyle = 'rgba(0, 0, 0, 0.6)';
    context.fillRect(0, 0, 256, 256);
    
    // 高亮"浮"字 - 使用大号、粗体、亮色字体
    context.font = 'bold 180px Arial';
    context.fillStyle = '#00ff00'; // 亮绿色
    context.strokeStyle = '#ffffff'; // 白色描边
    context.lineWidth = 8;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    // 先描边，再填充，使文字更醒目
    context.strokeText(text, 128, 128);
    context.fillText(text, 128, 128);
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    const spriteMaterial = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      alphaTest: 0.1,
      depthTest: false, // 始终显示在最前面
      depthWrite: false
    });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(3, 3, 1); // 增大尺寸，更醒目
    sprite.position.set(x, y, z);
    sprite.renderOrder = 999; // 确保在最前面渲染
    
    return sprite;
  }

  /**
   * 清除可视化标记
   * @private
   */
  _clearVisualizationMarkers() {
    if (this.scene) {
      const markersGroup = this.scene.getObjectByName('BuoyancyPointsVisualization');
      if (markersGroup) {
        this.scene.remove(markersGroup);
        // 清理资源
        markersGroup.traverse((child) => {
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
    }
    this.visualizationMarkers = [];
  }

  /**
   * 更新可视化标记位置（跟随船体）
   */
  updateVisualization(body) {
    if (!this.scene || !body) return;
    
    const markersGroup = this.scene.getObjectByName('BuoyancyPointsVisualization');
    if (!markersGroup) return;
    
    // 更新标记组的位置和旋转，跟随船体
    markersGroup.position.copy(body.position);
    markersGroup.quaternion.copy(body.quaternion);
    
    // 验证绿色网状平面位置
    // 重要：模型底部在原点（Y=0），物理体中心在 Y = shipSize.y * 0.5
    // 绿色网状平面在模型局部坐标中是 Y=0，世界坐标中跟随船体
    if (this.shipSize) {
      // 只在首次更新时输出一次日志
      if (!this._loggedBottomPlane) {
        const bodyCenterY = body.position.y;
        const shipBottomY = bodyCenterY - this.shipSize.y * 0.5; // 物理体中心 - 高度/2 = 船底
        console.log(`🌊 绿色网状平面位置 | Bottom plane position:`);
        console.log(`   模型局部坐标 | Local: Y=0.00m (模型底部，原点)`);
        console.log(`   物理体中心 | Body center: Y=${bodyCenterY.toFixed(2)}m (世界坐标)`);
        console.log(`   船底位置 | Ship bottom: Y=${shipBottomY.toFixed(2)}m (世界坐标)`);
        this._loggedBottomPlane = true;
      }
    }
  }

  update(deltaTime, shipState, environment) {
    const { body } = shipState;
    const { time } = environment;
    
    if (!body || this.buoyancyPoints.length === 0) return null;

    // 检测船体俯仰角度（pitch）- 仅用于统计，不用于调整浮力
    // Z轴方向（船头-船尾）的浮力参数保持一致，不进行俯仰补偿
    const bodyForward = body.quaternion.vmult(new CANNON.Vec3(0, 0, 1)); // 船体前进方向（Z轴）
    const bodyRight = body.quaternion.vmult(new CANNON.Vec3(1, 0, 0)); // 船体右侧方向（X轴）
    
    const pitchAngle = Math.asin(Math.max(-1, Math.min(1, bodyForward.y))); // 俯仰角（弧度）
    const pitchDegrees = pitchAngle * (180 / Math.PI); // 转换为度（仅用于统计）
    
    // 检测横摇角度（roll），用于调整左右两侧浮力分布
    // roll < 0（左侧下沉）→ 增加左侧浮力，减少右侧浮力
    // roll > 0（右侧下沉）→ 增加右侧浮力，减少左侧浮力
    const rollAngle = Math.asin(Math.max(-1, Math.min(1, bodyRight.y))); // 横摇角（弧度）
    const rollDegrees = rollAngle * (180 / Math.PI); // 转换为度
    
    // Z轴方向（船头-船尾）不进行浮力调整，保持参数一致
    // pitchAdjustment 已移除，不再使用
    
    // 根据横摇角度计算左右浮力调整权重
    // roll < 0（左侧下沉）→ 增加左侧浮力权重
    // roll > 0（右侧下沉）→ 增加右侧浮力权重
    const rollAdjustment = Math.max(-0.5, Math.min(0.5, rollDegrees * 0.02)); // 限制在±50%以内

    // 设定一个最大浮力，防止瞬间过度推离水面（按船重的 1.5 倍）
    // 最大浮力：对于大型船舶，需要更大的浮力上限
    // 3.7万吨需要至少等于重力的浮力，加上余量
    // 增加到3.0倍，确保有足够的浮力余量防止下沉
    const maxBuoyancy = body.mass * 9.82 * 3.0;
    
    // 计算每个点的浮力上限（在循环外计算，避免重复）
    // 对于大型船舶（3.7万吨），需要更大的每个点浮力上限
    // 每个点的上限 = 总最大浮力 / (采样点数量 * 0.2)
    // 进一步降低有效点数比例，允许每个点产生更大的浮力，确保总浮力足够支撑船体
    // 注意：当浮力系数较小时，需要允许每个点产生更大的浮力，否则无法支撑船体
    const effectivePointCount = Math.max(this.buoyancyPoints.length * 0.2, 5);
    const maxForcePerPoint = maxBuoyancy / effectivePointCount;
    
    // 调试信息：输出浮力计算参数
    if (Math.random() < 0.01) { // 1%概率输出
      console.log(`🔍 浮力计算参数 | Buoyancy params: coeff=${this.buoyancyCoeff}, points=${this.buoyancyPoints.length}, maxPerPoint=${maxForcePerPoint.toFixed(0)}N`);
    }
    
    let pointsUnderwater = 0;
    let totalBuoyancyForce = 0;
    let bowForce = 0;
    let sternForce = 0;
    let leftForce = 0;  // 左侧浮力
    let rightForce = 0;  // 右侧浮力
    let debugInfo = [];

    // 更新可视化标记位置
    this.updateVisualization(body);
    
    // 对每个采样点计算浮力并直接施加
    for (let i = 0; i < this.buoyancyPoints.length; i++) {
      const localPoint = this.buoyancyPoints[i];
      
      // 转换到世界坐标
      const worldPoint = new CANNON.Vec3();
      body.pointToWorldFrame(localPoint, worldPoint);

      // 获取该点的水面高度
      const waterHeight = getWaveHeight(worldPoint.x, -worldPoint.z, time) * this.yFlip;
      const depth = waterHeight - worldPoint.y;

      if (depth > 0) {
        pointsUnderwater++;
        
        // 根据采样点位置计算浮力权重
        // X轴=宽度，Y轴=高度，Z轴=长度（船头-船尾方向）
        // 注意：Z轴方向的浮力参数保持一致，不进行俯仰补偿
        // 左侧（x < 0，X轴负方向）：如果左侧下沉，增加浮力
        // 右侧（x > 0，X轴正方向）：如果右侧下沉，增加浮力
        let positionWeight = 1.0;
        if (this.shipSize) {
          // X轴=宽度，Z轴=长度
          const hx = this.shipSize.x * 0.5 * 0.85; // X轴半长（宽度方向）
          const isLeft = localPoint.x < -hx * 0.2;  // 左侧区域（X轴负方向）
          const isRight = localPoint.x > hx * 0.2;  // 右侧区域（X轴正方向）
          
          // Z轴方向（船头-船尾）浮力参数保持一致，不进行任何调整
          // 移除所有基于pitchAngle的Z轴方向浮力权重调整
          
          // 横摇补偿（左右）- 仅保留左右方向的调整
          if (isLeft && rollAngle < 0) {
            // 左侧下沉，增加左侧浮力
            positionWeight *= (1.0 - rollAdjustment); // rollAdjustment是负数，所以1.0 - (-0.4) = 1.4
          } else if (isRight && rollAngle > 0) {
            // 右侧下沉，增加右侧浮力
            positionWeight *= (1.0 + rollAdjustment); // rollAdjustment是正数
          } else if (isLeft && rollAngle > 0) {
            // 右侧下沉，左侧上翘，减少左侧浮力
            positionWeight *= (1.0 + rollAdjustment * 0.5);
          } else if (isRight && rollAngle < 0) {
            // 左侧下沉，右侧上翘，减少右侧浮力
            positionWeight *= (1.0 - rollAdjustment * 0.5);
          }
        }
        
        // 浮力计算：应用位置权重
        // 注意：maxForcePerPoint 已在循环外计算
        
        // 计算实际浮力（应用位置权重）
        // 浮力系数变化会直接影响浮力大小，从而影响船体位置
        const calculatedForce = depth * this.buoyancyCoeff * this.density * positionWeight;
        
        // 浮力 = min(每个点上限, 计算浮力)
        // 注意：权重只影响计算浮力，不影响上限（避免总浮力过大）
        const forceMagnitude = Math.min(maxForcePerPoint, calculatedForce);
        
        // 确保物理体被唤醒，以便浮力变化能立即生效
        if (forceMagnitude > 0) {
          body.wakeUp();
        }
        
        // 统计船头、船尾、左侧、右侧的浮力
        if (localPoint.z < 0) {
          bowForce += forceMagnitude;
        } else if (localPoint.z > 0) {
          sternForce += forceMagnitude;
        }
        if (localPoint.x < 0) {
          leftForce += forceMagnitude;
        } else if (localPoint.x > 0) {
          rightForce += forceMagnitude;
        }
        const upForce = new CANNON.Vec3(0, forceMagnitude, 0);
        totalBuoyancyForce += forceMagnitude;

        // 阻尼力（与速度相关）
        const velAtPoint = new CANNON.Vec3();
        body.getVelocityAtWorldPoint(worldPoint, velAtPoint);
        const drag = velAtPoint.scale(-this.dragCoeff);

        // 合力
        const totalForce = upForce.vadd(drag);
        
        // 直接在该点施加力（与原版一致！）
        body.applyForce(totalForce, worldPoint);
        
        // 调试信息
        if (Math.random() < 0.01) { // 1%概率输出调试信息
          debugInfo.push({
            point: i,
            worldY: worldPoint.y.toFixed(2),
            waterH: waterHeight.toFixed(2),
            depth: depth.toFixed(2),
            force: forceMagnitude.toFixed(0)
          });
        }
      }
    }

    // 偶尔输出调试信息（包含浮力分布、俯仰角度和横摇角度）
    if (Math.random() < 0.02) { // 2%概率输出
      const bowRatio = totalBuoyancyForce > 0 ? (bowForce / totalBuoyancyForce * 100).toFixed(1) : 0;
      const sternRatio = totalBuoyancyForce > 0 ? (sternForce / totalBuoyancyForce * 100).toFixed(1) : 0;
      const leftRatio = totalBuoyancyForce > 0 ? (leftForce / totalBuoyancyForce * 100).toFixed(1) : 0;
      const rightRatio = totalBuoyancyForce > 0 ? (rightForce / totalBuoyancyForce * 100).toFixed(1) : 0;
      console.log('🔍 Buoyancy Distribution:', {
        pitch: pitchDegrees.toFixed(2) + '° (仅统计，不调整浮力)',
        roll: rollDegrees.toFixed(2) + '°',
        pointsUnderwater,
        totalForce: totalBuoyancyForce.toFixed(0) + 'N',
        bowForce: bowForce.toFixed(0) + 'N (' + bowRatio + '%)',
        sternForce: sternForce.toFixed(0) + 'N (' + sternRatio + '%)',
        leftForce: leftForce.toFixed(0) + 'N (' + leftRatio + '%)',
        rightForce: rightForce.toFixed(0) + 'N (' + rightRatio + '%)',
        note: 'Z轴方向（船头-船尾）浮力参数一致',
        rollAdj: (rollAdjustment * 100).toFixed(1) + '%'
      });
    }

    // 返回null表示力已经直接施加，不需要SimulatorEngine再次施加
    return {
      force: null,  // 已直接施加，不返回
      torque: null, // 已通过applyForce产生，不返回
      metadata: {
        pointsUnderwater,
        totalBuoyancyForce,
        pitchAngle: pitchDegrees, // 仅统计，不用于调整浮力
        rollAngle: rollDegrees,
        bowForce,
        sternForce,
        leftForce,
        rightForce,
        note: 'Z轴方向（船头-船尾）浮力参数一致，无俯仰补偿',
        rollAdjustment: rollAdjustment * 100
      }
    };
  }
}

