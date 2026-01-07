/**
 * 生活舱室
 * Living Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class LivingCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'living-cabin',
      name: '生活舱室 | Living Cabin',
      type: 'accommodation',
      description: '船员生活休息区域 | Crew living and rest area',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-12, 5, -15),  // x轴=宽度，z轴=长度（长边）
        new THREE.Vector3(12, 15, 15)
      ),
      cameraConfig: {
        position: [0, 10, 0],  // 相机在舱室中心
        target: [0, 10, 10],   // 看向z轴正方向（船尾方向）
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'LivingCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a3a3a,
      roughness: 0.7,
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
    
    // 获取bounds的尺寸和范围（z轴为长边）
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const zLength = boundsSize.z; // z轴是长边
    const zStart = this.bounds.min.z;
    const zEnd = this.bounds.max.z;
    
    // 床铺（立方体表示）- 沿z轴（长边）排列
    const bedGeometry = new THREE.BoxGeometry(2, 0.5, 1);
    const bedMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a4a4a,
      roughness: 0.8,
      metalness: 0.1
    });
    
    const bedCount = Math.floor(zLength / 3); // 根据舱室长度计算床铺数量
    const bedSpacing = zLength / (bedCount + 1);
    for (let i = 0; i < bedCount; i++) {
      const bed = new THREE.Mesh(bedGeometry, bedMaterial);
      bed.position.set(
        boundsCenter.x - boundsSize.x * 0.3, // 左侧
        this.bounds.min.y + 0.25,
        zStart + (i + 1) * bedSpacing
      );
      bed.castShadow = true;
      cabinGroup.add(bed);
    }
    
    // 桌子 - 沿z轴（长边）排列
    const tableGeometry = new THREE.BoxGeometry(1.5, 0.1, 3);
    const tableMaterial = new THREE.MeshStandardMaterial({
      color: 0x5a4a3a,
      roughness: 0.6,
      metalness: 0.2
    });
    
    const tableCount = Math.floor(bedCount / 2);
    const tableSpacing = zLength / (tableCount + 1);
    for (let i = 0; i < tableCount; i++) {
      const table = new THREE.Mesh(tableGeometry, tableMaterial);
      table.position.set(
        boundsCenter.x + boundsSize.x * 0.3, // 右侧
        this.bounds.min.y + 0.8,
        zStart + (i + 1) * tableSpacing
      );
      table.castShadow = true;
      cabinGroup.add(table);
    }
    
    // 储物柜 - 沿z轴（长边）排列
    const lockerGeometry = new THREE.BoxGeometry(0.8, 2, 1);
    const lockerMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a3a3a,
      metalness: 0.5,
      roughness: 0.5
    });
    
    const lockerCount = Math.floor(zLength / 2.5);
    const lockerSpacing = zLength / (lockerCount + 1);
    for (let i = 0; i < lockerCount; i++) {
      const locker = new THREE.Mesh(lockerGeometry, lockerMaterial);
      locker.position.set(
        boundsCenter.x, // 中间
        this.bounds.min.y + 1,
        zStart + (i + 1) * lockerSpacing
      );
      locker.castShadow = true;
      cabinGroup.add(locker);
    }
    
    // 照明灯 - 沿z轴（长边）排列
    const lightGeometry = new THREE.SphereGeometry(0.3, 16, 16);
    const lightMaterial = new THREE.MeshBasicMaterial({
      color: 0xffffaa,
      emissive: 0xffffaa,
      emissiveIntensity: 0.8
    });
    
    const lightCount = Math.floor(zLength / 4);
    const lightSpacing = zLength / (lightCount + 1);
    for (let i = 0; i < lightCount; i++) {
      const light = new THREE.Mesh(lightGeometry, lightMaterial);
      light.position.set(
        boundsCenter.x,
        this.bounds.min.y + 4,
        zStart + (i + 1) * lightSpacing
      );
      cabinGroup.add(light);
    }
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const wallThickness = 0.2;
    // 生活舱室：粉红色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0xff6b6b, // 粉红色
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
        roughness: 0.6,
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

