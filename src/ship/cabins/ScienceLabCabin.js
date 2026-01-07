/**
 * 科学实验舱室
 * Science Laboratory Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class ScienceLabCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'science-lab',
      name: '科学实验舱室 | Science Laboratory Cabin',
      type: 'laboratory',
      description: '科学研究和实验区域 | Scientific research and experiment area',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-10, 5, -18),
        new THREE.Vector3(10, 16, 18)
      ),
      cameraConfig: {
        position: [0, 11, 0],
        target: [0, 11, 12],
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'ScienceLabCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a2a3e,
      roughness: 0.8,
      metalness: 0.2
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
    
    // 实验台（立方体）
    const benchGeometry = new THREE.BoxGeometry(4, 1, 1.5);
    const benchMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a3a4e,
      metalness: 0.6,
      roughness: 0.5
    });
    
    for (let i = 0; i < 6; i++) {
      const bench = new THREE.Mesh(benchGeometry, benchMaterial);
      bench.position.set(-6, this.bounds.min.y + 0.5, -15 + i * 6);
      bench.castShadow = true;
      cabinGroup.add(bench);
    }
    
    // 实验设备（立方体表示）
    const equipmentGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5);
    const equipmentMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a4a5e,
      metalness: 0.7,
      roughness: 0.4
    });
    
    for (let i = 0; i < 8; i++) {
      const equipment = new THREE.Mesh(equipmentGeometry, equipmentMaterial);
      equipment.position.set(6, this.bounds.min.y + 0.75, -14 + i * 4);
      equipment.castShadow = true;
      cabinGroup.add(equipment);
      
      // 设备指示灯
      const led = new THREE.Mesh(
        new THREE.SphereGeometry(0.08, 8, 8),
        new THREE.MeshBasicMaterial({
          color: 0x4a9eff,
          emissive: 0x4a9eff,
          emissiveIntensity: 0.7
        })
      );
      led.position.set(6, this.bounds.min.y + 1.6, -14 + i * 4);
      cabinGroup.add(led);
    }
    
    // 样品存储柜
    const storageGeometry = new THREE.BoxGeometry(1, 3, 2);
    const storageMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a2a3e,
      metalness: 0.5,
      roughness: 0.6
    });
    
    for (let i = 0; i < 4; i++) {
      const storage = new THREE.Mesh(storageGeometry, storageMaterial);
      storage.position.set(-10.5, this.bounds.min.y + 1.5, -12 + i * 8);
      storage.castShadow = true;
      cabinGroup.add(storage);
    }
    
    // 监控屏幕
    const monitorGeometry = new THREE.BoxGeometry(0.1, 0.8, 1);
    const monitorMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      metalness: 0.8,
      roughness: 0.3
    });
    
    for (let i = 0; i < 4; i++) {
      const monitor = new THREE.Mesh(monitorGeometry, monitorMaterial);
      monitor.position.set(-6.55, this.bounds.min.y + 2.5, -10 + i * 6.5);
      monitor.castShadow = true;
      cabinGroup.add(monitor);
      
      // 屏幕显示
      const screen = new THREE.Mesh(
        new THREE.PlaneGeometry(0.7, 0.9),
        new THREE.MeshBasicMaterial({
          color: 0x00ff00,
          emissive: 0x00ff00,
          emissiveIntensity: 0.5
        })
      );
      screen.rotation.y = Math.PI / 2;
      screen.position.set(-6.6, this.bounds.min.y + 2.5, -10 + i * 6.5);
      cabinGroup.add(screen);
    }
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const wallThickness = 0.2;
    // 科学实验室：青色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ced1, // 青色
      transparent: true,
      opacity: 0.85,
      roughness: 0.1,
      metalness: 0.0
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
        color: 0x4a4a5e,
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

