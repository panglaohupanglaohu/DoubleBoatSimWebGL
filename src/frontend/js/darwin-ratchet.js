/**
 * Darwin Ratchet — 达尔文棘轮演化机制
 * 系统只增不减地累积有益特性 (Irreversible Feature Accumulation)
 *
 * API:
 *   Darwin.record(item)  — 记录一次演化 (去重 by id)
 *   Darwin.list()        — 全部特性 (按时间排序)
 *   Darwin.locked()      — 已锁定特性
 *   Darwin.stats()       — 统计
 *   Darwin.onChange(cb)  — 变化订阅
 */
(function() {
    const STORAGE_KEY = 'poseidonx.darwin.ratchet';
    const listeners = [];
    
    function load() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    }
    
    function save(items) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        listeners.forEach(cb => { try { cb(items); } catch (e) {} });
        // Broadcast cross-tab
        try {
            const bc = new BroadcastChannel('poseidonx-darwin');
            bc.postMessage({ type: 'update', items });
            bc.close();
        } catch (e) {}
    }
    
    function record(item) {
        if (!item || !item.id) return null;
        const items = load();
        const existing = items.find(x => x.id === item.id);
        const now = new Date().toISOString();
        if (existing) {
            // Update fitness only — core record is locked
            if (item.fitness && item.fitness !== existing.fitness) {
                existing.fitness = item.fitness;
                existing.updatedAt = now;
                save(items);
            }
            return existing;
        }
        const record = {
            id: item.id,
            title: item.title || item.id,
            category: item.category || 'ui',
            description: item.description || '',
            fitness: item.fitness || 'pending',
            lockedAt: item.fitness === 'pass' ? now : null,
            createdAt: now,
            updatedAt: now,
            generation: items.length + 1,
        };
        items.push(record);
        save(items);
        console.log('[Darwin] 🧬 New evolution recorded:', record.title, '(Gen', record.generation + ')');
        return record;
    }
    
    function list() {
        return load().slice().sort((a, b) => (a.createdAt || '').localeCompare(b.createdAt || ''));
    }
    
    function locked() {
        return list().filter(x => x.fitness === 'pass');
    }
    
    function stats() {
        const items = load();
        const byCategory = {};
        items.forEach(i => { byCategory[i.category] = (byCategory[i.category] || 0) + 1; });
        return {
            total: items.length,
            locked: items.filter(i => i.fitness === 'pass').length,
            pending: items.filter(i => i.fitness === 'pending').length,
            rejected: items.filter(i => i.fitness === 'reject').length,
            byCategory,
            lastGeneration: items.length,
        };
    }
    
    function onChange(cb) {
        listeners.push(cb);
        // Cross-tab sync
        try {
            const bc = new BroadcastChannel('poseidonx-darwin');
            bc.onmessage = (e) => { if (e.data && e.data.type === 'update') cb(e.data.items); };
        } catch (e) {}
        return () => {
            const i = listeners.indexOf(cb);
            if (i >= 0) listeners.splice(i, 1);
        };
    }
    
    // 初始化: 一次性记录历史演化项 (只在首次运行时写入)
    function bootstrap() {
        const HERITAGE = [
            { id: 'day-mode-lighting-v1',    title: '日间模式亮化',             category: 'scene',   description: '环境光 + 半球光 1.6x 增强, 天空着色器日间蓝' },
            { id: 'sky-shader-day-v1',       title: '程序化日间天空',            category: 'scene',   description: '地平线浅蓝 → 天顶深蓝渐变 + 太阳光晕' },
            { id: 'cabin-interiors-v1',      title: '6 舱室 3D 内饰',           category: 'scene',   description: '驾驶台/机舱/ECR/货舱/船员舱/厨房 完整建模' },
            { id: 'cabin-split-screen-v1',   title: '分屏舱室信息系统',          category: 'ui',      description: '左 3D + 右系统信息, 进入舱室自动分屏' },
            { id: 'cabin-search-keywords-v1',title: '搜索框识别舱室中文名',      category: 'ui',      description: '输入驾驶台/动力舱/机舱自动进入' },
            { id: 'cabin-dropdown-menu-v1',  title: '舱室快速下拉菜单',          category: 'ui',      description: '右上角单按钮折叠展开式舱室导航' },
            { id: 'ar-cas-floating-v2',      title: 'AR-CAS Pro 可拖拽面板',    category: 'ui',      description: '独立浮动, 拖拽/折叠/调整大小, localStorage 持久化' },
            { id: 'ar-cas-enriched-v1',      title: 'AR-CAS Pro 丰富信息',      category: 'safety',  description: '本船状态 + 环境 + COLREGs 建议 + CPA/TCPA 分解' },
            { id: 'ais-iceberg-merge-v1',    title: 'AIS 列表聚合本地威胁',     category: 'data',    description: 'AIS 列表自动包含 3D 场景中的冰山和货船目标' },
            { id: 'ocean-shader-v1',         title: '海洋 GPU 着色器',          category: 'scene',   description: '多层正弦波 + 菲涅尔反射 + 次表面散射' },
            { id: 'icebergs-sss-v1',         title: '冰山次表面散射着色',        category: 'scene',   description: '5 座冰山, 菲涅尔边缘 + 水下蓝色渗透' },
            { id: 'weather-particles-v1',    title: '天气粒子系统',             category: 'scene',   description: '雨/雪/雾/海鸥/烟囱尾气' },
            { id: 'openbridge-hmi-v1',       title: 'OpenBridge HMI 主题',     category: 'ui',       description: 'DNV OpenBridge 2.4 四主题切换 (dusk/dawn/day/night)' },
            { id: 'colregs-brain-v1',        title: 'COLREGs Brain L3',        category: 'ai',       description: 'Rule 13/14/15/17 自动判断 + TCPA/CPA 威胁评估' },
            { id: 'wpc-attitude-v1',         title: '穿浪双体船姿态控制',       category: 'physics',  description: '水翼/T-Foil 主动姿态反馈 抑制 pitch/heave' },
            { id: 'iamsar-drift-v1',         title: 'MOB + IAMSAR 漂移',       category: 'safety',   description: '落水报警 + 风流联合搜索半径预测' },
            { id: 'darwin-ratchet-v1',       title: '达尔文棘轮机制',          category: 'ai',       description: '只增不减的演化累积引擎' },
            { id: 'bridge-task-dispatch-v1', title: '桥楼任务派发规则',        category: 'ai',       description: '桥楼聊天识别"给X团队的Y设置任务"指令并 POST 到 /agent-config/teams/{team}/tasks, 自动同步至智能体页面' },
            { id: 'ar-cas-pm-task-v1',       title: 'AR-CAS Pro PM 任务案例',  category: 'safety',   description: '用户在桥楼下达"AR-CAS Pro 菜单需要PM实现"任务, 经派发规则路由至 build_pm' },
            { id: 'agent-page-light-theme-v1', title: '智能体页强制浅色主题',   category: 'ui',       description: '/agent-team-config.html 使用 OpenBridge day 主题, 不从 localStorage 继承深色' },
            { id: 'bridge-uses-agent-llm-v1', title: '桥楼 LLM 统一走智能体团队', category: 'ai',      description: '数字孪生 Bridge Chat 通过 /api/v1/bridge-chat/send 使用智能体团队默认 LLM 配置 (localStorage 降级为 fallback)' },
            { id: 'marine-datacenter-v1',     title: '船载数据中心 AI 能耗管理',  category: 'energy',   description: '第一性原理重构: 4 视角(设备/设施/环境/流程) + IoT Hub(LoRa/MC-RFID/PLC-Agent) + Skill库 + Policy引擎 + 闭环 + Darwin 棘轮; 页面: /marine-datacenter.html' },
        ];
        
        const existing = load();
        let added = 0;
        HERITAGE.forEach(h => {
            if (!existing.find(x => x.id === h.id)) {
                existing.push({
                    ...h,
                    fitness: 'pass',  // Heritage 默认锁定
                    lockedAt: new Date().toISOString(),
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    generation: existing.length + 1,
                });
                added++;
            }
        });
        if (added > 0) {
            save(existing);
            console.log(`[Darwin] 🧬 Bootstrapped ${added} heritage evolutions`);
        }
    }
    
    bootstrap();
    
    window.Darwin = { record, list, locked, stats, onChange };
    console.log('[Darwin] 🧬 Ratchet evolution engine online. Current:', stats());
})();
