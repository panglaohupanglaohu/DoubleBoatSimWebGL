/**
 * 电源供应舱室
 * Power Supply Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class PowerSupplyCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'power-supply',
      name: '电源供应舱室 | Power Supply Cabin',
      type: 'power',
      description: '船舶主电源供应系统 | Main power supply system',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-8, 5, -15),
        new THREE.Vector3(8, 15, 15)
      ),
      cameraConfig: {
        position: [0, 8, 0],
        target: [0, 10, 12],
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'PowerSupplyCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x333333,
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
    
    // 发电机组（立方体表示）
    const generatorGeometry = new THREE.BoxGeometry(4, 3, 2);
    const generatorMaterial = new THREE.MeshStandardMaterial({
      color: 0x444444,
      metalness: 0.8,
      roughness: 0.3
    });
    
    for (let i = 0; i < 3; i++) {
      const generator = new THREE.Mesh(generatorGeometry, generatorMaterial);
      generator.position.set(0, this.bounds.min.y + 1.5, -8 + i * 8);
      generator.castShadow = true;
      cabinGroup.add(generator);
    }
    
    // 配电柜
    const panelGeometry = new THREE.BoxGeometry(0.5, 4, 2);
    const panelMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a5f8f,
      metalness: 0.7,
      roughness: 0.4
    });
    
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.position.set(0, this.bounds.min.y + 2, 12);
    panel.castShadow = true;
    cabinGroup.add(panel);
    
    // LED指示灯
    const ledGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const ledMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      emissive: 0x00ff00,
      emissiveIntensity: 1.0
    });
    
    for (let i = 0; i < 5; i++) {
      const led = new THREE.Mesh(ledGeometry, ledMaterial);
      led.position.set(0, this.bounds.min.y + 3, -10 + i * 5);
      cabinGroup.add(led);
    }
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const wallThickness = 0.2;
    // 电源供应舱：橙色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0xffa500, // 橙色
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
        color: 0x5a5a5a,
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

