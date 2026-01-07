/**
 * 零部件仓库舱室
 * Parts Warehouse Cabin
 */

import * as THREE from '../../../public/lib/three.module.js';
import { CabinBase } from './CabinBase.js';

export class PartsWarehouse extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'parts-warehouse',
      name: '零部件仓库 | Parts Warehouse',
      type: 'warehouse',
      description: '存储船舶备件和维修工具 | Stores ship spare parts and maintenance tools',
      bounds: config.bounds || new THREE.Box3(
        new THREE.Vector3(-8, 0, -6),
        new THREE.Vector3(8, 4, 6)
      ),
      cameraConfig: {
        position: [0, 2.5, 8],
        target: [0, 1.5, 0],
        fov: 75
      },
      ...config
    });
    
    this.shelves = [];
    this.parts = [];
  }

  build(scene, shipPosition, shipRotation) {
    // 创建舱室容器
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'PartsWarehouse';
    
    // 舱室地板
    const floorGeometry = new THREE.PlaneGeometry(16, 12);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a4a4a,
      roughness: 0.8,
      metalness: 0.1
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    cabinGroup.add(floor);
    
    // 添加蓝色网状面高亮地板
    const floorWireframeGeometry = new THREE.PlaneGeometry(16, 12, 10, 10);
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
    floorWireframe.position.y = 0.01; // 稍微抬高，避免z-fighting
    floorWireframe.renderOrder = 999; // 确保在最前面渲染
    cabinGroup.add(floorWireframe);
    
    // 舱室墙壁
    const wallHeight = 4;
    const wallThickness = 0.2;
    // 零部件仓库：灰色透明玻璃墙壁（85%透明度）
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x888888, // 灰色
      transparent: true,
      opacity: 0.85,
      roughness: 0.1,
      metalness: 0.0,
      // 注意：MeshStandardMaterial 不支持 transmission，只使用 opacity 实现透明效果
    });
    
    // 后墙
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(16, wallHeight, wallThickness),
      wallMaterial
    );
    backWall.position.set(0, wallHeight / 2, -6);
    backWall.castShadow = true;
    cabinGroup.add(backWall);
    
    // 左墙
    const leftWall = new THREE.Mesh(
      new THREE.BoxGeometry(wallThickness, wallHeight, 12),
      wallMaterial
    );
    leftWall.position.set(-8, wallHeight / 2, 0);
    leftWall.castShadow = true;
    cabinGroup.add(leftWall);
    
    // 右墙
    const rightWall = new THREE.Mesh(
      new THREE.BoxGeometry(wallThickness, wallHeight, 12),
      wallMaterial
    );
    rightWall.position.set(8, wallHeight / 2, 0);
    rightWall.castShadow = true;
    cabinGroup.add(rightWall);
    
    // 前墙
    const frontWall = new THREE.Mesh(
      new THREE.BoxGeometry(16, wallHeight, wallThickness),
      wallMaterial
    );
    frontWall.position.set(0, wallHeight / 2, 6);
    frontWall.castShadow = true;
    cabinGroup.add(frontWall);
    
    // 天花板
    const ceiling = new THREE.Mesh(
      new THREE.PlaneGeometry(16, 12),
      new THREE.MeshStandardMaterial({ color: 0x8a8a8a })
    );
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.y = wallHeight;
    cabinGroup.add(ceiling);
    
    // 为组件添加前缀
    floor.name = 'PartsWarehouse-地板';
    backWall.name = 'PartsWarehouse-后墙';
    leftWall.name = 'PartsWarehouse-左墙';
    rightWall.name = 'PartsWarehouse-右墙';
    frontWall.name = 'PartsWarehouse-前墙';
    ceiling.name = 'PartsWarehouse-天花板';
    
    // 创建货架
    this._createShelves(cabinGroup);
    
    // 创建零部件（虚拟对象）
    this._createParts(cabinGroup);
    
    // 添加照明
    this._addLighting(cabinGroup);
    
    this.mesh = cabinGroup;
    return cabinGroup;
  }

  /**
   * 创建货架
   * @private
   */
  _createShelves(cabinGroup) {
    const shelfMaterial = new THREE.MeshStandardMaterial({
      color: 0x8b7355,
      roughness: 0.6,
      metalness: 0.2
    });
    
    // 创建3排货架
    for (let row = 0; row < 3; row++) {
      const shelfGroup = new THREE.Group();
      
      // 每个货架有4层
      for (let level = 0; level < 4; level++) {
        const shelf = new THREE.Mesh(
          new THREE.BoxGeometry(3, 0.1, 1.2),
          shelfMaterial
        );
        shelf.position.set(
          -4.5 + row * 4.5,
          0.3 + level * 0.8,
          -4 + (row % 2) * 2
        );
        shelf.castShadow = true;
        shelf.receiveShadow = true;
        shelf.name = `PartsWarehouse-货架-${row + 1}-${level + 1}`;
        shelfGroup.add(shelf);
        
        // 货架支撑柱
        const post = new THREE.Mesh(
          new THREE.BoxGeometry(0.1, 0.8, 0.1),
          shelfMaterial
        );
        post.name = `PartsWarehouse-支撑柱-${row + 1}-${level + 1}-1`;
        post.position.set(
          shelf.position.x - 1.4,
          shelf.position.y - 0.4,
          shelf.position.z
        );
        shelfGroup.add(post);
        
        const post2 = post.clone();
        post2.name = `PartsWarehouse-支撑柱-${row + 1}-${level + 1}-2`;
        post2.position.x = shelf.position.x + 1.4;
        shelfGroup.add(post2);
      }
      
      shelfGroup.name = `PartsWarehouse-货架组-${row + 1}`;
      cabinGroup.add(shelfGroup);
      this.shelves.push(shelfGroup);
    }
  }

  /**
   * 创建零部件（虚拟对象）
   * @private
   */
  _createParts(cabinGroup) {
    const partColors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf9ca24, 0x6c5ce7];
    
    // 在货架上随机放置零部件
    this.shelves.forEach((shelf, shelfIndex) => {
      for (let i = 0; i < 4; i++) {
        const part = new THREE.Mesh(
          new THREE.BoxGeometry(0.3, 0.3, 0.3),
          new THREE.MeshStandardMaterial({
            color: partColors[Math.floor(Math.random() * partColors.length)],
            metalness: 0.5,
            roughness: 0.3
          })
        );
        
        const shelfLevel = shelf.children[i * 3]; // 获取对应的货架层
        if (shelfLevel) {
          part.position.copy(shelfLevel.position);
          part.position.y += 0.2;
          part.position.x += (Math.random() - 0.5) * 2;
          part.position.z += (Math.random() - 0.5) * 0.8;
          part.castShadow = true;
          part.receiveShadow = true;
          part.name = `PartsWarehouse-零部件-${shelfIndex + 1}-${i + 1}`;
          
          cabinGroup.add(part);
          this.parts.push(part);
          this.addObject(part, true); // 标记为可交互
        }
      }
    });
    
    // 添加标签
    this._addLabels(cabinGroup);
  }

  /**
   * 添加标签
   * @private
   */
  _addLabels(cabinGroup) {
    const labels = [
      { text: 'A区 | Zone A', position: [-4, 3.5, -4] },
      { text: 'B区 | Zone B', position: [0, 3.5, -2] },
      { text: 'C区 | Zone C', position: [4, 3.5, -4] }
    ];
    
    labels.forEach(label => {
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(0, 0, 256, 64);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(label.text, 128, 32);
      
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.position.set(...label.position);
      sprite.scale.set(2, 0.5, 1);
      cabinGroup.add(sprite);
    });
  }

  /**
   * 添加照明
   * @private
   */
  _addLighting(cabinGroup) {
    // 顶部照明
    const light1 = new THREE.PointLight(0xffffff, 0.8, 10);
    light1.position.set(-4, 3.5, -2);
    cabinGroup.add(light1);
    
    const light2 = new THREE.PointLight(0xffffff, 0.8, 10);
    light2.position.set(0, 3.5, -2);
    cabinGroup.add(light2);
    
    const light3 = new THREE.PointLight(0xffffff, 0.8, 10);
    light3.position.set(4, 3.5, -2);
    cabinGroup.add(light3);
  }

  /**
   * 获取库存信息（虚拟数据）
   */
  getInventory() {
    return {
      totalParts: this.parts.length,
      categories: ['Engine Parts', 'Electrical', 'Hydraulic', 'Structural'],
      criticalItems: 12,
      lastUpdate: new Date().toISOString()
    };
  }
}

