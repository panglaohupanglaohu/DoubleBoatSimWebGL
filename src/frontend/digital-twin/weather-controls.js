/**
 * weather-controls.js — PoseidonX Weather & Wave UI Controller
 * Global script loaded via <script defer>
 */

/* ═══════════════════════════════════════════
   Weather Presets
   ═══════════════════════════════════════════ */

const WEATHER_PRESETS = {
    clear:        { windSpeed: 3,  windDir: 180, precipIntensity: 0,  precipType: 'none', temp: 22, visibility: 15,  label: '☀️ Clear' },
    cloudy:       { windSpeed: 6,  windDir: 200, precipIntensity: 0,  precipType: 'none', temp: 18, visibility: 12,  label: '☁️ Cloudy' },
    drizzle:      { windSpeed: 5,  windDir: 210, precipIntensity: 15, precipType: 'rain', temp: 14, visibility: 8,   label: '🌦️ Drizzle' },
    lightRain:    { windSpeed: 8,  windDir: 220, precipIntensity: 35, precipType: 'rain', temp: 12, visibility: 6,   label: '🌧️ Light Rain' },
    heavyRain:    { windSpeed: 15, windDir: 230, precipIntensity: 75, precipType: 'rain', temp: 10, visibility: 3,   label: '🌧️ Heavy Rain' },
    snow:         { windSpeed: 4,  windDir: 190, precipIntensity: 30, precipType: 'snow', temp: -2, visibility: 5,   label: '🌨️ Snow' },
    heavySnow:    { windSpeed: 8,  windDir: 200, precipIntensity: 70, precipType: 'snow', temp: -8, visibility: 2,   label: '❄️ Heavy Snow' },
    thunderstorm: { windSpeed: 25, windDir: 260, precipIntensity: 90, precipType: 'rain', temp: 16, visibility: 1.5, label: '⛈️ Thunderstorm' },
    fog:          { windSpeed: 2,  windDir: 180, precipIntensity: 0,  precipType: 'none', temp: 10, visibility: 0.8, label: '🌫️ Fog' },
    tropicalStorm:{ windSpeed: 35, windDir: 270, precipIntensity: 95, precipType: 'rain', temp: 26, visibility: 1,   label: '🌀 Tropical Storm' },
};

/* ═══════════════════════════════════════════
   Temperature Constraints
   ═══════════════════════════════════════════ */

const TEMP_CONSTRAINTS = {
    snow:          { min: -20, max: 2,  default: -2  },
    heavySnow:     { min: -20, max: 0,  default: -8  },
    heavyRain:     { min: 8,   max: 35, default: 10  },
    thunderstorm:  { min: 12,  max: 38, default: 16  },
    tropicalStorm: { min: 24,  max: 35, default: 26  },
};

/* ═══════════════════════════════════════════
   Helper Functions
   ═══════════════════════════════════════════ */

function getCompassLabel(deg) {
    const labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    return labels[Math.round(((deg % 360 + 360) % 360) / 45) % 8];
}

function getPrecipTypeForTemp(temp) {
    if (temp < 0)  return 'snow';
    if (temp < 2)  return 'snow';
    if (temp < 4)  return 'mixed';
    return 'rain';
}

function getPrecipTypeLabel(type) {
    switch (type) {
        case 'snow':  return '❄️ Snow';
        case 'mixed': return '🌧️❄️ Mixed';
        case 'rain':  return '🌧️ Rain';
        default:      return '—';
    }
}

function calcVisibility(baseVis, precipIntensity, windSpeed) {
    let vis = baseVis * (1 - (precipIntensity / 100) * 0.4);
    if (windSpeed > 20) vis *= (1 - (windSpeed - 20) / 40);
    return Math.max(0.3, Math.min(vis, 20));
}

/* ═══════════════════════════════════════════
   DOM Accessors (cached after DOMContentLoaded)
   ═══════════════════════════════════════════ */

var _els = {};

function el(id) {
    if (!_els[id]) _els[id] = document.getElementById(id);
    return _els[id];
}

/* ═══════════════════════════════════════════
   Current State
   ═══════════════════════════════════════════ */

var _currentPreset = 'clear';
var _currentTemp = 22;

/* ═══════════════════════════════════════════
   Visibility Indicator
   ═══════════════════════════════════════════ */

function getVisIndicator(vis) {
    if (vis < 1)  return '🔴 极差';
    if (vis < 3)  return '🟠 差';
    if (vis < 6)  return '🟡 一般';
    if (vis < 10) return '🟢 良好';
    return '🔵 优秀';
}

/* ═══════════════════════════════════════════
   Update Display Helpers
   ═══════════════════════════════════════════ */

function updateWindDisplay() {
    var speedEl = el('wx-wind-speed-slider');
    var dirEl   = el('wx-wind-dir-slider');
    var speed = speedEl ? parseFloat(speedEl.value) : 3;
    var dir   = dirEl ? parseFloat(dirEl.value) : 180;

    if (el('wx-wind-speed-value')) el('wx-wind-speed-value').textContent = speed.toFixed(1) + ' m/s';
    if (el('wx-wind-dir-value'))   el('wx-wind-dir-value').textContent = dir.toFixed(0) + '\u00b0';
    if (el('wx-wind-dir-compass')) el('wx-wind-dir-compass').textContent = getCompassLabel(dir);
}

function updatePrecipDisplay() {
    var slider = el('wx-precip-slider');
    var intensity = slider ? parseFloat(slider.value) : 0;
    if (el('wx-precip-value')) el('wx-precip-value').textContent = intensity.toFixed(0) + '%';
}

function updatePrecipType() {
    var slider = el('wx-precip-slider');
    var intensity = slider ? parseFloat(slider.value) : 0;
    var type;
    if (intensity === 0) {
        type = 'none';
    } else {
        type = getPrecipTypeForTemp(_currentTemp);
    }
    if (el('wx-precip-type')) el('wx-precip-type').textContent = getPrecipTypeLabel(type);
}

function updateTempDisplay() {
    if (el('wx-temp-value')) el('wx-temp-value').textContent = _currentTemp + '\u00b0C';
}

function updateVisibility() {
    var preset = WEATHER_PRESETS[_currentPreset];
    var baseVis = preset ? preset.visibility : 15;
    var precipSlider = el('wx-precip-slider');
    var windSlider = el('wx-wind-speed-slider');
    var precipIntensity = precipSlider ? parseFloat(precipSlider.value) : 0;
    var windSpeed = windSlider ? parseFloat(windSlider.value) : 3;
    var vis = calcVisibility(baseVis, precipIntensity, windSpeed);

    if (el('wx-vis-value'))     el('wx-vis-value').textContent = vis.toFixed(1) + ' km';
    if (el('wx-vis-indicator')) el('wx-vis-indicator').textContent = getVisIndicator(vis);
}

function updateTempConstraints(presetKey) {
    var constraint = TEMP_CONSTRAINTS[presetKey];
    if (constraint) {
        _currentTemp = Math.max(constraint.min, Math.min(constraint.max, _currentTemp));
        updateTempDisplay();
        if (el('wx-temp-dec')) el('wx-temp-dec').disabled = (_currentTemp <= constraint.min);
        if (el('wx-temp-inc')) el('wx-temp-inc').disabled = (_currentTemp >= constraint.max);
    } else {
        _currentTemp = Math.max(-20, Math.min(45, _currentTemp));
        updateTempDisplay();
        if (el('wx-temp-dec')) el('wx-temp-dec').disabled = (_currentTemp <= -20);
        if (el('wx-temp-inc')) el('wx-temp-inc').disabled = (_currentTemp >= 45);
    }
}

/* ═══════════════════════════════════════════
   Apply Weather To 3D Scene
   ═══════════════════════════════════════════ */

function applyWeatherToScene() {
    var windSlider = el('wx-wind-speed-slider');
    var dirSlider  = el('wx-wind-dir-slider');
    var precipSlider = el('wx-precip-slider');

    var windSpeed = windSlider ? parseFloat(windSlider.value) : 3;
    var windDir   = dirSlider ? parseFloat(dirSlider.value) : 180;
    var precipIntensity = precipSlider ? parseFloat(precipSlider.value) : 0;

    var precipType;
    if (precipIntensity === 0) {
        precipType = 'none';
    } else {
        precipType = getPrecipTypeForTemp(_currentTemp);
    }

    var visText = el('wx-vis-value') ? el('wx-vis-value').textContent : '15';
    var vis = parseFloat(visText.replace(' km', ''));

    var weatherData = {
        wind: {
            speed: windSpeed,
            direction: windDir,
        },
        precipitation: {
            intensity: precipIntensity / 100,
            type: precipType,
        },
        temperature: _currentTemp,
        visibility: vis,
        preset: _currentPreset,
    };

    var waveHSlider = el('wave-height-slider');
    var wavePSlider = el('wave-period-slider');
    var waveHeight = waveHSlider ? parseFloat(waveHSlider.value) : 1;
    var wavePeriod = wavePSlider ? parseFloat(wavePSlider.value) : 8;
    weatherData.wave = {
        height: waveHeight,
        period: wavePeriod,
    };

    if (window.DigitalTwin && window.DigitalTwin.weatherEffects) {
        window.DigitalTwin.weatherEffects.setWeather(weatherData);
    }

    var preset = WEATHER_PRESETS[_currentPreset];
    if (el('wx-status')) {
        el('wx-status').textContent = (preset ? preset.label : _currentPreset) +
            ' | ' + windSpeed.toFixed(1) + 'm/s ' + getCompassLabel(windDir) +
            ' | ' + vis.toFixed(1) + 'km';
    }
}

/* ═══════════════════════════════════════════
   Apply Preset
   ═══════════════════════════════════════════ */

function applyPreset(presetKey) {
    var preset = WEATHER_PRESETS[presetKey];
    if (!preset) return;

    _currentPreset = presetKey;
    _currentTemp = preset.temp;

    if (el('wx-wind-speed-slider')) el('wx-wind-speed-slider').value = preset.windSpeed;
    if (el('wx-wind-dir-slider'))   el('wx-wind-dir-slider').value = preset.windDir;
    updateWindDisplay();

    if (el('wx-precip-slider')) el('wx-precip-slider').value = preset.precipIntensity;
    updatePrecipDisplay();

    updateTempDisplay();
    updateTempConstraints(presetKey);
    updatePrecipType();
    updateVisibility();
    applyWeatherToScene();
}

/* ═══════════════════════════════════════════
   Effect Toggle Helper
   ═══════════════════════════════════════════ */

function setupToggle(btnId, effectName) {
    var btn = el(btnId);
    if (!btn) return;
    btn.addEventListener('click', function () {
        if (window.DigitalTwin && window.DigitalTwin.weatherEffects) {
            window.DigitalTwin.weatherEffects.toggle(effectName);
        }
        btn.classList.toggle('is-active');
        if (btn.classList.contains('is-active')) {
            btn.style.background = 'rgba(79,195,247,0.15)';
            btn.style.color = '#4fc3f7';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#888';
        }
    });
}

/* ═══════════════════════════════════════════
   Wave Display
   ═══════════════════════════════════════════ */

function updateWaveDisplay() {
    var hSlider = el('wave-height-slider');
    var pSlider = el('wave-period-slider');
    var height = hSlider ? parseFloat(hSlider.value) : 1;
    var period = pSlider ? parseFloat(pSlider.value) : 8;
    if (el('wave-height-value')) el('wave-height-value').textContent = height.toFixed(1) + ' m';
    if (el('wave-period-value')) el('wave-period-value').textContent = period.toFixed(1) + ' s';
}

/* ═══════════════════════════════════════════
   Periodic Sync from 3D Engine
   ═══════════════════════════════════════════ */

function syncFromEngine() {
    if (!(window.DigitalTwin && window.DigitalTwin.weatherEffects)) return;
    var w = window.DigitalTwin.weatherEffects.weather;
    if (!w) return;

    var windSpeed = w.wind ? w.wind.speed : undefined;
    var windDir   = w.wind ? w.wind.direction : undefined;
    var vis       = w.visibility;
    var temp      = w.temperature;
    var waveH     = w.wave ? w.wave.height : undefined;

    if (windSpeed != null && el('wx-wind-speed-value'))
        el('wx-wind-speed-value').textContent = windSpeed.toFixed(1) + ' m/s';
    if (windDir != null) {
        if (el('wx-wind-dir-value'))
            el('wx-wind-dir-value').textContent = windDir.toFixed(0) + '\u00b0';
        if (el('wx-wind-dir-compass'))
            el('wx-wind-dir-compass').textContent = getCompassLabel(windDir);
    }
    if (vis != null && el('wx-vis-value'))
        el('wx-vis-value').textContent = vis.toFixed(1) + ' km';
    if (temp != null && el('wx-temp-value'))
        el('wx-temp-value').textContent = temp.toFixed(0) + '\u00b0C';
    if (waveH != null && el('wave-height-value'))
        el('wave-height-value').textContent = waveH.toFixed(1) + ' m';
}

/* ═══════════════════════════════════════════
   Initialization
   ═══════════════════════════════════════════ */

function initWeatherControls() {
    _els = {};

    var typeSelect = el('wx-type-select');
    if (typeSelect) {
        if (typeSelect.options.length <= 1) {
            Object.keys(WEATHER_PRESETS).forEach(function (key) {
                var opt = document.createElement('option');
                opt.value = key;
                opt.textContent = WEATHER_PRESETS[key].label;
                typeSelect.appendChild(opt);
            });
        }
        typeSelect.addEventListener('change', function () {
            applyPreset(typeSelect.value);
        });
    }

    var windSpeedSlider = el('wx-wind-speed-slider');
    if (windSpeedSlider) {
        windSpeedSlider.min = 0;
        windSpeedSlider.max = 40;
        windSpeedSlider.step = 0.5;
        windSpeedSlider.addEventListener('input', function () {
            updateWindDisplay();
            updateVisibility();
            applyWeatherToScene();
        });
    }

    var windDirSlider = el('wx-wind-dir-slider');
    if (windDirSlider) {
        windDirSlider.min = 0;
        windDirSlider.max = 360;
        windDirSlider.step = 1;
        windDirSlider.addEventListener('input', function () {
            updateWindDisplay();
            applyWeatherToScene();
        });
    }

    var precipSlider = el('wx-precip-slider');
    if (precipSlider) {
        precipSlider.min = 0;
        precipSlider.max = 100;
        precipSlider.step = 1;
        precipSlider.addEventListener('input', function () {
            updatePrecipDisplay();
            updatePrecipType();
            updateVisibility();
            applyWeatherToScene();
        });
    }

    var tempDec = el('wx-temp-dec');
    var tempInc = el('wx-temp-inc');
    if (tempDec) {
        tempDec.addEventListener('click', function () {
            _currentTemp -= 1;
            updateTempConstraints(_currentPreset);
            updatePrecipType();
            applyWeatherToScene();
        });
    }
    if (tempInc) {
        tempInc.addEventListener('click', function () {
            _currentTemp += 1;
            updateTempConstraints(_currentPreset);
            updatePrecipType();
            applyWeatherToScene();
        });
    }

    setupToggle('wx-toggle-wind',   'wind');
    setupToggle('wx-toggle-precip', 'precipitation');
    setupToggle('wx-toggle-fog',    'fog');

    var waveHSlider = el('wave-height-slider');
    if (waveHSlider) {
        waveHSlider.min = 0;
        waveHSlider.max = 10;
        waveHSlider.step = 0.1;
        waveHSlider.addEventListener('input', function () {
            updateWaveDisplay();
            applyWeatherToScene();
        });
    }

    var wavePSlider = el('wave-period-slider');
    if (wavePSlider) {
        wavePSlider.min = 3;
        wavePSlider.max = 20;
        wavePSlider.step = 0.5;
        wavePSlider.addEventListener('input', function () {
            updateWaveDisplay();
            applyWeatherToScene();
        });
    }

    setupToggle('wave-toggle', 'wave');

    applyPreset('clear');

    setInterval(syncFromEngine, 3000);

    console.log('[PoseidonX] Weather controls initialized');
}

/* ═══════════════════════════════════════════
   Exports
   ═══════════════════════════════════════════ */

window.applyPreset = applyPreset;
window.applyWeatherToScene = applyWeatherToScene;
window.getCompassLabel = getCompassLabel;
window.calcVisibility = calcVisibility;

/* ═══════════════════════════════════════════
   Bootstrap
   ═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', initWeatherControls);
