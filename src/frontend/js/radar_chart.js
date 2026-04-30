/**
 * RadarChart.js — AR-CAS Pro 雷达图组件
 *
 * 基于 Canvas 的雷达图渲染组件，用于在 VR 菜单中显示
 * 双体船及货船相对本船的运动态势。
 *
 * 功能:
 * - 绘制方位圈、距离圈
 * - 显示目标点、船名、MMSI
 * - 显示运动矢量 (COG/SOG)
 * - 碰撞风险等级颜色标识
 * - 每 2 秒动态更新
 */
class RadarChart {
    /**
     * @param {string|HTMLElement} container - 容器元素 ID 或 DOM 元素
     * @param {Object} options - 配置选项
     * @param {number} options.maxRange - 最大显示距离（海里），默认 5
     * @param {number} options.rangeRingStep - 距离圈步长（海里），默认 1
     * @param {number} options.bearingStep - 方位线步长（度），默认 30
     */
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.getElementById(container)
            : container;

        if (!this.container) {
            throw new Error(`RadarChart: container not found`);
        }

        this.maxRange = options.maxRange || 5;
        this.rangeRingStep = options.rangeRingStep || 1;
        this.bearingStep = options.bearingStep || 30;

        // 创建 Canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.display = 'block';
        this.container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');

        // 尺寸
        this._resize();
        this._boundResize = this._resize.bind(this);
        window.addEventListener('resize', this._boundResize);

        // 数据
        this._data = null;
        this._animationId = null;
        this._sweepAngle = 0;
    }

    /**
     * 调整 Canvas 尺寸
     */
    _resize() {
        const rect = this.container.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.width = rect.width || 400;
        this.height = rect.height || 400;
        this.canvas.width = Math.floor(this.width * dpr);
        this.canvas.height = Math.floor(this.height * dpr);
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        // 中心点和缩放
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
        this.radius = Math.min(this.width, this.height) / 2 - 30;
        this.scale = this.radius / this.maxRange;
    }

    /**
     * 更新雷达图数据
     * @param {Object} data - { own_ship: {latitude, longitude}, targets: [...] }
     */
    updateData(data) {
        this._data = data;
    }

    /**
     * 开始动画循环
     */
    start() {
        if (this._animationId) return;
        const loop = () => {
            this._draw();
            this._sweepAngle = (this._sweepAngle + 0.02) % (Math.PI * 2);
            this._animationId = requestAnimationFrame(loop);
        };
        loop();
    }

    /**
     * 停止动画循环
     */
    stop() {
        if (this._animationId) {
            cancelAnimationFrame(this._animationId);
            this._animationId = null;
        }
    }

    /**
     * 销毁组件
     */
    destroy() {
        this.stop();
        window.removeEventListener('resize', this._boundResize);
        if (this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }

    // ==================== 绘制方法 ====================

    /**
     * 主绘制函数
     */
    _draw() {
        const ctx = this.ctx;
        const w = this.width;
        const h = this.height;

        // 清空
        ctx.clearRect(0, 0, w, h);

        // 背景
        ctx.fillStyle = 'rgba(4, 8, 16, 0.94)';
        ctx.fillRect(0, 0, w, h);

        // 绘制雷达背景
        this._drawBackground();

        // 绘制扫描线
        this._drawSweep();

        // 绘制目标
        if (this._data && this._data.targets) {
            this._data.targets.forEach(target => {
                this._drawTarget(target);
            });
        }

        // 绘制中心本船标记
        this._drawOwnShip();

        // 绘制图例
        this._drawLegend();
    }

    /**
     * 绘制背景（方位圈、距离圈、方位线）
     */
    _drawBackground() {
        const ctx = this.ctx;
        const cx = this.centerX;
        const cy = this.centerY;

        // 距离圈
        for (let r = this.rangeRingStep; r <= this.maxRange; r += this.rangeRingStep) {
            const px = r * this.scale;
            ctx.beginPath();
            ctx.arc(cx, cy, px, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(0, 255, 136, 0.25)';
            ctx.lineWidth = 0.5;
            ctx.stroke();

            // 距离标签
            ctx.fillStyle = 'rgba(0, 255, 136, 0.5)';
            ctx.font = '9px monospace';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(`${r} NM`, cx + px + 3, cy + 3);
        }

        // 方位线
        for (let deg = 0; deg < 360; deg += this.bearingStep) {
            const rad = (deg - 90) * Math.PI / 180;
            const ex = cx + Math.cos(rad) * this.radius;
            const ey = cy + Math.sin(rad) * this.radius;

            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(ex, ey);
            ctx.strokeStyle = 'rgba(0, 255, 136, 0.12)';
            ctx.lineWidth = 0.5;
            ctx.stroke();

            // 方位标签
            const labelR = this.radius + 14;
            const lx = cx + Math.cos(rad) * labelR;
            const ly = cy + Math.sin(rad) * labelR;
            ctx.fillStyle = 'rgba(0, 255, 136, 0.6)';
            ctx.font = '9px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`${deg}°`, lx, ly);
        }

        // 外圈
        ctx.beginPath();
        ctx.arc(cx, cy, this.radius, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
    }

    /**
     * 绘制雷达扫描线
     */
    _drawSweep() {
        const ctx = this.ctx;
        const cx = this.centerX;
        const cy = this.centerY;
        const angle = this._sweepAngle;

        // 扫描扇形
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, this.radius, angle - 0.3, angle);
        ctx.closePath();
        ctx.fillStyle = 'rgba(0, 255, 136, 0.04)';
        ctx.fill();

        // 扫描线
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(
            cx + Math.cos(angle) * this.radius,
            cy + Math.sin(angle) * this.radius
        );
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.5)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();
    }

    /**
     * 绘制本船标记
     */
    _drawOwnShip() {
        const ctx = this.ctx;
        const cx = this.centerX;
        const cy = this.centerY;

        // 中心光晕
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 20);
        grad.addColorStop(0, 'rgba(0, 255, 136, 0.6)');
        grad.addColorStop(1, 'rgba(0, 255, 136, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, 20, 0, Math.PI * 2);
        ctx.fill();

        // 中心点
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00ff88';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();

        // 本船标签
        ctx.fillStyle = 'rgba(0, 255, 136, 0.8)';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText('本船', cx, cy - 10);
    }

    /**
     * 绘制单个目标
     * @param {Object} target - 目标数据
     */
    _drawTarget(target) {
        const ctx = this.ctx;
        const cx = this.centerX;
        const cy = this.centerY;

        const bearingRad = (target.bearing - 90) * Math.PI / 180;
        const rangePx = target.range * this.scale;

        // 如果超出显示范围，在边缘显示
        const displayRange = Math.min(rangePx, this.radius - 20);
        const x = cx + Math.cos(bearingRad) * displayRange;
        const y = cy + Math.sin(bearingRad) * displayRange;

        // 风险等级颜色
        let color, glowColor;
        switch (target.risk_level) {
            case 'high':
                color = '#f56565';
                glowColor = 'rgba(245,101,101,0.3)';
                break;
            case 'medium':
                color = '#f6ad55';
                glowColor = 'rgba(246,173,85,0.3)';
                break;
            default:
                color = '#48bb78';
                glowColor = 'rgba(72,187,120,0.3)';
        }

        // 目标光晕
        const grad = ctx.createRadialGradient(x, y, 0, x, y, 18);
        grad.addColorStop(0, glowColor);
        grad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, 18, 0, Math.PI * 2);
        ctx.fill();

        // 目标点
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // 目标标签（船名 + MMSI）
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        const label = `${target.ship_name || 'Unknown'} (${target.mmsi})`;
        ctx.fillText(label, x + 12, y - 8);

        // COG/SOG 信息
        ctx.fillStyle = 'rgba(255,255,255,0.7)';
        ctx.font = '9px monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`COG ${target.cog}°  SOG ${target.sog}kn`, x + 12, y + 2);

        // 运动矢量（沿 COG 方向）
        const cogRad = (target.cog - 90) * Math.PI / 180;
        const vectorLen = Math.max(15, target.sog * 2.5);
        const vx = x + Math.cos(cogRad) * vectorLen;
        const vy = y + Math.sin(cogRad) * vectorLen;

        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(vx, vy);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();

        // 矢量箭头
        const arrowSize = 6;
        const arrowAngle = Math.PI / 6;
        ctx.beginPath();
        ctx.moveTo(vx, vy);
        ctx.lineTo(
            vx - Math.cos(cogRad - arrowAngle) * arrowSize,
            vy - Math.sin(cogRad - arrowAngle) * arrowSize
        );
        ctx.moveTo(vx, vy);
        ctx.lineTo(
            vx - Math.cos(cogRad + arrowAngle) * arrowSize,
            vy - Math.sin(cogRad + arrowAngle) * arrowSize
        );
        ctx.stroke();

        // 如果超出范围，在边缘显示指示
        if (rangePx > this.radius) {
            ctx.fillStyle = color;
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('↗', x, y);
        }

        // 方位距离标注
        const infoY = y + 22;
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.font = '8px monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`方位 ${target.bearing}°  距离 ${target.range} NM`, x + 12, infoY);
    }

    /**
     * 绘制图例
     */
    _drawLegend() {
        const ctx = this.ctx;
        const x = 10;
        let y = this.height - 60;

        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(x, y, 120, 50);
        ctx.strokeStyle = 'rgba(0,255,136,0.2)';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, 120, 50);

        y += 8;
        const items = [
            { color: '#48bb78', label: '低风险' },
            { color: '#f6ad55', label: '中风险' },
            { color: '#f56565', label: '高风险' },
        ];

        items.forEach(item => {
            ctx.beginPath();
            ctx.arc(x + 12, y + 5, 4, 0, Math.PI * 2);
            ctx.fillStyle = item.color;
            ctx.fill();

            ctx.fillStyle = 'rgba(255,255,255,0.7)';
            ctx.font = '9px sans-serif';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(item.label, x + 22, y + 5);
            y += 14;
        });
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RadarChart;
}
