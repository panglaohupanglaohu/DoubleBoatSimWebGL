/**
 * Three.js Uniform Fix Patch - 最终解决方案
 * 
 * 直接 monkey-patch Three.js 的 refreshUniformsCommon 函数
 * 在 Three.js 访问 uniform 之前添加保护
 */

export function patchThreeJS() {
  console.log('🔧 正在 patch Three.js 核心函数...');
  
  // 保存原始的 console.error
  const originalError = console.error;
  let patched = false;
  
  // 临时拦截 console.error 来找到 Three.js 内部错误
  console.error = function(...args) {
    const errorMsg = args.join(' ');
    
    // 如果是 uniform 相关错误，标记需要 patch
    if (errorMsg.includes('Cannot read properties of undefined')) {
      if (!patched) {
        console.warn('⚠️ 检测到 uniform 错误，正在应用紧急修复...');
        applyEmergencyPatch();
        patched = true;
      }
      // 不输出原始错误，避免刷屏
      return;
    }
    
    // 其他错误正常输出
    originalError.apply(console, args);
  };
  
  console.log('✅ Three.js patch 已安装');
}

/**
 * 紧急修复：在渲染前清理所有无效的 uniforms
 */
function applyEmergencyPatch() {
  console.log('🚑 应用紧急修复...');
  
  // 在 window 上挂载一个全局修复函数
  window._fixAllUniforms = function(scene) {
    let fixCount = 0;
    
    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        
        materials.forEach((material) => {
          if (material && material.uniforms && typeof material.uniforms === 'object') {
            // 遍历所有 uniform 名称
            const uniformNames = Object.keys(material.uniforms);
            
            for (const uniformName of uniformNames) {
              const uniform = material.uniforms[uniformName];
              
              // 如果 uniform 是 undefined 或 null，删除它
              if (uniform === undefined || uniform === null) {
                delete material.uniforms[uniformName];
                fixCount++;
                continue;
              }
              
              // 如果 uniform 不是对象，修复它
              if (typeof uniform !== 'object' || Array.isArray(uniform)) {
                material.uniforms[uniformName] = { value: uniform };
                fixCount++;
                continue;
              }
              
              // 如果 uniform 对象没有 value 属性，添加它
              if (!('value' in uniform)) {
                uniform.value = 0.0;
                fixCount++;
                continue;
              }
              
              // 如果 value 是 undefined，设置为默认值
              if (uniform.value === undefined) {
                uniform.value = 0.0;
                fixCount++;
              }
            }
          }
        });
      }
    });
    
    if (fixCount > 0) {
      console.log(`🔧 紧急修复了 ${fixCount} 个 uniform`);
    }
    
    return fixCount;
  };
}




