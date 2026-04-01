/**
 * AgentTeamMonitor.js — 双智能体团队实时监控面板
 *
 * 展示构建团队 (Build Team) 和执行团队 (Execution Team) 的
 * 实时状态、KPI 指标、调度信息和反馈流。
 *
 * 与后端 /api/v1/agent-teams/* 端点通信。
 */

const API_BASE = '/api/v1/agent-teams';

export class AgentTeamMonitor {
  constructor(container, options = {}) {
    this.container = typeof container === 'string'
      ? document.getElementById(container)
      : container;
    this.options = {
      refreshInterval: options.refreshInterval || 5000,
      apiBase: options.apiBase || API_BASE,
    };
    this._timer = null;
    this._data = { build: null, execution: null, scheduler: null };
  }

  // ── Lifecycle ─────────────────────────────────────────────

  start() {
    this._render();
    this._poll();
    this._timer = setInterval(() => this._poll(), this.options.refreshInterval);
  }

  stop() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
  }

  // ── Data Fetching ─────────────────────────────────────────

  async _poll() {
    try {
      const [overview, buildKPIs] = await Promise.all([
        this._fetch('/overview'),
        this._fetch('/build/kpis'),
      ]);
      this._data.overview = overview;
      this._data.buildKPIs = buildKPIs;
      this._update();
    } catch (err) {
      console.warn('[AgentTeamMonitor] Poll error:', err.message);
    }
  }

  async _fetch(path) {
    const res = await fetch(`${this.options.apiBase}${path}`);
    if (!res.ok) return null;
    return res.json();
  }

  async triggerTick() {
    return this._fetch('/scheduler/tick');
  }

  async generateReport() {
    const res = await fetch(`${this.options.apiBase}/scheduler/report`, { method: 'POST' });
    return res.json();
  }

  // ── Rendering ─────────────────────────────────────────────

  _render() {
    if (!this.container) return;
    this.container.innerHTML = `
      <div class="agent-team-monitor" style="font-family:Inter,system-ui,sans-serif;color:#e0e0e0;padding:12px;">
        <h2 style="margin:0 0 12px;font-size:16px;color:#4fc3f7;">
          ⚓ 双智能体团队监控
        </h2>

        <!-- Scheduler Bar -->
        <div id="atm-scheduler" class="atm-card" style="margin-bottom:10px;padding:8px 12px;
             background:#1a2332;border-radius:6px;display:flex;justify-content:space-between;align-items:center;">
          <span id="atm-sched-status" style="font-size:13px;">调度器: 加载中...</span>
          <div>
            <button id="atm-btn-tick" style="margin-right:6px;padding:4px 10px;font-size:12px;
                    background:#37474f;border:1px solid #546e7a;color:#e0e0e0;border-radius:4px;cursor:pointer;">
              ▶ Tick
            </button>
            <button id="atm-btn-report" style="padding:4px 10px;font-size:12px;
                    background:#37474f;border:1px solid #546e7a;color:#e0e0e0;border-radius:4px;cursor:pointer;">
              📊 报告
            </button>
          </div>
        </div>

        <!-- Two‑column layout -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">

          <!-- Build Team -->
          <div class="atm-card" style="background:#1a2332;border-radius:6px;padding:10px;">
            <h3 style="margin:0 0 8px;font-size:14px;color:#81c784;">
              🏗️ 构建团队 <small style="color:#aaa;font-weight:normal;">(Copilot)</small>
            </h3>
            <div id="atm-build-metrics" style="font-size:12px;margin-bottom:8px;"></div>
            <table id="atm-build-agents" style="width:100%;font-size:11px;border-collapse:collapse;"></table>
          </div>

          <!-- Execution Team -->
          <div class="atm-card" style="background:#1a2332;border-radius:6px;padding:10px;">
            <h3 style="margin:0 0 8px;font-size:14px;color:#ce93d8;">
              ⚡ 执行团队 <small style="color:#aaa;font-weight:normal;">(DeepSeek)</small>
            </h3>
            <div id="atm-exec-metrics" style="font-size:12px;margin-bottom:8px;"></div>
            <table id="atm-exec-agents" style="width:100%;font-size:11px;border-collapse:collapse;"></table>
          </div>
        </div>
      </div>
    `;

    // Wire buttons
    const btnTick = this.container.querySelector('#atm-btn-tick');
    const btnReport = this.container.querySelector('#atm-btn-report');
    if (btnTick) btnTick.addEventListener('click', () => this.triggerTick().then(() => this._poll()));
    if (btnReport) btnReport.addEventListener('click', () => this.generateReport().then(() => this._poll()));
  }

  _update() {
    const ov = this._data.overview;
    if (!ov) return;

    // Scheduler
    const schedEl = this.container.querySelector('#atm-sched-status');
    if (schedEl && ov.scheduler) {
      const s = ov.scheduler;
      schedEl.textContent = `调度器: ${s.running ? '运行中' : '已停止'} | Tick #${s.tick_count} | 报告: ${s.reports_generated}`;
    }

    // Build Team
    if (ov.build_team) {
      const m = ov.build_team.metrics;
      const metricsEl = this.container.querySelector('#atm-build-metrics');
      if (metricsEl) {
        metricsEl.innerHTML = `
          代码: <b>${m.total_code_lines}</b> 行 &nbsp;|&nbsp;
          测试: <b>${m.total_test_cases}</b> 例 &nbsp;|&nbsp;
          部署: <b>${m.total_deployments}</b> 次 (${(m.deployment_success_rate * 100).toFixed(0)}%) &nbsp;|&nbsp;
          问题: <b>${m.issues_backlog}</b>
        `;
      }
    }

    // Build Team Agent Table
    if (this._data.buildKPIs) {
      const tbl = this.container.querySelector('#atm-build-agents');
      if (tbl) {
        tbl.innerHTML = this._agentKPITable(this._data.buildKPIs);
      }
    }

    // Execution Team
    if (ov.execution_team) {
      const m = ov.execution_team.metrics;
      const metricsEl = this.container.querySelector('#atm-exec-metrics');
      if (metricsEl) {
        metricsEl.innerHTML = `
          感知: <b>${m.total_perception_events}</b> 事件 &nbsp;|&nbsp;
          决策: <b>${m.total_decisions}</b> 次 &nbsp;|&nbsp;
          纠偏: <b>${m.total_nav_corrections}</b> &nbsp;|&nbsp;
          节能: <b>${m.energy_savings_pct}%</b> &nbsp;|&nbsp;
          异常: <b>${m.total_anomalies}</b>
        `;
      }
    }
  }

  _agentKPITable(kpis) {
    const stateColors = {
      idle: '#78909c', working: '#4fc3f7', reporting: '#81c784',
      blocked: '#ffb74d', error: '#ef5350',
    };
    let html = `<tr style="border-bottom:1px solid #333;">
      <th style="text-align:left;padding:3px;">Agent</th>
      <th>状态</th><th>完成</th><th>产出</th><th>分数</th>
    </tr>`;
    for (const [id, kpi] of Object.entries(kpis)) {
      const color = stateColors[kpi.state] || '#aaa';
      html += `<tr style="border-bottom:1px solid #222;">
        <td style="padding:3px;">${kpi.name || id}</td>
        <td style="text-align:center;color:${color};">${kpi.state}</td>
        <td style="text-align:center;">${kpi.tasks_completed}</td>
        <td style="text-align:center;">${kpi.deliverables}</td>
        <td style="text-align:center;">${kpi.score}</td>
      </tr>`;
    }
    return html;
  }
}

export default AgentTeamMonitor;
