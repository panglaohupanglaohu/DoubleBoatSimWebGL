/**
 * PoseidonX — Shared Navigation Sidebar
 * Injects OpenBridge-compliant sidebar navigation into any page.
 * Usage: <script src="/js/nav-sidebar.js" data-active="captain"></script>
 */
(function () {
  'use strict';

  const NAV_ITEMS = [
    { id: 'captain',    icon: '⚓', label: '船长总览',   href: '/captain-cockpit.html' },
    { id: 'navigation', icon: '🧭', label: '导航操纵',   href: '/navigation.html' },
    { id: 'dp',         icon: '📍', label: '动力定位',   href: '/dp-control.html' },
    { id: 'thruster',   icon: '⚙',  label: '推进控制',   href: '/thruster-control.html' },
    { id: 'monitor',    icon: '📡', label: '全船监控',   href: '/worldmonitor-map.html' },
    { id: 'cms',        icon: '🔧', label: '设备健康',   href: '/cms-health.html' },
    { id: 'hmi',        icon: '🖥',  label: '控制台',    href: '/hmi-console.html' },
    { id: 'offshore',   icon: '🏗',  label: '海工作业',   href: '/offshore-ops.html' },
    { sep: true },
    { id: 'sim',        icon: '🎮', label: '仿真训练',   href: '/sim-training.html' },
    { id: 'energy',     icon: '⚡', label: '能效合规',   href: '/energy-compliance.html' },
    { id: 'safety',     icon: '🛟', label: '安全应急',   href: '/safety-emergency.html' },
    { id: 'shore',      icon: '🌐', label: '船岸协同',   href: '/ship-shore.html' },
    { sep: true },
    { id: 'twin',       icon: '🚢', label: '数字孪生',   href: '/digital-twin.html' },
    { id: 'agents',     icon: '🤖', label: '智能体',    href: '/agent-team-config.html' },
  ];

  const THEMES = ['day', 'dusk', 'night', 'bright'];

  function getActiveId() {
    const script = document.querySelector('script[data-active]');
    return script ? script.getAttribute('data-active') : '';
  }

  function getCurrentTheme() {
    return document.documentElement.getAttribute('data-obc-theme') || 'dusk';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-obc-theme', theme);
    localStorage.setItem('ob-theme', theme);
  }

  function initTheme() {
    const saved = localStorage.getItem('ob-theme');
    if (saved && THEMES.includes(saved)) {
      setTheme(saved);
    } else {
      setTheme('dusk');
    }
  }

  function buildSidebar() {
    const activeId = getActiveId();
    const sidebar = document.createElement('nav');
    sidebar.className = 'ob-sidebar';
    sidebar.setAttribute('role', 'navigation');
    sidebar.setAttribute('aria-label', 'Main Navigation');

    // Brand
    const brand = document.createElement('div');
    brand.className = 'ob-nav-brand';
    brand.textContent = 'PX';
    brand.title = 'PoseidonX';
    sidebar.appendChild(brand);

    // Nav items container
    const items = document.createElement('div');
    items.className = 'ob-nav-items';

    NAV_ITEMS.forEach(item => {
      if (item.sep) {
        const sep = document.createElement('div');
        sep.className = 'ob-nav-sep';
        items.appendChild(sep);
        return;
      }

      const a = document.createElement('a');
      a.className = 'ob-nav-item' + (item.id === activeId ? ' active' : '');
      a.href = item.href;
      a.setAttribute('data-tooltip', item.label);

      const icon = document.createElement('span');
      icon.className = 'ob-nav-icon';
      icon.textContent = item.icon;
      icon.setAttribute('aria-hidden', 'true');

      const label = document.createElement('span');
      label.className = 'ob-nav-label';
      label.textContent = item.label;

      a.appendChild(icon);
      a.appendChild(label);
      items.appendChild(a);
    });

    sidebar.appendChild(items);

    // Footer with theme switcher
    const footer = document.createElement('div');
    footer.className = 'ob-nav-footer';

    const themeWrap = document.createElement('div');
    themeWrap.style.cssText = 'padding: 4px 6px;';

    const themeSwitch = document.createElement('div');
    themeSwitch.className = 'ob-theme-switch';
    themeSwitch.style.cssText = 'flex-direction: column;';

    const currentTheme = getCurrentTheme();
    const themeLabels = { day: '☀️', dusk: '🌅', night: '🌙', bright: '💡' };

    THEMES.forEach(t => {
      const btn = document.createElement('button');
      btn.className = 'ob-theme-btn' + (t === currentTheme ? ' active' : '');
      btn.textContent = themeLabels[t];
      btn.title = t.charAt(0).toUpperCase() + t.slice(1);
      btn.addEventListener('click', () => {
        setTheme(t);
        themeSwitch.querySelectorAll('.ob-theme-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
      themeSwitch.appendChild(btn);
    });

    themeWrap.appendChild(themeSwitch);
    footer.appendChild(themeWrap);
    sidebar.appendChild(footer);

    return sidebar;
  }

  function buildTopbar(title, subtitle) {
    const topbar = document.createElement('header');
    topbar.className = 'ob-topbar';

    const titleWrap = document.createElement('div');
    titleWrap.style.cssText = 'display:flex;align-items:baseline;gap:4px;min-width:0;';

    const h1 = document.createElement('span');
    h1.className = 'ob-topbar-title';
    h1.textContent = title || document.title;
    titleWrap.appendChild(h1);

    if (subtitle) {
      const sub = document.createElement('span');
      sub.className = 'ob-topbar-subtitle';
      sub.textContent = subtitle;
      titleWrap.appendChild(sub);
    }

    topbar.appendChild(titleWrap);

    // Right: clock + connection status
    const actions = document.createElement('div');
    actions.className = 'ob-topbar-actions';

    const connDot = document.createElement('span');
    connDot.className = 'ob-dot';
    connDot.id = 'ob-conn-dot';
    connDot.title = 'Backend connection';
    actions.appendChild(connDot);

    const clock = document.createElement('span');
    clock.className = 'ob-clock';
    clock.id = 'ob-clock';
    actions.appendChild(clock);

    topbar.appendChild(actions);

    return topbar;
  }

  function updateClock() {
    const el = document.getElementById('ob-clock');
    if (!el) return;
    const now = new Date();
    const utc = now.toISOString().slice(11, 19);
    el.textContent = utc + ' UTC';
  }

  function checkBackend() {
    const dot = document.getElementById('ob-conn-dot');
    if (!dot) return;
    fetch('/health', { signal: AbortSignal.timeout(3000) })
      .then(r => {
        dot.className = r.ok ? 'ob-dot ob-dot-ok' : 'ob-dot ob-dot-warning';
        dot.title = r.ok ? 'Backend connected' : 'Backend error';
      })
      .catch(() => {
        dot.className = 'ob-dot ob-dot-alarm';
        dot.title = 'Backend offline';
      });
  }

  /**
   * Initialize navigation shell.
   * Wraps existing <body> content in the OpenBridge layout.
   */
  function init() {
    initTheme();

    const pageTitle = document.querySelector('meta[name="ob-title"]');
    const pageSubtitle = document.querySelector('meta[name="ob-subtitle"]');
    const title = pageTitle ? pageTitle.content : document.title;
    const subtitle = pageSubtitle ? pageSubtitle.content : '';

    // Check if already wrapped
    if (document.querySelector('.ob-app')) return;

    // Create shell
    const app = document.createElement('div');
    app.className = 'ob-app';

    const sidebar = buildSidebar();
    const main = document.createElement('div');
    main.className = 'ob-main';

    const topbar = buildTopbar(title, subtitle);

    const content = document.createElement('div');
    content.className = 'ob-content';

    // Move existing body children into content
    while (document.body.firstChild) {
      // Skip our own script tag
      if (document.body.firstChild === document.currentScript) {
        document.body.removeChild(document.body.firstChild);
        continue;
      }
      content.appendChild(document.body.firstChild);
    }

    main.appendChild(topbar);
    main.appendChild(content);
    app.appendChild(sidebar);
    app.appendChild(main);
    document.body.appendChild(app);

    // Start clock + health check
    updateClock();
    setInterval(updateClock, 1000);
    checkBackend();
    setInterval(checkBackend, 10000);
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
