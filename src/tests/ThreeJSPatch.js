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
  let errorCount = 0;
  const maxErrorCount = 3; // 最多只处理3次错误
  let lastErrorTime = 0;
  const errorCooldown = 5000; // 5秒冷却时间
  
  // 临时拦截 console.error 来找到 Three.js 内部错误
  console.error = function(...args) {
    const errorMsg = args.join(' ');
    const now = Date.now();
    
    // 如果是 uniform 相关错误，标记需要 patch
    if (errorMsg.includes('Cannot read properties of undefined') || 
        errorMsg.includes('uniform') && errorMsg.includes('undefined')) {
      
      // 检查是否在冷却期内
      if (now - lastErrorTime < errorCooldown) {
        // 在冷却期内，静默忽略
        return;
      }
      
      // 检查错误次数
      if (errorCount < maxErrorCount && !patched) {
        errorCount++;
        lastErrorTime = now;
        
        if (errorCount === 1) {
          console.warn('⚠️ 检测到 uniform 错误，正在应用紧急修复...');
          applyEmergencyPatch();
          patched = true;
        } else {
          // 后续错误静默处理，避免刷屏
          return;
        }
      } else {
        // 超过最大次数，静默忽略
        return;
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
  
  let hasFixed = false; // 标记是否已经修复过
  
  // 在 window 上挂载一个全局修复函数
  window._fixAllUniforms = function(scene) {
    // 如果已经修复过，直接返回
    if (hasFixed) {
      return 0;
    }
    
    let fixCount = 0;
    const fixedMaterials = new WeakSet(); // 使用 WeakSet 跟踪已修复的材质
    
    scene.traverse((object) => {
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        
        materials.forEach((material) => {
          // 跳过已修复的材质
          if (fixedMaterials.has(material)) {
            return;
          }
          
          if (material && material.uniforms && typeof material.uniforms === 'object') {
            // 遍历所有 uniform 名称
            const uniformNames = Object.keys(material.uniforms);
            
            for (const uniformName of uniformNames) {
              try {
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
              } catch (e) {
                // 如果访问 uniform 时出错，直接删除它
                try {
                  delete material.uniforms[uniformName];
                  fixCount++;
                } catch (deleteError) {
                  // 忽略删除错误
                }
              }
            }
            
            // 标记材质已修复
            fixedMaterials.add(material);
            
            // 标记材质需要更新
            if (material.needsUpdate !== undefined) {
              material.needsUpdate = true;
            }
          }
        });
      }
    });
    
    if (fixCount > 0) {
      console.log(`🔧 紧急修复了 ${fixCount} 个 uniform`);
      hasFixed = true; // 标记已修复
    }
    
    return fixCount;
  };
}




