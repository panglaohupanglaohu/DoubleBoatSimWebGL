/**
 * 卫星通信舱室
 * Satellite Communication Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class SatelliteCommCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'satellite-comm',
      name: '卫星通信舱室 | Satellite Communication Cabin',
      type: 'communication',
      description: '卫星通信和导航系统 | Satellite communication and navigation system',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-8, 20, -10),
        new THREE.Vector3(8, 30, 10)
      ),
      cameraConfig: {
        position: [0, 25, 0],
        target: [0, 25, 10],
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'SatelliteCommCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a2a2a,
      roughness: 0.7,
      metalness: 0.3
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
    
    // 通信设备机架（立方体）
    const rackGeometry = new THREE.BoxGeometry(1.5, 3, 0.8);
    const rackMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a1a,
      metalness: 0.9,
      roughness: 0.2
    });
    
    for (let i = 0; i < 4; i++) {
      const rack = new THREE.Mesh(rackGeometry, rackMaterial);
      rack.position.set(0, this.bounds.min.y + 1.5, -6 + i * 4);
      rack.castShadow = true;
      cabinGroup.add(rack);
      
      // 设备面板LED
      for (let j = 0; j < 3; j++) {
        const led = new THREE.Mesh(
          new THREE.SphereGeometry(0.05, 8, 8),
          new THREE.MeshBasicMaterial({
            color: 0x4a9eff,
            emissive: 0x4a9eff,
            emissiveIntensity: 0.8
          })
        );
        led.position.set(0.45, this.bounds.min.y + 1 + j * 0.8, -6 + i * 4);
        cabinGroup.add(led);
      }
    }
    
    // 卫星天线控制台
    const consoleGeometry = new THREE.BoxGeometry(1.5, 1, 3);
    const consoleMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a5f8f,
      metalness: 0.6,
      roughness: 0.4
    });
    const console = new THREE.Mesh(consoleGeometry, consoleMaterial);
    console.position.set(-5, this.bounds.min.y + 0.5, 0);
    console.castShadow = true;
    cabinGroup.add(console);
    
    // 显示屏（模拟）
    const screenGeometry = new THREE.PlaneGeometry(1, 2);
    const screenMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      emissive: 0x00ff00,
      emissiveIntensity: 0.5
    });
    const screen = new THREE.Mesh(screenGeometry, screenMaterial);
    screen.rotation.y = Math.PI / 2;
    screen.position.set(-5.76, this.bounds.min.y + 1, 0);
    cabinGroup.add(screen);
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const wallThickness = 0.2;
    // 卫星通信舱：天蓝色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x87ceeb, // 天蓝色
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
        color: 0x4a4a5a,
        roughness: 0.8,
        metalness: 0.2
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

