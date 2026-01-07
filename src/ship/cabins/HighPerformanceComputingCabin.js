/**
 * 高性能计算舱室
 * High Performance Computing Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class HighPerformanceComputingCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'hpc-cabin',
      name: '高性能计算舱室 | HPC Cabin',
      type: 'computing',
      description: '高性能计算服务器集群 | High performance computing server cluster',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-10, 5, -20),
        new THREE.Vector3(10, 18, 20)
      ),
      cameraConfig: {
        position: [0, 12, 0],
        target: [0, 12, 15],
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'HPCCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a1a,
      roughness: 0.9,
      metalness: 0.1
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
    
    // 服务器机架（多个立方体）
    const rackGeometry = new THREE.BoxGeometry(0.8, 2.5, 1);
    const rackMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a1a,
      metalness: 0.8,
      roughness: 0.3
    });
    
    // 调试：输出bounds信息
    console.log(`📦 HPCCabin bounds: min.y=${this.bounds.min.y.toFixed(2)}m, max.y=${this.bounds.max.y.toFixed(2)}m, 地板高度=${this.bounds.min.y.toFixed(2)}m`);
    
    // 创建两排服务器机架 - 确保基于bounds.min.y定位
    const rackBaseY = this.bounds.min.y + 1.25; // 机架底部距离地板1.25米
    for (let row = 0; row < 2; row++) {
      for (let i = 0; i < 12; i++) {
        const rack = new THREE.Mesh(rackGeometry, rackMaterial);
        rack.position.set(
          -4 + row * 8,
          rackBaseY, // 使用计算出的Y位置
          -18 + i * 3.2
        );
        if (row === 0 && i === 0) {
          console.log(`  📐 机架 ${row + 1}-${i + 1} 位置: Y=${rackBaseY.toFixed(2)}m (距离地板1.25m, 距离船底${rackBaseY.toFixed(2)}m)`);
        }
        rack.castShadow = true;
        rack.name = `HPCCabin-服务器机架-${row + 1}-${i + 1}`;
        cabinGroup.add(rack);
        
        // 服务器LED指示灯
        for (let j = 0; j < 4; j++) {
          const led = new THREE.Mesh(
            new THREE.SphereGeometry(0.03, 8, 8),
            new THREE.MeshBasicMaterial({
              color: 0x00ff00,
              emissive: 0x00ff00,
              emissiveIntensity: 0.9
            })
          );
          led.name = `HPCCabin-LED指示灯-${row + 1}-${i + 1}-${j + 1}`;
          led.position.set(
            -4 + row * 8 + 0.51,
            this.bounds.min.y + 0.5 + j * 0.6,
            -18 + i * 3.2
          );
          cabinGroup.add(led);
        }
      }
    }
    
    // 冷却系统
    const coolerGeometry = new THREE.BoxGeometry(1.5, 1.5, 2);
    const coolerMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a5f8f,
      metalness: 0.7,
      roughness: 0.4
    });
    
    for (let i = 0; i < 4; i++) {
      const cooler = new THREE.Mesh(coolerGeometry, coolerMaterial);
      cooler.name = `HPCCabin-冷却系统-${i + 1}`;
      cooler.position.set(0, this.bounds.min.y + 0.75, -15 + i * 10);
      cooler.castShadow = true;
      cabinGroup.add(cooler);
    }
    
    // 控制面板
    const controlPanel = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, 2, 4),
      new THREE.MeshStandardMaterial({
        color: 0x1a1a2e,
        metalness: 0.6,
        roughness: 0.5
      })
    );
    controlPanel.name = 'HPCCabin-控制面板';
    controlPanel.position.set(-10.1, this.bounds.min.y + 1, 0);
    controlPanel.castShadow = true;
    cabinGroup.add(controlPanel);
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const wallThickness = 0.2;
    // 高性能计算舱：紫色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x9b59b6, // 紫色
      transparent: true,
      opacity: 0.85,
      roughness: 0.1,
      metalness: 0.0,
      // 注意：MeshStandardMaterial 不支持 transmission，只使用 opacity 实现透明效果
    });
    
    // 后墙（z轴负方向）
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(boundsSize.x, wallHeight, wallThickness),
      wallMaterial
    );
    backWall.position.set(boundsCenter.x, boundsCenter.y, this.bounds.min.z);
    backWall.castShadow = true;
    cabinGroup.add(backWall);
    
    // 前墙（z轴正方向）
    const frontWall = new THREE.Mesh(
      new THREE.BoxGeometry(boundsSize.x, wallHeight, wallThickness),
      wallMaterial
    );
    frontWall.position.set(boundsCenter.x, boundsCenter.y, this.bounds.max.z);
    frontWall.castShadow = true;
    cabinGroup.add(frontWall);
    
    // 左墙（x轴负方向）
    const leftWall = new THREE.Mesh(
      new THREE.BoxGeometry(wallThickness, wallHeight, boundsSize.z),
      wallMaterial
    );
    leftWall.position.set(this.bounds.min.x, boundsCenter.y, boundsCenter.z);
    leftWall.castShadow = true;
    cabinGroup.add(leftWall);
    
    // 右墙（x轴正方向）
    const rightWall = new THREE.Mesh(
      new THREE.BoxGeometry(wallThickness, wallHeight, boundsSize.z),
      wallMaterial
    );
    rightWall.position.set(this.bounds.max.x, boundsCenter.y, boundsCenter.z);
    rightWall.castShadow = true;
    cabinGroup.add(rightWall);
    
    // 天花板
    const ceiling = new THREE.Mesh(
      new THREE.PlaneGeometry(boundsSize.x, boundsSize.z),
      new THREE.MeshStandardMaterial({
        color: 0x3a3a3a,
        roughness: 0.8,
        metalness: 0.1
      })
    );
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.set(boundsCenter.x, this.bounds.max.y, boundsCenter.z);
    ceiling.receiveShadow = true;
    cabinGroup.add(ceiling);
    
    // 添加高亮舱室名字标注（5米大小）
    const nameLabel = this._createHighlightCabinNameLabel(this.name, 5.0);
    cabinGroup.add(nameLabel);
    
    // 添加高度标尺（从模型底部到舱室地板）
    const heightRuler = this._createHeightRuler(cabinGroup);
    cabinGroup.add(heightRuler);
    
    this.mesh = cabinGroup;
    // 不再直接添加到场景，由CabinManager添加到船模型中
    // scene.add(cabinGroup);
    
    return cabinGroup;
  }
}

