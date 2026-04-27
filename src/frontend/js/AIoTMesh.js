/**
 * AIoT Mesh Panel — BIOS + LoRA + MC-RFID + 带外通信 (OOB) 关联视图
 *
 * 与后端 /api/v1/aiot-mesh/* 对接, 展示三大关联 + 自学习规则 + Mesh 图.
 *
 * 三大关联:
 *   1) MC-RFID × LoRA    — 资产位置与环境参数匹配 (余弦相似度+阈值)
 *   2) MC-RFID × OOB     — 带外指令定位故障资产 (标签匹配)
 *   3) LoRA   × OOB      — 环境异常→优先级调度→自动调控 (孤立森林式)
 */

(function () {
  const API = '/api/v1/aiot-mesh';
  const KIND_COLORS = {
    bios: '#22d3ee',
    rfid: '#f59e0b',
    lora: '#86efac',
    oob:  '#f472b6',
  };
  const EDGE_COLORS = {
    bios_rfid: 'rgba(148,163,184,0.55)',
    rfid_lora: '#fbbf24',
    rfid_oob:  '#f472b6',
    lora_oob:  '#34d399',
  };

  let panelEl = null;
  let activeTab = 'overview';
  let cache = null;
  let refreshTimer = null;

  // ── Public API ──
  window.AIoTMeshPanel = {
    open: openPanel,
    close: closePanel,
    refresh: refresh,
  };

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('aiot-mesh-open');
    if (btn) btn.addEventListener('click', openPanel);
  });

  function openPanel() {
    if (!panelEl) buildPanel();
    panelEl.style.display = 'flex';
    refresh();
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(refresh, 15000);
  }

  function closePanel() {
    if (panelEl) panelEl.style.display = 'none';
    if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; }
  }

  async function refresh() {
    try {
      const r = await fetch(`${API}/overview`);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      cache = await r.json();
      render();
    } catch (e) {
      const body = document.getElementById('aiot-mesh-body');
      if (body) body.innerHTML =
        `<div style="padding:40px;text-align:center;color:#f87171;">
           <div style="font-size:36px;">⚠️</div>
           <div style="margin-top:10px;">无法加载 AIoT Mesh 数据</div>
           <div style="margin-top:6px;font-size:11px;opacity:0.7;">${e.message}</div>
           <div style="margin-top:12px;font-size:11px;opacity:0.7;">请确认后端已启动并注册 aiot_mesh channel</div>
         </div>`;
    }
  }

  // ── UI ──
  function buildPanel() {
    panelEl = document.createElement('div');
    panelEl.id = 'aiot-mesh-panel';
    panelEl.style.cssText = `
      display:none;position:fixed;inset:0;z-index:9999;
      background:rgba(2,8,20,0.92);backdrop-filter:blur(8px);
      flex-direction:column;color:#e5edf5;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",monospace;
    `;
    panelEl.innerHTML = `
      <div style="flex:0 0 auto;display:flex;align-items:center;gap:14px;
                  padding:14px 22px;background:rgba(8,18,35,0.95);
                  border-bottom:1px solid rgba(56,189,248,0.35);">
        <div style="font-size:18px;font-weight:700;color:#7dd3fc;letter-spacing:1px;">
          🕸️ AIoT Mesh
        </div>
        <div style="font-size:11px;color:#94a3b8;">
          BIOS · LoRA · MC-RFID · 带外通信 — 特征匹配 + 关联规则挖掘
        </div>
        <div id="aiot-mesh-summary" style="margin-left:auto;display:flex;gap:14px;
             font-size:11px;font-family:monospace;color:#cbd5e1;"></div>
        <button id="aiot-mesh-refresh" title="刷新" style="background:transparent;border:1px solid rgba(56,189,248,0.5);
                color:#7dd3fc;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:12px;">
          ⟲ 刷新
        </button>
        <button id="aiot-mesh-close" style="background:transparent;border:1px solid rgba(239,68,68,0.5);
                color:#fca5a5;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:12px;">
          ✕ 关闭
        </button>
      </div>
      <div style="flex:0 0 auto;display:flex;gap:6px;padding:10px 22px;
                  background:rgba(3,10,20,0.7);border-bottom:1px solid rgba(56,189,248,0.18);">
        ${tabButton('overview',  '🧭 概览')}
        ${tabButton('rfid_lora', '🌡️ RFID ↔ LoRA')}
        ${tabButton('rfid_oob',  '🏷️ RFID ↔ 带外')}
        ${tabButton('lora_oob',  '🚨 LoRA ↔ 带外')}
        ${tabButton('rules',     '🧠 自学习规则')}
        ${tabButton('graph',     '🕸️ Mesh 图')}
      </div>
      <div id="aiot-mesh-body" style="flex:1 1 auto;overflow:auto;padding:18px 22px;"></div>
    `;
    document.body.appendChild(panelEl);
    panelEl.querySelector('#aiot-mesh-close').addEventListener('click', closePanel);
    panelEl.querySelector('#aiot-mesh-refresh').addEventListener('click', refresh);
    panelEl.addEventListener('click', (e) => {
      const tab = e.target.closest('[data-aiot-tab]');
      if (tab) { activeTab = tab.dataset.aiotTab; render(); }
      const rbtn = e.target.closest('[data-rule-reinforce]');
      if (rbtn) {
        const id = rbtn.dataset.ruleReinforce;
        const ok = rbtn.dataset.ok === '1';
        reinforceRule(id, ok);
      }
    });
    document.addEventListener('keydown', (e) => {
      if (panelEl.style.display !== 'none' && e.key === 'Escape') closePanel();
    });
  }

  function tabButton(key, label) {
    return `<button data-aiot-tab="${key}" style="background:transparent;
      border:1px solid rgba(56,189,248,0.25);color:#cbd5e1;padding:6px 12px;
      border-radius:6px;cursor:pointer;font-size:12px;font-family:inherit;">
      ${label}
    </button>`;
  }

  function render() {
    if (!cache) return;
    // summary
    const s = cache.summary || {};
    const sumEl = document.getElementById('aiot-mesh-summary');
    if (sumEl) {
      sumEl.innerHTML = `
        <span>BIOS <b style="color:${KIND_COLORS.bios}">${s.bios}</b></span>
        <span>LoRA <b style="color:${KIND_COLORS.lora}">${s.lora}</b></span>
        <span>RFID <b style="color:${KIND_COLORS.rfid}">${s.rfid}</b></span>
        <span>OOB <b style="color:${KIND_COLORS.oob}">${s.oob_queue}</b></span>
        <span>规则 <b style="color:#a78bfa">${s.rules_learned}</b> · 置信度 ${s.avg_confidence}</span>
      `;
    }
    // highlight active tab
    panelEl.querySelectorAll('[data-aiot-tab]').forEach(b => {
      if (b.dataset.aiotTab === activeTab) {
        b.style.background = 'rgba(56,189,248,0.2)';
        b.style.borderColor = 'rgba(56,189,248,0.8)';
        b.style.color = '#7dd3fc';
      } else {
        b.style.background = 'transparent';
        b.style.borderColor = 'rgba(56,189,248,0.25)';
        b.style.color = '#cbd5e1';
      }
    });

    const body = document.getElementById('aiot-mesh-body');
    switch (activeTab) {
      case 'overview':  body.innerHTML = renderOverview(); break;
      case 'rfid_lora': body.innerHTML = renderRFIDLoRA(cache.rfid_lora || []); break;
      case 'rfid_oob':  body.innerHTML = renderRFIDOOB(cache.rfid_oob || []); break;
      case 'lora_oob':  body.innerHTML = renderLoRAOOB(cache.lora_oob || []); break;
      case 'rules':     renderRules(body); break;
      case 'graph':     renderGraph(body, cache.graph || {nodes:[],edges:[]}); break;
    }
  }

  function renderOverview() {
    const s = cache.summary || {};
    const card = (title, value, sub, color) =>
      `<div style="flex:1;min-width:200px;background:rgba(10,22,38,0.9);
        border:1px solid rgba(56,189,248,0.25);border-radius:10px;padding:14px 16px;">
        <div style="font-size:11px;color:#94a3b8;letter-spacing:1px;">${title}</div>
        <div style="font-size:28px;font-weight:700;color:${color};margin-top:4px;">${value}</div>
        <div style="font-size:11px;color:#64748b;margin-top:4px;">${sub}</div>
      </div>`;

    const kb = (title, desc, accent) =>
      `<div style="background:rgba(10,22,38,0.75);border-left:3px solid ${accent};
        border-radius:6px;padding:10px 14px;margin-bottom:10px;">
        <div style="font-size:13px;font-weight:600;color:#e2e8f0;">${title}</div>
        <div style="font-size:11px;color:#94a3b8;margin-top:4px;line-height:1.55;">${desc}</div>
      </div>`;

    return `
      <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px;">
        ${card('RFID ↔ LoRA 边', s.edges_rfid_lora, '资产 × 环境 匹配', '#fbbf24')}
        ${card('RFID ↔ OOB 边', s.edges_rfid_oob, '指令 × 资产 定位', '#f472b6')}
        ${card('LoRA ↔ OOB 边', s.edges_lora_oob, '异常 × 优先级 调度', '#34d399')}
        ${card('学习规则', s.rules_learned, `平均置信度 ${s.avg_confidence}`, '#a78bfa')}
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div>
          <h3 style="color:#7dd3fc;margin:0 0 12px 0;font-size:14px;">三大关联算法</h3>
          ${kb('① MC-RFID × LoRA — 资产-环境关联',
               '余弦相似度匹配资产空间特征与环境参数, 结合阈值模型判断是否超出存储/工作要求; 通过材质/服役年限量化影响程度, 为预警提供可量化依据.',
               '#fbbf24')}
          ${kb('② MC-RFID × 带外通信 — 指令-资产关联',
               '从 OOB 指令中提取故障类型/关联设备特征, 与 RFID 标签匹配, 快速锁定故障资产坐标, 自动关联型号/使用年限生成处置辅助信息.',
               '#f472b6')}
          ${kb('③ LoRA × 带外通信 — 异常-调控关联',
               '对 LoRA 采集的气体/温度序列做孤立森林式异常检测, 按严重程度自动提升 OOB 通道优先级, 同步下发新风/电源调控指令, 实现闭环处置.',
               '#34d399')}
        </div>
        <div>
          <h3 style="color:#7dd3fc;margin:0 0 12px 0;font-size:14px;">Mesh 自学习</h3>
          <div style="background:rgba(10,22,38,0.9);border:1px solid rgba(167,139,250,0.3);
                      border-radius:10px;padding:16px;font-size:12px;line-height:1.7;color:#cbd5e1;">
            关联过程中, 每条 (左 ⇌ 右) 关联自动写入 <code style="color:#a78bfa">association_rules</code>,
            记录特征 (距离 / 余弦 / 异常 Z-score / 标签得分) 与成功/失败次数.
            使用贝叶斯平滑计算置信度 <code>C = (s+1)/(s+f+2)</code>,
            随着数据积累持续优化, 减少误差.
            可在 <b>自学习规则</b> 页面手动反馈 ✓/✗ 强化或抑制规则.
          </div>
          <div style="background:rgba(10,22,38,0.9);border:1px solid rgba(56,189,248,0.25);
                      border-radius:10px;padding:14px 16px;margin-top:14px;font-size:12px;">
            <div style="color:#94a3b8;margin-bottom:8px;">当前 Mesh 状态</div>
            <div style="color:#e2e8f0;line-height:1.9;">
              ● BIOS 板卡: <b style="color:${KIND_COLORS.bios}">${s.bios}</b> 台<br>
              ● LoRA 环境节点: <b style="color:${KIND_COLORS.lora}">${s.lora}</b> 个<br>
              ● MC-RFID 资产: <b style="color:${KIND_COLORS.rfid}">${s.rfid}</b> 枚标签<br>
              ● OOB 指令队列: <b style="color:${KIND_COLORS.oob}">${s.oob_queue}</b> 条
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function renderRFIDLoRA(items) {
    if (!items.length) return emptyState('暂无 RFID ↔ LoRA 关联');
    const rows = items.map(r => `
      <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
        <td style="padding:8px 10px;color:${KIND_COLORS.rfid};">${r.tag_id}</td>
        <td style="padding:8px 10px;">${r.asset_type}</td>
        <td style="padding:8px 10px;color:${KIND_COLORS.lora};">${r.sensor_id}</td>
        <td style="padding:8px 10px;text-align:right;">${r.distance_m} m</td>
        <td style="padding:8px 10px;">
          🌡 ${r.environment.temp_c}°C · 💧 ${r.environment.rh_pct}% · 🧪 ${r.environment.gas_ppm}ppm ${r.environment.gas_species}
        </td>
        <td style="padding:8px 10px;color:${r.breaches.length ? '#f87171' : '#86efac'};">
          ${r.breaches.length ? '⚠ ' + r.breaches.join(' · ') : '✓ 正常'}
        </td>
        <td style="padding:8px 10px;text-align:right;">
          <span style="color:${impactColor(r.impact)};font-weight:600;">${(r.impact*100).toFixed(0)}%</span>
        </td>
        <td style="padding:8px 10px;text-align:right;color:#a78bfa;">${(r.confidence*100).toFixed(0)}%</td>
      </tr>`).join('');
    return tableWrap(
      `<tr><th>RFID 标签</th><th>资产类型</th><th>LoRA 传感器</th><th>距离</th><th>环境</th><th>阈值判断</th><th>影响</th><th>置信度</th></tr>`,
      rows);
  }

  function renderRFIDOOB(items) {
    if (!items.length) return emptyState('暂无 RFID ↔ OOB 关联');
    const rows = items.map(r => `
      <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
        <td style="padding:8px 10px;color:${KIND_COLORS.oob};font-size:11px;">${r.cmd_id}</td>
        <td style="padding:8px 10px;"><span style="background:${priorityBg(r.priority)};
            color:#fff;padding:2px 7px;border-radius:4px;font-size:10px;">P${r.priority} · ${r.cmd_kind}</span></td>
        <td style="padding:8px 10px;color:${KIND_COLORS.rfid};">${r.tag_id}</td>
        <td style="padding:8px 10px;">${r.asset_type} · ${r.model}</td>
        <td style="padding:8px 10px;font-family:monospace;font-size:11px;color:#94a3b8;">
          ${r.zone} · (${r.position.map(n=>n.toFixed(1)).join(', ')})
        </td>
        <td style="padding:8px 10px;color:#cbd5e1;">${r.handling_hint}</td>
        <td style="padding:8px 10px;text-align:right;color:#a78bfa;">${(r.confidence*100).toFixed(0)}%</td>
      </tr>`).join('');
    return tableWrap(
      `<tr><th>OOB 指令</th><th>优先级/类型</th><th>RFID</th><th>资产</th><th>位置</th><th>处置辅助</th><th>置信度</th></tr>`,
      rows);
  }

  function renderLoRAOOB(items) {
    if (!items.length) return emptyState('暂无 LoRA ↔ OOB 关联 (环境未触发异常)');
    const rows = items.map(r => `
      <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
        <td style="padding:8px 10px;color:${KIND_COLORS.lora};">${r.sensor_id}</td>
        <td style="padding:8px 10px;">${r.zone}</td>
        <td style="padding:8px 10px;">
          🧪 ${r.gas_ppm} ppm ${r.gas_species} · 🌡 ${r.temperature_c}°C
        </td>
        <td style="padding:8px 10px;color:#fbbf24;font-family:monospace;">Z=${r.anomaly_z}</td>
        <td style="padding:8px 10px;">
          <span style="background:${severityBg(r.severity)};color:#fff;
                 padding:2px 8px;border-radius:4px;font-size:10px;">${r.severity.toUpperCase()}</span>
        </td>
        <td style="padding:8px 10px;color:${KIND_COLORS.oob};font-size:11px;">${r.emit_cmd}</td>
        <td style="padding:8px 10px;font-family:monospace;font-size:11px;color:#86efac;">${r.routed_channel}</td>
        <td style="padding:8px 10px;color:#cbd5e1;">${(r.actions||[]).map(a=>'• '+a).join('<br>')}</td>
      </tr>`).join('');
    return tableWrap(
      `<tr><th>LoRA 传感器</th><th>区域</th><th>读数</th><th>异常分</th><th>等级</th><th>OOB 指令</th><th>路由</th><th>自动调控</th></tr>`,
      rows);
  }

  async function renderRules(body) {
    body.innerHTML = '<div style="padding:40px;text-align:center;color:#64748b;">⟲ 加载中…</div>';
    try {
      const r = await fetch(`${API}/rules`);
      const { rules } = await r.json();
      if (!rules.length) { body.innerHTML = emptyState('暂无学习规则'); return; }
      const rows = rules.map(rule => `
        <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
          <td style="padding:8px 10px;"><span style="background:${ruleKindBg(rule.kind)};
               color:#fff;padding:2px 8px;border-radius:4px;font-size:10px;">${rule.kind}</span></td>
          <td style="padding:8px 10px;font-family:monospace;font-size:11px;">${rule.left}</td>
          <td style="padding:8px 10px;color:#94a3b8;">↔</td>
          <td style="padding:8px 10px;font-family:monospace;font-size:11px;">${rule.right}</td>
          <td style="padding:8px 10px;font-family:monospace;font-size:10px;color:#94a3b8;">
            ${Object.entries(rule.features||{}).map(([k,v])=>`${k}=${v}`).join(' · ')}
          </td>
          <td style="padding:8px 10px;text-align:right;color:#86efac;">${rule.success}</td>
          <td style="padding:8px 10px;text-align:right;color:#f87171;">${rule.fail}</td>
          <td style="padding:8px 10px;text-align:right;color:${confColor(rule.confidence)};font-weight:600;">
            ${(rule.confidence*100).toFixed(0)}%
          </td>
          <td style="padding:8px 10px;text-align:right;white-space:nowrap;">
            <button data-rule-reinforce="${rule.rule_id}" data-ok="1"
              style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.5);
              color:#86efac;border-radius:4px;padding:3px 9px;cursor:pointer;font-size:11px;">✓</button>
            <button data-rule-reinforce="${rule.rule_id}" data-ok="0"
              style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.5);
              color:#fca5a5;border-radius:4px;padding:3px 9px;cursor:pointer;font-size:11px;margin-left:4px;">✗</button>
          </td>
        </tr>`).join('');
      body.innerHTML = tableWrap(
        `<tr><th>类型</th><th>左节点</th><th></th><th>右节点</th><th>特征</th><th>✓</th><th>✗</th><th>置信度</th><th>反馈</th></tr>`,
        rows);
    } catch (e) {
      body.innerHTML = `<div style="color:#f87171;padding:40px;text-align:center;">加载规则失败: ${e.message}</div>`;
    }
  }

  async function reinforceRule(id, ok) {
    try {
      await fetch(`${API}/rules/${encodeURIComponent(id)}/reinforce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ success: !!ok }),
      });
      if (activeTab === 'rules') renderRules(document.getElementById('aiot-mesh-body'));
      refresh();
    } catch (e) {
      console.warn('reinforce failed', e);
    }
  }

  // ── Mesh graph (pure SVG) ──
  function renderGraph(body, graph) {
    const W = body.clientWidth - 12, H = Math.max(520, body.clientHeight - 12);
    const nodes = graph.nodes || [];
    const edges = graph.edges || [];
    if (!nodes.length) { body.innerHTML = emptyState('Mesh 图为空'); return; }

    // 以 kind 分层: bios(上) / rfid(中上) / lora(中下) / oob(下)
    const lanes = { bios: 0.18, rfid: 0.40, lora: 0.64, oob: 0.86 };
    const byKind = { bios: [], rfid: [], lora: [], oob: [] };
    nodes.forEach(n => (byKind[n.kind] || (byKind[n.kind]=[])).push(n));
    const pos = {};
    Object.entries(byKind).forEach(([kind, list]) => {
      list.forEach((n, i) => {
        const x = 60 + (W - 120) * ((i + 0.5) / Math.max(list.length, 1));
        const y = H * (lanes[kind] ?? 0.5);
        pos[n.id] = { x, y };
      });
    });

    const defs = `
      <defs>
        ${Object.entries(EDGE_COLORS).map(([k,c]) =>
          `<marker id="arr-${k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">
             <path d="M0,0 L10,5 L0,10 Z" fill="${c}"/>
           </marker>`).join('')}
      </defs>`;

    const edgeSvg = edges.map(e => {
      const a = pos[e.source], b = pos[e.target];
      if (!a || !b) return '';
      const c = EDGE_COLORS[e.kind] || '#94a3b8';
      const w = 1 + (e.weight || 0.5) * 2.5;
      const op = 0.35 + (e.weight || 0.5) * 0.55;
      const dash = e.kind === 'bios_rfid' ? '3,3' : '';
      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"
                    stroke="${c}" stroke-width="${w}" stroke-opacity="${op}"
                    stroke-dasharray="${dash}"
                    marker-end="url(#arr-${e.kind})"/>`;
    }).join('');

    const nodeSvg = nodes.map(n => {
      const p = pos[n.id]; if (!p) return '';
      const c = KIND_COLORS[n.kind] || '#fff';
      const label = (n.label || n.id).slice(-16);
      return `
        <g transform="translate(${p.x},${p.y})">
          <circle r="10" fill="${c}" fill-opacity="0.25" stroke="${c}" stroke-width="1.5"/>
          <text y="22" text-anchor="middle" font-size="9" fill="#cbd5e1"
                font-family="monospace">${label}</text>
        </g>`;
    }).join('');

    const legend = Object.entries(KIND_COLORS).map(([k,c],i) =>
      `<g transform="translate(${20 + i*110},22)">
         <circle r="6" fill="${c}" fill-opacity="0.3" stroke="${c}"/>
         <text x="12" y="4" fill="#cbd5e1" font-size="11" font-family="monospace">${k.toUpperCase()}</text>
       </g>`).join('');
    const edgeLegend = Object.entries(EDGE_COLORS).map(([k,c],i) =>
      `<g transform="translate(${20 + i*140},46)">
         <line x1="0" y1="0" x2="18" y2="0" stroke="${c}" stroke-width="2.5"/>
         <text x="24" y="4" fill="#cbd5e1" font-size="11" font-family="monospace">${k}</text>
       </g>`).join('');

    body.innerHTML = `
      <div style="background:rgba(3,10,20,0.7);border:1px solid rgba(56,189,248,0.2);
                  border-radius:10px;overflow:hidden;">
        <svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}"
             style="background:radial-gradient(circle at 50% 50%, rgba(12,30,55,0.8), rgba(2,8,20,0.95));">
          ${defs}
          ${legend}
          ${edgeLegend}
          ${edgeSvg}
          ${nodeSvg}
        </svg>
      </div>
      <div style="font-size:11px;color:#64748b;margin-top:8px;">
        节点分层: BIOS (顶) → RFID → LoRA → OOB (底)。边宽度与透明度表示关联置信度。
      </div>`;
  }

  // ── helpers ──
  function tableWrap(head, rows) {
    return `
      <div style="background:rgba(3,10,20,0.65);border:1px solid rgba(56,189,248,0.18);
                  border-radius:10px;overflow:hidden;">
        <table style="width:100%;border-collapse:collapse;font-size:12px;">
          <thead style="background:rgba(15,32,58,0.9);color:#7dd3fc;font-size:11px;text-align:left;">
            ${head.replace(/<th>/g,'<th style="padding:10px;font-weight:600;letter-spacing:0.5px;">')}
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }
  function emptyState(msg) {
    return `<div style="padding:60px;text-align:center;color:#64748b;">
      <div style="font-size:32px;opacity:0.5;">∅</div>
      <div style="margin-top:10px;font-size:13px;">${msg}</div>
    </div>`;
  }
  function priorityBg(p) { return p === 0 ? '#dc2626' : p === 1 ? '#ea580c' : '#64748b'; }
  function severityBg(s) {
    return s === 'critical' ? '#dc2626' : s === 'high' ? '#ea580c' : '#64748b';
  }
  function ruleKindBg(k) {
    return ({ rfid_lora:'#b45309', rfid_oob:'#be185d', lora_oob:'#047857', bios_rfid:'#334155' })[k] || '#334155';
  }
  function impactColor(v) { return v > 0.5 ? '#f87171' : v > 0.2 ? '#fbbf24' : '#86efac'; }
  function confColor(v) { return v > 0.7 ? '#86efac' : v > 0.4 ? '#fbbf24' : '#f87171'; }
})();
