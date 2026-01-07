/**
 * 材质 Uniforms 诊断测试系统
 * Material Uniforms Diagnostic Test System
 * 
 * 目的：在渲染前检测和修复所有材质的 uniform 问题
 * Purpose: Detect and fix all material uniform issues before rendering
 */

import * as THREE from '../../public/lib/three.module.js';

export class MaterialUniformsTest {
  constructor() {
    this.testResults = [];
    this.errors = [];
    this.warnings = [];
    this.fixes = [];
  }

  /**
   * 深度检查场景中所有材质的 uniforms
   * Deep check all material uniforms in the scene
   */
  diagnoseScene(scene, renderer) {
    console.log('🔍 开始材质 Uniforms 诊断 | Starting Material Uniforms Diagnosis');
    console.log('================================================');
    
    this.testResults = [];
    this.errors = [];
    this.warnings = [];
    this.fixes = [];
    
    // 1. 检查渲染器配置
    this.checkRendererConfiguration(renderer);
    
    // 2. 遍历场景检查所有材质
    const materialMap = new Map();
    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.forEach((material, index) => {
          if (!material) {
            this.errors.push({
              object: object.name || object.uuid,
              issue: 'Material is null or undefined',
              materialIndex: index
            });
            return;
          }
          
          // 使用材质 UUID 作为唯一标识符
          if (!materialMap.has(material.uuid)) {
            materialMap.set(material.uuid, {
              material,
              objects: []
            });
          }
          materialMap.get(material.uuid).objects.push(object.name || object.uuid);
        });
      }
    });
    
    // 3. 检查每个唯一材质
    console.log(`\n📊 发现 ${materialMap.size} 个唯一材质 | Found ${materialMap.size} unique materials`);
    
    materialMap.forEach((data, uuid) => {
      this.checkMaterial(data.material, data.objects);
    });
    
    // 4. 输出诊断报告
    this.printDiagnosticReport();
    
    return {
      passed: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
      fixes: this.fixes,
      summary: {
        totalMaterials: materialMap.size,
        errorCount: this.errors.length,
        warningCount: this.warnings.length,
        fixCount: this.fixes.length
      }
    };
  }

  /**
   * 检查渲染器配置
   */
  checkRendererConfiguration(renderer) {
    console.log('\n🎨 检查渲染器配置 | Checking Renderer Configuration');
    
    const checks = {
      'antialias': renderer.antialias,
      'alpha': renderer.alpha,
      'toneMapping': renderer.toneMapping,
      'toneMappingExposure': renderer.toneMappingExposure,
      'outputEncoding': renderer.outputEncoding,
      'physicallyCorrectLights': renderer.physicallyCorrectLights,
      'shadowMap.enabled': renderer.shadowMap?.enabled,
      'transmissionResolutionScale': renderer.transmissionResolutionScale
    };
    
    Object.entries(checks).forEach(([key, value]) => {
      console.log(`  ${key}: ${value}`);
    });
  }

  /**
   * 检查单个材质
   */
  checkMaterial(material, usedByObjects) {
    const materialInfo = {
      type: material.type,
      uuid: material.uuid,
      name: material.name || 'unnamed',
      usedBy: usedByObjects.join(', ')
    };
    
    console.log(`\n🔬 检查材质 | Checking Material: ${materialInfo.type} (${materialInfo.name})`);
    console.log(`   使用对象 | Used by: ${materialInfo.usedBy}`);
    
    // 检查不同类型的材质
    if (material.type === 'ShaderMaterial') {
      this.checkShaderMaterial(material, materialInfo);
    } else if (material.type === 'MeshPhysicalMaterial') {
      this.checkPhysicalMaterial(material, materialInfo);
    } else if (material.type === 'MeshStandardMaterial') {
      this.checkStandardMaterial(material, materialInfo);
    } else {
      this.checkBasicMaterial(material, materialInfo);
    }
  }

  /**
   * 检查 ShaderMaterial 的 uniforms
   */
  checkShaderMaterial(material, materialInfo) {
    if (!material.uniforms) {
      this.errors.push({
        ...materialInfo,
        issue: 'ShaderMaterial has no uniforms object'
      });
      console.error('  ❌ 错误: 没有 uniforms 对象 | Error: No uniforms object');
      return;
    }

    console.log(`  📦 Uniforms 数量 | Uniform count: ${Object.keys(material.uniforms).length}`);
    
    // 检查每个 uniform
    Object.entries(material.uniforms).forEach(([uniformName, uniform]) => {
      const uniformStatus = this.checkUniform(uniformName, uniform, materialInfo);
      
      if (uniformStatus.error) {
        this.errors.push({
          ...materialInfo,
          uniformName,
          issue: uniformStatus.error,
          value: uniform
        });
        console.error(`  ❌ ${uniformName}: ${uniformStatus.error}`);
      } else if (uniformStatus.warning) {
        this.warnings.push({
          ...materialInfo,
          uniformName,
          issue: uniformStatus.warning,
          value: uniform
        });
        console.warn(`  ⚠️  ${uniformName}: ${uniformStatus.warning}`);
      } else {
        console.log(`  ✅ ${uniformName}: ${uniformStatus.valueType} = ${this.formatValue(uniform.value)}`);
      }
    });
  }

  /**
   * 检查单个 uniform 的有效性
   */
  checkUniform(uniformName, uniform, materialInfo) {
    // 检查 uniform 本身是否存在
    if (uniform === null || uniform === undefined) {
      return { error: `Uniform is ${uniform}` };
    }

    // 检查是否是对象
    if (typeof uniform !== 'object') {
      return { error: `Uniform is not an object (type: ${typeof uniform})` };
    }

    // 检查是否有 value 属性
    if (!('value' in uniform)) {
      return { error: 'Uniform object has no "value" property' };
    }

    // 检查 value 是否有效
    if (uniform.value === undefined) {
      return { error: 'Uniform value is undefined' };
    }

    if (uniform.value === null) {
      return { warning: 'Uniform value is null (may be intentional for textures)' };
    }

    // 检查 value 类型
    const valueType = this.getValueType(uniform.value);
    
    return { 
      success: true, 
      valueType 
    };
  }

  /**
   * 获取值的类型描述
   */
  getValueType(value) {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    
    if (value instanceof THREE.Texture) return 'Texture';
    if (value instanceof THREE.Vector2) return 'Vector2';
    if (value instanceof THREE.Vector3) return 'Vector3';
    if (value instanceof THREE.Vector4) return 'Vector4';
    if (value instanceof THREE.Color) return 'Color';
    if (value instanceof THREE.Matrix3) return 'Matrix3';
    if (value instanceof THREE.Matrix4) return 'Matrix4';
    
    if (typeof value === 'number') return 'number';
    if (typeof value === 'boolean') return 'boolean';
    if (Array.isArray(value)) return `Array[${value.length}]`;
    
    return typeof value;
  }

  /**
   * 格式化值用于显示
   */
  formatValue(value) {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    
    if (value instanceof THREE.Texture) {
      return `Texture(${value.image?.width || '?'}x${value.image?.height || '?'})`;
    }
    if (value instanceof THREE.Vector2) return `(${value.x.toFixed(2)}, ${value.y.toFixed(2)})`;
    if (value instanceof THREE.Vector3) return `(${value.x.toFixed(2)}, ${value.y.toFixed(2)}, ${value.z.toFixed(2)})`;
    if (value instanceof THREE.Color) return `#${value.getHexString()}`;
    
    if (typeof value === 'number') return value.toFixed(4);
    if (typeof value === 'boolean') return value.toString();
    if (Array.isArray(value)) return `[${value.length} elements]`;
    
    return String(value);
  }

  /**
   * 检查 MeshPhysicalMaterial
   */
  checkPhysicalMaterial(material, materialInfo) {
    console.warn('  ⚠️  MeshPhysicalMaterial 可能导致 uniform 错误 | May cause uniform errors');
    
    const issues = [];
    
    if (material.transmission !== undefined && material.transmission > 0) {
      issues.push(`transmission=${material.transmission}`);
    }
    
    if (material.thickness !== undefined && material.thickness > 0) {
      issues.push(`thickness=${material.thickness}`);
    }
    
    if (material.clearcoat !== undefined && material.clearcoat > 0) {
      issues.push(`clearcoat=${material.clearcoat}`);
    }

    if (issues.length > 0) {
      this.warnings.push({
        ...materialInfo,
        issue: `MeshPhysicalMaterial with advanced features: ${issues.join(', ')}`,
        recommendation: 'Consider downgrading to MeshStandardMaterial'
      });
      console.warn(`  ⚠️  高级特性 | Advanced features: ${issues.join(', ')}`);
      console.warn('  💡 建议降级为 MeshStandardMaterial | Recommend downgrading to MeshStandardMaterial');
    }
  }

  /**
   * 检查 MeshStandardMaterial
   */
  checkStandardMaterial(material, materialInfo) {
    // 检查是否错误地设置了 Physical Material 属性
    const invalidProps = [];
    
    if ('transmission' in material) invalidProps.push('transmission');
    if ('thickness' in material) invalidProps.push('thickness');
    if ('clearcoat' in material && material.type === 'MeshStandardMaterial') {
      // MeshStandardMaterial 本身不支持 clearcoat
      invalidProps.push('clearcoat');
    }
    
    if (invalidProps.length > 0) {
      this.warnings.push({
        ...materialInfo,
        issue: `MeshStandardMaterial has invalid Physical Material properties: ${invalidProps.join(', ')}`
      });
      console.warn(`  ⚠️  无效属性 | Invalid properties: ${invalidProps.join(', ')}`);
    } else {
      console.log('  ✅ 标准材质正常 | Standard material is valid');
    }
  }

  /**
   * 检查基础材质
   */
  checkBasicMaterial(material, materialInfo) {
    console.log(`  ✅ 基础材质类型 | Basic material type: ${material.type}`);
  }

  /**
   * 打印诊断报告
   */
  printDiagnosticReport() {
    console.log('\n\n================================================');
    console.log('📋 诊断报告 | Diagnostic Report');
    console.log('================================================');
    
    console.log(`\n✅ 通过 | Passed: ${this.errors.length === 0 ? 'YES' : 'NO'}`);
    console.log(`❌ 错误数 | Errors: ${this.errors.length}`);
    console.log(`⚠️  警告数 | Warnings: ${this.warnings.length}`);
    console.log(`🔧 修复数 | Fixes: ${this.fixes.length}`);
    
    if (this.errors.length > 0) {
      console.log('\n❌ 错误详情 | Error Details:');
      this.errors.forEach((error, index) => {
        console.log(`\n  ${index + 1}. ${error.type} (${error.name})`);
        console.log(`     问题 | Issue: ${error.issue}`);
        console.log(`     使用对象 | Used by: ${error.usedBy}`);
        if (error.uniformName) {
          console.log(`     Uniform: ${error.uniformName}`);
          console.log(`     值 | Value:`, error.value);
        }
      });
    }
    
    if (this.warnings.length > 0) {
      console.log('\n⚠️  警告详情 | Warning Details:');
      this.warnings.forEach((warning, index) => {
        console.log(`\n  ${index + 1}. ${warning.type} (${warning.name})`);
        console.log(`     问题 | Issue: ${warning.issue}`);
        if (warning.recommendation) {
          console.log(`     建议 | Recommendation: ${warning.recommendation}`);
        }
      });
    }
    
    console.log('\n================================================\n');
  }

  /**
   * 自动修复检测到的问题
   */
  autoFix(scene) {
    console.log('🔧 开始自动修复 | Starting Auto-Fix');
    console.log('================================================');
    
    let fixCount = 0;
    
    scene.traverse((object) => {
      if (!object.material) return;
      
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      const newMaterials = [];
      let materialsChanged = false;
      
      materials.forEach((material) => {
        if (!material) {
          newMaterials.push(null);
          return;
        }
        
        // 修复 1: 降级 MeshPhysicalMaterial
        if (material.type === 'MeshPhysicalMaterial') {
          console.log(`  🔧 降级 MeshPhysicalMaterial -> MeshStandardMaterial (对象: ${object.name || object.uuid})`);
          
          const newMaterial = new THREE.MeshStandardMaterial({
            color: material.color ? material.color.clone() : new THREE.Color(0xffffff),
            map: material.map,
            roughness: material.roughness !== undefined ? material.roughness : 0.5,
            metalness: material.metalness !== undefined ? material.metalness : 0.0,
            transparent: material.transparent !== undefined ? material.transparent : false,
            opacity: material.opacity !== undefined ? material.opacity : 1.0,
            side: material.side !== undefined ? material.side : THREE.FrontSide,
            depthWrite: material.depthWrite !== undefined ? material.depthWrite : true,
            depthTest: material.depthTest !== undefined ? material.depthTest : true
          });
          
          newMaterials.push(newMaterial);
          materialsChanged = true;
          fixCount++;
          
          this.fixes.push({
            object: object.name || object.uuid,
            action: 'Downgraded MeshPhysicalMaterial to MeshStandardMaterial'
          });
        }
        // 修复 2: 修复 ShaderMaterial 的 uniforms
        else if (material.type === 'ShaderMaterial') {
          let uniformsFixed = false;
          
          if (material.uniforms && typeof material.uniforms === 'object') {
            Object.entries(material.uniforms).forEach(([uniformName, uniform]) => {
              // 修复缺失的 uniform 对象
              if (uniform === null || uniform === undefined || typeof uniform !== 'object') {
                material.uniforms[uniformName] = { value: 0.0 };
                uniformsFixed = true;
                console.log(`    🔧 修复 uniform: ${uniformName} (创建默认对象)`);
              }
              // 修复缺失的 value 属性
              else if (!('value' in uniform)) {
                uniform.value = 0.0;
                uniformsFixed = true;
                console.log(`    🔧 修复 uniform: ${uniformName} (添加 value 属性)`);
              }
              // 修复 undefined value
              else if (uniform.value === undefined) {
                uniform.value = 0.0;
                uniformsFixed = true;
                console.log(`    🔧 修复 uniform: ${uniformName} (value 从 undefined 改为 0.0)`);
              }
            });
          }
          
          if (uniformsFixed) {
            material.needsUpdate = true;
            fixCount++;
            this.fixes.push({
              object: object.name || object.uuid,
              action: `Fixed ShaderMaterial uniforms`
            });
          }
          
          newMaterials.push(material);
        }
        // 修复 3: 移除 MeshStandardMaterial 的无效属性
        else if (material.type === 'MeshStandardMaterial') {
          let propsRemoved = false;
          
          if ('transmission' in material) {
            delete material.transmission;
            propsRemoved = true;
            console.log(`    🔧 移除无效属性: transmission`);
          }
          if ('thickness' in material) {
            delete material.thickness;
            propsRemoved = true;
            console.log(`    🔧 移除无效属性: thickness`);
          }
          
          if (propsRemoved) {
            material.needsUpdate = true;
            fixCount++;
            this.fixes.push({
              object: object.name || object.uuid,
              action: 'Removed invalid Physical Material properties from MeshStandardMaterial'
            });
          }
          
          newMaterials.push(material);
        }
        else {
          newMaterials.push(material);
        }
      });
      
      // 应用修复后的材质
      if (materialsChanged) {
        if (Array.isArray(object.material)) {
          object.material = newMaterials;
        } else {
          object.material = newMaterials[0];
        }
      }
    });
    
    console.log(`\n✅ 自动修复完成 | Auto-Fix Complete: ${fixCount} 个问题已修复 | issues fixed`);
    console.log('================================================\n');
    
    return fixCount;
  }

  /**
   * 运行完整的诊断和修复流程
   */
  runFullDiagnostic(scene, renderer) {
    console.log('🚀 运行完整诊断和修复流程 | Running Full Diagnostic and Fix Process');
    console.log('================================================\n');
    
    // 1. 诊断
    const diagnosticResult = this.diagnoseScene(scene, renderer);
    
    // 2. 如果有错误或警告，执行自动修复
    if (diagnosticResult.errors.length > 0 || diagnosticResult.warnings.length > 0) {
      const fixCount = this.autoFix(scene);
      
      // 3. 再次诊断验证修复结果
      console.log('\n🔄 验证修复结果 | Verifying Fix Results\n');
      const verifyResult = this.diagnoseScene(scene, renderer);
      
      return {
        initial: diagnosticResult,
        fixCount,
        verified: verifyResult,
        success: verifyResult.errors.length === 0
      };
    }
    
    return {
      initial: diagnosticResult,
      fixCount: 0,
      success: diagnosticResult.errors.length === 0
    };
  }
}

// 导出单例实例
export const materialUniformsTest = new MaterialUniformsTest();

