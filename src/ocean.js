// Ocean shader based on Three.js ocean examples
// 参考 Three.js 官方 ocean 示例实现

// 注意：THREE 需要在导入此模块的上下文中可用
// Note: THREE must be available in the context where this module is imported

export const oceanParams = {
  amplitude: 0.8,
  wavelength: 12.0,
  speed: 1.2,
  steepness: 0.65,
  // 新增参数
  choppiness: 1.5,      // 波浪陡峭度
  waveCount: 4,         // 波浪数量
  waterColor: 0x006994,  // 海水颜色
  foamColor: 0xffffff,  // 泡沫颜色
  sunColor: 0xffffff,   // 太阳颜色
  sunDirection: null // 太阳方向（将在初始化时设置）
};

// Gerstner 波参数（多个波浪叠加）
// 注意：direction 将在初始化时创建 Vector2
export const gerstnerWaves = [
  { direction: null, steepness: 0.5, wavelength: 20.0, amplitude: 0.5, speed: 1.0 },
  { direction: null, steepness: 0.3, wavelength: 15.0, amplitude: 0.3, speed: 1.2 },
  { direction: null, steepness: 0.4, wavelength: 10.0, amplitude: 0.2, speed: 0.8 },
  { direction: null, steepness: 0.35, wavelength: 8.0, amplitude: 0.15, speed: 1.1 }
];

// 初始化函数（需要 THREE 对象）
// 注意：此函数现在主要用于初始化参数，uniform 的更新在 createOceanUniforms 中进行
export function initOcean(THREE) {
  // 初始化太阳方向
  if (!oceanParams.sunDirection) {
    oceanParams.sunDirection = new THREE.Vector3(0.5, 1.0, 0.5).normalize();
  }
  
  // 初始化波浪方向（如果还未初始化）
  if (!gerstnerWaves[0].direction) {
    gerstnerWaves[0].direction = new THREE.Vector2(1.0, 0.0).normalize();
    gerstnerWaves[1].direction = new THREE.Vector2(0.0, 1.0).normalize();
    gerstnerWaves[2].direction = new THREE.Vector2(1.0, 1.0).normalize();
    gerstnerWaves[3].direction = new THREE.Vector2(-0.5, 1.0).normalize();
  }
  
  // 注意：oceanUniforms 现在在 createOceanUniforms 中创建
  // 如果需要在创建后更新，应该在调用 createOceanUniforms 之后进行
}

// Uniforms 将在初始化时创建
export let oceanUniforms = null;

// 创建 uniform 的函数
export function createOceanUniforms(THREE) {
  // 确保在创建 uniform 之前初始化
  if (!oceanParams.sunDirection) {
    oceanParams.sunDirection = new THREE.Vector3(0.5, 1.0, 0.5).normalize();
  }
  
  // 初始化波浪方向（确保所有方向都已初始化）
  for (let i = 0; i < gerstnerWaves.length; i++) {
    if (!gerstnerWaves[i].direction) {
      const directions = [
        new THREE.Vector2(1.0, 0.0).normalize(),
        new THREE.Vector2(0.0, 1.0).normalize(),
        new THREE.Vector2(1.0, 1.0).normalize(),
        new THREE.Vector2(-0.5, 1.0).normalize()
      ];
      gerstnerWaves[i].direction = directions[i] || new THREE.Vector2(1.0, 0.0).normalize();
    }
  }
  
  // 确保所有波浪方向都是有效的 Vector2 对象
  const waveDirections = gerstnerWaves.map((w, i) => {
    if (w.direction && typeof w.direction.clone === 'function') {
      return w.direction.clone();
    } else {
      // 如果 direction 无效，使用默认值
      const defaults = [
        new THREE.Vector2(1.0, 0.0).normalize(),
        new THREE.Vector2(0.0, 1.0).normalize(),
        new THREE.Vector2(1.0, 1.0).normalize(),
        new THREE.Vector2(-0.5, 1.0).normalize()
      ];
      return defaults[i] || new THREE.Vector2(1.0, 0.0).normalize();
    }
  });
  
  return {
    uTime: { value: 0.0 },
    uAmplitude: { value: oceanParams.amplitude },
    uWavelength: { value: oceanParams.wavelength },
    uSpeed: { value: oceanParams.speed },
    uSteepness: { value: oceanParams.steepness },
    uChoppiness: { value: oceanParams.choppiness },
    uWaterColor: { value: new THREE.Color(oceanParams.waterColor) },
    uFoamColor: { value: new THREE.Color(oceanParams.foamColor) },
    uSunColor: { value: new THREE.Color(oceanParams.sunColor) },
    uSunDirection: { value: (oceanParams.sunDirection && typeof oceanParams.sunDirection.clone === 'function') 
      ? oceanParams.sunDirection.clone() 
      : new THREE.Vector3(0.5, 1.0, 0.5).normalize() },
    uCameraPosition: { value: new THREE.Vector3() },
    // 法线贴图
    uNormalMap: { value: null },
    uNormalScale: { value: new THREE.Vector2(1.0, 1.0) },
    // Gerstner 波参数（确保数组中的所有元素都是有效的）
    uWaveDirections: { value: waveDirections },
    uWaveSteepness: { value: gerstnerWaves.map(w => (w.steepness !== undefined && w.steepness !== null) ? w.steepness : 0.5) },
    uWaveWavelength: { value: gerstnerWaves.map(w => (w.wavelength !== undefined && w.wavelength !== null) ? w.wavelength : 10.0) },
    uWaveAmplitude: { value: gerstnerWaves.map(w => (w.amplitude !== undefined && w.amplitude !== null) ? w.amplitude : 0.5) },
    uWaveSpeed: { value: gerstnerWaves.map(w => (w.speed !== undefined && w.speed !== null) ? w.speed : 1.0) },
    uWaveCount: { value: gerstnerWaves.length }
  };
}

// 顶点着色器 - 使用 Gerstner 波
export const oceanVertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uAmplitude;
  uniform float uWavelength;
  uniform float uSpeed;
  uniform float uSteepness;
  uniform float uChoppiness;
  uniform vec2 uWaveDirections[4];
  uniform float uWaveSteepness[4];
  uniform float uWaveWavelength[4];
  uniform float uWaveAmplitude[4];
  uniform float uWaveSpeed[4];
  uniform int uWaveCount;

  varying vec3 vPosition;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;
  varying float vElevation;

  // Gerstner 波函数
  vec3 gerstnerWave(vec2 position, vec2 direction, float steepness, float wavelength, float amplitude, float speed, float time) {
    float k = 2.0 * 3.14159265 / wavelength;
    float w = sqrt(9.81 * k); // 重力波速
    float phase = k * dot(direction, position) - w * time * speed;
    float c = cos(phase);
    float s = sin(phase);
    
    vec3 result;
    result.x = -steepness * amplitude * direction.x * c;
    result.y = amplitude * s;
    result.z = -steepness * amplitude * direction.y * c;
    
    return result;
  }

  void main() {
    vec3 pos = position;
    vec3 tangent = vec3(1.0, 0.0, 0.0);
    vec3 binormal = vec3(0.0, 0.0, 1.0);
    vec3 normal = vec3(0.0, 1.0, 0.0);
    
    float elevation = 0.0;
    
    // 叠加多个 Gerstner 波
    for (int i = 0; i < 4; i++) {
      if (i >= uWaveCount) break;
      
      vec3 wave = gerstnerWave(
        pos.xz,
        uWaveDirections[i],
        uWaveSteepness[i],
        uWaveWavelength[i],
        uWaveAmplitude[i],
        uWaveSpeed[i],
        uTime
      );
      
      pos += wave;
      elevation += wave.y;
      
      // 计算切线和法线
      float k = 2.0 * 3.14159265 / uWaveWavelength[i];
      float w = sqrt(9.81 * k);
      float phase = k * dot(uWaveDirections[i], pos.xz) - w * uTime * uWaveSpeed[i];
      float c = cos(phase);
      float s = sin(phase);
      
      float QA = uWaveSteepness[i] * uWaveAmplitude[i];
      
      tangent += vec3(
        -uWaveDirections[i].x * uWaveDirections[i].x * QA * s,
        uWaveDirections[i].x * QA * c,
        -uWaveDirections[i].x * uWaveDirections[i].y * QA * s
      );
      
      binormal += vec3(
        -uWaveDirections[i].x * uWaveDirections[i].y * QA * s,
        uWaveDirections[i].y * QA * c,
        -uWaveDirections[i].y * uWaveDirections[i].y * QA * s
      );
    }
    
    // 计算法线
    normal = normalize(cross(binormal, tangent));
    
    vPosition = pos;
    vNormal = normal;
    vWorldPosition = (modelMatrix * vec4(pos, 1.0)).xyz;
    vElevation = elevation;
    
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

// 片段着色器 - 包含菲涅尔效果、光照等
export const oceanFragmentShader = /* glsl */ `
  uniform vec3 uWaterColor;
  uniform vec3 uFoamColor;
  uniform vec3 uSunColor;
  uniform vec3 uSunDirection;
  uniform vec3 uCameraPosition;
  uniform sampler2D uNormalMap;
  uniform vec2 uNormalScale;
  uniform float uTime;

  varying vec3 vPosition;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;
  varying float vElevation;

  // 菲涅尔效果
  float fresnel(vec3 viewDir, vec3 normal) {
    return pow(1.0 - max(dot(viewDir, normal), 0.0), 2.0);
  }

  // 从法线贴图采样法线
  vec3 getNormalFromMap(vec2 uv) {
    // 尝试采样法线贴图
    // 如果纹理未加载，texture2D 会返回默认值 (0, 0, 0, 1)
    vec4 normalSample = texture2D(uNormalMap, uv);
    
    // 检查是否有效（如果纹理未加载，所有通道可能为 0 或接近默认值）
    // 法线贴图的默认值通常是 (0.5, 0.5, 1.0) 在 [0,1] 范围内
    // 转换为 [-1,1] 范围后应该是 (0, 0, 1)
    vec3 tangentNormal = normalSample.xyz * 2.0 - 1.0;
    
    // 如果法线接近 (0, 0, 1)，可能是默认值，使用计算的法线
    if (length(tangentNormal - vec3(0.0, 0.0, 1.0)) < 0.1) {
      return normalize(vNormal);
    }
    
    tangentNormal.xy *= uNormalScale;
    
    // 构建 TBN 矩阵（简化版，使用顶点法线）
    vec3 N = normalize(vNormal);
    vec3 T = normalize(cross(N, vec3(0.0, 0.0, 1.0)));
    if (length(T) < 0.1) {
      T = normalize(cross(N, vec3(1.0, 0.0, 0.0)));
    }
    vec3 B = normalize(cross(N, T));
    mat3 TBN = mat3(T, B, N);
    
    return normalize(TBN * tangentNormal);
  }

  void main() {
    vec3 viewDir = normalize(uCameraPosition - vWorldPosition);
    
    // 使用法线贴图增强法线（如果可用）
    vec3 normal = normalize(vNormal);
    // 注意：在 GLSL 中，我们通过检查纹理尺寸来判断是否有效
    // 如果法线贴图已加载，使用它来增强法线
    vec2 uv = vWorldPosition.xz * 0.1 + uTime * 0.05;
    vec3 normalMap = getNormalFromMap(uv);
    // 混合计算的法线和法线贴图（法线贴图提供细节）
    normal = normalize(mix(normal, normalMap, 0.6));
    
    // 计算光照
    vec3 lightDir = normalize(uSunDirection);
    float NdotL = max(dot(normal, lightDir), 0.0);
    
    // 菲涅尔效果
    float fresnelFactor = fresnel(viewDir, normal);
    
    // 基础颜色（根据深度和波浪）
    vec3 baseColor = uWaterColor;
    
    // 根据波浪高度调整颜色（高处更亮）
    float waveFactor = smoothstep(-0.3, 0.3, vElevation);
    baseColor = mix(baseColor, uWaterColor * 1.2, waveFactor);
    
    // 泡沫效果（在波峰处）
    float foamFactor = smoothstep(0.2, 0.4, vElevation);
    vec3 foamColor = mix(baseColor, uFoamColor, foamFactor * 0.3);
    
    // 光照计算
    vec3 diffuse = foamColor * NdotL;
    vec3 specular = uSunColor * pow(max(dot(reflect(-lightDir, normal), viewDir), 0.0), 64.0) * 0.5;
    
    // 菲涅尔混合（边缘更透明，中心更不透明）
    vec3 finalColor = mix(diffuse, diffuse + specular, fresnelFactor);
    finalColor += specular * fresnelFactor;
    
    // 环境光
    finalColor += foamColor * 0.3;
    
    // 输出颜色
    gl_FragColor = vec4(finalColor, 0.9);
  }
`;

// 导出函数用于更新 uniform
export function updateOceanUniforms(uniforms, time, camera) {
  if (!uniforms || typeof uniforms !== 'object') {
    return; // 如果 uniforms 不存在或无效，直接返回
  }
  
  // 安全检查：确保 uniform 存在且有效
  if (uniforms.uTime && typeof uniforms.uTime === 'object' && 'value' in uniforms.uTime) {
    uniforms.uTime.value = time;
  }
  
  if (uniforms.uCameraPosition && typeof uniforms.uCameraPosition === 'object' && 'value' in uniforms.uCameraPosition && camera) {
    try {
      uniforms.uCameraPosition.value.copy(camera.position);
    } catch (err) {
      console.warn('⚠️ Error updating camera position in ocean uniforms:', err);
    }
  }
}

// 导出函数用于更新波浪参数
export function updateOceanWaveParams(uniforms, params) {
  if (!uniforms || typeof uniforms !== 'object' || !params || typeof params !== 'object') {
    return; // 如果参数无效，直接返回
  }
  
  // 安全检查：确保 uniform 存在且有效
  if (params.amplitude !== undefined && uniforms.uAmplitude && typeof uniforms.uAmplitude === 'object' && 'value' in uniforms.uAmplitude) {
    uniforms.uAmplitude.value = params.amplitude;
  }
  if (params.wavelength !== undefined && uniforms.uWavelength && typeof uniforms.uWavelength === 'object' && 'value' in uniforms.uWavelength) {
    uniforms.uWavelength.value = params.wavelength;
  }
  if (params.speed !== undefined && uniforms.uSpeed && typeof uniforms.uSpeed === 'object' && 'value' in uniforms.uSpeed) {
    uniforms.uSpeed.value = params.speed;
  }
  if (params.steepness !== undefined && uniforms.uSteepness && typeof uniforms.uSteepness === 'object' && 'value' in uniforms.uSteepness) {
    uniforms.uSteepness.value = params.steepness;
  }
  if (params.choppiness !== undefined && uniforms.uChoppiness && typeof uniforms.uChoppiness === 'object' && 'value' in uniforms.uChoppiness) {
    uniforms.uChoppiness.value = params.choppiness;
  }
}

