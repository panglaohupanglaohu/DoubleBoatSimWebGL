/**
 * WeatherEffects.js — 3D 天气可视化效果
 *
 * 风粒子、雨粒子、雾气、波浪联动
 * 接收 WorldMonitor / externalSync 天气数据驱动
 */

import * as THREE from 'https://esm.sh/three@0.165.0';

const DEG2RAD = Math.PI / 180;

// ==================== 默认配置 ====================

const DEFAULT_WEATHER = {
    wind: { speed: 5, direction: 180 },     // m/s, degrees (0=N, 90=E)
    wave: { height: 1.0, period: 8 },       // m, s
    rain: { intensity: 0 },                 // 0-1
    precipitation: { type: 'none', intensity: 0 }, // type: none|rain|snow|mixed
    visibility: 10,                         // km
    temperature: 20,                        // °C
};

export default class WeatherEffects {
    constructor(scene, options = {}) {
        this.scene = scene;
        this.enabled = true;
        this.weather = { ...DEFAULT_WEATHER };

        // 可视化开关
        this.showWind = options.showWind ?? true;
        this.showRain = options.showRain ?? true;
        this.showFog = options.showFog ?? true;
        this.showWaves = options.showWaves ?? true;

        // 粒子容量
        this.windParticleCount = options.windParticleCount ?? 600;
        this.rainParticleCount = options.rainParticleCount ?? 2000;

        // 绑定范围 (场景立方体)
        this.bounds = options.bounds ?? { x: 80, y: 30, z: 80 };

        // 内部对象
        this._windParticles = null;
        this._rainParticles = null;
        this._originalFog = scene.fog ? scene.fog.clone() : null;
        this._windArrow = null;

        this._init();
    }

    // ==================== 初始化 ====================

    _init() {
        this._createWindParticles();
        this._createRainParticles();
        this._createWindArrow();
    }

    // ==================== 风粒子 ====================

    _createWindParticles() {
        const count = this.windParticleCount;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const velocities = new Float32Array(count * 3);
        const sizes = new Float32Array(count);

        for (let i = 0; i < count; i++) {
            positions[i * 3]     = (Math.random() - 0.5) * this.bounds.x;
            positions[i * 3 + 1] = this.bounds.y * 0.5 + Math.random() * this.bounds.y;
            positions[i * 3 + 2] = (Math.random() - 0.5) * this.bounds.z;
            sizes[i] = 0.15 + Math.random() * 0.25;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));

        const material = new THREE.PointsMaterial({
            color: 0xccddee,
            size: 0.3,
            transparent: true,
            opacity: 0.35,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            sizeAttenuation: true,
        });

        this._windParticles = new THREE.Points(geometry, material);
        this._windParticles.frustumCulled = false;
        this._windParticles.visible = this.showWind;
        this.scene.add(this._windParticles);
    }

    // ==================== 雨粒子 ====================

    _createRainParticles() {
        const count = this.rainParticleCount;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);

        for (let i = 0; i < count; i++) {
            positions[i * 3]     = (Math.random() - 0.5) * this.bounds.x;
            positions[i * 3 + 1] = this.bounds.y + Math.random() * 20;
            positions[i * 3 + 2] = (Math.random() - 0.5) * this.bounds.z;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            color: 0x8899bb,
            size: 0.08,
            transparent: true,
            opacity: 0.6,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            sizeAttenuation: true,
        });

        this._rainParticles = new THREE.Points(geometry, material);
        this._rainParticles.frustumCulled = false;
        this._rainParticles.visible = false; // 默认无雨
        this.scene.add(this._rainParticles);
    }

    // ==================== 风向箭头 ====================

    _createWindArrow() {
        const dir = new THREE.Vector3(0, 0, -1);
        const origin = new THREE.Vector3(0, 20, 0);
        this._windArrow = new THREE.ArrowHelper(dir, origin, 8, 0x4fc3f7, 1.5, 1.0);
        this._windArrow.visible = this.showWind;
        this.scene.add(this._windArrow);
    }

    // ==================== 更新天气数据 ====================

    setWeather(weatherData = {}) {
        const w = this.weather;
        if (weatherData.wind) {
            w.wind.speed = weatherData.wind.speed ?? w.wind.speed;
            w.wind.direction = weatherData.wind.direction ?? w.wind.direction;
        }
        if (weatherData.wave) {
            w.wave.height = weatherData.wave.height ?? w.wave.height;
            w.wave.period = weatherData.wave.period ?? w.wave.period;
        }
        if (weatherData.rain != null) {
            w.rain.intensity = typeof weatherData.rain === 'number'
                ? weatherData.rain
                : (weatherData.rain.intensity ?? w.rain.intensity);
        }
        if (weatherData.precipitation != null) {
            const p = weatherData.precipitation;
            w.rain.intensity = typeof p.intensity === 'number' ? p.intensity : w.rain.intensity;
            if (!w.precipitation) w.precipitation = { type: 'rain', intensity: 0 };
            w.precipitation.type = p.type ?? 'rain';
            w.precipitation.intensity = w.rain.intensity;
        }
        if (weatherData.visibility != null) {
            w.visibility = weatherData.visibility;
        }
        if (weatherData.temperature != null) {
            w.temperature = weatherData.temperature;
        }
        this._applyFog();
        this._applyRainVisibility();
        this._updateWindArrow();
    }

    // ==================== 逐帧更新 ====================

    update(dt) {
        if (!this.enabled) return;
        this._updateWindParticles(dt);
        this._updateRainParticles(dt);
    }

    _updateWindParticles(dt) {
        if (!this._windParticles || !this._windParticles.visible) return;

        const positions = this._windParticles.geometry.attributes.position.array;
        const count = this.windParticleCount;
        const { speed, direction } = this.weather.wind;

        // 风向转速度分量 (direction=0 => 北风=从北吹来 => -Z方向)
        const rad = direction * DEG2RAD;
        const vx = -Math.sin(rad) * speed * 0.5;
        const vz = -Math.cos(rad) * speed * 0.5;
        const vy = -0.3; // 轻微下沉

        const halfX = this.bounds.x / 2;
        const halfZ = this.bounds.z / 2;
        const maxY = this.bounds.y;

        for (let i = 0; i < count; i++) {
            const ix = i * 3;
            positions[ix]     += vx * dt;
            positions[ix + 1] += vy * dt;
            positions[ix + 2] += vz * dt;

            // 超出边界循环
            if (positions[ix] > halfX) positions[ix] = -halfX;
            if (positions[ix] < -halfX) positions[ix] = halfX;
            if (positions[ix + 2] > halfZ) positions[ix + 2] = -halfZ;
            if (positions[ix + 2] < -halfZ) positions[ix + 2] = halfZ;
            if (positions[ix + 1] < -1) positions[ix + 1] = maxY;
        }

        this._windParticles.geometry.attributes.position.needsUpdate = true;

        // 风速越大，粒子越明显
        const normalizedSpeed = Math.min(speed / 25, 1);
        this._windParticles.material.opacity = 0.15 + normalizedSpeed * 0.45;
        this._windParticles.material.size = 0.2 + normalizedSpeed * 0.3;
    }

    _updateRainParticles(dt) {
        if (!this._rainParticles || !this._rainParticles.visible) return;

        const positions = this._rainParticles.geometry.attributes.position.array;
        const count = this.rainParticleCount;
        const { speed, direction } = this.weather.wind;
        const intensity = this.weather.rain.intensity;
        const precipType = this.weather.precipitation?.type ?? 'rain';

        const rad = direction * DEG2RAD;

        // Physics-correct precipitation parameters (Gunn & Kinzer 1949)
        let terminalV, driftCoeff;
        if (precipType === 'snow') {
            terminalV = 1.0 + intensity * 0.5;
            driftCoeff = 0.98;
        } else if (precipType === 'mixed') {
            terminalV = 3.0 + intensity * 1.5;
            driftCoeff = 0.92;
        } else {
            terminalV = 5.0 + intensity * 4.0;
            driftCoeff = 0.85;
        }

        const windDrift = speed * driftCoeff;
        const vx = -Math.sin(rad) * windDrift;
        const vz = -Math.cos(rad) * windDrift;
        const fallSpeed = terminalV * 2.0;

        const halfX = this.bounds.x / 2;
        const halfZ = this.bounds.z / 2;
        const maxY = this.bounds.y;

        for (let i = 0; i < count; i++) {
            const ix = i * 3;
            positions[ix]     += vx * dt;
            positions[ix + 1] -= fallSpeed * dt;
            positions[ix + 2] += vz * dt;

            if (precipType === 'snow') {
                positions[ix] += Math.sin(Date.now() * 0.002 + i) * 0.3 * dt;
                positions[ix + 2] += Math.cos(Date.now() * 0.0015 + i * 1.3) * 0.2 * dt;
            }

            if (positions[ix + 1] < -1) {
                positions[ix]     = (Math.random() - 0.5) * this.bounds.x;
                positions[ix + 1] = maxY + 10 + Math.random() * 15;
                positions[ix + 2] = (Math.random() - 0.5) * this.bounds.z;
            }
            if (positions[ix] > halfX) positions[ix] = -halfX;
            if (positions[ix] < -halfX) positions[ix] = halfX;
            if (positions[ix + 2] > halfZ) positions[ix + 2] = -halfZ;
            if (positions[ix + 2] < -halfZ) positions[ix + 2] = halfZ;
        }

        this._rainParticles.geometry.attributes.position.needsUpdate = true;
    }

    // ==================== 雾效果 ====================

    _applyFog() {
        if (!this.showFog) return;

        const vis = Math.max(this.weather.visibility, 0.5);
        // visibility(km) -> fog near/far
        const fogNear = vis * 5;        // 5km => near=25
        const fogFar = vis * 22;        // 5km => far=110
        const fogColor = this._getFogColor();

        if (this.scene.fog) {
            this.scene.fog.near = fogNear;
            this.scene.fog.far = fogFar;
            this.scene.fog.color.copy(fogColor);
        } else {
            this.scene.fog = new THREE.Fog(fogColor, fogNear, fogFar);
        }

        // 同步背景色
        if (vis < 5) {
            this.scene.background = fogColor.clone().multiplyScalar(0.85);
        }
    }

    _getFogColor() {
        const vis = this.weather.visibility;
        const rain = this.weather.rain.intensity;
        // 低能见度 / 大雨 -> 灰暗色
        if (rain > 0.5 || vis < 3) {
            return new THREE.Color(0x283038);
        }
        if (vis < 6) {
            return new THREE.Color(0x1a2530);
        }
        return new THREE.Color(0x0b1525); // 正常深蓝
    }

    _applyRainVisibility() {
        const intensity = this.weather.rain.intensity;
        const precipType = this.weather.precipitation?.type ?? 'rain';
        if (this._rainParticles) {
            this._rainParticles.visible = this.showRain && intensity > 0.05;
            this._rainParticles.material.opacity = 0.3 + intensity * 0.5;
            if (precipType === 'snow') {
                this._rainParticles.material.color.setHex(0xffffff);
                this._rainParticles.material.size = 0.12 + intensity * 0.15;
            } else if (precipType === 'mixed') {
                this._rainParticles.material.color.setHex(0xaabbdd);
                this._rainParticles.material.size = 0.08 + intensity * 0.1;
            } else {
                this._rainParticles.material.color.setHex(0x8899bb);
                this._rainParticles.material.size = 0.05 + intensity * 0.08;
            }
        }
    }

    _updateWindArrow() {
        if (!this._windArrow) return;
        const { speed, direction } = this.weather.wind;
        const rad = direction * DEG2RAD;
        const dir = new THREE.Vector3(-Math.sin(rad), 0, -Math.cos(rad));
        this._windArrow.setDirection(dir.normalize());
        this._windArrow.setLength(4 + speed * 0.4, 1.5, 1.0);
        this._windArrow.visible = this.showWind && speed > 0.5;
    }

    // ==================== 波浪参数联动 ====================

    getWaveAmplitude() {
        // 浪高 -> 波浪振幅 (scale factor)
        return Math.max(0.3, this.weather.wave.height * 0.8);
    }

    getWaveSpeed() {
        // 波周期 -> 波速
        const period = Math.max(this.weather.wave.period, 3);
        return 12.0 / period;
    }

    // ==================== 开关控制 ====================

    setEffectEnabled(effect, enabled) {
        const mapping = { precipitation: 'rain', wave: 'waves' };
        effect = mapping[effect] || effect;
        switch (effect) {
            case 'wind':
                this.showWind = enabled;
                if (this._windParticles) this._windParticles.visible = enabled;
                if (this._windArrow) this._windArrow.visible = enabled && this.weather.wind.speed > 0.5;
                break;
            case 'rain':
                this.showRain = enabled;
                this._applyRainVisibility();
                break;
            case 'fog':
                this.showFog = enabled;
                if (!enabled && this._originalFog) {
                    this.scene.fog = this._originalFog.clone();
                    this.scene.background = new THREE.Color(0x0b1525);
                } else if (enabled) {
                    this._applyFog();
                }
                break;
            case 'waves':
                this.showWaves = enabled;
                break;
        }
    }

    toggle(effect) {
        const mapping = { precipitation: 'rain', wave: 'waves' };
        effect = mapping[effect] || effect;
        switch (effect) {
            case 'wind': this.setEffectEnabled('wind', !this.showWind); break;
            case 'rain': this.setEffectEnabled('rain', !this.showRain); break;
            case 'fog': this.setEffectEnabled('fog', !this.showFog); break;
            case 'waves': this.setEffectEnabled('waves', !this.showWaves); break;
        }
    }

    // ==================== 获取当前状态 ====================

    getSnapshot() {
        return {
            weather: { ...this.weather },
            effects: {
                wind: this.showWind,
                rain: this.showRain,
                fog: this.showFog,
                waves: this.showWaves,
            },
        };
    }

    // ==================== 销毁 ====================

    dispose() {
        if (this._windParticles) {
            this.scene.remove(this._windParticles);
            this._windParticles.geometry.dispose();
            this._windParticles.material.dispose();
        }
        if (this._rainParticles) {
            this.scene.remove(this._rainParticles);
            this._rainParticles.geometry.dispose();
            this._rainParticles.material.dispose();
        }
        if (this._windArrow) {
            this.scene.remove(this._windArrow);
        }
    }
}
