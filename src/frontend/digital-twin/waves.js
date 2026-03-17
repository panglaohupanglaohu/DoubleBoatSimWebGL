// Shared wave utilities for physics (JS) and shader (GLSL)

export const waveParams = {
  amplitude: 0.8,
  wavelength: 12.0,
  speed: 1.2,
  steepness: 0.65
};

export function getWaveHeight(x, z, t) {
  // 约定：在采样时对 Z 取反，便于与模型/场景坐标系对齐
  const zFlip = -z;
  const { amplitude, wavelength, speed } = waveParams;
  const k = (2 * Math.PI) / wavelength; // wave number
  const w = k * speed;                  // angular frequency

  const h1 = amplitude * Math.sin(k * x + w * t);
  const h2 = 0.55 * amplitude * Math.sin(k * (x + 0.45 * zFlip) + w * 1.35 * t);
  return h1 + h2;
}

export function getWaterNormal(x, z, t) {
  // Finite differences to approximate normal for lighting (optional)
  const eps = 0.1;
  const hL = getWaveHeight(x - eps, z, t);
  const hR = getWaveHeight(x + eps, z, t);
  const hD = getWaveHeight(x, z - eps, t);
  const hU = getWaveHeight(x, z + eps, t);
  const normal = {
    x: hL - hR,
    y: 2 * eps,
    z: hD - hU
  };
  const len = Math.hypot(normal.x, normal.y, normal.z) || 1;
  normal.x /= len; normal.y /= len; normal.z /= len;
  return normal;
}

export const waterUniforms = {
  uTime: { value: 0 },
  uAmplitude: { value: waveParams.amplitude },
  uWavelength: { value: waveParams.wavelength },
  uSpeed: { value: waveParams.speed },
  uSteepness: { value: waveParams.steepness },
  uYFlip: { value: 1.0 } // 正常为 1，若需要沿 Y 反转设为 -1
};

export const waterVertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uAmplitude;
  uniform float uWavelength;
  uniform float uSpeed;
  uniform float uSteepness;
  uniform float uYFlip;

  // Same function as JS getWaveHeight
  float getWaveHeight(vec2 xz, float time) {
    // Z 取反，保证与物理采样一致
    float zFlip = -xz.y;
    float k = 2.0 * 3.14159265 / uWavelength;
    float w = k * uSpeed;
    float h1 = uAmplitude * sin(k * xz.x + w * time);
    float h2 = 0.55 * uAmplitude * sin(k * (xz.x + 0.45 * zFlip) + w * 1.35 * time);
    return h1 + h2;
  }

  void main() {
    vec3 pos = position;
    float h = getWaveHeight(pos.xz, uTime);
    pos.y += h * uYFlip;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

export const waterFragmentShader = /* glsl */ `
  void main() {
    // Simple flat color; can be replaced with fresnel, normals, etc.
    gl_FragColor = vec4(0.0, 0.35, 0.6, 0.9);
  }
`;

