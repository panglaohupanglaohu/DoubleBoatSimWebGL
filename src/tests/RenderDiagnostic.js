/**
 * Render Diagnostic Tool - 渲染诊断工具
 * 
 * 这个工具在渲染前进行彻底的诊断，精确定位哪个材质、哪个uniform出现问题
 * This tool performs thorough diagnosis before rendering to pinpoint exactly which material and uniform has issues
 */

export class RenderDiagnostic {
  constructor() {
    this.issues = [];
    this.scannedMaterials = 0;
    this.scannedObjects = 0;
    this.fixedIssues = 0;
  }

  /**
   * 深度扫描场景中的所有材质
   * Deep scan all materials in the scene
   */
  scanScene(scene) {
    console.log('🔍 开始渲染诊断 | Starting render diagnostic...');
    this.reset();
    
    const startTime = performance.now();
    scene.traverse((object) => {
      this.scanObject(object);
    });
    
    const duration = performance.now() - startTime;
    this.reportResults(duration);
    
    return {
      issues: this.issues,
      scannedMaterials: this.scannedMaterials,
      scannedObjects: this.scannedObjects,
      fixedIssues: this.fixedIssues
    };
  }

  /**
   * 扫描单个对象
   * Scan a single object
   */
  scanObject(object) {
    this.scannedObjects++;
    
    if (!object.material) return;

    const materials = Array.isArray(object.material) ? object.material : [object.material];
    
    materials.forEach((material, materialIndex) => {
      if (!material) {
        this.logIssue(object, materialIndex, 'NULL_MATERIAL', 'Material is null or undefined');
        return;
      }
      
      this.scannedMaterials++;
      this.scanMaterial(object, material, materialIndex);
    });
  }

  /**
   * 扫描单个材质
   * Scan a single material
   */
  scanMaterial(object, material, materialIndex) {
    // 检查材质类型
    const materialType = material.type || material.constructor.name;
    
    // 只有ShaderMaterial和RawShaderMaterial需要检查uniforms
    if (materialType !== 'ShaderMaterial' && materialType !== 'RawShaderMaterial') {
      return; // 其他材质类型由Three.js自动管理
    }

    // 检查uniforms属性是否存在
    if (!material.uniforms) {
      this.logIssue(object, materialIndex, 'MISSING_UNIFORMS', 
        `Material type '${materialType}' has no uniforms property`);
      // 修复：添加空uniforms对象
      material.uniforms = {};
      this.fixedIssues++;
      return;
    }

    if (typeof material.uniforms !== 'object') {
      this.logIssue(object, materialIndex, 'INVALID_UNIFORMS_TYPE', 
        `Material uniforms is not an object (type: ${typeof material.uniforms})`);
      // 修复：重置为空对象
      material.uniforms = {};
      this.fixedIssues++;
      return;
    }

    // 深度检查每个uniform
    this.scanUniforms(object, material, materialIndex);
  }

  /**
   * 扫描材质的所有uniforms
   * Scan all uniforms of a material
   */
  scanUniforms(object, material, materialIndex) {
    const uniformNames = Object.keys(material.uniforms);
    
    uniformNames.forEach((uniformName) => {
      const uniform = material.uniforms[uniformName];
      const issues = this.validateUniform(uniformName, uniform);
      
      issues.forEach((issue) => {
        this.logIssue(object, materialIndex, issue.type, issue.message, {
          uniformName,
          uniformValue: uniform,
          materialType: material.type || material.constructor.name
        });
        
        // 尝试修复
        if (this.fixUniform(material, uniformName, uniform, issue.type)) {
          this.fixedIssues++;
        }
      });
    });
  }

  /**
   * 验证单个uniform的结构
   * Validate a single uniform structure
   */
  validateUniform(uniformName, uniform) {
    const issues = [];

    // 检查1: uniform是否为null或undefined
    if (uniform === null) {
      issues.push({
        type: 'NULL_UNIFORM',
        message: `Uniform '${uniformName}' is null`
      });
      return issues;
    }

    if (uniform === undefined) {
      issues.push({
        type: 'UNDEFINED_UNIFORM',
        message: `Uniform '${uniformName}' is undefined`
      });
      return issues;
    }

    // 检查2: uniform是否为对象
    if (typeof uniform !== 'object') {
      issues.push({
        type: 'PRIMITIVE_UNIFORM',
        message: `Uniform '${uniformName}' is a primitive (${typeof uniform}), should be an object with 'value' property`
      });
      return issues;
    }

    // 检查3: uniform是否为数组（应该是对象）
    if (Array.isArray(uniform)) {
      issues.push({
        type: 'ARRAY_UNIFORM',
        message: `Uniform '${uniformName}' is an array, should be an object with 'value' property`
      });
      return issues;
    }

    // 检查4: uniform是否有value属性
    if (!('value' in uniform)) {
      issues.push({
        type: 'MISSING_VALUE_PROPERTY',
        message: `Uniform '${uniformName}' is missing 'value' property`
      });
    }

    // 检查5: value属性是否为undefined
    if (uniform.value === undefined) {
      issues.push({
        type: 'UNDEFINED_VALUE',
        message: `Uniform '${uniformName}' has undefined value`
      });
    }

    return issues;
  }

  /**
   * 尝试修复uniform
   * Attempt to fix a uniform
   */
  fixUniform(material, uniformName, uniform, issueType) {
    try {
      switch (issueType) {
        case 'NULL_UNIFORM':
        case 'UNDEFINED_UNIFORM':
          material.uniforms[uniformName] = { value: 0.0 };
          console.log(`✅ 已修复 | Fixed: ${uniformName} = { value: 0.0 }`);
          return true;

        case 'PRIMITIVE_UNIFORM':
          // 保留原始值，但包装成正确的结构
          material.uniforms[uniformName] = { value: uniform };
          console.log(`✅ 已修复 | Fixed: ${uniformName} wrapped primitive value`);
          return true;

        case 'ARRAY_UNIFORM':
          // 假设数组本身就是value
          material.uniforms[uniformName] = { value: uniform };
          console.log(`✅ 已修复 | Fixed: ${uniformName} wrapped array value`);
          return true;

        case 'MISSING_VALUE_PROPERTY':
          // 添加默认value
          uniform.value = 0.0;
          console.log(`✅ 已修复 | Fixed: ${uniformName} added default value`);
          return true;

        case 'UNDEFINED_VALUE':
          // 将value设为0
          uniform.value = 0.0;
          console.log(`✅ 已修复 | Fixed: ${uniformName}.value = 0.0`);
          return true;

        default:
          return false;
      }
    } catch (error) {
      console.error(`❌ 修复失败 | Fix failed for ${uniformName}:`, error);
      return false;
    }
  }

  /**
   * 记录问题
   * Log an issue
   */
  logIssue(object, materialIndex, type, message, details = {}) {
    const issue = {
      objectName: object.name || 'Unnamed Object',
      objectType: object.type || object.constructor.name,
      objectUuid: object.uuid,
      materialIndex,
      type,
      message,
      ...details
    };
    
    this.issues.push(issue);
    
    // 控制台输出
    console.warn(`🔴 Issue found | 发现问题:`, {
      object: `${issue.objectName} (${issue.objectType})`,
      material: `Index ${materialIndex}`,
      issue: `${type}: ${message}`,
      details
    });
  }

  /**
   * 重置统计
   * Reset statistics
   */
  reset() {
    this.issues = [];
    this.scannedMaterials = 0;
    this.scannedObjects = 0;
    this.fixedIssues = 0;
  }

  /**
   * 报告结果
   * Report results
   */
  reportResults(duration) {
    console.log('');
    console.log('═══════════════════════════════════════════════════════');
    console.log('📊 渲染诊断报告 | Render Diagnostic Report');
    console.log('═══════════════════════════════════════════════════════');
    console.log(`⏱️  扫描时间 | Scan time: ${duration.toFixed(2)}ms`);
    console.log(`🔍 扫描对象 | Scanned objects: ${this.scannedObjects}`);
    console.log(`🎨 扫描材质 | Scanned materials: ${this.scannedMaterials}`);
    console.log(`🔴 发现问题 | Issues found: ${this.issues.length}`);
    console.log(`✅ 已修复问题 | Fixed issues: ${this.fixedIssues}`);
    
    if (this.issues.length > 0) {
      console.log('');
      console.log('🔴 问题详情 | Issue Details:');
      console.log('───────────────────────────────────────────────────────');
      
      // 按问题类型分组
      const issuesByType = {};
      this.issues.forEach((issue) => {
        if (!issuesByType[issue.type]) {
          issuesByType[issue.type] = [];
        }
        issuesByType[issue.type].push(issue);
      });
      
      Object.keys(issuesByType).forEach((type) => {
        const typeIssues = issuesByType[type];
        console.log(`\n${type} (${typeIssues.length} occurrences):`);
        typeIssues.forEach((issue, index) => {
          console.log(`  ${index + 1}. Object: ${issue.objectName} (${issue.objectType})`);
          console.log(`     Material Index: ${issue.materialIndex}`);
          if (issue.uniformName) {
            console.log(`     Uniform: ${issue.uniformName}`);
          }
          console.log(`     Message: ${issue.message}`);
        });
      });
    } else {
      console.log('');
      console.log('✅ 没有发现问题！渲染应该正常工作。');
      console.log('✅ No issues found! Rendering should work correctly.');
    }
    
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
  }

  /**
   * 导出问题为JSON（用于进一步分析）
   * Export issues as JSON (for further analysis)
   */
  exportIssues() {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      scannedObjects: this.scannedObjects,
      scannedMaterials: this.scannedMaterials,
      issuesFound: this.issues.length,
      fixedIssues: this.fixedIssues,
      issues: this.issues
    }, null, 2);
  }
}

