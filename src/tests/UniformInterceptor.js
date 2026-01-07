/**
 * Uniform Interceptor - Proactive Prevention System
 * 
 * This module intercepts and validates all uniform access BEFORE Three.js reads them.
 * Instead of reactively fixing errors, it proactively prevents them from occurring.
 * 
 * 主动拦截和验证所有 uniform 访问，在 Three.js 读取之前进行处理
 * 不是被动修复错误，而是主动防止错误发生
 */

import * as THREE from '../../public/lib/three.module.js';

export class UniformInterceptor {
  constructor() {
    this.interceptedMaterials = new WeakSet();
    this.validationStats = {
      materialsIntercepted: 0,
      uniformsFixed: 0,
      uniformsValidated: 0
    };
  }

  /**
   * Intercept and wrap all uniforms in a material
   * 拦截并包装材质中的所有 uniforms
   */
  interceptMaterial(material) {
    if (!material || this.interceptedMaterials.has(material)) {
      return; // Already intercepted
    }

    // Only intercept materials with uniforms
    if (!material.uniforms || typeof material.uniforms !== 'object') {
      return;
    }

    // Wrap the uniforms object with a Proxy that validates ALL access
    const originalUniforms = material.uniforms;
    const self = this;

    material.uniforms = new Proxy(originalUniforms, {
      get(target, uniformName) {
        // If asking for a uniform, ensure it's valid before returning
        if (uniformName in target) {
          const uniform = target[uniformName];
          
          // Validate the uniform structure
          if (uniform === null || uniform === undefined) {
            console.warn(`🔧 Interceptor: Fixing null/undefined uniform '${uniformName}'`);
            target[uniformName] = { value: 0.0 };
            self.validationStats.uniformsFixed++;
            return target[uniformName];
          }

          if (typeof uniform !== 'object' || Array.isArray(uniform)) {
            console.warn(`🔧 Interceptor: Fixing non-object uniform '${uniformName}' (type: ${typeof uniform})`);
            target[uniformName] = { value: uniform };
            self.validationStats.uniformsFixed++;
            return target[uniformName];
          }

          if (!('value' in uniform)) {
            console.warn(`🔧 Interceptor: Adding missing 'value' property to uniform '${uniformName}'`);
            uniform.value = 0.0;
            self.validationStats.uniformsFixed++;
          }

          if (uniform.value === undefined) {
            console.warn(`🔧 Interceptor: Fixing undefined value in uniform '${uniformName}'`);
            uniform.value = 0.0;
            self.validationStats.uniformsFixed++;
          }

          self.validationStats.uniformsValidated++;
          return uniform;
        }

        // Return undefined for non-existent uniforms (normal behavior)
        return undefined;
      },

      set(target, uniformName, value) {
        // When setting a uniform, ensure it's in the correct format
        if (value === null || value === undefined) {
          console.warn(`🔧 Interceptor: Prevented setting null/undefined uniform '${uniformName}'`);
          target[uniformName] = { value: 0.0 };
          self.validationStats.uniformsFixed++;
          return true;
        }

        if (typeof value === 'object' && 'value' in value) {
          // Already in correct format
          target[uniformName] = value;
        } else {
          // Wrap in correct format
          target[uniformName] = { value: value };
          self.validationStats.uniformsFixed++;
        }

        return true;
      },

      has(target, uniformName) {
        return uniformName in target;
      },

      ownKeys(target) {
        return Reflect.ownKeys(target);
      },

      getOwnPropertyDescriptor(target, uniformName) {
        return Reflect.getOwnPropertyDescriptor(target, uniformName);
      }
    });

    this.interceptedMaterials.add(material);
    this.validationStats.materialsIntercepted++;
  }

  /**
   * Intercept all materials in a scene
   * 拦截场景中的所有材质
   */
  interceptScene(scene) {
    console.log('🛡️ Uniform Interceptor: Scanning scene...');
    
    let materialCount = 0;
    const materialSet = new Set();

    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) 
          ? object.material 
          : [object.material];

        materials.forEach((material) => {
          if (material && !materialSet.has(material)) {
            materialSet.add(material);
            this.interceptMaterial(material);
            materialCount++;
          }
        });
      }
    });

    console.log(`✅ Uniform Interceptor: Protected ${materialCount} unique materials`);
    this.printStats();
  }

  /**
   * Deep validation and fix of all uniforms in a material
   * 深度验证并修复材质中的所有 uniforms
   */
  deepValidateMaterial(material) {
    if (!material || !material.uniforms) return 0;

    let fixCount = 0;
    const uniforms = material.uniforms;

    for (const uniformName in uniforms) {
      if (uniforms.hasOwnProperty(uniformName)) {
        let uniform = uniforms[uniformName];

        // Fix 1: Null or undefined uniform
        if (uniform === null || uniform === undefined) {
          uniforms[uniformName] = { value: 0.0 };
          fixCount++;
          continue;
        }

        // Fix 2: Non-object uniform (primitive value instead of {value: ...})
        if (typeof uniform !== 'object' || Array.isArray(uniform)) {
          uniforms[uniformName] = { value: uniform };
          fixCount++;
          uniform = uniforms[uniformName];
        }

        // Fix 3: Missing 'value' property
        if (!('value' in uniform)) {
          uniform.value = this.getDefaultValueForUniform(uniformName);
          fixCount++;
        }

        // Fix 4: Undefined or null value
        if (uniform.value === undefined) {
          uniform.value = this.getDefaultValueForUniform(uniformName);
          fixCount++;
        }
      }
    }

    if (fixCount > 0) {
      material.needsUpdate = true;
      this.validationStats.uniformsFixed += fixCount;
    }

    return fixCount;
  }

  /**
   * Get a sensible default value based on uniform name
   * 根据 uniform 名称推断合理的默认值
   */
  getDefaultValueForUniform(uniformName) {
    const nameLower = uniformName.toLowerCase();

    if (nameLower.includes('time')) {
      return 0.0;
    }
    if (nameLower.includes('color') || nameLower.includes('colour')) {
      return new THREE.Color(0xffffff);
    }
    if (nameLower.includes('direction') || nameLower.includes('dir')) {
      return new THREE.Vector3(0, 1, 0);
    }
    if (nameLower.includes('position') || nameLower.includes('pos')) {
      return new THREE.Vector3(0, 0, 0);
    }
    if (nameLower.includes('scale') || nameLower.includes('size')) {
      return 1.0;
    }
    if (nameLower.includes('texture') || nameLower.includes('map') || nameLower.includes('sampler')) {
      // For textures, null is acceptable (Three.js handles it)
      return null;
    }

    // Default: scalar 0
    return 0.0;
  }

  /**
   * Run full validation on all materials in the scene
   * 对场景中所有材质运行完整验证
   */
  validateAndFixScene(scene) {
    console.log('🔍 Uniform Interceptor: Running deep validation...');
    
    let totalFixes = 0;
    const materialSet = new Set();

    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) 
          ? object.material 
          : [object.material];

        materials.forEach((material) => {
          if (material && !materialSet.has(material)) {
            materialSet.add(material);
            const fixes = this.deepValidateMaterial(material);
            totalFixes += fixes;

            if (fixes > 0) {
              console.log(`  🔧 Fixed ${fixes} uniforms in ${material.type} (${material.name || 'unnamed'})`);
            }
          }
        });
      }
    });

    console.log(`✅ Deep validation complete: ${totalFixes} uniforms fixed`);
    return totalFixes;
  }

  /**
   * Print validation statistics
   * 打印验证统计信息
   */
  printStats() {
    console.log('📊 Uniform Interceptor Stats:');
    console.log(`   Materials intercepted: ${this.validationStats.materialsIntercepted}`);
    console.log(`   Uniforms validated: ${this.validationStats.uniformsValidated}`);
    console.log(`   Uniforms fixed: ${this.validationStats.uniformsFixed}`);
  }

  /**
   * Reset statistics
   * 重置统计信息
   */
  resetStats() {
    this.validationStats = {
      materialsIntercepted: 0,
      uniformsFixed: 0,
      uniformsValidated: 0
    };
  }
}

// Export singleton instance
export const uniformInterceptor = new UniformInterceptor();

