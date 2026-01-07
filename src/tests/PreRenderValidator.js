/**
 * Pre-Render Validator - 预渲染验证器
 * 
 * 在每次渲染前主动扫描并修复所有材质的 uniform 问题
 * This validator actively scans and fixes all material uniform issues BEFORE each render call
 * 
 * 这是一个高性能的运行时验证器，专门设计用于捕获和修复 Three.js 渲染前的 uniform 错误
 * This is a high-performance runtime validator specifically designed to catch and fix uniform errors before Three.js renders
 */

import * as THREE from '../../public/lib/three.module.js';

export class PreRenderValidator {
  constructor() {
    this.validatedMaterials = new WeakMap(); // 缓存已验证的材质，避免重复验证
    this.frameCount = 0;
    this.revalidateInterval = 60; // 每60帧重新验证一次所有材质
    this.stats = {
      materialsValidated: 0,
      uniformsFixed: 0,
      lastFixTimestamp: 0
    };
  }

  /**
   * 在渲染前验证场景
   * Validate scene before rendering
   * 
   * @param {THREE.Scene} scene - Three.js场景
   * @param {boolean} force - 是否强制重新验证所有材质
   * @returns {number} 修复的uniform数量
   */
  validateBeforeRender(scene, force = false) {
    this.frameCount++;
    
    // 每次都验证所有材质（确保捕获动态修改）
    // Always validate all materials (to catch dynamic changes)
    let fixCount = 0;
    const materialSet = new Set();
    
    // 第一步：先应用 Proxy 保护（必须在验证前）
    this._applyProxyProtection(scene);
    
    // 第二步：验证和修复材质
    scene.traverse((object) => {
      if (!object.material) return;
      
      const materials = Array.isArray(object.material) 
        ? object.material 
        : [object.material];
      
      materials.forEach((material) => {
        if (material && !materialSet.has(material)) {
          materialSet.add(material);
          
          // 每次都验证（不缓存，确保捕获所有问题）
          const fixes = this.validateMaterial(material, object);
          fixCount += fixes;
          
          if (fixes > 0) {
            this.stats.uniformsFixed += fixes;
            this.stats.lastFixTimestamp = Date.now();
            
            // 标记材质需要更新
            material.needsUpdate = true;
          }
          
          // 更新统计（但不在每次验证时重复计数）
          if (!this.validatedMaterials.has(material)) {
            this.validatedMaterials.set(material, true);
            this.stats.materialsValidated++;
          }
        }
      });
    });
    
    return fixCount;
  }

  /**
   * 应用 Proxy 保护到所有 ShaderMaterial
   * Apply Proxy protection to all ShaderMaterials
   * @private
   */
  _applyProxyProtection(scene) {
    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.forEach((material) => {
          if (material && (material.type === 'ShaderMaterial' || material.type === 'RawShaderMaterial')) {
            if (material.uniforms && typeof material.uniforms === 'object' && !material.uniforms._proxied) {
              // 标记已代理，避免重复代理
              const originalUniforms = material.uniforms;
              const self = this;
              
              material.uniforms = new Proxy(originalUniforms, {
                get(target, prop) {
                  // 如果是特殊属性，直接返回
                  if (prop === '_proxied' || prop === 'constructor' || typeof prop === 'symbol') {
                    return Reflect.get(target, prop);
                  }
                  
                  // 处理 Object 的方法
                  if (prop === 'hasOwnProperty' || prop === 'toString' || prop === 'valueOf') {
                    return Reflect.get(target, prop).bind(target);
                  }
                  
                  // 如果访问的 uniform 存在
                  if (prop in target) {
                    let uniform = target[prop];
                    
                    // 如果 uniform 无效，立即修复
                    if (uniform === undefined || uniform === null) {
                      const defaultValue = self.getDefaultValue(prop);
                      uniform = { value: defaultValue };
                      target[prop] = uniform;
                      material.needsUpdate = true;
                      return uniform;
                    }
                    
                    // 如果 uniform 不是对象，包装它
                    if (typeof uniform !== 'object' || Array.isArray(uniform)) {
                      uniform = { value: uniform };
                      target[prop] = uniform;
                      material.needsUpdate = true;
                      return uniform;
                    }
                    
                    // 如果 uniform 没有 value 属性，添加它
                    if (!('value' in uniform)) {
                      uniform.value = self.getDefaultValue(prop);
                      material.needsUpdate = true;
                    }
                    
                    // 如果 value 是 undefined，修复它
                    if (uniform.value === undefined) {
                      uniform.value = self.getDefaultValue(prop);
                      material.needsUpdate = true;
                    }
                    
                    // 额外保护：确保返回的 uniform 对象本身是有效的
                    // 如果 uniform 对象被修改为无效，再次修复
                    if (typeof uniform !== 'object' || Array.isArray(uniform)) {
                      uniform = { value: uniform };
                      target[prop] = uniform;
                      material.needsUpdate = true;
                    }
                    
                    return uniform;
                  }
                  
                  // 如果访问的 uniform 不存在，返回一个默认值（避免 Three.js 报错）
                  // 注意：这可能会隐藏一些真正的错误，但可以防止崩溃
                  const defaultValue = self.getDefaultValue(prop);
                  const defaultUniform = { value: defaultValue };
                  // 不直接设置到 target，避免污染原始对象
                  return defaultUniform;
                },
                
                set(target, prop, value) {
                  // 确保设置的值是有效的 uniform 格式
                  if (value === null || value === undefined) {
                    target[prop] = { value: self.getDefaultValue(prop) };
                  } else if (typeof value === 'object' && 'value' in value) {
                    target[prop] = value;
                  } else {
                    target[prop] = { value: value };
                  }
                  material.needsUpdate = true;
                  return true;
                },
                
                has(target, prop) {
                  return prop in target;
                },
                
                ownKeys(target) {
                  return Reflect.ownKeys(target);
                },
                
                getOwnPropertyDescriptor(target, prop) {
                  return Reflect.getOwnPropertyDescriptor(target, prop);
                }
              });
              
              material.uniforms._proxied = true;
            }
          }
        });
      }
    });
  }

  /**
   * 验证单个材质
   * Validate a single material
   * 
   * @param {THREE.Material} material - Three.js材质
   * @param {THREE.Object3D} object - 使用该材质的对象（用于日志）
   * @returns {number} 修复的uniform数量
   */
  validateMaterial(material, object) {
    if (!material) return 0;
    
    let fixCount = 0;
    
    // 处理所有可能有 uniforms 的材质类型
    const materialType = material.type || material.constructor.name;
    
    // 注意：MeshPhysicalMaterial 等也可能有内部 uniforms，但通常由 Three.js 管理
    // 我们主要关注自定义的 ShaderMaterial
    if (materialType !== 'ShaderMaterial' && materialType !== 'RawShaderMaterial') {
      // 但也要检查是否有自定义的 uniforms 属性（可能是错误的）
      if (material.uniforms && typeof material.uniforms === 'object') {
        // 如果非 ShaderMaterial 有 uniforms，这可能是问题
        console.warn(`⚠️ 非 ShaderMaterial 材质有 uniforms 属性: ${materialType} (${object.name || object.uuid})`);
        // 移除它，避免 Three.js 混淆
        delete material.uniforms;
        fixCount++;
      }
      return fixCount;
    }
    
    // 检查 uniforms 是否存在
    if (!material.uniforms) {
      console.warn(`🔧 PreRenderValidator: Material ${materialType} has no uniforms, creating empty object`);
      material.uniforms = {};
      fixCount++;
      return fixCount;
    }
    
    // 验证 uniforms 是对象
    if (typeof material.uniforms !== 'object' || Array.isArray(material.uniforms)) {
      console.warn(`🔧 PreRenderValidator: Material uniforms is not an object, resetting`);
      material.uniforms = {};
      fixCount++;
      return fixCount;
    }
    
    // 深度验证每个 uniform
    const uniformNames = Object.keys(material.uniforms);
    for (const uniformName of uniformNames) {
      const uniform = material.uniforms[uniformName];
      const fixResult = this.validateUniform(uniformName, uniform, material, object);
      
      if (fixResult.fixed) {
        fixCount++;
        material.uniforms[uniformName] = fixResult.newUniform;
        // 详细日志（仅在首次修复时）
        if (!window._uniformFixDetails) window._uniformFixDetails = new Set();
        const detailKey = `${materialType}:${uniformName}`;
        if (!window._uniformFixDetails.has(detailKey)) {
          console.log(`  🔧 修复 uniform: ${uniformName} in ${materialType} (${object.name || object.uuid})`);
          window._uniformFixDetails.add(detailKey);
        }
      }
    }
    
    // 额外检查：确保 uniforms 对象本身是有效的
    // 有时 uniforms 可能被设置为 undefined 或 null
    if (!material.uniforms || typeof material.uniforms !== 'object') {
      console.warn(`⚠️ Material uniforms 无效，重置为空对象: ${materialType} (${object.name || object.uuid})`);
      material.uniforms = {};
      fixCount++;
    }
    
    return fixCount;
  }

  /**
   * 验证单个 uniform
   * Validate a single uniform
   * 
   * @param {string} uniformName - uniform名称
   * @param {*} uniform - uniform对象
   * @param {THREE.Material} material - 所属材质
   * @param {THREE.Object3D} object - 所属对象
   * @returns {{fixed: boolean, newUniform: *}} 修复结果
   */
  validateUniform(uniformName, uniform, material, object) {
    const result = {
      fixed: false,
      newUniform: uniform
    };
    
    // 检查1: uniform 是否为 null 或 undefined
    if (uniform === null || uniform === undefined) {
      console.warn(
        `🔧 PreRenderValidator: Fixed ${uniform === null ? 'null' : 'undefined'} uniform '${uniformName}'`,
        `in ${material.type} (${object.name || object.uuid})`
      );
      result.fixed = true;
      result.newUniform = { value: this.getDefaultValue(uniformName) };
      return result;
    }
    
    // 检查2: uniform 必须是对象（不能是原始类型或数组）
    if (typeof uniform !== 'object') {
      console.warn(
        `🔧 PreRenderValidator: Wrapped primitive uniform '${uniformName}' (type: ${typeof uniform})`,
        `in ${material.type} (${object.name || object.uuid})`
      );
      result.fixed = true;
      result.newUniform = { value: uniform };
      return result;
    }
    
    // 检查3: uniform 不能是数组（Three.js 期望 {value: array}）
    if (Array.isArray(uniform)) {
      console.warn(
        `🔧 PreRenderValidator: Wrapped array uniform '${uniformName}'`,
        `in ${material.type} (${object.name || object.uuid})`
      );
      result.fixed = true;
      result.newUniform = { value: uniform };
      return result;
    }
    
    // 检查4: uniform 必须有 'value' 属性
    if (!('value' in uniform)) {
      console.warn(
        `🔧 PreRenderValidator: Added missing 'value' property to uniform '${uniformName}'`,
        `in ${material.type} (${object.name || object.uuid})`
      );
      result.fixed = true;
      uniform.value = this.getDefaultValue(uniformName);
      result.newUniform = uniform;
      return result;
    }
    
    // 检查5: uniform.value 不能是 undefined（null 对纹理是合法的）
    if (uniform.value === undefined) {
      console.warn(
        `🔧 PreRenderValidator: Fixed undefined value in uniform '${uniformName}'`,
        `in ${material.type} (${object.name || object.uuid})`
      );
      result.fixed = true;
      uniform.value = this.getDefaultValue(uniformName);
      result.newUniform = uniform;
      return result;
    }
    
    // 通过所有检查
    return result;
  }

  /**
   * 根据 uniform 名称推断默认值
   * Infer default value based on uniform name
   * 
   * @param {string} uniformName - uniform名称
   * @returns {*} 默认值
   */
  getDefaultValue(uniformName) {
    const nameLower = uniformName.toLowerCase();
    
    // 时间相关
    if (nameLower.includes('time') || nameLower === 'time' || nameLower.startsWith('u_time') || nameLower.startsWith('utime')) {
      return 0.0;
    }
    
    // 颜色相关
    if (nameLower.includes('color') || nameLower.includes('colour')) {
      return new THREE.Color(0xffffff);
    }
    
    // 方向向量
    if (nameLower.includes('direction') || nameLower.includes('dir') || nameLower.endsWith('dir')) {
      return new THREE.Vector3(0, 1, 0);
    }
    
    // 位置向量
    if (nameLower.includes('position') || nameLower.includes('pos')) {
      return new THREE.Vector3(0, 0, 0);
    }
    
    // 缩放/大小
    if (nameLower.includes('scale') || nameLower.includes('size')) {
      return 1.0;
    }
    
    // 透明度/不透明度
    if (nameLower.includes('opacity') || nameLower.includes('alpha')) {
      return 1.0;
    }
    
    // 纹理/采样器
    if (nameLower.includes('texture') || nameLower.includes('map') || 
        nameLower.includes('sampler') || nameLower.startsWith('u_texture')) {
      // 纹理使用 null 是合法的（Three.js 会处理）
      return null;
    }
    
    // 矩阵
    if (nameLower.includes('matrix')) {
      if (nameLower.includes('4')) return new THREE.Matrix4();
      if (nameLower.includes('3')) return new THREE.Matrix3();
      return new THREE.Matrix4();
    }
    
    // 2D 向量
    if (nameLower.includes('vec2') || nameLower.includes('uv') || nameLower.includes('resolution')) {
      return new THREE.Vector2(0, 0);
    }
    
    // 3D 向量
    if (nameLower.includes('vec3') || nameLower.includes('vec')) {
      return new THREE.Vector3(0, 0, 0);
    }
    
    // 4D 向量
    if (nameLower.includes('vec4') || nameLower.includes('quaternion')) {
      return new THREE.Vector4(0, 0, 0, 1);
    }
    
    // 默认: 标量 0.0
    return 0.0;
  }

  /**
   * 获取验证统计信息
   * Get validation statistics
   */
  getStats() {
    return {
      ...this.stats,
      frameCount: this.frameCount,
      cacheSize: 'N/A (WeakMap)' // WeakMap 不提供 size
    };
  }

  /**
   * 重置统计信息
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      materialsValidated: 0,
      uniformsFixed: 0,
      lastFixTimestamp: 0
    };
    this.frameCount = 0;
  }

  /**
   * 打印统计信息
   * Print statistics
   */
  printStats() {
    const stats = this.getStats();
    console.log('📊 PreRenderValidator Statistics:');
    console.log(`   Frames: ${stats.frameCount}`);
    console.log(`   Materials Validated: ${stats.materialsValidated}`);
    console.log(`   Uniforms Fixed: ${stats.uniformsFixed}`);
    if (stats.lastFixTimestamp > 0) {
      const lastFixTime = new Date(stats.lastFixTimestamp).toLocaleTimeString();
      console.log(`   Last Fix: ${lastFixTime}`);
    }
  }

  /**
   * 设置重新验证间隔
   * Set revalidation interval
   * 
   * @param {number} frames - 每N帧重新验证一次
   */
  setRevalidateInterval(frames) {
    this.revalidateInterval = Math.max(1, frames);
  }
}

// 导出单例实例
export const preRenderValidator = new PreRenderValidator();

