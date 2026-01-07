/**
 * 数据中心舱室
 * Data Center Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class DataCenter extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'data-center',
      name: '数据中心 | Data Center',
      type: 'datacenter',
      description: '船舶数据采集和处理中心 | Ship data acquisition and processing center',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-5, 0, -6),
        new THREE.Vector3(5, 3.5, 6)
      ),
      cameraConfig: {
        position: [0, 2, 7],
        target: [0, 1.5, 0],
        fov: 70
      },
      ...config
    });
    
    this.servers = [];
    this.screens = [];
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'DataCenter';
    
    // 地板（深色，科技感）- 长边沿Z轴方向
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      roughness: 0.3,
      metalness: 0.7,
      emissive: 0x0a0a1a,
      emissiveIntensity: 0.2
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.copy(this.bounds.getCenter(new THREE.Vector3()));
    floor.position.y = this.bounds.min.y;
    floor.receiveShadow = true;
    cabinGroup.add(floor);
    
    // 添加蓝色网状面高亮地板
    const floorWireframeGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z, 10, 10);
    const floorWireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x0066ff, // 蓝色
      wireframe: true,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide,
      depthWrite: false
    });
    const floorWireframe = new THREE.Mesh(floorWireframeGeometry, floorWireframeMaterial);
    floorWireframe.rotation.x = -Math.PI / 2;
    floorWireframe.position.copy(this.bounds.getCenter(new THREE.Vector3()));
    floorWireframe.position.y = this.bounds.min.y + 0.01; // 稍微抬高，避免z-fighting
    floorWireframe.renderOrder = 999; // 确保在最前面渲染
    cabinGroup.add(floorWireframe);
    
    // 墙壁（深色科技风格）
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    // 数据中心：蓝色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a9eff, // 蓝色
      transparent: true,
      opacity: 0.85,
      roughness: 0.1,
      metalness: 0.0
      // 注意：MeshStandardMaterial 不支持 transmission，只使用 opacity 实现透明效果
    });
    
    // 后墙（z轴负方向，长边沿z轴）
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(boundsSize.x, wallHeight, 0.2),
      wallMaterial
    );
    backWall.position.set(boundsCenter.x, boundsCenter.y, this.bounds.min.z);
    cabinGroup.add(backWall);
    
    // 前墙（z轴正方向）
    const frontWall = new THREE.Mesh(
      new THREE.BoxGeometry(boundsSize.x, wallHeight, 0.2),
      wallMaterial
    );
    frontWall.position.set(boundsCenter.x, boundsCenter.y, this.bounds.max.z);
    cabinGroup.add(frontWall);
    
    // 侧墙（x轴方向，长边沿z轴）
    const leftWall = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, wallHeight, boundsSize.z),
      wallMaterial
    );
    leftWall.position.set(this.bounds.min.x, boundsCenter.y, boundsCenter.z);
    cabinGroup.add(leftWall);
    
    const rightWall = leftWall.clone();
    rightWall.position.x = this.bounds.max.x;
    cabinGroup.add(rightWall);
    
    // 天花板（带网格效果）
    const ceiling = new THREE.Mesh(
      new THREE.PlaneGeometry(boundsSize.x, boundsSize.z),
      new THREE.MeshStandardMaterial({
        color: 0x0f3460,
        emissive: 0x050a1a,
        emissiveIntensity: 0.3
      })
    );
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.set(boundsCenter.x, this.bounds.max.y, boundsCenter.z);
    cabinGroup.add(ceiling);
    
    // 创建服务器机架
    this._createServerRacks(cabinGroup);
    
    // 创建显示屏
    this._createScreens(cabinGroup);
    
    // 添加照明（蓝色科技光）
    this._addLighting(cabinGroup);
    
    // 添加高亮舱室名字标注（5米大小）
    // 注意：boundsCenter 已在第73行声明，这里直接使用
    const nameLabel = this._createHighlightCabinNameLabel(this.name, 5.0);
    nameLabel.position.copy(boundsCenter);
    nameLabel.position.y = this.bounds.max.y + 1; // 在舱室上方
    cabinGroup.add(nameLabel);
    
    // 添加高度标尺（从模型底部到舱室地板）
    const heightRuler = this._createHeightRuler(cabinGroup);
    cabinGroup.add(heightRuler);
    
    this.mesh = cabinGroup;
    return cabinGroup;
  }

  /**
   * 创建服务器机架
   * @private
   */
  _createServerRacks(cabinGroup) {
    const rackMaterial = new THREE.MeshStandardMaterial({
      color: 0x2d3748,
      metalness: 0.8,
      roughness: 0.2
    });
    
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    
    // 调试：输出bounds信息
    console.log(`📦 DataCenter bounds: min.y=${this.bounds.min.y.toFixed(2)}m, max.y=${this.bounds.max.y.toFixed(2)}m, 地板高度=${this.bounds.min.y.toFixed(2)}m`);
    
    // 创建2排服务器机架（沿z轴方向排列，长边沿z轴）
    for (let row = 0; row < 2; row++) {
      const rackGroup = new THREE.Group();
      
      // 机架框架 - 确保基于bounds.min.y定位
      const frameY = this.bounds.min.y + 1.25; // 机架底部距离地板1.25米
      const frame = new THREE.Mesh(
        new THREE.BoxGeometry(1.5, 2.5, 0.8),
        rackMaterial
      );
      frame.position.set(
        boundsCenter.x - boundsSize.x * 0.25 + row * boundsSize.x * 0.5,
        frameY, // 使用计算出的Y位置
        boundsCenter.z - boundsSize.z * 0.3
      );
      console.log(`  📐 机架框架 ${row + 1} 位置: Y=${frameY.toFixed(2)}m (距离地板1.25m, 距离船底${frameY.toFixed(2)}m)`);
      frame.castShadow = true;
      frame.name = 'DataCenter-机架框架';
      rackGroup.name = 'DataCenter-机架组';
      rackGroup.add(frame);
      
      // 服务器单元（每排8个）- 基于bounds.min.y定位
      for (let i = 0; i < 8; i++) {
        const server = new THREE.Mesh(
          new THREE.BoxGeometry(1.4, 0.25, 0.75),
          new THREE.MeshStandardMaterial({
            color: 0x1a202c,
            metalness: 0.9,
            roughness: 0.1,
            emissive: new THREE.Color().setHSL(0.55, 0.8, 0.1 + Math.random() * 0.1),
            emissiveIntensity: 0.3
          })
        );
        server.name = `DataCenter-服务器单元-${i + 1}`;
        server.position.set(
          frame.position.x,
          this.bounds.min.y + 1.25 + 0.125 + i * 0.3, // 基于bounds.min.y定位
          frame.position.z + 0.05
        );
        server.castShadow = true;
        rackGroup.add(server);
        this.servers.push(server);
      }
      
      // LED指示灯 - 基于bounds.min.y定位
      for (let i = 0; i < 8; i++) {
        const led = new THREE.Mesh(
          new THREE.SphereGeometry(0.02, 8, 8),
          new THREE.MeshBasicMaterial({
            color: Math.random() > 0.5 ? 0x00ff00 : 0xff0000,
            emissive: Math.random() > 0.5 ? 0x00ff00 : 0xff0000,
            emissiveIntensity: 1.0
          })
        );
        led.name = `DataCenter-LED指示灯-${i + 1}`;
        led.position.set(
          frame.position.x - 0.7,
          this.bounds.min.y + 1.25 + 0.125 + i * 0.3, // 基于bounds.min.y定位
          frame.position.z + 0.4
        );
        rackGroup.add(led);
      }
      
      cabinGroup.add(rackGroup);
    }
  }

  /**
   * 创建显示屏
   * @private
   */
  _createScreens(cabinGroup) {
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    
    // 主显示屏（后墙，z轴负方向）- 基于bounds.min.y定位
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const mainScreen = new THREE.Mesh(
      new THREE.PlaneGeometry(4, 2.5),
      new THREE.MeshStandardMaterial({
        color: 0x000000,
        emissive: 0x0a0a2e,
        emissiveIntensity: 0.5
      })
    );
    mainScreen.name = 'DataCenter-主显示屏';
    mainScreen.position.set(
      boundsCenter.x, 
      this.bounds.min.y + wallHeight * 0.5 + 0.5, // 基于bounds.min.y定位
      this.bounds.min.z + 0.1
    );
    mainScreen.rotation.y = Math.PI;
    cabinGroup.add(mainScreen);
    this.screens.push(mainScreen);
    
    // 侧边显示屏（沿z轴方向排列）- 基于bounds.min.y定位
    for (let i = 0; i < 2; i++) {
      const sideScreen = new THREE.Mesh(
        new THREE.PlaneGeometry(1.5, 1),
        new THREE.MeshStandardMaterial({
          color: 0x000000,
          emissive: 0x0a0a2e,
          emissiveIntensity: 0.4
        })
      );
      sideScreen.name = `DataCenter-侧边显示屏-${i + 1}`;
      sideScreen.position.set(
        boundsCenter.x - boundsSize.x * 0.4 + i * boundsSize.x * 0.8,
        this.bounds.min.y + wallHeight * 0.5 + 1, // 基于bounds.min.y定位
        boundsCenter.z - boundsSize.z * 0.3
      );
      sideScreen.rotation.y = i === 0 ? Math.PI / 2 : -Math.PI / 2;
      cabinGroup.add(sideScreen);
      this.screens.push(sideScreen);
    }
  }

  /**
   * 添加照明
   * @private
   */
  _addLighting(cabinGroup) {
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    
    // 顶部蓝色照明（沿z轴方向排列）- 基于bounds.min.y定位
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const light1 = new THREE.PointLight(0x4a9eff, 0.6, 8);
    light1.position.set(
      boundsCenter.x - boundsSize.x * 0.25,
      this.bounds.min.y + wallHeight * 0.5 + 0.5, // 基于bounds.min.y定位
      boundsCenter.z - boundsSize.z * 0.3
    );
    cabinGroup.add(light1);
    
    const light2 = new THREE.PointLight(0x4a9eff, 0.6, 8);
    light2.position.set(
      boundsCenter.x + boundsSize.x * 0.25,
      this.bounds.min.y + wallHeight * 0.5 + 0.5, // 基于bounds.min.y定位
      boundsCenter.z - boundsSize.z * 0.3
    );
    cabinGroup.add(light2);
    
    // 环境光
    const ambient = new THREE.AmbientLight(0x1a1a3e, 0.3);
    cabinGroup.add(ambient);
  }

  /**
   * 更新动画（LED闪烁等）
   */
  update(deltaTime) {
    // 检查mesh是否存在且有效
    if (!this.mesh || typeof this.mesh.traverse !== 'function') {
      return;
    }
    
    try {
      // LED指示灯闪烁
      this.mesh.traverse((child) => {
        if (child && child.material && child.material.emissive) {
          const intensity = 0.5 + Math.sin(Date.now() * 0.005 + child.position.y * 10) * 0.5;
          child.material.emissiveIntensity = intensity;
        }
      });
    } catch (error) {
      // 静默处理错误，避免中断动画循环
      console.warn('⚠️ DataCenter.update error:', error);
    }
  }

  /**
   * 获取数据统计（虚拟数据）
   */
  getDataStats() {
    return {
      activeServers: this.servers.length,
      dataThroughput: Math.random() * 1000 + 500, // MB/s
      storageUsed: Math.random() * 30 + 70, // %
      lastBackup: new Date(Date.now() - Math.random() * 3600000).toISOString()
    };
  }
}

