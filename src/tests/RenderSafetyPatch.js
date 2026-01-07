/**
 * Render Safety Patch - Surgical Intervention at Three.js Core Level
 * 渲染安全补丁 - 在 Three.js 核心层级进行外科手术式干预
 * 
 * This module patches Three.js's WebGLRenderer at the lowest level possible
 * to intercept and fix uniform errors BEFORE they reach the GPU.
 * 
 * 在最底层修补 Three.js 的 WebGLRenderer，在错误到达 GPU 之前拦截并修复 uniform 错误
 */

import * as THREE from '../../public/lib/three.module.js';

export class RenderSafetyPatch {
  constructor() {
    this.patchApplied = false;
    this.errorsCaught = 0;
    this.fixesApplied = 0;
    this.debugMode = true;
  }

  /**
   * Apply surgical patches to Three.js renderer
   * 对 Three.js 渲染器应用外科手术式补丁
   */
  applyPatch(renderer) {
    if (this.patchApplied) {
      console.log('⚠️ Render safety patch already applied');
      return;
    }

    console.log('🔧 Applying render safety patch to Three.js WebGLRenderer...');

    // Patch 1: Wrap the render method to catch errors
    const originalRender = renderer.render.bind(renderer);
    renderer.render = (scene, camera) => {
      try {
        // Pre-render validation: scan scene for problematic materials
        this.validateSceneMaterials(scene);
        
        // Call original render
        originalRender(scene, camera);
      } catch (error) {
        this.handleRenderError(error, scene, camera);
        
        // Try rendering again after fix
        try {
          originalRender(scene, camera);
        } catch (secondError) {
          console.error('❌ Second render attempt failed:', secondError);
          // Prevent infinite error loop
          if (this.debugMode) {
            throw secondError;
          }
        }
      }
    };

    // Patch 2: Monkey-patch WebGLUniforms to add safety checks
    this.patchWebGLUniforms();

    this.patchApplied = true;
    console.log('✅ Render safety patch applied successfully');
  }

  /**
   * Validate all materials in the scene before rendering
   * 在渲染前验证场景中的所有材质
   */
  validateSceneMaterials(scene) {
    scene.traverse((object) => {
      if (!object.material) return;

      const materials = Array.isArray(object.material) 
        ? object.material 
        : [object.material];

      materials.forEach((material) => {
        if (!material) return;

        // Fix ShaderMaterial uniforms
        if (material.type === 'ShaderMaterial' && material.uniforms) {
          this.validateShaderMaterialUniforms(material, object);
        }

        // Fix MeshPhysicalMaterial issues
        if (material.type === 'MeshPhysicalMaterial') {
          this.fixPhysicalMaterial(material, object);
        }
      });
    });
  }

  /**
   * Validate and fix ShaderMaterial uniforms
   * 验证并修复 ShaderMaterial 的 uniforms
   */
  validateShaderMaterialUniforms(material, object) {
    if (!material.uniforms) {
      material.uniforms = {};
      return;
    }

    for (const uniformName in material.uniforms) {
      const uniform = material.uniforms[uniformName];

      // Critical fix: ensure uniform is an object with a value property
      if (uniform === null || uniform === undefined) {
        if (this.debugMode) {
          console.warn(`🔧 RenderSafetyPatch: Fixed null/undefined uniform '${uniformName}' in ${object.name || 'unnamed object'}`);
        }
        material.uniforms[uniformName] = { value: this.getDefaultValue(uniformName) };
        this.fixesApplied++;
        continue;
      }

      // If uniform is not an object (e.g., a primitive value)
      if (typeof uniform !== 'object' || Array.isArray(uniform)) {
        if (this.debugMode) {
          console.warn(`🔧 RenderSafetyPatch: Wrapped primitive uniform '${uniformName}' = ${uniform}`);
        }
        material.uniforms[uniformName] = { value: uniform };
        this.fixesApplied++;
        continue;
      }

      // If uniform object doesn't have a 'value' property
      if (!('value' in uniform)) {
        if (this.debugMode) {
          console.warn(`🔧 RenderSafetyPatch: Added missing 'value' to uniform '${uniformName}'`);
        }
        uniform.value = this.getDefaultValue(uniformName);
        this.fixesApplied++;
        continue;
      }

      // If uniform.value is undefined (not null, which can be valid for textures)
      if (uniform.value === undefined) {
        if (this.debugMode) {
          console.warn(`🔧 RenderSafetyPatch: Fixed undefined value in uniform '${uniformName}'`);
        }
        uniform.value = this.getDefaultValue(uniformName);
        this.fixesApplied++;
      }
    }
  }

  /**
   * Fix MeshPhysicalMaterial by downgrading or cleaning
   * 通过降级或清理来修复 MeshPhysicalMaterial
   */
  fixPhysicalMaterial(material, object) {
    // Check if material has problematic properties
    const hasTransmission = material.transmission !== undefined && material.transmission > 0;
    const hasThickness = material.thickness !== undefined && material.thickness > 0;
    const hasClearcoat = material.clearcoat !== undefined && material.clearcoat > 0;

    if (hasTransmission || hasThickness || hasClearcoat) {
      if (this.debugMode) {
        console.warn(`⚠️ RenderSafetyPatch: MeshPhysicalMaterial with advanced features detected on ${object.name || 'unnamed'}`);
        console.warn(`   transmission=${material.transmission}, thickness=${material.thickness}, clearcoat=${material.clearcoat}`);
      }
      // Don't downgrade automatically, but warn
    }
  }

  /**
   * Get a reasonable default value based on uniform name
   * 根据 uniform 名称获取合理的默认值
   */
  getDefaultValue(uniformName) {
    const nameLower = uniformName.toLowerCase();

    // Time-related uniforms
    if (nameLower.includes('time')) {
      return 0.0;
    }

    // Color uniforms
    if (nameLower.includes('color') || nameLower.includes('colour')) {
      return new THREE.Color(0xffffff);
    }

    // Direction/normal vectors
    if (nameLower.includes('direction') || nameLower.includes('dir') || 
        nameLower.includes('normal')) {
      return new THREE.Vector3(0, 1, 0);
    }

    // Position vectors
    if (nameLower.includes('position') || nameLower.includes('pos')) {
      return new THREE.Vector3(0, 0, 0);
    }

    // Scale/size
    if (nameLower.includes('scale') || nameLower.includes('size')) {
      return 1.0;
    }

    // Opacity/alpha
    if (nameLower.includes('opacity') || nameLower.includes('alpha')) {
      return 1.0;
    }

    // Texture/sampler (null is valid for Three.js)
    if (nameLower.includes('texture') || nameLower.includes('map') || 
        nameLower.includes('sampler')) {
      return null;
    }

    // Default: scalar zero
    return 0.0;
  }

  /**
   * Handle render errors with intelligent recovery
   * 使用智能恢复处理渲染错误
   */
  handleRenderError(error, scene, camera) {
    this.errorsCaught++;

    console.error('❌ RenderSafetyPatch: Caught render error:', error.message);
    console.error('   Error type:', error.constructor.name);

    // Check if error is uniform-related
    if (error.message && error.message.includes("Cannot read properties of undefined (reading 'value')")) {
      console.log('🚑 RenderSafetyPatch: Detected uniform access error, applying emergency fix...');

      // Emergency deep scan and fix
      let fixCount = 0;
      scene.traverse((object) => {
        if (object.material) {
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => {
            if (material && material.type === 'ShaderMaterial' && material.uniforms) {
              for (const uniformName in material.uniforms) {
                const uniform = material.uniforms[uniformName];
                
                if (uniform === null || uniform === undefined || 
                    typeof uniform !== 'object' || !('value' in uniform) ||
                    uniform.value === undefined) {
                  
                  material.uniforms[uniformName] = { 
                    value: this.getDefaultValue(uniformName) 
                  };
                  fixCount++;
                }
              }
              material.needsUpdate = true;
            }
          });
        }
      });

      console.log(`✅ RenderSafetyPatch: Emergency fix applied (${fixCount} uniforms fixed)`);
      this.fixesApplied += fixCount;
    } else {
      console.error('   Stack:', error.stack);
    }
  }

  /**
   * Patch WebGLUniforms (advanced - directly modify Three.js internals)
   * 修补 WebGLUniforms（高级 - 直接修改 Three.js 内部）
   */
  patchWebGLUniforms() {
    // This is a defensive patch that wraps uniform access at the WebGL level
    // It's more aggressive but also more robust

    if (typeof THREE.WebGLUniforms !== 'undefined') {
      console.log('🔧 Patching THREE.WebGLUniforms for extra safety...');
      
      // Store original method if it exists
      const originalGetValue = THREE.WebGLUniforms.getValue;
      
      if (originalGetValue) {
        THREE.WebGLUniforms.getValue = function(uniform) {
          try {
            // Validate before calling original
            if (uniform === null || uniform === undefined) {
              console.warn('🔧 WebGLUniforms: Prevented access to null/undefined uniform');
              return 0.0;
            }
            if (typeof uniform !== 'object' || !('value' in uniform)) {
              console.warn('🔧 WebGLUniforms: Prevented access to malformed uniform');
              return 0.0;
            }
            if (uniform.value === undefined) {
              console.warn('🔧 WebGLUniforms: Prevented access to uniform with undefined value');
              return 0.0;
            }
            return originalGetValue.call(this, uniform);
          } catch (error) {
            console.error('🔧 WebGLUniforms: Caught error in getValue:', error);
            return 0.0;
          }
        };
        
        console.log('✅ THREE.WebGLUniforms patched successfully');
      }
    }
  }

  /**
   * Get statistics about fixes applied
   * 获取已应用修复的统计信息
   */
  getStats() {
    return {
      patchApplied: this.patchApplied,
      errorsCaught: this.errorsCaught,
      fixesApplied: this.fixesApplied
    };
  }

  /**
   * Print statistics
   * 打印统计信息
   */
  printStats() {
    console.log('📊 Render Safety Patch Stats:');
    console.log(`   Patch applied: ${this.patchApplied ? 'YES' : 'NO'}`);
    console.log(`   Errors caught: ${this.errorsCaught}`);
    console.log(`   Fixes applied: ${this.fixesApplied}`);
  }

  /**
   * Enable or disable debug mode
   * 启用或禁用调试模式
   */
  setDebugMode(enabled) {
    this.debugMode = enabled;
    console.log(`🔧 RenderSafetyPatch debug mode: ${enabled ? 'ENABLED' : 'DISABLED'}`);
  }
}

// Export singleton instance
export const renderSafetyPatch = new RenderSafetyPatch();

