/**
 * 导航控制舱室
 * Navigation Control Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class NavigationControlCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'navigation-control',
      name: '导航控制舱室 | Navigation Control Cabin',
      type: 'navigation',
      description: '船舶导航和控制系统 | Ship navigation and control system',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-10, 20, -12),
        new THREE.Vector3(10, 28, 12)
      ),
      cameraConfig: {
        position: [0, 24, 0],
        target: [0, 24, 12],
        fov: 75
      },
      ...config
    });
  }

  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'NavigationControlCabin';
    
    // 舱室地板
    const floorSize = this.bounds.getSize(new THREE.Vector3());
    const floorGeometry = new THREE.PlaneGeometry(floorSize.x, floorSize.z);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      roughness: 0.8,
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
    
    // 导航控制台（主控制台）
    const consoleGeometry = new THREE.BoxGeometry(2, 1.5, 8);
    const consoleMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a2a3e,
      metalness: 0.5,
      roughness: 0.5
    });
    const mainConsole = new THREE.Mesh(consoleGeometry, consoleMaterial);
    mainConsole.position.set(0, this.bounds.min.y + 0.75, 0);
    mainConsole.castShadow = true;
    cabinGroup.add(mainConsole);
    
    // 多个显示屏
    const screenGeometry = new THREE.PlaneGeometry(1, 1.5);
    const screenMaterial = new THREE.MeshBasicMaterial({
      color: 0x4a9eff,
      emissive: 0x4a9eff,
      emissiveIntensity: 0.6
    });
    
    for (let i = 0; i < 5; i++) {
      const screen = new THREE.Mesh(screenGeometry, screenMaterial);
      screen.rotation.y = Math.PI / 2;
      screen.position.set(1.01, this.bounds.min.y + 1.5, -6 + i * 3);
      cabinGroup.add(screen);
    }
    
    // 雷达显示器
    const radarGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.2, 32);
    const radarMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      metalness: 0.8,
      roughness: 0.2
    });
    const radar = new THREE.Mesh(radarGeometry, radarMaterial);
    radar.rotation.x = Math.PI / 2;
    radar.position.set(-6, this.bounds.min.y + 2, -8);
    radar.castShadow = true;
    cabinGroup.add(radar);
    
    // 雷达屏幕
    const radarScreen = new THREE.Mesh(
      new THREE.CircleGeometry(1.3, 32),
      new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 0.4
      })
    );
    radarScreen.rotation.x = -Math.PI / 2;
    radarScreen.position.set(-6, this.bounds.min.y + 2.1, -8);
    cabinGroup.add(radarScreen);
    
    // 控制按钮和指示灯
    for (let i = 0; i < 8; i++) {
      const button = new THREE.Mesh(
        new THREE.CylinderGeometry(0.1, 0.1, 0.05, 16),
        new THREE.MeshStandardMaterial({
          color: 0x4a4a4a,
          metalness: 0.9,
          roughness: 0.1
        })
      );
      button.rotation.x = Math.PI / 2;
      button.position.set(1.01, this.bounds.min.y + 0.5, -7 + i * 2);
      cabinGroup.add(button);
    }
    
    // 添加6面体封闭：墙壁和天花板
    const wallHeight = this.bounds.max.y - this.bounds.min.y;
    const boundsSize = this.bounds.getSize(new THREE.Vector3());
    const boundsCenter = this.bounds.getCenter(new THREE.Vector3());
    const wallThickness = 0.2;
    // 导航控制舱：绿色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x4ade80, // 绿色
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
        color: 0x3a3a4e,
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

