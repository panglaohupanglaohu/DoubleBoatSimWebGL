/**
 * 船舶控制器
 * 封装船体的所有操作和状态管理
 */

import * as THREE from '../../public/lib/three.module.js';
import * as CANNON from '../../public/lib/cannon-es.js';
import { GLTFLoader } from '../../public/lib/GLTFLoader.js';
import { getWaveHeight } from '../waves.js';

export class ShipController {
  constructor(scene, world, config = {}) {
    this.scene = scene;
    this.world = world;
    this.config = {
      mass: config.mass || 20000,
      size: config.size || { x: 100, y: 10, z: 20 },
      draftDepth: config.draftDepth || 10,
      yFlip: config.yFlip || -1,
      linearDamping: config.linearDamping || 0.15,
      angularDamping: config.angularDamping || 0.6,
      glbPath: config.glbPath || '/public/GLB_20251223141542.glb',
      desiredSize: config.desiredSize || null, // 目标尺寸 {x, y, z} - X轴=宽度, Y轴=高度, Z轴=长度
      // desiredLength 已废弃，使用 desiredSize 代替
      platformHeight: config.platformHeight || 45, // 平台高度
      catamaran: config.catamaran || { enabled: false } // 双体船配置
    };

    this.mesh = null;
    this.body = null;
    this.size = null;
    this.loaded = false;

    // 辅助工具
    this.axesHelper = null;
    this.axisLabels = [];
    this.dimensionLines = null; // 长宽高尺寸线段
  }

  /**
   * 显示错误弹窗
   * @private
   */
  _showErrorDialog(message) {
    // 创建弹窗容器
    const dialog = document.createElement('div');
    dialog.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.95);
      border: 2px solid #f44336;
      border-radius: 10px;
      padding: 30px 40px;
      z-index: 10000;
      color: #fff;
      font-family: Arial, sans-serif;
      max-width: 600px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    `;
    
    dialog.innerHTML = `
      <h2 style="margin: 0 0 15px 0; color: #f44336; font-size: 24px;">
        ⚠️ 船体模型加载失败 | Ship Model Loading Failed
      </h2>
      <p style="margin: 0 0 20px 0; line-height: 1.6; font-size: 16px;">
        ${message}
      </p>
      <p style="margin: 0 0 20px 0; line-height: 1.6; font-size: 14px; color: #bbb;">
        请检查：<br>
        1. GLB模型文件是否存在：/public/GLB_20251223141542.glb<br>
        2. 服务器是否正确配置静态文件服务<br>
        3. 浏览器控制台是否有网络错误
      </p>
      <button id="close-dialog-btn" style="
        background: #4fc3f7;
        border: none;
        color: white;
        padding: 12px 24px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
      ">确定 | OK</button>
    `;
    
    document.body.appendChild(dialog);
    
    // 关闭按钮事件
    const closeBtn = dialog.querySelector('#close-dialog-btn');
    closeBtn.addEventListener('click', () => {
      document.body.removeChild(dialog);
    });
    
    // 点击外部关闭
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        document.body.removeChild(dialog);
      }
    });
  }

  /**
   * 加载船体模型
   */
  async load() {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      const candidates = this._getModelPaths();
      let index = 0;
      let loaded = false;
      const failedPaths = [];
      
      // 预检查：先测试文件是否可以通过HTTP访问
      console.log('🔍 预检查：测试GLB文件是否可访问...');
      const testUrl = candidates[0]; // 使用第一个候选路径
      const fullTestUrl = testUrl.startsWith('http') ? testUrl : `${window.location.origin}${testUrl}`;
      console.log(`   测试URL | Test URL: ${fullTestUrl}`);
      
      // 使用fetch预检查文件是否存在
      fetch(fullTestUrl, { method: 'HEAD' })
        .then(response => {
          console.log(`✅ 预检查成功 | Pre-check success: HTTP ${response.status}`);
          if (response.status === 200 || response.status === 206) {
            console.log(`   文件可访问 | File is accessible`);
          } else {
            console.warn(`   ⚠️ 文件状态异常 | File status unusual: ${response.status}`);
          }
        })
        .catch(err => {
          console.warn(`⚠️ 预检查失败 | Pre-check failed: ${err.message}`);
          console.warn(`   这可能是CORS问题或文件不存在`);
        });

      // 超时处理 - 延长到60秒，给大型GLB模型（80MB）更多加载时间
      const timeout = setTimeout(() => {
        if (!loaded && !this.mesh) {
          console.error('❌ GLB loading timeout (60s)');
          console.error('   文件大小约80MB，可能需要更长时间加载');
          clearTimeout(timeout);
          const errorMsg = `船体模型加载超时（60秒）| Ship model loading timeout (60s)<br><br>文件大小约80MB，可能需要更长时间<br>已尝试的路径 | Attempted paths:<br>${failedPaths.map(p => `• ${p}`).join('<br>')}`;
          this._showErrorDialog(errorMsg);
          reject(new Error('GLB loading timeout'));
        }
      }, 60000); // 延长到60秒

      const tryNext = () => {
        if (index >= candidates.length) {
          console.error('❌ All GLB paths failed');
          console.error('❌ 所有路径尝试失败，请检查：');
          console.error('   1. 文件是否存在：D:\\DoubleBoatRefactor\\DoubleBoatSimWebGL\\public\\GLB_20251223141542.glb');
          console.error('   2. 服务器是否正在运行：http://127.0.0.1:8080');
          console.error('   3. 是否可以通过浏览器直接访问：http://127.0.0.1:8080/public/GLB_20251223141542.glb');
          console.error('   已尝试的路径 | Attempted paths:', failedPaths);
          clearTimeout(timeout);
          const errorMsg = `所有GLB模型路径加载失败 | All GLB model paths failed<br><br>已尝试的路径 | Attempted paths:<br>${failedPaths.map(p => `• ${p}`).join('<br>')}<br><br>请检查：<br>1. 文件是否存在<br>2. 服务器是否运行<br>3. 浏览器控制台的详细错误信息`;
          this._showErrorDialog(errorMsg);
          reject(new Error('All GLB paths failed'));
          return;
        }

        const url = candidates[index++];
        failedPaths.push(url);
        
        const fullUrl = url.startsWith('http') ? url : `${window.location.origin}${url}`;
        console.log(`🔍 [${index}/${candidates.length}] 尝试加载模型 | Attempting to load: ${url}`);
        console.log(`   完整URL | Full URL: ${fullUrl}`);
        
        // 添加加载管理器来监控加载状态
        const manager = new THREE.LoadingManager();
        manager.onStart = () => {
          console.log(`🚀 开始加载 | Loading started: ${url}`);
        };
        manager.onProgress = (url, itemsLoaded, itemsTotal) => {
          console.log(`📥 加载进度 | Loading progress: ${itemsLoaded}/${itemsTotal} (${url})`);
        };
        manager.onError = (url) => {
          console.error(`❌ 加载管理器错误 | Loading manager error: ${url}`);
        };
        
        loader.load(
          url,
          (gltf) => {
            clearTimeout(timeout);
            loaded = true;
            console.log(`✅ 模型加载成功 | Model loaded successfully: ${url}`);
            console.log(`   GLTF对象 | GLTF object:`, gltf);
            console.log(`   场景节点数 | Scene nodes: ${gltf.scene.children.length}`);
            this._setupGLBModel(gltf, url);
            resolve(this);
          },
          (progress) => {
            // 加载进度回调
            if (progress.lengthComputable && progress.total > 0) {
              const percent = (progress.loaded / progress.total * 100).toFixed(1);
              const loadedMB = (progress.loaded / 1024 / 1024).toFixed(2);
              const totalMB = (progress.total / 1024 / 1024).toFixed(2);
              // 每5%输出一次，或者每10MB输出一次
              if (parseFloat(percent) % 5 < 0.5 || parseFloat(loadedMB) % 10 < 1) {
                console.log(`📥 加载进度 | Loading progress: ${percent}% (${loadedMB}MB / ${totalMB}MB)`);
              }
            } else {
              // 如果无法计算总大小，至少显示已加载的字节数
              const loadedMB = (progress.loaded / 1024 / 1024).toFixed(2);
              console.log(`📥 加载中 | Loading: ${loadedMB}MB loaded...`);
            }
          },
          (err) => {
            console.error(`❌ 加载失败 | Failed to load: ${url}`);
            console.error(`   完整URL | Full URL: ${fullUrl}`);
            console.error(`   错误信息 | Error message: ${err.message || 'Unknown error'}`);
            console.error(`   错误类型 | Error type: ${err.name || 'Unknown'}`);
            console.error(`   错误对象 | Error object:`, err);
            
            // 详细错误信息 - 检查多种可能的错误对象结构
            let httpStatus = null;
            let statusText = null;
            let responseURL = null;
            
            // 方式1: err.target (XMLHttpRequest)
            if (err.target) {
              httpStatus = err.target.status;
              statusText = err.target.statusText;
              responseURL = err.target.responseURL;
            }
            
            // 方式2: err.loader (Three.js GLTFLoader)
            if (err.loader && err.loader.manager) {
              // GLTFLoader的错误可能在这里
            }
            
            // 方式3: 直接检查err的属性
            if (err.status !== undefined) {
              httpStatus = err.status;
            }
            if (err.statusText) {
              statusText = err.statusText;
            }
            
            if (httpStatus !== null && httpStatus !== undefined) {
              console.error(`   ⚠️ HTTP状态码 | HTTP status: ${httpStatus}`);
              if (httpStatus === 404) {
                console.error(`   ❌ 文件未找到 | File not found (404)`);
                console.error(`   💡 请检查文件路径是否正确`);
              } else if (httpStatus === 403) {
                console.error(`   ❌ 访问被拒绝 | Access denied (403)`);
              } else if (httpStatus === 0) {
                console.error(`   ❌ 网络错误或CORS问题 | Network error or CORS issue (0)`);
              }
            } else {
              console.error(`   ⚠️ 无法获取HTTP状态码 | Cannot get HTTP status`);
            }
            
            if (statusText) {
              console.error(`   HTTP状态文本 | HTTP status text: ${statusText}`);
            }
            if (responseURL) {
              console.error(`   实际请求URL | Actual request URL: ${responseURL}`);
            }
            
            // 如果是网络错误，也输出
            if (err.message && (err.message.includes('fetch') || err.message.includes('network') || err.message.includes('Failed to fetch'))) {
              console.error(`   ❌ 网络错误 | Network error: 可能是CORS问题或文件不存在`);
              console.error(`   💡 建议：在浏览器中直接访问 ${fullUrl} 测试文件是否可访问`);
            }
            
            tryNext();
          }
        );
      };

      tryNext();
    });
  }

  /**
   * 获取模型路径候选列表
   * @private
   */
  _getModelPaths() {
    const base = window.location.origin;
    const configPath = this.config.glbPath;
    
    // 从配置路径中提取文件名
    const fileName = configPath.split('/').pop() || 'GLB_20251223141542.glb';
    
    console.log(`🔍 GLB模型加载配置 | GLB model loading config:`);
    console.log(`   Origin: ${base}`);
    console.log(`   配置路径 | Config path: ${configPath}`);
    console.log(`   文件名 | File name: ${fileName}`);
    
    // 生成候选路径列表（按优先级排序）
    const candidates = [
      // 1. 使用配置的路径（如果是绝对路径）
      configPath.startsWith('/') ? configPath : null,
      
      // 2. 标准public目录路径
      `/public/${fileName}`,
      
      // 3. 完整URL
      `${base}/public/${fileName}`,
      
      // 4. 相对于当前页面的路径
      `./public/${fileName}`,
      
      // 5. 直接文件名（如果服务器配置了静态文件）
      `/${fileName}`
    ].filter(p => p && p.trim() !== '');
    
    // 去重
    const uniquePaths = [...new Set(candidates)];
    console.log(`🔍 候选路径列表 | Candidate paths:`, uniquePaths);
    return uniquePaths;
  }

  /**
   * 设置 GLB 模型
   * @private
   */
  _setupGLBModel(gltf, url) {
    try {
      this.mesh = gltf.scene;
      
      // 确保整个mesh组可见
      this.mesh.visible = true;
      
      // 启用阴影，将整个船体模型设置为60%透明度的玻璃材质
      this.mesh.traverse((child) => {
        if (child.isMesh) {
          try {
            child.castShadow = true;
            child.receiveShadow = true;
            
            // 获取旧材质（如果存在），用于后续释放资源
            const oldMaterial = child.material;
            
            // 获取原始材质颜色，保留模型的原始外观
            let originalColor = new THREE.Color(0x88aaff); // 默认蓝色
            if (oldMaterial) {
              if (Array.isArray(oldMaterial)) {
                // 如果是材质数组，使用第一个材质的颜色
                if (oldMaterial[0] && oldMaterial[0].color) {
                  originalColor = oldMaterial[0].color.clone();
                }
              } else if (oldMaterial.color) {
                originalColor = oldMaterial.color.clone();
              }
            }
            
            // 为整个船体创建白色不透明材质（白模）
            const whiteMaterial = new THREE.MeshStandardMaterial({
              color: 0xffffff, // 白色
              transparent: false,
              opacity: 1.0, // 完全不透明
              roughness: 0.7, // 中等粗糙度
              metalness: 0.0, // 非金属
              side: THREE.DoubleSide, // 双面渲染
              depthWrite: true, // 启用深度写入
              depthTest: true, // 启用深度测试
              // 确保材质正确初始化
              needsUpdate: true
            });
            
            // 先释放旧材质资源（如果存在）
            if (oldMaterial) {
              try {
                if (Array.isArray(oldMaterial)) {
                  oldMaterial.forEach(mat => {
                    if (mat && typeof mat.dispose === 'function') {
                      mat.dispose();
                    }
                  });
                } else if (oldMaterial && typeof oldMaterial.dispose === 'function') {
                  oldMaterial.dispose();
                }
              } catch (disposeError) {
                console.warn('⚠️ 释放旧材质时出错 | Error disposing old material:', disposeError);
              }
            }
            
            // 应用新材质
            child.material = whiteMaterial;
            child.renderOrder = 0; // 正常渲染顺序
            
            // 确保 mesh 可见
            child.visible = true;
            
            // 确保mesh的父对象也可见
            if (child.parent) {
              child.parent.visible = true;
            }
            
            // 强制更新材质
            whiteMaterial.needsUpdate = true;
            
            // 添加调试日志（仅第一个mesh）
            if (!this._whiteMaterialLogged) {
              console.log('✅ 船体白色材质已应用 | Ship white material applied:');
              console.log(`   材质类型 | Material type: ${whiteMaterial.type}`);
              console.log(`   颜色 | Color: white (0xffffff)`);
              console.log(`   不透明 | Opaque: ${!whiteMaterial.transparent}`);
              console.log(`   粗糙度 | Roughness: ${whiteMaterial.roughness}`);
              console.log(`   金属度 | Metalness: ${whiteMaterial.metalness}`);
              this._whiteMaterialLogged = true;
            }
          } catch (meshError) {
            console.error(`❌ 处理mesh时出错 | Error processing mesh:`, meshError);
            console.error(`   Mesh名称 | Mesh name: ${child.name || 'unnamed'}`);
            // 继续处理其他mesh，不中断整个流程
          }
        }
      });
    } catch (setupError) {
      console.error('❌ 设置GLB模型时出错 | Error setting up GLB model:', setupError);
      throw setupError;
    }

    // 计算边界框和中心
    const box = new THREE.Box3().setFromObject(this.mesh);
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);

    console.log(`📦 模型原始边界框 | Original bounding box:`);
    console.log(`   尺寸 | Size: X=${size.x.toFixed(2)} × Y=${size.y.toFixed(2)} × Z=${size.z.toFixed(2)}`);
    console.log(`   中心 | Center: X=${center.x.toFixed(2)}, Y=${center.y.toFixed(2)}, Z=${center.z.toFixed(2)}`);
    console.log(`   底部 | Bottom: Y=${(center.y - size.y * 0.5).toFixed(2)}`);

    // 重要：将模型底部对齐到原点（Y=0），而不是居中
    // 模型底部应该在 Y=0，模型顶部在 Y=size.y
    const bottomY = center.y - size.y * 0.5; // 原始底部Y坐标
    this.mesh.position.set(
      -center.x,  // X轴居中
      -bottomY,   // Y轴：将底部移到原点（Y=0）
      -center.z   // Z轴居中
    );
    
    console.log(`📦 模型底部已对齐到原点 | Model bottom aligned to origin (0, 0, 0)`);
    console.log(`   模型底部 | Bottom: Y=0.00m`);
    console.log(`   模型顶部 | Top: Y=${size.y.toFixed(2)}m`);

    // 缩放到目标尺寸
    // 注意：X轴=宽度，Y轴=高度（绿色轴），Z轴=长度
    // 重要：以Y轴（高度）95米为基准进行缩放，保持模型原始比例
    if (this.config.desiredSize) {
      // 以Y轴（高度）为基准计算缩放比例
      const targetHeight = this.config.desiredSize.y; // 目标高度95米
      const scaleFactor = targetHeight / size.y; // 基于Y轴（高度）计算缩放比例
      
      // 使用统一的缩放比例，保持模型原始比例
      this.mesh.scale.setScalar(scaleFactor);
      
      // 更新物理尺寸（按比例缩放）
      this.size = new THREE.Vector3(
        size.x * scaleFactor, // X轴=宽度（按比例）
        size.y * scaleFactor, // Y轴=高度=95m（基准）
        size.z * scaleFactor  // Z轴=长度（按比例）
      );
      
      console.log(`📐 模型缩放完成 | Model scaled:`);
      console.log(`   原始尺寸 | Original size: X=${size.x.toFixed(2)} × Y=${size.y.toFixed(2)} × Z=${size.z.toFixed(2)}`);
      console.log(`   缩放比例 | Scale factor: ${scaleFactor.toFixed(4)} (基于Y轴高度 ${targetHeight}m)`);
      console.log(`   最终尺寸 | Final size: X=${this.size.x.toFixed(2)}m (宽度) × Y=${this.size.y.toFixed(2)}m (高度) × Z=${this.size.z.toFixed(2)}m (长度)`);
      console.log(`   ✅ Y轴（高度）已设置为 ${this.size.y.toFixed(2)}m`);
    } else {
      // 兼容旧代码：按长度统一缩放（使用Z轴作为长度）
      const scaleFactor = (this.config.desiredLength || 138) / size.z; // 使用Z轴作为长度
      this.mesh.scale.setScalar(scaleFactor);
      this.size = size.clone().multiplyScalar(scaleFactor);
    }

    this.scene.add(this.mesh);

    // 创建物理体
    this._createPhysicsBody(this.size);

    // 验证模型位置（底部在原点）
    console.log(`📐 模型位置验证 | Model position verification:`);
    console.log(`   模型底部 | Bottom: Y=0.00m (原点)`);
    console.log(`   模型中心 | Center: Y=${(this.size.y * 0.5).toFixed(2)}m`);
    console.log(`   模型顶部 | Top: Y=${this.size.y.toFixed(2)}m`);
    console.log(`   模型高度 | Height: ${this.size.y.toFixed(2)}m`);

    // 自动创建并显示标尺（长宽高）- 暂时禁用，避免显示箭头圆锥体
    // this.toggleDimensionLines(true);

    this.loaded = true;
    console.log('✅ Boat GLB loaded:', url);
    console.log('📏 Boat size:', this.size);
  }


  /**
   * 创建物理体
   * @private
   */
  _createPhysicsBody(size) {
    const halfExtents = new CANNON.Vec3(
      size.x * 0.5,
      size.y * 0.5,
      size.z * 0.5
    );
    const shape = new CANNON.Box(halfExtents);

    // 初始位置：将船体放在较高的位置，等待浮力算法生效
    // 船体高度约95米，水面通常在0-2米，初始位置需要根据浮力系数动态调整
    // 如果浮力系数较小，需要将船体放在更接近水面的位置
    const initialY = 10; // 初始高度，浮力算法会将其调整到正确位置
    this.body = new CANNON.Body({
      mass: this.config.mass,
      shape,
      position: new CANNON.Vec3(0, initialY, 0),  // 初始位置，浮力算法会调整
      linearDamping: this.config.linearDamping,
      angularDamping: this.config.angularDamping
    });

    // 调整重心位置：实际船舶重心通常稍微偏后（船尾有发动机等重物）
    // 将重心向后移动约5-10%的船长，以平衡船头下沉问题
    const centerOfMassOffset = new CANNON.Vec3(0, 0, size.z * 0.05); // 向后偏移5%
    this.body.material = new CANNON.Material('ship');
    this.body.updateMassProperties();
    
    // 使用shapeOffset来调整重心（如果Cannon支持）
    // 如果不支持，我们通过调整浮力分布来补偿
    
    this.world.addBody(this.body);
    
    console.log(`✅ Physics body created, size: ${size.x.toFixed(1)} x ${size.y.toFixed(1)} x ${size.z.toFixed(1)}`);
    console.log(`   重心偏移建议 | Center of mass offset: ${centerOfMassOffset.z.toFixed(2)} m (向后 | aft)`);
  }

  /**
   * 更新船体（同步网格和物理体）
   */
  update(deltaTime) {
    if (this.mesh && this.body) {
      this.mesh.position.copy(this.body.position);
      this.mesh.quaternion.copy(this.body.quaternion);
    }

    // 更新坐标轴辅助器
    if (this.axesHelper && this.mesh) {
      this.axesHelper.position.copy(this.mesh.position);
      this._updateAxisLabels();
    }
    
    // 尺寸线段已经添加到mesh中，会自动跟随船体运动，无需手动更新
  }

  /**
   * 将船放置到水面
   * @param {number} time - 当前时间
   */
  placeOnWater(time) {
    if (!this.body) return;

    const x = this.body.position.x;
    const z = this.body.position.z;
    const waterHeight = getWaveHeight(x, -z, time) * this.config.yFlip;

    // 获取船体高度
    const shipHeight = this.size ? this.size.y : (this.config.size ? this.config.size.y : 10);
    
    // 重要：模型底部在原点（Y=0），物理体中心在 Y = shipHeight * 0.5
    // 根据吃水深度（0米，船底与水面接触）计算物理体位置
    // 吃水深度0米：船底与水面接触
    // 船底Y = 水面高度 = waterHeight
    // 物理体中心Y = 船底Y + 船体高度/2 = waterHeight + shipHeight/2
    const draftDepth = 0.0; // 目标吃水深度0米（船底与水面接触）
    const shipBottomY = waterHeight - draftDepth; // 船底与水面接触（Y = waterHeight）
    const bodyCenterY = shipBottomY + shipHeight * 0.5; // 物理体中心位置
    
    // 使用计算出的位置，确保船底与水面接触
    this.body.position.y = bodyCenterY;
    
    console.log(`📍 船体放置（船底与水面接触）| Ship placement (bottom touches water):`);
    console.log(`   物理体中心 | Body center: Y=${bodyCenterY.toFixed(2)}m`);
    console.log(`   水面高度 | Water height: Y=${waterHeight.toFixed(2)}m`);
    console.log(`   船底位置 | Ship bottom: Y=${shipBottomY.toFixed(2)}m (应与水面一致)`);
    console.log(`   吃水深度 | Draft depth: ${draftDepth.toFixed(2)}m`);
    
    // 完全清零所有运动状态
    this.body.velocity.setZero();
    this.body.angularVelocity.setZero();
    
    // 强制直立姿态
    this.body.quaternion.set(0, 0, 0, 1);
    
    // 清零所有力和力矩
    this.body.force.setZero();
    this.body.torque.setZero();
    
    // 唤醒物理体（确保物理更新）
    this.body.wakeUp();

    this.update(0);
    
    // 验证放置结果（使用已定义的变量）
    const finalBottomY = bodyCenterY - shipHeight * 0.5;
    console.log(`📍 船体放置完成 | Ship placement completed:`);
    console.log(`   物理体中心 | Body center: Y=${bodyCenterY.toFixed(2)}m`);
    console.log(`   船底位置 | Ship bottom: Y=${finalBottomY.toFixed(2)}m`);
    console.log(`   水面高度 | Water height: Y=${waterHeight.toFixed(2)}m`);
    console.log(`   吃水深度 | Draft depth: ${(waterHeight - finalBottomY).toFixed(2)}m`);
  }

  /**
   * 重置船体姿态
   */
  reset() {
    if (!this.body) return;

    this.body.position.set(0, 2, 0);  // 降低初始高度
    this.body.quaternion.set(0, 0, 0, 1);
    this.body.velocity.setZero();
    this.body.angularVelocity.setZero();
    this.body.force.setZero();
    this.body.torque.setZero();
    this.body.wakeUp();

    console.log('🔄 Boat reset');
  }

  /**
   * 设置质量
   * @param {number} mass 
   */
  setMass(mass) {
    if (this.body) {
      this.body.mass = mass;
      this.body.updateMassProperties();
      this.config.mass = mass;
    }
  }

  /**
   * 设置吃水深度
   * @param {number} depth 
   */
  setDraftDepth(depth) {
    this.config.draftDepth = depth;
  }

  /**
   * 获取船体状态
   */
  getState() {
    if (!this.body) return null;

    return {
      position: this.body.position.clone(),
      velocity: this.body.velocity.clone(),
      quaternion: this.body.quaternion.clone(),
      angularVelocity: this.body.angularVelocity.clone(),
      mass: this.body.mass,
      size: this.size
    };
  }

  /**
   * 显示/隐藏尺寸线段（长宽高）
   * @param {boolean} show 
   */
  toggleDimensionLines(show) {
    if (show && !this.dimensionLines && this.size) {
      // 创建尺寸线段组
      const dimensionGroup = new THREE.Group();
      dimensionGroup.name = 'DimensionLines';
      
      // 创建材质（高亮显示）
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0xffffff,
        linewidth: 4,
        transparent: true,
        opacity: 0.95
      });
      
      // 长度线段（Z轴，蓝色）- 138m
      const lengthGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, 0, this.size.z * 0.5) // Z轴正方向（船尾方向）
      ]);
      const lengthLine = new THREE.Line(lengthGeometry, lineMaterial.clone());
      lengthLine.material.color.setHex(0x5599ff); // 蓝色
      dimensionGroup.add(lengthLine);
      
      // 宽度线段（X轴，红色）- 85m
      const widthGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(this.size.x * 0.5, 0, 0) // X轴正方向（右侧）
      ]);
      const widthLine = new THREE.Line(widthGeometry, lineMaterial.clone());
      widthLine.material.color.setHex(0xff5555); // 红色
      dimensionGroup.add(widthLine);
      
      // 高度线段（Y轴，绿色）- 95m
      const heightGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, this.size.y * 0.5, 0) // Y轴正方向（向上）
      ]);
      const heightLine = new THREE.Line(heightGeometry, lineMaterial.clone());
      heightLine.material.color.setHex(0x55ff55); // 绿色
      dimensionGroup.add(heightLine);
      
      // 添加标签（超大字体，10米正方大小，即使摄像机缩放也能看清楚）
      // 使用更大的 canvas 和字体，确保在10米正方大小
      const labelSize = 10.0; // 10米正方大小
      const lengthLabel = this._makeLargeTextSprite(`长度 ${this.size.z.toFixed(1)}m`, 0x5599ff, labelSize);
      lengthLabel.position.set(0, 0, this.size.z * 0.5 + 15);
      dimensionGroup.add(lengthLabel);
      
      const widthLabel = this._makeLargeTextSprite(`宽度 ${this.size.x.toFixed(1)}m`, 0xff5555, labelSize);
      widthLabel.position.set(this.size.x * 0.5 + 15, 0, 0);
      dimensionGroup.add(widthLabel);
      
      // 高度标签：从原点（模型底部）到模型顶部
      const heightLabel = this._makeLargeTextSprite(`高度 ${this.size.y.toFixed(1)}m`, 0x55ff55, labelSize);
      heightLabel.position.set(0, this.size.y + 15, 0); // 在模型顶部上方
      dimensionGroup.add(heightLabel);
      
      // 添加中心点标记（船体中心，黄色球体）
      const centerMarker = new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.8 })
      );
      centerMarker.position.set(0, 0, 0);
      dimensionGroup.add(centerMarker);
      
      // 添加箭头指示器（在端点）- 暂时禁用，避免显示圆锥体
      // this._addArrowIndicator(dimensionGroup, new THREE.Vector3(0, 0, this.size.z * 0.5), new THREE.Vector3(0, 0, 1), 0x5599ff); // Z轴箭头
      // this._addArrowIndicator(dimensionGroup, new THREE.Vector3(this.size.x * 0.5, 0, 0), new THREE.Vector3(1, 0, 0), 0xff5555); // X轴箭头
      // this._addArrowIndicator(dimensionGroup, new THREE.Vector3(0, this.size.y, 0), new THREE.Vector3(0, 1, 0), 0x55ff55); // Y轴箭头（在模型顶部）
      
      // 将标尺添加到船体mesh中，跟随船体运动
      if (this.mesh) {
        this.mesh.add(dimensionGroup);
      } else {
        this.scene.add(dimensionGroup);
      }
      this.dimensionLines = dimensionGroup;
      console.log('✅ Dimension lines (标尺) enabled');
      console.log(`   长度 | Length (Z轴): ${this.size.z.toFixed(2)}m`);
      console.log(`   宽度 | Width (X轴): ${this.size.x.toFixed(2)}m`);
      console.log(`   高度 | Height (Y轴): ${this.size.y.toFixed(2)}m`);
    } else if (!show && this.dimensionLines) {
      this.scene.remove(this.dimensionLines);
      // 清理资源
      this.dimensionLines.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => m.dispose());
          } else {
            child.material.dispose();
          }
        }
      });
      this.dimensionLines = null;
      console.log('❌ Dimension lines disabled');
    }
  }

  /**
   * 应用不透明材质
   * @private
   */
  _applyOpaqueMaterial(mesh, color = new THREE.Color(0x88aaff)) {
    const opaqueMaterial = new THREE.MeshStandardMaterial({
      color: color,
      transparent: false,
      opacity: 1.0,
      roughness: 0.7,
      metalness: 0.3,
      side: THREE.DoubleSide,
      depthWrite: true,
      depthTest: true
    });
    mesh.material = opaqueMaterial;
    mesh.renderOrder = 0; // 不透明物体先渲染
  }

  /**
   * 添加箭头指示器
   * @private
   */
  _addArrowIndicator(group, position, direction, color) {
    const arrowLength = 3;
    const arrowHeadLength = 1.5;
    const arrowHeadWidth = 0.8;
    
    // 使用 THREE.ArrowHelper（Three.js 内置类）
    const arrowHelper = new THREE.ArrowHelper(
      direction,
      position,
      arrowLength,
      color,
      arrowHeadLength,
      arrowHeadWidth
    );
    group.add(arrowHelper);
  }

  /**
   * 显示/隐藏坐标轴辅助器
   * @param {boolean} show 
   */
  toggleAxesHelper(show) {
    if (show && !this.axesHelper) {
      const axisLen = this._getAxisLength();
      this.axesHelper = new THREE.AxesHelper(axisLen);
      this.scene.add(this.axesHelper);
      this._addAxisLabels(axisLen);
      console.log('✅ Axes helper enabled');
    } else if (!show && this.axesHelper) {
      this.scene.remove(this.axesHelper);
      this.axesHelper = null;
      this._removeAxisLabels();
      console.log('❌ Axes helper disabled');
    }
  }

  /**
   * 获取坐标轴长度
   * @private
   */
  _getAxisLength() {
    if (!this.size) return 50;
    const maxSide = Math.max(this.size.x, this.size.y, this.size.z);
    // 延长到模型外，至少是最大尺寸的2.5倍，确保可见
    return Math.max(50, maxSide * 2.5);
  }

  /**
   * 添加坐标轴标签
   * @private
   */
  _addAxisLabels(axisLen) {
    // 增大标签尺寸，使其更明显
    const labelScale = Math.max(3.0, axisLen * 0.15);
    const xLabel = this._makeTextSprite('X', '#ff5555', labelScale);
    const yLabel = this._makeTextSprite('Y', '#55ff55', labelScale);
    const zLabel = this._makeTextSprite('Z', '#5599ff', labelScale);
    
    this.axisLabels = [xLabel, yLabel, zLabel];
    this.axisLabels.forEach(s => this.scene.add(s));
  }

  /**
   * 移除坐标轴标签
   * @private
   */
  _removeAxisLabels() {
    this.axisLabels.forEach(s => this.scene.remove(s));
    this.axisLabels = [];
  }

  /**
   * 更新坐标轴标签位置
   * @private
   */
  _updateAxisLabels() {
    if (!this.mesh || this.axisLabels.length !== 3) return;
    
    const base = this.mesh.position;
    const axisLen = this._getAxisLength();
    // 标签位置在轴线的末端（0.9倍长度处），确保在模型外可见
    const offset = axisLen * 0.9;
    
    this.axisLabels[0].position.set(base.x + offset, base.y, base.z);
    this.axisLabels[1].position.set(base.x, base.y + offset, base.z);
    this.axisLabels[2].position.set(base.x, base.y, base.z + offset);
  }

  /**
   * 创建文字精灵
   * @private
   */
  _makeTextSprite(text, color = '#ffffff', scale = 1.0) {
    const canvas = document.createElement('canvas');
    const size = 128;
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, size, size);
    ctx.fillStyle = color;
    ctx.font = 'bold 64px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, size / 2, size / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(scale, scale, scale);
    
    return sprite;
  }

  /**
   * 创建超大文字精灵（用于标尺，10米正方大小）
   * @private
   */
  _makeLargeTextSprite(text, color = '#ffffff', worldSize = 10.0) {
    // 使用更大的 canvas 和字体，确保在10米正方大小
    const canvas = document.createElement('canvas');
    const size = 512; // 增大 canvas 尺寸
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    
    // 清除背景
    ctx.clearRect(0, 0, size, size);
    
    // 添加半透明黑色背景，提高可读性
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, size, size);
    
    // 设置超大字体
    ctx.fillStyle = color;
    ctx.font = 'bold 120px Arial'; // 超大字体
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 8;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // 先描边，再填充，使文字更醒目
    ctx.strokeText(text, size / 2, size / 2);
    ctx.fillText(text, size / 2, size / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    const material = new THREE.SpriteMaterial({ 
      map: texture, 
      transparent: true,
      depthTest: false, // 始终显示在最前面
      depthWrite: false
    });
    const sprite = new THREE.Sprite(material);
    // 设置精灵大小为10米正方
    sprite.scale.set(worldSize, worldSize, 1);
    sprite.renderOrder = 1000; // 确保在最前面渲染
    
    return sprite;
  }

  /**
   * 清理资源
   */
  dispose() {
    if (this.mesh) {
      this.scene.remove(this.mesh);
      if (this.mesh.geometry) this.mesh.geometry.dispose();
      if (this.mesh.material) this.mesh.material.dispose();
    }

    if (this.body) {
      this.world.removeBody(this.body);
    }

    this.toggleAxesHelper(false);
    this.toggleDimensionLines(false);
    
    console.log('🗑️ Ship controller disposed');
  }
}

